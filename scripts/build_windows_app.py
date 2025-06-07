#!/usr/bin/env python3
"""
Windows应用自动化构建脚本
一键构建完整的Windows桌面应用
"""

import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path
import zipfile
import json

class WindowsAppBuilder:
    """Windows应用构建器 - 实用高效"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.desktop_dir = self.project_root / "desktop"
        self.build_dir = self.project_root / "build_output"
        self.temp_dir = None
        
    def build(self):
        """执行完整构建流程"""
        print("🚀 开始构建EMC知识图谱Windows应用...")
        
        try:
            self.prepare_environment()
            self.build_backend()
            self.build_frontend()
            self.setup_electron()
            self.build_electron_app()
            self.create_installer()
            
            print("✅ Windows应用构建完成!")
            print(f"📁 输出目录: {self.build_dir}")
            
        except Exception as e:
            print(f"❌ 构建失败: {e}")
            return False
        
        finally:
            self.cleanup()
        
        return True
    
    def prepare_environment(self):
        """准备构建环境"""
        print("📋 准备构建环境...")
        
        # 创建构建目录
        self.build_dir.mkdir(exist_ok=True)
        self.desktop_dir.mkdir(exist_ok=True)
        
        # 创建临时目录
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # 检查必要工具
        required_tools = ['python', 'npm', 'node']
        for tool in required_tools:
            if not shutil.which(tool):
                raise RuntimeError(f"缺少必要工具: {tool}")
        
        print("✅ 环境准备完成")
    
    def build_backend(self):
        """构建后端服务"""
        print("🔧 构建后端服务...")
        
        # 安装PyInstaller
        subprocess.run([
            sys.executable, "-m", "pip", "install", "pyinstaller"
        ], check=True)
        
        # 创建后端启动脚本
        gateway_script = self.project_root / "gateway_standalone.py"
        gateway_script.write_text('''
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from gateway.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
''')
        
        # 打包后端
        backend_build_dir = self.desktop_dir / "resources" / "backend"
        backend_build_dir.mkdir(parents=True, exist_ok=True)
        
        subprocess.run([
            "pyinstaller",
            "--onefile",
            "--name", "emc_backend",
            "--distpath", str(backend_build_dir),
            "--workpath", str(self.temp_dir / "backend_build"),
            str(gateway_script)
        ], cwd=self.project_root, check=True)
        
        print("✅ 后端构建完成")
    
    def build_frontend(self):
        """构建前端应用"""
        print("🎨 构建前端应用...")
        
        frontend_dir = self.project_root / "frontend"
        
        # 安装依赖
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        
        # 构建生产版本
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
        
        # 复制构建结果到desktop目录
        build_src = frontend_dir / "build"
        build_dst = self.desktop_dir / "build"
        
        if build_dst.exists():
            shutil.rmtree(build_dst)
        
        shutil.copytree(build_src, build_dst)
        
        print("✅ 前端构建完成")
    
    def setup_electron(self):
        """设置Electron环境"""
        print("⚡ 设置Electron环境...")
        
        # 复制Electron配置文件（如果不存在）
        electron_files = {
            "main.js": self.get_main_js_content(),
            "preload.js": self.get_preload_js_content(),
            "package.json": self.get_package_json_content()
        }
        
        for filename, content in electron_files.items():
            file_path = self.desktop_dir / filename
            if not file_path.exists():
                file_path.write_text(content, encoding='utf-8')
        
        # 创建资源目录
        assets_dir = self.desktop_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # 创建简单图标（如果不存在）
        icon_path = assets_dir / "icon.ico"
        if not icon_path.exists():
            self.create_default_icon(icon_path)
        
        # 安装Electron依赖
        subprocess.run(["npm", "install"], cwd=self.desktop_dir, check=True)
        
        print("✅ Electron环境设置完成")
    
    def build_electron_app(self):
        """构建Electron应用"""
        print("📦 构建Electron应用...")
        
        # 构建Windows应用
        subprocess.run([
            "npm", "run", "dist"
        ], cwd=self.desktop_dir, check=True)
        
        # 复制构建结果
        electron_dist = self.desktop_dir / "dist"
        if electron_dist.exists():
            for item in electron_dist.iterdir():
                if item.is_file() and item.suffix in ['.exe', '.msi']:
                    shutil.copy2(item, self.build_dir)
                elif item.is_dir():
                    shutil.copytree(item, self.build_dir / item.name, dirs_exist_ok=True)
        
        print("✅ Electron应用构建完成")
    
    def create_installer(self):
        """创建安装程序"""
        print("📦 创建安装程序...")
        
        # 创建便携版
        portable_dir = self.build_dir / "EMC_Knowledge_Graph_Portable"
        portable_dir.mkdir(exist_ok=True)
        
        # 复制可执行文件和资源
        exe_files = list(self.build_dir.glob("*.exe"))
        for exe_file in exe_files:
            if "Setup" not in exe_file.name:
                shutil.copy2(exe_file, portable_dir)
        
        # 创建启动脚本
        start_script = portable_dir / "启动EMC知识图谱.bat"
        start_script.write_text('''
@echo off
echo 启动EMC知识图谱系统...
echo 请等待服务启动完成...
start "" "EMC知识图谱系统.exe"
''', encoding='gbk')
        
        # 创建便携版压缩包
        portable_zip = self.build_dir / "EMC_Knowledge_Graph_Portable.zip"
        with zipfile.ZipFile(portable_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in portable_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(portable_dir)
                    zf.write(file_path, arcname)
        
        print("✅ 安装程序创建完成")
    
    def get_main_js_content(self):
        """获取main.js内容"""
        # 返回操作1中的main.js内容（简化版）
        return '''
const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        }
    });

    mainWindow.loadFile('build/index.html');
}

app.whenReady().then(createWindow);
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});
'''
    
    def get_preload_js_content(self):
        """获取preload.js内容"""
        return '''
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    onFilesSelected: (callback) => ipcRenderer.on('files-selected', callback),
    onExportData: (callback) => ipcRenderer.on('export-data', callback)
});
'''
    
    def get_package_json_content(self):
        """获取package.json内容"""
        return json.dumps({
            "name": "emc-knowledge-graph-desktop",
            "version": "1.0.0",
            "main": "main.js",
            "scripts": {
                "dist": "electron-builder"
            },
            "build": {
                "appId": "com.emc.knowledge-graph",
                "productName": "EMC知识图谱系统",
                "win": {
                    "target": "nsis",
                    "icon": "assets/icon.ico"
                }
            },
            "devDependencies": {
                "electron": "^28.0.0",
                "electron-builder": "^24.9.1"
            }
        }, indent=2)
    
    def create_default_icon(self, icon_path):
        """创建默认图标"""
        # 创建简单的32x32 ICO文件
        icon_data = b'\x00\x00\x01\x00\x01\x00  \x00\x00\x01\x00\x08\x00\xe8\x02\x00\x00\x16\x00\x00\x00(\x00\x00\x00 \x00\x00\x00@\x00\x00\x00\x01\x00\x08\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00'
        icon_path.write_bytes(icon_data)
    
    def cleanup(self):
        """清理临时文件"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

if __name__ == "__main__":
    builder = WindowsAppBuilder()
    success = builder.build()
    sys.exit(0 if success else 1)