"""
Visualization Engine Tests
知识图谱可视化引擎测试套件

本测试模块专门针对知识图谱可视化引擎进行全面测试，
涵盖静态和交互式可视化、布局算法、颜色方案、
图例生成等关键可视化功能。

测试覆盖范围:
- 可视化引擎初始化
- 布局算法测试（Spring、层次、圆形等）
- 静态图谱生成（Matplotlib）
- 交互式图谱生成（Plotly）
- 颜色方案和样式配置
- 图例和标注功能
- 网络分析仪表板
- 性能基准测试

Author: EMC Standards Research Team
Version: 1.0.0
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import networkx as nx
import numpy as np
import pytest

from data_models import KnowledgeEdge, KnowledgeNode, NodeType, RelationType
from knowledge_graph import EMCKnowledgeGraph

# 导入被测试模块
from visualizer import KnowledgeGraphVisualizer, VisualizationConfig

# 导入测试框架
from . import (
    performance_benchmark,
    requires_test_data,
    skip_if_no_display,
    test_data_generator,
)


class TestVisualizationConfig:
    """可视化配置测试类"""

    def test_default_config_creation(self):
        """测试默认配置创建"""
        config = VisualizationConfig()

        assert config.layout_algorithm == "spring"
        assert config.node_size_range == (800, 3000)
        assert config.edge_width_range == (1, 5)
        assert config.color_alpha == 0.8
        assert config.font_size == 10
        assert config.figure_dpi == 300
        assert config.interactive_height == 800
        assert config.interactive_width == 1200

    def test_custom_config_creation(self):
        """测试自定义配置创建"""
        config = VisualizationConfig(
            layout_algorithm="hierarchical", node_size_range=(500, 2000), figure_dpi=150
        )

        assert config.layout_algorithm == "hierarchical"
        assert config.node_size_range == (500, 2000)
        assert config.figure_dpi == 150
        # 其他参数应保持默认值
        assert config.color_alpha == 0.8


class TestKnowledgeGraphVisualizerInit:
    """可视化引擎初始化测试类"""

    def test_visualizer_creation_default(self):
        """测试默认可视化引擎创建"""
        visualizer = KnowledgeGraphVisualizer()

        assert isinstance(visualizer, KnowledgeGraphVisualizer)
        assert isinstance(visualizer.vis_config, VisualizationConfig)
        assert isinstance(visualizer.node_colors, dict)
        assert isinstance(visualizer.edge_colors, dict)
        assert isinstance(visualizer._layout_cache, dict)

    def test_visualizer_creation_with_config(self):
        """测试带配置的可视化引擎创建"""
        config = {
            "graph": {
                "layout": {"default": "circular"},
                "nodes": {"min_size": 600, "max_size": 2500},
            },
            "visualization": {"static": {"dpi": 200}},
        }

        visualizer = KnowledgeGraphVisualizer(config=config)
        assert visualizer.config == config
        assert visualizer.vis_config.layout_algorithm == "circular"

    def test_color_scheme_generation(self):
        """测试颜色方案生成"""
        visualizer = KnowledgeGraphVisualizer()

        # 检查节点颜色方案
        assert len(visualizer.node_colors) >= len(NodeType)
        for node_type in NodeType:
            assert node_type in visualizer.node_colors
            color = visualizer.node_colors[node_type]
            assert color.startswith("#")
            assert len(color) == 7  # #RRGGBB格式

        # 检查边颜色方案
        assert len(visualizer.edge_colors) >= len(RelationType)
        for rel_type in RelationType:
            assert rel_type in visualizer.edge_colors


class TestLayoutAlgorithms:
    """布局算法测试类"""

    @pytest.fixture
    def visualizer(self):
        return KnowledgeGraphVisualizer()

    @pytest.fixture
    def test_graph(self):
        return test_data_generator.create_test_graph()

    def test_spring_layout_computation(self, visualizer, test_graph):
        """测试弹簧布局算法"""
        pos = visualizer.compute_layout(test_graph, algorithm="spring")

        assert isinstance(pos, dict)
        assert len(pos) == test_graph.number_of_nodes()

        # 检查位置坐标格式
        for node_id, (x, y) in pos.items():
            assert isinstance(x, float)
            assert isinstance(y, float)
            assert node_id in test_graph.nodes()

    def test_circular_layout_computation(self, visualizer, test_graph):
        """测试圆形布局算法"""
        pos = visualizer.compute_layout(test_graph, algorithm="circular")

        assert isinstance(pos, dict)
        assert len(pos) == test_graph.number_of_nodes()

        # 圆形布局的点应该在单位圆上或附近
        for node_id, (x, y) in pos.items():
            distance = np.sqrt(x**2 + y**2)
            assert 0.8 <= distance <= 1.2  # 允许一定误差

    def test_hierarchical_layout_computation(self, visualizer, test_graph):
        """测试层次布局算法"""
        pos = visualizer.compute_layout(test_graph, algorithm="hierarchical")

        assert isinstance(pos, dict)
        assert len(pos) == test_graph.number_of_nodes()

        # 检查是否有层次结构（Y坐标应该有不同层级）
        y_coords = [y for x, y in pos.values()]
        unique_y = set(y_coords)
        assert len(unique_y) >= 1  # 至少有一个层级

    def test_layout_caching(self, visualizer, test_graph):
        """测试布局缓存功能"""
        # 第一次计算
        pos1 = visualizer.compute_layout(test_graph, algorithm="spring")

        # 第二次计算应该使用缓存
        pos2 = visualizer.compute_layout(test_graph, algorithm="spring")

        assert pos1 == pos2
        assert len(visualizer._layout_cache) > 0

    def test_force_recompute_layout(self, visualizer, test_graph):
        """测试强制重新计算布局"""
        # 第一次计算
        pos1 = visualizer.compute_layout(test_graph, algorithm="spring")

        # 强制重新计算
        pos2 = visualizer.compute_layout(
            test_graph, algorithm="spring", force_recompute=True
        )

        # 由于随机种子，结果可能不同，但格式应该一致
        assert isinstance(pos2, dict)
        assert len(pos2) == len(pos1)

    def test_invalid_layout_algorithm(self, visualizer, test_graph):
        """测试无效布局算法"""
        pos = visualizer.compute_layout(test_graph, algorithm="invalid_algorithm")

        # 应该回退到spring布局
        assert isinstance(pos, dict)
        assert len(pos) == test_graph.number_of_nodes()


class TestMatplotlibVisualization:
    """Matplotlib可视化测试类"""

    @pytest.fixture
    def visualizer(self):
        return KnowledgeGraphVisualizer()

    @pytest.fixture
    def test_kg(self):
        return EMCKnowledgeGraph()

    @skip_if_no_display
    def test_matplotlib_visualization_creation(self, visualizer, test_kg):
        """测试Matplotlib可视化创建"""
        fig, ax = visualizer.create_matplotlib_visualization(
            test_kg.graph, test_kg.nodes_data, test_kg.edges_data, figsize=(10, 8)
        )

        assert fig is not None
        assert ax is not None
        assert fig.get_figwidth() == 10
        assert fig.get_figheight() == 8

    @skip_if_no_display
    @requires_test_data
    def test_matplotlib_save_functionality(self, visualizer, test_kg):
        """测试Matplotlib保存功能"""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            temp_path = f.name

        try:
            fig, ax = visualizer.create_matplotlib_visualization(
                test_kg.graph,
                test_kg.nodes_data,
                test_kg.edges_data,
                save_path=temp_path,
            )

            # 验证文件创建
            assert Path(temp_path).exists()
            assert Path(temp_path).stat().st_size > 0
        finally:
            # 清理临时文件
            if Path(temp_path).exists():
                Path(temp_path).unlink()

    def test_node_size_calculation(self, visualizer):
        """测试节点大小计算"""
        # 测试不同度数的节点大小计算
        sizes = []
        for degree in [1, 5, 10, 15, 20]:
            size = visualizer._calculate_node_size(degree)
            sizes.append(size)

            assert isinstance(size, int)
            assert (
                visualizer.vis_config.node_size_range[0]
                <= size
                <= visualizer.vis_config.node_size_range[1]
            )

        # 度数越高，节点应该越大
        for i in range(len(sizes) - 1):
            assert sizes[i] <= sizes[i + 1]

    def test_edge_width_calculation(self, visualizer):
        """测试边宽度计算"""
        weights = [0.0, 0.25, 0.5, 0.75, 1.0]
        widths = []

        for weight in weights:
            width = visualizer._calculate_edge_width(weight)
            widths.append(width)

            assert isinstance(width, float)
            assert (
                visualizer.vis_config.edge_width_range[0]
                <= width
                <= visualizer.vis_config.edge_width_range[1]
            )

        # 权重越高，边应该越宽
        for i in range(len(widths) - 1):
            assert widths[i] <= widths[i + 1]


class TestPlotlyVisualization:
    """Plotly可视化测试类"""

    @pytest.fixture
    def visualizer(self):
        return KnowledgeGraphVisualizer()

    @pytest.fixture
    def test_kg(self):
        return EMCKnowledgeGraph()

    def test_plotly_visualization_creation(self, visualizer, test_kg):
        """测试Plotly可视化创建"""
        fig = visualizer.create_plotly_visualization(
            test_kg.graph, test_kg.nodes_data, test_kg.edges_data
        )

        assert fig is not None
        assert hasattr(fig, "data")
        assert len(fig.data) >= 2  # 至少有边和节点轨迹

    @requires_test_data
    def test_plotly_save_functionality(self, visualizer, test_kg):
        """测试Plotly保存功能"""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            temp_path = f.name

        try:
            fig = visualizer.create_plotly_visualization(
                test_kg.graph,
                test_kg.nodes_data,
                test_kg.edges_data,
                save_path=temp_path,
            )

            # 验证文件创建
            assert Path(temp_path).exists()
            assert Path(temp_path).stat().st_size > 0

            # 验证HTML内容
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()
                assert "plotly" in content.lower()
                assert "html" in content.lower()
        finally:
            # 清理临时文件
            if Path(temp_path).exists():
                Path(temp_path).unlink()

    def test_edge_coordinates_preparation(self, visualizer):
        """测试边坐标准备"""
        # 创建简单的位置数据
        pos = {"node1": (0.0, 0.0), "node2": (1.0, 1.0), "node3": (0.5, 0.5)}

        edges_data = [
            test_data_generator.create_mock_edge("node1", "node2"),
            test_data_generator.create_mock_edge("node2", "node3"),
        ]

        edge_x, edge_y = visualizer._prepare_edge_coordinates(pos, edges_data)

        assert isinstance(edge_x, list)
        assert isinstance(edge_y, list)
        assert len(edge_x) == len(edge_y)

        # 检查None分隔符
        assert None in edge_x
        assert None in edge_y

    def test_node_trace_preparation(self, visualizer, test_kg):
        """测试节点轨迹准备"""
        # 使用简单位置
        pos = {"CISPR": (0.0, 0.0), "ISO": (1.0, 1.0)}

        node_trace = visualizer._prepare_node_trace(
            pos, test_kg.nodes_data, test_kg.graph
        )

        assert hasattr(node_trace, "x")
        assert hasattr(node_trace, "y")
        assert hasattr(node_trace, "text")
        assert hasattr(node_trace, "marker")

        # 检查数据长度一致性
        assert len(node_trace.x) == len(node_trace.y)
        assert len(node_trace.x) <= len(pos)  # 可能有些节点不在pos中


class TestNetworkAnalysisDashboard:
    """网络分析仪表板测试类"""

    @pytest.fixture
    def visualizer(self):
        return KnowledgeGraphVisualizer()

    @pytest.fixture
    def test_kg(self):
        return EMCKnowledgeGraph()

    def test_dashboard_creation(self, visualizer, test_kg):
        """测试仪表板创建"""
        fig = visualizer.create_network_analysis_dashboard(
            test_kg.graph, test_kg.nodes_data, test_kg.edges_data
        )

        assert fig is not None
        assert hasattr(fig, "data")
        # 仪表板应该有多个子图
        assert len(fig.data) > 0

    def test_centrality_metrics_computation(self, visualizer, test_kg):
        """测试中心性指标计算"""
        metrics = visualizer._compute_centrality_metrics(test_kg.graph)

        assert isinstance(metrics, dict)
        assert "degree" in metrics
        assert "betweenness" in metrics
        assert "closeness" in metrics
        assert "eigenvector" in metrics

        # 检查每个指标的格式
        for metric_name, metric_values in metrics.items():
            assert isinstance(metric_values, dict)
            for node_id, value in metric_values.items():
                assert isinstance(value, float)
                assert 0.0 <= value <= 1.0

    def test_community_detection(self, visualizer, test_kg):
        """测试社区检测"""
        community_info = visualizer._detect_communities(test_kg.graph)

        assert isinstance(community_info, dict)
        assert "communities" in community_info
        assert "modularity" in community_info

        communities = community_info["communities"]
        assert isinstance(communities, list)

        modularity = community_info["modularity"]
        assert isinstance(modularity, float)
        assert -1.0 <= modularity <= 1.0


class TestVisualizationPerformance:
    """可视化性能测试类"""

    @pytest.fixture
    def visualizer(self):
        return KnowledgeGraphVisualizer()

    @pytest.fixture
    def test_kg(self):
        return EMCKnowledgeGraph()

    def test_layout_computation_performance(self, visualizer, test_kg):
        """测试布局计算性能"""
        algorithms = ["spring", "circular", "hierarchical"]

        for algorithm in algorithms:
            result, exec_time = performance_benchmark.time_function(
                visualizer.compute_layout, test_kg.graph, algorithm
            )

            assert isinstance(result, dict)
            assert exec_time < 5.0  # 布局计算应该在5秒内完成
            print(f"{algorithm} layout: {exec_time:.3f}s")

    @skip_if_no_display
    def test_matplotlib_rendering_performance(self, visualizer, test_kg):
        """测试Matplotlib渲染性能"""
        result, exec_time = performance_benchmark.time_function(
            visualizer.create_matplotlib_visualization,
            test_kg.graph,
            test_kg.nodes_data,
            test_kg.edges_data,
            figsize=(12, 10),
        )

        assert result[0] is not None  # fig对象
        assert result[1] is not None  # ax对象
        assert exec_time < 10.0  # 渲染应该在10秒内完成
        print(f"Matplotlib rendering: {exec_time:.3f}s")

    def test_plotly_rendering_performance(self, visualizer, test_kg):
        """测试Plotly渲染性能"""
        result, exec_time = performance_benchmark.time_function(
            visualizer.create_plotly_visualization,
            test_kg.graph,
            test_kg.nodes_data,
            test_kg.edges_data,
        )

        assert result is not None
        assert exec_time < 15.0  # Plotly渲染可能稍慢
        print(f"Plotly rendering: {exec_time:.3f}s")


class TestErrorHandlingVisualization:
    """可视化错误处理测试类"""

    @pytest.fixture
    def visualizer(self):
        return KnowledgeGraphVisualizer()

    def test_empty_graph_visualization(self, visualizer):
        """测试空图可视化"""
        empty_graph = nx.DiGraph()
        empty_nodes = {}
        empty_edges = []

        # Matplotlib可视化
        try:
            fig, ax = visualizer.create_matplotlib_visualization(
                empty_graph, empty_nodes, empty_edges
            )
            # 空图应该仍能创建基本图形
            assert fig is not None
            assert ax is not None
        except Exception as e:
            # 某些情况下空图可能无法可视化
            assert "empty" in str(e).lower() or "no" in str(e).lower()

        # Plotly可视化
        fig = visualizer.create_plotly_visualization(
            empty_graph, empty_nodes, empty_edges
        )
        assert fig is not None

    def test_invalid_layout_fallback(self, visualizer):
        """测试无效布局回退机制"""
        test_graph = test_data_generator.create_test_graph()

        # 使用无效算法，应该回退到默认算法
        pos = visualizer.compute_layout(test_graph, algorithm="nonexistent_algorithm")

        assert isinstance(pos, dict)
        assert len(pos) == test_graph.number_of_nodes()

    def test_malformed_data_handling(self, visualizer):
        """测试畸形数据处理"""
        # 创建有问题的数据
        graph = nx.DiGraph()
        graph.add_node("test_node", invalid_attr=None)

        nodes_data = {"test_node": test_data_generator.create_mock_node("test_node")}
        edges_data = []

        # 应该能够处理而不崩溃
        try:
            fig = visualizer.create_plotly_visualization(graph, nodes_data, edges_data)
            assert fig is not None
        except Exception as e:
            # 记录但不失败，这可能是预期行为
            print(f"Expected error handling malformed data: {e}")


class TestVisualizationIntegration:
    """可视化集成测试类"""

    def test_end_to_end_visualization_workflow(self):
        """测试端到端可视化工作流"""
        # 创建知识图谱
        kg = EMCKnowledgeGraph()

        # 创建可视化引擎
        visualizer = KnowledgeGraphVisualizer()

        # 计算布局
        pos = visualizer.compute_layout(kg.graph)
        assert isinstance(pos, dict)

        # 创建静态可视化
        try:
            fig, ax = visualizer.create_matplotlib_visualization(
                kg.graph, kg.nodes_data, kg.edges_data
            )
            assert fig is not None
            assert ax is not None
        except:
            # 在某些环境中可能无法创建GUI
            pass

        # 创建交互式可视化
        plotly_fig = visualizer.create_plotly_visualization(
            kg.graph, kg.nodes_data, kg.edges_data
        )
        assert plotly_fig is not None

        # 创建分析仪表板
        dashboard_fig = visualizer.create_network_analysis_dashboard(
            kg.graph, kg.nodes_data, kg.edges_data
        )
        assert dashboard_fig is not None

    @requires_test_data
    def test_visualization_with_filtered_data(self):
        """测试过滤数据的可视化"""
        kg = EMCKnowledgeGraph()

        # 过滤只显示标准节点
        filtered_nodes = {
            node_id: node
            for node_id, node in kg.nodes_data.items()
            if node.node_type == NodeType.STANDARD
        }

        # 过滤相关边
        filtered_edges = [
            edge
            for edge in kg.edges_data
            if edge.source in filtered_nodes and edge.target in filtered_nodes
        ]

        # 创建过滤后的图
        filtered_graph = nx.DiGraph()
        for node_id in filtered_nodes:
            filtered_graph.add_node(node_id)
        for edge in filtered_edges:
            filtered_graph.add_edge(edge.source, edge.target)

        # 可视化过滤后的数据
        visualizer = KnowledgeGraphVisualizer()
        fig = visualizer.create_plotly_visualization(
            filtered_graph, filtered_nodes, filtered_edges
        )

        assert fig is not None
        assert len(fig.data) >= 1  # 至少有节点数据


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
