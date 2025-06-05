"""
EMC知识图谱系统 - API网关主服务
提供统一的API入口点，整合DeepSeek AI、Neo4j图数据库和文件处理服务
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Security, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

# 自定义中间件
from .middleware.auth import AuthMiddleware, get_current_user
from .middleware.rate_limiting import RateLimitMiddleware
from .middleware.logging import LoggingMiddleware
from .middleware.error_handling import ErrorHandlingMiddleware

# 路由模块
from .routes.deepseek_routes import router as deepseek_router
from .routes.graph_routes import router as graph_router
from .routes.file_routes import router as file_router
from .routes.websocket_routes import router as websocket_router
from .routes.analysis_routes import router as analysis_router

# 服务依赖
from services.ai_integration.deepseek_service import create_deepseek_service, DeepSeekConfig
from services.knowledge_graph.neo4j_emc_service import create_emc_knowledge_service
from services.file_processing.emc_file_processor import create_emc_file_processor

# 配置管理
from .config import Settings, get_settings

# 数据库连接
from data_access.connections.database_connection import db_connection
from data_access.connections.redis_connection import redis_conn


class ServiceContainer:
    """服务容器 - 管理所有服务实例"""
    
    def __init__(self):
        self.deepseek_service = None
        self.neo4j_service = None
        self.file_processor = None
        self.settings = None
        
    async def initialize(self, settings: Settings):
        """初始化所有服务"""
        self.settings = settings
        
        # 初始化DeepSeek服务
        deepseek_config = DeepSeekConfig(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            model=settings.deepseek_model,
            max_tokens=settings.deepseek_max_tokens,
            temperature=settings.deepseek_temperature
        )
        self.deepseek_service = create_deepseek_service(deepseek_config)
        
        # 初始化Neo4j服务
        self.neo4j_service = await create_emc_knowledge_service(
            uri=settings.neo4j_uri,
            username=settings.neo4j_username,
            password=settings.neo4j_password
        )
        
        # 初始化文件处理服务
        self.file_processor = create_emc_file_processor(
            deepseek_service=self.deepseek_service,
            storage_path=settings.upload_directory
        )
        
        # 初始化数据库连接
        db_connection.initialize_sync()
        db_connection.initialize_async()
        
        # 初始化Redis连接
        redis_conn.initialize_sync()
        redis_conn.initialize_async()
        
        logging.info("所有服务初始化完成")
    
    async def cleanup(self):
        """清理资源"""
        if self.neo4j_service:
            await self.neo4j_service.close()
        
        db_connection.close()
        redis_conn.close()
        
        logging.info("服务清理完成")

# 全局服务容器
service_container = ServiceContainer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    settings = get_settings()
    await service_container.initialize(settings)
    
    # 设置日志级别
    log_level = getattr(logging, settings.log_level.upper())
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    yield
    
    # 关闭时清理
    await service_container.cleanup()


def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    settings = get_settings()
    
    app = FastAPI(
        title="EMC知识图谱系统",
        description="集成DeepSeek AI和Neo4j的EMC领域知识图谱平台",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 添加Gzip压缩
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # 添加自定义中间件
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(AuthMiddleware)
    
    # 配置Prometheus监控
    if settings.enable_metrics:
        instrumentator = Instrumentator()
        instrumentator.instrument(app).expose(app)
    
    # 静态文件服务
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # 注册路由
    app.include_router(deepseek_router, prefix="/api/deepseek", tags=["DeepSeek AI"])
    app.include_router(graph_router, prefix="/api/graph", tags=["知识图谱"])
    app.include_router(file_router, prefix="/api/files", tags=["文件处理"])
    app.include_router(analysis_router, prefix="/api/analysis", tags=["数据分析"])
    app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])
    
    return app


app = create_app()


# 依赖注入函数
def get_deepseek_service():
    """获取DeepSeek服务实例"""
    if not service_container.deepseek_service:
        raise HTTPException(status_code=500, detail="DeepSeek服务未初始化")
    return service_container.deepseek_service


def get_neo4j_service():
    """获取Neo4j服务实例"""
    if not service_container.neo4j_service:
        raise HTTPException(status_code=500, detail="Neo4j服务未初始化")
    return service_container.neo4j_service


def get_file_processor():
    """获取文件处理服务实例"""
    if not service_container.file_processor:
        raise HTTPException(status_code=500, detail="文件处理服务未初始化")
    return service_container.file_processor


# 健康检查端点
@app.get("/health")
async def health_check():
    """系统健康检查"""
    health_status = {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "deepseek": False,
            "neo4j": False,
            "redis": False,
            "database": False
        }
    }
    
    # 检查DeepSeek服务
    try:
        if service_container.deepseek_service:
            health_status["services"]["deepseek"] = True
    except Exception:
        pass
    
    # 检查Neo4j服务
    try:
        if service_container.neo4j_service:
            result = await service_container.neo4j_service.verify_connection()
            health_status["services"]["neo4j"] = result
    except Exception:
        pass
    
    # 检查Redis连接
    try:
        with redis_conn.sync_client() as client:
            client.ping()
            health_status["services"]["redis"] = True
    except Exception:
        pass
    
    # 检查数据库连接
    try:
        with db_connection.sync_session() as session:
            session.execute("SELECT 1")
            health_status["services"]["database"] = True
    except Exception:
        pass
    
    # 判断整体状态
    all_healthy = all(health_status["services"].values())
    health_status["status"] = "healthy" if all_healthy else "degraded"
    
    status_code = 200 if all_healthy else 503
    return JSONResponse(content=health_status, status_code=status_code)


# 系统信息端点
@app.get("/info")
async def system_info(current_user: dict = Depends(get_current_user)):
    """获取系统信息（需要认证）"""
    settings = get_settings()
    
    info = {
        "application": {
            "name": "EMC知识图谱系统",
            "version": "1.0.0",
            "environment": settings.environment,
            "debug": settings.debug
        },
        "services": {
            "deepseek_model": settings.deepseek_model,
            "neo4j_connected": service_container.neo4j_service is not None,
            "file_processor_ready": service_container.file_processor is not None
        }
    }
    
    # 如果是管理员，提供更多信息
    if current_user.get("role") == "admin":
        # 获取图数据库统计
        if service_container.neo4j_service:
            try:
                stats = await service_container.neo4j_service.get_knowledge_graph_summary()
                info["graph_statistics"] = stats
            except Exception:
                info["graph_statistics"] = {"error": "无法获取统计信息"}
        
        # 获取文件处理统计
        if service_container.file_processor:
            info["file_processing_stats"] = service_container.file_processor.get_processing_stats()
    
    return info


# 根路径重定向
@app.get("/")
async def root():
    """根路径信息"""
    return {
        "message": "EMC知识图谱系统 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "gateway.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.workers,
        log_level=settings.log_level.lower(),
        access_log=True
    )