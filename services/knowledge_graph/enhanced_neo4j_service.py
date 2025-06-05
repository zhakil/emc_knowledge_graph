from typing import List, Dict, Any, Optional
import asyncio
from neo4j import AsyncGraphDatabase

class EnhancedNeo4jService:
    """增强的Neo4j服务，支持实时编辑"""
    
    def __init__(self, uri: str, username: str, password: str):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(username, password))
    
    async def update_node_position(self, node_id: str, x: float, y: float) -> bool:
        """更新节点位置"""
        query = """
        MATCH (n {id: $node_id})
        SET n.x = $x, n.y = $y
        RETURN n
        """
        async with self.driver.session() as session:
            result = await session.run(query, node_id=node_id, x=x, y=y)
            return await result.single() is not None
    
    async def create_node_interactive(self, node_data: Dict[str, Any]) -> str:
        """交互式创建节点"""
        query = f"""
        CREATE (n:{node_data['type']} {{
            id: $id,
            label: $label,
            x: $x,
            y: $y,
            created_at: datetime()
        }})
        SET n += $properties
        RETURN n.id as id
        """
        async with self.driver.session() as session:
            result = await session.run(query, **node_data)
            record = await result.single()
            return record['id']
    
    async def create_relationship_interactive(
        self, 
        source_id: str, 
        target_id: str, 
        rel_type: str,
        properties: Dict[str, Any] = {}
    ) -> bool:
        """交互式创建关系"""
        query = f"""
        MATCH (a {{id: $source_id}}), (b {{id: $target_id}})
        CREATE (a)-[r:{rel_type}]->(b)
        SET r += $properties
        RETURN r
        """
        async with self.driver.session() as session:
            result = await session.run(
                query, 
                source_id=source_id,
                target_id=target_id,
                properties=properties
            )
            return await result.single() is not None
    
    async def get_subgraph_with_layout(
        self, 
        center_node_id: str, 
        depth: int = 2
    ) -> Dict[str, Any]:
        """获取子图并包含布局信息"""
        query = """
        MATCH (center {id: $center_id})
        CALL apoc.path.subgraphAll(center, {
            maxLevel: $depth,
            relationshipFilter: '>'
        })
        YIELD nodes, relationships
        RETURN 
            [n in nodes | {
                id: n.id,
                label: n.label,
                type: labels(n)[0],
                x: coalesce(n.x, rand() * 1000),
                y: coalesce(n.y, rand() * 1000),
                properties: properties(n)
            }] as nodes,
            [r in relationships | {
                source: startNode(r).id,
                target: endNode(r).id,
                type: type(r),
                properties: properties(r)
            }] as links
        """
        async with self.driver.session() as session:
            result = await session.run(
                query, 
                center_id=center_node_id,
                depth=depth
            )
            record = await result.single()
            return {
                'nodes': record['nodes'],
                'links': record['links']
            }