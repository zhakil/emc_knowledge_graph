"""
Neo4j EMC知识图谱服务
专为EMC领域优化的图数据库操作接口
"""

import asyncio
import json
import logging
    from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
    from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import Neo4jError


@dataclass
class EMCNode:
"""EMC节点数据结构"""
id: str
label: str
node_type: str  # 'EMCStandard', 'Equipment', 'TestMethod', 'Regulation', 'FrequencyRange'
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
relationship_type: str  # 'APPLIES_TO', 'REQUIRES', 'TESTS', 'COMPLIES_WITH'
properties: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
return {
    'source': self.source_id,
    'target': self.target_id,
    'type': self.relationship_type,
    'properties': self.properties
}


class Neo4jEMCService:
"""Neo4j EMC知识图谱核心服务"""

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
    auth = (self.username, self.password),
    max_connection_pool_size = 20,
    connection_timeout = 30
)

            # 验证连接
            async with self.driver.session() as session:
await session.run("RETURN 1")

self.logger.info("Neo4j连接成功")
return True

        except Exception as e:
self.logger.error(f"Neo4j连接失败: {str(e)}")
return False

    async def close(self):
"""关闭Neo4j连接"""
if self.driver:
    await self.driver.close()
self.logger.info("Neo4j连接已关闭")

    async def _execute_query(
    self,
    query: str,
    parameters: Optional[Dict] = None
) -> List[Dict[str, Any]]:
"""执行Cypher查询"""
if not self.driver:
            raise RuntimeError("Neo4j驱动未初始化")

try:
            async with self.driver.session() as session:
result = await session.run(query, parameters or {})
return [record.data() async for record in result]

        except Neo4jError as e:
self.logger.error(f"查询执行失败: {query}, 错误: {str(e)}")
raise

    async def _execute_write_query(
    self,
    query: str,
    parameters: Optional[Dict] = None
) -> List[Dict[str, Any]]:
"""执行写入查询"""
if not self.driver:
            raise RuntimeError("Neo4j驱动未初始化")

try:
            async with self.driver.session() as session:
result = await session.write_transaction(
    lambda tx: tx.run(query, parameters or {})
)
return [record.data() for record in result]

        except Neo4jError as e:
self.logger.error(f"写入查询失败: {query}, 错误: {str(e)}")
raise

    # === 节点操作 ===

    async def create_emc_node(self, node: EMCNode) -> str:
"""创建EMC节点"""
query = f"""
CREATE(n: { node.node_type } {{
    id: $id,
    label: $label,
    created_at: datetime(),
    updated_at: datetime()
}})
        SET n += $properties
        RETURN n.id as id
"""

result = await self._execute_write_query(query, {
    'id': node.id,
    'label': node.label,
    'properties': node.properties
})

return result[0]['id'] if result else node.id

    async def get_node_by_id(self, node_id: str) -> Optional[EMCNode]:
"""根据ID获取节点"""
query = """
MATCH(n { id: $id })
        RETURN n.id as id, labels(n)[0] as type, n.label as label, properties(n) as props
"""

result = await self._execute_query(query, { 'id': node_id })

if result:
    record = result[0]
properties = record['props']
            # 移除系统属性
properties.pop('id', None)
properties.pop('label', None)
properties.pop('created_at', None)
properties.pop('updated_at', None)

return EMCNode(
    id = record['id'],
    label = record['label'],
    node_type = record['type'],
    properties = properties
)

return None

    async def update_node_properties(
    self,
    node_id: str,
    properties: Dict[str, Any]
) -> bool:
"""更新节点属性"""
query = """
MATCH(n { id: $id })
        SET n += $properties, n.updated_at = datetime()
        RETURN count(n) as updated
"""

result = await self._execute_write_query(query, {
    'id': node_id,
    'properties': properties
})

return result[0]['updated'] > 0 if result else False

    async def delete_node(self, node_id: str) -> bool:
