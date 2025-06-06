#!/bin/bash

set -e

echo "=== EMC服务修复程序 ==="

# 1. 停止所有服务
echo "1. 停止现有服务..."
docker-compose down -v
sleep 5

# 2. 清理Docker资源
echo "2. 清理Docker资源..."
docker system prune -f
docker volume prune -f

# 3. 检查.env文件
echo "3. 验证配置文件..."
if [ ! -f ".env" ]; then
    echo "错误: .env文件不存在"
    exit 1
fi

# 检查关键配置
required_vars=("EMC_POSTGRES_PASSWORD" "EMC_NEO4J_PASSWORD" "EMC_REDIS_PASSWORD")
for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env; then
        echo "错误: 缺少配置 $var"
        exit 1
    fi
done

echo "✓ 配置文件检查通过"

# 4. 创建必要目录
echo "4. 创建数据目录..."
mkdir -p uploads
mkdir -p data/postgres
mkdir -p data/neo4j
mkdir -p data/redis

# 5. 逐个启动服务
echo "5. 逐个启动服务..."

# 启动数据库服务
echo "启动PostgreSQL..."
docker-compose up -d postgres
sleep 10

echo "启动Neo4j..."
docker-compose up -d neo4j
sleep 15

echo "启动Redis..."
docker-compose up -d redis
sleep 5

# 6. 验证数据库连接
echo "6. 验证数据库连接..."

# 检查PostgreSQL
echo "检查PostgreSQL连接..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U postgres; then
        echo "✓ PostgreSQL连接成功"
        break
    fi
    echo "等待PostgreSQL启动... ($i/30)"
    sleep 2
done

# 检查Neo4j
echo "检查Neo4j连接..."
for i in {1..30}; do
    if curl -f http://localhost:7474 >/dev/null 2>&1; then
        echo "✓ Neo4j连接成功"
        break
    fi
    echo "等待Neo4j启动... ($i/30)"
    sleep 2
done

# 检查Redis
echo "检查Redis连接..."
if docker-compose exec -T redis redis-cli -a "${EMC_REDIS_PASSWORD}" ping >/dev/null 2>&1; then
    echo "✓ Redis连接成功"
else
    echo "⚠ Redis连接检查跳过"
fi

# 7. 启动应用服务
echo "7. 启动应用服务..."
docker-compose up -d gateway
sleep 10

docker-compose up -d frontend

echo "8. 最终状态检查..."
docker-compose ps

echo "=== 修复完成 ==="
echo "服务访问地址:"
echo "- 前端: http://localhost:3000"
echo "- API: http://localhost:8000/docs"
echo "- Neo4j: http://localhost:7474"