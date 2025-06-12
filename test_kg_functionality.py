#!/usr/bin/env python3
"""
测试知识图谱功能
"""
import sys
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

async def test_knowledge_graph():
    """测试知识图谱功能"""
    try:
        from services.knowledge_graph.enhanced_neo4j_service import EnhancedNeo4jService
        
        print("🔧 测试知识图谱服务 (开发模式)")
        
        # 创建mock模式的服务
        service = EnhancedNeo4jService(
            uri="bolt://localhost:7687",
            username="neo4j", 
            password="password",
            mock_mode=True
        )
        
        # 测试创建节点
        print("📍 测试创建节点...")
        node_data_1 = {
            'label': 'EMC测试设备',
            'type': 'Equipment',
            'x': 100,
            'y': 100,
            'manufacturer': 'TestCorp',
            'model': 'EMC-2000'
        }
        
        node_id_1 = await service.create_node_interactive(node_data_1)
        print(f"✅ 创建节点成功: {node_id_1}")
        
        node_data_2 = {
            'label': 'IEC 61000-4-3',
            'type': 'Standard',
            'x': 300,
            'y': 100,
            'category': 'EMC标准',
            'frequency_range': '80 MHz - 1 GHz'
        }
        
        node_id_2 = await service.create_node_interactive(node_data_2)
        print(f"✅ 创建节点成功: {node_id_2}")
        
        # 测试创建关系
        print("🔗 测试创建关系...")
        rel_success = await service.create_relationship_interactive(
            source_id=node_id_1,
            target_id=node_id_2,
            rel_type="COMPLIES_WITH",
            properties={'compliance_level': 'Level 3'}
        )
        
        if rel_success:
            print("✅ 创建关系成功")
        else:
            print("❌ 创建关系失败")
        
        # 测试更新节点位置
        print("🎯 测试更新节点位置...")
        update_success = await service.update_node_position(node_id_1, 150, 150)
        
        if update_success:
            print("✅ 更新节点位置成功")
        else:
            print("❌ 更新节点位置失败")
        
        # 测试获取子图
        print("🗺️ 测试获取子图...")
        subgraph = await service.get_subgraph_with_layout(node_id_1)
        
        print(f"📊 子图数据:")
        print(f"   - 节点数量: {len(subgraph['nodes'])}")
        print(f"   - 关系数量: {len(subgraph['links'])}")
        
        if subgraph['nodes']:
            print("   节点详情:")
            for node in subgraph['nodes']:
                print(f"     * {node['label']} ({node['type']})")
        
        if subgraph['links']:
            print("   关系详情:")
            for link in subgraph['links']:
                print(f"     * {link['type']}: {link['source']} -> {link['target']}")
        
        # 关闭服务
        await service.close()
        
        print("\n🎉 知识图谱功能测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 知识图谱测试失败: {e}")
        return False

async def main():
    """主函数"""
    print("=" * 60)
    print("🧪 EMC知识图谱功能测试")
    print("=" * 60)
    
    success = await test_knowledge_graph()
    
    print()
    print("=" * 60)
    print("📋 测试结果汇总")
    print("=" * 60)
    
    if success:
        print("✅ 知识图谱功能正常 (开发模式)")
        print("📌 下一步: 安装Neo4j数据库以获得完整功能")
    else:
        print("❌ 知识图谱功能异常")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)