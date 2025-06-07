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

        # 检查关键的main.js文件是否存在
        main_js_path = self.desktop_dir / "main.js"
        if not main_js_path.exists():
            raise FileNotFoundError(
                "Critical file desktop/main.js is missing. Cannot proceed with build."
            )

        # 处理 preload.js 和 package.json，如果不存在则创建
        optional_electron_files = {
            "preload.js": self.get_preload_js_content(),
            "package.json": self.get_package_json_content()
        }
        
        for filename, content in optional_electron_files.items():
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

        # Define package.json path to read productName
        package_json_path = self.desktop_dir / "package.json"
        product_name = "EMC知识图谱系统" # Default
        if package_json_path.exists():
            with open(package_json_path, 'r', encoding='utf-8') as f:
                pkg_json = json.load(f)
                product_name = pkg_json.get("build", {}).get("productName", product_name)

        # Source for portable version is the win-unpacked directory
        # This directory should have been copied to self.build_dir by build_electron_app
        unpacked_src_dir_name = "win-unpacked" # Default name from electron-builder
        # A more robust way might involve finding the directory that contains productName.exe
        # For now, we assume "win-unpacked" or a directory named after the product.

        possible_unpacked_dirs = [
            self.build_dir / unpacked_src_dir_name,
            self.build_dir / f"{product_name}-win32-x64", # Another common pattern
            self.build_dir / f"{product_name}-win-x64"
        ]

        actual_unpacked_src_dir = None
        for d in possible_unpacked_dirs:
            if d.exists() and d.is_dir() and (d / f"{product_name}.exe").exists():
                actual_unpacked_src_dir = d
                break

        if not actual_unpacked_src_dir:
            raise FileNotFoundError(
                f"Could not find suitable unpacked directory (e.g., win-unpacked, {product_name}-win32-x64) "
                f"containing '{product_name}.exe' in {self.build_dir}. "
                "Ensure build_electron_app correctly copies it."
            )

        # 创建便携版目标目录
        portable_target_dir = self.build_dir / "EMC_Knowledge_Graph_Portable"
        if portable_target_dir.exists():
            shutil.rmtree(portable_target_dir) # Clean up old portable dir

        # 复制整个 win-unpacked 目录的内容到便携版目标目录
        shutil.copytree(actual_unpacked_src_dir, portable_target_dir)

        # 创建启动脚本 inside the portable directory
        # The .bat file will be at the root of the portable directory,
        # and it will launch the executable which is also at the root.
        start_script_content = f'''@echo off
echo 启动 {product_name}...
echo 请等待服务启动完成...
start "" "{product_name}.exe"
'''
        start_script_path = portable_target_dir / f"启动{product_name}.bat"
        start_script_path.write_text(start_script_content, encoding='gbk')
        
        # 创建便携版压缩包
        portable_zip_path = self.build_dir / "EMC_Knowledge_Graph_Portable.zip"
        if portable_zip_path.exists():
            portable_zip_path.unlink() # Remove old zip if exists

        with zipfile.ZipFile(portable_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in portable_target_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(portable_target_dir)
                    zf.write(file_path, arcname)
        
        print(f"✅ 便携版创建完成: {portable_zip_path}")
        print("✅ 安装程序和便携版创建流程结束")
    
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