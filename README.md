# EMC知识图谱系统

## 📋 项目概述

EMC知识图谱系统是一个专为电磁兼容性(EMC)领域设计的智能知识管理平台。系统集成了DeepSeek AI大语言模型和Neo4j图数据库，提供智能文档分析、实体提取、知识图谱构建和可视化等功能。

### 🎯 核心功能

- **🤖 AI智能分析**: 集成DeepSeek大语言模型，支持EMC文档智能解析和分析
- **📊 知识图谱**: 基于Neo4j构建EMC领域知识图谱，支持复杂关系查询和分析
- **📁 文件处理**: 支持PDF、Word、Excel等多种格式文档的自动解析和实体提取
- **🔍 可视化查询**: 交互式图谱可视化和Cypher查询界面
- **📈 实时监控**: 完整的系统监控和日志分析体系
- **🔒 安全认证**: JWT认证和基于角色的访问控制(RBAC)

### 🏗️ 技术架构
┌─────────────────────────────────────────────────┐
│                前端应用层                        │
│  React + TypeScript + Material-UI + D3.js      │
├─────────────────────────────────────────────────┤
│                API网关层                         │
│  FastAPI + Uvicorn + 中间件 + 负载均衡          │
├─────────────────────────────────────────────────┤
│                业务逻辑层                        │
│  AI集成服务 + 图谱服务 + 文件处理服务           │
├─────────────────────────────────────────────────┤
│                数据访问层                        │
│  PostgreSQL + Neo4j + Redis + 对象存储          │
└─────────────────────────────────────────────────┘


## 🚀 快速开始

### 前置要求

- Docker 20.0+
- Docker Compose 2.0+
- Git
- 至少 8GB RAM
- 20GB 可用磁盘空间

### 一键部署

