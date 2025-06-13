#!/usr/bin/env python3
"""
EMC知识图谱系统 - 独立Windows应用
无需GUI库，使用HTML+浏览器作为界面
"""

import webbrowser
import http.server
import socketserver
import threading
import time
import os
import sys
import subprocess
import socket
from pathlib import Path
import json
from urllib.parse import parse_qs
import tempfile

class EMCStandaloneApp:
    def __init__(self):
        self.port = 8080
        self.server = None
        self.backend_process = None
        self.running = False
        
    def find_free_port(self):
        """找到可用端口"""
        for port in range(8080, 8090):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('localhost', port))
                sock.close()
                return port
            except:
                continue
        return 8080
    
    def create_app_html(self):
        """创建应用界面HTML"""
        html_content = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EMC知识图谱系统</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏛️</text></svg>">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ 
            background: rgba(255,255,255,0.95); 
            padding: 30px; 
            border-radius: 15px; 
            margin-bottom: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .title {{ 
            font-size: 2.8em; 
            color: #2c3e50; 
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .subtitle {{ color: #666; font-size: 1.3em; margin-bottom: 20px; }}
        .status {{ 
            padding: 15px; 
            border-radius: 25px; 
            font-weight: bold;
            display: inline-block;
            min-width: 200px;
        }}
        .status.running {{ background: linear-gradient(45deg, #28a745, #20c997); color: white; }}
        .status.stopped {{ background: linear-gradient(45deg, #dc3545, #c82333); color: white; }}
        .status.starting {{ background: linear-gradient(45deg, #ffc107, #fd7e14); color: white; }}
        
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
        .card {{ 
            background: rgba(255,255,255,0.95); 
            padding: 25px; 
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}
        .card h3 {{ color: #2c3e50; margin-bottom: 20px; font-size: 1.4em; }}
        
        .btn {{ 
            display: inline-block;
            padding: 12px 24px; 
            margin: 8px; 
            color: white; 
            text-decoration: none; 
            border: none;
            border-radius: 25px; 
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
            font-weight: bold;
            border: 2px solid transparent;
        }}
        .btn:hover {{ 
            transform: translateY(-2px); 
            box-shadow: 0 8px 25px rgba(0,0,0,0.3); 
        }}
        .btn-primary {{ background: linear-gradient(45deg, #007bff, #0056b3); }}
        .btn-success {{ background: linear-gradient(45deg, #28a745, #20c997); }}
        .btn-warning {{ background: linear-gradient(45deg, #ffc107, #fd7e14); color: #333; }}
        .btn-danger {{ background: linear-gradient(45deg, #dc3545, #c82333); }}
        .btn-info {{ background: linear-gradient(45deg, #17a2b8, #138496); }}
        .btn:disabled {{ 
            opacity: 0.6; 
            cursor: not-allowed; 
            transform: none; 
            box-shadow: none; 
        }}
        
        .control-panel {{ text-align: center; margin: 20px 0; }}
        .links {{ margin: 15px 0; }}
        .links a {{ display: block; margin: 8px 0; text-align: center; }}
        
        .log-container {{ 
            background: #2c3e50; 
            color: #ecf0f1; 
            padding: 20px; 
            border-radius: 10px; 
            height: 300px; 
            overflow-y: auto; 
            font-family: 'Courier New', monospace; 
            font-size: 13px;
            line-height: 1.4;
        }}
        .log-entry {{ margin: 3px 0; }}
        .log-entry.success {{ color: #2ecc71; }}
        .log-entry.error {{ color: #e74c3c; }}
        .log-entry.warning {{ color: #f39c12; }}
        .log-entry.info {{ color: #3498db; }}
        
        .stats {{ 
            display: grid; 
            grid-template-columns: repeat(4, 1fr); 
            gap: 15px; 
            margin: 20px 0; 
        }}
        .stat-item {{ 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 10px; 
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .stat-number {{ font-size: 1.8em; font-weight: bold; color: #007bff; }}
        .stat-label {{ color: #666; margin-top: 5px; font-size: 0.9em; }}
        
        .feature-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 15px; 
            margin: 20px 0; 
        }}
        .feature-item {{ 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center;
            border-top: 3px solid #007bff;
        }}
        .feature-icon {{ font-size: 2em; margin-bottom: 10px; }}
        .feature-title {{ font-weight: bold; margin-bottom: 8px; }}
        .feature-desc {{ color: #666; font-size: 0.9em; }}
        
        .footer {{ 
            text-align: center; 
            margin-top: 30px; 
            padding: 20px; 
            background: rgba(255,255,255,0.1); 
            border-radius: 10px; 
            color: white; 
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        .pulsing {{ animation: pulse 2s infinite; }}
        
        /* 响应式设计 */
        @media (max-width: 768px) {{
            .grid {{ grid-template-columns: 1fr; }}
            .stats {{ grid-template-columns: repeat(2, 1fr); }}
            .title {{ font-size: 2em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">🏛️ EMC知识图谱系统</h1>
            <p class="subtitle">电磁兼容性知识管理与分析平台</p>
            <div class="status stopped" id="status">🔴 系统未启动</div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🎛️ 系统控制</h3>
                <div class="control-panel">
                    <button class="btn btn-success" id="startBtn" onclick="startSystem()">🚀 启动系统</button>
                    <button class="btn btn-danger" id="stopBtn" onclick="stopSystem()" disabled>🛑 停止系统</button>
                </div>
                <div class="control-panel">
                    <button class="btn btn-info" onclick="checkStatus()">🔄 检查状态</button>
                    <button class="btn btn-warning" onclick="openDemo()">🎨 演示模式</button>
                </div>
                
                <h4 style="margin-top: 20px;">📱 快速访问</h4>
                <div class="links">
                    <a href="#" class="btn btn-primary" onclick="openURL('http://localhost:8002')" id="webBtn" style="display:none;">🌐 系统主页</a>
                    <a href="#" class="btn btn-info" onclick="openURL('http://localhost:8002/docs')" id="apiBtn" style="display:none;">📊 API文档</a>
                    <a href="#" class="btn btn-success" onclick="openURL('http://localhost:8002/health')" id="healthBtn" style="display:none;">⚡ 健康检查</a>
                </div>
            </div>
            
            <div class="card">
                <h3>📋 系统日志</h3>
                <div style="margin-bottom: 10px;">
                    <button class="btn btn-info" onclick="clearLog()" style="padding: 6px 12px; font-size: 12px;">🗑️ 清空日志</button>
                    <button class="btn btn-info" onclick="refreshLog()" style="padding: 6px 12px; font-size: 12px;">🔄 刷新</button>
                </div>
                <div class="log-container" id="logContainer">
                    <div class="log-entry info">[启动] EMC知识图谱系统已加载</div>
                    <div class="log-entry info">[系统] 等待用户操作...</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>📊 系统统计</h3>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number" id="uptime">0</div>
                    <div class="stat-label">运行时间(分钟)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">6</div>
                    <div class="stat-label">知识节点</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">5</div>
                    <div class="stat-label">关系连接</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">100%</div>
                    <div class="stat-label">系统健康</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>🎯 核心功能</h3>
            <div class="feature-grid">
                <div class="feature-item">
                    <div class="feature-icon">🏗️</div>
                    <div class="feature-title">知识建模</div>
                    <div class="feature-desc">智能构建EMC知识图谱</div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">🔍</div>
                    <div class="feature-title">语义搜索</div>
                    <div class="feature-desc">基于语义的智能检索</div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">📊</div>
                    <div class="feature-title">可视化分析</div>
                    <div class="feature-desc">交互式图谱展示</div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">🤖</div>
                    <div class="feature-title">AI推理</div>
                    <div class="feature-desc">智能推理与决策支持</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>🏛️ EMC知识图谱系统 v1.0.0 | 电磁兼容性领域专业工具</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                <button class="btn btn-info" onclick="showAbout()" style="padding: 8px 16px;">ℹ️ 关于系统</button>
                <button class="btn btn-info" onclick="showHelp()" style="padding: 8px 16px;">❓ 使用帮助</button>
                <button class="btn btn-danger" onclick="closeApp()" style="padding: 8px 16px;">🚪 退出应用</button>
            </p>
        </div>
    </div>
    
    <script>
        let systemStartTime = null;
        let uptimeInterval = null;
        
        // 系统控制函数
        async function startSystem() {{
            updateStatus('starting', '🟡 正在启动系统...');
            addLog('info', '开始启动EMC知识图谱后端服务...');
            document.getElementById('startBtn').disabled = true;
            
            try {{
                const response = await fetch('/api/start', {{ method: 'POST' }});
                const result = await response.json();
                
                if (result.success) {{
                    updateStatus('running', '🟢 系统运行中');
                    addLog('success', '后端服务启动成功');
                    document.getElementById('stopBtn').disabled = false;
                    showQuickLinks();
                    systemStartTime = Date.now();
                    startUptimeCounter();
                }} else {{
                    updateStatus('stopped', '🔴 启动失败');
                    addLog('error', '启动失败: ' + result.error);
                    document.getElementById('startBtn').disabled = false;
                }}
            }} catch (error) {{
                updateStatus('stopped', '🔴 启动失败');
                addLog('error', '启动过程中发生错误: ' + error.message);
                document.getElementById('startBtn').disabled = false;
            }}
        }}
        
        async function stopSystem() {{
            updateStatus('starting', '🟡 正在停止系统...');
            addLog('warning', '正在停止系统服务...');
            document.getElementById('stopBtn').disabled = true;
            
            try {{
                const response = await fetch('/api/stop', {{ method: 'POST' }});
                const result = await response.json();
                
                updateStatus('stopped', '🔴 系统已停止');
                addLog('warning', '系统服务已停止');
                document.getElementById('startBtn').disabled = false;
                hideQuickLinks();
                stopUptimeCounter();
            }} catch (error) {{
                addLog('error', '停止过程中发生错误: ' + error.message);
                document.getElementById('stopBtn').disabled = false;
            }}
        }}
        
        async function checkStatus() {{
            addLog('info', '检查系统状态...');
            
            try {{
                const response = await fetch('/api/status');
                const result = await response.json();
                
                if (result.status === 'running') {{
                    updateStatus('running', '🟢 系统运行中');
                    addLog('success', '系统状态: 运行中');
                    showQuickLinks();
                    document.getElementById('startBtn').disabled = true;
                    document.getElementById('stopBtn').disabled = false;
                }} else {{
                    updateStatus('stopped', '🔴 系统未运行');
                    addLog('warning', '系统状态: 未运行');
                    hideQuickLinks();
                    document.getElementById('startBtn').disabled = false;
                    document.getElementById('stopBtn').disabled = true;
                }}
            }} catch (error) {{
                addLog('error', '状态检查失败: ' + error.message);
            }}
        }}
        
        function openDemo() {{
            addLog('info', '打开演示模式...');
            openURL('/demo');
        }}
        
        function openURL(url) {{
            window.open(url, '_blank');
            addLog('info', '打开链接: ' + url);
        }}
        
        // 界面更新函数
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
            
            // 限制日志条数
            while (logContainer.children.length > 100) {{
                logContainer.removeChild(logContainer.firstChild);
            }}
        }}
        
        function clearLog() {{
            document.getElementById('logContainer').innerHTML = '';
            addLog('info', '日志已清空');
        }}
        
        function refreshLog() {{
            addLog('info', '日志已刷新 - ' + new Date().toLocaleString());
        }}
        
        function showQuickLinks() {{
            document.getElementById('webBtn').style.display = 'block';
            document.getElementById('apiBtn').style.display = 'block';
            document.getElementById('healthBtn').style.display = 'block';
        }}
        
        function hideQuickLinks() {{
            document.getElementById('webBtn').style.display = 'none';
            document.getElementById('apiBtn').style.display = 'none';
            document.getElementById('healthBtn').style.display = 'none';
        }}
        
        function startUptimeCounter() {{
            uptimeInterval = setInterval(() => {{
                if (systemStartTime) {{
                    const uptime = Math.floor((Date.now() - systemStartTime) / 60000);
                    document.getElementById('uptime').textContent = uptime;
                }}
            }}, 60000);
        }}
        
        function stopUptimeCounter() {{
            if (uptimeInterval) {{
                clearInterval(uptimeInterval);
                uptimeInterval = null;
            }}
            document.getElementById('uptime').textContent = '0';
            systemStartTime = null;
        }}
        
        // 信息对话框
        function showAbout() {{
            alert(`🏛️ EMC知识图谱系统 v1.0.0

📋 系统信息:
• 专为电磁兼容性领域设计
• 集成知识建模、语义搜索、可视化分析
• 支持AI推理与决策支持

🔧 技术架构:
• 后端: Python + FastAPI
• 前端: HTML5 + JavaScript
• 数据库: Neo4j图数据库
• 部署: Docker容器化

👥 开发团队: EMC知识图谱团队
📅 版本日期: 2025-01-13`);
        }}
        
        function showHelp() {{
            alert(`❓ 使用帮助

🚀 快速开始:
1. 点击"启动系统"按钮
2. 等待系统启动完成
3. 使用"快速访问"链接打开功能页面

🎛️ 系统控制:
• 启动系统: 启动后端API服务
• 停止系统: 停止所有运行的服务
• 检查状态: 查看当前系统运行状态
• 演示模式: 查看系统功能演示

📱 访问方式:
• 系统主页: 查看系统概览
• API文档: 浏览完整API接口
• 健康检查: 验证系统运行状态

🆘 故障排除:
• 如果启动失败，请检查端口是否被占用
• 查看系统日志了解详细错误信息
• 尝试重新启动系统`);
        }}
        
        function closeApp() {{
            if (confirm('确定要关闭EMC知识图谱系统吗？\\n\\n如果系统正在运行，将自动停止所有服务。')) {{
                fetch('/api/shutdown', {{ method: 'POST' }}).finally(() => {{
                    window.close();
                }});
            }}
        }}
        
        // 页面加载完成后的初始化
        window.onload = function() {{
            addLog('success', 'EMC知识图谱系统界面已加载');
            addLog('info', '点击"启动系统"开始使用');
            
            // 检查初始状态
            setTimeout(checkStatus, 1000);
            
            // 定期状态检查
            setInterval(checkStatus, 30000);
        }};
        
        // 页面关闭前的清理
        window.onbeforeunload = function() {{
            fetch('/api/shutdown', {{ method: 'POST' }});
        }};
    </script>
</body>
</html>
        '''
        return html_content
    
    def create_demo_html(self):
        """创建演示页面"""
        try:
            demo_file = Path("standalone-demo.html")
            if demo_file.exists():
                return demo_file.read_text(encoding='utf-8')
        except:
            pass
        
        return """
        <html>
        <head><title>演示页面</title></head>
        <body style="font-family: Arial; padding: 40px; text-align: center;">
            <h1>🎨 EMC知识图谱系统演示</h1>
            <p>演示文件不可用，请检查 standalone-demo.html 文件是否存在。</p>
        </body>
        </html>
        """
    
    class AppHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, app_instance=None, **kwargs):
            self.app = app_instance
            super().__init__(*args, **kwargs)
        
        def do_GET(self):
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(self.app.create_app_html().encode('utf-8'))
            elif self.path == '/demo':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(self.app.create_demo_html().encode('utf-8'))
            elif self.path == '/api/status':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                status = "running" if self.app.backend_process and self.app.backend_process.poll() is None else "stopped"
                response = {"status": status, "port": 8002 if status == "running" else None}
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                super().do_GET()
        
        def do_POST(self):
            if self.path == '/api/start':
                try:
                    success = self.app.start_backend()
                    response = {"success": success, "message": "启动成功" if success else "启动失败"}
                except Exception as e:
                    response = {"success": False, "error": str(e)}
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            elif self.path == '/api/stop':
                try:
                    self.app.stop_backend()
                    response = {"success": True, "message": "停止成功"}
                except Exception as e:
                    response = {"success": False, "error": str(e)}
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            elif self.path == '/api/shutdown':
                self.app.shutdown()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"success": true}')
            else:
                self.send_response(404)
                self.end_headers()
        
        def log_message(self, format, *args):
            # 减少服务器日志输出
            pass
    
    def start_backend(self):
        """启动后端服务"""
        try:
            if self.backend_process and self.backend_process.poll() is None:
                self.backend_process.terminate()
                time.sleep(1)
            
            # 创建简化的后端API
            backend_code = '''
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import json

app = FastAPI(title="EMC知识图谱API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return HTMLResponse("""
    <html>
    <head><title>EMC知识图谱API</title></head>
    <body style="font-family: Arial; padding: 40px; text-align: center;">
        <h1>🏛️ EMC知识图谱API</h1>
        <p>API服务正在运行</p>
        <div style="margin: 20px;">
            <a href="/docs" style="padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px;">📊 API文档</a>
            <a href="/health" style="padding: 10px 20px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; margin: 5px;">⚡ 健康检查</a>
        </div>
    </body>
    </html>
    """)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "EMC Knowledge Graph", "version": "1.0.0"}

@app.get("/api/system/status")
async def system_status():
    return {"status": "running", "nodes": 6, "relationships": 5, "version": "1.0.0"}

@app.get("/api/system/statistics")
async def system_statistics():
    return {
        "nodes": 150,
        "relationships": 300,
        "entities": 75,
        "last_updated": "2025-01-13T10:30:00Z"
    }

if __name__ == "__main__":
    print("🚀 EMC知识图谱API服务启动中...")
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="warning")
'''
            
            # 写入临时文件
            backend_file = Path(tempfile.gettempdir()) / "emc_backend_api.py"
            backend_file.write_text(backend_code, encoding='utf-8')
            
            # 启动后端进程
            self.backend_process = subprocess.Popen([
                sys.executable, str(backend_file)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 等待启动
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"启动后端失败: {e}")
            return False
    
    def stop_backend(self):
        """停止后端服务"""
        if self.backend_process and self.backend_process.poll() is None:
            self.backend_process.terminate()
            self.backend_process.wait(timeout=5)
            self.backend_process = None
    
    def start_server(self):
        """启动HTTP服务器"""
        self.port = self.find_free_port()
        
        def handler(*args, **kwargs):
            return self.AppHandler(*args, app_instance=self, **kwargs)
        
        with socketserver.TCPServer(("", self.port), handler) as httpd:
            self.server = httpd
            self.running = True
            print(f"🌐 EMC知识图谱系统已启动")
            print(f"📱 访问地址: http://localhost:{self.port}")
            print(f"💡 正在自动打开浏览器...")
            print(f"🔄 按 Ctrl+C 停止应用")
            
            # 自动打开浏览器
            threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{self.port}")).start()
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                self.shutdown()
    
    def shutdown(self):
        """关闭应用"""
        print("\\n🛑 正在关闭EMC知识图谱系统...")
        self.running = False
        self.stop_backend()
        if self.server:
            self.server.shutdown()
        print("✅ 应用已关闭")

def main():
    """主函数"""
    print("🏛️ EMC知识图谱系统 - 独立Windows应用")
    print("=" * 50)
    
    app = EMCStandaloneApp()
    
    try:
        app.start_server()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()