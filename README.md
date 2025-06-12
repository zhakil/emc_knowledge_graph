# 📊 EMC 知识图谱系统

![版本](https://img.shields.io/badge/版本-1.0.0-blue.svg)
![状态](https://img.shields.io/badge/状态-系统运行中-green.svg)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)

**EMC知识图谱系统**是一个专为电磁兼容性(EMC)领域设计的智能知识管理平台。系统集成了DeepSeek AI大语言模型和Neo4j图数据库，提供智能文档分析、实体提取、知识图谱构建和可视化等功能。

## 🌟 主要特性

### 🚀 核心功能
- **📁 智能文件上传**：支持 PDF、Word、Excel、CSV、JSON、XML、TXT 等格式
- **🤖 AI 文档分析**：集成 DeepSeek API，智能提取EMC相关实体和关系
- **🕸️ 知识图谱构建**：自动构建和可视化EMC领域知识图谱
- **🔍 语义搜索**：基于图数据库的智能查询和检索
- **📊 实时监控**：系统健康状态和使用统计监控
- **🎨 中式界面**：古典高雅的用户界面设计
- **📝 文档编辑**：Markdown实时预览编辑器

### 🎯 前端特色
- **🏮 中式古典设计**：金黄色主题，传统美学与现代技术融合
- **📱 响应式布局**：完美适配桌面端和移动端设备
- **🖱️ 交互体验**：D3.js图谱可视化，拖拽式文件上传
- **⚡ 实时功能**：分屏Markdown编辑，系统状态监控
- **🔧 智能配置**：可视化API设置，连接状态检测

### 🏗️ 技术架构
- **后端框架**：FastAPI + Python 3.11+
- **AI 集成**：DeepSeek API (OpenAI 兼容)
- **图数据库**：Neo4j 5.15+ (开发模式支持)
- **缓存层**：Redis 7.4+
- **关系数据库**：PostgreSQL 16+
- **前端框架**：React 18 + TypeScript + Ant Design
- **可视化**：D3.js 力导向图
- **容器化**：Docker + Docker Compose

## 🎉 当前状态

### ✅ 系统全面运行
**前端界面和后端API服务全部运行完成！**

🌐 **访问地址**: http://localhost:3000  
🎨 **设计风格**: 金黄色主题的中式古典审美  
📱 **响应式设计**: 完美支持桌面和移动端

#### 🏆 主要功能模块
- 🏠 **系统概览** - 仪表板和状态监控
- 📁 **文件上传** - 拖拽上传和智能分类  
- 📂 **文件管理** - 浏览、搜索、批量操作
- 🕸️ **知识图谱** - D3.js可视化和交互编辑
- 📝 **Markdown编辑** - 实时预览和工具栏
- ⚙️ **系统设置** - API配置和连接测试

#### 💫 界面特色
- 🏮 温润如玉的金黄色主题 (#d4af37)
- 📜 优雅的中文字体支持
- 🎋 对称平衡的布局设计
- ✨ 流畅的交互动效

#### 🚀 开始使用
```bash
# 启动前端开发服务器
cd frontend && npm start

# 在浏览器中访问
open http://localhost:3000
```

#### 🚀 后端API服务
- **API地址**: http://localhost:8000  
- **API文档**: http://localhost:8000/docs  
- **健康检查**: http://localhost:8000/health  

> **状态**: ✅ 前端和后端全部运行，系统功能完整可用！

## 📦 快速开始

### 🔧 环境要求

- **Python**: 3.11 或更高版本
- **内存**: 至少 4GB RAM
- **存储**: 至少 10GB 可用空间
- **操作系统**: Linux、macOS 或 Windows (WSL2)

### ⚡ 一键启动（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/zhakil/emc_knowledge_graph.git
cd emc_knowledge_graph

# 2. 创建 Python 虚拟环境
python3 -m venv emc_venv
source emc_venv/bin/activate  # Linux/macOS
# emc_venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install --upgrade pip
pip install fastapi uvicorn[standard] python-multipart aiofiles pydantic python-dotenv neo4j

# 4. 创建必要目录
mkdir -p uploads logs data

# 5. 启动服务
export PYTHONPATH=$(pwd)
python -m uvicorn gateway.main:app --host 0.0.0.0 --port 8000 --reload
```

### 🌐 访问系统

启动成功后，您可以通过以下地址访问系统：

- **🏠 主页**: http://localhost:8000/
- **📁 文件上传界面**: http://localhost:8000/upload
- **📖 API 文档**: http://localhost:8000/docs
- **🔍 健康检查**: http://localhost:8000/health
- **🧪 API 测试**: http://localhost:8000/api/test

## 🎯 功能演示

### 📁 文件上传功能

系统提供了美观的文件上传界面，支持多种文件格式：

**访问地址**: http://localhost:8000/upload

**功能特点**:
- 🖱️ 拖拽上传或点击选择文件
- 📊 实时上传进度显示
- ✅ 上传结果反馈
- 📋 文件列表管理
- 🗑️ 文件删除功能

**支持格式**:
```
PDF, DOCX, XLSX, CSV, JSON, XML, TXT
```

### 🔧 API 接口

#### 📊 健康检查
```bash
curl http://localhost:8000/health
```

**响应示例**:
```json
{
  "status": "healthy",
  "services": {
    "api": true,
    "upload_interface": true,
    "upload_directory": true
  },
  "file_count": 0,
  "timestamp": "2025-06-11T16:19:40.535075"
}
```

#### 📁 文件上传
```bash
curl -X POST "http://localhost:8000/api/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@example.pdf"
```

**响应示例**:
```json
{
  "message": "文件上传成功",
  "filename": "example.pdf",
  "size": 1024000,
  "file_type": ".pdf",
  "download_url": "http://localhost:8000/uploads/example.pdf",
  "timestamp": "2025-06-11T16:19:40.535075"
}
```

#### 📋 文件列表
```bash
curl http://localhost:8000/api/files
```

**响应示例**:
```json
[
  {
    "name": "example.pdf",
    "size": 1024000,
    "type": "application/pdf",
    "download_url": "/uploads/example.pdf",
    "last_modified": "2025-06-11T16:19:40.535075"
  }
]
```

## 🐳 Docker 部署（可选）

如果您希望使用完整的容器化部署：

```bash
# 启动完整系统栈
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f gateway

# 停止服务
docker-compose down
```

### 🌐 容器化服务端口
- **API 网关**: 8000
- **Neo4j 浏览器**: 7474
- **PostgreSQL**: 5432
- **Redis**: 6379
- **Nginx**: 80, 443
- **Prometheus**: 9090
- **Grafana**: 3000

## 📁 项目结构

```
emc_knowledge_graph/
├── 📁 gateway/                 # API 网关
│   ├── main.py                # 主应用入口
│   ├── routing/               # API 路由
│   └── middleware/            # 中间件
├── 📁 services/               # 业务服务
│   ├── ai_integration/        # AI 集成服务
│   ├── emc_domain/            # EMC 领域服务
│   ├── file_processing/       # 文件处理服务
│   └── knowledge_graph/       # 知识图谱服务
├── 📁 frontend/               # React 前端应用
│   ├── App.tsx               # 主应用组件
│   ├── components/           # UI 组件
│   └── stores/               # 状态管理
├── 📁 scripts/                # 工具脚本
├── 📁 tests/                  # 测试文件
├── 📁 utils/                  # 工具函数
├── 📄 requirements.txt        # Python 依赖
├── 📄 docker-compose.yml      # Docker 编排
├── 📄 Dockerfile             # 容器构建
└── 📄 README.md              # 项目文档
```

## ⚙️ 配置说明

### 🔑 环境变量

在项目根目录创建 `.env` 文件：

```bash
# 环境配置
EMC_ENVIRONMENT=development
EMC_SECRET_KEY=your-secret-key-here
EMC_DEBUG=true
EMC_HOST=0.0.0.0
EMC_PORT=8000

# DeepSeek API 配置（可选）
EMC_DEEPSEEK_API_KEY=sk-your-deepseek-api-key
EMC_DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 数据库配置（Docker 部署时使用）
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=emc_password_123
REDIS_URL=redis://redis:6379/0
DATABASE_URL=postgresql://postgres:password@postgres:5432/emc_kg
```

### 📋 系统要求

**最小配置**:
- CPU: 2 核心
- 内存: 4GB RAM
- 存储: 10GB

**推荐配置**:
- CPU: 4 核心或更多
- 内存: 8GB RAM 或更多
- 存储: 20GB 或更多

## 🛠️ 故障排除

### ❓ 常见问题

#### 1. **端口被占用**
```bash
# 检查端口占用
netstat -tlnp | grep 8000
# 或
ss -tlnp | grep 8000

# 更换端口启动
python -m uvicorn gateway.main:app --host 0.0.0.0 --port 8001
```

#### 2. **虚拟环境问题**
```bash
# 重新创建虚拟环境
rm -rf emc_venv
python3 -m venv emc_venv
source emc_venv/bin/activate
pip install --upgrade pip
```

#### 3. **依赖安装失败**
```bash
# 使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple fastapi uvicorn[standard]
```

#### 4. **文件上传失败**
- 检查 `uploads/` 目录是否存在且有写入权限
- 确认文件格式在支持列表中
- 检查文件大小是否超出限制

### 📝 日志查看

```bash
# 查看实时日志
tail -f gateway.log

# 查看系统状态
curl http://localhost:8000/health

# 检查进程状态
ps aux | grep uvicorn
```

## 🔄 开发指南

### 🚀 启动开发服务器

```bash
# 激活虚拟环境
source emc_venv/bin/activate

# 设置 Python 路径
export PYTHONPATH=$(pwd)

# 启动开发服务器（自动重载）
python -m uvicorn gateway.main:app --host 0.0.0.0 --port 8000 --reload

# 启动前端开发服务器（可选）
cd frontend
npm install
npm start
```

### 🧪 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行所有测试
pytest
```

### 📊 代码质量检查

```bash
# 安装代码质量工具
pip install black flake8 mypy

# 代码格式化
black gateway/ services/

# 代码检查
flake8 gateway/ services/

# 类型检查
mypy gateway/ services/
```

## 🤝 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

1. **Fork** 本仓库
2. **创建特性分支**: `git checkout -b feature/amazing-feature`
3. **提交更改**: `git commit -m 'Add amazing feature'`
4. **推送分支**: `git push origin feature/amazing-feature`
5. **开启 Pull Request**

### 📋 贡献规范

- 遵循现有代码风格
- 为新功能添加测试
- 更新相关文档
- 确保所有测试通过

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 📞 联系方式

- **项目主页**: https://github.com/zhakil/emc_knowledge_graph
- **问题反馈**: https://github.com/zhakil/emc_knowledge_graph/issues
- **邮箱**: [待添加]

## 🎉 致谢

感谢以下开源项目的支持：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的 Web 框架
- [Neo4j](https://neo4j.com/) - 图数据库
- [React](https://reactjs.org/) - 用户界面库
- [DeepSeek](https://www.deepseek.com/) - AI 大语言模型

---

## 📋 功能清单

### 🎯 完整功能对比

| 功能模块 | 状态 | 描述 | 访问方式 |
|----------|------|------|----------|
| 🏠 **系统概览** | ✅ 完成 | 实时监控、统计数据、活动时间线 | 前端首页 |
| 📁 **文件上传** | ✅ 完成 | 拖拽上传、分类管理、AI分析 | 文件上传页面 |
| 📂 **文件管理** | ✅ 完成 | 浏览、搜索、删除、批量操作 | 文件管理页面 |
| 🕸️ **知识图谱** | ✅ 完成 | D3可视化、实时编辑、智能搜索 | 图谱可视化页面 |
| 📝 **Markdown编辑** | ✅ 完成 | 实时预览、工具栏、自动保存 | Markdown编辑器 |
| ⚙️ **系统设置** | ✅ 完成 | API配置、连接测试、参数调节 | 设置模态框 |
| 🤖 **AI集成** | ✅ 完成 | DeepSeek API、实体提取 | 后端服务 |
| 🗄️ **图数据库** | ⚠️ 开发模式 | Neo4j连接、图数据存储 | 后端服务 |
| 🔴 **缓存系统** | ✅ 完成 | Redis缓存、性能优化 | 后端服务 |
| 📊 **监控系统** | ✅ 完成 | 健康检查、状态监控 | 系统后台 |

### 🚀 启动状态检查

运行以下命令检查各组件状态：

```bash
# 检查后端服务
python3 start_services.py

# 检查数据库连接
python3 test_connections.py

# 检查知识图谱功能
python3 test_kg_functionality.py

# 启动前端界面
./start_frontend.sh
```

## 📈 系统状态

当前系统运行状态：

- ✅ **API 服务**: 正常运行
- ✅ **文件上传**: 功能可用
- ✅ **健康监控**: 实时监控
- ✅ **知识图谱**: 开发模式运行中 (支持节点创建、关系建立、图数据查询)
- ✅ **前端界面**: 中式古典设计完整界面 (包含所有功能模块)

### 🔧 开发模式说明

知识图谱系统当前运行在**开发模式**下，提供以下功能：
- ✅ **节点管理**: 创建、更新EMC实体节点 (设备、标准、测试等)
- ✅ **关系建立**: 建立实体间的语义关系
- ✅ **图数据查询**: 支持子图查询和图数据获取  
- ✅ **实时编辑**: 支持节点位置更新和属性修改
- 📋 **Mock数据**: 在内存中模拟图数据结构，便于测试和开发

**生产环境部署**：安装并启动Neo4j数据库以获得完整的图数据库功能。

### 🎨 前端界面功能

前端界面采用**中式古典审美设计**，提供完整的用户体验：

#### 🏠 系统概览
- **仪表板**: 系统状态监控、统计数据展示、最近活动时间线
- **服务状态**: 实时显示各组件运行状态
- **快捷操作**: 常用功能快速访问入口

#### 📁 文件管理
- **智能上传**: 支持拖拽上传、文件分类、标签管理
- **文件浏览**: 表格视图、搜索过滤、批量操作
- **AI分析**: 自动实体提取、关键词识别、内容摘要

#### 🕸️ 知识图谱
- **可视化**: D3.js力导向图、实时交互、节点拖拽
- **图谱编辑**: 节点创建、关系建立、属性修改
- **智能搜索**: 节点查找、类型过滤、图谱统计

#### 📝 Markdown编辑
- **实时预览**: 分屏编辑、语法高亮、快捷工具栏
- **文档管理**: 文件保存、历史版本、自动保存
- **EMC专业**: 表格支持、公式渲染、技术模板

#### ⚙️ 系统设置
- **API配置**: DeepSeek接口、Neo4j数据库、系统参数
- **连接测试**: 实时状态检查、错误诊断
- **主题切换**: 浅色/深色模式、字体调节

**立即体验**: 
- 前端界面: http://localhost:3000
- API服务: http://localhost:8000

---

## 🚀 快速启动

### 🖥️ 启动前端界面

```bash
# 方式一: 使用启动脚本 (推荐)
./start_frontend.sh

# 方式二: 手动启动
cd frontend
npm install  # 首次运行需要安装依赖
npm start
```

### 🔧 启动后端服务

```bash
# 启动知识图谱服务 (开发模式)
python3 start_services.py

# 测试数据库连接
python3 test_connections.py

# 测试知识图谱功能
python3 test_kg_functionality.py
```

### 📋 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 🎨 前端界面 | http://localhost:3000 | 中式古典设计的完整用户界面 |
| 🔌 API服务 | http://localhost:8000 | FastAPI后端服务接口 |
| 📚 API文档 | http://localhost:8000/docs | Swagger API交互文档 |
| 📁 文件上传 | http://localhost:8000/upload | 直接文件上传接口 |

---

## 📸 界面预览

### 🏠 系统概览仪表板
- 实时系统状态监控
- 文件统计和存储使用情况
- 最近活动时间线
- 快捷操作面板

### 📁 智能文件管理
- 拖拽式文件上传
- 多种文件格式支持 (PDF、Word、Excel、CSV等)
- 智能分类和标签管理
- AI自动分析和实体提取

### 🕸️ 知识图谱可视化
- D3.js力导向图渲染
- 实时交互式图谱编辑
- 节点和关系的创建、修改、删除
- 智能搜索和类型过滤

### 📝 Markdown编辑器
- 实时分屏预览
- 丰富的编辑工具栏
- EMC专业模板和示例
- 自动保存和版本管理

### ⚙️ 系统设置
- DeepSeek AI API配置
- Neo4j图数据库设置
- 系统参数调节
- 连接状态实时检测

---

## 🎨 设计理念

### 中式古典美学
本系统前端界面采用**中式古典审美设计**，将传统文化元素与现代技术完美融合：

- **🏮 色彩搭配**: 以金黄色(#d4af37)为主色调，象征高贵典雅
- **📜 字体选择**: 采用"马善政"等中文字体，传承古典韵味  
- **🎋 布局风格**: 对称平衡的设计原则，层次分明
- **💫 交互动效**: 温润如玉的过渡效果，提升用户体验

### 古典高雅设计
- **渐变背景**: 采用墨色渐变，营造雅致氛围
- **圆角设计**: 柔和的边角处理，符合东方审美
- **阴影效果**: 层次丰富的光影设计
- **金线装饰**: 精致的分割线和边框点缀

---

*最后更新: 2025年6月12日*

