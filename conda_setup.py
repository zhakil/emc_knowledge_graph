#!/usr/bin/env python3
"""
EMC知识图谱 - Conda环境自动化部署
高效实用的Python 3.11环境配置
"""

import subprocess
import sys
import os
import json
from pathlib import Path

class CondaEMCDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_name = "emc-kg-311"
        self.python_version = "3.11"
        
    def check_conda(self):
        """检查conda是否可用"""
        try:
            result = subprocess.run(["conda", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Conda已安装: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Conda未安装，请先安装Miniconda或Anaconda")
            print("💡 下载地址: https://docs.conda.io/en/latest/miniconda.html")
            return False
    
    def create_conda_env(self):
        """创建conda环境"""
        print(f"🚀 创建conda环境: {self.env_name}")
        
        # 检查环境是否已存在
        try:
            result = subprocess.run(["conda", "info", "--envs"], 
                                  capture_output=True, text=True, check=True)
            if self.env_name in result.stdout:
                print(f"⚠️ 环境 {self.env_name} 已存在，是否重新创建？")
                choice = input("输入 y 重新创建，其他键跳过: ").lower()
                if choice == 'y':
                    subprocess.run(["conda", "env", "remove", "-n", self.env_name, "-y"], 
                                 check=True)
                else:
                    return True
        except subprocess.CalledProcessError:
            pass
        
        # 创建新环境
        cmd = [
            "conda", "create", "-n", self.env_name, 
            f"python={self.python_version}", "-y", "-c", "conda-forge"
        ]
        subprocess.run(cmd, check=True)
        print(f"✅ 环境 {self.env_name} 创建成功")
        return True
    
    def install_conda_dependencies(self):
        """安装conda可用的依赖包"""
        print("📦 安装conda核心依赖...")
        
        # conda可直接安装的包（性能更好）
        conda_packages = [
            "fastapi", "uvicorn", "redis-py", "pandas", "numpy",
            "psycopg2", "sqlalchemy", "pydantic", "httpx", "aiofiles",
            "scipy", "scikit-learn", "networkx", "matplotlib", "plotly",
            "jupyter", "ipython", "pytest", "black", "isort"
        ]
        
        cmd = ["conda", "install", "-n", self.env_name, "-c", "conda-forge", "-y"] + conda_packages
        
        try:
            subprocess.run(cmd, check=True)
            print("✅ Conda核心依赖安装完成")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ 部分conda包安装失败: {e}")
            print("💡 将通过pip补充安装")
    
    def install_pip_dependencies(self):
        """安装pip专用依赖"""
        print("📦 安装pip特殊依赖...")
        
        # 获取conda环境中的pip
        if os.name == 'nt':
            pip_path = f"conda run -n {self.env_name} pip"
        else:
            pip_path = f"conda run -n {self.env_name} pip"
        
        # 特殊依赖（conda中不可用或版本不匹配）
        pip_packages = [
            "neo4j>=5.28.0", "neomodel==5.5.0", "python-multipart",
            "python-jose[cryptography]", "passlib[bcrypt]", "python-dotenv",
            "openai", "sentence-transformers", "transformers", "faiss-cpu",
            "spacy", "nltk", "celery", "rdflib", "owlready2", "typer"
        ]
        
        for package in pip_packages:
            try:
                subprocess.run(f"{pip_path} install {package}".split(), check=True)
                print(f"✅ {package}")
            except subprocess.CalledProcessError:
                print(f"⚠️ {package} 安装失败")
    
    def create_activation_scripts(self):
        """创建环境激活脚本"""
        print("📝 创建激活脚本...")
        
        # Windows批处理脚本
        bat_script = f"""@echo off
echo 🐍 激活EMC知识图谱Conda环境...
call conda activate {self.env_name}
echo ✅ 环境已激活: {self.env_name}
echo 📋 可用命令:
echo   python start_gateway.py  # 启动API服务
echo   jupyter lab              # 启动Jupyter
echo   pytest tests/            # 运行测试
cmd /k
"""
        with open("activate_emc_env.bat", "w", encoding="utf-8") as f:
            f.write(bat_script)
        
        # Linux/Mac shell脚本
        sh_script = f"""#!/bin/bash
echo "🐍 激活EMC知识图谱Conda环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate {self.env_name}
echo "✅ 环境已激活: {self.env_name}"
echo "📋 可用命令:"
echo "  python start_gateway.py  # 启动API服务"
echo "  jupyter lab              # 启动Jupyter"
echo "  pytest tests/            # 运行测试"
bash
"""
        with open("activate_emc_env.sh", "w", encoding="utf-8") as f:
            f.write(sh_script)
        os.chmod("activate_emc_env.sh", 0o755)
        
        print("✅ 激活脚本已创建")
    
    def create_environment_yml(self):
        """创建environment.yml用于环境复制"""
        print("📄 导出环境配置...")
        
        try:
            # 导出环境
            result = subprocess.run([
                "conda", "env", "export", "-n", self.env_name, "--no-builds"
            ], capture_output=True, text=True, check=True)
            
            with open("environment.yml", "w", encoding="utf-8") as f:
                f.write(result.stdout)
            print("✅ environment.yml 已生成")
            
        except subprocess.CalledProcessError:
            print("⚠️ 环境导出失败")
    
    def test_environment(self):
        """测试环境是否正确配置"""
        print("🔍 测试环境配置...")
        
        test_imports = [
            "fastapi", "neo4j", "redis", "pandas", "sqlalchemy", 
            "pydantic", "numpy", "networkx"
        ]
        
        for package in test_imports:
            try:
                cmd = f"conda run -n {self.env_name} python -c \"import {package}; print('✅ {package}')\""
                subprocess.run(cmd, shell=True, check=True)
            except subprocess.CalledProcessError:
                print(f"❌ {package} 导入失败")
    
    def deploy(self):
        """完整部署流程"""
        print("🎯 EMC知识图谱 - Conda环境部署")
        print("=" * 50)
        
        # 1. 检查conda
        if not self.check_conda():
            return False
        
        # 2. 创建环境
        if not self.create_conda_env():
            return False
        
        # 3. 安装依赖
        self.install_conda_dependencies()
        self.install_pip_dependencies()
        
        # 4. 创建脚本
        self.create_activation_scripts()
        self.create_environment_yml()
        
        # 5. 测试环境
        self.test_environment()
        
        print("=" * 50)
        print("🎉 Conda环境部署完成!")
        print(f"\n📋 环境信息:")
        print(f"  - 环境名称: {self.env_name}")
        print(f"  - Python版本: {self.python_version}")
        print(f"  - 项目路径: {self.project_root}")
        
        print(f"\n🚀 激活环境:")
        if os.name == 'nt':
            print(f"  - Windows: activate_emc_env.bat")
            print(f"  - 手动: conda activate {self.env_name}")
        else:
            print(f"  - Linux/Mac: ./activate_emc_env.sh")
            print(f"  - 手动: conda activate {self.env_name}")
        
        print(f"\n📚 常用命令:")
        print(f"  conda activate {self.env_name}        # 激活环境")
        print(f"  python start_gateway.py              # 启动后端")
        print(f"  jupyter lab                          # 开发环境")
        print(f"  conda deactivate                     # 退出环境")
        
        return True

if __name__ == "__main__":
    deployer = CondaEMCDeployer()
    success = deployer.deploy()
    
    if success:
        print("\n💡 下一步:")
        print("1. 激活环境")
        print("2. 配置.env文件")
        print("3. 启动数据库服务")
        print("4. 运行: python start_gateway.py")
    else:
        print("\n❌ 部署失败，请检查错误信息")