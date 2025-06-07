EMC知识图谱系统 - 完整部署指南
🎯 项目概述
EMC知识图谱系统是一个专为电磁兼容性领域设计的智能知识管理平台，集成DeepSeek AI和Neo4j图数据库，支持文档智能分析、实体提取、知识图谱构建和可视化查询。

**核心组件 (新增):**
*   **文档处理 (`services.file_processing`):** 解析多种格式的EMC文档 (PDF, DOCX, TXT等)。
*   **知识图谱构建 (`services.knowledge_graph`):**
    *   **EMC本体 (`emc_ontology.py`):** 定义知识图谱的节点（如标准、产品、测试）和关系。详情请见 [EMC_ONTOLOGY.md](EMC_ONTOLOGY.md)。
    *   **实体提取 (`entity_extractor.py`):** 从文本中识别定义的本体实体。
    *   **关系构建 (`relation_builder.py`):** 在提取的实体之间建立联系。
    *   **图谱管理 (`graph_manager.py`):** 编排实体提取和关系构建流程，并将其存入图数据库。
    *   **Neo4j服务 (`neo4j_emc_service.py`):** 提供与Neo4j图数据库的健壮交互。它使用`MERGE`操作来确保数据的一致性，避免重复创建节点和关系。在应用启动时，该服务还会自动为核心实体类型创建唯一性约束，以保证数据完整性和查询性能。
*   **EMC领域服务 (`services.emc_domain`):** 包含特定于EMC领域逻辑的服务，如标准处理、合规性检查等（利用知识图谱，开发中）。

🚀 安装与部署

本系统可以作为Windows桌面应用程序（推荐给终端用户）或作为一组开发者部署的服务来运行。

### 1. 终端用户 (Windows桌面应用程序)

对于希望直接使用本系统的用户，我们提供了预构建的Windows桌面应用程序。

*   **获取应用:**
    *   预构建的安装包 (`EMC知识图谱系统 Setup X.Y.Z.exe`) 和便携版ZIP (`EMC_Knowledge_Graph_Portable.zip`) 通常会在项目的 "Releases" 页面提供。
    *   如果从源码构建，这些文件会生成在项目根目录下的 `build_output` 文件夹中。
*   **包含内容:** 这些包内已集成用户界面和必要的Python后端服务。用户**无需单独安装Python或配置复杂的开发环境**。
*   **数据库依赖:**
    *   **重要:** 桌面应用程序需要后端数据库服务 (Neo4j, PostgreSQL, Redis) 才能完全运行。这些数据库服务**不包含**在桌面应用包内。
    *   **推荐设置:** 在运行桌面应用程序前，请使用Docker启动这些数据库。您可以使用项目根目录下的 `docker-compose.yml` 文件配合 `docker-compose up -d neo4j postgres redis` 命令，或者使用单独的配置文件如 `docker-compose-neo4j.yml`, `docker-compose-postgres.yml`, `docker-compose-redis.yml` 来分别启动它们。
    *   默认情况下，桌面应用的后端会尝试连接到 `localhost` 上的标准数据库端口和预设的凭据。对于高级用户，这些连接参数可以在后端服务的配置中修改（通常通过 `.env` 文件，详见配置部分）。
*   **运行:**
    1.  确保Docker已安装并正在运行。
    2.  使用 `docker-compose up -d neo4j postgres redis` (或针对性的docker-compose文件) 启动数据库服务。等待它们完全初始化。
    3.  运行安装程序 `EMC知识图谱系统 Setup X.Y.Z.exe` 并按提示安装，或解压 `EMC_Knowledge_Graph_Portable.zip` 到您选择的文件夹。
    4.  启动 "EMC知识图谱系统" 应用程序 (通过桌面快捷方式或便携文件夹中的启动脚本)。

### 2. 开发者 (设置完整开发环境)

开发者如果需要修改代码、参与贡献或在非Windows系统上运行，应设置完整的开发环境。

*   **环境要求:**
    *   Git
    *   Python 3.9+ (推荐使用虚拟环境)
    *   Node.js (LTS版本，包含npm)
    *   Docker Desktop (最新版)
    *   (Windows) Windows Terminal 或 PowerShell
*   **自动化部署 (Windows开发者):**
    *   项目根目录下的 `deploy_windows.bat` 脚本提供了一个自动化部署流程：
        *   检查并提示安装 Scoop (Windows包管理器)。
        *   通过Scoop安装Git, Python, Node.js, Docker (如果尚未安装)。
        *   克隆项目仓库 (如果脚本不在项目内)。
        *   设置Python虚拟环境并安装依赖。
        *   安装前端依赖。
        *   创建并提示配置 `.env` 文件。
        *   使用 Docker Compose 启动后端数据库服务 (Neo4j, PostgreSQL, Redis)。
        *   (可选) 构建并启动完整的Electron桌面应用。
    *   **使用:** 以管理员身份运行 `deploy_windows.bat` 并按照提示操作。