```bash
# 1. 克隆仓库
git clone https://github.com/zhakil/emc_knowledge_graph.git
cd emc_knowledge_graph

# 2. 执行部署脚本
chmod +x scripts/deploy.sh
./scripts/deploy.sh deploy

# 3. 编辑环境配置文件
vi .env
# 填写DeepSeek API密钥等必要配置

# 4. 重新启动服务
./scripts/deploy.sh restart
访问地址
部署完成后，您可以通过以下地址访问系统：

🌐 主应用: http://localhost:3000
📖 API文档: http://localhost:8000/docs
💾 Neo4j浏览器: http://localhost:7474
📊 监控面板: http://localhost:3001 (Grafana)
🔍 日志分析: http://localhost:5601 (Kibana)
默认登录信息
系统管理员: admin / (查看.env文件中的密码)
Neo4j: neo4j / (查看.env文件中的NEO4J_PASSWORD)
Grafana: admin / (查看.env文件中的GRAFANA_PASSWORD)
🔧 开发指南
开发环境设置
bash
# 1. 安装Python依赖
pip install -r requirements.txt

# 2. 设置开发环境变量
cp .env.example .env.dev
# 编辑.env.dev文件

# 3. 启动开发数据库
docker-compose -f docker-compose.dev.yml up -d postgres redis neo4j

# 4. 运行数据库迁移
alembic upgrade head

# 5. 启动开发服务器
uvicorn gateway.main:app --reload --host 0.0.0.0 --port 8000
前端开发
bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm start

# 构建生产版本
npm run build
代码规范
bash
# Python代码格式化
black .
isort .

# 代码检查
flake8 .
mypy .

# 运行测试
pytest
📁 项目结构
emc-knowledge-graph/
├── frontend/                   # React前端应用
│   ├── src/
│   │   ├── components/        # React组件
│   │   │   ├── Editor/       # 编辑窗口组件
│   │   │   │   ├── DeepSeekPromptEditor.tsx
│   │   │   │   ├── QueryEditor.tsx
│   │   │   │   └── ConfigEditor.tsx
│   │   │   ├── Display/      # 显示窗口组件
│   │   │   │   ├── GraphVisualization.tsx
│   │   │   │   ├── ResponseViewer.tsx
│   │   │   │   ├── FileContentViewer.tsx
│   │   │   │   └── QueryResultViewer.tsx
│   │   │   ├── Input/        # 输入组件
│   │   │   │   └── FileUploadZone.tsx
│   │   │   └── layouts/      # 布局组件
│   │   │       └── DualPaneLayout.tsx
│   │   ├── stores/           # 状态管理
│   │   │   ├── deepSeekStore.ts
│   │   │   ├── graphStore.ts
│   │   │   └── fileStore.ts
│   │   ├── services/         # API服务
│   │   │   ├── aiService.ts
│   │   │   ├── graphService.ts
│   │   │   └── fileService.ts
│   │   └── types/            # TypeScript类型定义
│   │       ├── TestTypes.ts
│   │       └── DeepSeekTypes.ts
│   ├── package.json
│   └── Dockerfile
├── gateway/                   # API网关
│   ├── main.py               # 主应用
│   ├── config.py            # 配置管理
│   ├── middleware/          # 中间件
│   │   ├── auth.py         # 认证中间件
│   │   ├── cors.py         # CORS中间件
│   │   ├── rate_limiting.py # 速率限制
│   │   └── logging.py      # 日志中间件
│   ├── routing/             # API路由
│   │   ├── deepseek_routes.py   # DeepSeek API路由
│   │   ├── graph_routes.py      # 图数据库路由
│   │   ├── file_routes.py       # 文件处理路由
│   │   └── websocket_routes.py  # WebSocket路由
│   └── Dockerfile
├── services/                 # 业务服务
│   ├── ai_integration/      # AI集成服务
│   │   ├── deepseek_service.py      # DeepSeek API集成
│   │   └── prompt_manager.py        # 提示词管理
│   ├── knowledge_graph/     # 知识图谱服务
│   │   ├── neo4j_emc_service.py     # Neo4j EMC服务
│   │   ├── graph_manager.py         # 图管理器
│   │   ├── graph_query_engine.py    # 图查询引擎
│   │   └── graph_visualizer.py      # 图可视化
│   ├── file_processing/     # 文件处理服务
│   │   ├── emc_file_processor.py    # EMC文件处理器
│   │   ├── content_extractor.py     # 内容提取器
│   │   └── file_handler.py          # 文件处理器
│   └── emc_domain/         # EMC领域服务
│       ├── compliance_checker.py    # 合规性检查
│       ├── equipment_manager.py     # 设备管理
│       └── standards_processor.py   # 标准处理
├── data_access/             # 数据访问层
│   ├── models/             # 数据模型
│   ├── repositories/       # 数据仓库
│   └── connections/        # 数据库连接
│       ├── database_connection.py
│       └── redis_connection.py
├── monitoring/              # 监控配置
│   ├── prometheus.yml
│   ├── grafana/
│   └── logstash/
├── scripts/                 # 部署和维护脚本
│   ├── deploy.sh           # 部署脚本
│   └── check_environment.sh # 环境检查
├── docker-compose.yml       # Docker编排文件
├── requirements.txt         # Python依赖
├── .env                    # 环境变量配置
└── README.md               # 项目文档
🔌 API接口
主要端点
端点	方法	描述
/api/deepseek/chat	POST	AI对话接口
/api/deepseek/analyze/document	POST	文档分析
/api/graph/data	GET	获取图数据
/api/graph/query	POST	执行Cypher查询
/api/files/upload	POST	文件上传
/api/files/status/{task_id}	GET	处理状态查询
认证方式
系统使用JWT Bearer Token认证：

bash
curl -H "Authorization: Bearer <your-token>" \
     http://localhost:8000/api/graph/data
💾 数据模型
核心实体
用户管理: User, RefreshToken, Permission
文件管理: FileMetadata, FileProcessingResult
AI交互: AISession, AIMessage
实体提取: EntityExtractionResult, GraphImportRecord
监控审计: AuditLog, SystemEvent, APIUsageLog
图数据库模式
cypher
# EMC标准节点
CREATE (s:EMCStandard {
  id: "EN_55032_2015",
  name: "EN 55032:2015",
  description: "Electromagnetic compatibility of multimedia equipment"
})

# 设备节点
CREATE (e:Equipment {
  id: "device_001",
  name: "Wireless Router",
  type: "ITE"
})

# 关系
CREATE (e)-[:COMPLIES_WITH {test_date: "2024-01-15"}]->(s)
🛠️ 运维管理
服务管理
bash
# 查看服务状态
./scripts/deploy.sh status

# 查看日志
./scripts/deploy.sh logs gateway

# 重启服务
./scripts/deploy.sh restart

# 数据备份
./scripts/deploy.sh backup

# 数据恢复
./scripts/deploy.sh restore backup/20240101_120000
监控指标
系统提供以下监控指标：

系统指标: CPU、内存、磁盘使用率
应用指标: API响应时间、错误率、吞吐量
业务指标: AI调用次数、文档处理量、图谱规模
数据库指标: 连接数、查询性能、存储使用
日志管理
日志通过ELK Stack集中管理：

Elasticsearch: 日志存储和索引
Logstash: 日志收集和处理
Kibana: 日志查询和可视化
🔧 配置说明
环境变量
变量名	描述	默认值
EMC_SECRET_KEY	JWT密钥	必填
EMC_DEEPSEEK_API_KEY	DeepSeek API密钥	必填
EMC_NEO4J_PASSWORD	Neo4j密码	必填
EMC_POSTGRES_PASSWORD	PostgreSQL密码	必填
EMC_REDIS_PASSWORD	Redis密码	可选
性能调优
API网关调优
python
# gateway/config.py
EMC_WORKERS=8  # 工作进程数
EMC_MAX_CONCURRENT_PROCESSING=5  # 最大并发处理
EMC_RATE_LIMIT_REQUESTS_PER_MINUTE=100  # 速率限制
Neo4j调优
bash
# Neo4j内存配置
NEO4J_dbms_memory_heap_max__size=4G
NEO4J_dbms_memory_pagecache_size=2G
🧪 测试
运行测试
bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_deepseek_service.py

# 生成覆盖率报告
pytest --cov=. --cov-report=html
端到端测试
bash
# 启动测试环境
docker-compose -f docker-compose.test.yml up -d

# 运行端到端测试
pytest tests/e2e/
🤝 贡献指南
Fork 项目仓库
创建特性分支 (git checkout -b feature/AmazingFeature)
提交变更 (git commit -m 'Add some AmazingFeature')
推送到分支 (git push origin feature/AmazingFeature)
创建 Pull Request
代码规范
遵循 PEP 8 Python代码规范
使用 TypeScript 严格模式
编写充分的测试用例
更新相关文档
🐛 故障排除
常见问题
Q: 无法连接到Neo4j数据库

bash
# 检查Neo4j服务状态
docker-compose logs neo4j

# 重启Neo4j服务
docker-compose restart neo4j
Q: DeepSeek API调用失败

bash
# 检查API密钥配置
grep DEEPSEEK_API_KEY .env

# 查看网关日志
./scripts/deploy.sh logs gateway
Q: 文件上传处理失败

bash
# 检查存储空间
df -h

# 查看文件处理日志
docker-compose logs gateway | grep "file_processing"
性能问题
Q: 图查询响应缓慢

检查Neo4j索引: CREATE INDEX ON :EMCStandard(id)
优化Cypher查询: 添加LIMIT子句
增加Neo4j内存配置
Q: API响应时间过长

检查数据库连接池配置
增加API网关工作进程数
启用Redis缓存
📚 核心组件详解
1. 编辑窗口组件
DeepSeek提示词编辑器
位置: frontend/src/components/Editor/DeepSeekPromptEditor.tsx
功能:
提示词模板管理
参数配置（温度、最大token数等）
变量替换
实时预览
查询编辑器
位置: frontend/src/components/Editor/QueryEditor.tsx
功能:
Cypher查询编写
语法高亮
自动补全
查询历史
2. 显示窗口组件
图谱可视化
位置: frontend/src/components/Display/GraphVisualization.tsx
功能:
交互式图谱展示
节点/边筛选
布局算法
导出功能
响应查看器
位置: frontend/src/components/Display/ResponseViewer.tsx
功能:
AI响应展示
格式化输出
导出结果
历史记录
3. DeepSeek AI集成
API服务
位置: services/ai_integration/deepseek_service.py
功能:
OpenAI兼容API调用
流式响应支持
错误处理和重试
会话管理
提示词管理
位置: services/ai_integration/prompt_manager.py
功能:
模板存储和检索
变量替换
版本控制
分类管理
4. 文件导入处理
支持格式
PDF: 文本和表格提取
Word: 段落和样式保持
Excel: 多sheet支持
CSV: 编码自动检测
JSON: 结构化数据导入
XML: 层次结构解析
处理流程
python
# 位置: services/file_processing/emc_file_processor.py
async def process_file(file_path):
    # 1. 文件格式检测
    # 2. 内容提取
    # 3. 实体识别
    # 4. 关系抽取
    # 5. 图数据生成
5. Neo4j图数据库集成
连接管理
位置: services/knowledge_graph/neo4j_emc_service.py
功能:
异步连接池
事务管理
错误恢复
性能监控
查询引擎
位置: services/knowledge_graph/graph_query_engine.py
功能:
Cypher查询执行
结果缓存
查询优化
安全检查
🔄 数据流示例
AI文档分析流程
用户上传文档 → 文件处理服务 → DeepSeek API → 实体提取 → Neo4j存储 → 图谱可视化
交互式查询流程
用户输入查询 → 查询验证 → Neo4j执行 → 结果格式化 → 可视化展示
知识图谱构建流程
原始数据 → 预处理 → 实体识别 → 关系抽取 → 图数据生成 → 存储入库
📄 许可证
本项目采用 MIT 许可证 - 查看 LICENSE 文件了解详情。

🙏 致谢
DeepSeek - 提供强大的AI语言模型
Neo4j - 图数据库支持
FastAPI - 现代化API框架
React - 前端框架
📞 支持
如有问题或建议，请通过以下方式联系：

📧 邮箱: support@emc-knowledge.com
🐛 问题反馈: GitHub Issues
📖 文档: 在线文档
EMC知识图谱系统 - 让EMC领域知识管理更智能 🚀


## 🎯 架构设计总结

基于您的要求，我设计了一个精简而功能完整的EMC知识图谱系统架构，重点突出了以下特性：

### 1. **双窗格用户界面**
- **编辑窗口**: DeepSeek提示词编辑器、查询编辑器
- **显示窗口**: 图谱可视化、AI响应展示、文件内容查看

### 2. **模块化架构设计**
- **表示层**: React组件，支持实时交互
- **API网关**: FastAPI路由，统一接口管理
- **业务逻辑**: AI集成、文件处理、图数据库服务
- **数据访问**: Neo4j、Redis、文件系统

### 3. **核心集成能力**
- **DeepSeek API**: OpenAI兼容格式，支持流式响应
- **文件导入**: 多格式支持，智能内容提取
- **Neo4j图数据库**: 高性能图查询和可视化
- **实时同步**: WebSocket支持实时协作

这个架构既保持了项目的完整性，又确保了代码的实用性和可维护性，完全满足您提出的所有技术要求。



Retry








