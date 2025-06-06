#!/bin/bash

echo "检查环境配置..."

# 检查 Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js 已安装: $(node --version)"
else
    echo "❌ Node.js 未安装"
fi

# 检查 npm
if command -v npm &> /dev/null; then
    echo "✅ npm 已安装: $(npm --version)"
else
    echo "❌ npm 未安装"
fi

# 检查 Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker 已安装: $(docker --version)"
    
    # 检查 Docker 服务
    if docker info &> /dev/null; then
        echo "✅ Docker 服务正在运行"
    else
        echo "❌ Docker 服务未运行，请启动 Docker Desktop"
    fi
else
    echo "❌ Docker 未安装"
fi

# 检查 .env 文件
if [ -f ".env" ]; then
    echo "✅ .env 文件存在"
else
    echo "❌ .env 文件不存在"
fi

# 检查目录结构
dirs=("frontend" "gateway" "services")
for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir 目录存在"
    else
        echo "❌ $dir 目录不存在"
    fi
done

# 在运行测试前添加文件存在检查
if [ ! -f "docker-compose.test.yml" ]; then
    echo "❌ docker-compose.test.yml 文件不存在，请先创建"
    exit 1
fi

# === FIXED TEST STARTUP ===
echo "启动测试数据库..."
docker compose -f docker-compose.test.yml up -d

echo "等待数据库初始化..."
sleep 10  # 增加等待时间

echo "运行测试..."
# 设置 Qt 绑定环境变量
export PYTEST_QT_API=pyqt5
python -m pytest tests/ --cov=services --cov-report=term
# === END FIX ===

# 3. 查看实时服务日志
docker-compose logs -f

# 运行知识图谱单元测试
pytest tests/unit/test_kg_service.py -v

# 测试API端点
pytest tests/api/test_api.py

# 示例输出
# test_create_standard (tests.unit.test_kg_service) ... OK
# test_link_standards (tests.unit.test_kg_service) ... OK
# test_health_check (tests.api.test_api) ... OK
# test_standard_search (tests.api.test_api) ... OK

# 启动前端
cd frontend
npm run dev

# 新终端运行测试
npm run test:e2e

# 示例输出
✔ 标准搜索功能: 成功搜索EMC标准 (1m23s)