*   **手动部署 (所有系统):**
    1.  **克隆项目:**
        ```bash
        git clone https://github.com/zhakil/emc_knowledge_graph.git
        cd emc_knowledge_graph
        ```
    2.  **配置环境变量:**
        复制 `.env.example` 为 `.env`，并根据您的环境和API密钥进行配置 (详见下方“配置说明”部分)。
        ```bash
        cp .env.example .env
        # 编辑 .env 文件，至少填入 EMC_DEEPSEEK_API_KEY 和数据库密码
        ```
    3.  **启动后端服务 (Docker):**
        这将启动API网关、Neo4j、PostgreSQL和Redis。
        ```bash
        docker-compose up -d
        ```
        *   若要仅启动数据库服务: `docker-compose up -d neo4j postgres redis`
        *   若要单独启动某个数据库 (例如使用 `docker-compose-neo4j.yml`):
            ```bash
            docker-compose -f docker-compose-neo4j.yml up -d
            ```
    4.  **构建和运行桌面应用 (可选):**
        如果您希望从源码运行或构建Windows桌面应用：
        ```bash
        python scripts/build_windows_app.py
        ```
        构建完成后，产物位于 `build_output` 目录。
        要运行Electron应用的开发版本 (假设后端服务已通过Docker或其他方式启动)：
        ```bash
        cd desktop
        npm install
        npm start
        ```
    5.  **前端开发 (可选):**
        如果仅需进行前端开发 (假设后端服务已运行)：
        ```bash
        cd frontend
        npm install
        npm start
        ```
    6.  **验证部署:**
        ```bash
        curl http://localhost:8000/health # 检查API网关 (如果已启动)
        # 访问 http://localhost:7474 查看Neo4j (如果已启动)
        # 访问 http://localhost:3000 查看前端 (如果已启动)
        ```

🔧 配置说明
1. 环境变量配置 (.env文件)
`.env` 文件用于存储所有敏感配置和环境特定参数。在首次启动任何服务或脚本前，请确保已从 `.env.example` 复制并正确配置了 `.env` 文件。
*   **创建:** `cp .env.example .env`
*   **关键参数:**
    *   `EMC_DEEPSEEK_API_KEY`: 您的DeepSeek API密钥 (**必填**)。
    *   `EMC_NEO4J_PASSWORD`, `EMC_POSTGRES_PASSWORD`, `EMC_REDIS_PASSWORD`: 数据库服务的密码。如果您在 `docker-compose.yml` 中修改了这些服务的默认密码，请务必在此处同步更新。
    *   `EMC_SECRET_KEY`: 用于API安全的密钥，应为一个长随机字符串。
    *   `EMC_NEO4J_URI`, `EMC_NEO4J_USER`: Neo4j连接参数，通常保持默认值，除非您的Neo4j实例位于不同地址或使用不同用户。
*   **桌面应用配置:**
    *   打包的Windows桌面应用 (`emc_backend.exe`) 在启动时会尝试加载位于其工作目录下的 `.env` 文件。当通过Electron主进程启动时，这个工作目录通常是 `emc_backend.exe` 所在的 `desktop/resources/backend/` 目录（在打包应用中，这会是 `process.resourcesPath + '/backend/'`）。
    *   如果您直接运行从 `build_output/EMC_Knowledge_Graph_Portable/` 启动的便携版，可以尝试将 `.env` 文件放置在该目录下。
    *   `deploy_windows.bat` 脚本会自动在项目根目录创建 `.env` 文件，构建过程可能会将其包含或按需复制。

2. 代理环境特殊配置 (如果需要通过代理访问外部API如DeepSeek)
由于使用v2rayn代理，需要特别注意：
bash# Docker代理配置
mkdir -p ~/.docker
cat > ~/.docker/config.json << EOF
{
  "proxies": {
    "default": {
      "httpProxy": "http://127.0.0.1:10809", # 根据您的v2rayn HTTP代理端口调整
      "httpsProxy": "http://127.0.0.1:10809" # 根据您的v2rayn HTTP代理端口调整
    }
  }
}
EOF
# Windows用户请在Docker Desktop设置中配置代理。

# 或者使用国内镜像源 (如果DeepSeek API和GitHub可以直连，则非必须)
# export DOCKER_REGISTRY=registry.cn-hangzhou.aliyuncs.com/library/

