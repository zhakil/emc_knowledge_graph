import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from neo4j import AsyncGraphDatabase

@dataclass
class GraphEditOperation:
    """图编辑操作"""
    operation_type: str  # "create_node", "update_node", "create_relationship", "delete_node"
    node_id: Optional[str] = None
    node_data: Optional[Dict[str, Any]] = None
    relationship_data: Optional[Dict[str, Any]] = None
    position: Optional[Dict[str, float]] = None

class RealTimeGraphEditor:
    """实时图编辑服务"""
    
    def __init__(self, neo4j_service):
        self.neo4j = neo4j_service
        self.active_editors: Dict[str, List] = {}
    
    async def apply_edit_operation(self, operation: GraphEditOperation, editor_id: str) -> Dict[str, Any]:
        """应用编辑操作"""
        try:
            if operation.operation_type == "create_node":
                result = await self._create_node(operation.node_data, operation.position)
            elif operation.operation_type == "update_node":
                result = await self._update_node(operation.node_id, operation.node_data)
            elif operation.operation_type == "create_relationship":
                result = await self._create_relationship(operation.relationship_data)
            elif operation.operation_type == "delete_node":
                result = await self._delete_node(operation.node_id)
            else:
                raise ValueError(f"不支持的操作类型: {operation.operation_type}")
            
            # 广播变更给其他编辑者
            await self._broadcast_change(operation, editor_id)
            
            return {
                "success": True,
                "result": result,
                "operation": operation.operation_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "operation": operation.operation_type
            }
    
    async def _create_node(self, node_data: Dict[str, Any], position: Optional[Dict[str, float]]) -> str:
        """创建新节点"""
        node_id = f"node_{int(asyncio.get_event_loop().time() * 1000)}"
        
        # 添加位置信息
        if position:
            node_data.update(position)
        
        query = f"""
        CREATE (n:{node_data.get('type', 'Entity')} {{
            id: $id,
            label: $label,
            x: $x,
            y: $y,
            created_at: datetime()
        }})
        SET n += $properties
        RETURN n.id as id
        """
        
        params = {
            'id': node_id,
            'label': node_data.get('label', 'New Node'),
            'x': position.get('x', 0) if position else 0,
            'y': position.get('y', 0) if position else 0,
            'properties': {k: v for k, v in node_data.items() 
                          if k not in ['id', 'label', 'x', 'y', 'type']}
        }
        
        result = await self.neo4j._execute_write_query(query, params)
        return result[0]['id'] if result else node_id
    
    async def _update_node(self, node_id: str, node_data: Dict[str, Any]) -> bool:
        """更新节点"""
        query = """
        MATCH (n {id: $node_id})
        SET n += $properties
        SET n.updated_at = datetime()
        RETURN count(n) as updated
        """
        
        result = await self.neo4j._execute_write_query(query, {
            'node_id': node_id,
            'properties': node_data
        })
        
        return result[0]['updated'] > 0 if result else False
    
    async def _create_relationship(self, rel_data: Dict[str, Any]) -> bool:
        """创建关系"""
        query = f"""
        MATCH (a {{id: $source_id}}), (b {{id: $target_id}})
        CREATE (a)-[r:{rel_data.get('type', 'RELATES_TO')}]->(b)
        SET r += $properties
        SET r.created_at = datetime()
        RETURN count(r) as created
        """
        
        result = await self.neo4j._execute_write_query(query, {
            'source_id': rel_data['source_id'],
            'target_id': rel_data['target_id'],
            'properties': rel_data.get('properties', {})
        })
        
        return result[0]['created'] > 0 if result else False
    
    async def _delete_node(self, node_id: str) -> bool:
        """删除节点"""
        query = """
        MATCH (n {id: $node_id})
        DETACH DELETE n
        RETURN count(n) as deleted
        """
        
        result = await self.neo4j._execute_write_query(query, {'node_id': node_id})
        return result[0]['deleted'] > 0 if result else False
    
    async def _broadcast_change(self, operation: GraphEditOperation, editor_id: str):
        """广播变更给其他编辑者"""
        # 这里可以集成WebSocket来实现实时同步
        change_event = {
            "type": "graph_change",
            "operation": operation.operation_type,
            "editor_id": editor_id,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # 发送给其他活跃的编辑者
        for active_editor_id in self.active_editors:
            if active_editor_id != editor_id:
                # 实现WebSocket推送逻辑
                pass