#!/usr/bin/env python3
"""
EMC Knowledge Graph Build System
知识图谱构建自动化系统

基于DevOps理念的知识图谱项目构建管道，集成代码质量检查、
测试执行、图谱生成和部署发布的完整工作流。

核心构建策略：
• 依赖管理与环境隔离
• 持续集成的质量门禁
• 知识图谱增量构建优化
• 多目标平台交付支持

Author: EMC Standards Research Team
Version: 1.0.0
"""

import os
import sys
import subprocess
import argparse
import shutil
import time
from pathlib import Path
from typing import List, Dict, Optional, Callable
import logging
from datetime import datetime
import json

# 构建系统配置
BUILD_CONFIG = {
    'python_version': '3.8+',
    'venv_name': 'venv',
    'requirements_file': 'requirements.txt',
    'test_pattern': 'tests/',
    'coverage_threshold': 85,
    'output_formats': ['png', 'html', 'json', 'graphml']
}

class BuildSystemError(Exception):
    """构建系统异常"""
    pass

class KnowledgeGraphBuilder:
    """
    知识图谱构建引擎
    
    实现面向知识图谱的专用构建系统，支持增量构建、
    依赖追踪和质量评估的完整构建生命周期管理。
    """
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent
        self.build_start = datetime.now()
        self.setup_logging()
        
        # 构建上下文
        self.build_context = {
            'platform': sys.platform,
            'python_version': sys.version,
            'project_root': str(self.project_root),
            'timestamp': self.build_start.isoformat()
        }
        
        logger.info(f"初始化知识图谱构建系统 - {self.project_root}")
        
    def setup_logging(self):
        """配置构建日志系统 - 知识图谱专用Unicode安全版本"""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # 知识图谱构建专用格式化器
        class KGBuildFormatter(logging.Formatter):
            def format(self, record):
                msg = super().format(record)
                # EMC知识图谱构建符号映射
                kg_symbols = {
                    '🧠': '[KG-BUILD]',     # 知识图谱构建
                    '🔍': '[VALIDATE]',     # 环境验证  
                    '📊': '[REPORT]',       # 构建报告
                    '🔧': '[QUALITY]',      # 代码质量
                    '🧪': '[TEST]',         # 测试执行
                    '✓': '[OK]',            # 成功
                    '✗': '[FAIL]',          # 失败
                    '📦': '[PACKAGE]',      # 打包
                    '📚': '[DOCS]',         # 文档生成
                    '🧹': '[CLEAN]',        # 清理
                    '🚀': '[START]',        # 启动
                    '⚡': '[STEP]',          # 执行步骤
                    '✅': '[SUCCESS]',      # 构建成功
                    '❌': '[ERROR]',        # 构建失败
                    '🛑': '[STOP]'          # 停止
                }
                for symbol, replacement in kg_symbols.items():
                    msg = msg.replace(symbol, replacement)
                return msg
        
        formatter = KGBuildFormatter('%(asctime)s - BUILD - %(levelname)s - %(message)s')
        
        # 控制台输出 - 兼容Windows GBK
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        # 文件输出 - UTF-8编码
        file_handler = logging.FileHandler(
            log_dir / f"build_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        
        logging.basicConfig(
            level=logging.INFO,
            handlers=[console_handler, file_handler]
        )
        
        global logger
        logger = logging.getLogger(__name__)
    def validate_environment(self) -> bool:
        """环境依赖验证"""
        logger.info("🔍 环境依赖验证")
        
        checks = [
            ('Python版本', self._check_python_version),
            ('Git可用性', self._check_git_available),
            ('项目结构', self._check_project_structure),
            ('核心依赖', self._check_core_dependencies)
        ]
        
        for check_name, check_func in checks:
            try:
                if check_func():
                    logger.info(f"  ✓ {check_name}")
                else:
                    logger.error(f"  ✗ {check_name}")
                    return False
            except Exception as e:
                logger.error(f"  ✗ {check_name}: {e}")
                return False
        
        return True
    
    def _check_python_version(self) -> bool:
        """检查Python版本兼容性"""
        return sys.version_info >= (3, 8)
    
    def _check_git_available(self) -> bool:
        """检查Git可用性"""
        try:
            subprocess.run(['git', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_project_structure(self) -> bool:
        """验证项目结构完整性"""
        required_paths = [
            'src',
            'requirements.txt',
            'config.yaml',
            'src/knowledge_graph.py',
            'src/data_models.py'
        ]
        
        for path in required_paths:
            if not (self.project_root / path).exists():
                logger.error(f"缺少必需文件/目录: {path}")
                return False
        
        return True
    
    def _check_core_dependencies(self) -> bool:
        """检查核心依赖可用性"""
        core_modules = ['networkx', 'matplotlib', 'plotly', 'pandas', 'yaml']
        
        for module in core_modules:
            try:
                __import__(module)
            except ImportError:
                logger.warning(f"核心模块未安装: {module}")
                return False
        
        return True
    
    def create_virtual_environment(self) -> bool:
        """创建虚拟环境"""
        venv_path = self.project_root / BUILD_CONFIG['venv_name']
        
        if venv_path.exists():
            logger.info("🔄 虚拟环境已存在，跳过创建")
            return True
        
        logger.info("🏗️ 创建Python虚拟环境")
        
        try:
            subprocess.run([
                sys.executable, '-m', 'venv', str(venv_path)
            ], check=True, cwd=self.project_root)
            
            logger.info(f"  ✓ 虚拟环境创建完成: {venv_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"虚拟环境创建失败: {e}")
            return False
    
    def install_dependencies(self, minimal: bool = False, timeout: int = 60):
        """智能分阶段依赖安装"""
        logger.info(f"📦 {'最小' if minimal else '完整'}依赖安装")
        
        pip_cmd = self._get_pip_command()
        
        try:
            if minimal:
                # 仅安装核心依赖
                core_deps = [
                    "networkx>=3.1,<4.0",
                    "pyyaml>=6.0,<7.0", 
                    "numpy>=1.24.0,<2.0"
                ]
                
                for dep in core_deps:
                    logger.info(f"  安装核心依赖: {dep}")
                    result = subprocess.run([
                        pip_cmd, 'install', dep,
                        '--timeout', str(timeout),
                        '--retries', '2'
                    ], capture_output=True, text=True, timeout=timeout)
                    
                    if result.returncode != 0:
                        logger.error(f"核心依赖安装失败: {dep}")
                        return False
            else:
                # 分组安装完整依赖
                dep_groups = {
                    "core": ["networkx>=3.1", "pyyaml>=6.0", "numpy>=1.24.0"],
                    "visualization": ["matplotlib>=3.7.0", "plotly>=5.15.0"],  
                    "development": ["pytest>=7.4.0", "black>=23.7.0", "mypy>=1.5.0"]
                }
                
                for group_name, deps in dep_groups.items():
                    logger.info(f"  安装 {group_name} 依赖组...")
                    for dep in deps:
                        result = subprocess.run([
                            pip_cmd, 'install', dep,
                            '--timeout', str(timeout//2),
                            '--retries', '1'
                        ], capture_output=True, text=True)
                        
                        if result.returncode != 0:
                            logger.warning(f"可选依赖安装失败: {dep}")
            
            logger.info("  ✓ 依赖安装完成")
            return True
            
        except Exception as e:
            logger.error(f"依赖安装异常: {e}")
            return False
    def execute_code_quality_checks(self) -> Dict[str, bool]:
        """代码质量检查管道"""
        logger.info("🔧 执行代码质量检查")
        
        quality_checks = {
            'formatting': self._run_black_formatting,
            'linting': self._run_flake8_linting,
            'type_checking': self._run_mypy_typing,
            'import_sorting': self._run_isort_imports
        }
        
        results = {}
        for check_name, check_func in quality_checks.items():
            try:
                results[check_name] = check_func()
                status = "✓" if results[check_name] else "✗"
                logger.info(f"  {status} {check_name}")
            except Exception as e:
                logger.error(f"  ✗ {check_name}: {e}")
                results[check_name] = False
        
        return results
    
    def _run_black_formatting(self) -> bool:
        """Black代码格式化"""
        python_cmd = self._get_python_command()
        try:
            subprocess.run([
                python_cmd, '-m', 'black', 
                'src/', 'tests/', 
                '--line-length', '88',
                '--check'
            ], check=True, capture_output=True, cwd=self.project_root)
            return True
        except subprocess.CalledProcessError:
            # 尝试自动格式化
            subprocess.run([
                python_cmd, '-m', 'black', 
                'src/', 'tests/', 
                '--line-length', '88'
            ], cwd=self.project_root)
            return True
    
    def _run_flake8_linting(self) -> bool:
        """Flake8代码检查"""
        python_cmd = self._get_python_command()
        try:
            subprocess.run([
                python_cmd, '-m', 'flake8',
                'src/', 'tests/',
                '--max-line-length=88',
                '--extend-ignore=E203,W503'
            ], check=True, capture_output=True, cwd=self.project_root)
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(f"代码风格问题: {e.stderr.decode() if e.stderr else ''}")
            return False
    
    def _run_mypy_typing(self) -> bool:
        """MyPy类型检查"""
        python_cmd = self._get_python_command()
        try:
            subprocess.run([
                python_cmd, '-m', 'mypy',
                'src/',
                '--ignore-missing-imports'
            ], check=True, capture_output=True, cwd=self.project_root)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _run_isort_imports(self) -> bool:
        """isort导入排序"""
        python_cmd = self._get_python_command()
        try:
            subprocess.run([
                python_cmd, '-m', 'isort',
                'src/', 'tests/',
                '--profile', 'black',
                '--check-only'
            ], check=True, capture_output=True, cwd=self.project_root)
            return True
        except subprocess.CalledProcessError:
            # 自动修复导入排序
            subprocess.run([
                python_cmd, '-m', 'isort',
                'src/', 'tests/',
                '--profile', 'black'
            ], cwd=self.project_root)
            return True
    
    def run_test_suite(self) -> Dict[str, any]:
        """测试套件执行"""
        logger.info("🧪 执行测试套件")
        
        python_cmd = self._get_python_command()
        test_results = {
            'passed': False,
            'coverage': 0.0,
            'test_count': 0,
            'failures': 0
        }
        
        try:
            # 执行pytest with coverage
            result = subprocess.run([
                python_cmd, '-m', 'pytest',
                BUILD_CONFIG['test_pattern'],
                '-v',
                '--cov=src',
                '--cov-report=term-missing',
                '--cov-report=html:htmlcov',
                '--cov-report=json:coverage.json',
                '--tb=short'
            ], 
            capture_output=True, 
            text=True, 
            cwd=self.project_root
            )
            
            # 解析测试结果
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'passed' in line and 'failed' in line:
                    # 提取测试统计
                    pass
                elif 'TOTAL' in line and '%' in line:
                    # 提取覆盖率
                    coverage_str = line.split()[-1].replace('%', '')
                    test_results['coverage'] = float(coverage_str)
            
            test_results['passed'] = result.returncode == 0
            
            if test_results['coverage'] < BUILD_CONFIG['coverage_threshold']:
                logger.warning(f"测试覆盖率低于阈值: {test_results['coverage']}% < {BUILD_CONFIG['coverage_threshold']}%")
            
            logger.info(f"  ✓ 测试完成，覆盖率: {test_results['coverage']}%")
            
        except Exception as e:
            logger.error(f"测试执行失败: {e}")
            test_results['passed'] = False
        
        return test_results
    
    def build_knowledge_graph(self) -> bool:
        """知识图谱构建核心流程"""
        logger.info("🧠 构建EMC知识图谱")
        
        python_cmd = self._get_python_command()
        
        try:
            # 设置Python路径
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.project_root / 'src')
            
            # 执行知识图谱构建
            result = subprocess.run([
                python_cmd, 
                str(self.project_root / 'src' / 'knowledge_graph.py')
            ], 
            env=env,
            capture_output=True, 
            text=True,
            cwd=self.project_root
            )
            
            if result.returncode == 0:
                logger.info("  ✓ 知识图谱构建完成")
                logger.info("  ✓ 可视化文件已生成")
                return True
            else:
                logger.error(f"知识图谱构建失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"构建过程异常: {e}")
            return False
    
    def generate_documentation(self) -> bool:
        """文档生成"""
        logger.info("📚 生成项目文档")
        
        try:
            # 确保输出目录存在
            docs_dir = self.project_root / 'docs'
            docs_dir.mkdir(exist_ok=True)
            
            # 生成API文档
            self._generate_api_docs()
            
            # 生成使用手册
            self._generate_user_guide()
            
            logger.info("  ✓ 文档生成完成")
            return True
            
        except Exception as e:
            logger.error(f"文档生成失败: {e}")
            return False
    
    def _generate_api_docs(self):
        """生成API文档"""
        # 简化的API文档生成
        api_doc_content = """# EMC Knowledge Graph API Documentation

## Core Classes

### EMCKnowledgeGraph
- 核心知识图谱引擎
- 支持语义搜索和路径发现
- 提供多格式数据导出

### KnowledgeGraphVisualizer  
- 可视化引擎
- 静态和交互式图谱生成
- 网络分析仪表板

### Data Models
- NodeType: 节点类型枚举
- RelationType: 关系类型枚举
- KnowledgeNode: 知识节点数据结构
- KnowledgeEdge: 知识边数据结构
"""
        
        with open(self.project_root / 'docs' / 'API.md', 'w', encoding='utf-8') as f:
            f.write(api_doc_content)
    
    def _generate_user_guide(self):
        """生成用户指南"""
        guide_content = """# EMC Knowledge Graph User Guide

## Quick Start

```python
from src.knowledge_graph import EMCKnowledgeGraph

# 创建知识图谱
kg = EMCKnowledgeGraph()

# 语义搜索
results = kg.semantic_search("CISPR 25")

# 路径发现
paths = kg.find_semantic_paths('CISPR', 'ElectricVehicles')

# 生成可视化
fig, ax = kg.create_matplotlib_visualization()
```

## Advanced Features

- 拓扑分析
- 社区检测
- 中心性计算
- 多格式导出
"""
        
        with open(self.project_root / 'docs' / 'UserGuide.md', 'w', encoding='utf-8') as f:
            f.write(guide_content)
    
    def package_distribution(self) -> bool:
        """打包分发"""
        logger.info("📦 创建分发包")
        
        python_cmd = self._get_python_command()
        
        try:
            # 清理之前的构建
            build_dirs = ['build', 'dist', '*.egg-info']
            for pattern in build_dirs:
                for path in self.project_root.glob(pattern):
                    if path.is_dir():
                        shutil.rmtree(path)
                    elif path.is_file():
                        path.unlink()
            
            # 构建源码包和wheel包
            subprocess.run([
                python_cmd, 'setup.py', 
                'sdist', 'bdist_wheel'
            ], check=True, cwd=self.project_root)
            
            logger.info("  ✓ 分发包创建完成")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"打包失败: {e}")
            return False
    
    def cleanup_build_artifacts(self):
        """清理构建产物"""
        logger.info("🧹 清理构建产物")
        
        cleanup_patterns = [
            '__pycache__',
            '*.pyc',
            '.pytest_cache',
            '.coverage',
            'htmlcov',
            '.mypy_cache',
            'build',
            'dist',
            '*.egg-info'
        ]
        
        cleaned_count = 0
        for pattern in cleanup_patterns:
            for path in self.project_root.rglob(pattern):
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"清理失败 {path}: {e}")
        
        logger.info(f"  ✓ 清理完成，删除 {cleaned_count} 个文件/目录")
    
    def generate_build_report(self, build_results: Dict) -> str:
        """生成构建报告"""
        build_duration = datetime.now() - self.build_start
        
        report = {
            'build_info': {
                'timestamp': self.build_start.isoformat(),
                'duration_seconds': build_duration.total_seconds(),
                'platform': self.build_context['platform'],
                'python_version': self.build_context['python_version']
            },
            'results': build_results,
            'artifacts': {
                'graphs': list((self.project_root / 'output' / 'graphs').glob('*')) if (self.project_root / 'output' / 'graphs').exists() else [],
                'exports': list((self.project_root / 'output' / 'exports').glob('*')) if (self.project_root / 'output' / 'exports').exists() else [],
                'docs': list((self.project_root / 'docs').glob('*')) if (self.project_root / 'docs').exists() else []
            }
        }
        
        # 保存构建报告
        report_path = self.project_root / 'build_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        return str(report_path)
    
    def _get_python_command(self) -> str:
        """获取Python命令路径"""
        venv_path = self.project_root / BUILD_CONFIG['venv_name']
        if venv_path.exists():
            if sys.platform == 'win32':
                return str(venv_path / 'Scripts' / 'python.exe')
            else:
                return str(venv_path / 'bin' / 'python')
        return sys.executable
    
    def _get_pip_command(self) -> str:
        """获取pip命令路径"""
        venv_path = self.project_root / BUILD_CONFIG['venv_name']
        if venv_path.exists():
            if sys.platform == 'win32':
                return str(venv_path / 'Scripts' / 'pip.exe')
            else:
                return str(venv_path / 'bin' / 'pip')
        return 'pip'

def execute_full_build(args) -> bool:
    """完整构建流程执行"""
    builder = KnowledgeGraphBuilder()
    
    logger.info("🚀 启动完整构建流程")
    
    build_steps = [
        ('环境验证', builder.validate_environment),
        ('虚拟环境', builder.create_virtual_environment),
        ('依赖安装', lambda: builder.install_dependencies(args.upgrade)),
        ('代码质量', builder.execute_code_quality_checks),
        ('测试执行', builder.run_test_suite),
        ('知识图谱构建', builder.build_knowledge_graph),
        ('文档生成', builder.generate_documentation)
    ]
    
    if args.package:
        build_steps.append(('分发打包', builder.package_distribution))
    
    build_results = {}
    success = True
    
    for step_name, step_func in build_steps:
        logger.info(f"\n⚡ 执行步骤: {step_name}")
        
        step_start = time.time()
        try:
            result = step_func()
            build_results[step_name] = {
                'success': bool(result),
                'duration': time.time() - step_start,
                'result': result
            }
            
            if not result:
                logger.error(f"步骤失败: {step_name}")
                success = False
                if args.fail_fast:
                    break
                    
        except Exception as e:
            logger.error(f"步骤异常: {step_name} - {e}")
            build_results[step_name] = {
                'success': False,
                'duration': time.time() - step_start,
                'error': str(e)
            }
            success = False
            if args.fail_fast:
                break
    
    # 生成构建报告
    report_path = builder.generate_build_report(build_results)
    logger.info(f"📊 构建报告: {report_path}")
    
    # 清理（如果需要）
    if args.clean:
        builder.cleanup_build_artifacts()
    
    build_time = datetime.now() - builder.build_start
    logger.info(f"\n{'✅ 构建成功' if success else '❌ 构建失败'} - 耗时: {build_time}")
    
    return success

def main():
    """构建系统主入口"""
    parser = argparse.ArgumentParser(
        description='EMC Knowledge Graph Build System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
构建命令示例:
  python build.py --all                 # 完整构建
  python build.py --graph               # 仅构建知识图谱  
  python build.py --test                # 仅执行测试
  python build.py --clean               # 清理构建产物
  python build.py --all --package       # 完整构建+打包
        """
    )
    
    # 构建选项
    parser.add_argument('--all', action='store_true', help='执行完整构建流程')
    parser.add_argument('--setup', action='store_true', help='环境设置')
    parser.add_argument('--deps', action='store_true', help='安装依赖')
    parser.add_argument('--quality', action='store_true', help='代码质量检查')
    parser.add_argument('--test', action='store_true', help='执行测试')
    parser.add_argument('--graph', action='store_true', help='构建知识图谱')
    parser.add_argument('--docs', action='store_true', help='生成文档')
    parser.add_argument('--package', action='store_true', help='创建分发包')
    parser.add_argument('--clean', action='store_true', help='清理构建产物')
    
    # 构建控制选项
    parser.add_argument('--upgrade', action='store_true', help='升级依赖包')
    parser.add_argument('--fail-fast', action='store_true', help='遇到错误立即停止')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return 1
    
    builder = KnowledgeGraphBuilder()
    
    try:
        if args.all:
            success = execute_full_build(args)
            return 0 if success else 1
        
        # 单独步骤执行
        if args.setup:
            builder.validate_environment()
            builder.create_virtual_environment()
        
        if args.deps:
            builder.install_dependencies(args.upgrade)
        
        if args.quality:
            builder.execute_code_quality_checks()
        
        if args.test:
            builder.run_test_suite()
        
        if args.graph:
            builder.build_knowledge_graph()
        
        if args.docs:
            builder.generate_documentation()
        
        if args.package:
            builder.package_distribution()
        
        if args.clean:
            builder.cleanup_build_artifacts()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n🛑 构建被用户中断")
        return 130
    except Exception as e:
        logger.error(f"构建系统异常: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())