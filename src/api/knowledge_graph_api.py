"""
统一知识图谱API接口
职责：提供稳定的外部接口，隔离内部实现变化
"""
import logging
from typing import Dict, List, Optional, Tuple, Any

from ..core.graph_engine import GraphEngine
from ..domain.emc_ontology import EMCOntologyManager
from ..presentation.visualizers.base_visualizer import BaseVisualizer
from ..utils.dependency_manager import dep_manager

logger = logging.getLogger(__name__)

class KnowledgeGraphAPI:
    """
    统一知识图谱API
    
    提供高级抽象接口，隐藏底层实现复杂性：
    - 知识图谱构建和管理
    - 语义搜索和推理
    - 路径发现和分析
    - 可视化和导出
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化API接口"""
        self.config = config or {}
        
        # 确保核心依赖
        if not dep_manager.ensure_core_dependencies():
            raise RuntimeError("核心依赖安装失败")
        
        # 初始化核心组件
        self.graph_engine = GraphEngine()
        self.ontology_manager = EMCOntologyManager()
        
        # 延迟加载可视化组件
        self._visualizer = None
        
        logger.info("知识图谱API初始化完成")
    
    @property
    def visualizer(self) -> BaseVisualizer:
        """延迟加载可视化引擎"""
        if self._visualizer is None:
            # 按需加载可视化依赖
            viz_type = self.config.get('visualization', {}).get('engine', 'plotly')
            
            if viz_type == 'plotly':
                plotly = dep_manager.lazy_import_with_fallback('plotly.graph_objects')
                from ..presentation.visualizers.plotly_viz import PlotlyVisualizer
                self._visualizer = PlotlyVisualizer(self.config)
            elif viz_type == 'matplotlib':
                plt = dep_manager.lazy_import_with_fallback('matplotlib.pyplot')
                from ..presentation.visualizers.matplotlib_viz import MatplotlibVisualizer  
                self._visualizer = MatplotlibVisualizer(self.config)
            else:
                raise ValueError(f"不支持的可视化引擎: {viz_type}")
                
        return self._visualizer
    
    def build_knowledge_graph(self) -> bool:
        """构建EMC知识图谱"""
        try:
            # 加载EMC领域知识
            if not self.ontology_manager.load_emc_knowledge_base():
                logger.error("EMC知识库加载失败")
                return False
            
            # 构建图结构
            if not self.ontology_manager.build_knowledge_graph(self.graph_engine):
                logger.error("知识图谱构建失败")
                return False
            
            logger.info("知识图谱构建成功")
            return True
            
        except Exception as e:
            logger.error(f"知识图谱构建异常: {e}")
            return False
    
    def semantic_search(self, query: str, 
                       entity_types: Optional[List[str]] = None,
                       max_results: int = 10) -> List[Tuple[str, str, float]]:
        """
        语义搜索
        
        Args:
            query: 搜索查询
            entity_types: 限制的实体类型
            max_results: 最大结果数
            
        Returns:
            (节点ID, 节点名称, 相关性分数) 的列表
        """
        try:
            results = []
            query_lower = query.lower()
            
            # 简单的TF-IDF搜索实现
            for node_id, node_data in self.graph_engine.graph.nodes(data=True):
                # 类型过滤
                if entity_types and node_data.get('entity_type') not in entity_types:
                    continue
                
                # 计算相关性分数
                score = 0.0
                name = node_data.get('name', '').lower()
                description = node_data.get('description', '').lower()
                
                # 名称匹配权重更高
                if query_lower in name:
                    score += 2.0
                
                # 描述匹配
                if query_lower in description:
                    score += 1.0
                
                # 部分匹配
                query_words = query_lower.split()
                for word in query_words:
                    if word in name:
                        score += 0.5
                    if word in description:
                        score += 0.3
                
                if score > 0:
                    results.append((node_id, node_data.get('name', node_id), score))
            
            # 按分数排序
            results.sort(key=lambda x: x[2], reverse=True)
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"语义搜索失败: {e}")
            return []
    
    def find_paths(self, source: str, target: str, 
                   max_length: int = 5) -> List[List[str]]:
        """查找语义路径"""
        return self.graph_engine.find_paths(source, target, max_length)
    
    def compute_centrality(self, algorithm: str = "pagerank") -> Dict[str, float]:
        """计算节点中心性"""
        return self.graph_engine.compute_centrality(algorithm)
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """获取图统计信息"""
        return self.graph_engine.get_graph_stats()
    
    def create_visualization(self, viz_type: str = "interactive", 
                           save_path: Optional[str] = None,
                           **kwargs) -> Any:
        """
        创建可视化
        
        Args:
            viz_type: 可视化类型 (static, interactive, dashboard)
            save_path: 保存路径
            **kwargs: 其他参数
            
        Returns:
            可视化对象
        """
        try:
            if viz_type == "static":
                return self.visualizer.create_static_visualization(
                    self.graph_engine.graph, save_path=save_path, **kwargs
                )
            elif viz_type == "interactive":
                return self.visualizer.create_interactive_visualization(
                    self.graph_engine.graph, save_path=save_path, **kwargs
                )
            elif viz_type == "dashboard":
                return self.visualizer.create_dashboard(
                    self.graph_engine.graph, save_path=save_path, **kwargs
                )
            else:
                raise ValueError(f"不支持的可视化类型: {viz_type}")
                
        except Exception as e:
            logger.error(f"可视化创建失败: {e}")
            return None
    
    def export_graph(self, format_type: str = "json", 
                    output_path: Optional[str] = None) -> Optional[str]:
        """
        导出知识图谱
        
        Args:
            format_type: 导出格式 (json, graphml, gexf)
            output_path: 输出路径
            
        Returns:
            导出文件路径
        """
        try:
            if format_type == "json":
                import json
                from datetime import datetime
                
                # 构建导出数据
                export_data = {
                    "metadata": {
                        "export_time": datetime.now().isoformat(),
                        "graph_stats": self.get_graph_statistics()
                    },
                    "nodes": [
                        {"id": node_id, **node_data}
                        for node_id, node_data in self.graph_engine.graph.nodes(data=True)
                    ],
                    "edges": [
                        {"source": u, "target": v, **edge_data}
                        for u, v, edge_data in self.graph_engine.graph.edges(data=True)
                    ]
                }
                
                # 保存文件
                output_path = output_path or f"knowledge_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
                
                logger.info(f"知识图谱已导出: {output_path}")
                return output_path
                
            else:
                raise ValueError(f"不支持的导出格式: {format_type}")
                
        except Exception as e:
            logger.error(f"知识图谱导出失败: {e}")
            return None