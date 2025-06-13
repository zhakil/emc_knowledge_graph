#!/usr/bin/env python3
"""
EMC知识图谱系统 - Web启动器
临时解决方案，提供Web界面控制
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import subprocess
import sys
import os
import signal
import time
from pathlib import Path

app = FastAPI(title="EMC知识图谱系统控制台", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局进程管理
backend_process = None

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """主控制台页面"""
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EMC知识图谱系统控制台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1000px; margin: 0 auto; }
        .header { 
            background: rgba(255,255,255,0.95); 
            padding: 30px; 
            border-radius: 15px; 
            margin-bottom: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        .title { 
            font-size: 2.5em; 
            color: #2c3e50; 
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { 
            background: rgba(255,255,255,0.95); 
            padding: 25px; 
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .status { 
            background: #e8f5e8; 
            padding: 15px; 
            border-radius: 10px; 
            margin: 15px 0;
            text-align: center;
            font-weight: bold;
        }
        .btn { 
            display: inline-block;
            padding: 12px 24px; 
            margin: 8px; 
            background: linear-gradient(45deg, #007bff, #0056b3); 
            color: white; 
            text-decoration: none; 
            border: none;
            border-radius: 25px; 
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
            font-weight: bold;
        }
        .btn:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 8px 25px rgba(0,123,255,0.4); 
        }
        .btn-success { background: linear-gradient(45deg, #28a745, #20c997); }
        .btn-warning { background: linear-gradient(45deg, #ffc107, #fd7e14); }
        .btn-danger { background: linear-gradient(45deg, #dc3545, #c82333); }
        .btn-info { background: linear-gradient(45deg, #17a2b8, #138496); }
        
        .links { margin: 20px 0; }
        .links a { display: block; margin: 10px 0; }
        
        #log { 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 8px; 
            height: 200px; 
            overflow-y: auto; 
            font-family: monospace; 
            font-size: 12px;
            border: 1px solid #dee2e6;
        }
        
        .refresh { margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">🏛️ EMC知识图谱系统</h1>
            <p style="font-size: 1.2em; color: #666;">控制台 - 管理和监控系统服务</p>
            <div class="status" id="status">🔴 检查系统状态中...</div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🎛️ 系统控制</h3>
                <div style="text-align: center; margin: 20px 0;">
                    <button class="btn btn-success" onclick="startSystem()">🚀 启动后端</button>
                    <button class="btn btn-danger" onclick="stopSystem()">🛑 停止后端</button>
                    <button class="btn btn-info" onclick="checkStatus()">🔄 检查状态</button>
                </div>
                
                <h4>📱 快速访问</h4>
                <div class="links">
                    <a href="/docs" class="btn btn-info" target="_blank">📊 API文档</a>
                    <a href="/health" class="btn btn-success" target="_blank">⚡ 健康检查</a>
                    <a href="/demo" class="btn btn-warning" target="_blank">🎨 演示页面</a>
                </div>
            </div>
            
            <div class="card">
                <h3>📋 系统日志</h3>
                <div class="refresh">
                    <button class="btn" onclick="refreshLog()" style="padding: 8px 16px; font-size: 12px;">🔄 刷新日志</button>
                </div>
                <div id="log">正在加载日志...</div>
            </div>
        </div>
        
        <div class="card" style="margin-top: 20px;">
            <h3>💡 使用说明</h3>
            <ul style="line-height: 1.8; margin-left: 20px;">
                <li><strong>启动后端</strong>：点击"启动后端"按钮启动API服务</li>
                <li><strong>访问系统</strong>：后端启动后可通过上方链接访问各功能</li>
                <li><strong>查看日志</strong>：右侧显示系统运行日志和状态</li>
                <li><strong>演示模式</strong>：无需启动后端也可查看系统演示</li>
            </ul>
        </div>
    </div>
    
    <script>
        async function makeRequest(url, method = 'GET') {
            try {
                const response = await fetch(url, { method });
                const data = await response.json();
                return { success: true, data };
            } catch (error) {
                return { success: false, error: error.message };
            }
        }
        
        async function startSystem() {
            updateStatus('🟡 正在启动后端服务...');
            const result = await makeRequest('/api/start', 'POST');
            if (result.success) {
                updateStatus('🟢 后端服务已启动');
                addLog('✅ 后端服务启动成功');
            } else {
                updateStatus('🔴 启动失败');
                addLog('❌ 启动失败: ' + result.error);
            }
        }
        
        async function stopSystem() {
            updateStatus('🟡 正在停止服务...');
            const result = await makeRequest('/api/stop', 'POST');
            if (result.success) {
                updateStatus('🔴 服务已停止');
                addLog('🛑 服务已停止');
            } else {
                addLog('⚠️ 停止过程中出现问题: ' + result.error);
            }
        }
        
        async function checkStatus() {
            const result = await makeRequest('/api/status');
            if (result.success) {
                const status = result.data.status;
                if (status === 'running') {
                    updateStatus('🟢 系统运行中');
                } else {
                    updateStatus('🔴 系统未运行');
                }
                addLog('📊 状态检查: ' + status);
            } else {
                updateStatus('❓ 状态未知');
                addLog('❌ 状态检查失败');
            }
        }
        
        function updateStatus(message) {
            document.getElementById('status').textContent = message;
        }
        
        function addLog(message) {
            const log = document.getElementById('log');
            const time = new Date().toLocaleTimeString();
            log.innerHTML += `[${time}] ${message}\\n`;
            log.scrollTop = log.scrollHeight;
        }
        
        function refreshLog() {
            document.getElementById('log').innerHTML = '日志已清空\\n';
            addLog('🔄 日志已刷新');
        }
        
        // 页面加载时检查状态
        window.onload = function() {
            addLog('🏛️ EMC知识图谱系统控制台已加载');
            checkStatus();
            
            // 定期检查状态
            setInterval(checkStatus, 30000);
        };
    </script>
</body>
</html>
    """)

