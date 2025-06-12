#!/usr/bin/env python3
"""
项目结构重组脚本
将散乱的文件整理到规范的目录结构中
"""
import os
import shutil
import glob
from pathlib import Path

def reorganize_project():
    """重组项目结构"""
    base_path = Path("/mnt/host/e/emc_knowledge_graph")
    
    # 创建标准目录结构
    directories = {
        "backend": "后端服务",
        "frontend": "前端应用", 
        "services": "微服务模块",
        "data": "数据存储",
        "config": "配置文件",
        "docs": "文档",
        "scripts": "脚本工具",
        "tests": "测试文件",
        "logs": "日志文件",
        "uploads": "上传文件",
        "dev-tools": "开发工具"
    }
    
    print("🔧 开始重组项目结构...")
    
    # 1. 创建目录
    for dir_name, desc in directories.items():
        dir_path = base_path / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"✅ 创建目录: {dir_name} ({desc})")
    
    # 2. 移动后端文件
    backend_files = [
        "enhanced_gateway.py",
        "start_gateway.py", 
        "quick_start.py"
    ]
    
    for file in backend_files:
        src = base_path / file
        if src.exists():
            dst = base_path / "backend" / file
            shutil.move(str(src), str(dst))
            print(f"📁 移动后端文件: {file}")
    
    # 3. 移动测试文件
    test_files = glob.glob(str(base_path / "test_*.py"))
    for file in test_files:
        dst = base_path / "dev-tools" / "tests" / Path(file).name
        shutil.move(file, str(dst))
        print(f"🧪 移动测试文件: {Path(file).name}")
    
    # 4. 移动日志文件
    log_files = glob.glob(str(base_path / "*.log"))
    for file in log_files:
        dst = base_path / "logs" / Path(file).name
        shutil.move(file, str(dst))
        print(f"📊 移动日志文件: {Path(file).name}")
    
    # 5. 移动配置文件
    config_files = [
        "environment.yml",
        "pyproject.toml", 
        "requirements.txt",
        "requirements-dev.txt",
        "docker-compose.yml",
        "Dockerfile",
        "neo4j.conf"
    ]
    
    for file in config_files:
        src = base_path / file
        if src.exists():
            dst = base_path / "config" / file
            shutil.move(str(src), str(dst))
            print(f"⚙️ 移动配置文件: {file}")
    
    # 6. 移动脚本文件
    script_files = glob.glob(str(base_path / "*.sh"))
    for file in script_files:
        dst = base_path / "scripts" / Path(file).name
        shutil.move(file, str(dst))
        print(f"📜 移动脚本文件: {Path(file).name}")
    
    # 7. 移动文档文件
    doc_files = [
        "README.md",
        "EMC_ONTOLOGY.md", 
        "FILE_DESCRIPTIONS.md"
    ]
    
    for file in doc_files:
        src = base_path / file
        if src.exists():
            dst = base_path / "docs" / file
            shutil.move(str(src), str(dst))
            print(f"📚 移动文档文件: {file}")
    
    # 8. 清理临时文件
    temp_files = [
        "*.msi",
        "test*.txt",
        "*.pyc"
    ]
    
    for pattern in temp_files:
        for file in glob.glob(str(base_path / pattern)):
            os.remove(file)
            print(f"🗑️ 清理临时文件: {Path(file).name}")
    
    print("\n🎉 项目结构重组完成！")
    
    # 生成新的项目结构说明
    create_project_structure_doc(base_path)

def create_project_structure_doc(base_path):
    """创建项目结构说明文档"""
    structure_doc = """# 📁 EMC知识图谱项目结构

## 🏗️ 目录结构说明

```
emc_knowledge_graph/
├── 📂 backend/           # 后端服务
│   ├── enhanced_gateway.py    # 主要API网关
│   ├── start_gateway.py       # 启动脚本
│   └── quick_start.py         # 快速启动
│
├── 📂 frontend/          # 前端应用
│   ├── src/                   # React源码
│   ├── public/                # 静态资源
│   └── package.json           # 依赖配置
│
├── 📂 services/          # 微服务模块
│   ├── ai_integration/        # AI集成服务
│   ├── knowledge_graph/       # 知识图谱服务
│   ├── file_processing/       # 文件处理服务
│   └── emc_domain/           # EMC领域服务
│
├── 📂 config/            # 配置文件
│   ├── environment.yml        # Conda环境
│   ├── requirements.txt       # Python依赖
│   ├── docker-compose.yml     # Docker配置
│   └── neo4j.conf            # Neo4j配置
│
├── 📂 data/              # 数据存储
│   ├── neo4j/                # 图数据库
│   ├── postgres/             # 关系数据库
│   └── uploads/              # 上传文件
│
├── 📂 scripts/           # 脚本工具
│   ├── deploy.sh             # 部署脚本
│   ├── start-system.sh       # 系统启动
│   └── init_project.sh       # 项目初始化
│
├── 📂 tests/             # 测试文件
│   ├── unit/                 # 单元测试
│   ├── integration/          # 集成测试
│   └── api/                  # API测试
│
├── 📂 dev-tools/         # 开发工具
│   ├── tests/                # 开发测试
│   ├── examples/             # 示例代码
│   ├── scripts/              # 工具脚本
│   └── docs/                 # 开发文档
│
├── 📂 docs/              # 文档
│   ├── README.md             # 项目说明
│   ├── EMC_ONTOLOGY.md       # 本体说明
│   └── FILE_DESCRIPTIONS.md  # 文件说明
│
├── 📂 logs/              # 日志文件
│   ├── backend.log           # 后端日志
│   ├── frontend.log          # 前端日志
│   └── gateway.log           # 网关日志
│
└── 📂 uploads/           # 上传文件
    ├── standards/            # 标准文档
    ├── reports/              # 测试报告
    └── temp/                 # 临时文件
```

## 🚀 快速启动

1. **安装依赖**:
   ```bash
   cd config
   pip install -r requirements.txt
   ```

2. **启动后端**:
   ```bash
   cd backend
   python enhanced_gateway.py
   ```

3. **启动前端**:
   ```bash
   cd frontend
   npm start
   ```

## 📝 开发指南

- **后端开发**: 在 `backend/` 目录下进行
- **前端开发**: 在 `frontend/` 目录下进行
- **测试文件**: 统一放在 `dev-tools/tests/` 目录
- **配置管理**: 所有配置文件在 `config/` 目录
- **文档更新**: 在 `docs/` 目录维护文档

## 🔧 开发工具

- `dev-tools/scripts/` - 开发脚本
- `dev-tools/tests/` - 开发测试
- `dev-tools/examples/` - 示例代码
"""
    
    doc_path = base_path / "docs" / "PROJECT_STRUCTURE.md"
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(structure_doc)
    
    print(f"📋 创建项目结构文档: {doc_path}")

if __name__ == "__main__":
    reorganize_project()