"""
知识图谱API路由模块
处理Neo4j图数据库相关的所有API端点
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from ..middleware.auth import get_current_user
from ..middleware.rate_limiting import rate_limit
from services.knowledge_graph.neo4j_emc_service import Neo4jEMCService, EMCNode, EMCRelationship


router = APIRouter()
logger = logging.getLogger(__name__)


# 请求/响应模型
class NodeCreateRequest(BaseModel):
    """创建节点请求"""
    label: str = Field(..., description="节点标签")
    node_type: str = Field(..., description="节点类型")
    properties: Dict[str, Any] = Field(default_factory=dict, description="节点属性")
    
    @validator('node_type')
    def validate_node_type(cls, v):
        allowed_types = ['EMCStandard', 'Equipment', 'TestMethod', 'Regulation', 'FrequencyRange']
        if v not in allowed_types:
            raise ValueError(f'节点类型必须是以下之一: {allowed_types}')
        return v


class NodeUpdateRequest(BaseModel):
    """更新节点请求"""
    label: Optional[str] = Field(None, description="节点标签")
    properties: Dict[str, Any] = Field(default_factory=dict, description="要更新的属性")


class RelationshipCreateRequest(BaseModel):
    """创建关系请求"""
    source_id: str = Field(..., description="源节点ID")
    target_id: str = Field(..., description="目标节点ID")
    relationship_type: str = Field(..., description="关系类型")
    properties: Dict[str, Any] = Field(default_factory=dict, description="关系属性")
    
    @validator('relationship_type')
    def validate_relationship_type(cls, v):
        allowed_types = ['APPLIES_TO', 'REQUIRES', 'TESTS', 'COMPLIES_WITH', 'RELATED_TO']
        if v not in allowed_types:
            raise ValueError(f'关系类型必须是以下之一: {allowed_types}')
        return v


class CypherQueryRequest(BaseModel):
    """Cypher查询请求"""
    query: str = Field(..., description="Cypher查询语句")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="查询参数")
    limit: Optional[int] = Field(100, description="结果限制数量")
    
    @validator('query')
    def validate_query(cls, v):
        # 安全检查：禁止危险操作
        dangerous_keywords = ['DELETE', 'REMOVE', 'DROP', 'CREATE DATABASE', 'CALL']
        query_upper = v.upper()
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise ValueError(f'查询包含禁止的关键词: {keyword}')
        return v


class GraphAnalysisRequest(BaseModel):
    """图分析请求"""
    analysis_type: str = Field(..., description="分析类型")
    node_ids: Optional[List[str]] = Field(None, description="节点ID列表")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="分析参数")
    
    @validator('analysis_type')
    def validate_analysis_type(cls, v):
        allowed_types = [
            'centrality', 'community_detection', 'shortest_path',
            'similarity', 'compliance_path', 'impact_analysis'
        ]
        if v not in allowed_types:
            raise ValueError(f'分析类型必须是以下之一: {allowed_types}')
        return v


class BatchNodeRequest(BaseModel):
    """批量节点请求"""
    nodes: List[NodeCreateRequest] = Field(..., description="节点列表")
    
    @validator('nodes')
    def validate_nodes_count(cls, v):
        if len(v) > 100:
            raise ValueError('单次批量操作最多支持100个节点')
        return v


class BatchRelationshipRequest(BaseModel):
    """批量关系请求"""
    relationships: List[RelationshipCreateRequest] = Field(..., description="关系列表")
    
    @validator('relationships')
    def validate_relationships_count(cls, v):
        if len(v) > 200:
            raise ValueError('单次批量操作最多支持200个关系')
        return v


class SubgraphRequest(BaseModel):
    """子图请求"""
    center_node_id: str = Field(..., description="中心节点ID")
    depth: int = Field(2, description="子图深度")
    node_types: Optional[List[str]] = Field(None, description="包含的节点类型")
    relationship_types: Optional[List[str]] = Field(None, description="包含的关系类型")
    
    @validator('depth')
    def validate_depth(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('子图深度必须在1-5之间')
        return v


# 依赖注入
def get_neo4j_service() -> Neo4jEMCService:
    """获取Neo4j服务实例"""
    from ..main import service_container
    if not service_container.neo4j_service:
        raise HTTPException(status_code=500, detail="Neo4j服务未初始化")
    return service_container.neo4j_service


@router.get("/health")
async def graph_health_check(
    neo4j_service: Neo4jEMCService = Depends(get_neo4j_service)
):
    """图数据库健康检查"""
    try:
        is_connected = await neo4j_service.verify_connection()
        
        if is_connected:
            stats = await neo4j_service.get_knowledge_graph_summary()
            return {
                "status": "healthy",
                "connected": True,
                "statistics": stats,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "connected": False,
                    "error": "无法连接到Neo4j数据库"
                }
            )
            
    except Exception as e:
        logger.error(f"图数据库健康检查失败: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "connected": False,
                "error": str(e)
            }
        )


@router.get("/statistics")
async def get_graph_statistics(
    current_user: dict = Depends(get_current_user),
    neo4j_service: Neo4jEMCService = Depends(get_neo4j_service)
):
    """获取图数据库统计信息"""
    try:
        stats = await neo4j_service.get_knowledge_graph_summary()
        
        return {
            "statistics": stats,
            "generated_at": datetime.now().isoformat(),
            "user_id": current_user["id"]
        }
        
    except Exception as e:
        logger.error(f"获取图统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/data")
async def get_graph_data(
    node_types: Optional[str] = Query(None, description="节点类型过滤(逗号分隔)"),
    relationship_types: Optional[str] = Query(None, description="关系类型过滤(逗号分隔)"),
    limit: int = Query(1000, description="结果限制"),
    current_user: dict = Depends(get_current_user),
    neo4j_service: Neo4jEMCService = Depends(get_neo4j_service)
):
    """获取图数据"""
    try:
        # 构建查询
        query_parts = ["MATCH (n)-[r]-(m)"]
        where_conditions = []
        
        if node_types:
            types = [t.strip() for t in node_types.split(',')]
            type_conditions = ' OR '.join([f'n:{t}' for t in types])
            where_conditions.append(f"({type_conditions})")
        
        if relationship_types:
            rel_types = [t.strip() for t in relationship_types.split(',')]
            rel_conditions = ' OR '.join([f'type(r) = "{t}"' for t in rel_types])
            where_conditions.append(f"({rel_conditions})")
        
        if where_conditions:
            query_parts.append(f"WHERE {' AND '.join(where_conditions)}")
        
        query_parts.append(f"""
        RETURN DISTINCT
            n.id as source_id, labels(n)[0] as source_type, n.label as source_label, properties(n) as source_props,
            m.id as target_id, labels(m)[0] as target_type, m.label as target_label, properties(m) as target_props,
            type(r) as rel_type, properties(r) as rel_props
        LIMIT {limit}
        """)
        
        query = " ".join(query_parts)
        results = await neo4j_service._execute_query(query)
        
        # 转换为前端需要的格式
        nodes_dict = {}
        edges = []
        
        for record in results:
            # 处理源节点
            source_id = record['source_id']
            if source_id not in nodes_dict:
                source_props = record['source_props']
                source_props.pop('id', None)
                source_props.pop('label', None)
                
                nodes_dict[source_id] = {
                    'id': source_id,
                    'label': record['source_label'],
                    'type': record['source_type'].lower(),
                    'properties': source_props
                }
            
            # 处理目标节点
            target_id = record['target_id']
            if target_id not in nodes_dict:
                target_props = record['target_props']
                target_props.pop('id', None)
                target_props.pop('label', None)
                
                nodes_dict[target_id] = {
                    'id': target_id,
                    'label': record['target_label'],
                    'type': record['target_type'].lower(),
                    'properties': target_props
                }
            
            # 处理关系
            rel_props = record['rel_props']
            edges.append({
                'id': f"{source_id}-{target_id}-{record['rel_type']}",
                'source': source_id,
                'target': target_id,
                'type': record['rel_type'].lower(),
                'properties': rel_props
            })
        
        return {
            'nodes': list(nodes_dict.values()),
            'edges': edges,
            'total_nodes': len(nodes_dict),
            'total_edges': len(edges),
            'query_time': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取图数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取图数据失败: {str(e)}")


@router.post("/nodes")
@rate_limit(requests_per_minute=30)
async def create_node(
    request: NodeCreateRequest,
    current_user: dict = Depends(get_current_user),
    neo4j_service: Neo4jEMCService = Depends(get_neo4j_service)
):
    """创建单个节点"""
    try:
        # 生成节点ID
        node_id = f"{request.node_type}_{datetime.now().timestamp()}".replace(".", "_")
        
        node = EMCNode(
            id=node_id,
            label=request.label,
            node_type=request.node_type,
            properties=request.properties
        )
        
        created_id = await neo4j_service.create_emc_node(node)
        
        return {
            "node_id": created_id,
            "label": request.label,
            "type": request.node_type,
            "properties": request.properties,
            "created_at": datetime.now().isoformat(),
            "created_by": current_user["username"]
        }
        
    except Exception as e:
        logger.error(f"创建节点失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建节点失败: {str(e)}")


@router.get("/nodes/{node_id}")
async def get_node(
    node_id: str,
    current_user: dict = Depends(get_current_user),
    neo4j_service: Neo4jEMCService = Depends(get_neo4j_service)
):
    """获取单个节点详情"""
    try:
        node = await neo4j_service.get_node_by_id(node_id)
        
        if not node:
            raise HTTPException(status_code=404, detail=f"节点 {node_id} 不存在")
        
        # 获取节点的关系
        relationships = await neo4j_service.get_node_relationships(node_id)
        
        return {
            "node": node.to_dict(),
            "relationships": [rel.to_dict() for rel in relationships],
            "relationship_count": len(relationships)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取节点失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取节点失败: {str(e)}")


@router.put("/nodes/{node_id}")
@rate_limit(requests_per_minute=20)
async def update_node(
    node_id: str,
    request: NodeUpdateRequest,
    current_user: dict = Depends(get_current_user),
    neo4j_service: Neo4jEMCService = Depends(get_neo4j_service)
):
    """更新节点"""
    try:
        # 检查节点是否存在
        existing_node = await neo4j_service.get_node_by_id(node_id)
        if not existing_node:
            raise HTTPException(status_code=404, detail=f"节点 {node_id} 不存在")
        
        # 准备更新数据
        update_data = request.properties.copy()
        if request.label:
            update_data["label"] = request.label
        
        success = await neo4j_service.update_node_properties(node_id, update_data)
        
        if success:
            return {
                "node_id": node_id,
                "updated_properties": update_data,
                "updated_at": datetime.now().isoformat(),
                "updated_by": current_user["username"]
            }
        else:
            raise HTTPException(status_code=500, detail="节点更新失败")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新节点失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新节点失败: {str(e)}")


@router.delete("/nodes/{node_id}")
@rate_limit(requests_per_minute=10)
async def delete_node(
    node_id: str,
    current_user: dict = Depends(get_current_user),
    neo4j_service: Neo4jEMCService = Depends(get_neo4j_service)
):
    """删除节点"""
    try:
        success = await neo4j_service.delete_node(node_id)
        
        if success:
            return {
                "message": f"节点 {node_id} 已删除",
                "deleted_at": datetime.now().isoformat(),
                "deleted_by": current_user["username"]
            }
        else:
            raise HTTPException(status_code=404, detail=f"节点 {node_id} 不存在")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除节点失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除节点失败: {str(e)}")


@router.post("/relationships")
@rate_limit(requests_per_minute=25)
async def create_relationship(
    request: RelationshipCreateRequest,
    current_user: dict = Depends(get_current_user),
    neo4j_service: Neo4jEMCService = Depends(get_neo4j_service)
):
    """创建关系"""
    try:
        relationship = EMCRelationship(
            source_id=request.source_id,
            target_id=request.target_id,
            relationship_type=request.relationship_type,
            properties=request.properties
        )
        
        success = await neo4j_service.create_relationship(relationship)
        
        if success:
            return {
                "source_id": request.source_id,
                "target_id": request.target_id,
                "relationship_type": request.relationship_type,
                "properties": request.properties,
                "created_at": datetime.now().isoformat(),
                "created_by": current_user["username"]
            }
        else:
            raise HTTPException(status_code=500, detail="关系创建失败")
        
    except Exception as e:
        logger.error(f"创建关系失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建关系失败: {str(e)}")


@router.post("/query")
@rate_limit(requests_per_minute=15)
async def execute_cypher_query(
    request: CypherQueryRequest,
    current_user: dict = Depends(get_current_user),
    neo4j_service: Neo4jEMCService = Depends(get_neo4j_service)
):
    """执行Cypher查询"""
    try:
        # 添加LIMIT子句以防止过大结果集
        query = request.query
        if request.limit and "LIMIT" not in query.upper():
            query = f"{query} LIMIT {request.limit}"
        
        start_time = datetime.now()
        results = await neo4j_service._execute_query(query, request.parameters)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "query": request.query,
            "parameters": request.parameters,
            "results": results,
            "result_count": len(results),
            "execution_time": execution_time,
            "executed_at": datetime.now().isoformat(),
            "executed_by": current_user["username"]
        }
        
    except Exception as e:
        logger.error(f"执行查询失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"查询执行失败: {str(e)}")


@router.post("/analysis")
@rate_limit(requests_per_minute=10)
async def run_graph_analysis(
    request: GraphAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    neo4j_service: Neo4jEMCService = Depends(get_neo4j_service)
):
    """运行图分析"""
    try:
        analysis_id = f"analysis_{datetime.now().timestamp()}".replace(".", "_")
        
        # 根据分析类型执行不同的分析
        if request.analysis_type == "centrality":
            result = await _run_centrality_analysis(neo4j_service, request.parameters)
        elif request.analysis_type == "shortest_path":
            if not request.node_ids or len(request.node_ids) != 2:
                raise HTTPException(status_code=400, detail="最短路径分析需要提供两个节点ID")
            result = await _run_shortest_path_analysis(
                neo4j_service, request.node_ids[0], request.node_ids[1]
            )
        elif request.analysis_type == "similarity":
            if not request.node_ids or len(request.node_ids) != 1:
                raise HTTPException(status_code=400, detail="相似性分析需要提供一个节点ID")
            result = await _run_similarity_analysis(neo4j_service, request.node_ids[0])
        elif request.analysis_type == "compliance_path":
            if not request.node_ids or len(request.node_ids) != 2:
                raise HTTPException(status_code=400, detail="合规路径分析需要提供两个节点ID")
            result = await _run_compliance_path_analysis(
                neo4j_service, request.node_ids[0], request.node_ids[1]
            )
        else:
            raise HTTPException(status_code=400, detail=f"不支持的分析类型: {request.analysis_type}")
        
        return {
            "analysis_id": analysis_id,
            "analysis_type": request.analysis_type,
            "parameters": request.parameters,
            "result": result,
            "completed_at": datetime.now().isoformat(),
            "analyzed_by": current_user["username"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"图分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"图分析失败: {str(e)}")


@router.post("/subgraph")
async def get_subgraph(
    request: SubgraphRequest,
    current_user: dict = Depends(get_current_user),
    neo4j_service: Neo4jEMCService = Depends(get_neo4j_service)
):
    """获取子图"""
    try:
        subgraph_data = await neo4j_service.export_subgraph(
            center_node_id=request.center_node_id,
            depth=request.depth
        )
        
        # 应用过滤器
        if request.node_types:
            filtered_nodes = []
            for node in subgraph_data['nodes']:
                if node['type'] in request.node_types:
                    filtered_nodes.append(node)
            subgraph_data['nodes'] = filtered_nodes
        
        if request.relationship_types:
            filtered_edges = []
            for edge in subgraph_data['relationships']:
                if edge['type'] in request.relationship_types:
                    filtered_edges.append(edge)
            subgraph_data['relationships'] = filtered_edges
        
        return {
            "center_node": request.center_node_id,
            "depth": request.depth,
            "nodes": subgraph_data['nodes'],
            "edges": subgraph_data['relationships'],
            "node_count": len(subgraph_data['nodes']),
            "edge_count": len(subgraph_data['relationships']),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取子图失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取子图失败: {str(e)}")


@router.post("/batch/nodes")
@rate_limit(requests_per_minute=5)
async def batch_create_nodes(
    request: BatchNodeRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    neo4j_service: Neo4jEMCService = Depends(get_neo4j_service)
):
    """批量创建节点"""
    try:
        # 转换为EMCNode对象
        nodes = []
        for i, node_req in enumerate(request.nodes):
            node_id = f"{node_req.node_type}_{datetime.now().timestamp()}_{i}".replace(".", "_")
            node = EMCNode(
                id=node_id,
                label=node_req.label,
                node_type=node_req.node_type,
                properties=node_req.properties
            )
            nodes.append(node)
        
        # 批量创建
        created_count = await neo4j_service.bulk_create_nodes(nodes)
        
        return {
            "requested_count": len(request.nodes),
            "created_count": created_count,
            "success_rate": created_count / len(request.nodes) if request.nodes else 0,
            "node_ids": [node.id for node in nodes],
            "created_at": datetime.now().isoformat(),
            "created_by": current_user["username"]
        }
        
    except Exception as e:
        logger.error(f"批量创建节点失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量创建节点失败: {str(e)}")


@router.post("/batch/relationships")
@rate_limit(requests_per_minute=5)
async def batch_create_relationships(
    request: BatchRelationshipRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    neo4j_service: Neo4jEMCService = Depends(get_neo4j_service)
):
    """批量创建关系"""
    try:
        # 转换为EMCRelationship对象
        relationships = []
        for rel_req in request.relationships:
            relationship = EMCRelationship(
                source_id=rel_req.source_id,
                target_id=rel_req.target_id,
                relationship_type=rel_req.relationship_type,
                properties=rel_req.properties
            )
            relationships.append(relationship)
        
        # 批量创建
        created_count = await neo4j_service.bulk_create_relationships(relationships)
        
        return {
            "requested_count": len(request.relationships),
            "created_count": created_count,
            "success_rate": created_count / len(request.relationships) if request.relationships else 0,
            "created_at": datetime.now().isoformat(),
            "created_by": current_user["username"]
        }
        
    except Exception as e:
        logger.error(f"批量创建关系失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量创建关系失败: {str(e)}")


# 分析辅助函数
async def _run_centrality_analysis(
    neo4j_service: Neo4jEMCService,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """运行中心性分析"""
    # 计算度中心性
    query = """
    MATCH (n)
    RETURN n.id as node_id, n.label as label, 
           size((n)--()) as degree_centrality
    ORDER BY degree_centrality DESC
    LIMIT 50
    """
    
    results = await neo4j_service._execute_query(query)
    
    return {
        "centrality_scores": results,
        "algorithm": "degree_centrality",
        "top_nodes": results[:10] if results else []
    }


async def _run_shortest_path_analysis(
    neo4j_service: Neo4jEMCService,
    source_id: str,
    target_id: str
) -> Dict[str, Any]:
    """运行最短路径分析"""
    query = """
    MATCH (source {id: $source_id}), (target {id: $target_id})
    MATCH path = shortestPath((source)-[*]-(target))
    RETURN [node in nodes(path) | node.id] as path_nodes,
           [rel in relationships(path) | type(rel)] as path_relationships,
           length(path) as path_length
    """
    
    results = await neo4j_service._execute_query(query, {
        'source_id': source_id,
        'target_id': target_id
    })
    
    if results:
        return {
            "path_found": True,
            "path_nodes": results[0]['path_nodes'],
            "path_relationships": results[0]['path_relationships'],
            "path_length": results[0]['path_length']
        }
    else:
        return {
            "path_found": False,
            "message": f"未找到从 {source_id} 到 {target_id} 的路径"
        }


async def _run_similarity_analysis(
    neo4j_service: Neo4jEMCService,
    node_id: str
) -> Dict[str, Any]:
    """运行相似性分析"""
    # 使用设备相似性分析
    similar_equipment = await neo4j_service.find_similar_equipment(node_id, 0.5)
    
    return {
        "target_node": node_id,
        "similar_nodes": [
            {
                "node": node.to_dict(),
                "similarity_score": score
            }
            for node, score in similar_equipment
        ],
        "similarity_threshold": 0.5
    }


async def _run_compliance_path_analysis(
    neo4j_service: Neo4jEMCService,
    equipment_id: str,
    standard_id: str
) -> Dict[str, Any]:
    """运行合规路径分析"""
    paths = await neo4j_service.check_compliance_path(equipment_id, standard_id)
    
    return {
        "equipment_id": equipment_id,
        "standard_id": standard_id,
        "compliance_paths": paths,
        "path_count": len(paths),
        "has_compliance_path": len(paths) > 0
    }