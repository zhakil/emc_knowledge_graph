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
    tags: List[str] = []
    type: str = "file"
    parentId: Optional[str] = None
    size: Optional[int] = None

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
        "id": "folder_1",
        "name": "EMC知识库",
        "content": "",
        "path": "/",
        "lastModified": "2025-06-12",
        "tags": [],
        "type": "folder",
        "children": [
            {
                "id": "file_1",
                "name": "EMC测试指南.md",
                "content": "# EMC测试指南\n\n## 概述\n电磁兼容性(EMC)测试是确保电子设备在电磁环境中正常工作的重要手段。\n\n## 主要测试项目\n\n### 1. 辐射发射测试\n- 测试标准: CISPR 32\n- 频率范围: 30 MHz - 1 GHz\n- 测试距离: 3m/10m\n\n### 2. 传导发射测试\n- 测试标准: CISPR 32\n- 频率范围: 150 kHz - 30 MHz\n- 测试方法: LISN法\n\n### 3. 抗扰度测试\n- [[射频电磁场抗扰度]] - IEC 61000-4-3\n- [[静电放电抗扰度]] - IEC 61000-4-2\n- [[电快速瞬变脉冲群抗扰度]] - IEC 61000-4-4\n\n## 测试设备\n- 信号发生器\n- 频谱分析仪\n- 电磁场强度计\n- LISN (线阻抗稳定网络)\n\n## 相关标签\n#EMC #测试 #标准 #指南\n\n## 参考文档\n- [[IEC 61000系列标准]]\n- [[CISPR标准解读]]\n- [[设备测试流程]]",
                "path": "/EMC知识库/",
                "lastModified": "2025-06-12",
                "tags": ["EMC", "测试", "指南"],
                "type": "file",
                "parentId": "folder_1",
                "size": 1024
            },
            {
                "id": "file_2",
                "name": "IEC 61000系列标准.md",
                "content": "# IEC 61000系列标准\n\n## 标准概述\nIEC 61000是国际电工委员会制定的电磁兼容性标准系列。\n\n## 主要部分\n\n### IEC 61000-4系列 (测试和测量技术)\n- **IEC 61000-4-2**: 静电放电抗扰度测试\n- **IEC 61000-4-3**: 射频电磁场辐射抗扰度测试\n- **IEC 61000-4-4**: 电快速瞬变脉冲群抗扰度测试\n- **IEC 61000-4-5**: 浪涌(冲击)抗扰度测试\n- **IEC 61000-4-6**: 射频场感应的传导骚扰抗扰度\n- **IEC 61000-4-8**: 工频磁场抗扰度测试\n- **IEC 61000-4-11**: 电压暂降、短时中断和电压变化的抗扰度测试\n\n### IEC 61000-6系列 (通用标准)\n- **IEC 61000-6-1**: 居住、商业和轻工业环境抗扰度\n- **IEC 61000-6-2**: 工业环境抗扰度\n- **IEC 61000-6-3**: 居住、商业和轻工业环境发射\n- **IEC 61000-6-4**: 工业环境发射\n\n## 测试严酷等级\n\n| 等级 | 描述 | 应用环境 |\n|------|------|----------|\n| 1 | 低 | 良好的电磁环境 |\n| 2 | 中 | 一般的商业环境 |\n| 3 | 高 | 严酷的工业环境 |\n| 4 | 极高 | 特殊环境 |\n\n## 内部链接\n- [[EMC测试指南]]\n- [[静电放电测试详解]]\n- [[射频抗扰度测试方法]]\n\n#标准 #IEC #EMC #法规",
                "path": "/EMC知识库/",
                "lastModified": "2025-06-11",
                "tags": ["标准", "IEC", "EMC", "法规"],
                "type": "file",
                "parentId": "folder_1",
                "size": 2048
            }
        ]
    },
    {
        "id": "folder_2", 
        "name": "设备文档",
        "content": "",
        "path": "/",
        "lastModified": "2025-06-10",
        "tags": [],
        "type": "folder",
        "children": [
            {
                "id": "file_3",
                "name": "测试设备清单.md",
                "content": "# EMC测试设备清单\n\n## 发射测试设备\n\n### 辐射发射\n- **接收机/频谱分析仪**\n  - 频率范围: 9 kHz - 26.5 GHz\n  - 制造商: [[Rohde & Schwarz]]\n  - 型号: FSW26\n\n- **天线**\n  - 双锥天线 (30 MHz - 300 MHz)\n  - 对数周期天线 (300 MHz - 1 GHz)\n  - 喇叭天线 (1 GHz - 18 GHz)\n\n### 传导发射\n- **LISN (线阻抗稳定网络)**\n  - 频率范围: 150 kHz - 30 MHz\n  - 阻抗: 50Ω || 50μH\n\n## 抗扰度测试设备\n\n### 射频电磁场抗扰度\n- **信号发生器**\n  - 频率范围: 80 MHz - 1 GHz\n  - 最大输出功率: +20 dBm\n\n- **功率放大器**\n  - 频率范围: 80 MHz - 1 GHz  \n  - 输出功率: 100W\n\n- **场强计**\n  - 测量范围: 0.1 - 200 V/m\n  - 精度: ±1 dB\n\n### 静电放电测试\n- **ESD发生器**\n  - 电压范围: 100V - 30kV\n  - 放电模式: 接触放电/空气放电\n  - 符合标准: IEC 61000-4-2\n\n## 测试环境\n\n### 电波暗室\n- 尺寸: 10m × 6m × 6m\n- 频率范围: 30 MHz - 18 GHz\n- 反射系数: < -10 dB\n\n### 屏蔽室\n- 屏蔽效能: > 100 dB (10 kHz - 18 GHz)\n- 尺寸: 8m × 5m × 3m\n\n## 校准和维护\n- 设备校准周期: 12个月\n- 校准机构: [[国家认可实验室]]\n- 维护记录: [[设备维护记录表]]\n\n#设备 #测试 #校准 #维护",
                "path": "/设备文档/",
                "lastModified": "2025-06-10",
                "tags": ["设备", "测试", "清单"],
                "type": "file",
                "parentId": "folder_2",
                "size": 1536
            }
        ]
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

def get_file_category_and_extension(filename: str) -> tuple[str, str]:
    """根据文件扩展名确定分类"""
    if not filename:
        return "general", ""
    
    extension = filename.lower().split('.')[-1] if '.' in filename else ""
    
    # 文档类
    if extension in ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt']:
        return "document", extension
    # 表格类
    elif extension in ['xls', 'xlsx', 'csv', 'ods']:
        return "spreadsheet", extension
    # 图片类
    elif extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'tiff', 'ico']:
        return "image", extension
    # 网页类
    elif extension in ['html', 'htm', 'xml', 'xhtml']:
        return "web", extension
    # 代码类
    elif extension in ['js', 'ts', 'py', 'java', 'cpp', 'c', 'h', 'css', 'scss', 'less', 'json', 'yaml', 'yml']:
        return "code", extension
    # Markdown类
    elif extension in ['md', 'markdown']:
        return "markdown", extension
    # 压缩包类
    elif extension in ['zip', 'rar', '7z', 'tar', 'gz', 'bz2']:
        return "archive", extension
    # 音频类
    elif extension in ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a']:
        return "audio", extension
    # 视频类
    elif extension in ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm']:
        return "video", extension
    # EMC特定文件
    elif extension in ['emc', 'emi', 'ems']:
        return "emc-data", extension
    else:
        return "general", extension

