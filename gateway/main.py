"""
EMC知识图谱系统 - API网关主应用
实用高效的API服务，专注核心功能实现
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="EMC知识图谱系统",
    description="集成DeepSeek AI和Neo4j的EMC领域知识图谱平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS - 实用的跨域设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 创建上传目录
os.makedirs("uploads", exist_ok=True)

# 挂载静态文件服务
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 请求/响应模型
class ChatRequest(BaseModel):
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 2000

class ChatResponse(BaseModel):
    content: str
    usage: Dict[str, int]
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, bool]
    version: str

# 全局状态管理
app_state = {
    "startup_time": datetime.now(),
    "request_count": 0,
    "uploaded_files": [],
    "chat_sessions": {},
    "graph_data": {"nodes": [], "edges": []}
}

@app.middleware("http")
async def request_counter(request, call_next):
    """请求计数中间件"""
    app_state["request_count"] += 1
    response = await call_next(request)
    return response

@app.get("/", response_model=Dict[str, Any])
async def root():
    """根路径 - 系统信息"""
    uptime = datetime.now() - app_state["startup_time"]
    return {
        "name": "EMC知识图谱系统",
        "version": "1.0.0",
        "status": "running",
        "uptime_seconds": int(uptime.total_seconds()),
        "request_count": app_state["request_count"],
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "api_endpoints": {
            "health": "/health",
            "test": "/api/test",
            "deepseek_chat": "/api/deepseek/chat",
            "graph_data": "/api/graph/data",
            "file_upload": "/api/files/upload"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查 - 实用的系统状态监控"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        services={
            "api_gateway": True,
            "file_system": os.path.exists("uploads"),
            "deepseek": bool(os.getenv("EMC_DEEPSEEK_API_KEY", "").startswith("sk-")),
            "neo4j": False,  # 待实现
            "postgres": False  # 待实现
        },
        version="1.0.0"
    )

@app.get("/api/test")
async def test_endpoint():
    """测试端点 - 验证API可用性"""
    return {
        "message": "API测试成功",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("EMC_ENVIRONMENT", "development"),
        "debug_mode": os.getenv("EMC_DEBUG", "false").lower() == "true",
        "python_path": os.environ.get("PYTHONPATH", "未设置"),
        "working_directory": os.getcwd()
    }

# DeepSeek AI集成模块
@app.post("/api/deepseek/chat", response_model=ChatResponse)
async def deepseek_chat(request: ChatRequest):
    """DeepSeek聊天接口"""
    api_key = os.getenv("EMC_DEEPSEEK_API_KEY")
    
    if not api_key or api_key == "sk-placeholder-key":
        raise HTTPException(
            status_code=501,
            detail="DeepSeek API密钥未配置。请在.env文件中设置EMC_DEEPSEEK_API_KEY"
        )
    
    # 模拟AI响应（实际项目中这里会调用DeepSeek API）
    mock_response = f"""
基于您的查询："{request.prompt}"

这是一个模拟的EMC专家回复。在实际部署中，这里会连接到DeepSeek API进行智能分析。

EMC分析要点：
1. 电磁兼容性测试标准
2. 设备辐射发射测量
3. 传导干扰评估
4. 抗扰度测试要求