"""删除节点及其所有关系"""
query = """
MATCH(n { id: $id })
        DETACH DELETE n
        RETURN count(n) as deleted
"""

result = await self._execute_write_query(query, { 'id': node_id })
return result[0]['deleted'] > 0 if result else False

    # === 关系操作 ===

    async def create_relationship(self, relationship: EMCRelationship) -> bool:
"""创建关系"""
query = f"""
MATCH(a {{ id: $source_id }}), (b { { id: $target_id } })
CREATE(a) - [r: { relationship.relationship_type }] -> (b)
        SET r += $properties
        SET r.created_at = datetime()
        RETURN count(r) as created
"""

result = await self._execute_write_query(query, {
    'source_id': relationship.source_id,
    'target_id': relationship.target_id,
    'properties': relationship.properties
})

return result[0]['created'] > 0 if result else False

    async def get_node_relationships(
    self,
    node_id: str,
    direction: str = 'both'
) -> List[EMCRelationship]:
"""获取节点的所有关系"""
if direction == 'outgoing':
    query = """
MATCH(n { id: $id }) - [r] -> (m)
            RETURN n.id as source, m.id as target, type(r) as rel_type, properties(r) as props
"""
        elif direction == 'incoming':
query = """
MATCH(n { id: $id }) < -[r] - (m)
            RETURN m.id as source, n.id as target, type(r) as rel_type, properties(r) as props
"""
        else:  # both
query = """
MATCH(n { id: $id }) - [r] - (m)
RETURN
                CASE WHEN startNode(r).id = $id THEN n.id ELSE m.id END as source,
    CASE WHEN startNode(r).id = $id THEN m.id ELSE n.id END as target,
        type(r) as rel_type,
        properties(r) as props
"""

result = await self._execute_query(query, { 'id': node_id })

relationships = []
for record in result:
    properties = record['props']
properties.pop('created_at', None)  # 移除系统属性

relationships.append(EMCRelationship(
    source_id = record['source'],
    target_id = record['target'],
    relationship_type = record['rel_type'],
    properties = properties
))

return relationships

    # === 专业EMC查询 ===

    async def find_applicable_standards(
        self,
        equipment_type: str,
        frequency_range: Optional[str] = None
    ) -> List[EMCNode]:
"""查找适用的EMC标准"""
base_query = """
MATCH(s: EMCStandard) - [: APPLIES_TO] -> (e:Equipment { type: $equipment_type })
"""

if frequency_range:
    base_query += """
MATCH(s) - [: COVERS] -> (f:FrequencyRange { range: $frequency_range })
"""

base_query += """
        RETURN s.id as id, s.label as label, 'EMCStandard' as type, properties(s) as props
"""

params = { 'equipment_type': equipment_type }
if frequency_range:
    params['frequency_range'] = frequency_range

result = await self._execute_query(base_query, params)

nodes = []
for record in result:
    properties = record['props']
properties.pop('id', None)
properties.pop('label', None)

nodes.append(EMCNode(
    id = record['id'],
    label = record['label'],
    node_type = record['type'],
    properties = properties
))

return nodes

    async def check_compliance_path(
    self,
    equipment_id: str,
    standard_id: str
) -> List[List[str]]:
"""检查设备到标准的合规路径"""
query = """
        MATCH path = (e: Equipment { id: $equipment_id })-[* 1..4] - (s:EMCStandard { id: $standard_id })
        WHERE ALL(r in relationships(path) WHERE type(r) IN['TESTED_BY', 'REQUIRES', 'COMPLIES_WITH'])
RETURN[node in nodes(path) | node.id] as node_path
        LIMIT 10
"""

result = await self._execute_query(query, {
    'equipment_id': equipment_id,
    'standard_id': standard_id
})

return [record['node_path'] for record in result]

    async def find_similar_equipment(
    self,
    equipment_id: str,
    similarity_threshold: float = 0.7
) -> List[Tuple[EMCNode, float]]:
"""查找相似设备"""
query = """
MATCH(e1: Equipment { id: $equipment_id })
MATCH(e2: Equipment)
        WHERE e1 <> e2
        WITH e1, e2,
    size([(e1) - [: TESTED_BY] -> (t) < -[: TESTED_BY] - (e2) | t]) as common_tests,
    size([(e1) - [: TESTED_BY] -> (t) | t]) as e1_tests,
    size([(e2) - [: TESTED_BY] -> (t) | t]) as e2_tests
        WITH e1, e2,
    CASE
                 WHEN e1_tests + e2_tests = 0 THEN 0
                 ELSE toFloat(2 * common_tests) / (e1_tests + e2_tests)
END as similarity
        WHERE similarity >= $threshold
        RETURN e2.id as id, e2.label as label, 'Equipment' as type,
    properties(e2) as props, similarity
        ORDER BY similarity DESC
"""

result = await self._execute_query(query, {
    'equipment_id': equipment_id,
    'threshold': similarity_threshold
})

similar_equipment = []
for record in result:
    properties = record['props']
properties.pop('id', None)
properties.pop('label', None)

node = EMCNode(
    id = record['id'],
    label = record['label'],
    node_type = record['type'],
    properties = properties
)
similarity = record['similarity']
similar_equipment.append((node, similarity))

return similar_equipment

    async def get_knowledge_graph_summary(self) -> Dict[str, Any]:
"""获取知识图谱统计摘要"""
query = """
MATCH(n)
        WITH labels(n)[0] as label, count(n) as count
        RETURN collect({ type: label, count: count }) as node_stats

        UNION ALL

MATCH() - [r] -> ()
        WITH type(r) as rel_type, count(r) as count
        RETURN collect({ type: rel_type, count: count }) as rel_stats
"""

result = await self._execute_query(query)

node_stats = {}
rel_stats = {}

for record in result:
    if 'node_stats' in record:
        for stat in record['node_stats']:
            node_stats[stat['type']] = stat['count']
if 'rel_stats' in record:
    for stat in record['rel_stats']:
        rel_stats[stat['type']] = stat['count']

return {
    'nodes': node_stats,
    'relationships': rel_stats,
    'total_nodes': sum(node_stats.values()),
    'total_relationships': sum(rel_stats.values())
}

    async def export_subgraph(
    self,
    center_node_id: str,
    depth: int = 2
) -> Dict[str, Any]:
"""导出以指定节点为中心的子图"""
query = f"""
MATCH(center {{ id: $center_id }})
        MATCH path = (center) - [* 1..{ depth }] - (n)
        WITH collect(DISTINCT center) + collect(DISTINCT n) as nodes,
    collect(DISTINCT relationships(path)) as rels
        UNWIND nodes as node
        WITH collect(DISTINCT {{
        id: node.id,
        label: node.label,
        type: labels(node)[0],
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

        RETURN node_list as nodes, relationship_list as relationships
"""

result = await self._execute_query(query, { 'center_id': center_node_id })

if result:
    return {
        'nodes': result[0]['nodes'],
        'relationships': result[0]['relationships']
    }

return { 'nodes': [], 'relationships': [] }

    # === 批量操作 ===

    async def bulk_create_nodes(self, nodes: List[EMCNode]) -> int:
"""批量创建节点"""
if not nodes:
    return 0

        # 按节点类型分组
nodes_by_type = {}
for node in nodes:
    if node.node_type not in nodes_by_type:
nodes_by_type[node.node_type] = []
nodes_by_type[node.node_type].append(node.to_dict())

total_created = 0

for node_type, node_list in nodes_by_type.items():
    query = f"""
            UNWIND $nodes as node_data
CREATE(n: { node_type })
            SET n = node_data.properties
            SET n.id = node_data.id
            SET n.label = node_data.label
            SET n.created_at = datetime()
            SET n.updated_at = datetime()
            RETURN count(n) as created
"""

