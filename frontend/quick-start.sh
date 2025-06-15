#!/bin/bash

echo "🚀 EMC知识图谱系统快速启动"
echo "================================"

# 检查服务器状态
if curl -s -f http://localhost:5000/ > /dev/null; then
    echo "✅ 系统已在运行"
    echo "🌐 访问地址: http://localhost:5000"
    echo ""
    echo "📊 功能列表:"
    echo "  📁 文件上传 - 拖拽上传多种格式文件"
    echo "  📂 文件管理 - 查看、编辑、删除文件"
    echo "  🤖 实体提取 - AI自动提取实体关系"
    echo "  🌐 知识图谱 - 可视化展示"
    echo ""
    echo "🔧 管理命令:"
    echo "  查看日志: tail -f app.log"
    echo "  重启服务: ./quick-start.sh restart"
    echo "  停止服务: ./quick-start.sh stop"
else
    echo "🔄 启动API服务器..."
    
    # 停止旧进程
    pkill -f "api_server.py" 2>/dev/null || true
    
    # 启动新服务器
    python3 api_server.py > app.log 2>&1 &
    
    # 等待启动
    sleep 3
    
    if curl -s -f http://localhost:5000/ > /dev/null; then
        echo "✅ 启动成功！"
        echo "🌐 访问地址: http://localhost:5000"
    else
        echo "❌ 启动失败，查看日志: cat app.log"
    fi
fi