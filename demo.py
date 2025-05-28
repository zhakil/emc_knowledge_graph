#!/usr/bin/env python3
"""
EMC Knowledge Graph System Demonstration
汽车电子EMC标准知识图谱系统综合演示

这是一个全面的演示脚本，展示EMC知识图谱系统的核心功能，
包括知识建模、语义搜索、路径发现、可视化生成、分析报告等。
适用于产品展示、教学演示和功能验证。

核心演示内容：
• 知识图谱构建与统计分析
• 智能语义搜索引擎
• 多维路径发现算法
• 交互式可视化生成
• 网络拓扑深度分析
• 实际应用场景模拟
• 性能基准测试

Author: EMC Standards Research Team
Version: 1.0.0
Usage: python demo.py [--interactive] [--save-all] [--benchmark]
"""

import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
import json

# 添加源码路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 导入核心模块
from knowledge_graph import EMCKnowledgeGraph
from data_models import NodeType, RelationType
from utils import setup_logging, ensure_directory
from visualizer import KnowledgeGraphVisualizer

class EMCKnowledgeGraphDemo:
    """
    EMC知识图谱系统演示类
    
    提供完整的系统功能演示，包括交互式和自动化两种模式。
    支持性能基准测试和详细的演示报告生成。
    """
    
    def __init__(self, interactive=False, save_outputs=True, benchmark=False):
        """
        初始化演示环境
        
        Args:
            interactive: 是否启用交互式演示
            save_outputs: 是否保存输出文件
            benchmark: 是否执行性能基准测试
        """
        self.interactive = interactive
        self.save_outputs = save_outputs
        self.benchmark = benchmark
        
        # 设置日志
        setup_logging()
        
        # 创建输出目录
        if save_outputs:
            self.output_dir = Path("demo_output")
            ensure_directory(self.output_dir)
            ensure_directory(self.output_dir / "visualizations")
            ensure_directory(self.output_dir / "reports")
            ensure_directory(self.output_dir / "exports")
        
        # 演示统计
        self.demo_stats = {
            'start_time': datetime.now(),
            'sections_completed': 0,
            'total_sections': 8,
            'benchmark_results': {}
        }
        
        print("🚀 EMC知识图谱系统演示启动")
        print("=" * 80)
        self._display_banner()
    
    def _display_banner(self):
        """显示演示横幅"""
        banner = """
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                    汽车电子EMC标准知识图谱系统                            ║
    ║                   Automotive EMC Standards Knowledge Graph                ║
    ║                                                                          ║
    ║  🧠 智能语义建模  📊 交互式可视化  🔍 路径发现  📈 深度分析               ║
    ╚══════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
        if self.interactive:
            input("\n按Enter键开始演示...")
    
    def run_complete_demo(self):
        """运行完整演示流程"""
        try:
            # 演示章节
            demo_sections = [
                ("系统初始化", self._demo_system_initialization),
                ("知识图谱分析", self._demo_graph_analysis), 
                ("语义搜索引擎", self._demo_semantic_search),
                ("路径发现算法", self._demo_path_discovery),
                ("相似度计算", self._demo_similarity_computation),
                ("可视化生成", self._demo_visualization_generation),
                ("应用场景模拟", self._demo_application_scenarios),
                ("性能基准测试", self._demo_performance_benchmark)
            ]
            
            for section_name, section_func in demo_sections:
                self._run_demo_section(section_name, section_func)
            
            # 生成演示报告
            self._generate_demo_report()
            
            print("\n🎉 演示完成！")
            self._display_completion_summary()
            
        except KeyboardInterrupt:
            print("\n\n⚠️ 演示被用户中断")
            self._generate_demo_report()
        except Exception as e:
            print(f"\n❌ 演示过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
    
    def _run_demo_section(self, section_name, section_func):
        """运行单个演示章节"""
        print(f"\n{'='*20} {section_name} {'='*20}")
        
        if self.interactive:
            input(f"准备开始 '{section_name}' 演示，按Enter继续...")
        
        start_time = time.time()
        
        try:
            section_func()
            execution_time = time.time() - start_time
            
            if self.benchmark:
                self.demo_stats['benchmark_results'][section_name] = execution_time
            
            self.demo_stats['sections_completed'] += 1
            print(f"✅ {section_name} 完成 (耗时: {execution_time:.2f}秒)")
            
        except Exception as e:
            print(f"❌ {section_name} 执行失败: {e}")
            if self.interactive:
                input("按Enter继续下一个演示章节...")
    
    def _demo_system_initialization(self):
        """演示系统初始化"""
        print("🔧 正在初始化EMC知识图谱系统...")
        
        # 创建知识图谱实例
        self.kg = EMCKnowledgeGraph()
        
        # 显示初始化信息
        print(f"  ✓ 知识图谱引擎初始化完成")
        print(f"  ✓ 节点数量: {len(self.kg.nodes_data)}")
        print(f"  ✓ 关系数量: {len(self.kg.edges_data)}")
        print(f"  ✓ 图密度: {self.kg.graph.number_of_edges() / (self.kg.graph.number_of_nodes() * (self.kg.graph.number_of_nodes() - 1)):.4f}")
        
        # 显示节点类型分布
        node_type_stats = {}
        for node in self.kg.nodes_data.values():
            node_type = node.node_type.value
            node_type_stats[node_type] = node_type_stats.get(node_type, 0) + 1
        
        print(f"\n📊 实体类型分布:")
        for node_type, count in sorted(node_type_stats.items()):
            print(f"  • {node_type}: {count}个")
        
        # 显示重要实体示例
        print(f"\n🏢 主要标准化组织:")
        orgs = [node_id for node_id, node in self.kg.nodes_data.items() 
                if node.node_type == NodeType.ORGANIZATION][:5]
        for org_id in orgs:
            org = self.kg.nodes_data[org_id]
            print(f"  • {org.name}")
        
        print(f"\n📋 核心EMC标准:")
        standards = [node_id for node_id, node in self.kg.nodes_data.items() 
                    if node.node_type == NodeType.STANDARD][:6]
        for std_id in standards:
            std = self.kg.nodes_data[std_id]
            print(f"  • {std.name}")
    
    def _demo_graph_analysis(self):
        """演示图分析功能"""
        print("📈 执行知识图谱深度分析...")
        
        # 拓扑分析
        topology = self.kg.analyze_graph_topology()
        
        print(f"\n🔍 拓扑分析结果:")
        basic_stats = topology['basic_stats']
        print(f"  • 图连通性: {'连通' if basic_stats['is_connected'] else '不连通'}")
        print(f"  • 图密度: {basic_stats['density']:.4f}")
        
        if 'path_metrics' in topology:
            path_metrics = topology['path_metrics']
            print(f"  • 平均路径长度: {path_metrics.get('average_shortest_path', 'N/A')}")
            print(f"  • 图直径: {path_metrics.get('diameter', 'N/A')}")
        
        # 中心性分析
        centrality = topology['centrality_measures']
        
        print(f"\n🎯 中心性分析 - 最重要的实体:")
        
        # 度中心性Top 5
        degree_centrality = sorted(centrality['degree'].items(), 
                                 key=lambda x: x[1], reverse=True)[:5]
        print(f"  📊 度中心性Top 5:")
        for i, (node_id, score) in enumerate(degree_centrality, 1):
            node_name = self.kg.nodes_data[node_id].name
            print(f"    {i}. {node_name} ({score:.3f})")
        
        # 介数中心性Top 5  
        betweenness_centrality = sorted(centrality['betweenness'].items(),
                                      key=lambda x: x[1], reverse=True)[:5]
        print(f"  🌉 介数中心性Top 5:")
        for i, (node_id, score) in enumerate(betweenness_centrality, 1):
            node_name = self.kg.nodes_data[node_id].name
            print(f"    {i}. {node_name} ({score:.3f})")
        
        # 生成完整分析报告
        print(f"\n📋 生成综合分析报告...")
        report = self.kg.generate_knowledge_report()
        
        quality_metrics = report['quality_metrics']
        print(f"  • 数据质量评分: {quality_metrics['overall_quality']:.3f}")
        print(f"  • 完整性评分: {quality_metrics['completeness']:.3f}")
        print(f"  • 一致性评分: {quality_metrics['consistency']:.3f}")
        
        if self.save_outputs:
            report_path = self.output_dir / "reports" / "analysis_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            print(f"  ✓ 详细报告已保存: {report_path}")
    
    def _demo_semantic_search(self):
        """演示语义搜索功能"""
        print("🔍 演示智能语义搜索引擎...")
        
        # 搜索测试用例
        search_cases = [
            ("CISPR 25", "查找CISPR 25相关标准"),
            ("电动车 EMC", "电动车EMC相关内容"),
            ("辐射发射测试", "辐射发射测试方法"),
            ("抗扰度", "抗扰度相关标准和方法"),
            ("ISO", "ISO组织相关内容")
        ]
        
        print(f"\n🎯 语义搜索演示:")
        
        for query, description in search_cases:
            print(f"\n  🔎 搜索: '{query}' ({description})")
            
            results = self.kg.semantic_search(query, max_results=3)
            
            if results:
                for i, (node_id, score) in enumerate(results, 1):
                    node = self.kg.nodes_data[node_id]
                    node_type_name = NodeType.get_display_names().get(node.node_type, node.node_type.value)
                    print(f"    {i}. {node.name}")
                    print(f"       类型: {node_type_name} | 相关度: {score:.3f}")
                    if len(node.description) > 100:
                        print(f"       描述: {node.description[:100]}...")
                    else:
                        print(f"       描述: {node.description}")
            else:
                print(f"    无匹配结果")
        
        # 高级搜索功能演示
        print(f"\n🔬 高级搜索功能:")
        
        # 按类型过滤搜索
        standard_results = self.kg.semantic_search(
            "EMC", 
            node_types=[NodeType.STANDARD],
            max_results=3
        )
        print(f"  • 仅搜索标准类型: 找到{len(standard_results)}个结果")
        for node_id, score in standard_results:
            node = self.kg.nodes_data[node_id]
            print(f"    - {node.name} ({score:.3f})")
        
        # 测试搜索性能
        if self.benchmark:
            import time
            search_terms = ["CISPR", "ISO", "电动车", "测试", "标准"]
            total_time = 0
            
            for term in search_terms:
                start_time = time.time()
                results = self.kg.semantic_search(term, max_results=5)
                search_time = time.time() - start_time
                total_time += search_time
            
            avg_time = total_time / len(search_terms)
            print(f"  • 搜索性能: 平均响应时间 {avg_time*1000:.1f}ms")
    
    def _demo_path_discovery(self):
        """演示路径发现功能"""
        print("🔗 演示智能路径发现算法...")
        
        # 路径发现测试用例
        path_cases = [
            ("CISPR", "CISPR25", "从组织到标准的制定路径"),
            ("ECER10", "ElectricVehicles", "从法规到车辆类型的适用路径"),
            ("ISO11452", "AnechoicChamber", "从标准到测试环境的实施路径"),
            ("CISPR25", "RadiatedEmissions", "从标准到测试方法的包含路径")
        ]
        
        print(f"\n🎯 路径发现演示:")
        
        for source, target, description in path_cases:
            print(f"\n  🔍 路径查询: {description}")
            print(f"    源点: {source} → 目标: {target}")
            
            paths = self.kg.find_semantic_paths(source, target, max_depth=4)
            
            if paths:
                print(f"    发现 {len(paths)} 条路径:")
                
                for i, path in enumerate(paths[:3], 1):  # 只显示前3条路径
                    path_names = []
                    for node_id in path:
                        if node_id in self.kg.nodes_data:
                            path_names.append(self.kg.nodes_data[node_id].name)
                        else:
                            path_names.append(node_id)
                    
                    print(f"      路径{i}: {' → '.join(path_names)}")
                    print(f"             长度: {len(path)} 步")
                
                if len(paths) > 3:
                    print(f"      ... 还有 {len(paths) - 3} 条路径")
            else:
                print(f"    未找到连接路径")
        
        # 关系类型过滤路径发现
        print(f"\n🔬 高级路径发现:")
        
        # 仅通过"制定"和"引用"关系的路径
        filtered_paths = self.kg.find_semantic_paths(
            'CISPR', 'ElectricVehicles',
            max_depth=5,
            relation_types=[RelationType.DEVELOPS, RelationType.REFERENCES, RelationType.APPLIES_TO]
        )
        
        if filtered_paths:
            print(f"  • 制定-引用-适用路径: 找到{len(filtered_paths)}条")
            if filtered_paths:
                path = filtered_paths[0]
                path_names = [self.kg.nodes_data[node_id].name for node_id in path]
                print(f"    示例: {' → '.join(path_names)}")
        else:
            print(f"  • 特定关系类型路径: 未找到")
        
        # 路径发现性能测试
        if self.benchmark:
            import time
            test_pairs = [('CISPR', 'CISPR25'), ('ISO', 'ISO11452'), ('UNECE', 'ECER10')]
            
            total_time = 0
            for source, target in test_pairs:
                start_time = time.time()
                paths = self.kg.find_semantic_paths(source, target, max_depth=3)
                path_time = time.time() - start_time
                total_time += path_time
            
            avg_time = total_time / len(test_pairs)
            print(f"  • 路径发现性能: 平均响应时间 {avg_time*1000:.1f}ms")
    
    def _demo_similarity_computation(self):
        """演示相似度计算功能"""
        print("📐 演示语义相似度计算...")
        
        # 相似度计算测试用例
        similarity_cases = [
            ("CISPR25", "CISPR12", "同组织标准间相似度"),
            ("ISO11452", "ISO11451", "同系列标准相似度"),
            ("RadiatedEmissions", "ConductedEmissions", "相关测试方法相似度"),
            ("CISPR", "ISO", "不同组织间相似度"),
            ("ElectricVehicles", "ConventionalVehicles", "不同车辆类型相似度")
        ]
        
        print(f"\n🎯 相似度计算演示:")
        
        for node1, node2, description in similarity_cases:
            if node1 in self.kg.nodes_data and node2 in self.kg.nodes_data:
                print(f"\n  📊 {description}")
                print(f"    对比: {self.kg.nodes_data[node1].name}")
                print(f"       vs {self.kg.nodes_data[node2].name}")
                
                # 不同算法的相似度计算
                methods = ['jaccard', 'structural', 'semantic']
                for method in methods:
                    similarity = self.kg.compute_semantic_similarity(node1, node2, method=method)
                    print(f"    {method.capitalize()}相似度: {similarity:.3f}")
        
        # 相似度矩阵演示
        print(f"\n🔬 核心标准相似度矩阵:")
        
        core_standards = ['CISPR25', 'CISPR12', 'ISO11452', 'ISO11451']
        available_standards = [std for std in core_standards if std in self.kg.nodes_data]
        
        if len(available_standards) >= 2:
            print(f"    {'':>12}", end='')
            for std in available_standards:
                print(f"{std:>10}", end='')
            print()
            
            for std1 in available_standards:
                print(f"    {std1:>12}", end='')
                for std2 in available_standards:
                    if std1 == std2:
                        print(f"{'1.000':>10}", end='')
                    else:
                        sim = self.kg.compute_semantic_similarity(std1, std2, method='semantic')
                        print(f"{sim:>10.3f}", end='')
                print()
    
    def _demo_visualization_generation(self):
        """演示可视化生成功能"""
        print("🎨 演示知识图谱可视化生成...")
        
        try:
            # 静态可视化
            print(f"\n📊 生成静态知识图谱...")
            
            if self.save_outputs:
                static_path = self.output_dir / "visualizations" / "knowledge_graph_static.png"
                fig, ax = self.kg.create_matplotlib_visualization(
                    figsize=(16, 12),
                    save_path=str(static_path),
                    title="EMC标准知识图谱 - 演示版本"
                )
                print(f"  ✓ 静态图谱已保存: {static_path}")
            else:
                fig, ax = self.kg.create_matplotlib_visualization(figsize=(12, 10))
                print(f"  ✓ 静态图谱已生成")
            
            # 交互式可视化
            print(f"\n🌐 生成交互式知识图谱...")
            
            if self.save_outputs:
                interactive_path = self.output_dir / "visualizations" / "knowledge_graph_interactive.html"
                plotly_fig = self.kg.create_plotly_visualization(
                    save_path=str(interactive_path),
                    title="EMC标准知识图谱 - 交互式演示"
                )
                print(f"  ✓ 交互式图谱已保存: {interactive_path}")
            else:
                plotly_fig = self.kg.create_plotly_visualization()
                print(f"  ✓ 交互式图谱已生成")
            
            # 分析仪表板
            print(f"\n📈 生成网络分析仪表板...")
            
            dashboard_fig = self.kg.create_analysis_dashboard()
            
            if self.save_outputs:
                dashboard_path = self.output_dir / "visualizations" / "analysis_dashboard.html"
                dashboard_fig.write_html(str(dashboard_path))
                print(f"  ✓ 分析仪表板已保存: {dashboard_path}")
            else:
                print(f"  ✓ 分析仪表板已生成")
            
            # 可视化特性说明
            print(f"\n✨ 可视化特性:")
            print(f"  • 节点颜色: 按实体类型自动着色")
            print(f"  • 节点大小: 基于连接度动态调整")
            print(f"  • 边的粗细: 基于关系权重渲染")
            print(f"  • 布局算法: 智能力导向布局优化")
            print(f"  • 交互功能: 缩放、平移、悬停信息")
            print(f"  • 中文支持: 完整的中文字体渲染")
            
        except Exception as e:
            print(f"  ⚠️ 可视化生成遇到问题: {e}")
            print(f"  提示: 某些环境可能缺少图形界面支持")
    
    def _demo_application_scenarios(self):
        """演示实际应用场景"""
        print("🏭 演示实际应用场景...")
        
        # 场景1: EMC工程师标准查询
        print(f"\n📋 场景1: EMC工程师标准查询")
        print(f"  需求: 为新的电动车项目确定所需EMC标准")
        
        # 搜索电动车相关标准
        ev_standards = self.kg.semantic_search("电动车 EMC 标准", max_results=5)
        print(f"  步骤1: 搜索电动车EMC标准")
        for i, (node_id, score) in enumerate(ev_standards, 1):
            node = self.kg.nodes_data[node_id]
            print(f"    {i}. {node.name} (相关度: {score:.3f})")
        
        # 查找测试方法
        if ev_standards:
            std_id = ev_standards[0][0]
            print(f"\n  步骤2: 查找 {self.kg.nodes_data[std_id].name} 的测试方法")
            test_methods = self.kg.get_neighbors(std_id)
            method_nodes = [nid for nid in test_methods 
                          if nid in self.kg.nodes_data and 
                          self.kg.nodes_data[nid].node_type == NodeType.TEST_METHOD]
            
            for method_id in method_nodes[:3]:
                method = self.kg.nodes_data[method_id]
                print(f"    • {method.name}")
        
        # 场景2: 测试实验室能力规划
        print(f"\n🔬 场景2: 测试实验室能力规划")
        print(f"  需求: 规划实验室测试设备和环境配置")
        
        # 查找测试环境
        test_environments = [node_id for node_id, node in self.kg.nodes_data.items()
                           if node.node_type == NodeType.TEST_ENVIRONMENT]
        
        print(f"  推荐测试环境配置:")
        for env_id in test_environments[:4]:
            env = self.kg.nodes_data[env_id]
            print(f"    • {env.name}")
            
            # 查找使用该环境的测试方法
            using_methods = []
            for edge in self.kg.edges_data:
                if (edge.target == env_id and 
                    edge.relation_type == RelationType.USES and
                    edge.source in self.kg.nodes_data):
                    using_methods.append(self.kg.nodes_data[edge.source].name)
            
            if using_methods:
                print(f"      用途: {', '.join(using_methods[:2])}")
        
        # 场景3: 法规合规路径分析
        print(f"\n⚖️ 场景3: 法规合规路径分析")
        print(f"  需求: 分析产品从开发到法规认证的完整路径")
        
        # 查找从法规到具体要求的路径
        compliance_paths = self.kg.find_semantic_paths('ECER10', 'CISPR25', max_depth=3)
        if compliance_paths:
            path = compliance_paths[0]
            path_names = [self.kg.nodes_data[node_id].name for node_id in path]
            print(f"  合规路径: {' → '.join(path_names)}")
        
        # 场景4: 标准演进趋势分析
        print(f"\n📈 场景4: 标准演进趋势分析")
        print(f"  需求: 分析EMC标准的发展趋势和技术方向")
        
        # 分析标准间的扩展和取代关系
        evolution_relations = []
        for edge in self.kg.edges_data:
            if edge.relation_type in [RelationType.EXTENDS, RelationType.SUPERSEDES]:
                source_name = self.kg.nodes_data.get(edge.source, {}).name if edge.source in self.kg.nodes_data else edge.source
                target_name = self.kg.nodes_data.get(edge.target, {}).name if edge.target in self.kg.nodes_data else edge.target
                relation_name = RelationType.get_display_names().get(edge.relation_type, edge.relation_type.value)
                evolution_relations.append((source_name, relation_name, target_name))
        
        if evolution_relations:
            print(f"  标准演进关系:")
            for source, relation, target in evolution_relations[:3]:
                print(f"    • {source} {relation} {target}")
        else:
            print(f"  当前数据中未发现明显的标准演进关系")
    
    def _demo_performance_benchmark(self):
        """演示性能基准测试"""
        if not self.benchmark:
            print("⚡ 性能基准测试已跳过（使用--benchmark启用）")
            return
        
        print("⚡ 执行性能基准测试...")
        
        import time
        
        benchmark_results = {}
        
        # 1. 图构建性能
        print(f"\n🏗️ 图构建性能测试:")
        start_time = time.time()
        test_kg = EMCKnowledgeGraph()
        build_time = time.time() - start_time
        benchmark_results['graph_build'] = build_time
        print(f"  • 图构建时间: {build_time:.3f}秒")
        print(f"  • 构建速度: {len(test_kg.nodes_data) / build_time:.1f} 节点/秒")
        
        # 2. 搜索性能测试
        print(f"\n🔍 搜索性能测试:")
        search_terms = ["CISPR", "电动车", "EMC", "ISO", "测试方法", "抗扰度"]
        search_times = []
        
        for term in search_terms:
            start_time = time.time()
            results = self.kg.semantic_search(term, max_results=10)
            search_time = time.time() - start_time
            search_times.append(search_time)
        
        avg_search_time = sum(search_times) / len(search_times)
        benchmark_results['search_avg'] = avg_search_time
        print(f"  • 平均搜索时间: {avg_search_time*1000:.1f}ms")
        print(f"  • 搜索吞吐量: {1/avg_search_time:.1f} 查询/秒")
        
        # 3. 路径发现性能测试
        print(f"\n🔗 路径发现性能测试:")
        path_test_cases = [
            ('CISPR', 'CISPR25'),
            ('ISO', 'AnechoicChamber'), 
            ('ECER10', 'ElectricVehicles')
        ]
        
        path_times = []
        for source, target in path_test_cases:
            start_time = time.time()
            paths = self.kg.find_semantic_paths(source, target, max_depth=4)
            path_time = time.time() - start_time
            path_times.append(path_time)
        
        avg_path_time = sum(path_times) / len(path_times)
        benchmark_results['path_avg'] = avg_path_time
        print(f"  • 平均路径查找时间: {avg_path_time*1000:.1f}ms")
        
        # 4. 相似度计算性能测试
        print(f"\n📐 相似度计算性能测试:")
        node_pairs = [
            ('CISPR25', 'CISPR12'),
            ('ISO11452', 'ISO11451'),
            ('RadiatedEmissions', 'ConductedEmissions')
        ]
        
        similarity_times = []
        for node1, node2 in node_pairs:
            if node1 in self.kg.nodes_data and node2 in self.kg.nodes_data:
                start_time = time.time()
                similarity = self.kg.compute_semantic_similarity(node1, node2)
                sim_time = time.time() - start_time
                similarity_times.append(sim_time)
        
        if similarity_times:
            avg_sim_time = sum(similarity_times) / len(similarity_times)
            benchmark_results['similarity_avg'] = avg_sim_time
            print(f"  • 平均相似度计算时间: {avg_sim_time*1000:.1f}ms")
        
        # 5. 可视化渲染性能测试
        print(f"\n🎨 可视化渲染性能测试:")
        try:
            start_time = time.time()
            fig = self.kg.create_plotly_visualization()
            viz_time = time.time() - start_time
            benchmark_results['visualization'] = viz_time
            print(f"  • 交互式图谱渲染时间: {viz_time:.3f}秒")
        except Exception as e:
            print(f"  • 可视化测试跳过: {e}")
        
        # 6. 内存使用分析
        print(f"\n💾 内存使用分析:")
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            benchmark_results['memory_mb'] = memory_mb
            print(f"  • 当前内存使用: {memory_mb:.1f} MB")
            print(f"  • 每节点内存: {memory_mb / len(self.kg.nodes_data):.2f} MB")
        except ImportError:
            print(f"  • 内存分析需要psutil库")
        
        # 保存基准测试结果
        if self.save_outputs:
            benchmark_path = self.output_dir / "reports" / "benchmark_results.json"
            with open(benchmark_path, 'w', encoding='utf-8') as f:
                json.dump(benchmark_results, f, indent=2)
            print(f"\n📊 基准测试结果已保存: {benchmark_path}")
        
        # 性能评级
        print(f"\n🏆 性能评级:")
        if avg_search_time < 0.01:
            print(f"  • 搜索性能: 优秀 (< 10ms)")
        elif avg_search_time < 0.05:
            print(f"  • 搜索性能: 良好 (< 50ms)")
        else:
            print(f"  • 搜索性能: 一般 (≥ 50ms)")
        
        self.demo_stats['benchmark_results'].update(benchmark_results)
    
    def _generate_demo_report(self):
        """生成演示报告"""
        if not self.save_outputs:
            return
        
        print(f"\n📄 生成演示报告...")
        
        end_time = datetime.now()
        total_duration = end_time - self.demo_stats['start_time']
        
        demo_report = {
            'demo_info': {
                'start_time': self.demo_stats['start_time'].isoformat(),
                'end_time': end_time.isoformat(),
                'total_duration_seconds': total_duration.total_seconds(),
                'sections_completed': self.demo_stats['sections_completed'],
                'total_sections': self.demo_stats['total_sections'],
                'completion_rate': self.demo_stats['sections_completed'] / self.demo_stats['total_sections']
            },
            'system_info': {
                'python_version': sys.version,
                'platform': sys.platform,
                'knowledge_graph_nodes': len(self.kg.nodes_data) if hasattr(self, 'kg') else 0,
                'knowledge_graph_edges': len(self.kg.edges_data) if hasattr(self, 'kg') else 0
            },
            'benchmark_results': self.demo_stats['benchmark_results'],
            'output_files': {
                'visualizations': list((self.output_dir / "visualizations").glob("*")) if (self.output_dir / "visualizations").exists() else [],
                'reports': list((self.output_dir / "reports").glob("*")) if (self.output_dir / "reports").exists() else [],
                'exports': list((self.output_dir / "exports").glob("*")) if (self.output_dir / "exports").exists() else []
            }
        }
        
        report_path = self.output_dir / "demo_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(demo_report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"  ✓ 演示报告已保存: {report_path}")
    
    def _display_completion_summary(self):
        """显示完成总结"""
        duration = datetime.now() - self.demo_stats['start_time']
        completion_rate = self.demo_stats['sections_completed'] / self.demo_stats['total_sections']
        
        print(f"\n{'='*80}")
        print(f"🎊 演示完成总结")
        print(f"{'='*80}")
        print(f"📊 完成度: {completion_rate:.1%} ({self.demo_stats['sections_completed']}/{self.demo_stats['total_sections']})")
        print(f"⏱️ 总耗时: {duration.total_seconds():.1f}秒")
        
        if hasattr(self, 'kg'):
            print(f"🧠 知识图谱: {len(self.kg.nodes_data)}个实体, {len(self.kg.edges_data)}个关系")
        
        if self.save_outputs:
            print(f"📁 输出目录: {self.output_dir}")
            print(f"   • 可视化文件: {len(list((self.output_dir / 'visualizations').glob('*')))}个")
            print(f"   • 分析报告: {len(list((self.output_dir / 'reports').glob('*')))}个")
        
        if self.benchmark and self.demo_stats['benchmark_results']:
            print(f"⚡ 性能亮点:")
            results = self.demo_stats['benchmark_results']
            if 'search_avg' in results:
                print(f"   • 搜索平均响应: {results['search_avg']*1000:.1f}ms")
            if 'memory_mb' in results:
                print(f"   • 内存使用: {results['memory_mb']:.1f}MB")
        
        print(f"\n💡 建议后续操作:")
        if self.save_outputs:
            print(f"   • 查看交互式图谱: 打开 {self.output_dir}/visualizations/knowledge_graph_interactive.html")
            print(f"   • 查看分析仪表板: 打开 {self.output_dir}/visualizations/analysis_dashboard.html")
            print(f"   • 查看详细报告: {self.output_dir}/reports/")
        
        print(f"   • 尝试修改代码: 在src/目录中自定义知识图谱")
        print(f"   • 运行完整测试: python -m pytest tests/ -v")
        print(f"   • 查看帮助文档: README.md")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="EMC Knowledge Graph System Demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
演示模式：
  python demo.py                    # 标准演示模式
  python demo.py --interactive      # 交互式演示模式  
  python demo.py --benchmark        # 包含性能基准测试
  python demo.py --save-all         # 保存所有输出文件
  python demo.py --all              # 完整演示（交互+基准+保存）

输出文件将保存在 demo_output/ 目录中
        """
    )
    
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='启用交互式演示模式（需要用户输入）')
    parser.add_argument('--benchmark', '-b', action='store_true', 
                       help='执行性能基准测试')
    parser.add_argument('--save-all', '-s', action='store_true',
                       help='保存所有输出文件')
    parser.add_argument('--no-save', action='store_true',
                       help='不保存输出文件（仅演示）')
    parser.add_argument('--all', '-a', action='store_true',
                       help='完整演示模式（交互+基准+保存）')
    
    args = parser.parse_args()
    
    # 处理参数组合
    if args.all:
        interactive = True
        benchmark = True
        save_outputs = True
    else:
        interactive = args.interactive
        benchmark = args.benchmark
        save_outputs = args.save_all and not args.no_save
        if not args.save_all and not args.no_save:
            save_outputs = True  # 默认保存
    
    try:
        # 创建演示实例
        demo = EMCKnowledgeGraphDemo(
            interactive=interactive,
            save_outputs=save_outputs,
            benchmark=benchmark
        )
        
        # 运行演示
        demo.run_complete_demo()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
        return 130
    except Exception as e:
        print(f"\n❌ 演示执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())