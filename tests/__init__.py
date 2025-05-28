"""
Test Package for EMC Knowledge Graph System
汽车电子EMC标准知识图谱系统测试包

本测试包提供了知识图谱系统的全面测试覆盖，包括单元测试、
集成测试和性能测试。测试框架基于pytest，支持自动化测试
和持续集成。

测试模块结构:
- test_knowledge_graph.py: 核心知识图谱功能测试
- test_data_models.py: 数据模型和类型定义测试
- test_visualizer.py: 可视化引擎测试
- test_utils.py: 工具函数测试
- test_integration.py: 集成测试
- test_performance.py: 性能基准测试

Author: EMC Standards Research Team
Version: 1.0.0
"""

import os
import sys
from pathlib import Path

# 添加源码目录到Python路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# 测试配置
TEST_CONFIG = {
    "test_data_dir": project_root / "tests" / "test_data",
    "output_dir": project_root / "tests" / "output",
    "fixtures_dir": project_root / "tests" / "fixtures",
    "mock_data": True,
    "cleanup_after_tests": True,
    "performance_benchmark": False,
}

# 测试常量
TEST_STANDARDS = [
    "CISPR25",
    "CISPR12",
    "CISPR36",
    "ISO11452",
    "ISO11451",
    "ISO7637",
    "ECER10",
    "IEC61000",
]

TEST_ORGANIZATIONS = ["CISPR", "ISO", "SAE", "UNECE", "IEC"]

TEST_NODE_TYPES = [
    "organization",
    "standard",
    "regulation",
    "test_method",
    "test_environment",
    "vehicle_type",
]


# 测试工具函数
def setup_test_environment():
    """设置测试环境"""
    # 创建测试输出目录
    TEST_CONFIG["output_dir"].mkdir(exist_ok=True)
    TEST_CONFIG["fixtures_dir"].mkdir(exist_ok=True)

    # 设置环境变量
    os.environ["EMC_KG_TEST_MODE"] = "1"
    os.environ["EMC_KG_LOG_LEVEL"] = "DEBUG"


def cleanup_test_environment():
    """清理测试环境"""
    if TEST_CONFIG["cleanup_after_tests"]:
        import shutil

        if TEST_CONFIG["output_dir"].exists():
            shutil.rmtree(TEST_CONFIG["output_dir"])


def get_test_config():
    """获取测试配置"""
    return TEST_CONFIG.copy()


# 测试数据生成器
class TestDataGenerator:
    """测试数据生成器"""

    @staticmethod
    def create_mock_node(node_id: str = "test_node"):
        """创建模拟节点数据"""
        from data_models import KnowledgeNode, NodeType

        return KnowledgeNode(
            id=node_id,
            name=f"Test Node {node_id}",
            node_type=NodeType.STANDARD,
            description=f"Test description for {node_id}",
            attributes={"test": True, "mock": True},
            tags={"test", "mock"},
        )

    @staticmethod
    def create_mock_edge(source: str = "src", target: str = "tgt"):
        """创建模拟边数据"""
        from data_models import KnowledgeEdge, RelationType

        return KnowledgeEdge(
            source=source,
            target=target,
            relation_type=RelationType.REFERENCES,
            weight=0.8,
            confidence=0.9,
            attributes={"test": True},
        )

    @staticmethod
    def create_test_graph():
        """创建测试用知识图谱"""
        import networkx as nx

        from data_models import NodeType, RelationType

        graph = nx.DiGraph()

        # 添加测试节点
        test_nodes = [
            ("test_org", {"node_type": NodeType.ORGANIZATION.value}),
            ("test_std", {"node_type": NodeType.STANDARD.value}),
            ("test_method", {"node_type": NodeType.TEST_METHOD.value}),
        ]

        graph.add_nodes_from(test_nodes)

        # 添加测试边
        test_edges = [
            ("test_org", "test_std", {"relation_type": RelationType.DEVELOPS.value}),
            ("test_std", "test_method", {"relation_type": RelationType.INCLUDES.value}),
        ]

        graph.add_edges_from(test_edges)

        return graph


# 测试装饰器
def requires_test_data(func):
    """需要测试数据的装饰器"""

    def wrapper(*args, **kwargs):
        setup_test_environment()
        try:
            return func(*args, **kwargs)
        finally:
            if TEST_CONFIG["cleanup_after_tests"]:
                cleanup_test_environment()

    return wrapper


def skip_if_no_display(func):
    """无显示环境时跳过测试的装饰器"""
    import pytest

    def wrapper(*args, **kwargs):
        if "DISPLAY" not in os.environ and sys.platform.startswith("linux"):
            pytest.skip("No display available for GUI tests")
        return func(*args, **kwargs)

    return wrapper


# 测试断言辅助函数
def assert_valid_knowledge_graph(kg):
    """断言知识图谱有效性"""
    assert kg is not None, "Knowledge graph should not be None"
    assert hasattr(kg, "graph"), "Knowledge graph should have graph attribute"
    assert hasattr(kg, "nodes_data"), "Knowledge graph should have nodes_data"
    assert hasattr(kg, "edges_data"), "Knowledge graph should have edges_data"
    assert len(kg.nodes_data) > 0, "Knowledge graph should have nodes"


def assert_valid_node(node):
    """断言节点有效性"""
    from data_models import KnowledgeNode, NodeType

    assert isinstance(node, KnowledgeNode), "Should be KnowledgeNode instance"
    assert node.id, "Node should have valid ID"
    assert node.name, "Node should have valid name"
    assert isinstance(node.node_type, NodeType), "Node should have valid type"
    assert node.description, "Node should have description"


def assert_valid_edge(edge):
    """断言边有效性"""
    from data_models import KnowledgeEdge, RelationType

    assert isinstance(edge, KnowledgeEdge), "Should be KnowledgeEdge instance"
    assert edge.source, "Edge should have valid source"
    assert edge.target, "Edge should have valid target"
    assert isinstance(
        edge.relation_type, RelationType
    ), "Edge should have valid relation type"
    assert 0.0 <= edge.weight <= 1.0, "Edge weight should be between 0 and 1"
    assert 0.0 <= edge.confidence <= 1.0, "Edge confidence should be between 0 and 1"


# 性能测试辅助
class PerformanceBenchmark:
    """性能基准测试类"""

    def __init__(self):
        self.results = {}

    def time_function(self, func, *args, **kwargs):
        """测量函数执行时间"""
        import time

        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        func_name = func.__name__

        if func_name not in self.results:
            self.results[func_name] = []

        self.results[func_name].append(execution_time)

        return result, execution_time

    def get_average_time(self, func_name):
        """获取函数平均执行时间"""
        if func_name in self.results:
            times = self.results[func_name]
            return sum(times) / len(times)
        return None

    def get_benchmark_report(self):
        """获取性能基准报告"""
        report = {}
        for func_name, times in self.results.items():
            report[func_name] = {
                "average_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times),
                "total_calls": len(times),
            }
        return report


# 全局测试实例
test_data_generator = TestDataGenerator()
performance_benchmark = PerformanceBenchmark()

# 初始化测试环境
setup_test_environment()

__all__ = [
    "TEST_CONFIG",
    "TEST_STANDARDS",
    "TEST_ORGANIZATIONS",
    "TEST_NODE_TYPES",
    "TestDataGenerator",
    "test_data_generator",
    "performance_benchmark",
    "PerformanceBenchmark",
    "setup_test_environment",
    "cleanup_test_environment",
    "get_test_config",
    "requires_test_data",
    "skip_if_no_display",
    "assert_valid_knowledge_graph",
    "assert_valid_node",
    "assert_valid_edge",
]
