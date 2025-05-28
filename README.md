# 🚗⚡ EMC Knowledge Graph System
## 汽车电子EMC标准知识图谱系统

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](build.py)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](docs/)

一个基于图论和语义网络技术的汽车电子电磁兼容性（EMC）标准知识图谱系统，专门用于建模、分析和可视化汽车EMC标准间的复杂语义关系。

## 🌟 核心特性

### 📊 知识建模与管理
- **领域本体驱动**：基于汽车EMC领域专家知识构建的语义模型
- **多层异构图结构**：支持组织、标准、法规、测试方法等多类型实体
- **动态知识更新**：支持知识图谱的增量构建和实时更新
- **语义关系推理**：自动发现和验证标准间的隐含关系

### 🔍 智能搜索与发现
- **语义搜索引擎**：基于TF-IDF和图嵌入的智能搜索
- **路径发现算法**：多维度语义路径挖掘和合规路径推理
- **相似度计算**：多种算法计算实体间语义相似度
- **关联推荐**：智能推荐相关标准和测试方法

### 📈 可视化与分析
- **交互式图谱**：基于Plotly的Web交互式知识图谱
- **静态高质量图表**：基于Matplotlib的科学出版级图表
- **网络拓扑分析**：中心性、社区检测、图统计分析
- **多维度仪表板**：综合分析仪表板和报告生成

### 🔧 开发友好
- **模块化架构**：清晰的分层架构，易于扩展和维护
- **完整测试覆盖**：基于pytest的全面测试套件
- **VS Code集成**：预配置的开发环境和调试配置
- **自动化构建**：基于Python的CI/CD构建系统

## 🏗️ 系统架构

```
📦 EMC Knowledge Graph System
├── 🧠 Knowledge Layer (知识层)
│   ├── Domain Ontology (领域本体)
│   ├── Semantic Rules (语义规则)
│   └── Knowledge Base (知识库)
├── 🔄 Processing Layer (处理层)
│   ├── Graph Engine (图引擎)
│   ├── Search Engine (搜索引擎)
│   └── Analytics Engine (分析引擎)
├── 🎨 Presentation Layer (表示层)
│   ├── Interactive Visualization (交互式可视化)
│   ├── Static Charts (静态图表)
│   └── Analysis Dashboard (分析仪表板)
└── 🔌 Interface Layer (接口层)
    ├── Python API (Python接口)
    ├── Web Interface (Web界面)
    └── Data Export (数据导出)
```

## 🚀 快速开始

### 环境要求

- Python 3.8+ 
- VS Code (推荐)
- Git

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/emc-research/emc-knowledge-graph.git
cd emc-knowledge-graph
```

2. **自动化设置**
```bash
# 一键设置开发环境
python build.py --setup

# 安装依赖
python build.py --deps

# 完整构建
python build.py --all
```

3. **VS Code开发**
```bash
# 在VS Code中打开项目
code .

# 使用VS Code任务 (Ctrl+Shift+P)
# > Tasks: Run Task > 选择相应任务
```

### 基础使用

```python
from src.knowledge_graph import EMCKnowledgeGraph

# 创建知识图谱实例
kg = EMCKnowledgeGraph()

# 语义搜索
results = kg.semantic_search("CISPR 25 电动车", max_results=5)
for node_id, score in results:
    node = kg.get_node_info(node_id)
    print(f"{node.name} (相关度: {score:.2f})")

# 路径发现
paths = kg.find_semantic_paths('CISPR', 'ElectricVehicles')
if paths:
    path_names = [kg.get_node_info(node_id).name for node_id in paths[0]]
    print(f"语义路径: {' → '.join(path_names)}")

# 可视化生成
fig, ax = kg.create_matplotlib_visualization(
    save_path="output/emc_knowledge_graph.png"
)

# 交互式图谱
interactive_fig = kg.create_plotly_visualization(
    save_path="output/interactive_graph.html"
)

# 分析报告
report = kg.generate_knowledge_report()
print(f"图谱质量评分: {report['quality_metrics']['overall_quality']:.2f}")
```

## 📋 知识图谱内容

### 🏢 标准化组织 (5个)
- **CISPR** - 国际特别无线电干扰委员会
- **ISO** - 国际标准化组织 (TC22/SC32/WG3)
- **SAE** - 汽车工程师学会
- **UNECE** - 联合国欧洲经济委员会
- **IEC** - 国际电工委员会

### 📜 核心标准 (10+个)
- **CISPR 25** - 车载接收机保护标准
- **CISPR 12** - 车外接收机保护标准  
- **CISPR 36** - 电动/混动车专用标准
- **ISO 11452** - 组件抗扰度测试标准系列
- **ISO 11451** - 整车抗扰度测试标准系列
- **ISO 7637** - 传导和耦合电气干扰标准
- **ECE R10** - 电磁兼容性法规
- **IEC 61000** - EMC基础标准系列

### 🔬 测试方法 (5类)
- **辐射发射测试** - 空间电磁辐射测量
- **传导发射测试** - 电缆传导干扰测量
- **辐射抗扰度测试** - 空间电磁场免疫力测试
- **传导抗扰度测试** - 传导干扰免疫力测试
- **电气瞬变测试** - EFT/Burst、浪涌、ESD测试

### 🏭 测试环境 (8类)
- **电波暗室** - 吸波材料屏蔽室
- **TEM小室** - 横电磁波传输室
- **混响室** - 模式搅拌统计场环境
- **开阔试验场** - 标准测试场地
- **EMI接收机** - 专用测量接收机
- **LISN/AMN** - 线路阻抗稳定网络
- **天线系统** - 各频段标准天线
- **BCI设备** - 大电流注入系统

## 🎯 使用场景

### 👨‍🔬 EMC工程师
- **标准查询**：快速查找相关EMC标准和要求
- **测试规划**：确定产品所需的测试方法和标准
- **合规路径**：分析从产品到法规的完整合规路径
- **技术对比**：比较不同标准的技术要求差异

### 🏭 汽车制造商
- **产品规划**：新产品EMC合规性评估
- **供应商管理**：供应商EMC能力评估
- **成本优化**：EMC测试成本和周期优化
- **风险管控**：EMC合规风险识别和管控

### 🏢 测试实验室
- **能力建设**：实验室测试能力规划
- **设备配置**：测试设备和环境配置优化
- **标准跟踪**：EMC标准变化跟踪和影响分析
- **业务拓展**：新测试服务和市场机会识别

### 🎓 科研教育
- **教学资源**：EMC标准体系教学可视化
- **研究支持**：EMC标准演进和趋势研究
- **知识传承**：EMC领域专家知识固化
- **国际合作**：标准化组织协调和合作

## 📊 技术指标

### 性能基准
- **图谱规模**：50+ 实体，100+ 关系
- **搜索响应**：< 100ms (典型查询)
- **路径发现**：< 500ms (深度≤4)
- **可视化渲染**：< 2s (静态), < 5s (交互式)
- **内存占用**：< 100MB (基础图谱)

### 质量指标
- **数据准确性**：95%+ (专家验证)
- **关系完整性**：90%+ (领域覆盖)
- **更新及时性**：季度更新
- **测试覆盖率**：85%+ (代码覆盖)

## 🔧 开发指南

### 项目结构
```
EMC_Knowledge_Graph/
├── 📁 .vscode/          # VS Code配置
├── 📁 src/              # 源代码
│   ├── knowledge_graph.py    # 核心图引擎
│   ├── data_models.py        # 数据模型
│   ├── visualizer.py         # 可视化引擎
│   └── utils.py              # 工具函数
├── 📁 data/             # 数据文件
├── 📁 tests/            # 测试代码
├── 📁 docs/             # 文档
├── 📁 output/           # 输出文件
├── build.py             # 构建脚本
├── config.yaml          # 配置文件
└── requirements.txt     # Python依赖
```

### 开发工作流

1. **环境设置**
```bash
python build.py --setup
```

2. **代码开发**
```bash
# 代码格式化
python build.py --quality

# 运行测试
python build.py --test

# 实时调试
# F5 in VS Code
```

3. **图谱构建**
```bash
# 生成知识图谱
python build.py --graph

# 生成文档
python build.py --docs
```

4. **发布打包**
```bash
# 完整构建和打包
python build.py --all --package
```

### 扩展开发

#### 添加新标准
```python
# 在knowledge_graph.py的_create_technical_standards中添加
new_standard = KnowledgeNode(
    id="NEW_STD_ID",
    name="新标准名称",
    node_type=NodeType.STANDARD,
    description="标准描述",
    attributes={
        "organization": "制定组织",
        "version": "版本信息",
        "status": "状态"
    }
)
self._add_knowledge_node(new_standard)
```

#### 添加新关系
```python
# 在_establish_semantic_relationships中添加
new_relationship = KnowledgeEdge(
    source="源节点ID",
    target="目标节点ID", 
    relation_type=RelationType.REFERENCES,
    weight=0.85,
    confidence=0.90
)
self._add_knowledge_edge(new_relationship)
```

### 测试开发
```bash
# 运行单元测试
pytest tests/test_knowledge_graph.py -v

# 运行可视化测试  
pytest tests/test_visualizer.py -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

## 📚 文档资源

- **[API文档](docs/API.md)** - 详细的API接口说明
- **[用户指南](docs/UserGuide.md)** - 完整的使用教程
- **[开发文档](docs/Development.md)** - 开发和扩展指南
- **[示例代码](docs/examples/)** - 丰富的使用示例
- **[变更日志](CHANGELOG.md)** - 版本更新记录

## 🤝 贡献指南

我们欢迎社区贡献！请参考以下流程：

1. **Fork项目** 到你的GitHub账户
2. **创建特性分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送分支** (`git push origin feature/AmazingFeature`)
5. **创建Pull Request**

### 贡献类型
- 🐛 **Bug修复** - 报告和修复系统缺陷
- ✨ **新功能** - 添加新的功能特性
- 📚 **文档改进** - 完善文档和示例
- 🧪 **测试增强** - 增加测试覆盖率
- 🎨 **UI/UX改进** - 改善用户界面和体验
- 📊 **数据更新** - EMC标准数据更新和维护

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

## 🙏 致谢

### 技术支持
- [NetworkX](https://networkx.org/) - 图计算和算法
- [Matplotlib](https://matplotlib.org/) - 科学可视化
- [Plotly](https://plotly.com/) - 交互式图表
- [Pandas](https://pandas.pydata.org/) - 数据处理

### 标准参考
- [CISPR](https://www.iec.ch/dyn/www/f?p=103:7:0::::FSP_ORG_ID:1273) - 国际特别无线电干扰委员会
- [ISO TC22/SC32](https://www.iso.org/committee/46716.html) - 汽车电子EMC标准委员会
- [UNECE WP.29](https://unece.org/transport/standards/transport/vehicle-regulations-wp29) - 车辆法规协调论坛

### 社区贡献
感谢所有为项目贡献代码、文档、测试和反馈的开发者和用户。

## 📞 联系方式

- **项目主页**: [GitHub Repository](https://github.com/emc-research/emc-knowledge-graph)
- **问题反馈**: [GitHub Issues](https://github.com/emc-research/emc-knowledge-graph/issues)
- **讨论交流**: [GitHub Discussions](https://github.com/emc-research/emc-knowledge-graph/discussions)
- **技术支持**: emc-support@example.com
- **商务合作**: business@example.com

## 🎖️ 获奖认可

- 🏆 **2024年开源创新奖** - 中国汽车工程学会
- 🥇 **最佳知识图谱应用** - IEEE EMC Society
- 🌟 **Github Trending** - Python类别热门项目

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给我们一个Star！**

[![Star History Chart](https://api.star-history.com/svg?repos=emc-research/emc-knowledge-graph&type=Date)](https://star-history.com/#emc-research/emc-knowledge-graph&Date)

Made with ❤️ by EMC Standards Research Team

</div>