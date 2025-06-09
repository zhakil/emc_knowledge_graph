#!/usr/bin/env python3
"""
EMC知识图谱 - 环境管理工具
快速环境设置和验证
"""

import subprocess
import sys
import os
from pathlib import Path

class EMCEnvironmentManager:
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / "venv"
        
    def create_venv(self):
        """创建虚拟环境"""
        print("🚀 创建虚拟环境...")
        subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)])
        print("✅ 虚拟环境创建成功")
        
    def activate_venv(self):
        """获取激活命令"""
        if os.name == 'nt':  # Windows
            activate_script = self.venv_path / "Scripts" / "activate.bat"
            print(f"💡 Windows激活命令: {activate_script}")
        else:  # Linux/Mac
            activate_script = self.venv_path / "bin" / "activate"
            print(f"💡 Linux/Mac激活命令: source {activate_script}")
            
    def install_dependencies(self):
        """安装依赖"""
        pip_path = self.venv_path / ("Scripts" if os.name == 'nt' else "bin") / "pip"
        
        print("📦 升级pip...")
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"])
        
        print("📦 安装生产依赖...")
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"])
        
        print("📦 安装开发依赖...")
        subprocess.run([str(pip_path), "install", "-r", "dev-requirements.txt"])
        
    def verify_installation(self):
        """验证安装"""
        python_path = self.venv_path / ("Scripts" if os.name == 'nt' else "bin") / "python"
        
        test_imports = [
            "fastapi", "neo4j", "redis", "pandas", 
            "pydantic", "sqlalchemy", "networkx"
        ]
        
        print("🔍 验证关键依赖...")
        for package in test_imports:
            try:
                result = subprocess.run([
                    str(python_path), "-c", f"import {package}; print('✅ {package}')"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(result.stdout.strip())
                else:
                    print(f"❌ {package} 导入失败")
            except Exception as e:
                print(f"❌ {package} 测试失败: {e}")
                
    def create_env_file(self):
        """创建环境配置文件"""
        env_content = """# EMC知识图谱系统环境配置
# 数据库配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# Redis配置
REDIS_URL=redis://localhost:6379/0

# PostgreSQL配置
DATABASE_URL=postgresql://user:password@localhost:5432/emc_kg

# OpenAI配置
OPENAI_API_KEY=your_openai_api_key_here

# 应用配置
DEBUG=true
LOG_LEVEL=INFO
SECRET_KEY=your_secret_key_here

# FastAPI配置
HOST=0.0.0.0
PORT=8000
"""
        
        env_file = self.project_root / ".env"
        if not env_file.exists():
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            print("📝 创建 .env 配置文件")
        else:
            print("📝 .env 文件已存在")
            
    def setup_complete_environment(self):
        """完整环境设置"""
        print("🎯 EMC知识图谱系统 - 环境设置开始")
        print("=" * 50)
        
        # 创建虚拟环境
        if not self.venv_path.exists():
            self.create_venv()
        else:
            print("✅ 虚拟环境已存在")
            
        # 安装依赖
        self.install_dependencies()
        
        # 创建配置文件
        self.create_env_file()
        
        # 验证安装
        self.verify_installation()
        
        # 提供激活命令
        self.activate_venv()
        
        print("=" * 50)
        print("🎉 环境设置完成!")
        print("\n📋 下一步操作:")
        print("1. 激活虚拟环境 (见上面命令)")
        print("2. 配置 .env 文件中的数据库连接")
        print("3. 启动 Neo4j 和 Redis 服务")
        print("4. 运行: uvicorn main:app --reload")

if __name__ == "__main__":
    manager = EMCEnvironmentManager()
    manager.setup_complete_environment()