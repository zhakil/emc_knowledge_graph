#!/usr/bin/env python3
"""
EMC知识图谱系统 - Windows桌面应用
使用Tkinter创建本地GUI应用
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import webbrowser
import subprocess
import threading
import os
import sys
import socket
import time
from pathlib import Path
import json

class EMCKnowledgeGraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EMC知识图谱系统")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置图标（如果有的话）
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 进程管理
        self.backend_process = None
        self.frontend_process = None
        
        self.setup_ui()
        self.check_dependencies()
    
    def setup_ui(self):
        """设置用户界面"""
        # 主标题
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = ttk.Label(
            title_frame, 
            text="🏛️ EMC知识图谱系统", 
            font=("Arial", 20, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame, 
            text="电磁兼容性知识管理与分析平台", 
            font=("Arial", 12)
        )
        subtitle_label.pack(pady=5)
        
        # 状态框架
        status_frame = ttk.LabelFrame(self.root, text="系统状态", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_text = ttk.Label(status_frame, text="🔴 系统未启动", font=("Arial", 11))
        self.status_text.pack()
        
        # 控制按钮框架
        control_frame = ttk.LabelFrame(self.root, text="系统控制", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 按钮网格
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X)
        
        # 第一行按钮
        row1 = ttk.Frame(btn_frame)
        row1.pack(fill=tk.X, pady=2)
        
        self.start_btn = ttk.Button(
            row1, text="🚀 启动系统", command=self.start_system, width=15
        )
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.stop_btn = ttk.Button(
            row1, text="🛑 停止系统", command=self.stop_system, width=15, state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=2)
        
        self.demo_btn = ttk.Button(
            row1, text="🎨 演示模式", command=self.open_demo, width=15
        )
        self.demo_btn.pack(side=tk.LEFT, padx=2)
        
        # 第二行按钮
        row2 = ttk.Frame(btn_frame)
        row2.pack(fill=tk.X, pady=2)
        
        self.web_btn = ttk.Button(
            row2, text="🌐 打开前端", command=self.open_frontend, width=15, state=tk.DISABLED
        )
        self.web_btn.pack(side=tk.LEFT, padx=2)
        
        self.api_btn = ttk.Button(
            row2, text="📊 API文档", command=self.open_api_docs, width=15, state=tk.DISABLED
        )
        self.api_btn.pack(side=tk.LEFT, padx=2)
        
        self.health_btn = ttk.Button(
            row2, text="⚡ 健康检查", command=self.check_health, width=15
        )
        self.health_btn.pack(side=tk.LEFT, padx=2)
        
        # 快速链接框架
        links_frame = ttk.LabelFrame(self.root, text="快速访问", padding=10)
        links_frame.pack(fill=tk.X, padx=10, pady=5)
        
        links_grid = ttk.Frame(links_frame)
        links_grid.pack(fill=tk.X)
        
        ttk.Button(links_grid, text="📄 查看文档", command=self.open_docs, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(links_grid, text="🐳 Docker部署", command=self.show_docker_info, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(links_grid, text="⚙️ 设置", command=self.open_settings, width=12).pack(side=tk.LEFT, padx=2)
        
        # 日志框架
        log_frame = ttk.LabelFrame(self.root, text="系统日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=12, width=80, font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        status_bar = ttk.Frame(self.root)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_bar_text = ttk.Label(status_bar, text="就绪", relief=tk.SUNKEN)
        self.status_bar_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 退出时清理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def log(self, message):
        """添加日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_msg)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, message, color="black"):
        """更新状态显示"""
        self.status_text.config(text=message)
        self.status_bar_text.config(text=message)
        self.log(message.replace("🟢", "").replace("🔴", "").replace("🟡", "").strip())
    
    def check_dependencies(self):
        """检查依赖"""
        self.log("检查系统依赖...")
        
        # 检查Python
        python_version = sys.version.split()[0]
        self.log(f"Python版本: {python_version}")
        
        # 检查必要的包
        required_packages = ["uvicorn", "fastapi"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                self.log(f"✅ {package} 已安装")
            except ImportError:
                missing_packages.append(package)
                self.log(f"❌ {package} 未安装")
        
        if missing_packages:
            self.log("⚠️ 缺少必要的Python包，系统功能可能受限")
        else:
            self.log("✅ 所有依赖检查通过")
    
    def check_port(self, port):
        """检查端口是否可用"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except:
            return False
    
    def start_system(self):
        """启动系统"""
        self.update_status("🟡 正在启动系统...")
        self.start_btn.config(state=tk.DISABLED)
        
        def start_thread():
            try:
                # 启动后端
                self.log("🚀 启动后端服务...")
                backend_file = Path(__file__).parent / "backend" / "enhanced_gateway.py"
                
                if backend_file.exists():
                    self.backend_process = subprocess.Popen([
                        sys.executable, str(backend_file)
                    ], cwd=str(backend_file.parent))
                    self.log(f"后端进程启动 (PID: {self.backend_process.pid})")
                    time.sleep(3)
                else:
                    self.log("❌ 后端文件不存在，创建简化服务...")
                    self.start_simple_backend()
                
                # 检查后端状态
                if self.check_port(8001):
                    self.log("✅ 后端服务启动成功")
                    self.root.after(0, self.on_backend_started)
                else:
                    self.log("❌ 后端服务启动失败")
                    self.root.after(0, self.on_start_failed)
                
            except Exception as e:
                self.log(f"❌ 启动过程中发生错误: {e}")
                self.root.after(0, self.on_start_failed)
        
        threading.Thread(target=start_thread, daemon=True).start()
    
    def start_simple_backend(self):
        """启动简化的后端服务"""
        backend_code = '''
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

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
    return {"message": "EMC知识图谱API正在运行", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "EMC Knowledge Graph"}

@app.get("/api/system/status")
async def system_status():
    return {"status": "running", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
'''
        
        backend_file = Path("/tmp/emc_backend.py")
        backend_file.write_text(backend_code)
        
        self.backend_process = subprocess.Popen([
            sys.executable, str(backend_file)
        ])
    
    def on_backend_started(self):
        """后端启动成功后的回调"""
        self.update_status("🟢 系统运行中")
        self.stop_btn.config(state=tk.NORMAL)
        self.web_btn.config(state=tk.NORMAL)
        self.api_btn.config(state=tk.NORMAL)
    
    def on_start_failed(self):
        """启动失败后的回调"""
        self.update_status("🔴 启动失败")
        self.start_btn.config(state=tk.NORMAL)
    
    def stop_system(self):
        """停止系统"""
        self.update_status("🟡 正在停止系统...")
        
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process = None
            self.log("后端服务已停止")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process = None
            self.log("前端服务已停止")
        
        self.update_status("🔴 系统已停止")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.web_btn.config(state=tk.DISABLED)
        self.api_btn.config(state=tk.DISABLED)
    
    def open_demo(self):
        """打开演示页面"""
        demo_file = Path(__file__).parent / "standalone-demo.html"
        if demo_file.exists():
            webbrowser.open(f"file://{demo_file.absolute()}")
            self.log("已打开演示页面")
        else:
            messagebox.showwarning("文件不存在", "演示文件不存在")
    
    def open_frontend(self):
        """打开前端页面"""
        webbrowser.open("http://127.0.0.1:3002")
        self.log("已打开前端页面")
    
    def open_api_docs(self):
        """打开API文档"""
        webbrowser.open("http://127.0.0.1:8001/docs")
        self.log("已打开API文档")
    
    def check_health(self):
        """健康检查"""
        try:
            import urllib.request
            urllib.request.urlopen("http://127.0.0.1:8001/health", timeout=5)
            messagebox.showinfo("健康检查", "✅ 系统运行正常")
            self.log("健康检查通过")
        except:
            messagebox.showwarning("健康检查", "❌ 系统未响应")
            self.log("健康检查失败")
    
    def open_docs(self):
        """打开文档"""
        doc_file = Path(__file__).parent / "DOCKER_DEPLOYMENT.md"
        if doc_file.exists():
            os.startfile(str(doc_file))
        else:
            messagebox.showinfo("提示", "文档文件不存在")
    
    def show_docker_info(self):
        """显示Docker信息"""
        info = """🐳 Docker部署指南

快速启动命令:
docker compose -f docker-compose.community.yml up -d

或运行脚本:
./start-docker.sh

详细信息请查看 DOCKER_DEPLOYMENT.md 文件"""
        messagebox.showinfo("Docker部署", info)
    
    def open_settings(self):
        """打开设置窗口"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("系统设置")
        settings_window.geometry("400x300")
        
        ttk.Label(settings_window, text="系统设置", font=("Arial", 14, "bold")).pack(pady=10)
        
        # 端口设置
        port_frame = ttk.LabelFrame(settings_window, text="端口配置", padding=10)
        port_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(port_frame, text="后端端口:").pack(anchor=tk.W)
        backend_port = ttk.Entry(port_frame)
        backend_port.insert(0, "8001")
        backend_port.pack(fill=tk.X, pady=2)
        
        ttk.Label(port_frame, text="前端端口:").pack(anchor=tk.W)
        frontend_port = ttk.Entry(port_frame)
        frontend_port.insert(0, "3002")
        frontend_port.pack(fill=tk.X, pady=2)
        
        ttk.Button(settings_window, text="保存设置", command=settings_window.destroy).pack(pady=10)
    
    def on_closing(self):
        """窗口关闭时的清理"""
        if self.backend_process or self.frontend_process:
            if messagebox.askokcancel("退出", "系统正在运行，确定要退出吗？"):
                self.stop_system()
                self.root.quit()
        else:
            self.root.quit()

def main():
    """主函数"""
    root = tk.Tk()
    app = EMCKnowledgeGraphApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()