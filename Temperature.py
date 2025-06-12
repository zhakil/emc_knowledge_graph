"""
增强的DeepSeek服务 - 集成自适应Temperature控制
修改文件: services/ai_integration/deepseek_service.py
"""

import asyncio
import httpx
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import logging
from enum import Enum

# 导入自适应temperature控制器
from .adaptive_temperature_controller import AdaptiveTemperatureController, QueryType

@dataclass
class ChatRequest:
    """聊天请求数据结构"""
    prompt: str
    conversation_history: Optional[List[str]] = None
    user_feedback: Optional[float] = None
    override_temperature: Optional[float] = None
    max_tokens: int = 1000
    stream: bool = False

@dataclass
class ChatResponse:
    """聊天响应数据结构"""
    content: str
    temperature_used: float
    query_type: QueryType
    temperature_explanation: str
    usage_stats: Dict[str, Any]
    confidence_score: float

class EnhancedDeepSeekService:
    """增强的DeepSeek服务，支持自适应temperature调整"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0
        )
        
        # 初始化自适应temperature控制器
        self.temp_controller = AdaptiveTemperatureController()
        
        # 日志配置
        self.logger = logging.getLogger(__name__)
        
        # EMC领域专用提示词模板
        self.emc_system_prompts = {
            QueryType.STANDARD_QUERY: (
                "你是一个EMC标准专家。请基于权威标准文档提供准确、具体的答案。"
                "引用具体的标准条款和数值。保持回答的准确性和权威性。"
            ),
            QueryType.TECHNICAL_ANALYSIS: (
                "你是一个EMC技术分析专家。请从技术角度深入分析问题，"
                "结合理论知识和实际经验，提供系统性的分析和建议。"
            ),
            QueryType.CREATIVE_DESIGN: (
                "你是一个创新的EMC设计工程师。请发挥创造性思维，"
                "提出新颖的设计思路和解决方案，同时确保技术可行性。"
            ),
            QueryType.TROUBLESHOOTING: (
                "你是一个经验丰富的EMC故障诊断专家。请系统性地分析问题，"
                "提供逐步的诊断流程和多种可能的解决方案。"
            ),
            QueryType.EXPLORATION: (
                "你是一个EMC领域的研究专家。请从前沿研究角度探索问题，"
                "分析发展趋势，提出创新性的观点和假设。"
            )
        }
    
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """
        执行聊天完成，使用自适应temperature
        """
        try:
            # 1. 计算最优temperature
            if request.override_temperature is not None:
                temperature = request.override_temperature
                query_type = QueryType.TECHNICAL_ANALYSIS  # 默认类型
                temp_explanation = f"使用用户指定的temperature: {temperature}"
            else:
                temperature = self.temp_controller.calculate_adaptive_temperature(
                    prompt=request.prompt,
                    conversation_history=request.conversation_history,
                    user_feedback=request.user_feedback
                )
                query_type, _ = self.temp_controller.classify_query(request.prompt)
                temp_explanation = self.temp_controller.get_temperature_explanation(
                    temperature, query_type
                )
            
            # 2. 构建系统提示词
            system_prompt = self.emc_system_prompts.get(
                query_type, 
                self.emc_system_prompts[QueryType.TECHNICAL_ANALYSIS]
            )
            
            # 3. 构建消息列表
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加对话历史
            if request.conversation_history:
                for i, msg in enumerate(request.conversation_history[-6:]):  # 最近6轮对话
                    role = "user" if i % 2 == 0 else "assistant"
                    messages.append({"role": role, "content": msg})
            
            # 添加当前用户消息
            messages.append({"role": "user", "content": request.prompt})
            
            # 4. 调用DeepSeek API
            api_request = {
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": request.max_tokens,
                "stream": request.stream
            }
            
            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json=api_request
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 5. 处理响应
            content = result["choices"][0]["message"]["content"]
            usage_stats = result.get("usage", {})
            
            # 6. 计算置信度分数
            confidence_score = self._calculate_confidence_score(
                content, temperature, query_type
            )
            
            return ChatResponse(
                content=content,
                temperature_used=temperature,
                query_type=query_type,
                temperature_explanation=temp_explanation,
                usage_stats=usage_stats,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            self.logger.error(f"DeepSeek API调用失败: {e}")
            raise
    
    def _calculate_confidence_score(self, 
                                  content: str, 
                                  temperature: float, 
                                  query_type: QueryType) -> float:
        """
        计算回答的置信度分数
        基于temperature、内容长度、结构性等因素
        """
        base_confidence = 1.0 - (temperature - 0.1) * 0.5  # temperature越低置信度越高
        
        # 内容长度调整
        length_factor = min(len(content) / 500, 1.0)  # 适当长度提高置信度
        
        # 结构性分析
        structure_indicators = [
            "首先", "其次", "然后", "最后", "总结",
            "First", "Second", "Finally", "In conclusion"
        ]
        structure_score = sum(1 for indicator in structure_indicators 
                            if indicator in content) / len(structure_indicators)
        
        # EMC专业词汇密度
        emc_terms = [
            "EMC", "EMI", "EMS", "标准", "测试", "频率", "辐射", "传导",
            "屏蔽", "滤波", "接地", "compliance", "emission", "immunity"
        ]
        term_density = sum(content.lower().count(term.lower()) 
                          for term in emc_terms) / max(len(content.split()), 1)
        
        # 综合计算
        confidence = (
            base_confidence * 0.4 + 
            length_factor * 0.2 + 
            structure_score * 0.2 + 
            min(term_density * 10, 1.0) * 0.2
        )
        
        return max(0.1, min(0.95, confidence))
    
    async def provide_feedback(self, 
                             conversation_id: str, 
                             feedback_score: float,
                             feedback_text: Optional[str] = None):
        """
        收集用户反馈用于优化temperature策略
        """
        # 这里可以将反馈存储到数据库中，用于进一步的模型优化
        self.logger.info(f"收到用户反馈: {feedback_score}, {feedback_text}")
        
        # 更新temperature控制器的学习数据
        # 实际应用中可以根据conversation_id找到对应的交互记录
        pass
    
    async def get_temperature_recommendation(self, prompt: str) -> Dict[str, Any]:
        """
        为给定提示词推荐最佳temperature设置
        """
        query_type, confidence = self.temp_controller.classify_query(prompt)
        recommended_temp = self.temp_controller.calculate_adaptive_temperature(prompt)
        
        return {
            "query_type": query_type.value,
            "type_confidence": confidence,
            "recommended_temperature": recommended_temp,
            "explanation": self.temp_controller.get_temperature_explanation(
                recommended_temp, query_type
            ),
            "alternative_temperatures": {
                "conservative": max(0.1, recommended_temp - 0.2),
                "balanced": recommended_temp,
                "creative": min(1.2, recommended_temp + 0.2)
            }
        }
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()

# 使用示例
async def demo_enhanced_service():
    """演示增强服务的使用"""
    service = EnhancedDeepSeekService(api_key="your-api-key")
    
    # 测试不同类型的查询
    requests = [
        ChatRequest(
            prompt="EN 55032标准中Class A设备的传导发射限值是多少？",
        ),
        ChatRequest(
            prompt="请分析开关电源EMI噪声的产生机理和抑制方法",
            conversation_history=["之前我们讨论了滤波器设计"]
        ),
        ChatRequest(
            prompt="如何创新性地设计一个超低EMI的DC-DC转换器？",
        )
    ]
    
    for i, req in enumerate(requests, 1):
        print(f"\n=== 测试 {i} ===")
        print(f"查询: {req.prompt}")
        
        # 获取temperature推荐
        recommendation = await service.get_temperature_recommendation(req.prompt)
        print(f"推荐temperature: {recommendation['recommended_temperature']:.3f}")
        print(f"查询类型: {recommendation['query_type']}")
        print(f"解释: {recommendation['explanation']}")
        
        # 执行聊天
        # response = await service.chat_completion(req)
        # print(f"使用temperature: {response.temperature_used:.3f}")
        # print(f"置信度: {response.confidence_score:.3f}")
    
    await service.close()

if __name__ == "__main__":
    asyncio.run(demo_enhanced_service())