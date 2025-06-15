# EMC知识图谱系统 - 文档中心

## 📚 文档索引

### 🚀 快速开始
- **[构建说明](BUILD_INSTRUCTIONS.md)** - 项目构建和开发环境配置
- **[运行指南](RUN_APP.md)** - 如何启动和运行应用程序

### 🖥️ 桌面应用
- **[Windows应用指南](WINDOWS_APP_GUIDE.md)** - Windows桌面应用构建完整指南
- **[桌面应用README](README_DESKTOP.md)** - 桌面版功能说明和使用方法
- **[桌面应用状态](desktop-app-status.md)** - 开发进度和功能状态

### 🐳 Docker部署
- **[Docker设置指南](DOCKER_SETUP.md)** - Docker环境配置和部署方法
- **[Docker构建指南](DOCKER_BUILD_GUIDE.md)** - Docker镜像构建详细说明

## 🎯 核心功能

### 📁 文件管理系统
- **多格式文件上传** - 支持PDF、DOCX、TXT、MD等格式
- **Obsidian风格管理** - 左侧文件树，右侧详情展示
- **在线文件编辑** - TXT和MD文件的实时编辑
- **批量文件操作** - 支持单个和批量删除

### 🤖 AI智能处理
- **KAG-DeepSeek融合** - 知识增强生成框架
- **实体关系提取** - 自动识别文档中的实体和关系
- **多跳推理** - DIKW层次化知识分析
- **实时状态更新** - 处理进度可视化

### 🌐 知识图谱
- **交互式可视化** - D3.js动态图谱展示
- **节点关系操作** - 点击、拖拽、缩放交互
- **多种布局算法** - 自适应图谱布局
- **数据导出功能** - 支持多种格式导出

## 🛠️ 技术架构

### 前端技术栈
- **React 18** + **TypeScript** - 现代化前端框架
- **Ant Design 5** - 专业UI组件库
- **D3.js** - 数据可视化库
- **Electron** - 跨平台桌面应用框架

### 后端技术栈
- **Flask 3.1** - Python Web框架
- **Flask-CORS** - 跨域资源共享
- **Python 3.12** - 后端运行环境

### 部署方案
- **Docker** - 容器化部署
- **Nginx** - 生产环境代理
- **Electron Builder** - 桌面应用打包

## 📋 版本信息

- **当前版本**: 1.0.0
- **Python要求**: 3.12+
- **Node.js要求**: 18+
- **支持平台**: Windows、Linux、macOS

## 🤝 开发指南

### 开发环境
1. 安装Node.js 18+和Python 3.12+
2. 克隆项目并安装依赖
3. 启动开发服务器
4. 参考相关文档进行开发

### 构建部署
1. **Web版本**: 使用Docker部署
2. **桌面版本**: 使用Electron Builder打包
3. **生产环境**: 配置Nginx和SSL

## 📞 技术支持

如有问题请参考对应的详细文档或提交Issue。

---

*EMC知识图谱系统 - 基于KAG-DeepSeek融合AI的专业级知识图谱构建系统*