result = await self._execute_write_query(query, { 'nodes': node_list })
if result:
    total_created += result[0]['created']

return total_created

    async def bulk_create_relationships(
    self,
    relationships: List[EMCRelationship]
) -> int:
"""批量创建关系"""
if not relationships:
    return 0

        # 按关系类型分组
rels_by_type = {}
for rel in relationships:
    if rel.relationship_type not in rels_by_type:
rels_by_type[rel.relationship_type] = []
rels_by_type[rel.relationship_type].append(rel.to_dict())

total_created = 0

for rel_type, rel_list in rels_by_type.items():
    query = f"""
            UNWIND $relationships as rel_data
MATCH(a {{ id: rel_data.source }}), (b { { id: rel_data.target } })
CREATE(a) - [r: { rel_type }] -> (b)
            SET r += rel_data.properties
            SET r.created_at = datetime()
            RETURN count(r) as created
"""

result = await self._execute_write_query(query, { 'relationships': rel_list })
if result:
    total_created += result[0]['created']

return total_created


class EMCKnowledgeGraphBuilder:
"""EMC知识图谱构建器"""

    def __init__(self, neo4j_service: Neo4jEMCService):
self.neo4j = neo4j_service
self.logger = logging.getLogger(__name__)

    async def build_emc_ontology(self):
"""构建EMC领域本体"""
        # 创建基础节点类型的约束和索引
constraints = [
    "CREATE CONSTRAINT emc_standard_id IF NOT EXISTS FOR (n:EMCStandard) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT equipment_id IF NOT EXISTS FOR (n:Equipment) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT test_method_id IF NOT EXISTS FOR (n:TestMethod) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT regulation_id IF NOT EXISTS FOR (n:Regulation) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT frequency_range_id IF NOT EXISTS FOR (n:FrequencyRange) REQUIRE n.id IS UNIQUE"
]

for constraint in constraints:
    try:
await self.neo4j._execute_write_query(constraint)
            except Exception as e:
self.logger.warning(f"约束创建可能已存在: {str(e)}")

        # 创建索引
indexes = [
    "CREATE INDEX emc_label_index IF NOT EXISTS FOR (n:EMCStandard) ON (n.label)",
    "CREATE INDEX equipment_type_index IF NOT EXISTS FOR (n:Equipment) ON (n.type)",
    "CREATE INDEX test_frequency_index IF NOT EXISTS FOR (n:TestMethod) ON (n.frequency_range)"
]

for index in indexes:
    try:
await self.neo4j._execute_write_query(index)
            except Exception as e:
self.logger.warning(f"索引创建可能已存在: {str(e)}")

    async def import_from_extraction_result(
    self,
    extraction_result: Dict[str, Any]
) -> Tuple[int, int]:
"""从实体提取结果导入数据"""
nodes = []
relationships = []

        # 处理实体
if 'entities' in extraction_result:
    for entity in extraction_result['entities']:
        node = EMCNode(
            id = f"{entity['type']}_{len(nodes)}_{entity['name'].replace(' ', '_')}",
            label = entity['name'],
            node_type = entity['type'],
            properties = entity.get('properties', {})
        )
nodes.append(node)

        # 处理关系
if 'relationships' in extraction_result:
    for rel in extraction_result['relationships']:
                # 查找对应的节点ID
source_id = None
target_id = None

for node in nodes:
    if node.label == rel['source']:
        source_id = node.id
if node.label == rel['target']:
    target_id = node.id

if source_id and target_id:
relationship = EMCRelationship(
    source_id = source_id,
    target_id = target_id,
    relationship_type = rel['type'].upper(),
    properties = rel.get('properties', {})
)
relationships.append(relationship)

        # 批量导入
nodes_created = await self.neo4j.bulk_create_nodes(nodes)
rels_created = await self.neo4j.bulk_create_relationships(relationship