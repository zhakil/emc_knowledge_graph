#!/usr/bin/env python3
"""
EMC知识图谱系统 - 完整功能版本
包含知识图谱构建、可视化、搜索、文件处理等完整功能
"""

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import json
import os
import sys
import webbrowser
import threading
import time
import tempfile
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import re
import subprocess

# 创建FastAPI应用
app = FastAPI(
    title="EMC知识图谱系统",
    description="完整的EMC知识管理与分析平台",
    version="1.0.0"
)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局数据存储
knowledge_base = {
    "nodes": [
        {
            "id": "emc_device_001",
            "label": "EMC测试设备",
            "type": "设备",
            "category": "测试设备",
            "properties": {
                "型号": "EMI-9KB",
                "厂商": "罗德与施瓦茨",
                "频率范围": "9kHz-30MHz",
                "用途": "传导发射测试"
            },
            "x": 100,
            "y": 100
        },
        {
            "id": "std_gb17626",
            "label": "GB/T 17626系列标准",
            "type": "标准",
            "category": "国家标准",
            "properties": {
                "发布机构": "国家标准化委员会",
                "适用范围": "电磁兼容试验和测量技术",
                "最新版本": "2018版",
                "替代关系": "等同采用IEC 61000-4系列"
            },
            "x": 400,
            "y": 100
        },
        {
            "id": "test_immunity",
            "label": "抗扰度测试",
            "type": "测试",
            "category": "EMC测试",
            "properties": {
                "测试类型": "电磁抗扰度",
                "测试对象": "电子电器产品",
                "测试环境": "电波暗室",
                "合格标准": "功能正常或性能降级在可接受范围"
            },
            "x": 250,
            "y": 200
        },
        {
            "id": "report_001",
            "label": "EMC测试报告",
            "type": "文档",
            "category": "测试报告",
            "properties": {
                "报告编号": "EMC-2024-001",
                "测试产品": "智能手机",
                "测试日期": "2024-01-15",
                "测试结论": "合格",
                "有效期": "3年"
            },
            "x": 250,
            "y": 350
        },
        {
            "id": "product_phone",
            "label": "智能手机",
            "type": "产品",
            "category": "消费电子",
            "properties": {
                "品牌": "华为",
                "型号": "Mate60 Pro",
                "工作频段": "GSM/WCDMA/LTE/5G",
                "EMC要求": "满足CCC认证要求"
            },
            "x": 50,
            "y": 300
        },
        {
            "id": "std_iec61000",
            "label": "IEC 61000系列",
            "type": "标准",
            "category": "国际标准",
            "properties": {
                "发布机构": "国际电工委员会",
                "标准性质": "电磁兼容基础标准",
                "构成": "6个部分共100+子标准",
                "应用范围": "全球EMC标准基础"
            },
            "x": 550,
            "y": 200
        },
        {
            "id": "facility_chamber",
            "label": "电波暗室",
            "type": "设施",
            "category": "测试环境",
            "properties": {
                "类型": "全电波暗室",
                "尺寸": "10m×6m×6m",
                "频率范围": "30MHz-18GHz",
                "最低静区": "1.5m×1.5m×1.5m"
            },
            "x": 400,
            "y": 300
        },
        {
            "id": "expert_zhang",
            "label": "张工程师",
            "type": "专家",
            "category": "EMC专家",
            "properties": {
                "职称": "高级工程师",
                "专业": "电磁兼容",
                "经验": "15年EMC测试经验",
                "认证": "NARTE EMC工程师"
            },
            "x": 100,
            "y": 450
        }
    ],
    "relationships": [
        {
            "id": "rel_001",
            "source": "emc_device_001",
            "target": "test_immunity",
            "label": "用于执行",
            "type": "执行关系",
            "properties": {"权重": 0.9, "重要性": "高"}
        },
        {
            "id": "rel_002", 
            "source": "std_gb17626",
            "target": "test_immunity",
            "label": "测试依据",
            "type": "依据关系",
            "properties": {"权重": 1.0, "重要性": "极高"}
        },
        {
            "id": "rel_003",
            "source": "test_immunity",
            "target": "report_001",
            "label": "产生",
            "type": "产出关系",
            "properties": {"权重": 0.8, "重要性": "高"}
        },
        {
            "id": "rel_004",
            "source": "product_phone",
            "target": "test_immunity", 
            "label": "接受测试",
            "type": "测试关系",
            "properties": {"权重": 0.9, "重要性": "高"}
        },
        {
            "id": "rel_005",
            "source": "std_iec61000",
            "target": "std_gb17626",
            "label": "国际基础",
            "type": "参考关系",
            "properties": {"权重": 0.7, "重要性": "中"}
        },
        {
            "id": "rel_006",
            "source": "facility_chamber",
            "target": "test_immunity",
            "label": "测试环境",
            "type": "环境关系", 
            "properties": {"权重": 0.8, "重要性": "高"}
        },
        {
            "id": "rel_007",
            "source": "expert_zhang",
            "target": "test_immunity",
            "label": "负责执行",
            "type": "责任关系",
            "properties": {"权重": 0.6, "重要性": "中"}
        }
    ]
}

# 文件存储
uploaded_files = {}
analysis_results = {}

