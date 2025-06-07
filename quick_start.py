#!/usr/bin/env python3
"""
EMC知识图谱系统 - 最简运行脚本
一键启动，无需复杂配置
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并显示输出"""
    print(f"🔧 执行: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 失败: {e}")
        return False

def main():
    print("🚀 EMC知识图谱系统 - 快速启动")
    print("=" * 50)
    
    project_dir = Path(__file__).parent
    
    # 1. 安装Python依赖
    print("\n📦 安装依赖...")
    if not run_command("pip install fastapi uvicorn python-multipart aiofiles", project_dir):
        print("依赖安装失败，但继续尝试...")
    
    # 2. 启动简化后端
    print("\n🔧 启动后端服务...")
    backend_process = subprocess.Popen([
        sys.executable, "-c", """
import sys
sys.path.append('.')

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime

app = FastAPI(title="EMC知识图谱API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "EMC知识图谱系统", "status": "运行中", "time": datetime.now()}

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/api/test")
def test():
    return {"message": "API测试成功", "backend": "简化版后端"}

@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "size": file.size,
        "type": file.content_type,
        "status": "uploaded",
        "message": "文件上传成功（演示版）"
    }

@app.get("/api/graph/data")
def get_graph():
    return {
        "nodes": [
            {"id": "1", "label": "EMC标准", "type": "standard"},
            {"id": "2", "label": "测试设备", "type": "equipment"}
        ],
        "edges": [
            {"source": "1", "target": "2", "type": "uses"}
        ]
    }

if __name__ == "__main__":
    print("🔧 EMC后端服务启动 - http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
    ], cwd=project_dir)
    
    # 3. 等待后端启动
    print("⏳ 等待后端启动...")
    time.sleep(3)
    
    # 4. 启动前端（如果存在）
    frontend_dir = project_dir / "frontend"
    if frontend_dir.exists():
        print("\n🎨 启动前端...")
        subprocess.Popen(["npm", "start"], cwd=frontend_dir)
        time.sleep(5)
        webbrowser.open("http://localhost:3000")
    else:
        # 创建简单HTML页面
        print("\n🌐 创建简单前端页面...")
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>EMC知识图谱系统</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        button:hover { background: #0056b3; }
        #result { background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 EMC知识图谱系统</h1>
            <p>电磁兼容性知识管理平台</p>
        </div>
        
        <div class="section">
            <h3>📡 API测试</h3>
            <button onclick="testAPI()">测试后端连接</button>
            <button onclick="getGraph()">获取图数据</button>
            <div id="result"></div>
        </div>
        
        <div class="section">
            <h3>📁 文件上传</h3>
            <input type="file" id="fileInput" accept=".pdf,.doc,.docx,.csv">
            <button onclick="uploadFile()">上传文件</button>
        </div>
        
        <div class="section">
            <h3>🔗 系统链接</h3>
            <a href="http://localhost:8000/docs" target="_blank">
                <button>API文档</button>
            </a>
            <a href="http://localhost:8000/health" target="_blank">
                <button>健康检查</button>
            </a>
        </div>
    </div>

    <script>
        async function testAPI() {
            try {
                const response = await fetch('http://localhost:8000/api/test');
                const data = await response.json();
                document.getElementById('result').innerHTML = 
                    '<strong>✅ API连接成功!</strong><br>' + JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById('result').innerHTML = 
                    '<strong>❌ API连接失败:</strong> ' + error.message;
            }
        }
        
        async function getGraph() {
            try {
                const response = await fetch('http://localhost:8000/api/graph/data');
                const data = await response.json();
                document.getElementById('result').innerHTML = 
                    '<strong>📊 图数据获取成功!</strong><br>' + JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById('result').innerHTML = 
                    '<strong>❌ 获取失败:</strong> ' + error.message;
            }
        }
        
        async function uploadFile() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            if (!file) {
                alert('请选择文件');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('http://localhost:8000/api/files/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                document.getElementById('result').innerHTML = 
                    '<strong>📁 文件上传成功!</strong><br>' + JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById('result').innerHTML = 
                    '<strong>❌ 上传失败:</strong> ' + error.message;
            }
        }
    </script>
</body>
</html>
        """
        
        html_file = project_dir / "index.html"
        html_file.write_text(html_content, encoding='utf-8')
        
        webbrowser.open(f"file://{html_file.absolute()}")
    
    print("\n🎉 启动完成!")
    print("📋 访问地址:")
    print("  - 前端界面: http://localhost:3000 或 file://index.html")
    print("  - API文档: http://localhost:8000/docs")
    print("  - 健康检查: http://localhost:8000/health")
    print("\n💡 按 Ctrl+C 停止服务")
    
    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n🔄 正在停止服务...")
        backend_process.terminate()

if __name__ == "__main__":
    main()