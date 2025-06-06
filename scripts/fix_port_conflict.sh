#!/bin/bash

echo "=== 解决端口冲突问题 ==="

# 1. 停止冲突的Redis容器
echo "1. 停止占用端口的Redis容器..."
docker stop my-redis 2>/dev/null || echo "my-redis容器已停止"
docker rm my-redis 2>/dev/null || echo "my-redis容器已删除"

# 2. 清理所有测试容器
echo "2. 清理测试容器..."
docker stop emc_knowledge_graph-postgres-test-1 2>/dev/null
docker rm emc_knowledge_graph-postgres-test-1 2>/dev/null
docker stop emc_knowledge_graph-neo4j-test-1 2>/dev/null
docker rm emc_knowledge_graph-neo4j-test-1 2>/dev/null

# 3. 检查端口占用情况
echo "3. 检查关键端口状态..."
for port in 5432 6379 7474 7687 8000 3000; do
    if netstat -tln 2>/dev/null | grep -q ":$port "; then
        echo "⚠ 端口 $port 仍被占用"
    else
        echo "✓ 端口 $port 可用"
    fi
done

# 4. 重新启动完整服务栈
echo "4. 启动完整服务栈..."
docker-compose down -v
docker-compose up -d

echo "5. 等待服务就绪..."
sleep 15

# 6. 验证服务状态
echo "6. 验证服务状态..."
docker-compose ps

echo "=== 修复完成 ==="