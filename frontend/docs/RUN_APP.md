# 🚀 EMC知识图谱系统 - 运行指南

## 🎉 应用程序已启动！

### 📱 Web版本 (当前演示)
**立即访问**: http://localhost:3003

### 🖥️ 桌面版本演示
**查看演示**: http://localhost:8080/desktop-app-demo.html

---

## 🎯 运行方式

### 1. 📊 Web版本 (已运行)
- **地址**: http://localhost:3003
- **类型**: React Web应用
- **功能**: 完整的EMC知识图谱功能
- **状态**: ✅ 正在运行

### 2. 🖥️ Windows桌面版本
要运行真正的Windows桌面客户端：

#### 方法A: 使用Docker构建 (推荐)
```bash
# 在Windows PowerShell中运行
docker-build-windows.bat
```

#### 方法B: 手动构建
```bash
# 在Windows中运行
npm install --legacy-peer-deps
npm run build
npm run dist

# 然后运行生成的安装程序
dist\EMC知识图谱系统-1.0.0-x64.exe
```

#### 方法C: 开发模式 (需要Windows环境)
```bash
npm run electron-dev
```

---

## 🎨 应用程序界面

### 主要功能模块:
1. **📁 文件上传** - 上传PDF、DOCX、TXT等文档
2. **📂 文件管理** - Obsidian风格的文件管理器
3. **🤖 实体关系提取** - KAG-DeepSeek AI引擎
4. **📝 Markdown编辑器** - 支持YAML front matter
5. **🌐 知识图谱** - 交互式可视化图谱

### 桌面版特有功能:
- 🖥️ **原生Windows窗口**
- 🔧 **系统托盘集成**
- ⌨️ **全局快捷键** (Ctrl+Shift+E)
- 📱 **桌面通知**
- 🎛️ **系统菜单栏**
- 📁 **文件关联** (.emckg格式)

---

## 🔍 当前状态

### ✅ 正在运行的服务:
- **Web应用服务器**: http://localhost:3003
- **桌面演示服务器**: http://localhost:8080
- **应用程序状态**: 完全功能演示

### 📊 功能演示:
- **用户界面**: 专业级企业设计
- **文件管理**: Obsidian风格界面
- **AI集成**: KAG-DeepSeek融合系统
- **知识图谱**: 交互式可视化

---

## 🎮 立即体验

### 选择你的体验方式:

#### 🌐 在浏览器中体验 (推荐开始)
点击访问: **http://localhost:3003**

#### 🖥️ 查看桌面版界面演示
点击访问: **http://localhost:8080/desktop-app-demo.html**

#### 💻 构建真正的Windows桌面应用
```bash
# 复制整个项目到Windows环境
# 然后运行构建命令获得真正的.exe文件
```

---

## 🎊 恭喜！

**EMC知识图谱系统现已完全运行！**

- ✅ Web版本正在 http://localhost:3003 运行
- ✅ 桌面演示在 http://localhost:8080/desktop-app-demo.html 
- ✅ 所有配置已完成，可随时构建Windows桌面版本

**立即点击上面的链接开始体验你的知识图谱系统！**