3. 服务端口说明
服务端口用途默认访问地址 (可能因配置而异)前端应用 (开发模式)3000Web界面http://localhost:3000API网关 (通过Docker或直接运行)8000后端APIhttp://localhost:8000 (或网关配置的端口，如8001)Neo4j7474图数据库管理http://localhost:7474 (或Docker映射的端口，如7475)PostgreSQL5432关系数据库localhost:5432 (或Docker映射的端口，如5433)Redis6379缓存服务localhost:6379 (或Docker映射的端口，如6380)

## 技术细节与可扩展性

*   **Neo4j性能:**
    *   **内存配置:** 对于通过 Docker 运行 Neo4j 服务的用户，可以在 `docker-compose.yml` 文件中调整 Neo4j 的内存设置 (如 `NEO4J_dbms_memory_pagecache_size` 和 `NEO4J_dbms_memory_heap_max__size`) 以适应不同规模的数据集和负载。
    *   **数据完整性与查询:** 系统现在会自动在 Neo4j 数据库中为核心实体类型（如 `EMCStandard`, `Product`, `Document`, `Component` 等）的 `id` 属性创建唯一性约束。这不仅增强了数据的一致性，也显著提升了相关查询的性能。此功能在应用启动时由 `Neo4jEMCService`自动处理。
*   **后端服务:** API网关和核心服务被设计为可独立扩展。

# 测试AI对话API (通过网关)
curl -X POST http://localhost:8000/api/deepseek/chat   -H "Content-Type: application/json"   -d '{
    "prompt": "解释一下什么是EMC电磁兼容性?",
    "temperature": 0.5,
    "max_tokens": 500
  }'

# 访问前端Web界面
echo "Access Frontend at: http://localhost:3000"
echo "Access Neo4j Browser at: http://localhost:7474 (User: neo4j, Password: your .env password)"

🛠️ 开发环境搭建
后端开发 (`gateway` 和 `services`)
bash# 创建Python虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scriptsctivate

# 安装依赖
pip install -r requirements.txt

# (可选) 启动开发用数据库 (如果不想用全局docker-compose里的)
# docker-compose -f docker-compose.dev.yml up -d # 假设有此文件

# 运行API服务 (gateway)
# python gateway/main.py # 或者 python start_gateway.py 如果有此脚本
# (请根据实际启动脚本调整)

前端开发 (`frontend`)
bashcd frontend

# 安装依赖（建议使用npm或yarn，根据package.json配置）
# npm config set registry https://registry.npmmirror.com # 可选，设置国内源
npm install

# 启动开发服务器
npm start # 通常是 react-scripts start 或 vite

# 构建生产版本
npm run build

🔍 功能使用指南
1. AI对话功能
通过API或前端界面与DeepSeek模型进行对话，获取EMC专业知识问答。
bash# 示例API调用 (见上方验证部署部分)

2. 文件上传与知识提取
通过API上传EMC相关文档（如测试报告、标准PDF等）。系统将尝试提取文本内容，并（未来）通过`EMCGraphManager`构建知识图谱。
bash# 上传EMC文档 (API示例)
curl -X POST http://localhost:8000/api/files/upload   -F "file=@path/to/your/emc_document.pdf"   # -F "extract_entities=true" # (旧参数，新流程由GraphManager处理)
  # -F "build_graph=true"     # (旧参数，新流程由GraphManager处理)

*注意：文件上传后的知识图谱构建流程依赖于 `EMCGraphManager` 和 `Neo4jEMCService`。*

3. 图数据库查询 (通过Neo4j浏览器或API)
直接查询Neo4j数据库以探索已构建的知识图谱。
*   **Neo4j Browser:**访问 `http://localhost:7474`
*   **API查询 (示例):**
bash# 执行Cypher查询 (此API端点 `/api/graph/query` 可能需要实现或调整)
curl -X POST http://localhost:8000/api/graph/query   -H "Content-Type: application/json"   -d '{
    "query": "MATCH (s:EMCStandard) WHERE s.category = 'Emissions' RETURN s.name, s.version LIMIT 10"
  }'

🚨 故障排除
常见问题及解决方案
1. Docker镜像拉取失败
bash# 问题：网络超时
# 解决：配置Docker代理 (见上方"代理环境特殊配置") 或使用国内镜像源。
# export DOCKER_REGISTRY=registry.cn-hangzhou.aliyuncs.com/library/
# docker-compose down && docker-compose pull && docker-compose up -d
2. DeepSeek API调用失败
bash# 检查API密钥和Base URL
grep DEEPSEEK_API .env

# 测试网络连接 (确保能访问 DeepSeek API 地址)
curl -v https://api.deepseek.com/v1/models -H "Authorization: Bearer YOUR_API_KEY"

