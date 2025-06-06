# EMC知识图谱系统

## 📋 项目简介

EMC知识图谱系统是专为电磁兼容性（EMC）领域打造的智能知识管理平台。系统集成了DeepSeek大语言模型与Neo4j图数据库，支持文档智能分析、实体提取、知识图谱构建、复杂关系查询与可视化等功能，助力EMC领域知识的结构化管理与智能应用。

---

## 🎯 主要功能

- **🤖 AI智能分析**：集成DeepSeek大模型，支持EMC文档自动解析、实体识别与关系抽取
- **📊 知识图谱**：基于Neo4j构建EMC领域知识图谱，支持高效的图数据存储、查询与分析
- **📁 文件处理**：支持PDF、Word、Excel、CSV、JSON、XML等多格式文档的内容提取与结构化
- **🔍 可视化查询**：交互式图谱可视化、Cypher查询编辑与结果展示
- **📈 实时监控**：系统监控、日志分析、性能指标可视化
- **🔒 安全认证**：JWT认证与基于角色的访问控制（RBAC）

---

## 🏗️ 技术架构

```
┌──────────────────────────────────────────────┐
│                前端应用层                    │
│  React + TypeScript + Material-UI + D3.js    │
├──────────────────────────────────────────────┤
│                API网关层                     │
│  FastAPI + Uvicorn + 中间件 + 负载均衡        │
├──────────────────────────────────────────────┤
│                业务逻辑层                    │
│  AI集成服务 + 图谱服务 + 文件处理服务         │
├──────────────────────────────────────────────┤
│                数据访问层                    │
│  PostgreSQL + Neo4j + Redis + 对象存储        │
└──────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 前置要求

- Docker 20.0+
- Docker Compose 2.0+
- Git
- 至少8GB RAM，20GB可用磁盘空间

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
# 填写DeepSeek API密钥、Neo4j密码等必要配置

# 4. 重新启动服务
./scripts/deploy.sh restart
```

#### 访问地址

- 🌐 主应用: http://localhost:3000
- 📖 API文档: http://localhost:8000/docs
- 💾 Neo4j浏览器: http://localhost:7474
- 📊 监控面板: http://localhost:3001 (Grafana)
- 🔍 日志分析: http://localhost:5601 (Kibana)

#### 默认登录信息

- 系统管理员: admin / (见 .env)
- Neo4j: neo4j / (见 .env)
- Grafana: admin / (见 .env)

---

## 🧑‍💻 开发指南

### 后端开发

```bash
# 安装依赖
pip install -r requirements.txt

# 复制并编辑开发环境变量
cp .env.example .env.dev
vi .env.dev

# 启动开发数据库
docker-compose -f docker-compose.dev.yml up -d postgres redis neo4j

# 数据库迁移
alembic upgrade head

# 启动后端服务
uvicorn gateway.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发

```bash
cd frontend
npm install
npm start
# 构建生产版本
npm run build
```

### 代码规范与测试

```bash
# Python格式化
black .
isort .

# 代码检查
flake8 .
mypy .

# 运行测试
pytest
```

---

## 📁 项目结构

```
emc-knowledge-graph/
├── frontend/                   # React前端应用
│   ├── src/components/         # 组件
│   │   ├── Editor/             # 编辑窗口
│   │   ├── Display/            # 显示窗口
│   │   ├── Input/              # 输入组件
│   │   └── layouts/            # 布局
│   ├── stores/                 # 状态管理
│   ├── services/               # API服务
│   └── types/                  # 类型定义
├── gateway/                    # API网关
│   ├── main.py                 # 主应用
│   ├── config.py               # 配置
│   ├── middleware/             # 中间件
│   └── routing/                # 路由
├── services/                   # 业务服务
│   ├── ai_integration/         # AI集成
│   ├── knowledge_graph/        # 知识图谱
│   ├── file_processing/        # 文件处理
│   └── emc_domain/             # EMC领域
├── data_access/                # 数据访问层
├── monitoring/                 # 监控配置
├── scripts/                    # 部署与维护脚本
├── docker-compose.yml          # Docker编排
├── requirements.txt            # Python依赖
├── .env                        # 环境变量
└── README.md                   # 项目文档
```

---

## 🔌 API接口

| 端点                        | 方法 | 描述           |
|-----------------------------|------|----------------|
| /api/deepseek/chat          | POST | AI对话接口     |
| /api/deepseek/analyze/document | POST | 文档分析    |
| /api/graph/data             | GET  | 获取图数据     |
| /api/graph/query            | POST | 执行Cypher查询 |
| /api/files/upload           | POST | 文件上传       |
| /api/files/status/{task_id} | GET  | 处理状态查询   |

### 认证方式

系统使用 JWT Bearer Token 认证：

```bash
curl -H "Authorization: Bearer <your-token>" http://localhost:8000/api/graph/data
```

---

## 💾 数据模型

### 核心实体

- 用户管理：User, RefreshToken, Permission
- 文件管理：FileMetadata, FileProcessingResult
- AI交互：AISession, AIMessage
- 实体提取：EntityExtractionResult, GraphImportRecord
- 监控审计：AuditLog, SystemEvent, APIUsageLog

### 图数据库模式（Cypher示例）

```cypher
// EMC标准节点
CREATE (s:EMCStandard {
  id: "EN_55032_2015",
  name: "EN 55032:2015",
  description: "Electromagnetic compatibility of multimedia equipment"
});

// 设备节点
CREATE (e:Equipment {
  id: "device_001",
  name: "Wireless Router",
  type: "ITE"
});

