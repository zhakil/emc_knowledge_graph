#!/bin/bash

# EMC知识图谱系统 - 本地API网关启动脚本
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}🚀 启动EMC知识图谱API网关...${NC}"

# 获取脚本所在目录的父目录作为项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}📁 项目根目录: $PROJECT_ROOT${NC}"

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python未安装，请先安装Python 3.8+${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python已安装: $(python --version)${NC}"

# 设置Python路径
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"
echo -e "${BLUE}📦 PYTHONPATH: $PYTHONPATH${NC}"

# 检查并安装最小依赖
echo -e "${YELLOW}📦 安装必要依赖...${NC}"
pip install -q fastapi==0.104.1 uvicorn[standard]==0.24.0 python-multipart==0.0.6 aiofiles==23.2.1 pydantic==2.5.0 python-dotenv==1.0.0

# 创建gateway目录（如果不存在）
mkdir -p gateway

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env文件不存在，创建默认配置${NC}"
    cat > .env << 'EOF'
EMC_ENVIRONMENT=development
EMC_SECRET_KEY=dev-secret-key-for-local-development-32chars
EMC_DEEPSEEK_API_KEY=sk-placeholder-key
EMC_DEBUG=true
EMC_HOST=0.0.0.0
EMC_PORT=8000
EOF
fi

# 创建uploads目录
mkdir -p uploads

# 启动API网关
echo -e "${GREEN}🚀 启动API网关服务...${NC}"
echo -e "${BLUE}📍 工作目录: $(pwd)${NC}"
echo -e "${BLUE}📍 网关模块: gateway.main:app${NC}"

# 使用nohup在后台启动服务
nohup python -m uvicorn gateway.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info \
    --access-log > gateway.log 2>&1 &

GATEWAY_PID=$!
echo -e "${GREEN}✓ API网关已启动 (PID: $GATEWAY_PID)${NC}"

# 等待服务启动
echo -e "${YELLOW}等待服务就绪...${NC}"
sleep 3

# 验证服务
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✓ API网关服务就绪${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ API网关启动超时${NC}"
        cat gateway.log
        exit 1
    fi
    sleep 1
done

echo -e "${GREEN}🎯 EMC知识图谱系统启动完成${NC}"
echo -e "${GREEN}📋 访问地址:${NC}"
echo -e "   - API文档: ${BLUE}http://localhost:8000/docs${NC}"
echo -e "   - 健康检查: ${BLUE}http://localhost:8000/health${NC}"
echo -e "   - 测试接口: ${BLUE}http://localhost:8000/api/test${NC}"
echo ""
echo -e "${YELLOW}💡 停止服务: kill $GATEWAY_PID${NC}"
echo -e "${YELLOW}📋 查看日志: tail -f gateway.log${NC}"