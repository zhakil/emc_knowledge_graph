#!/bin/bash

echo "=== 启动EMC数据库服务（仅数据库）==="

# 停止现有服务
docker-compose down -v

# 直接拉取国内镜像
echo "1. 拉取数据库镜像..."
docker pull registry.cn-hangzhou.aliyuncs.com/library/postgres:15-alpine
docker pull registry.cn-hangzhou.aliyuncs.com/library/neo4j:5.15-community  
docker pull registry.cn-hangzhou.aliyuncs.com/library/redis:7-alpine

# 重新标记为原始名称
docker tag registry.cn-hangzhou.aliyuncs.com/library/postgres:15-alpine postgres:15-alpine
docker tag registry.cn-hangzhou.aliyuncs.com/library/neo4j:5.15-community neo4j:5.15-community
docker tag registry.cn-hangzhou.aliyuncs.com/library/redis:7-alpine redis:7-alpine

echo "2. 启动数据库服务..."
# 使用国内compose文件启动
docker-compose -f docker-compose-cn.yml up -d

echo "3. 等待服务就绪..."
sleep 15

# 验证服务
echo "4. 验证服务状态..."
docker-compose -f docker-compose-cn.yml ps

echo "5. 连接测试..."
for i in {1..10}; do
    echo "尝试连接数据库... ($i/10)"
    
    # 测试PostgreSQL
    if docker exec emc_postgres pg_isready -U postgres 2>/dev/null; then
        echo "✓ PostgreSQL 连接成功"
        break
    fi
    sleep 3
done

# 测试Neo4j
for i in {1..10}; do
    if curl -f http://localhost:7474 2>/dev/null; then
        echo "✓ Neo4j 连接成功"
        break
    fi
    echo "等待Neo4j启动... ($i/10)"
    sleep 3
done

echo "=== 数据库服务启动完成 ==="
echo "可以访问："
echo "- Neo4j浏览器: http://localhost:7474 (neo4j/Zqz112233)"
echo "- PostgreSQL: localhost:5432 (postgres/Zqz112233)"
echo "- Redis: localhost:6379 (密码: Zqz112233)"