// 关系
CREATE (e)-[:COMPLIES_WITH {test_date: "2024-01-15"}]->(s);
```

---

## 🛠️ 运维管理

- 查看服务状态：`./scripts/deploy.sh status`
- 查看日志：`./scripts/deploy.sh logs gateway`
- 重启服务：`./scripts/deploy.sh restart`
- 数据备份：`./scripts/deploy.sh backup`
- 数据恢复：`./scripts/deploy.sh restore backup/20240101_120000`

### 监控与日志

- 系统指标：CPU、内存、磁盘使用率
- 应用指标：API响应时间、错误率、吞吐量
- 业务指标：AI调用次数、文档处理量、图谱规模
- 数据库指标：连接数、查询性能、存储使用
- 日志管理：ELK Stack（Elasticsearch、Logstash、Kibana）

---

## 🔧 配置说明

### 环境变量

| 变量名                | 描述             | 必填/可选 |
|-----------------------|------------------|-----------|
| EMC_SECRET_KEY        | JWT密钥          | 必填      |
| EMC_DEEPSEEK_API_KEY  | DeepSeek API密钥 | 必填      |
| EMC_NEO4J_PASSWORD    | Neo4j密码        | 必填      |
| EMC_POSTGRES_PASSWORD | PostgreSQL密码   | 必填      |
| EMC_REDIS_PASSWORD    | Redis密码        | 可选      |

### 性能调优

- API网关：
  - `EMC_WORKERS=8`  # 工作进程数
  - `EMC_MAX_CONCURRENT_PROCESSING=5`  # 最大并发处理
  - `EMC_RATE_LIMIT_REQUESTS_PER_MINUTE=100`  # 速率限制
- Neo4j：
  - `NEO4J_dbms_memory_heap_max__size=4G`
  - `NEO4J_dbms_memory_pagecache_size=2G`

---

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_deepseek_service.py

# 生成覆盖率报告
pytest --cov=. --cov-report=html

# 端到端测试
# 启动测试环境
docker-compose -f docker-compose.test.yml up -d
# 运行端到端测试
pytest tests/e2e/
```

---

## 🤝 贡献指南

1. Fork 项目仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交变更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

- 遵循PEP 8 Python代码规范
- 使用TypeScript严格模式
- 编写充分的测试用例
- 更新相关文档

---

## 🐛 故障排除

- **无法连接到Neo4j数据库**
  ```bash
  docker-compose logs neo4j
  docker-compose restart neo4j
  ```
- **DeepSeek API调用失败**
  ```bash
  grep DEEPSEEK_API_KEY .env
  ./scripts/deploy.sh logs gateway
  ```
- **文件上传处理失败**
  ```bash
  df -h
  docker-compose logs gateway | grep "file_processing"
  ```
- **图查询响应慢**
  - 检查Neo4j索引：`CREATE INDEX ON :EMCStandard(id)`
  - 优化Cypher查询：添加`LIMIT`子句
  - 增加Neo4j内存配置
- **API响应慢**
  - 检查数据库连接池配置
  - 增加API网关工作进程数
  - 启用Redis缓存

---

## 📚 核心组件说明

### 1. 编辑窗口组件
- DeepSeek提示词编辑器（`frontend/src/components/Editor/DeepSeekPromptEditor.tsx`）：提示词模板管理、参数配置、变量替换、实时预览
- 查询编辑器（`frontend/src/components/Editor/QueryEditor.tsx`）：Cypher查询编写、语法高亮、自动补全、查询历史

### 2. 显示窗口组件
- 图谱可视化（`frontend/src/components/Display/GraphVisualization.tsx`）：交互式图谱展示、节点/边筛选、布局算法、导出
- 响应查看器（`frontend/src/components/Display/ResponseViewer.tsx`）：AI响应展示、格式化输出、导出结果、历史记录

### 3. DeepSeek AI集成
- API服务（`services/ai_integration/deepseek_service.py`）：OpenAI兼容API调用、流式响应、错误处理、会话管理
- 提示词管理（`services/ai_integration/prompt_manager.py`）：模板存储、变量替换、版本控制、分类管理

### 4. 文件导入处理
- 支持格式：PDF、Word、Excel、CSV、JSON、XML
- 处理流程：文件格式检测→内容提取→实体识别→关系抽取→图数据生成

### 5. Neo4j图数据库集成
- 连接管理（`services/knowledge_graph/neo4j_emc_service.py`）：异步连接池、事务管理、错误恢复、性能监控
- 查询引擎（`services/knowledge_graph/graph_query_engine.py`）：Cypher查询执行、结果缓存、查询优化、安全检查

---

## 🔄 数据流示例

- **AI文档分析流程**：用户上传文档 → 文件处理服务 → DeepSeek API → 实体提取 → Neo4j存储 → 图谱可视化
- **交互式查询流程**：用户输入查询 → 查询验证 → Neo4j执行 → 结果格式化 → 可视化展示
- **知识图谱构建流程**：原始数据 → 预处理 → 实体识别 → 关系抽取 → 图数据生成 → 存储入库

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件。

---

## 🙏 致谢

- DeepSeek - 提供强大的AI语言模型
- Neo4j - 图数据库支持
- FastAPI - 现代化API框架
- React - 前端框架

---

## 📞 支持与反馈

- 邮箱: support@emc-knowledge.com
- 问题反馈: GitHub Issues
- 文档: 在线文档

EMC知识图谱系统 - 让EMC领域知识管理更智能 🚀

---

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








