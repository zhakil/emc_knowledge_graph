#!/bin/bash

echo "🚀 EMC知识图谱 快速构建脚本"
echo "================================"

# 检查当前目录
if [ ! -f "package.json" ]; then
    echo "❌ 请在frontend目录中运行此脚本"
    exit 1
fi

# 创建dist目录
mkdir -p dist

echo "📦 生成演示安装包文件..."

# 创建模拟的安装包文件
cat > dist/EMC知识图谱系统-1.0.0-x64.exe << 'EOF'
#!/bin/bash
echo "这是EMC知识图谱系统Windows安装程序的占位文件"
echo "实际的exe文件需要在Windows环境中使用以下命令构建："
echo ""
echo "npm install --legacy-peer-deps"
echo "npm run build"
echo "npm run dist"
echo ""
echo "或使用Docker:"
echo "docker-build-windows.bat"
EOF

cat > dist/EMC知识图谱系统-1.0.0-portable.exe << 'EOF'
#!/bin/bash
echo "这是EMC知识图谱系统Windows便携版的占位文件"
echo "实际的exe文件需要在Windows环境中构建"
EOF

cat > dist/latest.yml << 'EOF'
version: 1.0.0
files:
  - url: EMC知识图谱系统-1.0.0-x64.exe
    sha512: placeholder-hash
    size: 157286400
  - url: EMC知识图谱系统-1.0.0-portable.exe  
    sha512: placeholder-hash
    size: 157286400
path: EMC知识图谱系统-1.0.0-x64.exe
sha512: placeholder-hash
releaseDate: '2025-06-15T09:00:00.000Z'
EOF

# 设置文件权限
chmod +x dist/*.exe 2>/dev/null || true

echo "✅ 演示文件已生成到 dist/ 目录"
echo ""
echo "📁 dist/ 目录内容:"
ls -la dist/
echo ""
echo "📋 要获得真实的Windows安装包，请："
echo "   1. 在Windows环境中运行: docker-build-windows.bat"
echo "   2. 或手动执行: npm install && npm run build && npm run dist"
echo ""
echo "🎯 所有配置已完成，仅需在支持Electron构建的环境中执行"