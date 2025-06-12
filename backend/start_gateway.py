#!/usr/bin/env python3
"""
EMC知识图谱系统 - 高效API网关
实用主义设计，专注核心功能
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI实例
app = FastAPI(
    title="EMC知识图谱API",
    description="实用的EMC知识管理系统",
    version="1.0.0"
)

# 配置CORS - 实用的跨域设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """系统根路径 - 快速状态概览"""
    return {
        "system": "EMC知识图谱系统",
        "version": "1.0.0",
        "status": "运行中",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "health": "/health", 
            "test": "/api/test"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查 - 实际数据库连接验证"""
    status = {
        "api": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {}
    }
    
    # PostgreSQL连接检查
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost", port=5432, database="emc_knowledge",
            user="postgres", password="Zqz112233", connect_timeout=3
        )
        conn.close()
        status["services"]["postgres"] = {"status": "connected", "port": 5432}
        logger.info("✅ PostgreSQL连接成功")
    except Exception as e:
        status["services"]["postgres"] = {"status": "failed", "error": str(e)}
        logger.warning(f"❌ PostgreSQL连接失败: {e}")
    
    # Redis连接检查
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, password='Zqz112233', socket_timeout=3)
        r.ping()
        status["services"]["redis"] = {"status": "connected", "port": 6379}
        logger.info("✅ Redis连接成功")
    except Exception as e:
        status["services"]["redis"] = {"status": "failed", "error": str(e)}
        logger.warning(f"❌ Redis连接失败: {e}")
    
    # Neo4j连接检查
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Zqz112233"))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            result.single()
        driver.close()
        status["services"]["neo4j"] = {"status": "connected", "port": 7687}
        logger.info("✅ Neo4j连接成功")
    except Exception as e:
        status["services"]["neo4j"] = {"status": "failed", "error": str(e)}
        logger.warning(f"❌ Neo4j连接失败: {e}")
    
    # DeepSeek API检查
    deepseek_key = "sk-c23ccb18185d488ab996189cd62b7216"
    if deepseek_key and deepseek_key.startswith("sk-"):
        status["services"]["deepseek"] = {"status": "configured"}
        logger.info("✅ DeepSeek API已配置")
    else:
        status["services"]["deepseek"] = {"status": "not_configured"}
        logger.warning("❌ DeepSeek API未配置")
    
    # 计算整体健康状态
    healthy_services = sum(1 for svc in status["services"].values() 
                          if svc.get("status") in ["connected", "configured"])
    total_services = len(status["services"])
    
    status["summary"] = {
        "healthy_services": healthy_services,
        "total_services": total_services,
        "health_percentage": round((healthy_services / total_services) * 100, 1)
    }
    
    # 根据健康状态返回HTTP状态码
    http_status = 200 if healthy_services >= 3 else 503
    return JSONResponse(content=status, status_code=http_status)

@app.get("/api/test")
async def test_endpoint():
    """API测试端点 - 快速验证"""
    return {
        "message": "API测试成功",
        "timestamp": datetime.now().isoformat(),
        "test_data": {
            "system": "EMC知识图谱",
            "database_hosts": {
                "postgres": "localhost:5432",
                "redis": "localhost:6379", 
                "neo4j": "localhost:7687"
            },
            "api_status": "operational"
        }
    }

@app.get("/api/status")
async def system_status():
    """系统状态概览 - 实用的监控信息"""
    return {
        "system": "EMC知识图谱系统",
        "uptime": "运行中",
        "version": "1.0.0",
        "environment": "development",
        "features": [
            "AI文档分析 (DeepSeek)",
            "知识图谱构建 (Neo4j)",
            "数据存储 (PostgreSQL)",
            "缓存服务 (Redis)"
        ],
        "endpoints_count": len(app.routes),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 启动EMC知识图谱API网关...")
    print("📋 核心访问地址:")
    print("   - API文档: http://localhost:8000/docs")
    print("   - 系统健康: http://localhost:8000/health")
    print("   - 快速测试: http://localhost:8000/api/test")
    print("   - 状态概览: http://localhost:8000/api/status")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )