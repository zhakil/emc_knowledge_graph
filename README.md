# 📊 EMC 知识图谱系统

![版本](https://img.shields.io/badge/版本-1.0.0-blue.svg)
![状态](https://img.shields.io/badge/状态-运行中-green.svg)
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

### 🏗️ 技术架构
- **后端框架**：FastAPI + Python 3.11+
- **AI 集成**：DeepSeek API (OpenAI 兼容)
- **图数据库**：Neo4j 5.15+
- **缓存层**：Redis 7.4+
- **关系数据库**：PostgreSQL 16+
- **前端框架**：React 18 + TypeScript + Material-UI
- **容器化**：Docker + Docker Compose

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

## 📈 系统状态

当前系统运行状态：

- ✅ **API 服务**: 正常运行
- ✅ **文件上传**: 功能可用
- ✅ **健康监控**: 实时监控
- ⚠️ **知识图谱**: 开发模式（跳过数据库连接）
- ⚠️ **前端界面**: 可选组件

**立即开始**: http://localhost:8000/upload

---

*最后更新: 2025年6月11日*