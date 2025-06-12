#!/usr/bin/env python3
"""
EMC知识图谱系统启动脚本
重组后的统一启动入口
"""
import subprocess
import os
import sys
import time
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 检查系统依赖...")
    
    try:
        import aiohttp
        print("✅ aiohttp 已安装")
    except ImportError:
        print("❌ aiohttp 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "aiohttp"])
    
    try:
        import fastapi
        print("✅ FastAPI 已安装")
    except ImportError:
        print("❌ FastAPI 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn"])

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    
    backend_path = Path(__file__).parent / "backend" / "enhanced_gateway.py"
    if not backend_path.exists():
        print("❌ 后端文件不存在:", backend_path)
        return None
    
    # 启动后端
    process = subprocess.Popen([
        sys.executable, str(backend_path)
    ], cwd=str(backend_path.parent))
    
    print(f"✅ 后端服务已启动 (PID: {process.pid})")
    return process

def start_frontend():
    """启动前端服务"""
    print("🌐 启动前端服务...")
    
    frontend_path = Path(__file__).parent / "frontend"
    if not frontend_path.exists():
        print("❌ 前端目录不存在:", frontend_path)
        return None
    
    package_json = frontend_path / "package.json"
    if not package_json.exists():
        print("❌ package.json 不存在")
        return None
    
    # 检查 node_modules
    node_modules = frontend_path / "node_modules"
    if not node_modules.exists():
        print("📦 安装前端依赖...")
        subprocess.run(["npm", "install"], cwd=str(frontend_path))
    
    # 启动前端
    process = subprocess.Popen([
        "npm", "start"
    ], cwd=str(frontend_path))
    
    print(f"✅ 前端服务已启动 (PID: {process.pid})")
    return process

def start_test_server():
    """启动测试服务器"""
    print("🧪 启动测试服务器...")
    
    test_html = Path(__file__).parent / "dev-tools" / "examples" / "simple_frontend.html"
    if test_html.exists():
        process = subprocess.Popen([
            sys.executable, "-m", "http.server", "3001"
        ], cwd=str(test_html.parent))
        
        print(f"✅ 测试服务器已启动 (PID: {process.pid})")
        return process
    
    return None

def main():
    """主函数"""
    print("🏛️ EMC知识图谱系统")
    print("=" * 50)
    
    # 检查依赖
    check_dependencies()
    
    print("\n🚀 启动系统服务...")
    
    # 启动后端
    backend_process = start_backend()
    time.sleep(3)  # 等待后端启动
    
    # 启动前端
    frontend_process = start_frontend()
    time.sleep(2)  # 等待前端启动
    
    # 启动测试服务器
    test_process = start_test_server()
    
    print("\n" + "=" * 50)
    print("🎉 系统启动完成！")
    print("\n📱 访问地址:")
    print("   - 🌐 完整前端: http://localhost:3000")
    print("   - 🧪 测试界面: http://localhost:3001/simple_frontend.html") 
    print("   - 📊 API文档: http://localhost:8000/docs")
    print("   - ⚙️ 后端健康: http://localhost:8000/health")
    
    print("\n📋 开发指南:")
    print("   - 📁 后端代码: ./backend/")
    print("   - 🌐 前端代码: ./frontend/src/")
    print("   - 🧪 测试文件: ./dev-tools/tests/")
    print("   - 📚 文档: ./docs/")
    
    print("\n按 Ctrl+C 停止系统")
    
    try:
        # 等待用户中断
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 正在停止系统...")
        
        if backend_process:
            backend_process.terminate()
            print("✅ 后端服务已停止")
        
        if frontend_process:
            frontend_process.terminate()
            print("✅ 前端服务已停止")
            
        if test_process:
            test_process.terminate()
            print("✅ 测试服务器已停止")
        
        print("👋 系统已关闭")

if __name__ == "__main__":
    main()