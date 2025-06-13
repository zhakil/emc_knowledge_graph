# EMC知识图谱系统 - Docker部署指南

## 🚀 快速开始

### 前提条件
- Docker 20.10+
- Docker Compose 2.0+
- 至少4GB可用内存
- 10GB可用磁盘空间

### 一键部署
```bash
# 克隆项目
git clone <repository-url>
cd emc_knowledge_graph

# 启动完整系统
docker compose -f docker-compose.community.yml up -d

# 查看服务状态
docker compose -f docker-compose.community.yml ps
```

## 📱 访问地址

部署成功后，可以通过以下地址访问：

- **🌐 前端界面**: http://localhost:3000
- **📊 API文档**: http://localhost:8000/docs
- **⚡ Neo4j Browser**: http://localhost:7474 (用户名: neo4j, 密码: emc_password_123)
- **📈 系统健康**: http://localhost:8000/health
- **🔄 Nginx代理**: http://localhost:80

## 🏗️ 服务架构

### 核心服务
- **emc-frontend**: React前端应用 (端口: 3000)
- **emc-backend**: FastAPI后端服务 (端口: 8000)
- **neo4j**: 图数据库 (端口: 7474, 7687)
- **redis**: 缓存服务 (端口: 6379)
- **nginx**: 反向代理 (端口: 80)

### 网络配置
- 内部网络: emc-network (172.21.0.0/16)
- 所有服务通过内部网络通信
- 外部只暴露必要端口

## 🔧 配置说明

### 环境变量
主要环境变量在 `docker-compose.community.yml` 中配置：

```yaml
# 前端配置
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_WEBSOCKET_URL=ws://localhost:8000

# 后端配置
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=emc_password_123
REDIS_URL=redis://redis:6379/0
```

### 数据持久化
以下数据卷用于数据持久化：
- `neo4j_data`: Neo4j数据文件
- `neo4j_logs`: Neo4j日志文件
- `redis_data`: Redis数据文件
- `./data`: 应用数据目录
- `./logs`: 应用日志目录

## 🛠️ 常用命令

### 启动和停止
```bash
# 启动所有服务
docker compose -f docker-compose.community.yml up -d

# 停止所有服务
docker compose -f docker-compose.community.yml down

# 重启特定服务
docker compose -f docker-compose.community.yml restart emc-backend

# 查看服务状态
docker compose -f docker-compose.community.yml ps

# 查看服务日志
docker compose -f docker-compose.community.yml logs -f emc-backend
```

### 数据管理
```bash
# 备份Neo4j数据
docker exec emc-neo4j neo4j-admin dump --database=neo4j --to=/tmp/neo4j-backup.dump

# 清理未使用的数据卷
docker volume prune

# 查看数据卷使用情况
docker system df
```

### 开发调试
```bash
# 进入后端容器
docker exec -it emc-backend bash

# 进入Neo4j容器
docker exec -it emc-neo4j bash

# 实时查看所有服务日志
docker compose -f docker-compose.community.yml logs -f
```

## 🔍 健康检查

### 系统状态检查
```bash
# 检查所有服务健康状态
curl http://localhost:8000/health

# 检查Neo4j连接
curl http://localhost:7474/db/neo4j/tx/commit \
  -H "Authorization: Basic bmVvNGo6ZW1jX3Bhc3N3b3JkXzEyMw==" \
  -H "Content-Type: application/json" \
  -d '{"statements":[{"statement":"RETURN 1"}]}'

# 检查Redis连接
docker exec emc-redis redis-cli ping
```

### 性能监控
```bash
# 查看容器资源使用
docker stats

# 查看网络连接
docker compose -f docker-compose.community.yml exec emc-backend netstat -tulpn
```

## 🚨 故障排除

### 常见问题

#### 1. 端口冲突
如果遇到端口冲突，修改 `docker-compose.community.yml` 中的端口映射：
```yaml
ports:
  - "8080:8000"  # 将后端端口改为8080
```

#### 2. 内存不足
调整服务资源限制：
```yaml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'
```

#### 3. Neo4j启动失败
检查Neo4j日志并调整内存配置：
```bash
docker compose -f docker-compose.community.yml logs neo4j

# 减少Neo4j内存使用
NEO4J_dbms_memory_heap_max_size=512m
```

#### 4. 前端构建失败
清理并重新构建前端镜像：
```bash
docker compose -f docker-compose.community.yml build --no-cache emc-frontend
```

### 日志分析
```bash
# 查看错误日志
docker compose -f docker-compose.community.yml logs --tail=100 emc-backend | grep ERROR

# 导出日志到文件
docker compose -f docker-compose.community.yml logs > system.log
```

## 🔐 安全配置

### 生产环境建议
1. **修改默认密码**:
   ```yaml
   NEO4J_AUTH=neo4j/your_secure_password
   ```

2. **限制网络访问**:
   ```yaml
   ports:
     - "127.0.0.1:7474:7474"  # 只允许本地访问
   ```

3. **启用HTTPS**: 配置SSL证书并修改nginx配置

4. **数据备份**: 设置定期备份任务

## 📈 扩展部署

### 高可用部署
使用多副本部署关键服务：
```yaml
deploy:
  replicas: 2
  restart_policy:
    condition: on-failure
    max_attempts: 3
```

### 集群部署
参考 `config/docker-compose.yml` 中的完整监控栈配置。

## 🆘 支持与反馈

如果遇到问题：
1. 检查本文档的故障排除部分
2. 查看项目的GitHub Issues
3. 提交新的Issue并附上详细日志

---

**注意**: 这是社区版Docker配置，适用于开发和测试环境。生产环境部署请参考完整版配置文件。