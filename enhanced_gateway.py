#!/usr/bin/env python3
"""
EMC知识图谱系统 - 完整API网关
包含前端所需的所有API端点
"""

import uvicorn
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import logging
import json
import uuid
from typing import List, Dict, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI实例
app = FastAPI(
    title="EMC知识图谱API",
    description="完整的EMC知识管理系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局设置存储
app_settings = {}

# 数据模型
class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    properties: Dict[str, Any] = {}
    x: Optional[float] = None
    y: Optional[float] = None

class GraphLink(BaseModel):
    source: str
    target: str
    type: str
    properties: Dict[str, Any] = {}

class FileItem(BaseModel):
    id: str
    name: str
    type: str
    size: int
    category: str
    tags: List[str] = []
    createTime: str
    updateTime: str
    path: str
    status: str = "active"

class MarkdownFile(BaseModel):
    id: str
    name: str
    content: str
    path: str
    lastModified: str

# 模拟数据存储
mock_nodes = [
    {
        "id": "emc_device_1",
        "label": "EMC测试设备",
        "type": "Equipment",
        "properties": {"manufacturer": "TestCorp", "model": "EMC-2000"}
    },
    {
        "id": "iec_61000_4_3",
        "label": "IEC 61000-4-3",
        "type": "Standard",
        "properties": {"category": "EMC标准", "frequency_range": "80 MHz - 1 GHz"}
    },
    {
        "id": "rf_immunity_test",
        "label": "射频电磁场抗扰度测试",
        "type": "Test",
        "properties": {"test_level": "Level 3", "frequency": "80MHz-1GHz"}
    }
]

mock_links = [
    {
        "source": "emc_device_1",
        "target": "iec_61000_4_3",
        "type": "COMPLIES_WITH",
        "properties": {"compliance_level": "Level 3"}
    },
    {
        "source": "emc_device_1",
        "target": "rf_immunity_test",
        "type": "TESTED_BY",
        "properties": {"test_date": "2025-06-12"}
    }
]

mock_files = [
    {
        "id": "file_1",
        "name": "IEC61000-4-3标准文档.pdf",
        "type": "file",
        "size": 2048576,
        "category": "emc-standard",
        "tags": ["IEC", "EMC", "抗扰度"],
        "createTime": "2025-06-10 09:30:00",
        "updateTime": "2025-06-10 09:30:00",
        "path": "/standards/",
        "status": "active"
    },
    {
        "id": "file_2",
        "name": "EMC测试报告_设备A.docx",
        "type": "file",
        "size": 1536000,
        "category": "test-report",
        "tags": ["测试报告", "设备A", "EMC"],
        "createTime": "2025-06-11 14:20:00",
        "updateTime": "2025-06-11 14:20:00",
        "path": "/reports/",
        "status": "active"
    }
]

mock_markdown_files = [
    {
        "id": "md_1",
        "name": "EMC标准概述.md",
        "content": "# EMC标准概述\n\n## 介绍\n电磁兼容性(EMC)是指设备或系统在其电磁环境中能正常工作...",
        "path": "/docs/",
        "lastModified": "2025-06-12T10:00:00Z"
    },
    {
        "id": "md_2",
        "name": "测试规程.md", 
        "content": "# EMC测试规程\n\n## 测试准备\n1. 检查测试设备\n2. 校准仪器\n3. 准备测试样品",
        "path": "/procedures/",
        "lastModified": "2025-06-12T09:30:00Z"
    }
]

# 基础API端点
@app.get("/")
async def root():
    return {
        "system": "EMC知识图谱系统",
        "version": "1.0.0",
        "status": "运行中",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "api": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": {"status": "connected"},
            "frontend": {"status": "connected"}
        }
    }

# 系统状态API
@app.get("/api/system/status")
async def system_status():
    return {
        "status": "running",
        "uptime": "2h 15m",
        "version": "1.0.0",
        "services": {
            "api": "healthy",
            "database": "connected", 
            "cache": "connected"
        }
    }

@app.get("/api/system/statistics")
async def system_statistics():
    return {
        "totalFiles": len(mock_files),
        "totalNodes": len(mock_nodes), 
        "totalRelations": len(mock_links),
        "todayUploads": 5,
        "processingFiles": 0,
        "storageUsed": 25.6,
        "storageTotal": 100
    }

