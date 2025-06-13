#!/usr/bin/env python3
"""
EMC知识图谱系统 - Windows桌面应用
使用webview库创建原生窗口，内部使用Web技术
"""

try:
    import webview
except ImportError:
    print("正在安装webview库...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview"])
    import webview

import threading
import time
import subprocess
import sys
import os
import tempfile
from pathlib import Path
import webbrowser
import json
import socket

class EMCDesktopApp:
    def __init__(self):
        self.backend_process = None
        self.backend_port = 8002
        self.window = None
        
    def find_free_port(self, start_port=8002):
        """找到可用端口"""
        for port in range(start_port, start_port + 10):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('localhost', port))
                sock.close()
                return port
            except:
                continue
        return start_port

    def create_backend_service(self):
        """创建后端服务代码"""
        backend_code = '''
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import json
import asyncio
from datetime import datetime

app = FastAPI(title="EMC知识图谱API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟数据
demo_nodes = [
    {"id": "1", "label": "EMC测试设备", "type": "设备", "x": 100, "y": 100},
    {"id": "2", "label": "GB/T 17626", "type": "标准", "x": 300, "y": 100},
    {"id": "3", "label": "抗扰度测试", "type": "测试", "x": 200, "y": 200},
    {"id": "4", "label": "合格报告", "type": "结果", "x": 200, "y": 300},
    {"id": "5", "label": "手机", "type": "产品", "x": 50, "y": 250},
    {"id": "6", "label": "IEC 61000", "type": "标准", "x": 350, "y": 200},
]

demo_links = [
    {"source": "1", "target": "3", "label": "执行"},
    {"source": "2", "target": "3", "label": "依据"},
    {"source": "3", "target": "4", "label": "产生"},
    {"source": "5", "target": "3", "label": "被测试"},
    {"source": "6", "target": "2", "label": "参考"},
]

@app.get("/")
async def root():
    return {"message": "EMC知识图谱API正在运行", "status": "healthy", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "EMC Knowledge Graph", "timestamp": datetime.now().isoformat()}

@app.get("/api/system/status")
async def system_status():
    return {
        "status": "running", 
        "nodes": len(demo_nodes), 
        "relationships": len(demo_links),
        "version": "1.0.0",
        "uptime": "0:05:23"
    }

@app.get("/api/system/statistics")
async def system_statistics():
    return {
        "total_nodes": 150,
        "total_relationships": 300,
        "entities_extracted": 75,
        "last_updated": datetime.now().isoformat(),
        "database_size": "2.3 MB",
        "active_sessions": 1
    }

@app.get("/api/system/activities")
async def system_activities():
    return {
        "recent_activities": [
            {"time": datetime.now().strftime("%H:%M"), "action": "系统启动", "user": "system", "status": "success"},
            {"time": "10:25", "action": "知识图谱构建", "user": "admin", "status": "completed"},
            {"time": "10:20", "action": "数据导入", "user": "user1", "status": "success"},
            {"time": "10:15", "action": "用户登录", "user": "admin", "status": "success"},
            {"time": "10:10", "action": "系统初始化", "user": "system", "status": "completed"}
        ]
    }

@app.get("/api/graph/nodes")
async def get_nodes():
    return {"nodes": demo_nodes}

@app.get("/api/graph/links") 
async def get_links():
    return {"links": demo_links}

@app.get("/api/graph/data")
async def get_graph_data():
    return {"nodes": demo_nodes, "links": demo_links}

@app.post("/api/graph/nodes")
async def create_node(node_data: dict):
    new_node = {
        "id": str(len(demo_nodes) + 1),
        "label": node_data.get("label", "新节点"),
        "type": node_data.get("type", "未知"),
        "x": node_data.get("x", 100),
        "y": node_data.get("y", 100)
    }
    demo_nodes.append(new_node)
    return {"success": True, "node": new_node}

@app.get("/api/search")
async def search_knowledge(q: str = ""):
    results = []
    if q:
        for node in demo_nodes:
            if q.lower() in node["label"].lower() or q.lower() in node["type"].lower():
                results.append(node)
    return {"query": q, "results": results, "total": len(results)}

if __name__ == "__main__":
    print("🚀 EMC知识图谱API服务启动...")
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="warning")
'''
        return backend_code

    def start_backend(self):
        """启动后端服务"""
        try:
            self.backend_port = self.find_free_port()
            
            # 创建后端代码
            backend_code = self.create_backend_service()
            backend_code = backend_code.replace('port=8002', f'port={self.backend_port}')
            
            # 写入临时文件
            backend_file = Path(tempfile.gettempdir()) / "emc_api_service.py"
            backend_file.write_text(backend_code, encoding='utf-8')
            
            # 启动后端进程
            self.backend_process = subprocess.Popen([
                sys.executable, str(backend_file)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return True
            
        except Exception as e:
            print(f"启动后端失败: {e}")
            return False

    def stop_backend(self):
        """停止后端服务"""
        if self.backend_process and self.backend_process.poll() is None:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            self.backend_process = None

    def create_app_html(self):
        """创建应用界面HTML"""
        return f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EMC知识图谱系统</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            overflow: hidden;
        }}
        
        .titlebar {{ 
            background: rgba(0,0,0,0.8); 
            color: white; 
            padding: 8px 15px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            -webkit-app-region: drag;
            user-select: none;
        }}
        .titlebar .title {{ font-weight: bold; }}
        .titlebar .controls {{ -webkit-app-region: no-drag; }}
        .titlebar .controls button {{ 
            background: none; 
            border: none; 
            color: white; 
            padding: 4px 8px; 
            cursor: pointer; 
            border-radius: 3px;
        }}
        .titlebar .controls button:hover {{ background: rgba(255,255,255,0.2); }}
        
        .container {{ 
            height: calc(100vh - 40px); 
            display: flex; 
            flex-direction: column; 
            padding: 20px; 
        }}
        
        .header {{ 
            background: rgba(255,255,255,0.95); 
            padding: 20px; 
            border-radius: 12px; 
            margin-bottom: 15px;
            text-align: center;
            backdrop-filter: blur(10px);
        }}
        .title-main {{ 
            font-size: 1.8em; 
            color: #2c3e50; 
            margin-bottom: 8px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .subtitle {{ color: #666; margin-bottom: 15px; }}
        .status {{ 
            padding: 8px 15px; 
            border-radius: 20px; 
            font-weight: bold;
            display: inline-block;
        }}
        .status.running {{ background: linear-gradient(45deg, #28a745, #20c997); color: white; }}
        .status.stopped {{ background: linear-gradient(45deg, #dc3545, #c82333); color: white; }}
        
        .main-content {{ 
            flex: 1; 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 15px; 
        }}
        
        .card {{ 
            background: rgba(255,255,255,0.95); 
            padding: 20px; 
            border-radius: 12px;
            backdrop-filter: blur(10px);
            display: flex;
            flex-direction: column;
        }}
        .card h3 {{ color: #2c3e50; margin-bottom: 15px; }}
        
        .btn {{ 
            padding: 10px 20px; 
            margin: 5px; 
            color: white; 
            border: none;
            border-radius: 20px; 
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: bold;
            font-size: 14px;
        }}
        .btn:hover {{ transform: translateY(-1px); box-shadow: 0 4px 15px rgba(0,0,0,0.3); }}
        .btn-primary {{ background: linear-gradient(45deg, #007bff, #0056b3); }}
        .btn-success {{ background: linear-gradient(45deg, #28a745, #20c997); }}
        .btn-danger {{ background: linear-gradient(45deg, #dc3545, #c82333); }}
        .btn-info {{ background: linear-gradient(45deg, #17a2b8, #138496); }}
        .btn:disabled {{ opacity: 0.6; cursor: not-allowed; transform: none; }}
        
        .control-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 15px; }}
        .links {{ margin-top: 10px; }}
        .links a {{ display: block; margin: 5px 0; text-align: center; text-decoration: none; }}
        
        .stats {{ 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 10px; 
            margin-bottom: 15px; 
        }}
        .stat-item {{ 
            background: #f8f9fa; 
            padding: 10px; 
            border-radius: 8px; 
            text-align: center;
        }}
        .stat-number {{ font-size: 1.5em; font-weight: bold; color: #007bff; }}
        .stat-label {{ color: #666; font-size: 0.85em; }}
        
        .log-container {{ 
            flex: 1;
            background: #2c3e50; 
            color: #ecf0f1; 
            padding: 15px; 
            border-radius: 8px; 
            overflow-y: auto; 
            font-family: 'Consolas', monospace; 
            font-size: 12px;
            line-height: 1.3;
        }}
        .log-entry {{ margin: 2px 0; }}
        .log-entry.success {{ color: #2ecc71; }}
        .log-entry.error {{ color: #e74c3c; }}
        .log-entry.warning {{ color: #f39c12; }}
        .log-entry.info {{ color: #3498db; }}
        
        .footer {{ 
            margin-top: 15px; 
            text-align: center; 
            background: rgba(255,255,255,0.1); 
            padding: 10px; 
            border-radius: 8px; 
            color: white; 
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        .pulsing {{ animation: pulse 2s infinite; }}
        
        /* 滚动条样式 */
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: rgba(255,255,255,0.1); }}
        ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.5); border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="titlebar">
        <div class="title">🏛️ EMC知识图谱系统</div>
        <div class="controls">
            <button onclick="minimizeWindow()">－</button>
            <button onclick="closeApp()">✕</button>
        </div>
    </div>
    
    <div class="container">
        <div class="header">
            <h1 class="title-main">EMC知识图谱系统</h1>
            <p class="subtitle">电磁兼容性知识管理与分析平台</p>
            <div class="status stopped" id="status">🔴 系统未启动</div>
        </div>
        
        <div class="main-content">
            <div class="card">
                <h3>🎛️ 系统控制</h3>
                <div class="control-grid">
                    <button class="btn btn-success" id="startBtn" onclick="startSystem()">🚀 启动</button>
                    <button class="btn btn-danger" id="stopBtn" onclick="stopSystem()" disabled>🛑 停止</button>
                    <button class="btn btn-info" onclick="checkStatus()">🔄 状态</button>
                    <button class="btn btn-info" onclick="openBrowser()">🌐 浏览器</button>
                </div>
                
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-number" id="nodeCount">6</div>
                        <div class="stat-label">知识节点</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="linkCount">5</div>
                        <div class="stat-label">关系连接</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="uptime">0m</div>
                        <div class="stat-label">运行时间</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">100%</div>
                        <div class="stat-label">系统健康</div>
                    </div>
                </div>
                
                <div class="links" id="quickLinks" style="display:none;">
                    <a href="#" class="btn btn-primary" onclick="openURL('http://localhost:{self.backend_port}')">🏠 主页</a>
                    <a href="#" class="btn btn-info" onclick="openURL('http://localhost:{self.backend_port}/docs')">📊 API</a>
                </div>
            </div>
            
            <div class="card">
                <h3>📋 系统日志</h3>
                <div style="margin-bottom: 10px;">
                    <button class="btn btn-info" onclick="clearLog()" style="padding: 5px 10px; font-size: 11px;">清空</button>
                </div>
                <div class="log-container" id="logContainer">
                    <div class="log-entry info">[启动] EMC知识图谱系统已加载</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <button class="btn btn-info" onclick="showAbout()" style="padding: 6px 12px; font-size: 12px;">关于</button>
            <button class="btn btn-info" onclick="showHelp()" style="padding: 6px 12px; font-size: 12px;">帮助</button>
        </div>
    </div>
    
    <script>
        let startTime = null;
        let uptimeInterval = null;
        
        // API调用函数
        async function apiCall(endpoint, method = 'GET', data = null) {{
            try {{
                const options = {{ method }};
                if (data) {{
                    options.headers = {{ 'Content-Type': 'application/json' }};
                    options.body = JSON.stringify(data);
                }}
                const response = await fetch(`http://localhost:{self.backend_port}${{endpoint}}`, options);
                return await response.json();
            }} catch (error) {{
                addLog('error', '网络请求失败: ' + error.message);
                return null;
            }}
        }}
        
        // 系统控制
        async function startSystem() {{
            updateStatus('starting', '🟡 正在启动...');
            addLog('info', '开始启动EMC知识图谱系统...');
            document.getElementById('startBtn').disabled = true;
            
            // 调用Python后端启动API
            if (window.pywebview) {{
                try {{
                    const result = await window.pywebview.api.start_backend();
                    if (result) {{
                        updateStatus('running', '🟢 系统运行中');
                        addLog('success', 'EMC知识图谱系统启动成功');
                        document.getElementById('stopBtn').disabled = false;
                        document.getElementById('quickLinks').style.display = 'block';
                        startUptimeCounter();
                        await updateStats();
                    }} else {{
                        updateStatus('stopped', '🔴 启动失败');
                        addLog('error', '系统启动失败');
                        document.getElementById('startBtn').disabled = false;
                    }}
                }} catch (error) {{
                    updateStatus('stopped', '🔴 启动失败');
                    addLog('error', '启动过程中发生错误: ' + error.message);
                    document.getElementById('startBtn').disabled = false;
                }}
            }}
        }}
        
        async function stopSystem() {{
            updateStatus('starting', '🟡 正在停止...');
            addLog('warning', '正在停止系统...');
            document.getElementById('stopBtn').disabled = true;
            
            if (window.pywebview) {{
                await window.pywebview.api.stop_backend();
            }}
            
            updateStatus('stopped', '🔴 系统已停止');
            addLog('warning', '系统已停止');
            document.getElementById('startBtn').disabled = false;
            document.getElementById('quickLinks').style.display = 'none';
            stopUptimeCounter();
        }}
        
        async function checkStatus() {{
            addLog('info', '检查系统状态...');
            const result = await apiCall('/health');
            if (result && result.status === 'healthy') {{
                updateStatus('running', '🟢 系统运行中');
                addLog('success', '系统状态正常');
                await updateStats();
            }} else {{
                updateStatus('stopped', '🔴 系统未运行');
                addLog('warning', '系统未响应');
            }}
        }}
        
        async function updateStats() {{
            const stats = await apiCall('/api/system/statistics');
            if (stats) {{
                document.getElementById('nodeCount').textContent = stats.total_nodes || '6';
                document.getElementById('linkCount').textContent = stats.total_relationships || '5';
            }}
        }}
        
        function openBrowser() {{
            if (window.pywebview) {{
                window.pywebview.api.open_browser(`http://localhost:{self.backend_port}`);
            }}
            addLog('info', '在外部浏览器中打开系统');
        }}
        
        function openURL(url) {{
            if (window.pywebview) {{
                window.pywebview.api.open_browser(url);
            }}
            addLog('info', '打开: ' + url);
        }}
        
        // 界面控制
        function updateStatus(type, message) {{
            const statusEl = document.getElementById('status');
            statusEl.className = 'status ' + type;
            statusEl.textContent = message;
            if (type === 'starting') {{
                statusEl.classList.add('pulsing');
            }} else {{
                statusEl.classList.remove('pulsing');
            }}
        }}
        
        function addLog(type, message) {{
            const logContainer = document.getElementById('logContainer');
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry ' + type;
            logEntry.textContent = `[${{timestamp}}] ${{message}}`;
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
            
            if (logContainer.children.length > 50) {{
                logContainer.removeChild(logContainer.firstChild);
            }}
        }}
        
        function clearLog() {{
            document.getElementById('logContainer').innerHTML = '';
            addLog('info', '日志已清空');
        }}
        
        function startUptimeCounter() {{
            startTime = Date.now();
            uptimeInterval = setInterval(() => {{
                const uptime = Math.floor((Date.now() - startTime) / 60000);
                document.getElementById('uptime').textContent = uptime + 'm';
            }}, 60000);
        }}
        
        function stopUptimeCounter() {{
            if (uptimeInterval) {{
                clearInterval(uptimeInterval);
                uptimeInterval = null;
            }}
            document.getElementById('uptime').textContent = '0m';
            startTime = null;
        }}
        
        // 窗口控制
        function minimizeWindow() {{
            if (window.pywebview) {{
                window.pywebview.api.minimize_window();
            }}
        }}
        
        function closeApp() {{
            if (confirm('确定要关闭EMC知识图谱系统吗？')) {{
                if (window.pywebview) {{
                    window.pywebview.api.close_app();
                }}
            }}
        }}
        
        function showAbout() {{
            alert(`🏛️ EMC知识图谱系统 v1.0.0

📋 系统信息:
• 专为电磁兼容性领域设计
• 集成知识建模、语义搜索、可视化分析  
• 支持AI推理与决策支持

🔧 技术架构:
• 后端: Python + FastAPI
• 前端: HTML5 + JavaScript  
• 界面: PyWebView桌面应用
• 数据: Neo4j图数据库

开发: EMC知识图谱团队`);
        }}
        
        function showHelp() {{
            alert(`❓ 使用帮助

🚀 快速开始:
1. 点击"启动"按钮启动系统
2. 等待状态变为"系统运行中"  
3. 使用"浏览器"按钮在外部打开Web界面

🎛️ 功能说明:
• 启动: 启动后端API服务
• 停止: 停止所有运行的服务
• 状态: 检查当前系统运行状态
• 浏览器: 在外部浏览器中打开完整界面

💡 提示:
• 系统启动后可在浏览器中使用完整功能
• 日志窗口显示实时运行状态
• 支持最小化到系统托盘`);
        }}
        
        // 初始化
        window.onload = function() {{
            addLog('success', 'EMC知识图谱桌面应用已加载');
            addLog('info', '点击"启动"按钮开始使用系统');
        }};
    </script>
</body>
</html>
        '''

    class Api:
        def __init__(self, app_instance):
            self.app = app_instance

        def start_backend(self):
            """启动后端服务"""
            return self.app.start_backend()

        def stop_backend(self):
            """停止后端服务"""
            self.app.stop_backend()
            return True

        def open_browser(self, url=""):
            """在外部浏览器中打开URL"""
            if not url:
                url = f"http://localhost:{self.app.backend_port}"
            webbrowser.open(url)

        def minimize_window(self):
            """最小化窗口"""
            if self.app.window:
                self.app.window.minimize()

        def close_app(self):
            """关闭应用"""
            self.app.stop_backend()
            if self.app.window:
                self.app.window.destroy()

    def run(self):
        """运行桌面应用"""
        print("🏛️ EMC知识图谱系统")
        print("正在启动桌面应用...")

        # 创建API实例
        api = self.Api(self)

        # 创建应用窗口
        self.window = webview.create_window(
            title="EMC知识图谱系统",
            html=self.create_app_html(),
            width=1000,
            height=700,
            min_size=(800, 600),
            resizable=True,
            js_api=api
        )

        # 设置窗口图标（如果有的话）
        try:
            icon_path = Path("icon.ico")
            if icon_path.exists():
                self.window.icon = str(icon_path)
        except:
            pass

        def on_window_close():
            """窗口关闭事件"""
            self.stop_backend()

        # 启动应用
        webview.start(debug=False, http_server=False)

def main():
    """主函数"""
    app = EMCDesktopApp()
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\\n用户中断")
    except Exception as e:
        print(f"应用启动失败: {e}")
        print("\\n可能需要安装webview库:")
        print("pip install pywebview")
    finally:
        app.stop_backend()

if __name__ == "__main__":
    main()