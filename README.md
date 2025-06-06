EMC知识图谱系统 - 完整部署指南
🎯 项目概述
EMC知识图谱系统是一个专为电磁兼容性领域设计的智能知识管理平台，集成DeepSeek AI和Neo4j图数据库，支持文档智能分析、实体提取、知识图谱构建和可视化查询。
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
# 编辑.env文件，填入你的DeepSeek API密钥

# 3. 启动所有服务
docker-compose up -d

# 4. 验证部署
curl http://localhost:8000/health
🔧 详细配置说明
1. 环境变量配置 (.env文件)
创建.env文件并配置以下必需参数：
bash# 安全配置
EMC_SECRET_KEY=your-super-secret-key-min-32-chars
EMC_ENVIRONMENT=production

# DeepSeek API配置（必填）
EMC_DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
EMC_DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 数据库密码（必填）
EMC_NEO4J_PASSWORD=YourNeo4jPassword123
EMC_POSTGRES_PASSWORD=YourPostgresPassword123
EMC_REDIS_PASSWORD=YourRedisPassword123

# 可选配置
EMC_MAX_FILE_SIZE=104857600
EMC_RATE_LIMIT_REQUESTS_PER_MINUTE=60
2. 代理环境特殊配置
由于使用v2rayn代理，需要特别注意：
bash# Docker代理配置
mkdir -p ~/.docker
cat > ~/.docker/config.json << EOF
{
  "proxies": {
    "default": {
      "httpProxy": "http://127.0.0.1:10809",
      "httpsProxy": "http://127.0.0.1:10809"
    }
  }
}
EOF

# 或者使用国内镜像源
export DOCKER_REGISTRY=registry.cn-hangzhou.aliyuncs.com/library/
3. 服务端口说明
服务端口用途访问地址前端应用3000Web界面http://localhost:3000API网关8000后端APIhttp://localhost:8000Neo4j7474图数据库管理http://localhost:7474PostgreSQL5432关系数据库localhost:5432Redis6379缓存服务localhost:6379
📋 分步部署指南
步骤1：准备工作
bash# 检查Docker状态
docker --version
docker-compose --version

# 检查端口占用
netstat -tuln | grep -E ":(3000|8000|7474|5432|6379)"

# 创建必要目录
mkdir -p uploads temp logs
步骤2：获取DeepSeek API密钥

访问 DeepSeek官网
注册并登录账户
进入API管理页面
创建新的API密钥
复制密钥到.env文件

步骤3：启动数据库服务
bash# 仅启动数据库服务
docker-compose up -d postgres neo4j redis

# 等待数据库初始化（重要）
sleep 30

# 验证数据库连接
docker-compose logs postgres | grep "ready to accept connections"
docker-compose logs neo4j | grep "Started"
步骤4：启动应用服务
bash# 启动网关和前端
docker-compose up -d gateway frontend

# 查看启动日志
docker-compose logs -f gateway
步骤5：验证部署
bash# 健康检查
curl -s http://localhost:8000/health | jq

# 测试API
curl -X POST http://localhost:8000/api/deepseek/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello DeepSeek", "temperature": 0.7}'

# 访问前端
open http://localhost:3000
🛠️ 开发环境搭建
后端开发
bash# 创建Python虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动开发数据库
docker-compose -f docker-compose.test.yml up -d

# 运行API服务
python start_gateway.py
前端开发
bashcd frontend

# 安装依赖（使用国内源）
npm config set registry https://registry.npmmirror.com
npm install

# 启动开发服务器
npm start

# 构建生产版本
npm run build
🔍 功能使用指南
1. AI对话功能
bash# 测试DeepSeek集成
curl -X POST http://localhost:8000/api/deepseek/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "分析EMC标准EN 55032的主要要求",
    "temperature": 0.3,
    "max_tokens": 2000
  }'
2. 文件上传处理
bash# 上传EMC文档
curl -X POST http://localhost:8000/api/files/upload \
  -F "file=@test_document.pdf" \
  -F "extract_entities=true" \
  -F "build_graph=true"
3. 图数据库查询
bash# 执行Cypher查询
curl -X POST http://localhost:8000/api/graph/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "MATCH (n:EMCStandard) RETURN n LIMIT 10"
  }'
🚨 故障排除
常见问题及解决方案
1. Docker镜像拉取失败
bash# 问题：网络超时
# 解决：配置Docker代理或使用国内镜像
export DOCKER_REGISTRY=registry.cn-hangzhou.aliyuncs.com/library/
docker-compose down
docker-compose up -d
2. DeepSeek API调用失败
bash# 检查API密钥
grep DEEPSEEK_API_KEY .env

# 测试网络连接
curl -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  https://api.deepseek.com/v1/models

# 检查代理设置
echo $https_proxy
3. Neo4j连接失败
bash# 检查Neo4j状态
docker-compose logs neo4j

# 重启Neo4j
docker-compose restart neo4j

# 验证连接
curl http://localhost:7474/db/data/
4. 前端访问404
bash# 检查nginx配置
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf

# 重启前端服务
docker-compose restart frontend
5. 端口冲突
bash# 查找占用端口的进程
lsof -i :8000
netstat -tulpn | grep 8000

# 修改docker-compose.yml中的端口映射
# ports: - "8001:8000"  # 改为8001
日志分析
bash# 查看所有服务日志
docker-compose logs --tail=100

# 查看特定服务日志
docker-compose logs -f gateway
docker-compose logs -f neo4j

# 查看错误日志
docker-compose logs | grep -i error
📊 监控和维护
系统监控
bash# 检查服务状态
docker-compose ps

# 查看资源使用
docker stats

# 备份数据
docker-compose exec postgres pg_dump -U postgres emc_knowledge > backup.sql
定期维护
bash# 清理日志
docker-compose logs --tail=0 -f > /dev/null &
docker system prune -f

# 更新镜像
docker-compose pull
docker-compose up -d

# 重启所有服务
docker-compose restart
🔐 安全注意事项
生产环境安全

更改默认密码：修改所有数据库密码
配置HTTPS：使用SSL证书
限制访问：配置防火墙规则
定期备份：设置自动备份计划
监控日志：启用安全日志监控

bash# 生成强密码
openssl rand -base64 32

# 设置文件权限
chmod 600 .env
chown root:root .env
📚 API文档
主要端点
端点方法描述示例/healthGET健康检查curl http://localhost:8000/health/api/deepseek/chatPOSTAI对话见上文示例/api/files/uploadPOST文件上传见上文示例/api/graph/dataGET获取图数据curl http://localhost:8000/api/graph/data
认证方式
系统使用JWT认证，获取token后在请求头中添加：
bashAuthorization: Bearer your-jwt-token
🤝 开发贡献
代码规范
bash# Python代码格式化
black .
isort .

# 运行测试
pytest

# TypeScript检查
cd frontend && npm run type-check
📞 技术支持

文档问题：查看 /docs 页面
API问题：访问 http://localhost:8000/docs
网络问题：检查v2rayn代理设置
性能问题：调整Docker内存分配


部署完成后可以：

🌐 访问 http://localhost:3000 使用Web界面
📖 访问 http://localhost:8000/docs 查看API文档
💾 访问 http://localhost:7474 管理Neo4j数据库

记住：确保v2rayn代理正常工作，所有网络请求都能正常访问！