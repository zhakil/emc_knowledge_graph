# 📁 EMC知识图谱项目结构

## 🏗️ 重组后的规范目录结构

```
emc_knowledge_graph/
├── 📂 backend/                    # 🔧 后端服务
│   ├── enhanced_gateway.py             # 主要API网关
│   ├── start_gateway.py                # 启动脚本
│   └── quick_start.py                  # 快速启动
│
├── 📂 frontend/                   # 🌐 前端应用
│   ├── src/                            # React源码
│   │   ├── components/                 # 组件
│   │   ├── stores/                     # 状态管理
│   │   └── styles/                     # 样式
│   ├── public/                         # 静态资源
│   └── package.json                    # 依赖配置
│
├── 📂 services/                   # 🔬 微服务模块
│   ├── ai_integration/                 # AI集成服务
│   ├── knowledge_graph/                # 知识图谱服务
│   ├── file_processing/                # 文件处理服务
│   └── emc_domain/                     # EMC领域服务
│
├── 📂 config/                     # ⚙️ 配置文件
│   ├── environment.yml                 # Conda环境
│   ├── requirements.txt                # Python依赖
│   ├── docker-compose.yml              # Docker配置
│   └── neo4j.conf                      # Neo4j配置
│
├── 📂 data/                       # 💾 数据存储
│   ├── neo4j/                          # 图数据库
│   ├── postgres/                       # 关系数据库
│   └── uploads/                        # 上传文件
│
├── 📂 scripts/                    # 📜 系统脚本
│   ├── deploy.sh                       # 部署脚本
│   ├── start-system.sh                 # 系统启动
│   └── init_project.sh                 # 项目初始化
│
├── 📂 tests/                      # ✅ 正式测试
│   ├── unit/                           # 单元测试
│   ├── integration/                    # 集成测试
│   └── api/                            # API测试
│
├── 📂 dev-tools/                  # 🛠️ 开发工具
│   ├── tests/                          # 开发测试
│   │   ├── test_*.py                   # 各种测试脚本
│   │   ├── *.log                       # 测试日志
│   │   └── run_all_tests.py            # 测试运行器
│   ├── examples/                       # 示例代码
│   │   └── simple_frontend.html        # 简单测试界面
│   ├── scripts/                        # 工具脚本
│   │   └── reorganize_project.py       # 项目重组脚本
│   └── docs/                           # 开发文档
│
├── 📂 docs/                       # 📚 项目文档
│   ├── README.md                       # 项目说明
│   ├── EMC_ONTOLOGY.md                 # 本体说明
│   ├── FILE_DESCRIPTIONS.md            # 文件说明
│   └── PROJECT_STRUCTURE.md            # 结构说明(本文件)
│
├── 📂 logs/                       # 📊 日志文件
│   ├── backend*.log                    # 后端日志
│   ├── frontend*.log                   # 前端日志
│   └── gateway*.log                    # 网关日志
│
├── 📂 uploads/                    # 📁 上传文件
│   ├── standards/                      # 标准文档
│   ├── reports/                        # 测试报告
│   └── temp/                           # 临时文件
│
└── 📄 start_system.py             # 🚀 统一启动脚本
```

## 🚀 快速启动

### 一键启动全系统:
```bash
python3 start_system.py
```

### 分别启动各服务:
```bash
# 后端
cd backend && python3 enhanced_gateway.py

# 前端  
cd frontend && npm start

# 测试界面
cd dev-tools/examples && python3 -m http.server 3001
```

## 🧪 测试运行

### 运行所有开发测试:
```bash
cd dev-tools/tests && python3 run_all_tests.py
```

### 运行单个测试:
```bash
cd dev-tools/tests && python3 test_strict_validation.py
```

## 📱 访问地址

- **🌐 完整React前端**: http://localhost:3000
- **🧪 简单测试界面**: http://localhost:3001/simple_frontend.html  
- **📊 后端API文档**: http://localhost:8000/docs
- **⚙️ 系统健康检查**: http://localhost:8000/health

## 🔧 开发指南

### 后端开发
- **位置**: `backend/` 目录
- **主文件**: `enhanced_gateway.py`
- **启动**: `python3 enhanced_gateway.py`

### 前端开发
- **位置**: `frontend/src/` 目录
- **主文件**: `src/App.tsx`
- **启动**: `npm start`

### 测试开发
- **位置**: `dev-tools/tests/` 目录
- **命名**: `test_*.py`
- **运行**: `python3 run_all_tests.py`

### 添加新功能
1. **后端API**: 在 `backend/enhanced_gateway.py` 添加端点
2. **前端组件**: 在 `frontend/src/components/` 添加组件
3. **测试验证**: 在 `dev-tools/tests/` 添加测试
4. **文档更新**: 在 `docs/` 更新相关文档

## 📋 文件分类

| 类型 | 位置 | 说明 |
|------|------|------|
| 🔧 后端代码 | `backend/` | API服务、网关 |
| 🌐 前端代码 | `frontend/` | React应用 |
| 🔬 微服务 | `services/` | 各种业务服务 |
| ⚙️ 配置 | `config/` | 环境、依赖配置 |
| 💾 数据 | `data/` | 数据库、上传文件 |
| 📜 脚本 | `scripts/` | 部署、启动脚本 |
| ✅ 测试 | `tests/` | 正式测试套件 |
| 🛠️ 开发工具 | `dev-tools/` | 开发阶段工具 |
| 📚 文档 | `docs/` | 项目文档 |
| 📊 日志 | `logs/` | 系统运行日志 |

## 🎯 优势

✅ **结构清晰**: 按功能模块组织，易于导航  
✅ **开发友好**: 测试工具集中管理  
✅ **维护便利**: 配置文件统一放置  
✅ **扩展性强**: 模块化设计，易于添加新功能  
✅ **文档完整**: 每个目录都有明确说明  

## 🔄 迁移说明

原来散落在根目录的文件已按功能重新组织:
- 测试文件 → `dev-tools/tests/`
- 配置文件 → `config/`
- 文档文件 → `docs/`
- 日志文件 → `logs/`
- 脚本文件 → `scripts/`

新的统一启动方式让开发更加便捷！