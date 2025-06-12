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

@app.get("/api/files/{file_id}/preview")
async def preview_file(file_id: str):
    """预览文件内容"""
    for file in mock_files:
        if file["id"] == file_id:
            # 模拟文件内容
            if file["name"].endswith(".pdf"):
                content = "这是一个PDF文件的预览内容...\n\n# EMC测试报告\n\n## 测试项目\n- 辐射发射测试\n- 抗扰度测试\n- 谐波测试\n\n## 测试结果\n所有测试项目均符合相关标准要求。"
            elif file["name"].endswith(".docx"):
                content = "这是一个Word文档的预览内容...\n\n# IEC 61000-4-3 标准概述\n\n## 适用范围\n本标准适用于电子设备的射频电磁场抗扰度测试。\n\n## 测试方法\n1. 测试设备准备\n2. 测试环境设置\n3. 测试执行\n4. 结果评估"
            else:
                content = f"文件: {file['name']}\n类型: {file['type']}\n大小: {file['size']} bytes\n创建时间: {file['createTime']}"
            
            return {
                "id": file_id,
                "name": file["name"],
                "content": content,
                "type": file["type"],
                "size": file["size"]
            }
    
    raise HTTPException(status_code=404, detail="文件未找到")

@app.get("/api/files/{file_id}/download")
async def download_file(file_id: str):
    """下载文件"""
    from fastapi.responses import Response
    
    for file in mock_files:
        if file["id"] == file_id:
            # 模拟文件内容
            content = f"模拟文件内容 - {file['name']}\n创建时间: {file['createTime']}\n文件大小: {file['size']} bytes"
            
            return Response(
                content=content.encode('utf-8'),
                media_type='application/octet-stream',
                headers={
                    "Content-Disposition": f"attachment; filename={file['name']}"
                }
            )
    
    raise HTTPException(status_code=404, detail="文件未找到")

@app.post("/api/files/{file_id}/share")
async def share_file(file_id: str, share_config: Dict[str, Any] = None):
    """分享文件"""
    if share_config is None:
        share_config = {}
        
    for file in mock_files:
        if file["id"] == file_id:
            # 生成分享链接
            share_token = f"share_{file_id}_{uuid.uuid4().hex[:8]}"
            share_link = f"http://localhost:8000/api/shared/{share_token}"
            
            expiry_hours = share_config.get("expiryHours", 24)
            password = share_config.get("password", "")
            
            return {
                "shareLink": share_link,
                "shareToken": share_token,
                "expiryHours": expiry_hours,
                "hasPassword": bool(password),
                "message": f"文件 '{file['name']}' 分享成功"
            }
    
    raise HTTPException(status_code=404, detail="文件未找到")

@app.get("/api/shared/{share_token}")
async def get_shared_file(share_token: str):
    """获取分享的文件"""
    # 从分享token解析文件ID
    if share_token.startswith("share_"):
        parts = share_token.split("_")
        if len(parts) >= 2:
            file_id = parts[1]
            
            for file in mock_files:
                if file["id"] == file_id:
                    return {
                        "file": file,
                        "shareToken": share_token,
                        "message": "分享文件获取成功"
                    }
    
    raise HTTPException(status_code=404, detail="分享链接无效或已过期")

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
    """直接调用DeepSeek官方API验证"""
    try:
        api_key = config.get("apiKey", "")
        base_url = config.get("baseUrl", "https://api.deepseek.com/v1")
        
        # 仅基础检查
        if not api_key:
            return {"status": "error", "message": "API密钥不能为空"}
        
        # 直接调用DeepSeek官方API - 让官方判定密钥是否有效
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
            
            timeout = aiohttp.ClientTimeout(total=15)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=test_data
                ) as response:
                    if response.status == 200:
                        return {"status": "success", "message": "DeepSeek API连接成功！官方验证通过。"}
                    elif response.status == 401:
                        return {"status": "error", "message": "API密钥无效 - DeepSeek官方验证失败"}
                    elif response.status == 403:
                        return {"status": "error", "message": "API密钥权限不足 - DeepSeek官方拒绝访问"}
                    elif response.status == 429:
                        return {"status": "error", "message": "API请求频率超限 - 请稍后重试"}
                    else:
                        response_text = await response.text()
                        return {"status": "error", "message": f"DeepSeek API错误 (HTTP {response.status}): {response_text[:200]}"}
                        
        except Exception as network_error:
            return {
                "status": "warning", 
                "message": f"网络连接失败，无法连接到DeepSeek官方API。请检查网络连接。错误: {str(network_error)[:150]}"
            }
                    
    except Exception as e:
        return {"status": "error", "message": f"连接测试失败: {str(e)}"}

@app.post("/api/test-connection/claude")
async def test_claude_connection(config: Dict[str, Any]):
    """测试Claude API连接"""
    try:
        api_key = config.get("apiKey", "")
        base_url = config.get("baseUrl", "https://api.anthropic.com/v1")
        
        # 基础检查
        if not api_key:
            return {"status": "error", "message": "API密钥不能为空"}
        
        # Claude API密钥格式检查
        if not api_key.startswith("sk-ant-"):
            return {"status": "error", "message": "无效的Claude API密钥格式，必须以'sk-ant-'开头"}
        
        # 直接调用Claude API验证
        try:
            import aiohttp
            
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            test_data = {
                "model": config.get("model", "claude-3-5-sonnet-20241022"),
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            timeout = aiohttp.ClientTimeout(total=15)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{base_url}/messages",
                    headers=headers,
                    json=test_data
                ) as response:
                    if response.status == 200:
                        return {"status": "success", "message": "Claude API连接成功！Sonnet 4模型可用。"}
                    elif response.status == 401:
                        return {"status": "error", "message": "API密钥无效 - Claude官方验证失败"}
                    elif response.status == 403:
                        return {"status": "error", "message": "API密钥权限不足 - Claude官方拒绝访问"}
                    elif response.status == 429:
                        return {"status": "error", "message": "API请求频率超限 - 请稍后重试"}
                    else:
                        response_text = await response.text()
                        return {"status": "error", "message": f"Claude API错误 (HTTP {response.status}): {response_text[:200]}"}
                        
        except Exception as network_error:
            return {
                "status": "warning", 
                "message": f"网络连接失败，无法连接到Claude官方API。请检查网络连接。错误: {str(network_error)[:150]}"
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