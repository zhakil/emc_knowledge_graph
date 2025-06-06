#!/bin/bash

echo "=== 快速服务检查 ==="

# 检查Docker Compose服务
echo "1. Docker Compose服务:"
docker-compose ps --format "table {{.Service}}\t{{.State}}\t{{.Ports}}"

# 检查独立容器
echo -e "\n2. 独立运行的容器:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -v NAMES

# 检查关键端口
echo -e "\n3. 端口检查:"
services=("PostgreSQL:5432" "Redis:6379" "Neo4j-HTTP:7474" "Neo4j-Bolt:7687" "Gateway:8000" "Frontend:3000")
for service_port in "${services[@]}"; do
    service=${service_port%:*}
    port=${service_port#*:}
    if netstat -tln 2>/dev/null | grep -q ":$port "; then
        echo "✓ $service (端口 $port): 运行中"
    else
        echo "✗ $service (端口 $port): 未运行"
    fi
done

# 简单连接测试
echo -e "\n4. 连接测试:"
if curl -f http://localhost:7474 >/dev/null 2>&1; then
    echo "✓ Neo4j Web界面可访问"
else
    echo "✗ Neo4j Web界面不可访问"
fi

if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✓ Gateway健康检查通过"
else
    echo "✗ Gateway健康检查失败"
fi

echo -e "\n=== 检查完成 ==="