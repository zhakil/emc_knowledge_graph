import asyncio
import json
from typing import Dict, List, Optional, Any, AsyncGenerator
from openai import AsyncOpenAI
from dataclasses import dataclass

@dataclass
class DeepSeekRequest:
    """统一的DeepSeek请求模型"""
    prompt: str
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 4000
    stream: bool = False
    session_id: Optional[str] = None

class EnhancedDeepSeekService:
    """增强的DeepSeek服务，支持实时交互"""
    
    def __init__(self, api_key: str, base_url: str):
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.sessions: Dict[str, List[Dict]] = {}
    
    async def execute_prompt(self, request: DeepSeekRequest) -> Dict[str, Any]:
        """执行提示词请求"""
        messages = [{"role": "user", "content": request.prompt}]
        
        # 添加会话历史
        if request.session_id and request.session_id in self.sessions:
            messages = self.sessions[request.session_id] + messages
        
        try:
            if request.stream:
                return await self._stream_response(messages, request)
            else:
                return await self._single_response(messages, request)
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def _single_response(self, messages: List[Dict], request: DeepSeekRequest) -> Dict[str, Any]:
        """单次响应"""
        response = await self.client.chat.completions.create(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # 更新会话历史
        if request.session_id:
            self._update_session(request.session_id, messages, response.choices[0].message.content)
        
        return {
            "content": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "model": response.model,
            "status": "success"
        }
    
    async def _stream_response(self, messages: List[Dict], request: DeepSeekRequest) -> AsyncGenerator[Dict, None]:
        """流式响应"""
        full_content = ""
        
        async for chunk in await self.client.chat.completions.create(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True
        ):
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                
                yield {
                    "content": content,
                    "full_content": full_content,
                    "is_complete": False
                }
        
        # 最终响应
        if request.session_id:
            self._update_session(request.session_id, messages, full_content)
        
        yield {
            "content": "",
            "full_content": full_content,
            "is_complete": True
        }
    
    def _update_session(self, session_id: str, messages: List[Dict], response: str):
        """更新会话历史"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].extend(messages)
        self.sessions[session_id].append({
            "role": "assistant", 
            "content": response
        })
        
        # 限制历史长度
        if len(self.sessions[session_id]) > 20:
            self.sessions[session_id] = self.sessions[session_id][-20:]