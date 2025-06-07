"""
Neo4j EMC知识图谱服务 - 修复类型错误
专注实用性和性能的图数据库操作
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, cast
from dataclasses import dataclass, asdict
from datetime import datetime

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession, Query
from neo4j.exceptions import Neo4jError


@dataclass
class EMCNode:
    """EMC节点数据结构"""
    id: str
    label: str
    node_type: str
    properties: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'label': self.label,
            'type': self.node_type,
            'properties': self.properties
        }


@dataclass
class EMCRelationship:
    """EMC关系数据结构"""
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source': self.source_id,
            'target': self.target_id,
            'type': self.relationship_type,
            'properties': self.properties
        }


class Neo4jEMCService:
    """Neo4j EMC知识图谱核心服务 - 实用高效版本"""
    
    def __init__(self, uri: str, username: str, password: str):
        self.uri = uri
        self.username = username
        self.password = password
        self.driver: Optional[AsyncDriver] = None
        self.logger = logging.getLogger(__name__)
    
    async def connect(self) -> bool:
        """建立Neo4j连接"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                max_connection_pool_size=20,
                connection_timeout=30
            )
            
            # 验证连接
            async with self.driver.session() as session:
                # 使用Query类型包装查询字符串
                test_query = Query("RETURN 1")
                await session.run(test_query)
            
            self.logger.info("Neo4j连接成功")
            return True

        except (Neo4jError, neo4j.exceptions.ServiceUnavailable, neo4j.exceptions.AuthError) as e:
            self.logger.error(f"Neo4j连接失败: {type(e).__name__} - {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Neo4j连接时发生未知错误: {type(e).__name__} - {str(e)}")
            return False
    
    async def close(self):
        """关闭Neo4j连接"""
        if self.driver:
            await self.driver.close()
            self.logger.info("Neo4j连接已关闭")

    async def ensure_constraints_and_indexes(self):
        """确保知识图谱的约束和索引符合EMC本体定义"""
        node_types_for_constraints = ["EMCStandard", "Product", "Document", "Component"]

        for node_type in node_types_for_constraints:
            constraint_query = f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{node_type}) REQUIRE n.id IS UNIQUE"
            try:
                await self._execute_write_query(constraint_query)
                self.logger.info(f"Constraint created or already exists for node type: {node_type}")
            except Neo4jError as e:
                self.logger.error(f"Failed to create constraint for node type {node_type}: {str(e)}")
            except Exception as e:
                self.logger.error(f"An unexpected error occurred while creating constraint for {node_type}: {str(e)}")

        # TODO: 根据EMC_ONTOLOGY.md中的定义，扩展此方法以覆盖所有节点类型，
        # 并考虑为经常查询的属性添加其他索引 (例如: CREATE INDEX IF NOT EXISTS FOR (n:Product) ON (n.name);)
        pass
    
    async def _execute_query(
        self, 
        query_str: str, 
        parameters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """执行Cypher查询 - 类型安全版本"""
        if not self.driver:
            raise RuntimeError("Neo4j驱动未初始化")
        
        try:
            async with self.driver.session() as session:
                # 将字符串包装为Query类型
                query = Query(query_str)
                result = await session.run(query, parameters or {})
                return [record.data() async for record in result]
                
        except Neo4jError as e:
            self.logger.error(f"查询执行失败: {query_str}, 错误: {str(e)}")
            raise
    
    async def _execute_write_query(
        self,
        query_str: str,
        parameters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """执行写入查询 - 类型安全版本"""
        if not self.driver:
            raise RuntimeError("Neo4j驱动未初始化")
        
        try:
            async with self.driver.session() as session:
                # 使用事务执行写入操作
                async def _write_transaction(tx):
                    query = Query(query_str)
                    result = await tx.run(query, parameters or {})
                    return [record.data() async for record in result]
                
                return await session.execute_write(_write_transaction)
                
        except Neo4jError as e:
            self.logger.error(f"写入查询失败: {query_str}, 错误: {str(e)}")
            raise

    async def create_emc_node(self, node: EMCNode) -> str:
        """创建EMC节点 - 实用版本"""
        query_str = f"""
        MERGE (n:{node.node_type} {{id: $id}})
        ON CREATE SET
            n.label = $label,
            n.created_at = datetime(),
            n.updated_at = datetime(),
            n += $properties
        ON MATCH SET
            n.label = $label,
            n.updated_at = datetime(),
            n += $properties
        RETURN n.id as id
        """
        
        result = await self._execute_write_query(query_str, {
            'id': node.id,
            'label': node.label,
            'properties': node.properties
        })
        
        return result[0]['id'] if result else node.id
    
    async def get_node_by_id(self, node_id: str) -> Optional[EMCNode]:
        """根据ID获取节点"""
        query_str = """
        MATCH (n {id: $id})
        RETURN n.id as id, labels(n)[0] as type, n.label as label, properties(n) as props
        """
        
        result = await self._execute_query(query_str, {'id': node_id})
        
        if result:
            record = result[0]
            properties = record['props']
            # 清理系统属性
            for key in ['id', 'label', 'created_at', 'updated_at']:
                properties.pop(key, None)
            
            return EMCNode(
                id=record['id'],
                label=record['label'],
                node_type=record['type'],
                properties=properties
            )
        
        return None
    
    async def create_relationship(self, relationship: EMCRelationship) -> bool:
        """创建关系 - 实用版本"""
        query_str = f"""
        MATCH (a {{id: $source_id}}), (b {{id: $target_id}})
        MERGE (a)-[r:{relationship.relationship_type}]->(b)
        ON CREATE SET
            r.created_at = datetime(),
            r.updated_at = datetime(),
            r += $properties
        ON MATCH SET
            r.updated_at = datetime(),
            r += $properties
        RETURN r IS NOT NULL as created_or_matched
        """
        
        result = await self._execute_write_query(query_str, {
            'source_id': relationship.source_id,
            'target_id': relationship.target_id,
            'properties': relationship.properties
        })
        
        return result[0]['created_or_matched'] if result else False
    
    async def get_knowledge_graph_summary(self) -> Dict[str, Any]:
        """获取知识图谱统计摘要 - 高效版本"""
        # 分别查询节点和关系统计
        node_query = """
        MATCH (n)
        WITH labels(n)[0] as label, count(n) as count
        RETURN collect({type: label, count: count}) as node_stats
        """
        
        rel_query = """
        MATCH ()-[r]->()
        WITH type(r) as rel_type, count(r) as count
        RETURN collect({type: rel_type, count: count}) as rel_stats
        """
        
        try:
            node_result = await self._execute_query(node_query)
            rel_result = await self._execute_query(rel_query)
            
            node_stats = {}
            rel_stats = {}
            
            if node_result and node_result[0]['node_stats']:
                for stat in node_result[0]['node_stats']:
                    node_stats[stat['type']] = stat['count']
            
            if rel_result and rel_result[0]['rel_stats']:
                for stat in rel_result[0]['rel_stats']:
                    rel_stats[stat['type']] = stat['count']
            
            return {
                'nodes': node_stats,
                'relationships': rel_stats,
                'total_nodes': sum(node_stats.values()),
                'total_relationships': sum(rel_stats.values())
            }
            
        except Exception as e:
            self.logger.error(f"获取统计摘要失败: {str(e)}")
            return {'nodes': {}, 'relationships': {}, 'total_nodes': 0, 'total_relationships': 0}

    async def verify_connection(self) -> bool:
        """验证连接状态"""
        try:
            if not self.driver:
                return False
            
            async with self.driver.session() as session:
                query = Query("RETURN 1 as test")
                result = await session.run(query)
                await result.single()
                return True
                
        except Exception:
            return False


# 工厂函数 - 简化实例化
async def create_emc_knowledge_service(
    uri: str, 
    username: str, 
    password: str
) -> Neo4jEMCService:
    """创建EMC知识图谱服务 - 实用工厂函数"""
    service = Neo4jEMCService(uri, username, password)
    if await service.connect():
        return service
    else:
        raise RuntimeError("无法连接到Neo4j数据库")