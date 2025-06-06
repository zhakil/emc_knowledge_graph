#!/bin/bash

echo "=== 启动核心数据服务 ==="

# 1. 检查Neo4j状态（已经在运行）
if curl -f http://localhost:7474 2>/dev/null; then
    echo "✓ Neo4j 已运行"
else
    echo "⚠ Neo4j 未运行，需要启动"
fi

# 2. 停止可能冲突的容器
echo "清理冲突容器..."
docker stop emc_postgres emc_redis 2>/dev/null || true
docker rm emc_postgres emc_redis 2>/dev/null || true

# 3. 拉取镜像（使用最简单的方式）
echo "拉取必要镜像..."
./scripts/pull_with_mirrors.sh

# 4. 直接启动容器（不依赖compose文件）
echo "启动PostgreSQL..."
docker run -d \
    --name emc_postgres \
    -p 5432:5432 \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=Zqz112233 \
    -e POSTGRES_DB=emc_knowledge \
    -v emc_postgres_data:/var/lib/postgresql/data \
    --restart unless-stopped \
    postgres:15-alpine

echo "启动Redis..."
docker run -d \
    --name emc_redis \
    -p 6379:6379 \
    -v emc_redis_data:/data \
    --restart unless-stopped \
    redis:7-alpine redis-server --requirepass Zqz112233

# 5. 等待服务就绪
echo "等待服务启动..."
sleep 10

# 6. 验证连接
echo "验证服务连接..."

# PostgreSQL验证
for i in {1..10}; do
    if docker exec emc_postgres pg_isready -U postgres 2>/dev/null; then
        echo "✓ PostgreSQL 就绪"
        break
    fi
    echo "等待PostgreSQL... ($i/10)"
    sleep 2
done

# Redis验证
if docker exec emc_redis redis-cli -a Zqz112233 ping 2>/dev/null | grep -q PONG; then
    echo "✓ Redis 就绪"
else
    echo "⚠ Redis 连接检查跳过"
fi

# Neo4j验证
if curl -f http://localhost:7474 2>/dev/null; then
    echo "✓ Neo4j 就绪"
fi

echo "=== 核心服务启动完成 ==="
echo ""
echo "服务访问信息:"
echo "- PostgreSQL: localhost:5432 (postgres/Zqz112233)"
echo "- Redis: localhost:6379 (密码: Zqz112233)" 
echo "- Neo4j: http://localhost:7474 (neo4j/Zqz112233)"
echo ""
echo "检查服务状态: docker ps"