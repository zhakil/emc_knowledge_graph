#!/bin/bash

echo "🚀 构建EMC知识图谱Windows桌面应用程序..."

# 检查Node.js和npm
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装，请先安装Node.js"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm未安装，请先安装npm"
    exit 1
fi

# 清理旧的构建文件
echo "🧹 清理旧的构建文件..."
rm -rf dist/ build/

# 安装依赖
echo "📦 安装依赖包..."
npm install

# 构建React应用
echo "🔨 构建React前端应用..."
npm run build

# 检查构建是否成功
if [ ! -d "build" ]; then
    echo "❌ React应用构建失败"
    exit 1
fi

# 构建Electron应用
echo "🖥️ 构建Electron桌面应用..."
npm run dist

# 检查输出
if [ -d "dist" ]; then
    echo "✅ 构建成功！"
    echo ""
    echo "📁 输出文件位置: ./dist/"
    echo "🔍 生成的文件:"
    
    # 列出所有exe文件
    find dist/ -name "*.exe" -exec echo "  📦 {}" \;
    
    echo ""
    echo "🎉 EMC知识图谱桌面应用程序已生成完成！"
    echo "💾 安装包: EMC知识图谱系统-1.0.0-x64.exe"
    echo "🎒 便携版: EMC知识图谱系统-1.0.0-portable.exe"
    echo ""
    echo "📋 使用说明:"
    echo "1. 双击.exe文件安装或运行"
    echo "2. 支持系统托盘最小化"
    echo "3. 快捷键 Ctrl+Shift+E 显示/隐藏窗口"
    echo "4. 内置完整API服务器，无需额外配置"
    echo ""
    echo "📚 详细文档: docs/WINDOWS_APP_GUIDE.md"
    
else
    echo "❌ 构建失败，请检查错误信息"
    exit 1
fi