# 检查代理设置 (Docker内服务是否能通过代理访问外部)
3. Neo4j连接失败或密码错误
bash# 检查Neo4j状态和日志
docker-compose logs neo4j
# 确认Neo4j密码与.env文件中 EMC_NEO4J_PASSWORD 一致。
# 首次启动后，可能需要在Neo4j浏览器中更改初始密码，并同步更新.env。
# 如果修改了密码，需要重启 gateway 服务 (或所有服务) 以加载新密码。
# docker-compose restart gateway neo4j
4. 前端访问404或连接后端失败
bash# 检查nginx配置 (如果前端通过nginx代理)
# docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
# 检查API网关 (gateway) 是否正常运行且端口正确。
docker-compose logs gateway
5. 端口冲突
bash# 查找占用端口的进程 (示例: 8000)
# lsof -i :8000 (Linux/macOS)
# netstat -ano | findstr ":8000" (Windows)
# 修改 `docker-compose.yml` 中的端口映射，例如: "8001:8000"
日志分析
bash# 查看所有服务日志 (最近100条)
docker-compose logs --tail=100

# 实时查看特定服务日志
docker-compose logs -f gateway
docker-compose logs -f neo4j

# 查看错误日志
docker-compose logs | grep -iE "error|failed|exception"
📊 监控和维护
系统监控
bash# 检查服务状态
docker-compose ps

# 查看容器资源使用
docker stats
备份数据
bash# Neo4j 数据备份 (Neo4j Enterprise有在线备份, Community版通常是停止服务后复制数据目录或dump)
# docker-compose stop neo4j
# sudo cp -r data/neo4j data/neo4j_backup_YYYYMMDD
# docker-compose start neo4j
# 或者使用 neo4j-admin dump (查阅Neo4j文档)

# PostgreSQL 数据备份
docker-compose exec postgres pg_dumpall -U postgres > emc_kg_pg_dump.sql # 用户名可能不同，参考.env
定期维护
bash# 清理Docker未使用资源
docker system prune -af

# 更新镜像 (谨慎操作，注意版本兼容性)
# docker-compose pull
# docker-compose up -d --remove-orphans

# 重启所有服务
docker-compose restart
🔐 安全注意事项
生产环境安全

*   **强密码策略:** 为所有服务（特别是数据库）设置强密码，并定期更新。
*   **环境变量安全:** 不要将 `.env` 文件直接提交到公共代码库。使用 `.env.example` 作为模板。
*   **网络暴露:** 仅将必要的端口暴露给外部网络。使用防火墙限制访问。
*   **HTTPS:** 为前端和API网关配置HTTPS (SSL/TLS证书)。
*   **定期备份:** 实施定期数据备份策略。
*   **安全审计:** 定期进行安全审计和漏洞扫描。

bash# 生成强密码示例
# openssl rand -base64 32
📚 API文档
主要端点 (部分为规划中或待实现)
*   `/health` (GET): 系统健康检查。
*   `/api/deepseek/chat` (POST): AI对话接口。
*   `/api/files/upload` (POST): 文件上传接口，用于知识图谱构建。
*   `/api/graph/query` (POST): (规划中) 执行Cypher查询知识图谱。
*   `/api/graph/data` (GET): (规划中) 获取图数据用于可视化。

详细API文档请在网关启动后访问 `/docs` (Swagger UI) 或 `/redoc`。

🤝 开发贡献
我们欢迎对本项目的贡献！请遵循以下步骤：
1.  Fork本仓库。
2.  创建您的特性分支 (`git checkout -b feature/AmazingFeature`)。
3.  提交您的更改 (`git commit -m 'Add some AmazingFeature'`)。
4.  推送到分支 (`git push origin feature/AmazingFeature`)。
5.  打开一个Pull Request。

代码规范
bash# Python (使用 Black 和 isort)
black .
isort .

# 运行测试 (规划中，需要完善测试用例)
# pytest tests/
# (或者 python -m unittest discover tests)

# TypeScript/Frontend (根据项目内工具配置)
# cd frontend && npm run lint && npm run test
📞 技术支持

*   文档问题：请先仔细阅读本文档和 [EMC_ONTOLOGY.md](EMC_ONTOLOGY.md)。
*   部署问题：参考“故障排除”部分，检查Docker、网络和环境变量配置。
*   API问题：参考API文档或Swagger UI。
*   代码问题：欢迎提交Issue或Pull Request。


部署完成后可以：

🌐 访问 `http://localhost:3000` 使用Web界面 (如果通过 `docker-compose up -d frontend` 或类似方式启动)
📖 访问 `http://localhost:8000/docs` 查看API文档 (若API网关服务启动)
💾 访问 `http://localhost:7474` 管理Neo4j数据库 (默认用户: `neo4j`, 密码见 `.env` 文件)

**重要提示:** 确保v2rayn（或其他网络代理）配置正确，以便Docker容器或本地运行的服务可以访问外部网络（如DeepSeek API）。