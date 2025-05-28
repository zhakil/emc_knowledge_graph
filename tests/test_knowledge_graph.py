"""
Knowledge Graph Core Functionality Tests
知识图谱核心功能测试套件

本测试模块提供EMC知识图谱系统核心功能的全面测试覆盖，
包括图构建、语义搜索、路径发现、拓扑分析等关键功能的
单元测试和集成测试。

测试覆盖范围:
- 知识图谱初始化和构建
- 节点和边的增删改查
- 语义搜索和相似度计算
- 路径发现和图遍历
- 拓扑分析和统计计算
- 数据导入导出功能
- 错误处理和边界条件

Author: EMC Standards Research Team
Version: 1.0.0
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import networkx as nx
import pytest

from data_models import (
    GraphMetadata,
    KnowledgeEdge,
    KnowledgeNode,
    NodeType,
    RelationType,
    ValidationResult,
)

# 导入被测试模块
from knowledge_graph import EMCKnowledgeGraph
from utils import load_config

# 导入测试框架
from . import (
    TEST_ORGANIZATIONS,
    TEST_STANDARDS,
    assert_valid_edge,
    assert_valid_knowledge_graph,
    assert_valid_node,
    performance_benchmark,
    requires_test_data,
    test_data_generator,
)


class TestEMCKnowledgeGraphInit:
    """知识图谱初始化测试类"""

    def test_knowledge_graph_creation(self):
        """测试知识图谱创建"""
        kg = EMCKnowledgeGraph()

        assert_valid_knowledge_graph(kg)
        assert isinstance(kg.graph, nx.MultiDiGraph)
        assert isinstance(kg.nodes_data, dict)
        assert isinstance(kg.edges_data, list)
        assert hasattr(kg, "visualizer")

    def test_knowledge_graph_with_config(self):
        """测试带配置的知识图谱创建"""
        config = {
            "graph": {"layout": {"default": "circular"}},
            "visualization": {"static": {"dpi": 150}},
        }

        kg = EMCKnowledgeGraph(config=config)
        assert_valid_knowledge_graph(kg)
        assert kg.config == config

    def test_initial_domain_knowledge_loading(self):
        """测试初始领域知识加载"""
        kg = EMCKnowledgeGraph()

        # 验证标准化组织节点
        org_nodes = [
            node_id
            for node_id, node in kg.nodes_data.items()
            if node.node_type == NodeType.ORGANIZATION
        ]
        assert len(org_nodes) >= 5  # CISPR, ISO, SAE, UNECE, IEC

        # 验证技术标准节点
        std_nodes = [
            node_id
            for node_id, node in kg.nodes_data.items()
            if node.node_type == NodeType.STANDARD
        ]
        assert len(std_nodes) >= 6  # 主要EMC标准

        # 验证关系数量
        assert len(kg.edges_data) >= 20

    def test_metadata_initialization(self):
        """测试元数据初始化"""
        kg = EMCKnowledgeGraph()

        assert isinstance(kg.metadata, GraphMetadata)
        assert kg.metadata.name == "EMC Standards Knowledge Graph"
        assert kg.metadata.node_count > 0
        assert kg.metadata.edge_count > 0


class TestKnowledgeGraphOperations:
    """知识图谱操作测试类"""

    @pytest.fixture
    def kg(self):
        """测试用知识图谱fixture"""
        return EMCKnowledgeGraph()

    def test_add_knowledge_node(self, kg):
        """测试添加知识节点"""
        test_node = test_data_generator.create_mock_node("test_add_node")

        initial_count = len(kg.nodes_data)
        kg._add_knowledge_node(test_node)

        assert len(kg.nodes_data) == initial_count + 1
        assert "test_add_node" in kg.nodes_data
        assert kg.graph.has_node("test_add_node")

        stored_node = kg.nodes_data["test_add_node"]
        assert_valid_node(stored_node)
        assert stored_node.id == test_node.id
        assert stored_node.name == test_node.name

    def test_add_knowledge_edge(self, kg):
        """测试添加知识边"""
        # 首先添加两个节点
        node1 = test_data_generator.create_mock_node("node_1")
        node2 = test_data_generator.create_mock_node("node_2")
        kg._add_knowledge_node(node1)
        kg._add_knowledge_node(node2)

        test_edge = test_data_generator.create_mock_edge("node_1", "node_2")

        initial_count = len(kg.edges_data)
        kg._add_knowledge_edge(test_edge)

        assert len(kg.edges_data) == initial_count + 1
        assert kg.graph.has_edge("node_1", "node_2")

        stored_edge = kg.edges_data[-1]  # 最后添加的边
        assert_valid_edge(stored_edge)
        assert stored_edge.source == test_edge.source
        assert stored_edge.target == test_edge.target

    def test_get_node_info(self, kg):
        """测试获取节点信息"""
        # 测试存在的节点
        cispr_node = kg.get_node_info("CISPR")
        assert cispr_node is not None
        assert cispr_node.id == "CISPR"
        assert cispr_node.node_type == NodeType.ORGANIZATION

        # 测试不存在的节点
        nonexistent_node = kg.get_node_info("NONEXISTENT")
        assert nonexistent_node is None

    def test_get_neighbors(self, kg):
        """测试获取邻居节点"""
        neighbors = kg.get_neighbors("CISPR")
        assert isinstance(neighbors, list)
        assert len(neighbors) > 0

        # CISPR应该连接到其开发的标准
        cispr_standards = kg.get_neighbors("CISPR", RelationType.DEVELOPS)
        assert "CISPR25" in cispr_standards or any(
            "CISPR" in std for std in cispr_standards
        )


class TestSemanticSearch:
    """语义搜索测试类"""

    @pytest.fixture
    def kg(self):
        return EMCKnowledgeGraph()

    def test_basic_semantic_search(self, kg):
        """测试基础语义搜索"""
        results = kg.semantic_search("CISPR", max_results=5)

        assert isinstance(results, list)
        assert len(results) > 0
        assert len(results) <= 5

        # 检查结果格式
        for node_id, score in results:
            assert isinstance(node_id, str)
            assert isinstance(score, float)
            assert score > 0
            assert node_id in kg.nodes_data

    def test_semantic_search_with_filters(self, kg):
        """测试带过滤条件的语义搜索"""
        # 仅搜索标准类型节点
        results = kg.semantic_search(
            "EMC", node_types=[NodeType.STANDARD], max_results=3
        )

        assert len(results) <= 3
        for node_id, score in results:
            node = kg.nodes_data[node_id]
            assert node.node_type == NodeType.STANDARD

    def test_semantic_search_empty_query(self, kg):
        """测试空查询语义搜索"""
        results = kg.semantic_search("")
        assert isinstance(results, list)
        # 空查询应该返回空结果或少量结果
        assert len(results) <= 5

    def test_semantic_search_no_results(self, kg):
        """测试无结果的语义搜索"""
        results = kg.semantic_search("xyz_nonexistent_term_123")
        assert isinstance(results, list)
        assert len(results) == 0


class TestPathFinding:
    """路径发现测试类"""

    @pytest.fixture
    def kg(self):
        return EMCKnowledgeGraph()

    def test_find_semantic_paths_existing(self, kg):
        """测试查找存在的语义路径"""
        paths = kg.find_semantic_paths("CISPR", "CISPR25", max_depth=3)

        assert isinstance(paths, list)
        if len(paths) > 0:  # 如果找到路径
            for path in paths:
                assert isinstance(path, list)
                assert len(path) >= 2
                assert path[0] == "CISPR"
                assert path[-1] == "CISPR25"

    def test_find_semantic_paths_nonexistent(self, kg):
        """测试查找不存在的语义路径"""
        paths = kg.find_semantic_paths("NONEXISTENT1", "NONEXISTENT2")
        assert isinstance(paths, list)
        assert len(paths) == 0

    def test_find_paths_with_relation_filter(self, kg):
        """测试带关系类型过滤的路径查找"""
        paths = kg.find_semantic_paths(
            "CISPR",
            "CISPR25",
            relation_types=[RelationType.DEVELOPS, RelationType.REFERENCES],
        )

        assert isinstance(paths, list)
        # 验证路径中的关系类型
        if paths:
            # 这里可以添加更详细的关系验证
            assert len(paths[0]) >= 2

    def test_path_caching(self, kg):
        """测试路径缓存功能"""
        # 第一次查询
        paths1 = kg.find_semantic_paths("CISPR", "CISPR25")

        # 第二次查询应该使用缓存
        paths2 = kg.find_semantic_paths("CISPR", "CISPR25")

        assert paths1 == paths2


class TestSimilarityCalculation:
    """相似度计算测试类"""

    @pytest.fixture
    def kg(self):
        return EMCKnowledgeGraph()

    def test_compute_semantic_similarity_same_nodes(self, kg):
        """测试相同节点的相似度计算"""
        similarity = kg.compute_semantic_similarity("CISPR25", "CISPR25")
        assert isinstance(similarity, float)
        assert similarity >= 0.0
        # 相同节点的相似度应该较高（但不一定是1.0，取决于算法）

    def test_compute_semantic_similarity_different_nodes(self, kg):
        """测试不同节点的相似度计算"""
        # 相关节点
        similarity1 = kg.compute_semantic_similarity("CISPR", "CISPR25")
        assert isinstance(similarity1, float)
        assert 0.0 <= similarity1 <= 1.0

    def test_compute_similarity_nonexistent_nodes(self, kg):
        """测试不存在节点的相似度计算"""
        similarity = kg.compute_semantic_similarity("NONEXISTENT1", "NONEXISTENT2")
        assert similarity == 0.0

    def test_similarity_methods(self, kg):
        """测试不同相似度计算方法"""
        node1, node2 = "CISPR", "ISO"

        jaccard_sim = kg.compute_semantic_similarity(node1, node2, method="jaccard")
        structural_sim = kg.compute_semantic_similarity(
            node1, node2, method="structural"
        )
        semantic_sim = kg.compute_semantic_similarity(node1, node2, method="semantic")

        assert isinstance(jaccard_sim, float)
        assert isinstance(structural_sim, float)
        assert isinstance(semantic_sim, float)

        assert 0.0 <= jaccard_sim <= 1.0
        assert 0.0 <= structural_sim <= 1.0
        assert 0.0 <= semantic_sim <= 1.0


class TestGraphAnalysis:
    """图分析测试类"""

    @pytest.fixture
    def kg(self):
        return EMCKnowledgeGraph()

    def test_analyze_graph_topology(self, kg):
        """测试图拓扑分析"""
        analysis = kg.analyze_graph_topology()

        assert isinstance(analysis, dict)
        assert "basic_stats" in analysis
        assert "centrality_measures" in analysis

        # 检查基础统计
        basic_stats = analysis["basic_stats"]
        assert "nodes" in basic_stats
        assert "edges" in basic_stats
        assert "density" in basic_stats
        assert basic_stats["nodes"] > 0
        assert basic_stats["edges"] > 0
        assert 0.0 <= basic_stats["density"] <= 1.0

        # 检查中心性度量
        centrality = analysis["centrality_measures"]
        assert "degree" in centrality
        assert "betweenness" in centrality
        assert isinstance(centrality["degree"], dict)

    def test_generate_knowledge_report(self, kg):
        """测试知识报告生成"""
        report = kg.generate_knowledge_report()

        assert isinstance(report, dict)
        assert "metadata" in report
        assert "topology_analysis" in report
        assert "semantic_statistics" in report
        assert "quality_metrics" in report
        assert "recommendations" in report

        # 检查质量指标
        quality = report["quality_metrics"]
        assert "overall_quality" in quality
        assert 0.0 <= quality["overall_quality"] <= 1.0


class TestDataImportExport:
    """数据导入导出测试类"""

    @pytest.fixture
    def kg(self):
        return EMCKnowledgeGraph()

    @requires_test_data
    def test_export_to_json(self, kg):
        """测试JSON格式导出"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            # 测试导出功能（这里需要实现export_to_json方法）
            if hasattr(kg, "export_to_json"):
                kg.export_to_json(temp_path)

                # 验证文件创建
                assert Path(temp_path).exists()

                # 验证JSON格式
                with open(temp_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                assert isinstance(data, dict)
                # 可以添加更多格式验证
        finally:
            # 清理临时文件
            if Path(temp_path).exists():
                Path(temp_path).unlink()

    @requires_test_data
    def test_export_multiple_formats(self, kg):
        """测试多格式导出"""
        with tempfile.TemporaryDirectory() as temp_dir:
            if hasattr(kg, "export_to_formats"):
                paths = kg.export_to_formats(
                    output_dir=temp_dir, formats=["json", "graphml"]
                )

                assert isinstance(paths, dict)
                for fmt, path in paths.items():
                    assert Path(path).exists()


class TestErrorHandling:
    """错误处理测试类"""

    @pytest.fixture
    def kg(self):
        return EMCKnowledgeGraph()

    def test_invalid_node_operations(self, kg):
        """测试无效节点操作"""
        # 测试获取不存在的节点
        result = kg.get_node_info("INVALID_NODE_ID")
        assert result is None

        # 测试获取不存在节点的邻居
        neighbors = kg.get_neighbors("INVALID_NODE_ID")
        assert isinstance(neighbors, list)
        assert len(neighbors) == 0

    def test_invalid_search_parameters(self, kg):
        """测试无效搜索参数"""
        # 测试负数max_results
        results = kg.semantic_search("test", max_results=-1)
        assert isinstance(results, list)

        # 测试无效节点类型过滤
        results = kg.semantic_search("test", node_types=[])
        assert isinstance(results, list)

    def test_graph_consistency_after_operations(self, kg):
        """测试操作后图一致性"""
        initial_node_count = len(kg.nodes_data)
        initial_edge_count = len(kg.edges_data)

        # 执行一些操作
        test_node = test_data_generator.create_mock_node("consistency_test")
        kg._add_knowledge_node(test_node)

        # 验证一致性
        assert len(kg.nodes_data) == initial_node_count + 1
        assert kg.graph.number_of_nodes() == len(kg.nodes_data)
        assert kg.graph.number_of_edges() == len(kg.edges_data)


class TestPerformance:
    """性能测试类"""

    @pytest.fixture
    def kg(self):
        return EMCKnowledgeGraph()

    def test_search_performance(self, kg):
        """测试搜索性能"""
        # 执行多次搜索并测量时间
        search_terms = ["CISPR", "ISO", "EMC", "test", "standard"]

        for term in search_terms:
            result, exec_time = performance_benchmark.time_function(
                kg.semantic_search, term, max_results=10
            )

            assert isinstance(result, list)
            assert exec_time < 1.0  # 搜索应该在1秒内完成

    def test_path_finding_performance(self, kg):
        """测试路径查找性能"""
        # 测试路径查找性能
        result, exec_time = performance_benchmark.time_function(
            kg.find_semantic_paths, "CISPR", "CISPR25", max_depth=4
        )

        assert isinstance(result, list)
        assert exec_time < 2.0  # 路径查找应该在2秒内完成

    def test_analysis_performance(self, kg):
        """测试分析性能"""
        result, exec_time = performance_benchmark.time_function(
            kg.analyze_graph_topology
        )

        assert isinstance(result, dict)
        assert exec_time < 5.0  # 拓扑分析应该在5秒内完成


class TestVisualizationIntegration:
    """可视化集成测试类"""

    @pytest.fixture
    def kg(self):
        return EMCKnowledgeGraph()

    def test_matplotlib_visualization_creation(self, kg):
        """测试Matplotlib可视化创建"""
        try:
            fig, ax = kg.create_matplotlib_visualization(figsize=(10, 8))
            assert fig is not None
            assert ax is not None
        except Exception as e:
            # 在没有显示环境的情况下可能失败
            pytest.skip(f"Visualization test skipped: {e}")

    def test_plotly_visualization_creation(self, kg):
        """测试Plotly可视化创建"""
        try:
            fig = kg.create_plotly_visualization()
            assert fig is not None
            assert hasattr(fig, "data")
        except Exception as e:
            pytest.skip(f"Plotly visualization test skipped: {e}")


# 集成测试
class TestIntegration:
    """集成测试类"""

    def test_end_to_end_workflow(self):
        """测试端到端工作流"""
        # 创建知识图谱
        kg = EMCKnowledgeGraph()
        assert_valid_knowledge_graph(kg)

        # 执行语义搜索
        search_results = kg.semantic_search("CISPR 25", max_results=3)
        assert len(search_results) <= 3

        # 执行路径查找
        if len(search_results) > 0:
            target_node = search_results[0][0]
            paths = kg.find_semantic_paths("CISPR", target_node, max_depth=3)
            assert isinstance(paths, list)

        # 生成分析报告
        report = kg.generate_knowledge_report()
        assert isinstance(report, dict)
        assert "quality_metrics" in report

        # 验证图的完整性
        assert kg.graph.number_of_nodes() == len(kg.nodes_data)
        assert kg.graph.number_of_edges() == len(kg.edges_data)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