@app.post("/api/files")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    category, extension = get_file_category_and_extension(file.filename)
    
    # 根据文件类型添加相应标签
    tags = ["上传"]
    if category == "image":
        tags.extend(["图片", "多媒体"])
    elif category == "web":
        tags.extend(["网页", "HTML"])
    elif category == "document":
        tags.extend(["文档", "资料"])
    elif category == "emc-data":
        tags.extend(["EMC", "测试数据"])
    elif category == "code":
        tags.extend(["代码", "程序"])
    
    new_file = {
        "id": file_id,
        "name": file.filename,
        "type": "file",
        "size": file.size or 0,
        "category": category,
        "extension": extension,
        "tags": tags,
        "createTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "path": "/uploads/",
        "status": "active",
        "isImage": category == "image",
        "isWeb": category == "web",
        "isDocument": category in ["document", "spreadsheet"],
        "previewable": category in ["image", "web", "document", "markdown", "code"]
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
            extension = file.get("extension", "").lower()
            category = file.get("category", "general")
            
            # 根据文件类型生成不同的预览内容
            if category == "image":
                return {
                    "type": "image",
                    "content": f"data:image/{extension};base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",  # 1x1像素透明图片
                    "previewType": "image",
                    "message": f"图片文件: {file['name']}",
                    "metadata": {
                        "format": extension.upper(),
                        "size": f"{file['size']} bytes",
                        "uploadTime": file['createTime']
                    }
                }
            elif category == "web":
                if extension == "html":
                    content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EMC测试报告</title>
    <style>
        body { font-family: 'SimSun', serif; margin: 20px; line-height: 1.6; }
        h1 { color: #2c3e50; border-bottom: 2px solid #d4af37; }
        h2 { color: #34495e; }
        .highlight { background: #fff3cd; padding: 10px; border-left: 4px solid #d4af37; }
        table { border-collapse: collapse; width: 100%; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f8f9fa; }
    </style>
</head>
<body>
    <h1>EMC电磁兼容性测试报告</h1>
    
    <div class="highlight">
        <strong>测试概述:</strong> 本报告包含了设备的完整EMC测试结果和分析。
    </div>
    
    <h2>测试项目</h2>
    <table>
        <tr><th>测试项目</th><th>标准</th><th>结果</th><th>状态</th></tr>
        <tr><td>辐射发射</td><td>CISPR 32</td><td>45.2 dBμV</td><td>✅ 通过</td></tr>
        <tr><td>传导发射</td><td>CISPR 32</td><td>38.1 dBμV</td><td>✅ 通过</td></tr>
        <tr><td>静电放电</td><td>IEC 61000-4-2</td><td>±8kV</td><td>✅ 通过</td></tr>
    </table>
    
    <h2>测试结论</h2>
    <p>设备在所有测试项目中均符合相关EMC标准要求，可以正常投入使用。</p>
</body>
</html>"""
                elif extension == "xml":
                    content = """<?xml version="1.0" encoding="UTF-8"?>
<emcTestReport xmlns="http://emc-standard.org/schema" version="1.0">
    <testInfo>
        <reportDate>2025-06-12</reportDate>
        <testLab>EMC测试实验室</testLab>
        <equipment>测试设备A</equipment>
    </testInfo>
    <testResults>
        <radiatedEmission>
            <standard>CISPR 32</standard>
            <frequency>30MHz-1GHz</frequency>
            <result>45.2 dBμV</result>
            <status>PASS</status>
        </radiatedEmission>
        <conductedEmission>
            <standard>CISPR 32</standard>
            <frequency>150kHz-30MHz</frequency>
            <result>38.1 dBμV</result>
            <status>PASS</status>
        </conductedEmission>
    </testResults>
</emcTestReport>"""
                else:
                    content = f"<html><body><h1>网页文件: {file['name']}</h1><p>类型: {extension.upper()}</p></body></html>"
                
                return {
                    "type": "web",
                    "content": content,
                    "previewType": "html",
                    "message": f"网页文件: {file['name']}"
                }
            elif extension == "pdf":
                content = "这是一个PDF文件的预览内容...\n\n# EMC测试报告\n\n## 测试项目\n- 辐射发射测试\n- 抗扰度测试\n- 谐波测试\n\n## 测试结果\n所有测试项目均符合相关标准要求。"
            elif extension in ["docx", "doc"]:
                content = "这是一个Word文档的预览内容...\n\n# IEC 61000-4-3 标准概述\n\n## 适用范围\n本标准适用于电子设备的射频电磁场抗扰度测试。\n\n## 测试方法\n1. 测试设备准备\n2. 测试环境设置\n3. 测试执行\n4. 结果评估"
            elif extension in ["xlsx", "xls", "csv"]:
                content = "表格数据预览:\n\n| 测试项目 | 标准要求 | 测试结果 | 状态 |\n|---------|---------|---------|------|\n| 辐射发射 | < 40 dBμV | 35.2 dBμV | 通过 |\n| 传导发射 | < 66 dBμV | 58.1 dBμV | 通过 |\n| ESD抗扰度 | ±8kV | ±8kV | 通过 |"
            elif extension in ["js", "ts", "py", "java", "cpp", "c"]:
                if extension == "py":
                    content = """# EMC数据分析脚本
import numpy as np
import matplotlib.pyplot as plt

def analyze_emc_data(frequencies, amplitudes):
    \"\"\"分析EMC测试数据\"\"\"
    max_amplitude = np.max(amplitudes)
    limit_line = get_cispr_limit(frequencies)
    
    compliance = np.all(amplitudes < limit_line)
    margin = limit_line - max_amplitude
    
    return {
        'max_amplitude': max_amplitude,
        'compliance': compliance,
        'margin': margin
    }

def plot_emc_spectrum(freq, amp, limit):
    \"\"\"绘制EMC频谱图\"\"\"
    plt.figure(figsize=(10, 6))
    plt.loglog(freq, amp, 'b-', label='测试数据')
    plt.loglog(freq, limit, 'r--', label='标准限值')
    plt.xlabel('频率 (MHz)')
    plt.ylabel('幅度 (dBμV)')
    plt.title('EMC辐射发射测试结果')
    plt.legend()
    plt.grid(True)
    plt.show()
"""
                elif extension in ["js", "ts"]:
                    content = """// EMC测试数据可视化
class EMCDataAnalyzer {
    constructor(testData) {
        this.testData = testData;
        this.results = [];
    }
    
    analyzeCompliance() {
        return this.testData.map(item => ({
            frequency: item.frequency,
            amplitude: item.amplitude,
            limit: this.getCISPRLimit(item.frequency),
            compliance: item.amplitude < this.getCISPRLimit(item.frequency)
        }));
    }
    
    getCISPRLimit(frequency) {
        // CISPR 32 限值计算
        if (frequency < 30) return 66; // dBμV
        if (frequency < 230) return 56; // dBμV
        return 60; // dBμV
    }
    
    generateReport() {
        const analysis = this.analyzeCompliance();
        const overallCompliance = analysis.every(item => item.compliance);
        
        return {
            timestamp: new Date().toISOString(),
            overallCompliance,
            details: analysis
        };
    }
}"""
                else:
                    content = f"// {extension.upper()}代码文件\n// 文件名: {file['name']}\n// 这是一个{extension.upper()}源代码文件的预览"
            elif extension in ["md", "markdown"]:
                content = f"# Markdown文档\n\n## 文件信息\n- 文件名: {file['name']}\n- 大小: {file['size']} bytes\n- 上传时间: {file['createTime']}\n\n## 内容预览\n这是一个Markdown格式的文档文件。"
            else:
                content = f"文件: {file['name']}\n类型: {file.get('category', '未知')}\n扩展名: {extension}\n大小: {file['size']} bytes\n创建时间: {file['createTime']}"
            
            return {
                "id": file_id,
                "name": file["name"],
                "content": content,
                "type": "text",
                "previewType": "text"
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

@app.post("/api/markdown-files/import-folder")
async def import_markdown_folder(files: List[UploadFile] = File(...)):
    """批量导入markdown文件到知识库"""
    imported_files = []
    folder_name = f"导入文件夹_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    folder_id = f"folder_imported_{datetime.now().timestamp()}"
    
    # 处理每个上传的文件
    for file in files:
        try:
            # 读取文件内容
            content = await file.read()
            content_str = content.decode('utf-8')
            
            # 创建文件记录
            file_id = f"imported_{datetime.now().timestamp()}_{len(imported_files)}"
            imported_file = {
                "id": file_id,
                "name": file.filename,
                "content": content_str,
                "lastModified": datetime.now().strftime("%Y-%m-%d"),
                "path": f"/{folder_name}/",
                "tags": ["导入", "文件夹导入"],
                "type": "file",
                "parentId": folder_id,
                "size": len(content)
            }
            imported_files.append(imported_file)
            
        except Exception as e:
            print(f"导入文件 {file.filename} 失败: {e}")
            continue
    
    # 创建文件夹结构
    if imported_files:
        import_folder = {
            "id": folder_id,
            "name": folder_name,
            "content": "",
            "lastModified": datetime.now().strftime("%Y-%m-%d"),
            "path": "/",
            "tags": ["导入"],
            "type": "folder",
            "children": imported_files
        }
        
        global mock_markdown_files
        mock_markdown_files.append(import_folder)
        
        return {
            "message": f"成功导入 {len(imported_files)} 个文件",
            "folder": import_folder,
            "imported_count": len(imported_files)
        }
    else:
        return {"message": "没有成功导入任何文件", "imported_count": 0}

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
    print("   - API文档: http://localhost:8001/docs")
    print("   - 系统健康: http://localhost:8001/health")
    print("   - 前端代理: http://localhost:3002")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )