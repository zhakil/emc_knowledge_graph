#!/bin/bash

# EMC知识图谱前端启动脚本
echo "🚀 启动EMC知识图谱前端应用..."

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装，请先安装Node.js"
    exit 1
fi

# 检查npm是否安装
if ! command -v npm &> /dev/null; then
    echo "❌ npm未安装，请先安装npm"
    exit 1
fi

echo "✅ Node.js版本: $(node --version)"
echo "✅ npm版本: $(npm --version)"

# 进入前端目录
cd frontend

# 检查是否存在node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖包..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi

# 设置环境变量
export GENERATE_SOURCEMAP=false
export REACT_APP_API_BASE_URL=http://localhost:8000

# 启动开发服务器
echo "🌐 启动前端开发服务器..."
echo "📍 访问地址: http://localhost:3000"
echo "📍 API地址: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

npm start