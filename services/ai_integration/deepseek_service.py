"""
DeepSeek AI API集成服务
支持OpenAI兼容的API格式，专为EMC知识图谱优化
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Union
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
import aiohttp
import openai
from openai import AsyncOpenAI


@dataclass
class DeepSeekConfig:
    """DeepSeek API配置"""
    api_key: str
    base_url: str = "https://api.deepseek.com/v1"  # DeepSeek API端点
    model: str = "deepseek-chat"  # 默认模型
    max_tokens: int = 4000
    temperature: float = 0.7
    top_p: float = 0.9
    timeout: int = 30
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EMCPromptTemplate:
    """EMC领域专用提示词模板"""
    name: str
    description: str
    template: str
    variables: List[str]
    category: str  # "analysis", "extraction", "compliance", "query"
    
    def format(self, **kwargs) -> str:
        """格式化模板"""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")


class DeepSeekService:
    """DeepSeek AI服务核心类"""
    
    def __init__(self, config: DeepSeekConfig):
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout
        )
        self.logger = logging.getLogger(__name__)
        self._conversation_history: Dict[str, List[Dict]] = {}
        
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        session_id: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """
        发送聊天请求到DeepSeek API
        
        Args:
            messages: 消息列表，格式为[{"role": "user/assistant", "content": "..."}]
            session_id: 会话ID，用于维护对话历史
            stream: 是否启用流式响应
            **kwargs: 额外的API参数
        """
        # 合并会话历史
        if session_id and session_id in self._conversation_history:
            messages = self._conversation_history[session_id] + messages
        
        # API参数配置
        params = {
            "model": kwargs.get("model", self.config.model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", self.config.top_p),
            "stream": stream
        }
        
        try:
            if stream:
                return self._stream_chat_completion(params, session_id)
            else:
                return await self._single_chat_completion(params, session_id)
                
        except Exception as e:
            self.logger.error(f"DeepSeek API调用失败: {str(e)}")
            raise
    
    async def _single_chat_completion(
        self, 
        params: Dict[str, Any], 
        session_id: Optional[str]
    ) -> Dict[str, Any]:
        """单次聊天完成"""
        start_time = time.time()
        
        response = await self.client.chat.completions.create(**params)
        
        # 记录响应时间
        response_time = time.time() - start_time
        
        # 更新会话历史
        if session_id:
            self._update_conversation_history(
                session_id, 
                params["messages"], 
                response.choices[0].message.content
            )
        
        return {
            "id": response.id,
            "content": response.choices[0].message.content,
            "finish_reason": response.choices[0].finish_reason,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "response_time": response_time,
            "model": response.model
        }
    
    async def _stream_chat_completion(
        self, 
        params: Dict[str, Any], 
        session_id: Optional[str]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式聊天完成"""
        full_content = ""
        start_time = time.time()
        
        async for chunk in await self.client.chat.completions.create(**params):
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                
                yield {
                    "id": chunk.id,
                    "content": content,
                    "full_content": full_content,
                    "finish_reason": chunk.choices[0].finish_reason,
                    "is_final": chunk.choices[0].finish_reason is not None
                }
        
        # 最终响应
        response_time = time.time() - start_time
        if session_id:
            self._update_conversation_history(
                session_id, 
                params["messages"], 
                full_content
            )
        
        yield {
            "id": chunk.id,
            "content": "",
            "full_content": full_content,
            "finish_reason": "stop",
            "is_final": True,
            "response_time": response_time
        }
    
    def _update_conversation_history(
        self, 
        session_id: str, 
        messages: List[Dict], 
        response: str
    ):
        """更新对话历史"""
        if session_id not in self._conversation_history:
            self._conversation_history[session_id] = []
        
        # 添加用户消息和助手响应
        if messages:
            self._conversation_history[session_id].extend(messages)
        
        self._conversation_history[session_id].append({
            "role": "assistant",
            "content": response
        })
        
        # 限制历史长度，保留最近20条消息
        if len(self._conversation_history[session_id]) > 20:
            self._conversation_history[session_id] = \
                self._conversation_history[session_id][-20:]


