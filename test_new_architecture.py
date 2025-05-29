#!/usr/bin/env python3
"""新架构集成测试"""

def test_minimal_functionality():
    """测试最小功能集"""
    try:
        # 测试核心依赖
        import networkx as nx
        import yaml
        print("✓ 核心依赖OK")
        
        # 测试图引擎
        from src.core.graph_engine import GraphEngine, Triple
        engine = GraphEngine()
        
        triple = Triple("A", "relates_to", "B")
        success = engine.add_triple(triple)
        assert success, "三元组添加失败"
        print("✓ 图引擎OK")
        
        # 测试EMC本体
        from src.domain.emc_ontology import EMCOntologyManager
        ontology = EMCOntologyManager()
        print("✓ EMC本体OK")
        
        # 测试API接口
        from src.api.knowledge_graph_api import KnowledgeGraphAPI
        api = KnowledgeGraphAPI()
        success = api.build_knowledge_graph()
        assert success, "知识图谱构建失败"
        print("✓ API接口OK")
        
        print("\n🎉 新架构测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 新架构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_minimal_functionality()