温度参数：{request.temperature}
最大令牌数：{request.max_tokens}
    """
    
    return ChatResponse(
        content=mock_response.strip(),
        usage={"prompt_tokens": len(request.prompt), "completion_tokens": 150, "total_tokens": len(request.prompt) + 150},
        timestamp=datetime.now().isoformat()
    )

# 图数据库模块
@app.get("/api/graph/data")
async def get_graph_data():
    """获取图数据"""
    # 返回示例图数据结构
    sample_data = {
        "nodes": [
            {
                "id": "standard_1",
                "label": "EN 55032:2015",
                "type": "EMCStandard",
                "properties": {
                    "title": "Electromagnetic compatibility of multimedia equipment",
                    "frequency_range": "9 kHz to 400 GHz"
                }
            },
            {
                "id": "equipment_1", 
                "label": "无线路由器",
                "type": "Equipment",
                "properties": {
                    "category": "ITE",
                    "power": "12V DC"
                }
            }
        ],
        "edges": [
            {
                "id": "rel_1",
                "source": "equipment_1",
                "target": "standard_1", 
                "type": "COMPLIES_WITH",
                "properties": {
                    "test_date": "2024-01-15",
                    "result": "PASS"
                }
            }
        ],
        "metadata": {
            "total_nodes": 2,
            "total_edges": 1,
            "last_updated": datetime.now().isoformat()
        }
    }
    
    return sample_data

@app.post("/api/graph/query")
async def execute_graph_query(query: Dict[str, Any]):
    """执行图查询"""
    cypher_query = query.get("cypher", "")
    
    if not cypher_query:
        raise HTTPException(status_code=400, detail="缺少Cypher查询语句")
    
    # 模拟查询结果
    return {
        "query": cypher_query,
        "results": [
            {"node_id": "standard_1", "label": "EN 55032:2015"},
            {"node_id": "equipment_1", "label": "无线路由器"}
        ],
        "execution_time": 0.05,
        "timestamp": datetime.now().isoformat()
    }

# 文件处理模块
@app.post("/api/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    extract_entities: bool = Form(True),
    build_graph: bool = Form(False)
):
    """文件上传和处理"""
    
    # 验证文件类型
    allowed_types = ['.pdf', '.docx', '.xlsx', '.csv', '.json', '.xml', '.txt']
    filename = file.filename or ""
    file_ext = os.path.splitext(filename)[1].lower()
    
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file_ext}。支持的类型: {', '.join(allowed_types)}"
        )
    
    # 保存文件
    file_path = f"uploads/{file.filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 模拟文件处理结果
        processing_result = {
            "file_id": f"file_{len(app_state['uploaded_files']) + 1}",
            "filename": file.filename,
            "size": len(content),
            "type": file_ext,
            "status": "processed",
            "entities_extracted": extract_entities,
            "graph_built": build_graph,
            "upload_time": datetime.now().isoformat(),
            "download_url": f"/uploads/{file.filename}"
        }
        
        if extract_entities:
            processing_result["entities"] = [
                {"type": "EMCStandard", "name": "EN 55032", "confidence": 0.95},
                {"type": "Equipment", "name": "测试设备", "confidence": 0.88},
                {"type": "FrequencyRange", "name": "30MHz-1GHz", "confidence": 0.92}
            ]
        
        app_state["uploaded_files"].append(processing_result)
        
        return processing_result
        
    except Exception as e:
        logger.error(f"文件处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")

@app.get("/api/files/list")
async def list_uploaded_files():
    """获取已上传文件列表"""
    return {
        "files": app_state["uploaded_files"],
        "total_count": len(app_state["uploaded_files"]),
        "timestamp": datetime.now().isoformat()
    }

# 统计和监控
@app.get("/api/stats")
async def get_system_stats():
    """系统统计信息"""
    uptime = datetime.now() - app_state["startup_time"]
    
    return {
        "system": {
            "uptime_seconds": int(uptime.total_seconds()),
            "request_count": app_state["request_count"],
            "uploaded_files": len(app_state["uploaded_files"]),
            "memory_usage": "模拟数据",
            "cpu_usage": "模拟数据"
        },
        "api": {
            "total_endpoints": len([route for route in app.routes if hasattr(route, 'methods')]),
            "health_status": "healthy"
        },
        "timestamp": datetime.now().isoformat()
    }

# 错误处理
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """404错误处理"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "接口不存在",
            "path": str(request.url.path),
            "message": "请检查API路径是否正确",
            "available_endpoints": ["/docs", "/health", "/api/test"]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """500错误处理"""
    logger.error(f"内部服务器错误: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "内部服务器错误",
            "message": "服务暂时不可用，请稍后重试",
            "timestamp": datetime.now().isoformat()
        }
    )

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("🚀 EMC知识图谱系统启动完成")
    logger.info(f"📁 工作目录: {os.getcwd()}")
    logger.info(f"📂 上传目录: {os.path.abspath('uploads')}")

@app.on_event("shutdown") 
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("🔄 EMC知识图谱系统正在关闭")

# 开发环境运行
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )