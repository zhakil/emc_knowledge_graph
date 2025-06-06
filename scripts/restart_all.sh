#!/bin/bash

echo "=== EMC系统完全重启 ==="

# 1. 彻底停止所有相关服务
echo "1. 停止所有Docker服务..."
docker-compose down -v --remove-orphans
docker stop $(docker ps -aq) 2>/dev/null || echo "没有运行的容器"

# 2. 清理资源
echo "2. 清理Docker资源..."
docker system prune -f
docker volume prune -f

# 3. 验证端口完全清空
echo "3. 验证端口状态..."
for port in 3000 5432 6379 7474 7687 8000; do
    if netstat -tln 2>/dev/null | grep -q ":$port "; then
        echo "⚠ 端口 $port 仍被占用"
        # 在Windows上找到并终止占用进程
        netstat -ano 2>/dev/null | grep ":$port " | head -1
    else
        echo "✓ 端口 $port 已清空"
    fi
done

# 4. 确保必要目录存在
echo "4. 创建必要目录..."
mkdir -p uploads data/postgres data/neo4j data/redis

# 5. 启动基础数据库服务
echo "5. 启动数据库服务..."
echo "启动 PostgreSQL..."
docker-compose up -d postgres
sleep 8

echo "启动 Neo4j..."
docker-compose up -d neo4j  
sleep 12

echo "启动 Redis..."
docker-compose up -d redis
sleep 5

# 6. 验证数据库启动
echo "6. 验证数据库连接..."
timeout=30
counter=0

# 等待PostgreSQL
while [ $counter -lt $timeout ]; do
    if docker-compose exec -T postgres pg_isready -U postgres 2>/dev/null; then
        echo "✓ PostgreSQL 就绪"
        break
    fi
    echo "等待PostgreSQL... ($counter/$timeout)"
    sleep 2
    ((counter++))
done

# 等待Neo4j
counter=0
while [ $counter -lt $timeout ]; do
    if curl -f http://localhost:7474 2>/dev/null; then
        echo "✓ Neo4j 就绪"
        break
    fi
    echo "等待Neo4j... ($counter/$timeout)" 
    sleep 2
    ((counter++))
done

# 7. 启动应用服务
echo "7. 启动应用服务..."
docker-compose up -d gateway
sleep 8

docker-compose up -d frontend
sleep 5

# 8. 最终状态检查
echo "8. 服务状态检查..."
docker-compose ps

echo "9. 连接测试..."
services=(
    "PostgreSQL:5432"
    "Redis:6379" 
    "Neo4j:7474"
    "Gateway:8000"
    "Frontend:3000"
)

for service_port in "${services[@]}"; do
    service=${service_port%:*}
    port=${service_port#*:}
    
    if netstat -tln 2>/dev/null | grep -q ":$port "; then
        echo "✓ $service (端口 $port): 运行中"
    else
        echo "✗ $service (端口 $port): 未运行"
    fi
done

echo "=== 重启完成 ==="
echo ""
echo "访问地址:"
echo "- 前端应用: http://localhost:3000"
echo "- API文档: http://localhost:8000/docs"  
echo "- Neo4j浏览器: http://localhost:7474"
echo ""
echo "如果服务仍有问题，请检查Docker容器日志:"
echo "docker-compose logs [service_name]"