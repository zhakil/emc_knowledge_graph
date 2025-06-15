#!/bin/bash

# EMC知识图谱系统 - Docker启动脚本

echo "🚀 启动EMC知识图谱系统Docker容器..."

# 停止并删除现有容器
echo "🛑 停止现有容器..."
docker-compose -f docker-compose.app.yml down

# 构建并启动新容器
echo "🔨 构建Docker镜像..."
docker-compose -f docker-compose.app.yml build

echo "▶️ 启动容器..."
docker-compose -f docker-compose.app.yml up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose -f docker-compose.app.yml ps

# 测试服务连接
echo "🌐 测试服务连接..."
if curl -s -f http://localhost:5000/ > /dev/null; then
    echo "✅ EMC知识图谱系统启动成功！"
    echo "🌐 访问地址: http://localhost:5000"
    echo "📊 功能列表:"
    echo "  📁 文件上传 - 拖拽或选择多文件上传"
    echo "  📂 文件管理 - Obsidian风格管理界面"
    echo "  ✏️ 文件编辑 - 在线编辑TXT/MD文件"
    echo "  🗑️ 文件删除 - 单个和批量删除"
    echo "  🤖 实体提取 - KAG-DeepSeek AI引擎"
    echo "  🌐 知识图谱 - 交互式可视化展示"
    echo ""
    echo "📝 查看日志: docker-compose -f docker-compose.app.yml logs -f"
    echo "🛑 停止服务: docker-compose -f docker-compose.app.yml down"
else
    echo "❌ 服务启动失败，请检查日志:"
    docker-compose -f docker-compose.app.yml logs
fi