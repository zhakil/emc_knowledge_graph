#!/usr/bin/env python3
"""
EMC知识图谱 Windows应用构建脚本 - 重构版
===========================================

这个脚本采用了分层设计的理念，将构建过程分解为若干个独立的、可测试的模块。
每个模块都有明确的职责，这样可以更好地处理错误并提供清晰的日志输出。

设计思路：
1. 环境检查层：确保所有必要的工具和文件都存在
2. 构建层：分别处理后端、前端和Electron的构建
3. 打包层：创建最终的可分发应用
4. 错误处理层：提供详细的错误信息和恢复建议
"""

import os
import sys
import json
import shutil
import tempfile
import zipfile
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging


class BuildLogger:
    """
    构建日志管理器
    
    这个类负责统一管理构建过程中的所有日志输出，让用户能够清楚地
    了解构建进度和遇到的问题。我们使用不同的日志级别来区分信息的重要性。
    """
    
    def __init__(self):
        # 配置日志格式，让输出更加友好
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        self.logger = logging.getLogger(__name__)
    
    def info(self, message: str, emoji: str = "ℹ️"):
        """输出信息级别的日志"""
        self.logger.info(f"{emoji} {message}")
    
    def success(self, message: str):
        """输出成功信息"""
        self.logger.info(f"✅ {message}")
    
    def warning(self, message: str):
        """输出警告信息"""
        self.logger.warning(f"⚠️ {message}")
    
    def error(self, message: str):
        """输出错误信息"""
        self.logger.error(f"❌ {message}")
    
    def step(self, message: str):
        """输出构建步骤信息"""
        self.logger.info(f"🔧 {message}")


class EnvironmentChecker:
    """
    环境检查器
    
    在开始构建之前，我们需要确保所有必要的工具和文件都已准备就绪。
    这个类采用了"快速失败"的策略，一旦发现环境问题就立即停止，
    避免在后续步骤中浪费时间。
    """
    
    def __init__(self, project_root: Path, logger: BuildLogger):
        self.project_root = project_root
        self.logger = logger
    
    def check_all(self) -> bool:
        """
        执行所有环境检查
        
        这个方法按照依赖关系的顺序检查各种环境要求，
        确保每个检查都通过后再进行下一个。
        """
        self.logger.step("检查构建环境")
        
        try:
            self._check_tools()
            self._check_directories()
            self._check_files()
            self._check_dependencies()
            
            self.logger.success("环境检查通过")
            return True
            
        except EnvironmentError as e:
            self.logger.error(f"环境检查失败: {e}")
            return False
    
    def _check_tools(self):
        """
        检查必要的工具是否可用
        
        我们使用shutil.which()来查找可执行文件，这比硬编码路径更加灵活。
        对于Windows系统，我们还会检查.cmd和.exe后缀的变体。
        """
        required_tools = {
            'python': ['python', 'python3'],
            'node': ['node', 'node.exe'],
            'npm': ['npm', 'npm.cmd', 'npm.exe']
        }
        
        missing_tools = []
        
        for tool_name, possible_names in required_tools.items():
            found = False
            for name in possible_names:
                if shutil.which(name):
                    found = True
                    break
            
            if not found:
                missing_tools.append(tool_name)
        
        if missing_tools:
            raise EnvironmentError(
                f"缺少必要工具: {', '.join(missing_tools)}\n"
                f"请确保已安装 Python、Node.js 和 npm"
            )
    
    def _check_directories(self):
        """
        检查项目目录结构
        
        EMC知识图谱项目需要特定的目录结构才能正确构建。
        我们检查这些关键目录是否存在。
        """
        required_dirs = ['frontend', 'gateway', 'scripts']
        missing_dirs = []
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                missing_dirs.append(dir_name)
                
        if missing_dirs:
            raise EnvironmentError(
                f"缺少必要目录: {', '.join(missing_dirs)}\n"
                f"请确保在正确的项目根目录中运行此脚本"
            )
    
    def _check_files(self):
        """
        检查关键文件是否存在
        
        某些文件对于构建过程至关重要，我们需要在开始之前确认它们存在。
        """
        critical_files = [
            'frontend/package.json',
            'gateway/main.py'
        ]
        
        missing_files = []
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            raise EnvironmentError(
                f"缺少关键文件: {', '.join(missing_files)}\n"
                f"请检查项目完整性"
            )
    
    def _check_dependencies(self):
        """
        检查Python依赖是否满足要求
        
        我们检查是否能够导入关键的Python模块，这有助于提前发现依赖问题。
        """
        try:
            try:
                import uvicorn
            except ImportError:
                raise EnvironmentError(
                    "未找到 'uvicorn' 模块。请运行 'pip install uvicorn' 安装依赖。"
                )
            try:
                import fastapi
            except ImportError:
                raise EnvironmentError(
                    "未找到 'fastapi' 模块。请运行 'pip install fastapi' 安装依赖。"
                )
        except ImportError as e:
            raise EnvironmentError(
                f"Python依赖检查失败: {e}\n"
                f"请运行 'pip install -r requirements.txt' 安装依赖"
            )


