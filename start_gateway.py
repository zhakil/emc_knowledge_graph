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
