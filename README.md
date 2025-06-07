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
    *   **Neo4j服务 (`neo4j_emc_service.py`):** 与Neo4j图数据库进行交互（*注意：此组件的实现目前遇到工具问题，正在积极解决中*）。
*   **EMC领域服务 (`services.emc_domain`):** 包含特定于EMC领域逻辑的服务，如标准处理、合规性检查等（利用知识图谱，开发中）。

🚀 快速开始（5分钟部署）
环境要求

Docker Desktop 4.0+
Git
8GB+ RAM，20GB+ 磁盘空间
网络环境：确保v2rayn代理正常工作

一键部署步骤
bash# 1. 克隆项目
git clone https://github.com/zhakil/emc_knowledge_graph.git
cd emc_knowledge_graph

# 2. 配置环境变量
cp .env.example .env
# 编辑.env文件，填入你的DeepSeek API密钥和Neo4j密码

# 3. 启动所有服务
docker-compose up -d

# 4. 验证部署
curl http://localhost:8000/health

🔧 详细配置说明
1. 环境变量配置 (.env文件)
创建.env文件并配置以下必需参数：
bash# 安全配置
EMC_SECRET_KEY=your-super-secret-key-min-32-chars
EMC_ENVIRONMENT=production # development or production

# DeepSeek API配置（必填）
EMC_DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
EMC_DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 数据库密码（必填）
EMC_NEO4J_URI=bolt://localhost:7687 # Or your Neo4j instance URI
EMC_NEO4J_USER=neo4j
EMC_NEO4J_PASSWORD=YourNeo4jPassword123 # 修改为您自己的强密码
EMC_POSTGRES_PASSWORD=YourPostgresPassword123
EMC_REDIS_PASSWORD=YourRedisPassword123

# 可选配置
EMC_MAX_FILE_SIZE=104857600 # Maximum upload file size in bytes
EMC_RATE_LIMIT_REQUESTS_PER_MINUTE=60 # API rate limit

2. 代理环境特殊配置
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
服务端口用途访问地址前端应用3000Web界面http://localhost:3000API网关8000后端APIhttp://localhost:8000Neo4j7474图数据库管理http://localhost:7474PostgreSQL5432关系数据库localhost:5432Redis6379缓存服务localhost:6379
📋 分步部署指南
步骤1：准备工作
bash# 检查Docker状态
docker --version
docker-compose --version

# 检查端口占用 (Linux/macOS)
# netstat -tuln | grep -E ":(3000|8000|7474|5432|6379)"
# Windows: netstat -ano | findstr ":3000 :8000 :7474 :5432 :6379"

# 创建必要目录 (如果项目未包含)
mkdir -p uploads temp logs data/neo4j data/postgres
步骤2：获取DeepSeek API密钥

访问 DeepSeek官网
注册并登录账户
进入API管理页面
创建新的API密钥
复制密钥到`.env`文件的`EMC_DEEPSEEK_API_KEY`。

步骤3：启动数据库服务
bash# 仅启动数据库服务
docker-compose up -d postgres neo4j redis

# 等待数据库初始化（重要）
echo "Waiting for databases to initialize..."
sleep 30 # 增加等待时间确保Neo4j完全启动

# 验证数据库连接
docker-compose logs postgres | grep "ready to accept connections"
docker-compose logs neo4j | grep "Remote interface available at" # Neo4j 4.x/5.x
# 或者 docker-compose logs neo4j | grep "Started." (旧版)
docker-compose logs redis | grep "Ready to accept connections"

步骤4：启动应用服务
bash# 启动网关和前端
docker-compose up -d gateway frontend

# 查看启动日志
docker-compose logs -f gateway
docker-compose logs -f frontend

步骤5：验证部署
bash# 健康检查 (API 网关)
curl -s http://localhost:8000/health | jq

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

*注意：文件上传后的知识图谱构建流程依赖于 `EMCGraphManager` 和 `Neo4jEMCService`。由于 `Neo4jEMCService` 当前实现存在问题，此部分功能可能未完全激活。*

3. 图数据库查询 (通过Neo4j浏览器或API)
直接查询Neo4j数据库以探索已构建的知识图谱。
*   **Neo4j Browser:**访问 `http://localhost:7474`
*   **API查询 (示例):**
bash# 执行Cypher查询 (此API端点 `/api/graph/query` 可能需要实现或调整)
curl -X POST http://localhost:8000/api/graph/query   -H "Content-Type: application/json"   -d '{
    "query": "MATCH (s:EMCStandard) WHERE s.category = 'Emissions' RETURN s.name, s.version LIMIT 10"
  }'

*当前知识图谱的自动构建和查询功能受限于 `Neo4jEMCService` 的状态。*

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

🌐 访问 `http://localhost:3000` 使用Web界面
📖 访问 `http://localhost:8000/docs` 查看API文档 (若网关服务包含Swagger)
💾 访问 `http://localhost:7474` 管理Neo4j数据库 (默认用户: `neo4j`, 密码见 `.env` 文件)

**重要提示:** 确保v2rayn（或其他网络代理）配置正确，以便Docker容器可以访问外部网络（如DeepSeek API）。由于`Neo4jEMCService`组件的实现问题，知识图谱的自动构建和利用功能目前可能不完整。我们正在努力解决此问题。