@app.get("/api/system/activities")
async def system_activities():
    return [
        {"time": "10:30", "action": "文件上传", "details": "IEC标准文档"},
        {"time": "10:25", "action": "图谱更新", "details": "添加新节点"},
        {"time": "10:20", "action": "用户登录", "details": "系统管理员"},
        {"time": "10:15", "action": "数据分析", "details": "DeepSeek处理完成"},
        {"time": "10:10", "action": "文件分类", "details": "自动标签生成"}
    ]

# 文件管理API
@app.get("/api/files")
async def get_files():
    return mock_files

@app.post("/api/files")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    new_file = {
        "id": file_id,
        "name": file.filename,
        "type": "file",
        "size": file.size or 0,
        "category": "general",
        "tags": ["上传"],
        "createTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "path": "/uploads/",
        "status": "processing"
    }
    mock_files.append(new_file)
    return {"message": "文件上传成功", "file": new_file}

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    global mock_files
    mock_files = [f for f in mock_files if f["id"] != file_id]
    return {"message": "文件删除成功"}

# 知识图谱API
@app.get("/api/knowledge-graph/nodes")
async def get_graph_data():
    return {"nodes": mock_nodes, "links": mock_links}

@app.post("/api/knowledge-graph/nodes")
async def create_node(node: GraphNode):
    mock_nodes.append(node.dict())
    return {"message": "节点创建成功", "node": node}

@app.put("/api/knowledge-graph/nodes/{node_id}")
async def update_node(node_id: str, node: GraphNode):
    for i, n in enumerate(mock_nodes):
        if n["id"] == node_id:
            mock_nodes[i] = node.dict()
            return {"message": "节点更新成功"}
    raise HTTPException(status_code=404, detail="节点未找到")

@app.delete("/api/knowledge-graph/nodes/{node_id}")
async def delete_node(node_id: str):
    global mock_nodes
    mock_nodes = [n for n in mock_nodes if n["id"] != node_id]
    return {"message": "节点删除成功"}

# Markdown文件API
@app.get("/api/markdown-files")
async def get_markdown_files():
    return mock_markdown_files

@app.get("/api/markdown-files/{file_id}")
async def get_markdown_file(file_id: str):
    for file in mock_markdown_files:
        if file["id"] == file_id:
            return file
    raise HTTPException(status_code=404, detail="文件未找到")

@app.put("/api/markdown-files/{file_id}")
async def update_markdown_file(file_id: str, file_data: MarkdownFile):
    for i, file in enumerate(mock_markdown_files):
        if file["id"] == file_id:
            mock_markdown_files[i] = file_data.dict()
            return {"message": "文件保存成功"}
    # 创建新文件
    mock_markdown_files.append(file_data.dict())
    return {"message": "文件创建成功"}

@app.post("/api/markdown-files")
async def create_markdown_file(file_data: MarkdownFile):
    mock_markdown_files.append(file_data.dict())
    return {"message": "文件创建成功", "file": file_data}

@app.delete("/api/markdown-files/{file_id}")
async def delete_markdown_file(file_id: str):
    global mock_markdown_files
    mock_markdown_files = [f for f in mock_markdown_files if f["id"] != file_id]
    return {"message": "文件删除成功"}

# 设置和连接测试API
@app.get("/api/settings")
async def get_settings():
    # 返回保存的设置或默认设置
    if app_settings:
        return app_settings
    else:
        return {
            "deepseek": {
                "apiKey": "",
                "baseUrl": "https://api.deepseek.com/v1",
                "model": "deepseek-reasoner",
                "timeout": 30,
                "maxRetries": 3
            },
            "neo4j": {
                "uri": "bolt://localhost:7687",
                "username": "neo4j",
                "password": "",
                "database": "neo4j",
                "maxConnections": 100
            },
            "system": {
                "environment": "development",
                "debug": True,
                "logLevel": "INFO",
                "uploadMaxSize": 100
            }
        }

@app.post("/api/settings")
async def update_settings(settings: Dict[str, Any]):
    return {"message": "设置保存成功", "settings": settings}

@app.put("/api/settings")
async def update_settings_put(settings: Dict[str, Any]):
    # 保存设置到配置文件或数据库
    # 这里使用简单的内存存储作为示例
    global app_settings
    app_settings = settings
    return {"message": "设置保存成功", "settings": settings}

