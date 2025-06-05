#!/bin/bash
# EMC知识图谱项目初始化脚本

set -e

echo "🚀 开始项目初始化..."

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
alembic upgrade head

# 前端依赖安装
cd frontend
npm install
cd ..

echo "✅ 初始化完成！使用命令启动:"
echo "  后端: uvicorn gateway.main:app --reload"
echo "  前端: cd frontend && npm run dev" 