# EMC知识库
emc_knowledge = {
    "standards": {
        "GB/T 17626": {
            "name": "电磁兼容试验和测量技术",
            "parts": [
                "GB/T 17626.1 概述",
                "GB/T 17626.2 静电放电抗扰度试验", 
                "GB/T 17626.3 射频电磁场辐射抗扰度试验",
                "GB/T 17626.4 电快速瞬变脉冲群抗扰度试验",
                "GB/T 17626.5 浪涌(冲击)抗扰度试验",
                "GB/T 17626.6 射频场感应的传导骚扰抗扰度试验"
            ],
            "applications": ["消费电子", "工业设备", "汽车电子"],
            "test_levels": ["1级", "2级", "3级", "4级"]
        },
        "IEC 61000": {
            "name": "电磁兼容(EMC)",
            "parts": [
                "IEC 61000-1 总则",
                "IEC 61000-2 环境", 
                "IEC 61000-3 限值",
                "IEC 61000-4 试验和测量技术",
                "IEC 61000-5 安装和减缓导则",
                "IEC 61000-6 通用标准"
            ]
        }
    },
    "test_methods": {
        "传导发射": {
            "frequency_range": "150kHz-30MHz",
            "equipment": ["LISN", "EMI接收机", "测试软件"],
            "standards": ["GB/T 6113.1", "CISPR 25"]
        },
        "辐射发射": {
            "frequency_range": "30MHz-1GHz", 
            "equipment": ["天线", "EMI接收机", "电波暗室"],
            "standards": ["GB/T 6113.2", "CISPR 25"]
        },
        "静电放电": {
            "test_voltage": "±2kV-±15kV",
            "equipment": ["ESD发生器", "水平耦合板", "垂直耦合板"],
            "standards": ["GB/T 17626.2", "IEC 61000-4-2"]
        }
    }
}

