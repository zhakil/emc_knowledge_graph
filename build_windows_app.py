#!/usr/bin/env python3
"""
构建Windows可执行文件的脚本
使用PyInstaller打包EMC知识图谱应用
"""

import subprocess
import sys
import os
from pathlib import Path

def install_pyinstaller():
    """安装PyInstaller"""
    print("📦 安装PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ PyInstaller安装失败")
        return False

def create_spec_file():
    """创建PyInstaller规格文件"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['emc_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('standalone-demo.html', '.'),
        ('local-demo.html', '.'),
        ('DOCKER_DEPLOYMENT.md', '.'),
        ('docker-compose.community.yml', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'webbrowser',
        'subprocess',
        'threading',
        'socket',
        'pathlib',
        'json',
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
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    spec_file = Path("emc_app.spec")
    spec_file.write_text(spec_content.strip())
    print(f"✅ 创建规格文件: {spec_file}")
    return spec_file

def build_executable():
    """构建可执行文件"""
    print("🔨 构建Windows可执行文件...")
    
    spec_file = create_spec_file()
    
    try:
        # 使用PyInstaller构建
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", str(spec_file)]
        subprocess.run(cmd, check=True)
        
        exe_path = Path("dist") / "EMC知识图谱系统.exe"
        if exe_path.exists():
            print(f"✅ 构建成功: {exe_path}")
            print(f"📁 文件大小: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
            return exe_path
        else:
            print("❌ 可执行文件未生成")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return None

def create_installer_script():
    """创建安装脚本"""
    installer_content = '''@echo off
echo 🏛️ EMC知识图谱系统 - 安装程序
echo ================================

:: 创建程序目录
set INSTALL_DIR=%USERPROFILE%\\EMC知识图谱系统
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: 复制文件
echo 📁 复制程序文件...
copy "EMC知识图谱系统.exe" "%INSTALL_DIR%\\"
copy "standalone-demo.html" "%INSTALL_DIR%\\" 2>nul
copy "DOCKER_DEPLOYMENT.md" "%INSTALL_DIR%\\" 2>nul

:: 创建桌面快捷方式
echo 🔗 创建桌面快捷方式...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\EMC知识图谱系统.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\EMC知识图谱系统.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'EMC知识图谱系统'; $Shortcut.Save()"

:: 创建开始菜单快捷方式
echo 📋 创建开始菜单快捷方式...
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\EMC知识图谱系统" mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\EMC知识图谱系统"
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\EMC知识图谱系统\\EMC知识图谱系统.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\EMC知识图谱系统.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'EMC知识图谱系统'; $Shortcut.Save()"

echo.
echo ✅ 安装完成！
echo.
echo 📍 安装位置: %INSTALL_DIR%
echo 🖥️ 桌面快捷方式已创建
echo 📋 开始菜单快捷方式已创建
echo.
echo 按任意键启动程序...
pause >nul
start "" "%INSTALL_DIR%\\EMC知识图谱系统.exe"
'''
    
    installer_file = Path("installer.bat")
    installer_file.write_text(installer_content)
    print(f"✅ 创建安装脚本: {installer_file}")
    return installer_file

def create_readme():
    """创建说明文件"""
    readme_content = '''# EMC知识图谱系统 - Windows应用

## 🚀 快速开始

### 方法1: 直接运行
双击 `EMC知识图谱系统.exe` 即可启动

### 方法2: 完整安装
1. 双击运行 `installer.bat`
2. 自动创建桌面和开始菜单快捷方式
3. 程序将安装到用户目录

## 🎯 应用功能

- **🏠 系统控制**: 启动/停止后端服务
- **🌐 Web界面**: 一键打开前端页面
- **📊 API文档**: 查看完整API文档
- **🎨 演示模式**: 离线演示功能
- **⚡ 健康检查**: 实时监控系统状态
- **📋 系统日志**: 实时查看运行日志

## 📱 访问地址

启动后可通过以下地址访问:
- 前端界面: http://localhost:3002
- API文档: http://localhost:8001/docs
- 健康检查: http://localhost:8001/health

## 🔧 系统要求

- Windows 10/11
- 无需额外安装Python或其他依赖
- 建议4GB以上内存

## 🆘 故障排除

1. **端口被占用**: 关闭其他使用8001/3002端口的程序
2. **防火墙拦截**: 允许程序通过Windows防火墙
3. **权限问题**: 以管理员身份运行

## 📞 技术支持

如遇问题请查看:
- 应用内的系统日志
- DOCKER_DEPLOYMENT.md 详细文档
- 或使用演示模式进行离线体验

---
EMC知识图谱系统 v1.0.0
'''
    
    readme_file = Path("README_Windows.md")
    readme_file.write_text(readme_content)
    print(f"✅ 创建说明文件: {readme_file}")
    return readme_file

def main():
    """主函数"""
    print("🏛️ EMC知识图谱系统 - Windows应用构建工具")
    print("=" * 50)
    
    # 检查是否存在主应用文件
    if not Path("emc_app.py").exists():
        print("❌ 找不到 emc_app.py 文件")
        return
    
    # 安装PyInstaller
    if not install_pyinstaller():
        return
    
    # 构建可执行文件
    exe_path = build_executable()
    if not exe_path:
        return
    
    # 创建相关文件
    create_installer_script()
    create_readme()
    
    print("\n" + "=" * 50)
    print("🎉 Windows应用构建完成！")
    print("\n📦 生成的文件:")
    print(f"   🖥️ 可执行文件: {exe_path}")
    print(f"   📄 安装脚本: installer.bat")
    print(f"   📖 说明文档: README_Windows.md")
    
    print("\n🚀 使用方法:")
    print("   1. 直接双击运行 EMC知识图谱系统.exe")
    print("   2. 或运行 installer.bat 进行完整安装")
    
    print("\n💡 提示:")
    print("   • 可执行文件包含了所有必要的依赖")
    print("   • 首次运行可能需要Windows防火墙确认")
    print("   • 支持离线演示模式")

if __name__ == "__main__":
    main()