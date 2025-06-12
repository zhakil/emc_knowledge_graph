"""
增强的Neo4j服务 - 类型安全的实时编辑支持
专注实用性和高效性
"""

from typing import List, Dict, Any, Optional
import asyncio
from neo4j import AsyncGraphDatabase, Query

class EnhancedNeo4jService:
    """增强的Neo4j服务，支持实时编辑"""
    
    def __init__(self, uri: str, username: str, password: str, mock_mode: bool = False):
        self.mock_mode = mock_mode
        if not mock_mode:
            self.driver = AsyncGraphDatabase.driver(uri, auth=(username, password))
        else:
            self.driver = None
            self.mock_data = {
                'nodes': [],
                'links': []
            }
    
    async def close(self):
        """关闭连接"""
        if self.driver:
            await self.driver.close()
    
    async def update_node_position(self, node_id: str, x: float, y: float) -> bool:
        """更新节点位置 - 类型安全版本"""
        if self.mock_mode:
            for node in self.mock_data['nodes']:
                if node.get('id') == node_id:
                    node['x'] = x
                    node['y'] = y
                    return True
            return False
            
        query_str = """
        MATCH (n {id: $node_id})
        SET n.x = $x, n.y = $y, n.updated_at = datetime()
        RETURN count(n) as updated
        """
        
        async with self.driver.session() as session:
            query = Query(query_str)
            result = await session.run(query, node_id=node_id, x=x, y=y)
            record = await result.single()
            return record['updated'] > 0 if record else False
    
    async def create_node_interactive(self, node_data: Dict[str, Any]) -> str:
        """交互式创建节点 - 实用版本"""
        node_id = f"node_{int(asyncio.get_event_loop().time() * 1000)}"
        node_type = node_data.get('type', 'Entity')
        
        if self.mock_mode:
            new_node = {
                'id': node_id,
                'label': node_data.get('label', 'New Node'),
                'type': node_type,
                'x': node_data.get('x', 0),
                'y': node_data.get('y', 0),
                'properties': {k: v for k, v in node_data.items() 
                              if k not in ['id', 'label', 'x', 'y', 'type']}
            }
            self.mock_data['nodes'].append(new_node)
            return node_id
        
        query_str = f"""
        CREATE (n:{node_type} {{
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
            'x': node_data.get('x', 0),
            'y': node_data.get('y', 0),
            'properties': {k: v for k, v in node_data.items() 
                          if k not in ['id', 'label', 'x', 'y', 'type']}
        }
        
        async with self.driver.session() as session:
            query = Query(query_str)
            result = await session.run(query, **params)
            record = await result.single()
            return record['id'] if record else node_id
    
    async def create_relationship_interactive(
        self, 
        source_id: str, 
        target_id: str, 
        rel_type: str,
        properties: Dict[str, Any] = None
    ) -> bool:
        """交互式创建关系 - 类型安全版本"""
        if properties is None:
            properties = {}
            
        if self.mock_mode:
            new_link = {
                'source': source_id,
                'target': target_id,
                'type': rel_type,
                'properties': properties
            }
            self.mock_data['links'].append(new_link)
            return True
            
        query_str = f"""
        MATCH (a {{id: $source_id}}), (b {{id: $target_id}})
        CREATE (a)-[r:{rel_type}]->(b)
        SET r += $properties
        SET r.created_at = datetime()
        RETURN count(r) as created
        """
        
        async with self.driver.session() as session:
            query = Query(query_str)
            result = await session.run(
                query, 
                source_id=source_id,
                target_id=target_id,
                properties=properties
            )
            record = await result.single()
            return record['created'] > 0 if record else False
    
    async def get_subgraph_with_layout(
        self, 
        center_node_id: str, 
        depth: int = 2
    ) -> Dict[str, Any]:
        """获取子图并包含布局信息 - 实用版本"""
        if self.mock_mode:
            return {
                'nodes': self.mock_data['nodes'],
                'links': self.mock_data['links']
            }
            
        query_str = f"""
        MATCH (center {{id: $center_id}})
        MATCH path = (center)-[*1..{depth}]-(n)
        WITH collect(DISTINCT center) + collect(DISTINCT n) as nodes,
             collect(DISTINCT relationships(path)) as rels
        UNWIND nodes as node
        WITH collect(DISTINCT {{
            id: node.id,
            label: node.label,
            type: labels(node)[0],
            x: coalesce(node.x, rand() * 1000),
            y: coalesce(node.y, rand() * 1000),
            properties: properties(node)
        }}) as node_list,
        rels
        
        UNWIND rels as rel_list
        UNWIND rel_list as rel
        WITH node_list, collect(DISTINCT {{
            source: startNode(rel).id,
            target: endNode(rel).id,
            type: type(rel),
            properties: properties(rel)
        }}) as relationship_list
        
        RETURN node_list as nodes, relationship_list as links
        """
        
        async with self.driver.session() as session:
            query = Query(query_str)
            result = await session.run(query, center_id=center_node_id)
            record = await result.single()
            
            if record:
                return {
                    'nodes': record['nodes'],
                    'links': record['links']
                }
            
            return {'nodes': [], 'links': []}