class NPMManager:
    """
    NPM管理器
    
    这个类专门处理与NPM相关的操作。我们将NPM逻辑封装到单独的类中，
    是因为不同操作系统和Node.js安装方式可能导致NPM路径不同。
    """
    
    def __init__(self, logger: BuildLogger):
        self.logger = logger
        self.npm_path = self._find_npm_executable()
    
    def _find_npm_executable(self) -> str:
        """
        智能查找NPM可执行文件
        
        这个方法使用多种策略来定位NPM，确保在不同环境下都能工作。
        我们优先使用系统PATH中的npm，然后尝试常见的安装位置。
        """
        # 首先尝试从PATH中查找
        npm_candidates = ['npm', 'npm.cmd', 'npm.exe']
        
        for candidate in npm_candidates:
            npm_path = shutil.which(candidate)
            if npm_path:
                self.logger.info(f"找到NPM: {npm_path}")
                return npm_path
        
        # 如果PATH中没有，尝试Windows的常见安装位置
        if os.name == 'nt':  # Windows
            common_paths = [
                r"C:\Program Files\nodejs\npm.cmd",
                r"C:\Program Files (x86)\nodejs\npm.cmd",
                os.path.expanduser(r"~\AppData\Roaming\npm\npm.cmd")
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    self.logger.info(f"找到NPM: {path}")
                    return path
        
        raise EnvironmentError(
            "无法找到NPM可执行文件\n"
            "请确保Node.js已正确安装并添加到系统PATH中"
        )
    
    def run_command(self, command: List[str], cwd: Path) -> subprocess.CompletedProcess:
        """
        执行NPM命令
        
        这个方法统一处理NPM命令的执行，包括错误处理和输出捕获。
        我们使用shell=True来确保在Windows上正确执行。
        """
        full_command = [self.npm_path] + command
        
        self.logger.info(f"执行命令: {' '.join(full_command)}")
        
        try:
            # 在Windows上使用shell=True，在Unix系统上不需要
            shell = os.name == 'nt'
            
            result = subprocess.run(
                full_command,
                cwd=cwd,
                shell=shell,
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            # 输出命令执行的结果，帮助调试
            if result.stdout:
                self.logger.info(f"命令输出: {result.stdout[:200]}...")
            
            return result
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"NPM命令执行失败: {e}")
            if e.stdout:
                self.logger.error(f"标准输出: {e.stdout}")
            if e.stderr:
                self.logger.error(f"错误输出: {e.stderr}")
            raise


class BackendBuilder:
    """
    后端构建器
    
    负责将Python后端应用打包成独立的可执行文件。
    我们使用PyInstaller来创建不依赖Python环境的可执行文件。
    """
    
    def __init__(self, project_root: Path, logger: BuildLogger):
        self.project_root = project_root
        self.logger = logger
        self.temp_dir = None
    
    def build(self, output_dir: Path) -> bool:
        """
        构建后端可执行文件
        
        这个过程包括：
        1. 创建临时的入口脚本
        2. 安装PyInstaller
        3. 使用PyInstaller打包应用
        4. 将结果复制到指定位置
        """
        self.logger.step("开始构建后端服务")
        
        try:
            self._create_temp_directory()
            self._install_pyinstaller()
            self._create_gateway_script()
            self._run_pyinstaller(output_dir)
            
            self.logger.success("后端构建完成")
            return True
            
        except Exception as e:
            self.logger.error(f"后端构建失败: {e}")
            return False
        finally:
            self._cleanup()
    
    def _create_temp_directory(self):
        """创建临时工作目录"""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="emc_backend_"))
        self.logger.info(f"创建临时目录: {self.temp_dir}")
    
    def _install_pyinstaller(self):
        """安装PyInstaller"""
        self.logger.info("安装PyInstaller...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "pyinstaller"
        ], check=True, capture_output=True)
    
    def _create_gateway_script(self):
        """
        创建网关入口脚本
        
        我们创建一个简单的启动脚本，它导入并运行FastAPI应用。
        这个脚本是PyInstaller的入口点。
        """
        gateway_script_content = '''
import sys
import os

# 确保项目根目录在Python路径中
sys.path.insert(0, os.path.dirname(__file__))

try:
    from gateway.main import app
    import uvicorn
    
    if __name__ == "__main__":
        print("🚀 启动EMC知识图谱后端服务...")
        print("📍 服务地址: http://127.0.0.1:8000")
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
        
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保所有依赖都已正确安装")
    sys.exit(1)
'''
        
        gateway_script_path = self.project_root / "gateway_standalone.py"
        gateway_script_path.write_text(gateway_script_content, encoding='utf-8')
        self.logger.info(f"创建网关脚本: {gateway_script_path}")
    
    def _run_pyinstaller(self, output_dir: Path):
        """
        运行PyInstaller进行打包
        
        我们使用--onefile选项创建单个可执行文件，这样分发更方便。
        同时设置合适的工作目录和输出目录。
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        pyinstaller_command = [
            "pyinstaller",
            "--onefile",
            "--name", "emc_backend",
            "--distpath", str(output_dir),
            "--workpath", str(self.temp_dir / "backend_build"),
            "--specpath", str(self.temp_dir),
            str(self.project_root / "gateway_standalone.py")
        ]
        
        self.logger.info("开始PyInstaller打包...")
        subprocess.run(pyinstaller_command, cwd=self.project_root, check=True)
    
    def _cleanup(self):
        """清理临时文件"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            self.logger.info("清理临时文件")


class FrontendBuilder:
    """
    前端构建器
    
    负责构建React前端应用。我们使用标准的npm构建流程，
    但加强了错误处理和环境适配。
    """
    
    def __init__(self, project_root: Path, logger: BuildLogger):
        self.project_root = project_root
        self.logger = logger
        self.npm_manager = NPMManager(logger)
        self.frontend_dir = project_root / "frontend"
    
    def build(self, output_dir: Path) -> bool:
        """
        构建前端应用
        
        执行标准的React构建流程：npm install -> npm run build
        然后将构建结果复制到指定位置。
        """
        self.logger.step("开始构建前端应用")
        
        try:
            self._install_dependencies()
            self._build_application()
            self._copy_build_output(output_dir)
            
            self.logger.success("前端构建完成")
            return True
            
        except Exception as e:
            self.logger.error(f"前端构建失败: {e}")
            return False
    
    def _install_dependencies(self):
        """安装Node.js依赖"""
        self.logger.info("安装前端依赖...")
        self.npm_manager.run_command(["install"], self.frontend_dir)
    
    def _build_application(self):
        """构建React应用"""
        self.logger.info("构建React应用...")
        self.npm_manager.run_command(["run", "build"], self.frontend_dir)
    
    def _copy_build_output(self, output_dir: Path):
        """
        复制构建输出
        
        将React的构建结果复制到Electron应用的目录中。
        我们首先清理目标目录，确保没有旧文件干扰。
        """
        build_src = self.frontend_dir / "build"
        build_dst = output_dir / "build"
        
        if not build_src.exists():
            raise FileNotFoundError(f"前端构建输出目录不存在: {build_src}")
        
        if build_dst.exists():
            shutil.rmtree(build_dst)
            
        shutil.copytree(build_src, build_dst)
        self.logger.info(f"复制构建结果: {build_src} -> {build_dst}")


class ElectronBuilder:
    """
    Electron应用构建器
    
    负责设置Electron环境并构建桌面应用。Electron让我们能够
    将Web应用打包成原生桌面应用。
    """
    
    def __init__(self, project_root: Path, logger: BuildLogger):
        self.project_root = project_root
        self.logger = logger
        self.npm_manager = NPMManager(logger)
        self.desktop_dir = project_root / "desktop"
    
    def build(self, backend_dir: Path, frontend_dir: Path, output_dir: Path) -> bool:
        """
        构建Electron应用
        
        这个过程包括设置Electron环境、创建必要的配置文件，
        然后使用electron-builder创建可分发的应用。
        """
        self.logger.step("开始构建Electron应用")
        
        try:
            self._setup_desktop_directory()
            self._create_electron_files()
            self._install_electron_dependencies()
            self._build_electron_app()
            self._copy_output(output_dir)
            
            self.logger.success("Electron应用构建完成")
            return True
            
        except Exception as e:
            self.logger.error(f"Electron构建失败: {e}")
            return False
    
    def _setup_desktop_directory(self):
        """设置桌面应用目录"""
        self.desktop_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建资源目录
        (self.desktop_dir / "resources").mkdir(exist_ok=True)
        (self.desktop_dir / "assets").mkdir(exist_ok=True)
    
    def _create_electron_files(self):
        """
        创建Electron配置文件
        
        我们创建必要的Electron文件，包括主进程脚本、预加载脚本
        和package.json配置文件。
        """
        self._create_main_js()
        self._create_preload_js()
        self._create_package_json()
        self._create_default_icon()
    
    def _create_main_js(self):
        """创建Electron主进程脚本"""
        main_js_content = '''
const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let backendProcess;

function createWindow() {
    // 创建浏览器窗口
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: path.join(__dirname, 'assets', 'icon.ico')
    });

    // 加载应用
    mainWindow.loadFile('build/index.html');

    // 开发时打开开发者工具
    if (process.env.NODE_ENV === 'development') {
        mainWindow.webContents.openDevTools();
    }
}

function startBackendServer() {
    const backendPath = path.join(__dirname, 'resources', 'backend', 'emc_backend.exe');
    
    backendProcess = spawn(backendPath, {
        detached: false,
        stdio: 'pipe'
    });

    backendProcess.stdout.on('data', (data) => {
        console.log(`后端服务: ${data}`);
    });

    backendProcess.stderr.on('data', (data) => {
        console.error(`后端错误: ${data}`);
    });
}

// 应用准备就绪时的处理
app.whenReady().then(() => {
    startBackendServer();
    createWindow();

    app.on('activate', function () {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

// 所有窗口关闭时的处理
app.on('window-all-closed', function () {
    if (backendProcess) {
        backendProcess.kill();
    }
    
    if (process.platform !== 'darwin') app.quit();
});
'''
        
        main_js_path = self.desktop_dir / "main.js"
        main_js_path.write_text(main_js_content, encoding='utf-8')
    
    def _create_preload_js(self):
        """创建预加载脚本"""
        preload_content = '''
const { contextBridge, ipcRenderer } = require('electron');

// 为渲染进程暴露安全的API
contextBridge.exposeInMainWorld('electronAPI', {
    // 文件操作相关
    onFilesSelected: (callback) => ipcRenderer.on('files-selected', callback),
    onExportData: (callback) => ipcRenderer.on('export-data', callback),
    
    // 应用信息
    getVersion: () => ipcRenderer.invoke('get-version'),
    
    // 通知渲染进程
    showNotification: (title, body) => {
        new Notification(title, { body });
    }
});
'''
        
        preload_path = self.desktop_dir / "preload.js"
        preload_path.write_text(preload_content, encoding='utf-8')
    
    def _create_package_json(self):
        """创建Electron项目的package.json"""
        package_config = {
            "name": "emc-knowledge-graph-desktop",
            "version": "1.0.0",
            "description": "EMC知识图谱桌面应用",
            "main": "main.js",
            "author": "EMC Team",
            "license": "MIT",
            "scripts": {
                "start": "electron .",
                "dist": "electron-builder",
                "dist:win": "electron-builder --win"
            },
            "build": {
                "appId": "com.emc.knowledge-graph",
                "productName": "EMC知识图谱系统",
                "directories": {
                    "output": "dist"
                },
                "files": [
                    "build/**/*",
                    "resources/**/*",
                    "assets/**/*",
                    "main.js",
                    "preload.js"
                ],
                "win": {
                    "target": [
                        {
                            "target": "nsis",
                            "arch": ["x64"]
                        },
                        {
                            "target": "portable",
                            "arch": ["x64"]
                        }
                    ],
                    "icon": "assets/icon.ico"
                },
                "nsis": {
                    "oneClick": False,
                    "allowToChangeInstallationDirectory": True,
                    "installerIcon": "assets/icon.ico",
                    "uninstallerIcon": "assets/icon.ico",
                    "installerHeaderIcon": "assets/icon.ico",
                    "createDesktopShortcut": True,
                    "createStartMenuShortcut": True
                }
            },
            "devDependencies": {
                "electron": "^28.0.0",
                "electron-builder": "^24.9.1"
            }
        }
        
        package_path = self.desktop_dir / "package.json"
        package_path.write_text(json.dumps(package_config, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def _create_default_icon(self):
        """
        创建默认应用图标
        
        这里我们创建一个简单的ICO文件。在实际项目中，
        你应该使用专业设计的图标文件。
        """
        icon_path = self.desktop_dir / "assets" / "icon.ico"
        
        # 创建一个最小的有效ICO文件
        # 这只是一个占位符，实际使用中应该替换为真正的图标
        ico_header = b'\\x00\\x00\\x01\\x00\\x01\\x00'  # ICO文件头
        ico_data = ico_header + b'\\x20\\x20\\x00\\x00\\x01\\x00\\x08\\x00\\xe8\\x02\\x00\\x00\\x16\\x00\\x00\\x00'
        
        icon_path.write_bytes(ico_data)
        self.logger.info(f"创建默认图标: {icon_path}")
    
    def _install_electron_dependencies(self):
        """安装Electron相关依赖"""
        self.logger.info("安装Electron依赖...")
        self.npm_manager.run_command(["install"], self.desktop_dir)
    
    def _build_electron_app(self):
        """使用electron-builder构建应用"""
        self.logger.info("使用electron-builder构建应用...")
        self.npm_manager.run_command(["run", "dist"], self.desktop_dir)
    
    def _copy_output(self, output_dir: Path):
        """复制构建输出到最终目录"""
        electron_dist = self.desktop_dir / "dist"
        
        if not electron_dist.exists():
            raise FileNotFoundError("Electron构建输出目录不存在")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制所有构建产物
        for item in electron_dist.iterdir():
            if item.is_file():
                shutil.copy2(item, output_dir)
            elif item.is_dir():
                target = output_dir / item.name
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(item, target)
        
        self.logger.info(f"复制构建输出到: {output_dir}")


class WindowsAppBuilder:
    """
    Windows应用主构建器
    
    这是整个构建过程的协调者，它组织和管理各个子构建器的工作。
    采用了设计模式中的"外观模式"，为复杂的构建过程提供简单的接口。
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.build_dir = self.project_root / "build"
        self.desktop_dir = self.project_root / "desktop"
        
        # 初始化日志系统
        self.logger = BuildLogger()
        
        # 初始化各种构建器
        self.env_checker = EnvironmentChecker(self.project_root, self.logger)
        self.backend_builder = BackendBuilder(self.project_root, self.logger)
        self.frontend_builder = FrontendBuilder(self.project_root, self.logger)
        self.electron_builder = ElectronBuilder(self.project_root, self.logger)
    
    def build(self) -> bool:
        """
        执行完整的构建流程
        
        这个方法是整个构建过程的入口点。它按照正确的顺序
        执行各个构建步骤，并在出错时提供有用的错误信息。
        """
        self.logger.info("🚀 开始构建EMC知识图谱Windows应用", "🚀")
        
        try:
            # 第一步：环境检查
            if not self.env_checker.check_all():
                return False
            
            # 第二步：准备构建目录
            self._prepare_build_directories()
            
            # 第三步：构建后端
            backend_output = self.desktop_dir / "resources" / "backend"
            if not self.backend_builder.build(backend_output):
                return False
            
            # 第四步：构建前端
            if not self.frontend_builder.build(self.desktop_dir):
                return False
            
            # 第五步：构建Electron应用
            if not self.electron_builder.build(backend_output, self.desktop_dir, self.build_dir):
                return False
            
            # 第六步：创建便携版
            self._create_portable_version()
            
            self._show_build_summary()
            return True
            
        except Exception as e:
            self.logger.error(f"构建过程中发生未预期的错误: {e}")
            return False
        finally:
            self._cleanup()
    
    def _prepare_build_directories(self):
        """
        准备构建目录
        
        清理并创建所有必要的构建目录，确保构建过程有干净的工作环境。
        """
        self.logger.step("准备构建目录")
        
        # 清理旧的构建输出
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        
        # 创建必要的目录
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.desktop_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.success("构建目录准备完成")
    
    def _create_portable_version(self):
        """
        创建便携版应用
        
        便携版应用可以直接运行，无需安装，这对于某些用户来说更方便。
        """
        self.logger.step("创建便携版应用")
        
        try:
            # 查找win-unpacked目录
            possible_dirs = [
                self.build_dir / "win-unpacked",
                self.desktop_dir / "dist" / "win-unpacked"
            ]
            
            unpacked_dir = None
            for dir_path in possible_dirs:
                if dir_path.exists():
                    unpacked_dir = dir_path
                    break
            
            if not unpacked_dir:
                self.logger.warning("未找到win-unpacked目录，跳过便携版创建")
                return
            
            # 创建便携版目录
            portable_dir = self.build_dir / "EMC_Knowledge_Graph_Portable"
            if portable_dir.exists():
                shutil.rmtree(portable_dir)
            
            shutil.copytree(unpacked_dir, portable_dir)
            
            # 创建启动脚本
            start_script = portable_dir / "启动EMC知识图谱.bat"
            start_script_content = '''@echo off
echo 正在启动EMC知识图谱系统...
echo 请等待应用加载完成...
start "" "EMC知识图谱系统.exe"
'''
            start_script.write_text(start_script_content, encoding='gbk')
            
            # 创建便携版压缩包
            portable_zip = self.build_dir / "EMC_Knowledge_Graph_Portable.zip"
            with zipfile.ZipFile(portable_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in portable_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(portable_dir)
                        zf.write(file_path, arcname)
            
            self.logger.success(f"便携版创建完成: {portable_zip}")
            
        except Exception as e:
            self.logger.warning(f"便携版创建失败: {e}")
    
    def _show_build_summary(self):
        """显示构建摘要信息"""
        self.logger.info("", "")  # 空行分隔
        self.logger.success("🎉 Windows应用构建完成!")
        self.logger.info(f"📁 输出目录: {self.build_dir}")
        
        # 列出生成的文件
        if self.build_dir.exists():
            self.logger.info("📦 生成的文件:")
            for item in self.build_dir.iterdir():
                if item.is_file():
                    size = item.stat().st_size / (1024 * 1024)  # MB
                    self.logger.info(f"   📄 {item.name} ({size:.1f} MB)")
                elif item.is_dir():
                    self.logger.info(f"   📁 {item.name}/")
    
    def _cleanup(self):
        """清理临时文件和目录"""
        # 清理临时创建的网关脚本
        gateway_script = self.project_root / "gateway_standalone.py"
        if gateway_script.exists():
            gateway_script.unlink()
        
        # 清理其他临时文件
        temp_files = [
            self.project_root / "emc_backend.spec"
        ]
        
        for temp_file in temp_files:
            if temp_file.exists():
                temp_file.unlink()


def main():
    """
    主函数 - 程序入口点
    
    这个函数是整个构建脚本的入口。它创建构建器实例并执行构建过程，
    然后根据构建结果设置适当的退出代码。
    """
    builder = WindowsAppBuilder()
    success = builder.build()
    
    # 根据构建结果设置退出代码
    # 这对于CI/CD系统识别构建状态很重要
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()