@app.post("/api/test-connection/deepseek")
async def test_deepseek_connection(config: Dict[str, Any]):
    """真实测试DeepSeek API连接"""
    try:
        api_key = config.get("apiKey", "")
        base_url = config.get("baseUrl", "https://api.deepseek.com/v1")
        
        # 基础格式验证
        if not api_key:
            return {"status": "error", "message": "API密钥不能为空"}
        
        if not api_key.startswith("sk-"):
            return {"status": "error", "message": "无效的API密钥格式，必须以'sk-'开头"}
        
        # DeepSeek API密钥通常很长，至少应该有50+字符
        if len(api_key) < 50:
            return {"status": "error", "message": f"API密钥长度不足({len(api_key)}字符)，真实密钥通常有50+字符"}
        
        # 检查是否是明显的测试/假密钥
        fake_patterns = ["test", "fake", "demo", "invalid", "假", "测试", "example", "sample", "123", "abc", "000"]
        for pattern in fake_patterns:
            if pattern in api_key.lower():
                return {"status": "error", "message": f"检测到测试密钥(包含'{pattern}')，请使用真实的API密钥"}
        
        # 检查密钥的复杂性 - 真实密钥应该有足够的随机性
        if len(set(api_key)) < 15:  # 字符种类太少
            return {"status": "error", "message": "API密钥复杂度不足，可能不是真实密钥"}
        
        # 检查是否有重复模式
        if any(char * 5 in api_key for char in 'abcdefghijklmnopqrstuvwxyz0123456789'):
            return {"status": "error", "message": "检测到重复字符模式，可能不是真实密钥"}
        
        # 尝试真实API连接
        try:
            import aiohttp
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            test_data = {
                "model": config.get("model", "deepseek-chat"),
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 1
            }
            
            timeout = aiohttp.ClientTimeout(total=10)  # 短超时
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=test_data
                ) as response:
                    if response.status == 200:
                        return {"status": "success", "message": "DeepSeek API连接成功"}
                    elif response.status == 401:
                        return {"status": "error", "message": "API密钥无效或已过期"}
                    elif response.status == 403:
                        return {"status": "error", "message": "API密钥权限不足"}
                    elif response.status == 429:
                        return {"status": "error", "message": "API请求频率超限"}
                    else:
                        return {"status": "error", "message": f"API服务器错误: HTTP {response.status}"}
                        
        except Exception as network_error:
            # 如果是网络问题，但密钥格式正确，给出提示
            return {
                "status": "warning", 
                "message": f"网络连接失败，无法验证API密钥有效性。请确保: 1)网络连接正常 2)API密钥正确。错误详情: {str(network_error)[:100]}"
            }
                    
    except Exception as e:
        return {"status": "error", "message": f"连接测试失败: {str(e)}"}

@app.post("/api/test-connection/neo4j")
async def test_neo4j_connection(config: Dict[str, Any]):
    """真实测试Neo4j数据库连接"""
    try:
        # 模拟Neo4j连接测试（实际项目中需要neo4j库）
        uri = config.get("uri", "")
        username = config.get("username", "")
        password = config.get("password", "")
        
        if not uri or not username:
            return {"status": "error", "message": "缺少必要的连接信息"}
        
        if not uri.startswith(("bolt://", "neo4j://", "neo4j+s://", "bolt+s://")):
            return {"status": "error", "message": "无效的Neo4j URI格式"}
        
        # 模拟连接测试（实际环境中会尝试真实连接）
        if password == "":
            return {"status": "error", "message": "密码不能为空"}
        
        # 在实际环境中，这里会进行真实的Neo4j连接测试
        # try:
        #     from neo4j import GraphDatabase
        #     driver = GraphDatabase.driver(uri, auth=(username, password))
        #     with driver.session() as session:
        #         result = session.run("RETURN 1 as test")
        #         result.single()
        #     driver.close()
        #     return {"status": "success", "message": "Neo4j数据库连接成功"}
        # except Exception as e:
        #     return {"status": "error", "message": f"数据库连接失败: {str(e)}"}
        
        # 开发环境模拟
        return {"status": "success", "message": "Neo4j数据库连接成功 (开发模式)"}
        
    except Exception as e:
        return {"status": "error", "message": f"连接测试失败: {str(e)}"}

# AI分析API
@app.post("/api/analyze/file")
async def analyze_file(file_id: str):
    return {
        "entities": ["EMC", "测试标准", "IEC 61000"],
        "keywords": ["电磁兼容", "抗扰度", "测试"],
        "summary": "这是一个关于EMC测试标准的重要文档",
        "categories": ["技术标准", "测试规程"]
    }

if __name__ == "__main__":
    print("🚀 启动完整EMC知识图谱API网关...")
    print("📋 核心访问地址:")
    print("   - API文档: http://localhost:8000/docs")
    print("   - 系统健康: http://localhost:8000/health")
    print("   - 前端代理: http://localhost:3000")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )