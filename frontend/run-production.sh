#!/bin/bash

echo "🚀 启动EMC知识图谱完整生产版本"
echo "=================================="

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装"
    exit 1
fi

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose -f docker-production.yml down 2>/dev/null || true

# 构建并启动生产版本
echo "🔨 构建生产版本..."
docker-compose -f docker-production.yml build --no-cache

echo "🚀 启动生产服务..."
docker-compose -f docker-production.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "✅ 检查服务状态..."
docker-compose -f docker-production.yml ps

echo ""
echo "🎉 EMC知识图谱生产版本已启动！"
echo "=================================="
echo "📱 前端应用: http://localhost:3000"
echo "🔧 后端API: http://localhost:8001"
echo ""
echo "🔍 查看日志:"
echo "   docker-compose -f docker-production.yml logs -f"
echo ""
echo "🛑 停止服务:"
echo "   docker-compose -f docker-production.yml down"