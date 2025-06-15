# EMC知识图谱系统

> 基于KAG-DeepSeek融合AI的专业级知识图谱构建系统

## 🚀 快速开始

### 🖥️ Windows桌面应用（推荐）
```bash
# 在Windows中运行
build-desktop.bat

# 或在WSL/Linux中运行
./build-desktop.sh
```

### 🌐 Web版本
```bash
# Docker部署（推荐）
./docker-run.sh

# 或手动启动
python3 api_server.py
# 访问 http://localhost:5000
```

## 📚 完整文档

所有详细文档位于 `docs/` 目录：

- **[文档中心](docs/README.md)** - 文档索引和概览
- **[Windows应用指南](docs/WINDOWS_APP_GUIDE.md)** - 桌面应用完整指南
- **[Docker部署指南](docs/DOCKER_SETUP.md)** - 容器化部署方法
- **[构建说明](docs/BUILD_INSTRUCTIONS.md)** - 开发环境配置
- **[运行指南](docs/RUN_APP.md)** - 启动和使用方法

## ✨ 核心功能

### 📁 智能文件管理
- 🔄 多格式文件上传（PDF、DOCX、TXT、MD等）
- 📂 Obsidian风格文件管理界面
- ✏️ 在线文件编辑（TXT/MD）
- 🗑️ 批量文件操作

### 🤖 AI智能分析
- 🧠 KAG-DeepSeek融合AI引擎
- 🔍 自动实体关系提取
- 🌊 多跳推理和DIKW分析
- 📊 实时处理状态显示

### 🌐 知识图谱可视化
- 🎨 D3.js交互式图谱
- 🔗 节点关系可视化
- 🖱️ 拖拽、缩放、点击交互
- 📤 多格式数据导出

## 🛠️ 技术栈

**前端**: React 18 + TypeScript + Ant Design + D3.js + Electron  
**后端**: Flask 3.1 + Python 3.12  
**部署**: Docker + Nginx  

## 📋 系统要求

- **Python**: 3.12+
- **Node.js**: 18+
- **内存**: 4GB+
- **存储**: 2GB+

## 🎯 版本特性

### v1.0.0 功能列表
✅ 完整的文件管理系统  
✅ KAG-DeepSeek AI集成  
✅ Windows桌面应用  
✅ Docker容器化部署  
✅ 交互式知识图谱  
✅ 实时编辑和预览  

## 📞 获取帮助

1. **查看文档**: `docs/` 目录中的详细指南
2. **快速启动**: 运行相应的启动脚本
3. **问题反馈**: 提交Issue或查看日志

---

**EMC知识图谱系统 v1.0.0** - 让知识图谱构建更智能、更高效！