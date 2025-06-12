#!/bin/bash
# EMC知识图谱前端修复脚本
# 专注解决实际启动问题

set -e

echo "🔧 EMC前端诊断修复开始"
echo "=========================="

# 检查环境
check_environment() {
    echo "📋 环境检查..."
    
    # 检查Node.js版本
    if command -v node >/dev/null 2>&1; then
        NODE_VERSION=$(node --version)
        echo "✅ Node.js: $NODE_VERSION"
    else
        echo "❌ Node.js未安装"
        exit 1
    fi
    
    # 检查npm版本
    if command -v npm >/dev/null 2>&1; then
        NPM_VERSION=$(npm --version)
        echo "✅ npm: $NPM_VERSION"
    else
        echo "❌ npm未安装"
        exit 1
    fi
    
    # 检查前端目录
    if [ -d "frontend" ]; then
        echo "✅ frontend目录存在"
        cd frontend
    else
        echo "❌ frontend目录不存在"
        exit 1
    fi
}

# 修复package.json
fix_package_json() {
    echo "📝 修复package.json..."
    
    # 备份原文件
    cp package.json package.json.backup
    
    # 创建修复后的package.json
    cat > package.json << 'EOF'
{
  "name": "emc-knowledge-graph-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.16.4",
    "@testing-library/react": "^13.3.0",
    "@testing-library/user-event": "^13.5.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "react-router-dom": "^6.3.0",
    "axios": "^1.4.0",
    "antd": "^5.6.0",
    "@ant-design/icons": "^5.1.0",
    "d3": "^7.8.0",
    "vis-network": "^9.1.0",
    "web-vitals": "^2.1.4"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "proxy": "http://localhost:8000"
}
EOF

    echo "✅ package.json已修复"
}

# 清理和重装依赖
reinstall_dependencies() {
    echo "🧹 清理依赖..."
    
    # 删除node_modules和package-lock.json
    rm -rf node_modules package-lock.json
    
    # 清理npm缓存
    npm cache clean --force
    
    echo "📦 重新安装依赖..."
    npm install --legacy-peer-deps
    
    echo "✅ 依赖安装完成"
}

# 检查端口占用
check_port() {
    echo "🔍 检查端口3000..."
    
    if lsof -i :3000 >/dev/null 2>&1; then
        echo "⚠️  端口3000被占用，尝试释放..."
        lsof -ti :3000 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    echo "✅ 端口3000可用"
}

# 启动开发服务器
start_development_server() {
    echo "🚀 启动开发服务器..."
    
    # 设置环境变量
    export BROWSER=none
    export PORT=3000
    export REACT_APP_API_URL=http://localhost:8000
    
    # 启动服务器
    echo "⏳ 正在启动React开发服务器..."
    npm start &
    
    # 等待服务器启动
    SERVER_PID=$!
    echo "📋 服务器PID: $SERVER_PID"
    
    # 等待端口开放
    for i in {1..30}; do
        if curl -s http://localhost:3000 >/dev/null 2>&1; then
            echo "✅ 前端服务器启动成功! http://localhost:3000"
            return 0
        fi
        echo "⏳ 等待服务器启动... ($i/30)"
        sleep 2
    done
    
    echo "❌ 服务器启动超时"
    kill $SERVER_PID 2>/dev/null || true
    return 1
}

# 验证服务连接
verify_services() {
    echo "🔍 验证服务连接..."
    
    # 检查后端服务
    BACKEND_SERVICES=(
        "http://localhost:8000:API网关"
        "http://localhost:7474:Neo4j"
        "http://localhost:5432:PostgreSQL"
        "http://localhost:6379:Redis"
    )
    
    for service in "${BACKEND_SERVICES[@]}"; do
        url=$(echo $service | cut -d: -f1-2)
        name=$(echo $service | cut -d: -f3)
        
        if curl -s --connect-timeout 5 $url >/dev/null 2>&1; then
            echo "✅ $name: 可访问"
        else
            echo "⚠️  $name: 无法访问 ($url)"
        fi
    done
}

# 创建启动脚本
create_start_script() {
    cat > start_frontend.sh << 'EOF'
#!/bin/bash
cd frontend
export BROWSER=none
export PORT=3000  
export REACT_APP_API_URL=http://localhost:8000
npm start
EOF
    
    chmod +x start_frontend.sh
    echo "✅ 创建启动脚本: start_frontend.sh"
}

# 主执行流程
main() {
    check_environment
    fix_package_json
    reinstall_dependencies
    check_port
    verify_services
    create_start_script
    
    echo ""
    echo "🎯 手动启动前端:"
    echo "cd frontend && npm start"
    echo ""
    echo "🌐 预期访问地址:"
    echo "前端: http://localhost:3000"
    echo "后端: http://localhost:8000"
    echo "Neo4j: http://localhost:7474"
    
    # 尝试自动启动
    if start_development_server; then
        echo ""
        echo "🎉 EMC知识图谱前端启动成功!"
        echo "🌐 访问地址: http://localhost:3000"
    else
        echo ""
        echo "⚠️  自动启动失败，请手动执行:"
        echo "cd frontend && npm start"
    fi
}

# 错误处理
trap 'echo "❌ 脚本执行失败"; exit 1' ERR

# 执行主流程
main "$@"