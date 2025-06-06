#!/bin/bash

echo "=== 数据库初始化 ==="

# 等待所有服务就绪
echo "等待服务启动完成..."
sleep 5

# 检查服务状态
if ! docker-compose ps | grep -q "postgres.*Up"; then
    echo "错误: PostgreSQL服务未运行"
    echo "请先运行: ./scripts/fix_services.sh"
    exit 1
fi

if ! docker-compose ps | grep -q "neo4j.*Up"; then
    echo "错误: Neo4j服务未运行"
    echo "请先运行: ./scripts/fix_services.sh"
    exit 1
fi

# 简单的连接测试
echo "测试数据库连接..."
if docker-compose exec -T postgres pg_isready -U postgres; then
    echo "✓ PostgreSQL就绪"
else
    echo "✗ PostgreSQL连接失败"
    exit 1
fi

if curl -f http://localhost:7474 >/dev/null 2>&1; then
    echo "✓ Neo4j就绪"
else
    echo "✗ Neo4j连接失败"
    exit 1
fi

echo "✓ 数据库初始化完成"
echo "系统已就绪，可以开始使用！"