#!/bin/bash

echo "🐳 EMC知识图谱 Docker构建环境"
echo "================================"

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

echo "📦 构建Docker镜像..."
docker build -f Dockerfile.desktop -t emc-knowledge-graph-builder .

if [ $? -eq 0 ]; then
    echo "✅ Docker镜像构建成功"
    
    echo "🚀 在Docker容器中构建Windows桌面客户端..."
    docker run --rm -v "$(pwd)/dist:/app/dist" emc-knowledge-graph-builder
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 构建完成！"
        echo "📁 构建文件位置: $(pwd)/dist/"
        echo ""
        echo "生成的文件:"
        ls -la dist/ 2>/dev/null || echo "dist目录为空，请检查构建过程"
        echo ""
        echo "📦 安装包文件:"
        echo "   - EMC知识图谱系统-1.0.0-x64.exe (Windows安装程序)"
        echo "   - EMC知识图谱系统-1.0.0-portable.exe (便携版)"
        echo "   - latest.yml (自动更新配置)"
    else
        echo "❌ Docker容器构建失败"
        exit 1
    fi
else
    echo "❌ Docker镜像构建失败"
    exit 1
fi