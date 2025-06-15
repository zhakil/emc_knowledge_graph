#!/bin/bash

# EMC知识图谱系统 - 手动Docker启动脚本

echo "🚀 手动启动EMC知识图谱系统Docker容器..."

# 检查Docker是否可用
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装或未在WSL中启用"
    echo "请确保:"
    echo "1. 已安装Docker Desktop"
    echo "2. 在Docker Desktop设置中启用WSL集成"
    echo "3. 重启WSL: wsl --shutdown"
    exit 1
fi

# 构建镜像
echo "🔨 构建Docker镜像..."
docker build -f Dockerfile.app -t emc-knowledge-graph:latest .

# 停止现有容器
echo "🛑 停止现有容器..."
docker stop emc-kg-system 2>/dev/null || true
docker rm emc-kg-system 2>/dev/null || true

# 启动新容器
echo "▶️ 启动新容器..."
docker run -d \
  --name emc-kg-system \
  -p 5000:5000 \
  -v "$(pwd)/uploads:/app/uploads" \
  -v "$(pwd)/files_db.json:/app/files_db.json" \
  --restart unless-stopped \
  emc-knowledge-graph:latest

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查容器状态
echo "🔍 检查容器状态..."
docker ps | grep emc-kg-system

# 测试服务连接
echo "🌐 测试服务连接..."
if curl -s -f http://localhost:5000/ > /dev/null; then
    echo "✅ EMC知识图谱系统启动成功！"
    echo "🌐 访问地址: http://localhost:5000"
    echo ""
    echo "🔧 管理命令:"
    echo "  查看日志: docker logs -f emc-kg-system"
    echo "  停止容器: docker stop emc-kg-system"
    echo "  重启容器: docker restart emc-kg-system"
    echo "  删除容器: docker rm -f emc-kg-system"
else
    echo "❌ 服务启动失败，查看日志:"
    docker logs emc-kg-system
fi