#!/bin/bash

echo "🚀 启动EMC知识图谱系统..."

# 创建必要目录
mkdir -p uploads scripts frontend

# 启动核心服务
echo "📋 启动核心服务 (数据库+API)..."
docker-compose up -d postgres neo4j redis gateway

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 15

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 显示访问信息
echo ""
echo "✅ 系统启动完成！"
echo ""
echo "📋 访问地址："
echo "   🌐 API文档:     http://localhost:8000/docs"
echo "   🔍 健康检查:    http://localhost:8000/health"
echo "   🧪 测试接口:    http://localhost:8000/api/test"
echo "   💾 Neo4j浏览器: http://localhost:7474 (neo4j/Zqz112233)"
echo ""
echo "🛠️ 管理命令："
echo "   查看日志: docker-compose logs -f gateway"
echo "   停止系统: docker-compose down"
echo "   重启系统: docker-compose restart"
echo ""

# 可选：启动前端开发服务器
read -p "是否启动前端开发服务器? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌐 启动前端开发服务器..."
    docker-compose --profile frontend up -d frontend-dev
    echo "   前端地址: http://localhost:3000"
fi