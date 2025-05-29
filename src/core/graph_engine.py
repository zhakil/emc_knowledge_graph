"""
高性能图计算引擎
职责：纯粹的图论计算，无业务逻辑
"""
import logging
from typing import Dict, List, Tuple, Any, Optional, Set
import networkx as nx
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Triple:
    """RDF三元组标准结构"""
    subject: str
    predicate: str 
    object: str
    weight: float = 1.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class GraphEngine:
    """
    高性能图计算引擎
    
    基于NetworkX优化的图操作核心，提供：
    - 高效的三元组存储和索引
    - 多种中心性算法计算
    - 路径发现和图遍历
    - 社区检测和聚类分析
    """
    
    def __init__(self, directed: bool = True, multigraph: bool = True):
        """初始化图引擎"""
        if directed and multigraph:
            self.graph = nx.MultiDiGraph()
        elif directed:
            self.graph = nx.DiGraph()
        elif multigraph:
            self.graph = nx.MultiGraph()
        else:
            self.graph = nx.Graph()
            
        # 索引结构优化查询性能
        self._subject_index: Dict[str, Set[str]] = {}
        self._predicate_index: Dict[str, Set[Tuple[str, str]]] = {}
        self._object_index: Dict[str, Set[str]] = {}
        
        # 计算缓存
        self._centrality_cache: Dict[str, Dict] = {}
        self._path_cache: Dict[str, List] = {}
        
        logger.info(f"图引擎初始化完成，类型: {type(self.graph).__name__}")
    
    def add_triple(self, triple: Triple) -> bool:
        """
        添加RDF三元组到图中
        
        Args:
            triple: RDF三元组对象
            
        Returns:
            bool: 添加是否成功
        """
        try:
            # 添加节点（如果不存在）
            if not self.graph.has_node(triple.subject):
                self.graph.add_node(triple.subject)
            if not self.graph.has_node(triple.object):
                self.graph.add_node(triple.object)
            
            # 添加边
            self.graph.add_edge(
                triple.subject, 
                triple.object,
                predicate=triple.predicate,
                weight=triple.weight,
                **triple.metadata
            )
            
            # 更新索引
            self._update_indexes(triple)
            
            # 清除相关缓存
            self._invalidate_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"添加三元组失败: {e}")
            return False
    
    def batch_add_triples(self, triples: List[Triple]) -> int:
        """批量添加三元组，优化性能"""
        success_count = 0
        
        # 禁用索引更新以提升批量性能
        self._batch_mode = True
        
        try:
            for triple in triples:
                if self.add_triple(triple):
                    success_count += 1
        finally:
            self._batch_mode = False
            self._rebuild_indexes()
            
        logger.info(f"批量添加三元组完成: {success_count}/{len(triples)}")
        return success_count
    
    def find_paths(self, source: str, target: str, 
                   max_length: int = 5,
                   predicates: Optional[List[str]] = None) -> List[List[str]]:
        """
        智能路径发现算法
        
        Args:
            source: 源节点
            target: 目标节点  
            max_length: 最大路径长度
            predicates: 允许的谓词类型
            
        Returns:
            路径列表
        """
        cache_key = f"{source}-{target}-{max_length}-{predicates}"
        if cache_key in self._path_cache:
            return self._path_cache[cache_key]
        
        try:
            # 创建过滤子图
            if predicates:
                filtered_edges = [
                    (u, v) for u, v, d in self.graph.edges(data=True)
                    if d.get('predicate') in predicates
                ]
                subgraph = self.graph.edge_subgraph(filtered_edges)
            else:
                subgraph = self.graph
            
            # 查找所有简单路径
            paths = list(nx.all_simple_paths(
                subgraph, source, target, cutoff=max_length
            ))
            
            # 缓存结果
            self._path_cache[cache_key] = paths
            
            return paths
            
        except nx.NetworkXNoPath:
            return []
        except Exception as e:
            logger.error(f"路径查找失败: {e}")
            return []
    
    def compute_centrality(self, algorithm: str = "pagerank", 
                          **kwargs) -> Dict[str, float]:
        """
        计算节点中心性
        
        Args:
            algorithm: 中心性算法 (pagerank, degree, betweenness, closeness)
            **kwargs: 算法参数
            
        Returns:
            节点中心性字典
        """
        if algorithm in self._centrality_cache:
            return self._centrality_cache[algorithm]
        
        try:
            if algorithm == "pagerank":
                centrality = nx.pagerank(self.graph, weight='weight', **kwargs)
            elif algorithm == "degree":
                centrality = nx.degree_centrality(self.graph)
            elif algorithm == "betweenness":
                centrality = nx.betweenness_centrality(self.graph, weight='weight', **kwargs)
            elif algorithm == "closeness":
                centrality = nx.closeness_centrality(self.graph, distance='weight')
            elif algorithm == "eigenvector":
                centrality = nx.eigenvector_centrality(self.graph, weight='weight', **kwargs)
            else:
                raise ValueError(f"不支持的中心性算法: {algorithm}")
            
            # 缓存结果
            self._centrality_cache[algorithm] = centrality
            
            return centrality
            
        except Exception as e:
            logger.error(f"中心性计算失败 ({algorithm}): {e}")
            return {}
    
    def detect_communities(self, algorithm: str = "louvain") -> List[Set[str]]:
        """
        社区检测算法
        
        Args:
            algorithm: 社区检测算法
            
        Returns:
            社区列表
        """
        try:
            # 转换为无向图用于社区检测
            undirected = self.graph.to_undirected()
            
            if algorithm == "louvain":
                # 需要额外安装 python-louvain
                try:
                    import community.community_louvain as community_louvain
                    partition = community_louvain.best_partition(undirected)
                    
                    # 转换分区格式
                    communities = {}
                    for node, comm_id in partition.items():
                        if comm_id not in communities:
                            communities[comm_id] = set()
                        communities[comm_id].add(node)
                    
                    return list(communities.values())
                    
                except ImportError:
                    logger.warning("Louvain算法需要安装 python-louvain 包")
                    return []
            
            elif algorithm == "greedy_modularity":
                import networkx.algorithms.community as nx_community
                communities = nx_community.greedy_modularity_communities(undirected)
                return [set(comm) for comm in communities]
            
            else:
                raise ValueError(f"不支持的社区检测算法: {algorithm}")
                
        except Exception as e:
            logger.error(f"社区检测失败: {e}")
            return []
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """获取图统计信息"""
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "is_connected": nx.is_connected(self.graph.to_undirected()),
            "clustering_coefficient": nx.average_clustering(self.graph.to_undirected()),
            "diameter": self._safe_diameter(),
        }
    
    def _safe_diameter(self) -> Optional[int]:
        """安全计算图直径"""
        try:
            if nx.is_connected(self.graph.to_undirected()):
                return nx.diameter(self.graph.to_undirected())
        except:
            pass
        return None
    
    def _update_indexes(self, triple: Triple):
        """更新索引结构"""
        if hasattr(self, '_batch_mode') and self._batch_mode:
            return
            
        # Subject索引
        if triple.subject not in self._subject_index:
            self._subject_index[triple.subject] = set()
        self._subject_index[triple.subject].add(triple.object)
        
        # Predicate索引
        if triple.predicate not in self._predicate_index:
            self._predicate_index[triple.predicate] = set()
        self._predicate_index[triple.predicate].add((triple.subject, triple.object))
        
        # Object索引
        if triple.object not in self._object_index:
            self._object_index[triple.object] = set()
        self._object_index[triple.object].add(triple.subject)
    
    def _rebuild_indexes(self):
        """重建所有索引"""
        self._subject_index.clear()
        self._predicate_index.clear()
        self._object_index.clear()
        
        for u, v, data in self.graph.edges(data=True):
            triple = Triple(
                subject=u,
                predicate=data.get('predicate', 'unknown'),
                object=v,
                weight=data.get('weight', 1.0),
                metadata=data
            )
            self._update_indexes(triple)
    
    def _invalidate_cache(self):
        """清除计算缓存"""
        self._centrality_cache.clear()
        self._path_cache.clear()