class EMCPromptManager:
    """EMC领域提示词管理器"""
    
    def __init__(self):
        self.templates: Dict[str, EMCPromptTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """加载默认EMC提示词模板"""
        
        # EMC标准分析模板
        self.add_template(EMCPromptTemplate(
            name="emc_standard_analysis",
            description="分析EMC标准文档并提取关键信息",
            template="""
作为EMC（电磁兼容性）专家，请分析以下EMC标准文档：

标准文档内容：
{document_content}

请提取并返回以下信息（JSON格式）：
1. 标准编号和版本
2. 适用频率范围
3. 测试方法和要求
4. 限值和容差
5. 相关设备类型
6. 合规要求

请确保输出为有效的JSON格式。
            """,
            variables=["document_content"],
            category="analysis"
        ))
        
        # 设备合规性检查模板
        self.add_template(EMCPromptTemplate(
            name="equipment_compliance_check",
            description="检查设备是否符合EMC标准",
            template="""
请评估以下设备的EMC合规性：

设备信息：
{equipment_info}

测试报告数据：
{test_report}

适用标准：
{applicable_standards}

请分析：
1. 设备是否满足相关EMC标准
2. 识别任何潜在的合规性问题
3. 提供改进建议
4. 计算合规性评分（0-100）

请以JSON格式返回分析结果。
            """,
            variables=["equipment_info", "test_report", "applicable_standards"],
            category="compliance"
        ))
        
        # 知识图谱实体提取模板
        self.add_template(EMCPromptTemplate(
            name="entity_extraction",
            description="从EMC文档中提取实体和关系",
            template="""
从以下EMC相关文本中提取实体和关系：

文本内容：
{text_content}

请识别以下类型的实体：
- EMC标准 (Standard)
- 测试设备 (Equipment) 
- 测试方法 (TestMethod)
- 频率范围 (FrequencyRange)
- 限值 (Limit)
- 产品类别 (ProductCategory)

以及它们之间的关系：
- 适用于 (APPLIES_TO)
- 需要 (REQUIRES)
- 测试 (TESTS)
- 符合 (COMPLIES_WITH)

请以JSON格式返回：
{{
  "entities": [
    {{"type": "实体类型", "name": "实体名称", "properties": {{"key": "value"}}}}
  ],
  "relationships": [
    {{"source": "实体1", "target": "实体2", "type": "关系类型"}}
  ]
}}
            """,
            variables=["text_content"],
            category="extraction"
        ))
    
    def add_template(self, template: EMCPromptTemplate):
        """添加提示词模板"""
        self.templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[EMCPromptTemplate]:
        """获取提示词模板"""
        return self.templates.get(name)
    
    def list_templates(self, category: Optional[str] = None) -> List[EMCPromptTemplate]:
        """列出所有模板或指定类别的模板"""
        if category:
            return [t for t in self.templates.values() if t.category == category]
        return list(self.templates.values())
    
    def format_template(self, name: str, **kwargs) -> str:
        """格式化指定模板"""
        template = self.get_template(name)
        if not template:
            raise ValueError(f"模板 '{name}' 不存在")
        
        return template.format(**kwargs)


class DeepSeekEMCService:
    """面向EMC应用的DeepSeek服务封装"""
    
    def __init__(self, config: DeepSeekConfig):
        self.deepseek = DeepSeekService(config)
        self.prompt_manager = EMCPromptManager()
        self.logger = logging.getLogger(__name__)
    
    async def analyze_emc_document(
        self, 
        document_content: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """分析EMC文档"""
        prompt = self.prompt_manager.format_template(
            "emc_standard_analysis",
            document_content=document_content
        )
        
        messages = [{"role": "user", "content": prompt}]
        
        return await self.deepseek.chat_completion(
            messages=messages,
            session_id=session_id,
            temperature=0.3  # 分析任务使用较低温度
        )
    
    async def check_equipment_compliance(
        self,
        equipment_info: str,
        test_report: str,
        standards: List[str],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """检查设备EMC合规性"""
        prompt = self.prompt_manager.format_template(
            "equipment_compliance_check",
            equipment_info=equipment_info,
            test_report=test_report,
            applicable_standards="\n".join(standards)
        )
        
        messages = [{"role": "user", "content": prompt}]
        
        return await self.deepseek.chat_completion(
            messages=messages,
            session_id=session_id,
            temperature=0.2  # 合规性检查需要精确性
        )
    
    async def extract_entities_from_text(
        self,
        text_content: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """从文本中提取EMC实体和关系"""
        prompt = self.prompt_manager.format_template(
            "entity_extraction",
            text_content=text_content
        )
        
        messages = [{"role": "user", "content": prompt}]
        
        return await self.deepseek.chat_completion(
            messages=messages,
            session_id=session_id,
            temperature=0.1  # 实体提取需要高度一致性
        )
    
    async def interactive_chat(
        self,
        user_message: str,
        session_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """交互式EMC专家对话"""
        
        # 构建系统提示
        system_prompt = """
你是一个专业的EMC（电磁兼容性）专家，具有丰富的标准解读、测试方法、合规性评估经验。
请根据用户的问题提供准确、实用的EMC相关建议和信息。

如果用户提供了设备信息、测试数据或标准文档，请进行专业分析。
如果涉及具体的合规性问题，请给出明确的建议和改进方案。
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # 添加上下文信息
        if context:
            context_info = f"参考信息：\n{json.dumps(context, ensure_ascii=False, indent=2)}"
            messages.insert(-1, {"role": "user", "content": context_info})
        
        return await self.deepseek.chat_completion(
            messages=messages,
            session_id=session_id,
            temperature=0.7  # 对话保持适度创造性
        )
    
    def clear_session(self, session_id: str):
        """清除会话历史"""
        if session_id in self.deepseek._conversation_history:
            del self.deepseek._conversation_history[session_id]
    
    def get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        """获取会话历史"""
        return self.deepseek._conversation_history.get(session_id, [])


# 使用示例和配置
def create_deepseek_service(api_key: str) -> DeepSeekEMCService:
    """创建DeepSeek EMC服务实例"""
    config = DeepSeekConfig(
        api_key=api_key,
        model="deepseek-chat",  # 或使用其他DeepSeek模型
        max_tokens=4000,
        temperature=0.7
    )
    
    return DeepSeekEMCService(config)


# 异步上下文管理器用于服务生命周期管理
@asynccontextmanager
async def deepseek_service_context(api_key: str):
    """DeepSeek服务上下文管理器"""
    service = create_deepseek_service(api_key)
    try:
        yield service
    finally:
        # 清理资源
        await service.deepseek.client.close()