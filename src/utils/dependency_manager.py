"""
智能依赖管理器
解决依赖冲突和按需加载问题
"""
import importlib
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
import yaml

class DependencyManager:
    """智能依赖管理和按需安装"""
    
    def __init__(self, config_path: str = "config/dependencies.yaml"):
        self.config_path = Path(config_path)
        self.dependencies = self._load_dependencies()
        self._installed_cache = {}
    
    def _load_dependencies(self) -> Dict:
        """加载依赖配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def ensure_core_dependencies(self) -> bool:
        """确保核心依赖已安装"""
        return self._install_dependency_group("core_dependencies")
    
    def lazy_import_with_fallback(self, module_name: str, 
                                 fallback_func: Optional[callable] = None):
        """延迟导入，支持优雅降级"""
        try:
            return importlib.import_module(module_name)
        except ImportError as e:
            if fallback_func:
                return fallback_func()
            raise ImportError(f"模块 {module_name} 未安装，请运行: pip install {module_name}")
    
    def _install_dependency_group(self, group_name: str) -> bool:
        """安装指定依赖组"""
        if group_name not in self.dependencies:
            return False
            
        deps = self.dependencies[group_name]
        for dep in deps:
            if not self._is_installed(dep):
                success = self._install_package(dep)
                if not success:
                    return False
        return True
    
    def _is_installed(self, package_spec: str) -> bool:
        """检查包是否已安装"""
        package_name = package_spec.split(">=")[0].split("==")[0]
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            return False
    
    def _install_package(self, package_spec: str) -> bool:
        """安装单个包"""
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                package_spec, "--timeout", "30"
            ])
            return True
        except subprocess.CalledProcessError:
            return False

# 全局依赖管理器实例
dep_manager = DependencyManager()