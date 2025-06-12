#!/bin/bash

echo "🚀 启动EMC知识图谱前端应用 (后台模式)..."

# 进入前端目录
cd /mnt/host/e/emc_knowledge_graph/frontend

# 检查是否有正在运行的React服务
PID=$(ps aux | grep 'react-scripts start' | grep -v grep | awk '{print $2}')
if [ ! -z "$PID" ]; then
    echo "⚠️  检测到已有React服务运行 (PID: $PID)"
    echo "🔄 正在重启服务..."
    kill $PID
    sleep 2
fi

# 设置环境变量
export GENERATE_SOURCEMAP=false
export REACT_APP_API_BASE_URL=http://localhost:8000
export PORT=3000

echo "📦 检查依赖..."
if [ ! -d "node_modules" ] || [ ! -f "node_modules/.package-lock.json" ]; then
    echo "📥 安装依赖包..."
    npm install --silent
fi

echo "🌐 启动前端开发服务器..."
echo "📍 访问地址: http://localhost:3000"
echo "📍 API代理: http://localhost:8000"
echo ""

# 后台启动
nohup npm start > frontend.log 2>&1 &
PID=$!

echo "✅ 前端服务已启动"
echo "📋 进程ID: $PID"
echo "📄 日志文件: frontend.log"
echo ""
echo "💡 使用以下命令查看状态:"
echo "   tail -f frontend.log     # 查看日志"
echo "   ps aux | grep react      # 查看进程"
echo "   kill $PID               # 停止服务"
echo ""

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
if ps -p $PID > /dev/null; then
    echo "🎉 前端服务启动成功！"
    echo "🔗 请在浏览器中访问: http://localhost:3000"
else
    echo "❌ 前端服务启动失败，请查看日志:"
    echo "   tail frontend.log"
fi