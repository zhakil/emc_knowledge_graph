# EMC知识图谱系统 - 智能部署指南

> 🎯 **项目定位**：基于DeepSeek AI和Neo4j图数据库的电磁兼容性领域智能知识管理平台

## 📋 系统架构概述

EMC知识图谱系统采用微服务架构，集成了现代化的AI技术栈和图数据库技术。系统核心组件包括文档智能处理引擎、知识图谱构建器、实体关系提取器和可视化查询接口。整个系统通过Docker容器化部署，确保环境一致性和快速扩展能力。

**核心技术栈理论基础：**
- **DeepSeek AI模型**：提供自然语言理解和专业领域知识问答能力
- **Neo4j图数据库**：存储和管理复杂的实体关系网络
- **FastAPI网关**：高性能异步API服务框架
- **React前端**：现代化用户交互界面

---

## 🚀 快速部署（三步完成）

### ⚡ 第一步：环境准备与项目获取

**🔧 必须操作：**
```bash
# 克隆项目到本地
git clone https://github.com/zhakil/emc_knowledge_graph.git
cd emc_knowledge_graph

# 检查系统环境
docker --version && docker-compose --version
```

**⚠️ 关键注意事项：**
- 确保Docker Desktop版本≥4.0，内存分配≥8GB
- 网络环境必须能够访问DeepSeek API（需要稳定的网络连接）
- 预留磁盘空间≥20GB用于镜像和数据存储

**📍 修改地址**：如果GitHub访问困难，可通过以下镜像地址获取：
```bash
# 备用镜像地址
git clone https://gitee.com/mirror/emc_knowledge_graph.git
```

### ⚡ 第二步：配置环境变量

**🔧 必须操作：**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件（使用你熟悉的编辑器）
nano .env  # 或 vim .env 或 code .env
```

**📝 核心配置项（必须填写）：**
```env
# 安全密钥（32位以上随机字符串）
EMC_SECRET_KEY=your-super-secret-key-min-32-chars

# DeepSeek API配置（从官网获取）
EMC_DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
EMC_DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 数据库密码（设置强密码）
EMC_NEO4J_PASSWORD=YourNeo4jPassword123
EMC_POSTGRES_PASSWORD=YourPostgresPassword123
EMC_REDIS_PASSWORD=YourRedisPassword123
```

**⚠️ 重要注意事项：**
- DeepSeek API密钥获取地址：https://platform.deepseek.com/
- 密码设置必须包含大小写字母、数字和特殊字符
- 切勿将包含真实密钥的.env文件提交到代码仓库

**📍 修改地址**：
- DeepSeek API申请：https://platform.deepseek.com/api_keys
- 配置文件模板路径：`项目根目录/.env.example`

### ⚡ 第三步：启动系统服务

**🔧 必须操作：**
```bash
# 一键启动所有服务
docker-compose up -d

# 等待服务初始化（重要）
echo "等待系统初始化完成..."
sleep 60

# 验证部署状态
curl http://localhost:8000/health
```

**🎯 验证操作：**
```bash
# 测试AI对话功能
curl -X POST http://localhost:8000/api/deepseek/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "什么是EMC电磁兼容性?", "temperature": 0.5}'