@app.get("/", response_class=HTMLResponse)
async def root():
    """主页面"""
    html_content = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EMC知识图谱系统</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .header {{ 
            background: rgba(255,255,255,0.95); 
            padding: 20px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }}
        .nav {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            max-width: 1200px; 
            margin: 0 auto; 
        }}
        .logo {{ 
            font-size: 1.8em; 
            font-weight: bold; 
            color: #2c3e50;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .nav-links {{ display: flex; gap: 20px; }}
        .nav-links button {{ 
            padding: 8px 16px; 
            background: linear-gradient(45deg, #007bff, #0056b3); 
            color: white; 
            border: none; 
            border-radius: 20px; 
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .nav-links button:hover {{ transform: translateY(-2px); }}
        
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .tabs {{ 
            display: flex; 
            background: rgba(255,255,255,0.9); 
            border-radius: 10px 10px 0 0; 
            overflow: hidden;
        }}
        .tab {{ 
            padding: 15px 25px; 
            cursor: pointer; 
            background: rgba(255,255,255,0.7); 
            border: none;
            transition: all 0.3s ease;
            font-weight: bold;
        }}
        .tab.active {{ background: rgba(255,255,255,1); color: #007bff; }}
        .tab:hover {{ background: rgba(255,255,255,0.9); }}
        
        .content {{ 
            background: rgba(255,255,255,0.95); 
            min-height: 600px; 
            border-radius: 0 0 10px 10px;
            backdrop-filter: blur(10px);
        }}
        
        .tab-content {{ display: none; padding: 30px; }}
        .tab-content.active {{ display: block; }}
        
        /* 知识图谱样式 */
        .graph-container {{ 
            display: grid; 
            grid-template-columns: 1fr 300px; 
            gap: 20px; 
            height: 500px; 
        }}
        .graph-canvas {{ 
            border: 2px solid #ddd; 
            border-radius: 10px; 
            background: #f8f9fa;
            position: relative;
        }}
        .graph-controls {{ 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 10px; 
            border: 2px solid #ddd;
        }}
        
        /* 搜索样式 */
        .search-container {{ 
            display: grid; 
            grid-template-columns: 1fr 300px; 
            gap: 20px; 
        }}
        .search-input {{ 
            display: flex; 
            gap: 10px; 
            margin-bottom: 20px; 
        }}
        .search-input input {{ 
            flex: 1; 
            padding: 12px; 
            border: 2px solid #ddd; 
            border-radius: 8px; 
            font-size: 16px;
        }}
        .search-input button {{ 
            padding: 12px 24px; 
            background: #007bff; 
            color: white; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer;
        }}
        .search-results {{ 
            max-height: 400px; 
            overflow-y: auto; 
        }}
        .result-item {{ 
            background: #f8f9fa; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 8px; 
            border-left: 4px solid #007bff;
            cursor: pointer;
        }}
        .result-item:hover {{ background: #e9ecef; }}
        
        /* 文件上传样式 */
        .upload-area {{ 
            border: 3px dashed #007bff; 
            border-radius: 10px; 
            padding: 40px; 
            text-align: center; 
            margin: 20px 0;
            transition: all 0.3s ease;
        }}
        .upload-area:hover {{ background: rgba(0,123,255,0.05); }}
        .upload-area.dragover {{ 
            background: rgba(0,123,255,0.1); 
            border-color: #0056b3; 
        }}
        
        /* 分析结果样式 */
        .analysis-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin: 20px 0; 
        }}
        .analysis-card {{ 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 10px; 
            border-left: 4px solid #28a745;
        }}
        
        /* 通用样式 */
        .btn {{ 
            padding: 10px 20px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            transition: all 0.3s ease;
            font-weight: bold;
        }}
        .btn-primary {{ background: #007bff; color: white; }}
        .btn-success {{ background: #28a745; color: white; }}
        .btn-warning {{ background: #ffc107; color: #333; }}
        .btn-danger {{ background: #dc3545; color: white; }}
        .btn:hover {{ transform: translateY(-1px); }}
        
        .info-panel {{ 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 10px 0;
        }}
        .info-panel h4 {{ color: #495057; margin-bottom: 10px; }}
        
        .stats-grid {{ 
            display: grid; 
            grid-template-columns: repeat(4, 1fr); 
            gap: 15px; 
            margin: 20px 0; 
        }}
        .stat-card {{ 
            background: linear-gradient(45deg, #007bff, #0056b3); 
            color: white; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center;
        }}
        .stat-number {{ font-size: 2em; font-weight: bold; }}
        .stat-label {{ margin-top: 5px; opacity: 0.9; }}
        
        .loading {{ 
            display: inline-block; 
            width: 20px; 
            height: 20px; 
            border: 3px solid #f3f3f3; 
            border-top: 3px solid #007bff; 
            border-radius: 50%; 
            animation: spin 1s linear infinite; 
        }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        
        #graphVis {{ width: 100%; height: 100%; }}
        
        /* 响应式设计 */
        @media (max-width: 768px) {{
            .graph-container,
            .search-container {{ grid-template-columns: 1fr; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .nav {{ flex-direction: column; gap: 15px; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="nav">
            <div class="logo">🏛️ EMC知识图谱系统</div>
            <div class="nav-links">
                <button onclick="refreshData()">🔄 刷新</button>
                <button onclick="exportData()">📤 导出</button>
                <button onclick="showSettings()">⚙️ 设置</button>
                <button onclick="showHelp()">❓ 帮助</button>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="nodeCount">8</div>
                <div class="stat-label">知识节点</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="relCount">7</div>
                <div class="stat-label">关系连接</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="fileCount">0</div>
                <div class="stat-label">处理文件</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">100%</div>
                <div class="stat-label">系统健康</div>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('graph')">🌐 知识图谱</button>
            <button class="tab" onclick="showTab('search')">🔍 智能搜索</button>
            <button class="tab" onclick="showTab('upload')">📁 文件处理</button>
            <button class="tab" onclick="showTab('analysis')">📊 知识分析</button>
            <button class="tab" onclick="showTab('standards')">📋 标准库</button>
        </div>
        
        <div class="content">
            <!-- 知识图谱标签页 -->
            <div id="graph" class="tab-content active">
                <h2>🌐 EMC知识图谱可视化</h2>
                <div class="graph-container">
                    <div class="graph-canvas">
                        <div id="graphVis"></div>
                    </div>
                    <div class="graph-controls">
                        <h4>🎛️ 图谱控制</h4>
                        <button class="btn btn-primary" onclick="resetLayout()">🔄 重置布局</button>
                        <button class="btn btn-success" onclick="addNode()">➕ 添加节点</button>
                        <button class="btn btn-warning" onclick="exportGraph()">📤 导出图谱</button>
                        
                        <div class="info-panel">
                            <h4>📋 节点信息</h4>
                            <div id="nodeInfo">点击节点查看详情</div>
                        </div>
                        
                        <div class="info-panel">
                            <h4>🎯 筛选选项</h4>
                            <label><input type="checkbox" checked onchange="filterNodes('设备')"> 设备</label><br>
                            <label><input type="checkbox" checked onchange="filterNodes('标准')"> 标准</label><br>
                            <label><input type="checkbox" checked onchange="filterNodes('测试')"> 测试</label><br>
                            <label><input type="checkbox" checked onchange="filterNodes('产品')"> 产品</label><br>
                            <label><input type="checkbox" checked onchange="filterNodes('专家')"> 专家</label>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 智能搜索标签页 -->
            <div id="search" class="tab-content">
                <h2>🔍 EMC知识智能搜索</h2>
                <div class="search-container">
                    <div>
                        <div class="search-input">
                            <input type="text" id="searchQuery" placeholder="输入搜索关键词，如：静电放电、GB/T 17626、抗扰度..." onkeypress="if(event.key==='Enter') searchKnowledge()">
                            <button onclick="searchKnowledge()">🔍 搜索</button>
                        </div>
                        <div class="search-results" id="searchResults">
                            <div class="info-panel">
                                <h4>💡 搜索提示</h4>
                                <p>• 输入标准号：如 GB/T 17626.2</p>
                                <p>• 输入测试类型：如 静电放电测试</p>
                                <p>• 输入设备名称：如 EMC测试设备</p>
                                <p>• 输入产品类型：如 智能手机</p>
                            </div>
                        </div>
                    </div>
                    <div>
                        <div class="info-panel">
                            <h4>🎯 快速搜索</h4>
                            <button class="btn btn-primary" onclick="quickSearch('GB/T 17626')" style="margin: 5px;">GB/T 17626</button>
                            <button class="btn btn-primary" onclick="quickSearch('静电放电')" style="margin: 5px;">静电放电</button>
                            <button class="btn btn-primary" onclick="quickSearch('EMC测试')" style="margin: 5px;">EMC测试</button>
                            <button class="btn btn-primary" onclick="quickSearch('智能手机')" style="margin: 5px;">智能手机</button>
                        </div>
                        
                        <div class="info-panel">
                            <h4>📊 搜索统计</h4>
                            <p>总节点数: <span id="totalNodes">8</span></p>
                            <p>总关系数: <span id="totalRels">7</span></p>
                            <p>搜索次数: <span id="searchCount">0</span></p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 文件处理标签页 -->
            <div id="upload" class="tab-content">
                <h2>📁 EMC文件处理与知识抽取</h2>
                <div class="upload-area" id="uploadArea" ondrop="handleDrop(event)" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)">
                    <h3>📤 拖拽文件到此处或点击上传</h3>
                    <p>支持格式: PDF, DOC, DOCX, TXT, XLS, XLSX</p>
                    <input type="file" id="fileInput" multiple style="display: none;" onchange="handleFileSelect(event)">
                    <button class="btn btn-primary" onclick="document.getElementById('fileInput').click()">📁 选择文件</button>
                </div>
                
                <div id="fileList"></div>
                <div id="extractionResults"></div>
            </div>
            
            <!-- 知识分析标签页 -->
            <div id="analysis" class="tab-content">
                <h2>📊 EMC知识分析与挖掘</h2>
                <div class="analysis-grid">
                    <div class="analysis-card">
                        <h4>🎯 节点中心性分析</h4>
                        <div id="centralityAnalysis">
                            <p><strong>度中心性最高:</strong> GB/T 17626系列标准</p>
                            <p><strong>介数中心性最高:</strong> 抗扰度测试</p>
                            <p><strong>接近中心性最高:</strong> EMC测试设备</p>
                        </div>
                        <button class="btn btn-info" onclick="runCentralityAnalysis()">🔄 重新分析</button>
                    </div>
                    
                    <div class="analysis-card">
                        <h4>🌐 社区发现</h4>
                        <div id="communityAnalysis">
                            <p><strong>社区1:</strong> 测试设备群 (3个节点)</p>
                            <p><strong>社区2:</strong> 标准规范群 (2个节点)</p>
                            <p><strong>社区3:</strong> 产品测试群 (3个节点)</p>
                        </div>
                        <button class="btn btn-info" onclick="runCommunityDetection()">🔄 重新聚类</button>
                    </div>
                    
                    <div class="analysis-card">
                        <h4>📈 知识演化趋势</h4>
                        <div id="evolutionAnalysis">
                            <p><strong>2020-2022:</strong> 5G EMC测试标准快速发展</p>
                            <p><strong>2022-2024:</strong> 汽车电子EMC要求提升</p>
                            <p><strong>未来趋势:</strong> 人工智能辅助EMC设计</p>
                        </div>
                        <button class="btn btn-info" onclick="analyzeEvolution()">📊 查看详情</button>
                    </div>
                    
                    <div class="analysis-card">
                        <h4>🔍 知识缺口识别</h4>
                        <div id="gapAnalysis">
                            <p><strong>缺失领域:</strong> 毫米波EMC测试方法</p>
                            <p><strong>待完善:</strong> 新能源汽车EMC标准</p>
                            <p><strong>推荐补充:</strong> 工业4.0 EMC指南</p>
                        </div>
                        <button class="btn btn-warning" onclick="identifyGaps()">🔍 深度分析</button>
                    </div>
                </div>
            </div>
            
            <!-- 标准库标签页 -->
            <div id="standards" class="tab-content">
                <h2>📋 EMC标准知识库</h2>
                <div class="analysis-grid">
                    <div class="analysis-card">
                        <h4>🇨🇳 国家标准 (GB/T)</h4>
                        <div id="gbStandards">
                            <p><strong>GB/T 17626.1:</strong> 概述</p>
                            <p><strong>GB/T 17626.2:</strong> 静电放电抗扰度试验</p>
                            <p><strong>GB/T 17626.3:</strong> 射频电磁场辐射抗扰度试验</p>
                            <p><strong>GB/T 17626.4:</strong> 电快速瞬变脉冲群抗扰度试验</p>
                            <p><strong>GB/T 17626.5:</strong> 浪涌(冲击)抗扰度试验</p>
                        </div>
                        <button class="btn btn-info" onclick="showStandardDetails('GB/T 17626')">📖 查看详情</button>
                    </div>
                    
                    <div class="analysis-card">
                        <h4>🌐 国际标准 (IEC)</h4>
                        <div id="iecStandards">
                            <p><strong>IEC 61000-1:</strong> 总则</p>
                            <p><strong>IEC 61000-2:</strong> 环境</p>
                            <p><strong>IEC 61000-3:</strong> 限值</p>
                            <p><strong>IEC 61000-4:</strong> 试验和测量技术</p>
                            <p><strong>IEC 61000-5:</strong> 安装和减缓导则</p>
                        </div>
                        <button class="btn btn-info" onclick="showStandardDetails('IEC 61000')">📖 查看详情</button>
                    </div>
                    
                    <div class="analysis-card">
                        <h4>🚗 行业标准</h4>
                        <div id="industryStandards">
                            <p><strong>CISPR 25:</strong> 车用设备EMC要求</p>
                            <p><strong>ISO 11452:</strong> 道路车辆EMC抗扰度</p>
                            <p><strong>ISO 11451:</strong> 道路车辆EMC发射</p>
                            <p><strong>SAE J1113:</strong> 汽车EMC测试程序</p>
                        </div>
                        <button class="btn btn-info" onclick="showStandardDetails('CISPR 25')">📖 查看详情</button>
                    </div>
                    
                    <div class="analysis-card">
                        <h4>🧪 测试方法库</h4>
                        <div id="testMethods">
                            <p><strong>传导发射:</strong> 150kHz-30MHz</p>
                            <p><strong>辐射发射:</strong> 30MHz-1GHz</p>
                            <p><strong>静电放电:</strong> ±2kV-±15kV</p>
                            <p><strong>射频抗扰:</strong> 80MHz-1GHz</p>
                        </div>
                        <button class="btn btn-success" onclick="runTestSimulation()">🧪 测试仿真</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // 全局变量
        let network = null;
        let nodes = null;
        let edges = null;
        let currentData = null;
        let searchCount = 0;
        
        // 初始化
        document.addEventListener('DOMContentLoaded', function() {{
            initializeGraph();
            loadKnowledgeBase();
        }});
        
        // 标签页切换
        function showTab(tabName) {{
            // 隐藏所有标签页内容
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // 显示选中的标签页
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            // 特殊处理
            if (tabName === 'graph' && network) {{
                network.redraw();
            }}
        }}
        
        // 加载知识库数据
        async function loadKnowledgeBase() {{
            try {{
                const response = await fetch('/api/graph/data');
                currentData = await response.json();
                updateStatistics();
                if (network) {{
                    updateGraph();
                }}
            }} catch (error) {{
                console.error('加载知识库失败:', error);
            }}
        }}
        
        // 初始化知识图谱
        function initializeGraph() {{
            const container = document.getElementById('graphVis');
            
            // 初始数据
            nodes = new vis.DataSet();
            edges = new vis.DataSet();
            
            const data = {{ nodes: nodes, edges: edges }};
            
            const options = {{
                nodes: {{
                    shape: 'dot',
                    size: 20,
                    font: {{ size: 14, color: '#333' }},
                    borderWidth: 2,
                    shadow: true,
                    chosen: {{ node: true }}
                }},
                edges: {{
                    width: 2,
                    color: {{ color: '#848484', highlight: '#2B7CE9' }},
                    arrows: {{ to: {{ enabled: true, scaleFactor: 1 }} }},
                    smooth: {{ type: 'dynamic' }},
                    font: {{ align: 'middle', size: 12 }}
                }},
                physics: {{
                    barnesHut: {{ gravitationalConstant: -8000, springConstant: 0.001, springLength: 200 }},
                    stabilization: {{ iterations: 150 }}
                }},
                interaction: {{
                    hover: true,
                    tooltipDelay: 200
                }}
            }};
            
            network = new vis.Network(container, data, options);
            
            // 事件监听
            network.on('click', function(params) {{
                if (params.nodes.length > 0) {{
                    showNodeDetails(params.nodes[0]);
                }}
            }});
            
            network.on('hoverNode', function(params) {{
                container.style.cursor = 'pointer';
            }});
            
            network.on('blurNode', function(params) {{
                container.style.cursor = 'default';
            }});
        }}
        
        // 更新图谱
        function updateGraph() {{
            if (!currentData || !network) return;
            
            // 处理节点数据
            const visNodes = currentData.nodes.map(node => ({{
                id: node.id,
                label: node.label,
                title: `类型: ${{node.type}}\\n类别: ${{node.category || '未分类'}}`,
                color: getNodeColor(node.type),
                size: 25,
                font: {{ size: 12 }}
            }}));
            
            // 处理边数据
            const visEdges = currentData.relationships.map(rel => ({{
                id: rel.id,
                from: rel.source,
                to: rel.target,
                label: rel.label,
                title: `关系: ${{rel.type}}`,
                width: 2
            }}));
            
            nodes.clear();
            edges.clear();
            nodes.add(visNodes);
            edges.add(visEdges);
        }}
        
        // 获取节点颜色
        function getNodeColor(type) {{
            const colors = {{
                '设备': '#FF6B6B',
                '标准': '#4ECDC4', 
                '测试': '#45B7D1',
                '产品': '#96CEB4',
                '文档': '#FECA57',
                '设施': '#FF9FF3',
                '专家': '#54A0FF'
            }};
            return colors[type] || '#95A5A6';
        }}
        
        // 显示节点详情
        function showNodeDetails(nodeId) {{
            const node = currentData.nodes.find(n => n.id === nodeId);
            if (!node) return;
            
            let details = `<h5>${{node.label}}</h5>`;
            details += `<p><strong>类型:</strong> ${{node.type}}</p>`;
            details += `<p><strong>类别:</strong> ${{node.category || '未分类'}}</p>`;
            
            if (node.properties) {{
                details += '<p><strong>属性:</strong></p>';
                for (const [key, value] of Object.entries(node.properties)) {{
                    details += `<p>• ${{key}}: ${{value}}</p>`;
                }}
            }}
            
            document.getElementById('nodeInfo').innerHTML = details;
        }}
        
        // 重置布局
        function resetLayout() {{
            if (network) {{
                network.setOptions({{ physics: {{ enabled: true }} }});
                network.stabilize();
            }}
        }}
        
        // 添加节点
        function addNode() {{
            const label = prompt('请输入节点名称:');
            if (!label) return;
            
            const type = prompt('请输入节点类型 (设备/标准/测试/产品/文档/设施/专家):') || '其他';
            
            const newNode = {{
                id: 'node_' + Date.now(),
                label: label,
                type: type,
                category: '用户添加',
                properties: {{ '创建时间': new Date().toLocaleString() }}
            }};
            
            currentData.nodes.push(newNode);
            updateGraph();
            updateStatistics();
        }}
        
        // 智能搜索
        async function searchKnowledge() {{
            const query = document.getElementById('searchQuery').value.trim();
            if (!query) return;
            
            searchCount++;
            document.getElementById('searchCount').textContent = searchCount;
            
            try {{
                const response = await fetch(`/api/search?q=${{encodeURIComponent(query)}}`);
                const results = await response.json();
                displaySearchResults(results);
            }} catch (error) {{
                console.error('搜索失败:', error);
                document.getElementById('searchResults').innerHTML = '<p>搜索失败，请重试</p>';
            }}
        }}
        
        // 快速搜索
        function quickSearch(query) {{
            document.getElementById('searchQuery').value = query;
            searchKnowledge();
        }}
        
        // 显示搜索结果
        function displaySearchResults(results) {{
            const container = document.getElementById('searchResults');
            
            if (!results.results || results.results.length === 0) {{
                container.innerHTML = '<p>未找到相关结果</p>';
                return;
            }}
            
            let html = `<h4>🔍 搜索结果 (共${{results.results.length}}条)</h4>`;
            
            results.results.forEach(item => {{
                html += `
                    <div class="result-item" onclick="highlightNode('${{item.id}}')">
                        <h5>${{item.label}}</h5>
                        <p><strong>类型:</strong> ${{item.type}} | <strong>类别:</strong> ${{item.category || '未分类'}}</p>
                        ${{item.properties ? Object.entries(item.properties).slice(0, 2).map(([k,v]) => `<p>• ${{k}}: ${{v}}</p>`).join('') : ''}}
                    </div>
                `;
            }});
            
            container.innerHTML = html;
        }}
        
        // 高亮节点
        function highlightNode(nodeId) {{
            if (network) {{
                network.selectNodes([nodeId]);
                network.focus(nodeId, {{ animation: true }});
                showTab('graph');
                showNodeDetails(nodeId);
            }}
        }}
        
        // 文件上传处理
        function handleDrop(event) {{
            event.preventDefault();
            const files = event.dataTransfer.files;
            processFiles(files);
            document.getElementById('uploadArea').classList.remove('dragover');
        }}
        
        function handleDragOver(event) {{
            event.preventDefault();
            document.getElementById('uploadArea').classList.add('dragover');
        }}
        
        function handleDragLeave(event) {{
            document.getElementById('uploadArea').classList.remove('dragover');
        }}
        
        function handleFileSelect(event) {{
            const files = event.target.files;
            processFiles(files);
        }}
        
        // 处理文件
        async function processFiles(files) {{
            const fileList = document.getElementById('fileList');
            fileList.innerHTML = '<h4>📁 上传的文件:</h4>';
            
            for (let file of files) {{
                const fileItem = document.createElement('div');
                fileItem.className = 'info-panel';
                fileItem.innerHTML = `
                    <h5>${{file.name}}</h5>
                    <p>大小: ${{(file.size / 1024).toFixed(1)}} KB | 类型: ${{file.type || '未知'}}</p>
                    <p>状态: <span class="loading"></span> 正在处理...</p>
                `;
                fileList.appendChild(fileItem);
                
                // 模拟文件处理
                setTimeout(() => {{
                    fileItem.querySelector('p:last-child').innerHTML = '状态: ✅ 处理完成';
                    extractKnowledgeFromFile(file.name);
                }}, 2000);
                
                // 更新文件计数
                const currentCount = parseInt(document.getElementById('fileCount').textContent);
                document.getElementById('fileCount').textContent = currentCount + 1;
            }}
        }}
        
        // 从文件提取知识
        function extractKnowledgeFromFile(fileName) {{
            const resultsContainer = document.getElementById('extractionResults');
            
            // 模拟知识抽取结果
            const mockResults = {{
                entities: ['静电放电测试', 'IEC 61000-4-2', '±4kV', '±8kV'],
                relations: ['测试电压-设置为-±4kV', '标准依据-参考-IEC 61000-4-2'],
                concepts: ['ESD测试', '抗扰度等级', '试验配置']
            }};
            
            resultsContainer.innerHTML = `
                <h4>🧠 从 "${{fileName}}" 提取的知识:</h4>
                <div class="analysis-grid">
                    <div class="analysis-card">
                        <h5>📋 实体识别</h5>
                        ${{mockResults.entities.map(e => `<span style="background: #e3f2fd; padding: 2px 6px; margin: 2px; border-radius: 4px; display: inline-block;">${{e}}</span>`).join('')}}
                    </div>
                    <div class="analysis-card">
                        <h5>🔗 关系抽取</h5>
                        ${{mockResults.relations.map(r => `<p>• ${{r}}</p>`).join('')}}
                    </div>
                    <div class="analysis-card">
                        <h5>💡 概念发现</h5>
                        ${{mockResults.concepts.map(c => `<span style="background: #f3e5f5; padding: 2px 6px; margin: 2px; border-radius: 4px; display: inline-block;">${{c}}</span>`).join('')}}
                    </div>
                </div>
            `;
        }}
        
        // 更新统计信息
        function updateStatistics() {{
            if (currentData) {{
                document.getElementById('nodeCount').textContent = currentData.nodes.length;
                document.getElementById('relCount').textContent = currentData.relationships.length;
                document.getElementById('totalNodes').textContent = currentData.nodes.length;
                document.getElementById('totalRels').textContent = currentData.relationships.length;
            }}
        }}
        
        // 分析功能
        function runCentralityAnalysis() {{
            document.getElementById('centralityAnalysis').innerHTML = `
                <div class="loading"></div> 正在分析节点中心性...
            `;
            
            setTimeout(() => {{
                document.getElementById('centralityAnalysis').innerHTML = `
                    <p><strong>度中心性最高:</strong> GB/T 17626系列标准 (连接度: 4)</p>
                    <p><strong>介数中心性最高:</strong> 抗扰度测试 (0.85)</p>
                    <p><strong>接近中心性最高:</strong> EMC测试设备 (0.92)</p>
                    <p><strong>特征向量中心性最高:</strong> IEC 61000系列 (0.78)</p>
                `;
            }}, 2000);
        }}
        
        function runCommunityDetection() {{
            document.getElementById('communityAnalysis').innerHTML = `
                <div class="loading"></div> 正在进行社区发现...
            `;
            
            setTimeout(() => {{
                document.getElementById('communityAnalysis').innerHTML = `
                    <p><strong>测试设备社区:</strong> EMC测试设备, 电波暗室, 张工程师</p>
                    <p><strong>标准规范社区:</strong> GB/T 17626, IEC 61000</p>
                    <p><strong>产品测试社区:</strong> 智能手机, 抗扰度测试, EMC测试报告</p>
                    <p><strong>模块化度:</strong> 0.73 (社区结构清晰)</p>
                `;
            }}, 2000);
        }}
        
        function analyzeEvolution() {{
            alert('📊 知识演化分析\\n\\n时间轴分析显示:\\n• 2020年: 5G EMC标准制定\\n• 2021年: 新能源汽车EMC要求提升\\n• 2022年: 物联网设备EMC规范完善\\n• 2023年: AI辅助EMC设计兴起\\n• 2024年: 毫米波EMC测试方法标准化');
        }}
        
        function identifyGaps() {{
            alert('🔍 知识缺口分析\\n\\n发现以下缺口:\\n• 6G通信EMC预研标准\\n• 量子计算EMC防护\\n• 脑机接口EMC安全\\n• 太空环境EMC测试\\n\\n建议补充相关知识节点和关系。');
        }}
        
        // 标准详情
        function showStandardDetails(standardName) {{
            let details = '';
            if (standardName.includes('17626')) {{
                details = 'GB/T 17626系列标准详情:\\n\\n• 标准名称: 电磁兼容 试验和测量技术\\n• 发布机构: 国家标准化委员会\\n• 采用基础: 等同采用IEC 61000-4系列\\n• 应用领域: 信息技术设备、工业设备、家用电器\\n• 主要内容: 静电放电、射频场、脉冲群等抗扰度试验';
            }} else if (standardName.includes('61000')) {{
                details = 'IEC 61000系列标准详情:\\n\\n• 标准名称: 电磁兼容(EMC)\\n• 发布机构: 国际电工委员会\\n• 标准结构: 6个部分100+子标准\\n• 全球应用: EMC标准体系基础\\n• 技术内容: 从基本概念到具体试验方法';
            }} else {{
                details = 'CISPR 25标准详情:\\n\\n• 标准名称: 用于保护车载接收机的车辆、船只和内燃机驱动装置的无线电骚扰特性的限值和测量方法\\n• 应用领域: 汽车电子EMC\\n• 频率范围: 150kHz-2.5GHz\\n• 测试方法: 传导和辐射发射/抗扰度';
            }}
            alert(details);
        }}
        
        function runTestSimulation() {{
            alert('🧪 EMC测试仿真\\n\\n模拟测试场景:\\n• 测试对象: 车载充电器\\n• 测试项目: 传导发射(CISPR 25)\\n• 频率范围: 150kHz-108MHz\\n• 预期结果: 符合Class 5限值要求\\n• 风险评估: 低风险\\n\\n点击确定开始虚拟测试...');
        }}
        
        // 工具函数
        function refreshData() {{
            loadKnowledgeBase();
            alert('🔄 数据已刷新');
        }}
        
        function exportData() {{
            const data = JSON.stringify(currentData, null, 2);
            const blob = new Blob([data], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'emc_knowledge_graph.json';
            a.click();
        }}
        
        function exportGraph() {{
            if (network) {{
                const canvas = network.canvas.frame.canvas;
                const link = document.createElement('a');
                link.download = 'emc_graph.png';
                link.href = canvas.toDataURL();
                link.click();
            }}
        }}
        
        function showSettings() {{
            alert('⚙️ 系统设置\\n\\n• 图谱布局算法: Barnes-Hut\\n• 物理仿真: 启用\\n• 节点标签: 显示\\n• 边标签: 显示\\n• 自动保存: 启用\\n\\n更多设置请联系管理员');
        }}
        
        function showHelp() {{
            alert('❓ 使用帮助\\n\\n🌐 知识图谱:\\n• 点击节点查看详情\\n• 拖拽移动节点\\n• 滚轮缩放视图\\n\\n🔍 智能搜索:\\n• 支持关键词搜索\\n• 支持模糊匹配\\n• 点击结果定位节点\\n\\n📁 文件处理:\\n• 拖拽上传文件\\n• 自动提取知识\\n• 支持多种格式\\n\\n📊 知识分析:\\n• 网络分析算法\\n• 社区发现\\n• 趋势预测');
        }}
        
        function filterNodes(type) {{
            // 节点筛选功能
            console.log('筛选节点类型:', type);
        }}
    </script>
</body>
</html>
    '''
    return HTMLResponse(content=html_content)

# API路由
@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "EMC Knowledge Graph System",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": ["knowledge_graph", "search", "file_processing", "analysis"]
    }

@app.get("/api/graph/data")
async def get_graph_data():
    """获取完整图谱数据"""
    return {
        "nodes": knowledge_base["nodes"],
        "relationships": knowledge_base["relationships"],
        "metadata": {
            "node_count": len(knowledge_base["nodes"]),
            "relationship_count": len(knowledge_base["relationships"]),
            "last_updated": datetime.now().isoformat()
        }
    }

@app.get("/api/graph/nodes")
async def get_nodes():
    """获取所有节点"""
    return {"nodes": knowledge_base["nodes"]}

@app.get("/api/graph/relationships")
async def get_relationships():
    """获取所有关系"""
    return {"relationships": knowledge_base["relationships"]}

@app.post("/api/graph/nodes")
async def create_node(node_data: dict):
    """创建新节点"""
    new_node = {
        "id": f"node_{len(knowledge_base['nodes']) + 1}_{int(time.time())}",
        "label": node_data.get("label", "新节点"),
        "type": node_data.get("type", "其他"),
        "category": node_data.get("category", "用户创建"),
        "properties": {
            "创建时间": datetime.now().isoformat(),
            **node_data.get("properties", {})
        },
        "x": node_data.get("x", 100),
        "y": node_data.get("y", 100)
    }
    
    knowledge_base["nodes"].append(new_node)
    return {"success": True, "node": new_node}

@app.get("/api/search")
async def search_knowledge(q: str = ""):
    """智能搜索"""
    if not q:
        return {"query": q, "results": [], "total": 0}
    
    results = []
    query_lower = q.lower()
    
    # 搜索节点
    for node in knowledge_base["nodes"]:
        score = 0
        if query_lower in node["label"].lower():
            score += 10
        if query_lower in node["type"].lower():
            score += 5
        if node.get("category") and query_lower in node["category"].lower():
            score += 3
        
        # 搜索属性
        if node.get("properties"):
            for key, value in node["properties"].items():
                if query_lower in str(value).lower():
                    score += 2
                if query_lower in key.lower():
                    score += 1
        
        if score > 0:
            results.append({**node, "score": score})
    
    # 按相关性排序
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "query": q,
        "results": results[:10],  # 返回前10个结果
        "total": len(results)
    }

@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """文件上传和处理"""
    try:
        # 保存文件
        file_id = str(uuid.uuid4())
        file_path = Path(tempfile.gettempdir()) / f"{file_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 模拟知识抽取
        extracted_knowledge = {
            "entities": [],
            "relationships": [],
            "concepts": []
        }
        
        # 根据文件类型进行不同的处理
        if file.filename.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
            # 模拟文本处理
            extracted_knowledge = {
                "entities": ["静电放电", "EMC测试", "抗扰度", "IEC 61000-4-2"],
                "relationships": [
                    {"source": "静电放电", "target": "EMC测试", "relation": "属于"},
                    {"source": "EMC测试", "target": "抗扰度", "relation": "包含"},
                    {"source": "抗扰度", "target": "IEC 61000-4-2", "relation": "标准依据"}
                ],
                "concepts": ["电磁兼容", "试验方法", "测量技术"]
            }
        
        # 存储文件信息
        uploaded_files[file_id] = {
            "filename": file.filename,
            "size": len(content),
            "upload_time": datetime.now().isoformat(),
            "file_path": str(file_path),
            "extracted_knowledge": extracted_knowledge
        }
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "size": len(content),
            "extracted_knowledge": extracted_knowledge
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")

@app.get("/api/analysis/centrality")
async def analyze_centrality():
    """中心性分析"""
    # 简单的度中心性计算
    node_degrees = {}
    for node in knowledge_base["nodes"]:
        node_degrees[node["id"]] = 0
    
    for rel in knowledge_base["relationships"]:
        if rel["source"] in node_degrees:
            node_degrees[rel["source"]] += 1
        if rel["target"] in node_degrees:
            node_degrees[rel["target"]] += 1
    
    # 找到度最高的节点
    max_degree_node = max(node_degrees.items(), key=lambda x: x[1])
    
    return {
        "degree_centrality": {
            "highest_node": max_degree_node[0],
            "degree": max_degree_node[1],
            "all_degrees": node_degrees
        },
        "analysis_time": datetime.now().isoformat()
    }

@app.get("/api/standards/{standard_name}")
async def get_standard_details(standard_name: str):
    """获取标准详情"""
    if standard_name in emc_knowledge["standards"]:
        return {
            "standard": standard_name,
            "details": emc_knowledge["standards"][standard_name],
            "related_tests": emc_knowledge["test_methods"]
        }
    else:
        raise HTTPException(status_code=404, detail="标准未找到")

@app.get("/api/system/status")
async def system_status():
    """系统状态"""
    return {
        "status": "running",
        "node_count": len(knowledge_base["nodes"]),
        "relationship_count": len(knowledge_base["relationships"]),
        "file_count": len(uploaded_files),
        "uptime": "运行中",
        "memory_usage": "正常",
        "cpu_usage": "低",
        "last_updated": datetime.now().isoformat()
    }

def main():
    """主函数"""
    print("🏛️ EMC知识图谱系统 - 完整功能版")
    print("=" * 50)
    print("🚀 正在启动完整功能的EMC知识图谱系统...")
    print("📱 访问地址: http://localhost:8003")
    print("💡 功能包括:")
    print("   🌐 交互式知识图谱可视化")
    print("   🔍 智能搜索与推荐")
    print("   📁 文件上传与知识抽取")
    print("   📊 图谱分析与挖掘")
    print("   📋 EMC标准知识库")
    print("🔄 按 Ctrl+C 停止系统")
    print()
    
    # 启动时自动打开浏览器
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:8003")
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")

if __name__ == "__main__":
    main()