# EMC Knowledge Graph User Guide

## Quick Start

```python
from src.knowledge_graph import EMCKnowledgeGraph

# 创建知识图谱
kg = EMCKnowledgeGraph()

# 语义搜索
results = kg.semantic_search("CISPR 25")

# 路径发现
paths = kg.find_semantic_paths('CISPR', 'ElectricVehicles')

# 生成可视化
fig, ax = kg.create_matplotlib_visualization()
```

## Advanced Features

- 拓扑分析
- 社区检测
- 中心性计算
- 多格式导出