# 检查所有服务状态
docker-compose ps
```

**⚠️ 启动注意事项：**
- Neo4j数据库初始化需要额外时间，请耐心等待
- 如果使用代理网络，确保Docker可以通过代理访问外部API
- 首次启动可能需要下载较大的镜像文件

**📍 访问地址：**
- Web界面：http://localhost:3000
- API文档：http://localhost:8000/docs
- Neo4j管理：http://localhost:7474 （用户名：neo4j，密码：配置文件中的密码）

---

## 🛠️ 高级配置选项

### 网络代理配置（可选）

如果您的网络环境需要代理访问外部API，请配置Docker代理设置：

**配置理论：** Docker容器默认使用宿主机网络配置，但在某些网络环境下需要显式配置代理参数以确保容器内服务能够访问外部API接口。

```bash
# 创建Docker代理配置
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
```

### 服务端口映射说明

| 服务 | 内部端口 | 外部端口 | 用途 | 访问地址 |
|------|----------|----------|------|----------|
| 前端界面 | 3000 | 3000 | Web用户界面 | http://localhost:3000 |
| API网关 | 8000 | 8000 | 后端API服务 | http://localhost:8000 |
| Neo4j | 7474/7687 | 7474/7687 | 图数据库 | http://localhost:7474 |
| PostgreSQL | 5432 | 5432 | 关系数据库 | localhost:5432 |
| Redis | 6379 | 6379 | 缓存服务 | localhost:6379 |

---

## 🚨 故障排除指南

### 常见问题诊断

**问题1：Docker镜像拉取失败**
```bash
# 诊断命令
docker pull hello-world

# 解决方案：配置镜像源
export DOCKER_REGISTRY=registry.cn-hangzhou.aliyuncs.com/library/
```

**问题2：DeepSeek API连接失败**
```bash
# 测试API连接
curl -v https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"

# 检查环境变量
grep DEEPSEEK .env
```

**问题3：Neo4j连接异常**
```bash
# 查看Neo4j日志
docker-compose logs neo4j

# 重置Neo4j密码
docker-compose restart neo4j
```

### 系统监控命令

```bash
# 查看服务运行状态
docker-compose ps

# 查看系统资源使用
docker stats

# 查看服务日志
docker-compose logs -f gateway
```

---

## 📚 API使用指南

### 核心API端点

**理论基础：** 系统采用RESTful API设计，所有接口遵循HTTP标准，支持JSON格式数据交换。API网关负责请求路由、认证授权和负载均衡。

**主要接口：**

1. **健康检查接口**
   ```bash
   GET /health
   # 返回系统各组件运行状态
   ```

2. **AI对话接口**
   ```bash
   POST /api/deepseek/chat
   # 发送EMC专业问题，获取AI解答
   ```

3. **文档上传接口**
   ```bash
   POST /api/files/upload
   # 上传EMC相关文档，自动提取知识图谱
   ```

4. **图谱查询接口**
   ```bash
   POST /api/graph/query
   # 执行Cypher查询，检索知识图谱数据
   ```

详细API文档请访问：http://localhost:8000/docs

---

## 🔐 安全最佳实践

### 生产环境安全配置

**安全理论基础：** 容器化应用的安全性需要从多个层面考虑，包括网络隔离、访问控制、数据加密和审计日志。

**必要安全措施：**

1. **密码安全策略**
   - 使用至少32位随机密钥
   - 定期轮换数据库密码
   - 启用多因素认证

2. **网络安全配置**
   - 仅暴露必要端口到外网
   - 配置防火墙规则
   - 使用HTTPS加密传输

3. **数据保护措施**
   - 定期备份重要数据
   - 实施访问权限控制
   - 监控异常访问行为

---

## 🤝 开发贡献

我们欢迎所有形式的技术贡献！请遵循以下开发流程：

1. Fork项目仓库
2. 创建功能分支 `git checkout -b feature/YourFeature`
3. 提交代码变更 `git commit -m 'Add YourFeature'`
4. 推送到远程分支 `git push origin feature/YourFeature`
5. 创建Pull Request

**代码规范要求：**
```bash
# Python代码格式化
black . && isort .

# 运行单元测试
pytest tests/

# 前端代码检查
cd frontend && npm run lint
```

---

## 📞 技术支持

**获取帮助的优先顺序：**

1. **文档自查**：先阅读本文档和项目Wiki
2. **日志分析**：使用故障排除部分的诊断命令
3. **社区支持**：在GitHub Issues提交问题
4. **技术交流**：参与项目讨论区

**项目地址：** https://github.com/zhakil/emc_knowledge_graph

**文档更新：** 本文档持续更新，建议定期查看最新版本

---

*最后更新时间：2025年6月*