"""
DeepSeek API路由模块
处理所有与DeepSeek AI交互相关的API端点
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator

from ..middleware.auth import get_current_user
from ..middleware.rate_limiting import rate_limit
from services.ai_integration.deepseek_service import DeepSeekEMCService, DeepSeekConfig


router = APIRouter()
logger = logging.getLogger(__name__)


# 请求/响应模型
class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['user', 'assistant', 'system']
        if v not in allowed_roles:
            raise ValueError(f'角色必须是以下之一: {allowed_roles}')
        return v


class ChatRequest(BaseModel):
    """聊天请求模型"""
    messages: List[ChatMessage] = Field(..., description="消息历史")
    session_id: Optional[str] = Field(None, description="会话ID")
    stream: bool = Field(False, description="是否启用流式响应")
    
    # 模型参数
    model: Optional[str] = Field("deepseek-chat", description="模型名称")
    temperature: Optional[float] = Field(0.7, description="温度参数")
    max_tokens: Optional[int] = Field(4000, description="最大token数")
    top_p: Optional[float] = Field(0.9, description="Top-p参数")
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if v is not None and not 0 <= v <= 2:
            raise ValueError('温度参数必须在0-2之间')
        return v
    
    @validator('max_tokens')
    def validate_max_tokens(cls, v):
        if v is not None and not 1 <= v <= 8000:
            raise ValueError('最大token数必须在1-8000之间')
        return v


class ChatResponse(BaseModel):
    """聊天响应模型"""
    id: str = Field(..., description="响应ID")
    content: str = Field(..., description="响应内容")
    finish_reason: str = Field(..., description="完成原因")
    usage: Dict[str, int] = Field(..., description="token使用统计")
    response_time: float = Field(..., description="响应时间")
    model: str = Field(..., description="使用的模型")
    session_id: Optional[str] = Field(None, description="会话ID")


class DocumentAnalysisRequest(BaseModel):
    """文档分析请求"""
    document_content: str = Field(..., description="文档内容")
    analysis_type: str = Field("emc_standard_analysis", description="分析类型")
    session_id: Optional[str] = Field(None, description="会话ID")
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        allowed_types = [
            'emc_standard_analysis',
            'equipment_compliance_check',
            'entity_extraction',
            'content_summarization'
        ]
        if v not in allowed_types:
            raise ValueError(f'分析类型必须是以下之一: {allowed_types}')
        return v


class ComplianceCheckRequest(BaseModel):
    """合规性检查请求"""
    equipment_info: str = Field(..., description="设备信息")
    test_report: str = Field(..., description="测试报告")
    standards: List[str] = Field(..., description="适用标准列表")
    session_id: Optional[str] = Field(None, description="会话ID")


class EntityExtractionRequest(BaseModel):
    """实体提取请求"""
    text_content: str = Field(..., description="文本内容")
    extraction_mode: str = Field("comprehensive", description="提取模式")
    session_id: Optional[str] = Field(None, description="会话ID")
    
    @validator('extraction_mode')
    def validate_extraction_mode(cls, v):
        allowed_modes = ['comprehensive', 'fast', 'detailed']
        if v not in allowed_modes:
            raise ValueError(f'提取模式必须是以下之一: {allowed_modes}')
        return v


class TemplateRequest(BaseModel):
    """模板请求"""
    template_name: str = Field(..., description="模板名称")
    variables: Dict[str, str] = Field(..., description="模板变量")
    session_id: Optional[str] = Field(None, description="会话ID")


class SessionInfo(BaseModel):
    """会话信息"""
    session_id: str
    message_count: int
    created_at: datetime
    last_activity: datetime


# 依赖注入
def get_deepseek_service() -> DeepSeekEMCService:
    """获取DeepSeek服务实例"""
    # 这里应该从服务容器获取实例
    from ..main import service_container
    if not service_container.deepseek_service:
        raise HTTPException(status_code=500, detail="DeepSeek服务未初始化")
    return service_container.deepseek_service


@router.post("/chat", response_model=ChatResponse)
@rate_limit(requests_per_minute=30)
async def chat_completion(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    deepseek_service: DeepSeekEMCService = Depends(get_deepseek_service)
):
    """
    发送聊天消息到DeepSeek API
    支持普通和流式响应
    """
    try:
        # 转换消息格式
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # 配置参数
        config = {}
        if request.model:
            config["model"] = request.model
        if request.temperature is not None:
            config["temperature"] = request.temperature
        if request.max_tokens is not None:
            config["max_tokens"] = request.max_tokens
        if request.top_p is not None:
            config["top_p"] = request.top_p
        
        # 如果是流式响应，使用不同的处理方式
        if request.stream:
            return StreamingResponse(
                _stream_chat_response(deepseek_service, messages, request.session_id, config),
                media_type="text/event-stream"
            )
        
        # 普通响应
        response = await deepseek_service.deepseek.chat_completion(
            messages=messages,
            session_id=request.session_id,
            stream=False,
            **config
        )
        
        # 记录使用情况
        await _log_usage(current_user["id"], response.get("usage", {}))
        
        return ChatResponse(
            id=response["id"],
            content=response["content"],
            finish_reason=response["finish_reason"],
            usage=response["usage"],
            response_time=response["response_time"],
            model=response["model"],
            session_id=request.session_id
        )
        
    except Exception as e:
        logger.error(f"聊天完成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"聊天请求失败: {str(e)}")


async def _stream_chat_response(
    deepseek_service: DeepSeekEMCService,
    messages: List[Dict[str, str]],
    session_id: Optional[str],
    config: Dict[str, Any]
) -> AsyncGenerator[str, None]:
    """流式聊天响应生成器"""
    try:
        async for chunk in deepseek_service.deepseek.chat_completion(
            messages=messages,
            session_id=session_id,
            stream=True,
            **config
        ):
            # 转换为SSE格式
            event_data = {
                "id": chunk["id"],
                "content": chunk["content"],
                "is_final": chunk.get("is_final", False)
            }
            
            yield f"data: {json.dumps(event_data)}\n\n"
            
            if chunk.get("is_final"):
                yield "data: [DONE]\n\n"
                break
                
    except Exception as e:
        error_data = {"error": str(e)}
        yield f"data: {json.dumps(error_data)}\n\n"


@router.post("/analyze/document")
@rate_limit(requests_per_minute=10)
async def analyze_document(
    request: DocumentAnalysisRequest,
    current_user: dict = Depends(get_current_user),
    deepseek_service: DeepSeekEMCService = Depends(get_deepseek_service)
):
    """
    分析EMC文档
    """
    try:
        if request.analysis_type == "emc_standard_analysis":
            response = await deepseek_service.analyze_emc_document(
                document_content=request.document_content,
                session_id=request.session_id
            )
        else:
            # 其他分析类型可以扩展
            raise HTTPException(status_code=400, detail=f"不支持的分析类型: {request.analysis_type}")
        
        # 尝试解析JSON响应
        try:
            analysis_result = json.loads(response["content"])
        except json.JSONDecodeError:
            analysis_result = {"raw_response": response["content"]}
        
        return {
            "analysis_id": response["id"],
            "analysis_type": request.analysis_type,
            "result": analysis_result,
            "usage": response.get("usage", {}),
            "response_time": response.get("response_time", 0),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"文档分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文档分析失败: {str(e)}")


@router.post("/check/compliance")
@rate_limit(requests_per_minute=15)
async def check_compliance(
    request: ComplianceCheckRequest,
    current_user: dict = Depends(get_current_user),
    deepseek_service: DeepSeekEMCService = Depends(get_deepseek_service)
):
    """
    检查设备EMC合规性
    """
    try:
        response = await deepseek_service.check_equipment_compliance(
            equipment_info=request.equipment_info,
            test_report=request.test_report,
            standards=request.standards,
            session_id=request.session_id
        )
        
        # 解析合规性结果
        try:
            compliance_result = json.loads(response["content"])
        except json.JSONDecodeError:
            compliance_result = {"raw_response": response["content"]}
        
        return {
            "compliance_id": response["id"],
            "equipment_info": request.equipment_info,
            "standards_checked": request.standards,
            "result": compliance_result,
            "usage": response.get("usage", {}),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"合规性检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"合规性检查失败: {str(e)}")


@router.post("/extract/entities")
@rate_limit(requests_per_minute=20)
async def extract_entities(
    request: EntityExtractionRequest,
    current_user: dict = Depends(get_current_user),
    deepseek_service: DeepSeekEMCService = Depends(get_deepseek_service)
):
    """
    从文本中提取EMC实体和关系
    """
    try:
        response = await deepseek_service.extract_entities_from_text(
            text_content=request.text_content,
            session_id=request.session_id
        )
        
        # 解析实体提取结果
        try:
            extraction_result = json.loads(response["content"])
        except json.JSONDecodeError:
            extraction_result = {
                "entities": [],
                "relationships": [],
                "raw_response": response["content"]
            }
        
        return {
            "extraction_id": response["id"],
            "extraction_mode": request.extraction_mode,
            "entities": extraction_result.get("entities", []),
            "relationships": extraction_result.get("relationships", []),
            "usage": response.get("usage", {}),
            "confidence_score": _calculate_extraction_confidence(extraction_result),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"实体提取失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"实体提取失败: {str(e)}")


@router.post("/template/process")
@rate_limit(requests_per_minute=25)
async def process_template(
    request: TemplateRequest,
    current_user: dict = Depends(get_current_user),
    deepseek_service: DeepSeekEMCService = Depends(get_deepseek_service)
):
    """
    使用模板处理请求
    """
    try:
        # 获取并格式化模板
        formatted_prompt = deepseek_service.prompt_manager.format_template(
            request.template_name,
            **request.variables
        )
        
        # 发送请求
        messages = [{"role": "user", "content": formatted_prompt}]
        response = await deepseek_service.deepseek.chat_completion(
            messages=messages,
            session_id=request.session_id
        )
        
        return {
            "template_id": response["id"],
            "template_name": request.template_name,
            "variables_used": request.variables,
            "result": response["content"],
            "usage": response.get("usage", {}),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"模板处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"模板处理失败: {str(e)}")


@router.get("/templates")
async def list_templates(
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    deepseek_service: DeepSeekEMCService = Depends(get_deepseek_service)
):
    """
    获取可用的提示词模板列表
    """
    try:
        templates = deepseek_service.prompt_manager.list_templates(category)
        
        return {
            "templates": [
                {
                    "name": template.name,
                    "description": template.description,
                    "category": template.category,
                    "variables": template.variables
                }
                for template in templates
            ],
            "count": len(templates),
            "categories": list(set(t.category for t in templates))
        }
        
    except Exception as e:
        logger.error(f"获取模板列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取模板失败: {str(e)}")


@router.get("/sessions/{session_id}")
async def get_session_info(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    deepseek_service: DeepSeekEMCService = Depends(get_deepseek_service)
):
    """
    获取会话信息
    """
    try:
        history = deepseek_service.get_session_history(session_id)
        
        if not history:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        return {
            "session_id": session_id,
            "message_count": len(history),
            "messages": history,
            "created_at": history[0].get("timestamp") if history else None,
            "last_activity": history[-1].get("timestamp") if history else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取会话信息失败: {str(e)}")


@router.delete("/sessions/{session_id}")
async def clear_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    deepseek_service: DeepSeekEMCService = Depends(get_deepseek_service)
):
    """
    清除会话历史
    """
    try:
        deepseek_service.clear_session(session_id)
        
        return {
            "message": f"会话 {session_id} 已清除",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"清除会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清除会话失败: {str(e)}")


@router.get("/usage/stats")
async def get_usage_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    获取API使用统计
    """
    try:
        # 这里可以从数据库或缓存中获取用户的使用统计
        # 暂时返回模拟数据
        return {
            "user_id": current_user["id"],
            "today": {
                "requests": 42,
                "tokens": 15680,
                "cost": 0.23
            },
            "this_month": {
                "requests": 1250,
                "tokens": 456789,
                "cost": 6.85
            },
            "limits": {
                "daily_requests": 1000,
                "monthly_tokens": 1000000
            }
        }
        
    except Exception as e:
        logger.error(f"获取使用统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


# 辅助函数
async def _log_usage(user_id: str, usage: Dict[str, int]):
    """记录API使用情况"""
    try:
        # 这里应该记录到数据库或监控系统
        logger.info(f"用户 {user_id} API使用: {usage}")
    except Exception as e:
        logger.error(f"记录使用情况失败: {str(e)}")


def _calculate_extraction_confidence(extraction_result: Dict[str, Any]) -> float:
    """计算实体提取的置信度分数"""
    try:
        entities = extraction_result.get("entities", [])
        relationships = extraction_result.get("relationships", [])
        
        # 简单的置信度计算
        entity_score = min(len(entities) * 0.1, 0.6)
        relation_score = min(len(relationships) * 0.15, 0.4)
        
        return min(entity_score + relation_score, 1.0)
    except Exception:
        return 0.0