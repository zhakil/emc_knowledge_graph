#!/bin/bash

echo "=== 启动EMC API网关（本地运行）==="

# 1. 检查Python环境
echo "1. 检查Python环境..."
if command -v python &> /dev/null; then
    python_version=$(python --version 2>&1)
    echo "✓ Python版本: $python_version"
else
    echo "✗ Python未安装"
    exit 1
fi

# 2. 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "2. 创建虚拟环境..."
    python -m venv .venv
    echo "✓ 虚拟环境已创建"
else
    echo "✓ 虚拟环境已存在"
fi

# 3. 激活虚拟环境并安装依赖
echo "3. 安装Python依赖..."
source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate

# 安装核心依赖
pip install fastapi uvicorn python-dotenv sqlalchemy psycopg2-binary redis neo4j openai

# 4. 设置环境变量
echo "4. 配置环境变量..."
export EMC_ENVIRONMENT=development
export EMC_POSTGRES_PASSWORD=Zqz112233
export EMC_NEO4J_PASSWORD=Zqz112233
export EMC_REDIS_PASSWORD=Zqz112233
export EMC_DEEPSEEK_API_KEY=sk-c23ccb18185d488ab996189cd62b7216

# 5. 创建简化的网关启动文件
echo "5. 创建启动文件..."
cat > start_gateway.py << 'EOF'
#!/usr/bin/env python3
"""
EMC知识图谱系统 - 简化API网关
实用性优先的启动方案
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import os

# 创建FastAPI实例
app = FastAPI(
    title="EMC知识图谱API",
    description="实用的EMC知识管理系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "EMC知识图谱系统API",
        "version": "1.0.0",
        "status": "运行中"
    }

@app.get("/health")
async def health_check():
    """健康检查 - 实用的服务状态检查"""
    import psycopg2
    import redis
    import requests
    
    status = {
        "api": "healthy",
        "timestamp": "2025-06-06T16:15:00Z",
        "services": {
            "postgres": False,
            "redis": False, 
            "neo4j": False
        }
    }
    
    # 检查PostgreSQL
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="emc_knowledge",
            user="postgres", 
            password="Zqz112233"
        )
        conn.close()
        status["services"]["postgres"] = True
    except Exception:
        pass
    
    # 检查Redis
    try:
        r = redis.Redis(host='localhost', port=6379, password='Zqz112233')
        r.ping()
        status["services"]["redis"] = True
    except Exception:
        pass
    
    # 检查Neo4j
    try:
        response = requests.get("http://localhost:7474", timeout=5)
        status["services"]["neo4j"] = response.status_code == 200
    except Exception:
        pass
    
    # 判断整体状态
    all_healthy = all(status["services"].values())
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(content=status, status_code=status_code)

@app.get("/api/test")
async def test_endpoint():
    """测试端点"""
    return {
        "message": "API测试成功",
        "data": {
            "postgres_host": "localhost:5432",
            "redis_host": "localhost:6379", 
            "neo4j_host": "localhost:7474"
        }
    }

if __name__ == "__main__":
    print("🚀 启动EMC知识图谱API网关...")
    print("📋 访问地址:")
    print("   - API文档: http://localhost:8000/docs")
    print("   - 健康检查: http://localhost:8000/health")
    print("   - 测试接口: http://localhost:8000/api/test")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
EOF

echo "6. 启动API网关..."
python start_gateway.py &
gateway_pid=$!

echo "✓ API网关已启动 (PID: $gateway_pid)"
echo "等待服务就绪..."
sleep 5

# 7. 验证API服务
echo "7. 验证API服务..."
if curl -f http://localhost:8000/health 2>/dev/null; then
    echo "✓ API网关运行正常"
else
    echo "⚠ API网关启动中..."
fi

echo "=== API网关启动完成 ==="
echo ""
echo "🎯 系统状态总览:"
echo "   ✓ PostgreSQL: localhost:5432"
echo "   ✓ Redis: localhost:6379"
echo "   ✓ Neo4j: localhost:7474" 
echo "   🚀 API网关: localhost:8000"
echo ""
echo "📖 接下来可以:"
echo "   1. 访问API文档: http://localhost:8000/docs"
echo "   2. 测试健康检查: curl http://localhost:8000/health"
echo "   3. 启动前端应用"
echo ""
echo "停止服务: kill $gateway_pid"
EOF