@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """演示页面"""
    try:
        demo_file = Path("standalone-demo.html")
        if demo_file.exists():
            return HTMLResponse(demo_file.read_text(encoding='utf-8'))
        else:
            return HTMLResponse("<h1>演示页面不可用</h1><p>找不到 standalone-demo.html 文件</p>")
    except Exception as e:
        return HTMLResponse(f"<h1>错误</h1><p>{str(e)}</p>")

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy", "service": "EMC Knowledge Graph Launcher", "version": "1.0.0"}

@app.get("/api/status")
async def get_status():
    """获取系统状态"""
    global backend_process
    if backend_process and backend_process.poll() is None:
        return {"status": "running", "pid": backend_process.pid}
    else:
        return {"status": "stopped"}

@app.post("/api/start")
async def start_backend():
    """启动后端服务"""
    global backend_process
    
    try:
        # 停止现有进程
        if backend_process and backend_process.poll() is None:
            backend_process.terminate()
            time.sleep(2)
        
        # 创建简化后端
        backend_code = '''
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="EMC知识图谱API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"message": "EMC知识图谱API正在运行", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "EMC Knowledge Graph"}

@app.get("/api/system/status")
async def system_status():
    return {"status": "running", "nodes": 6, "relationships": 5}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
'''
        
        backend_file = Path("/tmp/emc_backend_api.py")
        backend_file.write_text(backend_code)
        
        # 启动后端进程
        backend_process = subprocess.Popen([sys.executable, str(backend_file)])
        
        return {"success": True, "message": "后端服务已启动", "pid": backend_process.pid}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/stop")
async def stop_backend():
    """停止后端服务"""
    global backend_process
    
    try:
        if backend_process and backend_process.poll() is None:
            backend_process.terminate()
            backend_process.wait(timeout=5)
            backend_process = None
            return {"success": True, "message": "服务已停止"}
        else:
            return {"success": True, "message": "服务未在运行"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def cleanup():
    """清理函数"""
    global backend_process
    if backend_process and backend_process.poll() is None:
        backend_process.terminate()

# 注册清理函数
import atexit
atexit.register(cleanup)

def signal_handler(signum, frame):
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    print("🏛️ EMC知识图谱系统 - Web控制台")
    print("=" * 40)
    print("🌐 启动Web控制台...")
    print("📱 访问地址: http://localhost:8001")
    print("💡 在浏览器中打开上述地址进行控制")
    print("🔄 按 Ctrl+C 停止")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")