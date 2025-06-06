#!/bin/bash

echo "=== EMC服务状态诊断 ==="

# 检查Docker Compose服务状态
echo "1. 检查Docker Compose服务状态:"
docker-compose ps

echo -e "\n2. 检查Docker容器状态:"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n3. 检查服务日志:"
services=("postgres" "neo4j" "redis" "gateway")

for service in "${services[@]}"; do
    echo "=== $service 日志 ==="
    docker-compose logs --tail=10 "$service" 2>/dev/null || echo "服务 $service 不存在或未启动"
    echo ""
done

echo "4. 检查端口占用:"
netstat -tlnp 2>/dev/null | grep -E ":5432|:7474|:7687|:6379|:8000" || echo "netstat不可用，跳过端口检查"

echo -e "\n5. 磁盘空间检查:"
df -h | head -2

echo -e "\n6. Docker资源使用:"
docker system df