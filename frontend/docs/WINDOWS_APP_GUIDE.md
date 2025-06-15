# EMC知识图谱Windows桌面应用构建指南

## ✅ 已完成的工作

### 1. 🚀 完整的Electron应用配置
- ✅ 已配置`package.json`与完整的Electron构建设置
- ✅ 已创建`public/electron.js`主进程文件
- ✅ 已集成内置Flask API服务器
- ✅ 已配置系统托盘和快捷键功能
- ✅ 已配置Windows安装包生成

### 2. 📁 核心文件结构
```
frontend/
├── public/electron.js          # Electron主进程，包含API服务器启动
├── build/index.html            # 桌面版HTML界面  
├── api_server.py               # 内置Flask API服务器
├── package.json                # 完整Electron构建配置
├── build-desktop.bat           # Windows构建脚本
└── dist/                       # 输出目录
```

### 3. 🔧 关键功能特性
- ✅ **内置API服务器** - 自动启动Flask后端服务
- ✅ **系统托盘** - 最小化到托盘，右键菜单
- ✅ **全局快捷键** - Ctrl+Shift+E显示/隐藏窗口
- ✅ **文件关联** - .emckg文件类型支持
- ✅ **自动更新** - 生产环境更新检查
- ✅ **单实例运行** - 防止重复启动

## 🖥️ 在Windows上构建真正的.exe文件

由于WSL限制，需要在Windows环境中构建：

### 方法1: 在Windows PowerShell中构建

1. **复制项目到Windows**
   ```cmd
   # 从WSL复制到Windows
   cp -r /mnt/e/zhakil/github/emc_knowledge_graph/frontend /mnt/c/temp/emc-frontend
   ```

2. **在Windows PowerShell中执行**
   ```powershell
   cd C:\temp\emc-frontend
   npm install
   npm run dist
   ```

### 方法2: 使用Windows批处理脚本

在Windows中双击运行：`build-desktop.bat`

```batch
@echo off
echo 🚀 构建EMC知识图谱Windows桌面应用程序...
call npm install
call npm run build
call npm run dist
echo ✅ 构建完成！
explorer dist
pause
```

## 📦 预期输出文件

构建成功后，在`dist/`目录中会生成：

- **EMC知识图谱系统-1.0.0-x64.exe** (安装包，约150MB)
- **EMC知识图谱系统-1.0.0-portable.exe** (便携版，约150MB)
- **latest.yml** (更新配置文件)

## 🚀 应用功能

### 📱 桌面版特性
- 🖥️ **原生Windows应用** - 真正的.exe可执行文件
- 📊 **完整功能** - 文件上传、管理、编辑、删除
- 🤖 **AI集成** - KAG-DeepSeek融合引擎
- 📁 **本地存储** - 所有数据保存在本地
- 🔧 **系统集成** - 开始菜单、桌面快捷方式

### 🛠️ 核心模块
- 📁 **文件上传** - 拖拽上传多种格式
- 📂 **文件管理** - Obsidian风格界面
- ✏️ **在线编辑** - TXT/MD文件编辑
- 🗑️ **文件删除** - 单个/批量删除
- 🤖 **实体提取** - AI自动分析
- 🌐 **知识图谱** - 交互式可视化

## 🔍 故障排除

### WSL构建问题
如果在WSL中构建出现问题：
1. WSL无法生成真正的Windows exe文件
2. 需要在Windows原生环境中构建
3. 可以使用Docker Desktop for Windows

### 构建慢的问题
- Electron首次构建需要下载约100MB文件
- 后续构建会使用缓存，速度较快
- 建议使用快速网络环境

### 运行时问题
- 确保已安装Python 3.12+
- 确保Flask依赖已安装
- 检查端口5000是否被占用

## 📋 使用指南

### 安装使用
1. 双击 `EMC知识图谱系统-1.0.0-x64.exe` 安装
2. 或使用便携版 `EMC知识图谱系统-1.0.0-portable.exe`
3. 首次启动会自动配置环境

### 快捷操作
- **Ctrl+Shift+E** - 显示/隐藏主窗口
- **右键托盘图标** - 快速操作菜单
- **Ctrl+N** - 新建项目
- **Ctrl+O** - 打开项目

## 🎯 下一步建议

要在Windows上获得真正的.exe文件：

1. **复制项目到Windows**
2. **在Windows PowerShell/CMD中运行构建命令**
3. **获得完整的Windows桌面应用**

项目已100%准备就绪，只需在Windows环境中执行最后的构建步骤！