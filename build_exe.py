#!/usr/bin/env python3
"""
构建EMC知识图谱系统Windows可执行文件
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """安装必要的依赖"""
    print("📦 安装构建依赖...")
    requirements = [
        "pywebview",
        "fastapi", 
        "uvicorn",
        "pyinstaller"
    ]
    
    for req in requirements:
        try:
            __import__(req.replace("-", "_"))
            print(f"✅ {req} 已安装")
        except ImportError:
            print(f"📥 安装 {req}...")
            subprocess.run([sys.executable, "-m", "pip", "install", req], check=True)

def create_spec_file():
    """创建PyInstaller配置文件"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['emc_desktop_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('standalone-demo.html', '.'),
    ],
    hiddenimports=[
        'webview',
        'fastapi',
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EMC知识图谱系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    spec_file = Path("emc_app.spec")
    spec_file.write_text(spec_content.strip())
    print(f"✅ 创建配置文件: {spec_file}")
    return spec_file

def build_exe():
    """构建可执行文件"""
    print("🔨 开始构建Windows可执行文件...")
    
    try:
        # 清理之前的构建
        import shutil
        for dir_name in ['build', 'dist']:
            if Path(dir_name).exists():
                shutil.rmtree(dir_name)
                print(f"🗑️ 清理 {dir_name} 目录")
        
        # 创建规格文件
        spec_file = create_spec_file()
        
        # 构建
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", str(spec_file)]
        print("⚙️ 执行构建命令...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            exe_path = Path("dist") / "EMC知识图谱系统.exe"
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / 1024 / 1024
                print(f"✅ 构建成功!")
                print(f"📁 可执行文件: {exe_path}")
                print(f"📊 文件大小: {size_mb:.1f} MB")
                return exe_path
            else:
                print("❌ 可执行文件未生成")
        else:
            print("❌ 构建失败:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ 构建过程中发生错误: {e}")
    
    return None

def create_installer():
    """创建安装程序"""
    installer_bat = '''@echo off
chcp 65001 >nul
echo 🏛️ EMC知识图谱系统 - 安装程序
echo ================================

set INSTALL_DIR=%LOCALAPPDATA%\\EMC知识图谱系统
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo 📁 复制程序文件...
copy "EMC知识图谱系统.exe" "%INSTALL_DIR%\\" >nul

echo 🔗 创建桌面快捷方式...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\EMC知识图谱系统.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\EMC知识图谱系统.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'EMC知识图谱系统 - 电磁兼容性知识管理平台'; $Shortcut.Save()" >nul

echo 📋 创建开始菜单项...
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\EMC工具" mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\EMC工具"
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\EMC工具\\EMC知识图谱系统.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\EMC知识图谱系统.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'EMC知识图谱系统'; $Shortcut.Save()" >nul

echo.
echo ✅ 安装完成!
echo.
echo 📍 程序位置: %INSTALL_DIR%
echo 🖥️ 桌面快捷方式已创建
echo 📋 开始菜单项已创建
echo.
echo 是否立即启动程序? (Y/N)
set /p choice=
if /i "%choice%"=="Y" start "" "%INSTALL_DIR%\\EMC知识图谱系统.exe"

echo.
echo 👋 感谢使用EMC知识图谱系统!
pause >nul
'''
    
    installer_file = Path("安装程序.bat")
    installer_file.write_text(installer_bat, encoding='utf-8')
    print(f"✅ 创建安装程序: {installer_file}")

def create_readme():
    """创建使用说明"""
    readme_content = '''# EMC知识图谱系统 - Windows桌面应用

## 🚀 快速开始

### 方法1: 直接运行
双击 `EMC知识图谱系统.exe` 立即启动

### 方法2: 完整安装  
1. 双击 `安装程序.bat`
2. 自动创建桌面快捷方式和开始菜单项
3. 程序安装到用户目录，无需管理员权限

## 💻 应用特性

- **🖥️ 原生界面**: 真正的Windows桌面应用
- **🌐 Web技术**: 内部使用现代Web界面
- **🔄 完整功能**: 支持知识图谱的所有核心功能
- **📱 响应式**: 界面自适应不同窗口大小
- **🔧 易部署**: 单文件可执行，无需额外安装

## 🎛️ 功能说明

### 主界面控制
- **启动**: 启动内置的EMC知识图谱API服务
- **停止**: 停止所有运行的后台服务  
- **状态**: 实时检查系统运行状态
- **浏览器**: 在外部浏览器中打开完整Web界面

### 系统监控
- **实时日志**: 显示系统运行状态和操作记录
- **统计面板**: 展示知识节点、关系连接等统计信息
- **运行时间**: 显示系统连续运行时间

## 🌐 Web界面访问

应用启动后，可通过以下方式访问完整功能:
- 点击应用内"浏览器"按钮
- 手动访问: http://localhost:8002
- API文档: http://localhost:8002/docs

## 🔧 系统要求

- **操作系统**: Windows 10/11 (64位)
- **内存**: 建议4GB以上
- **磁盘**: 100MB可用空间
- **网络**: 本地回环(无需互联网)

## 📊 技术架构

- **界面框架**: PyWebView (原生窗口)
- **前端技术**: HTML5 + CSS3 + JavaScript
- **后端API**: Python + FastAPI
- **数据处理**: 内置模拟数据 + 可扩展接口
- **打包工具**: PyInstaller

## 🛠️ 开发与扩展

本应用采用模块化设计，支持:
- 自定义知识图谱数据源
- 扩展API接口
- 定制界面主题
- 集成外部分析工具

## 🆘 故障排除

### 常见问题
1. **启动失败**: 检查端口8002是否被占用
2. **界面异常**: 尝试重启应用
3. **功能无响应**: 查看应用内日志信息

### 获取帮助
- 点击应用内"帮助"按钮
- 查看系统日志窗口
- 检查Windows事件查看器

---

🏛️ **EMC知识图谱系统 v1.0.0**  
专业的电磁兼容性知识管理与分析平台

开发团队: EMC知识图谱团队  
技术支持: 查看应用内帮助文档
'''
    
    readme_file = Path("使用说明.md")
    readme_file.write_text(readme_content, encoding='utf-8')
    print(f"✅ 创建使用说明: {readme_file}")

def main():
    """主函数"""
    print("🏛️ EMC知识图谱系统 - Windows应用构建工具")
    print("=" * 60)
    
    if not Path("emc_desktop_app.py").exists():
        print("❌ 找不到主应用文件 emc_desktop_app.py")
        return
    
    try:
        # 安装依赖
        install_requirements()
        
        # 构建可执行文件
        exe_path = build_exe()
        
        if exe_path:
            # 创建相关文件
            create_installer()
            create_readme()
            
            print("\n" + "=" * 60)
            print("🎉 Windows桌面应用构建完成!")
            
            print("\n📦 生成的文件:")
            print(f"   🖥️ 应用程序: {exe_path}")
            print(f"   ⚙️ 安装程序: 安装程序.bat")  
            print(f"   📖 使用说明: 使用说明.md")
            
            print("\n🚀 使用方法:")
            print("   1. 双击 EMC知识图谱系统.exe 直接运行")
            print("   2. 或运行 安装程序.bat 完整安装")
            
            print("\n✨ 应用特点:")
            print("   • 真正的Windows桌面应用")
            print("   • 内置Web服务，功能完整")
            print("   • 单文件可执行，部署简单")
            print("   • 支持最小化和窗口控制")
            
        else:
            print("\n❌ 构建失败，请检查错误信息")
            
    except Exception as e:
        print(f"\n❌ 构建过程中发生错误: {e}")

if __name__ == "__main__":
    main()