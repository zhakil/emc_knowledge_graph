from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Any
import json
import asyncio

class GraphSyncManager:
    """图数据实时同步管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.graph_states: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, graph_id: str):
        """建立WebSocket连接"""
        await websocket.accept()
        
        if graph_id not in self.active_connections:
            self.active_connections[graph_id] = set()
        
        self.active_connections[graph_id].add(websocket)
        
        # 发送当前图状态
        if graph_id in self.graph_states:
            await websocket.send_json({
                'type': 'initial_state',
                'data': self.graph_states[graph_id]
            })
    
    async def disconnect(self, websocket: WebSocket, graph_id: str):
        """断开WebSocket连接"""
        if graph_id in self.active_connections:
            self.active_connections[graph_id].discard(websocket)
            if not self.active_connections[graph_id]:
                del self.active_connections[graph_id]
    
    async def broadcast_update(self, graph_id: str, update: Dict[str, Any], sender: WebSocket = None):
        """广播图更新"""
        if graph_id not in self.active_connections:
            return
        
        message = {
            'type': 'graph_update',
            'data': update,
            'timestamp': asyncio.get_event_loop().time()
        }
        
        # 发送给除发送者外的所有连接
        tasks = []
        for connection in self.active_connections[graph_id]:
            if connection != sender:
                tasks.append(self._safe_send(connection, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _safe_send(self, websocket: WebSocket, message: Dict):
        """安全发送消息"""
        try:
            await websocket.send_json(message)
        except Exception:
            # 连接已断开，忽略错误
            pass