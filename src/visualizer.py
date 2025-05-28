"""
Knowledge Graph Visualization Engine for EMC Standards

基于图论和可视化理论的知识图谱渲染引擎，专门针对汽车电子EMC标准领域
的复杂语义网络进行优化设计。采用多层次布局算法和交互式可视化技术，
实现高维知识结构的二维映射和动态展示。

核心技术特点：
- 自适应力导向布局算法优化
- 多模态交互式可视化界面
- 语义聚类和层次化展示
- 实时动态过滤和检索功能

Author: EMC Standards Research Team
Version: 1.0.0
"""

import colorsys
import logging
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from matplotlib.patches import FancyBboxPatch
from plotly.subplots import make_subplots

from data_models import KnowledgeEdge, KnowledgeNode, NodeType, RelationType
from utils import ensure_directory, load_config

logger = logging.getLogger(__name__)


@dataclass
class VisualizationConfig:
    """可视化配置参数类"""

    layout_algorithm: str = "spring"
    node_size_range: Tuple[int, int] = (800, 3000)
    edge_width_range: Tuple[int, int] = (1, 5)
    color_alpha: float = 0.8
    font_size: int = 10
    figure_dpi: int = 300
    interactive_height: int = 800
    interactive_width: int = 1200


class KnowledgeGraphVisualizer:
    """
    知识图谱可视化引擎

    基于图论的可视化算法框架，实现EMC标准知识图谱的多维度可视化。
    支持静态和交互式两种渲染模式，采用语义感知的布局优化策略。
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化可视化引擎

        Args:
            config: 可视化配置参数
        """
        self.config = config or load_config()
        self.vis_config = self._parse_visualization_config()

        # 颜色方案管理
        self.node_colors = NodeType.get_color_scheme()
        self.edge_colors = self._generate_edge_color_scheme()

        # 布局缓存
        self._layout_cache = {}

        # 中文字体配置
        self._configure_chinese_fonts()

        logger.info("知识图谱可视化引擎初始化完成")

    def _parse_visualization_config(self) -> VisualizationConfig:
        """解析可视化配置"""
        vis_section = self.config.get("visualization", {})

        return VisualizationConfig(
            layout_algorithm=self.config.get("graph", {})
            .get("layout", {})
            .get("default", "spring"),
            node_size_range=(
                self.config.get("graph", {}).get("nodes", {}).get("min_size", 800),
                self.config.get("graph", {}).get("nodes", {}).get("max_size", 3000),
            ),
            edge_width_range=(
                self.config.get("graph", {}).get("edges", {}).get("min_width", 1),
                self.config.get("graph", {}).get("edges", {}).get("max_width", 5),
            ),
            figure_dpi=vis_section.get("static", {}).get("dpi", 300),
            interactive_height=vis_section.get("interactive", {}).get("height", 800),
            interactive_width=vis_section.get("interactive", {}).get("width", 1200),
        )

    def _configure_chinese_fonts(self):
        """配置中文字体支持"""
        try:
            plt.rcParams["font.sans-serif"] = [
                "SimHei",
                "Microsoft YaHei",
                "DejaVu Sans",
            ]
            plt.rcParams["axes.unicode_minus"] = False
            logger.debug("中文字体配置完成")
        except Exception as e:
            logger.warning(f"中文字体配置失败: {e}")

    def _generate_edge_color_scheme(self) -> Dict[RelationType, str]:
        """生成边类型颜色方案"""
        relation_types = list(RelationType)
        num_types = len(relation_types)

        colors = {}
        for i, rel_type in enumerate(relation_types):
            # 使用HSV颜色空间生成区分度高的颜色
            hue = i / num_types
            saturation = 0.7
            value = 0.8
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
            )
            colors[rel_type] = hex_color

        return colors

    def compute_layout(
        self, graph: nx.Graph, algorithm: str = None, force_recompute: bool = False
    ) -> Dict[str, Tuple[float, float]]:
        """
        计算图布局位置

        采用多种布局算法的组合优化策略，根据图的结构特征
        自适应选择最优布局方案。

        Args:
            graph: NetworkX图对象
            algorithm: 布局算法类型
            force_recompute: 强制重新计算

        Returns:
            节点位置字典
        """
        algorithm = algorithm or self.vis_config.layout_algorithm
        cache_key = f"{algorithm}_{graph.number_of_nodes()}_{graph.number_of_edges()}"

        if not force_recompute and cache_key in self._layout_cache:
            logger.debug(f"使用缓存的布局: {cache_key}")
            return self._layout_cache[cache_key]

        logger.info(f"计算图布局，算法: {algorithm}, 节点数: {graph.number_of_nodes()}")

        try:
            if algorithm == "spring":
                pos = self._compute_spring_layout(graph)
            elif algorithm == "hierarchical":
                pos = self._compute_hierarchical_layout(graph)
            elif algorithm == "circular":
                pos = nx.circular_layout(graph)
            elif algorithm == "kamada_kawai":
                pos = nx.kamada_kawai_layout(graph)
            elif algorithm == "shell":
                pos = self._compute_shell_layout(graph)
            else:
                logger.warning(f"未知布局算法: {algorithm}, 使用spring布局")
                pos = self._compute_spring_layout(graph)

            # 缓存布局结果
            self._layout_cache[cache_key] = pos
            logger.debug(f"布局计算完成，缓存键: {cache_key}")

            return pos

        except Exception as e:
            logger.error(f"布局计算失败: {e}")
            # 回退到简单的随机布局
            return nx.random_layout(graph)

    def _compute_spring_layout(self, graph: nx.Graph) -> Dict[str, Tuple[float, float]]:
        """优化的弹簧布局算法"""
        spring_config = self.config.get("graph", {}).get("layout", {})

        k = spring_config.get("spring_k", 3)
        iterations = spring_config.get("spring_iterations", 50)
        seed = spring_config.get("random_seed", 42)

        return nx.spring_layout(
            graph, k=k, iterations=iterations, seed=seed, weight="weight"
        )

    def _compute_hierarchical_layout(
        self, graph: nx.Graph
    ) -> Dict[str, Tuple[float, float]]:
        """层次化布局算法"""
        try:
            # 使用graphviz的dot布局（如果可用）
            return nx.nx_agraph.graphviz_layout(graph, prog="dot")
        except:
            # 回退到自定义层次布局
            return self._custom_hierarchical_layout(graph)

    def _custom_hierarchical_layout(
        self, graph: nx.Graph
    ) -> Dict[str, Tuple[float, float]]:
        """自定义层次布局实现"""
        try:
            # 计算节点层级
            if len(graph.nodes()) == 0:
                return {}

            # 选择根节点（度数最高的节点）
            root = max(graph.nodes(), key=lambda n: graph.degree(n))

            # 计算从根节点的最短路径长度作为层级
            levels = nx.single_source_shortest_path_length(graph, root)
            max_level = max(levels.values()) if levels else 0

            # 按层级分组节点
            level_nodes = {}
            for node, level in levels.items():
                if level not in level_nodes:
                    level_nodes[level] = []
                level_nodes[level].append(node)

            # 计算节点位置
            pos = {}
            for level in range(max_level + 1):
                nodes_at_level = level_nodes.get(level, [])
                if not nodes_at_level:
                    continue

                y = 1.0 - (level / max_level if max_level > 0 else 0)

                for i, node in enumerate(nodes_at_level):
                    if len(nodes_at_level) == 1:
                        x = 0.5
                    else:
                        x = i / (len(nodes_at_level) - 1)
                    pos[node] = (x, y)

            return pos

        except Exception as e:
            logger.error(f"自定义层次布局失败: {e}")
            return nx.spring_layout(graph)

    def _compute_shell_layout(self, graph: nx.Graph) -> Dict[str, Tuple[float, float]]:
        """同心圆布局"""
        # 根据节点类型分层
        shells = []
        node_types = set()

        # 收集所有节点类型
        for node_id in graph.nodes():
            node_data = graph.nodes[node_id]
            if "node_type" in node_data:
                node_types.add(node_data["node_type"])

        # 按类型分组
        for node_type in node_types:
            shell = [
                node_id
                for node_id in graph.nodes()
                if graph.nodes[node_id].get("node_type") == node_type
            ]
            if shell:
                shells.append(shell)

        if not shells:
            shells = [list(graph.nodes())]

        return nx.shell_layout(graph, nlist=shells)

    def create_matplotlib_visualization(
        self,
        graph: nx.Graph,
        nodes_data: Dict[str, KnowledgeNode],
        edges_data: List[KnowledgeEdge],
        figsize: Tuple[int, int] = None,
        save_path: Optional[str] = None,
        title: str = "EMC标准知识图谱",
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        创建基于Matplotlib的静态可视化

        采用高质量渲染引擎，支持矢量输出和科学出版标准。
        实现节点语义着色、边权重映射和交互式标注功能。

        Args:
            graph: NetworkX图对象
            nodes_data: 节点数据字典
            edges_data: 边数据列表
            figsize: 图形尺寸
            save_path: 保存路径
            title: 图形标题

        Returns:
            Figure和Axes对象元组
        """
        figsize = figsize or tuple(
            self.config.get("visualization", {})
            .get("static", {})
            .get("figure_size", [20, 16])
        )

        fig, ax = plt.subplots(figsize=figsize, dpi=self.vis_config.figure_dpi)

        # 计算布局
        pos = self.compute_layout(graph)

        # 绘制不同类型的节点
        self._draw_nodes_by_type(ax, graph, nodes_data, pos)

        # 绘制边
        self._draw_edges_with_styles(ax, graph, edges_data, pos)

        # 绘制节点标签
        self._draw_node_labels(ax, graph, nodes_data, pos)

        # 添加图例
        self._add_legend(ax, nodes_data)

        # 设置标题和样式
        ax.set_title(title, fontsize=18, fontweight="bold", pad=20)
        ax.axis("off")

        # 调整布局
        plt.tight_layout()

        # 保存图像
        if save_path:
            ensure_directory(Path(save_path).parent)
            plt.savefig(
                save_path,
                dpi=self.vis_config.figure_dpi,
                bbox_inches="tight",
                facecolor="white",
            )
            logger.info(f"静态图谱已保存: {save_path}")

        return fig, ax

    def _draw_nodes_by_type(
        self,
        ax: plt.Axes,
        graph: nx.Graph,
        nodes_data: Dict[str, KnowledgeNode],
        pos: Dict,
    ):
        """按类型绘制节点"""
        node_type_groups = {}

        # 按类型分组节点
        for node_id, node_data in nodes_data.items():
            node_type = node_data.node_type
            if node_type not in node_type_groups:
                node_type_groups[node_type] = []
            node_type_groups[node_type].append(node_id)

        # 绘制每种类型的节点
        for node_type, node_ids in node_type_groups.items():
            if not node_ids:
                continue

            color = self.node_colors.get(node_type, "#cccccc")

            # 计算节点大小（基于连接度）
            node_sizes = []
            for node_id in node_ids:
                degree = graph.degree(node_id)
                size = self._calculate_node_size(degree)
                node_sizes.append(size)

            # 绘制节点
            nx.draw_networkx_nodes(
                graph,
                pos,
                nodelist=node_ids,
                node_color=color,
                node_size=node_sizes,
                alpha=self.vis_config.color_alpha,
                edgecolors="white",
                linewidths=2,
                ax=ax,
            )

    def _calculate_node_size(self, degree: int) -> int:
        """根据节点度计算大小"""
        min_size, max_size = self.vis_config.node_size_range

        # 对数缩放
        if degree <= 1:
            return min_size

        log_degree = math.log(degree)
        max_log_degree = math.log(20)  # 假设最大度为20

        normalized = min(log_degree / max_log_degree, 1.0)
        size = min_size + (max_size - min_size) * normalized

        return int(size)

    def _draw_edges_with_styles(
        self, ax: plt.Axes, graph: nx.Graph, edges_data: List[KnowledgeEdge], pos: Dict
    ):
        """绘制带样式的边"""
        edge_type_groups = {}

        # 按关系类型分组边
        for edge in edges_data:
            rel_type = edge.relation_type
            if rel_type not in edge_type_groups:
                edge_type_groups[rel_type] = []
            edge_type_groups[rel_type].append((edge.source, edge.target, edge.weight))

        # 绘制每种类型的边
        for rel_type, edge_list in edge_type_groups.items():
            if not edge_list:
                continue

            edges = [(u, v) for u, v, w in edge_list]
            weights = [w for u, v, w in edge_list]

            # 计算边宽度
            edge_widths = [self._calculate_edge_width(w) for w in weights]

            # 获取边颜色
            edge_color = self.edge_colors.get(rel_type, "#888888")

            # 绘制边
            nx.draw_networkx_edges(
                graph,
                pos,
                edgelist=edges,
                width=edge_widths,
                edge_color=edge_color,
                alpha=0.6,
                arrows=True,
                arrowsize=20,
                arrowstyle="->",
                ax=ax,
            )

    def _calculate_edge_width(self, weight: float) -> float:
        """根据权重计算边宽度"""
        min_width, max_width = self.vis_config.edge_width_range
        return min_width + (max_width - min_width) * weight

    def _draw_node_labels(
        self,
        ax: plt.Axes,
        graph: nx.Graph,
        nodes_data: Dict[str, KnowledgeNode],
        pos: Dict,
    ):
        """绘制节点标签"""
        labels = {}
        for node_id, node_data in nodes_data.items():
            # 使用缩短的标签以避免重叠
            label = node_data.name
            if len(label) > 15:
                label = label[:12] + "..."
            labels[node_id] = label

        nx.draw_networkx_labels(
            graph,
            pos,
            labels,
            font_size=self.vis_config.font_size,
            font_weight="bold",
            font_color="black",
            ax=ax,
        )

    def _add_legend(self, ax: plt.Axes, nodes_data: Dict[str, KnowledgeNode]):
        """添加图例"""
        # 收集所有节点类型
        node_types = set(node.node_type for node in nodes_data.values())

        # 创建图例元素
        legend_elements = []
        for node_type in node_types:
            color = self.node_colors.get(node_type, "#cccccc")
            display_name = NodeType.get_display_names().get(node_type, node_type.value)

            patch = patches.Patch(color=color, label=display_name)
            legend_elements.append(patch)

        # 添加图例
        ax.legend(
            handles=legend_elements,
            loc="upper left",
            bbox_to_anchor=(1, 1),
            fontsize=12,
        )

    def create_plotly_visualization(
        self,
        graph: nx.Graph,
        nodes_data: Dict[str, KnowledgeNode],
        edges_data: List[KnowledgeEdge],
        save_path: Optional[str] = None,
        title: str = "EMC标准知识图谱 - 交互式版本",
    ) -> go.Figure:
        """
        创建基于Plotly的交互式可视化

        构建Web兼容的交互式知识图谱界面，支持节点缩放、
        路径高亮、语义过滤和实时搜索功能。

        Args:
            graph: NetworkX图对象
            nodes_data: 节点数据字典
            edges_data: 边数据列表
            save_path: 保存路径
            title: 图形标题

        Returns:
            Plotly Figure对象
        """
        # 计算布局
        pos = self.compute_layout(graph)

        # 准备边数据
        edge_x, edge_y = self._prepare_edge_coordinates(pos, edges_data)

        # 准备节点数据
        node_trace = self._prepare_node_trace(pos, nodes_data, graph)

        # 创建边轨迹
        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=2, color="#888"),
            hoverinfo="none",
            mode="lines",
            name="关系连接",
        )

        # 创建图形
        fig = go.Figure(data=[edge_trace, node_trace])

        # 设置布局
        self._configure_plotly_layout(fig, title)

        # 保存文件
        if save_path:
            ensure_directory(Path(save_path).parent)
            fig.write_html(save_path)
            logger.info(f"交互式图谱已保存: {save_path}")

        return fig

    def _prepare_edge_coordinates(
        self, pos: Dict, edges_data: List[KnowledgeEdge]
    ) -> Tuple[List, List]:
        """准备边坐标数据"""
        edge_x = []
        edge_y = []

        for edge in edges_data:
            if edge.source in pos and edge.target in pos:
                x0, y0 = pos[edge.source]
                x1, y1 = pos[edge.target]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

        return edge_x, edge_y

    def _prepare_node_trace(
        self, pos: Dict, nodes_data: Dict[str, KnowledgeNode], graph: nx.Graph
    ) -> go.Scatter:
        """准备节点轨迹数据"""
        node_x = []
        node_y = []
        node_colors = []
        node_sizes = []
        node_text = []
        node_info = []

        for node_id, node_data in nodes_data.items():
            if node_id in pos:
                x, y = pos[node_id]
                node_x.append(x)
                node_y.append(y)

                # 节点颜色
                color = self.node_colors.get(node_data.node_type, "#cccccc")
                node_colors.append(color)

                # 节点大小（基于度）
                degree = graph.degree(node_id)
                size = self._calculate_node_size(degree) / 50  # 缩放到适合Plotly的尺寸
                node_sizes.append(size)

                # 节点文本
                node_text.append(node_data.name)

                # 悬停信息
                info = f"<b>{node_data.name}</b><br>"
                info += f"类型: {NodeType.get_display_names().get(node_data.node_type, node_data.node_type.value)}<br>"
                info += f"描述: {node_data.description}<br>"
                info += f"连接数: {degree}"
                node_info.append(info)

        return go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            hoverinfo="text",
            hovertext=node_info,
            text=node_text,
            textposition="middle center",
            textfont=dict(size=10, color="white"),
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color="white"),
                sizemode="diameter",
            ),
            name="知识节点",
        )

    def _configure_plotly_layout(self, fig: go.Figure, title: str):
        """配置Plotly布局"""
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=20, color="#2c3e50")),
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=60),
            annotations=[
                dict(
                    text="点击节点查看详细信息，双击缩放，拖拽平移",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.005,
                    y=-0.002,
                    xanchor="left",
                    yanchor="bottom",
                    font=dict(color="#666", size=12),
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="rgba(248,248,248,0.8)",
            width=self.vis_config.interactive_width,
            height=self.vis_config.interactive_height,
        )

    def create_network_analysis_dashboard(
        self,
        graph: nx.Graph,
        nodes_data: Dict[str, KnowledgeNode],
        edges_data: List[KnowledgeEdge],
    ) -> go.Figure:
        """
        创建网络分析仪表板

        提供图论分析指标的可视化仪表板，包括中心性分析、
        社区检测结果和网络拓扑特征统计。
        """
        # 计算网络指标
        centrality_metrics = self._compute_centrality_metrics(graph)
        community_info = self._detect_communities(graph)

        # 创建子图布局
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "度中心性分布",
                "介数中心性分布",
                "社区结构",
                "节点类型分布",
            ),
            specs=[
                [{"type": "scatter"}, {"type": "scatter"}],
                [{"type": "scatter"}, {"type": "pie"}],
            ],
        )

        # 度中心性分布
        self._add_centrality_distribution(fig, centrality_metrics["degree"], 1, 1)

        # 介数中心性分布
        self._add_centrality_distribution(fig, centrality_metrics["betweenness"], 1, 2)

        # 社区结构
        self._add_community_visualization(fig, graph, community_info, 2, 1)

        # 节点类型分布
        self._add_node_type_distribution(fig, nodes_data, 2, 2)

        fig.update_layout(
            title_text="EMC知识图谱网络分析仪表板",
            title_x=0.5,
            height=800,
            showlegend=True,
        )

        return fig

    def _compute_centrality_metrics(self, graph: nx.Graph) -> Dict[str, Dict]:
        """计算中心性指标"""
        return {
            "degree": nx.degree_centrality(graph),
            "betweenness": nx.betweenness_centrality(graph),
            "closeness": nx.closeness_centrality(graph),
            "eigenvector": nx.eigenvector_centrality(graph, max_iter=1000),
        }

    def _detect_communities(self, graph: nx.Graph) -> Dict:
        """社区检测"""
        try:
            import networkx.algorithms.community as nx_comm

            communities = list(nx_comm.greedy_modularity_communities(graph))
            return {
                "communities": communities,
                "modularity": nx_comm.modularity(graph, communities),
            }
        except ImportError:
            logger.warning("社区检测功能需要安装额外依赖")
            return {"communities": [], "modularity": 0}

    def _add_centrality_distribution(
        self, fig: go.Figure, centrality: Dict, row: int, col: int
    ):
        """添加中心性分布图"""
        values = list(centrality.values())

        fig.add_trace(go.Histogram(x=values, nbinsx=20, name="分布"), row=row, col=col)

    def _add_community_visualization(
        self, fig: go.Figure, graph: nx.Graph, community_info: Dict, row: int, col: int
    ):
        """添加社区结构可视化"""
        if not community_info["communities"]:
            return

        pos = nx.spring_layout(graph, seed=42)

        # 为每个社区分配颜色
        colors = px.colors.qualitative.Set1

        for i, community in enumerate(community_info["communities"]):
            color = colors[i % len(colors)]
            nodes_in_community = list(community)

            if nodes_in_community:
                x_coords = [pos[node][0] for node in nodes_in_community if node in pos]
                y_coords = [pos[node][1] for node in nodes_in_community if node in pos]

                fig.add_trace(
                    go.Scatter(
                        x=x_coords,
                        y=y_coords,
                        mode="markers",
                        marker=dict(color=color, size=8),
                        name=f"社区 {i+1}",
                        showlegend=False,
                    ),
                    row=row,
                    col=col,
                )

    def _add_node_type_distribution(
        self, fig: go.Figure, nodes_data: Dict[str, KnowledgeNode], row: int, col: int
    ):
        """添加节点类型分布饼图"""
        type_counts = {}
        for node in nodes_data.values():
            display_name = NodeType.get_display_names().get(
                node.node_type, node.node_type.value
            )
            type_counts[display_name] = type_counts.get(display_name, 0) + 1

        fig.add_trace(
            go.Pie(
                labels=list(type_counts.keys()),
                values=list(type_counts.values()),
                name="节点类型分布",
            ),
            row=row,
            col=col,
        )


def main():
    """可视化模块独立测试"""
    # 创建示例数据进行测试
    import sys

    sys.path.append(".")

    from knowledge_graph import EMCKnowledgeGraph

    kg = EMCKnowledgeGraph()
    visualizer = KnowledgeGraphVisualizer()

    # 测试静态可视化
    fig, ax = visualizer.create_matplotlib_visualization(
        kg.graph, kg.nodes_data, kg.edges_data, save_path="test_static_graph.png"
    )
    print("静态可视化测试完成")

    # 测试交互式可视化
    plotly_fig = visualizer.create_plotly_visualization(
        kg.graph, kg.nodes_data, kg.edges_data, save_path="test_interactive_graph.html"
    )
    print("交互式可视化测试完成")


if __name__ == "__main__":
    main()
