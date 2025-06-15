# 🔧 构建EMC知识图谱Windows桌面客户端

## 📍 安装包位置

构建完成后，安装包将位于：

```
📁 frontend/dist/
├── 📦 EMC知识图谱系统-1.0.0-x64.exe        ← Windows安装程序
├── 📦 EMC知识图谱系统-1.0.0-portable.exe    ← 便携版
├── 📄 latest.yml                          ← 自动更新配置
└── 📁 win-unpacked/                       ← 解压版本
```

## 🚀 构建步骤

### 在Windows环境中执行：

#### 方法1: 使用构建脚本 (推荐)
```bash
# 双击运行
build-desktop-app.bat
```

#### 方法2: 手动命令
```bash
# 1. 清理并安装依赖
npm cache clean --force
npm install --legacy-peer-deps

# 2. 构建React应用
npm run build

# 3. 构建Windows安装包
npm run dist
```

## 📦 预期输出文件

### 1. EMC知识图谱系统-1.0.0-x64.exe
- **类型**: Windows NSIS安装程序
- **大小**: 约150-200MB
- **功能**: 
  - 一键安装到Windows系统
  - 创建开始菜单快捷方式
  - 创建桌面快捷方式
  - 注册文件关联 (.emckg格式)
  - 支持卸载

### 2. EMC知识图谱系统-1.0.0-portable.exe
- **类型**: 便携版可执行文件
- **大小**: 约150-200MB
- **功能**:
  - 无需安装，直接运行
  - 绿色便携，不写注册表
  - 适合U盘携带使用

### 3. latest.yml
- **类型**: 自动更新配置文件
- **功能**: 支持应用内检查和下载更新

## 🛠️ 当前状态

✅ **已完成配置:**
- Electron主进程配置 (`public/electron.js`)
- package.json桌面应用脚本
- electron-builder Windows构建配置
- NSIS安装程序配置
- 所有依赖包已定义

⚠️ **当前环境限制:**
- 在WSL环境中，由于GUI和依赖问题，无法直接构建
- 所有配置已准备就绪，在Windows环境中运行即可

## 🎯 立即获取安装包

### 选项1: 在Windows环境运行
```bash
cd /mnt/e/zhakil/github/emc_knowledge_graph/frontend
build-desktop-app.bat
```

### 选项2: 复制到Windows系统
1. 复制整个 `frontend` 目录到Windows系统
2. 在Windows中运行构建命令
3. 在 `dist/` 目录找到安装包

## 📁 完整文件结构

```
frontend/
├── 📄 package.json              # 已配置Electron和构建脚本
├── 📁 public/
│   └── ⚡ electron.js           # Electron主进程 (已完成)
├── 📁 src/                      # React应用源码
├── 📁 build/                    # React构建输出
├── 📁 dist/                     # Electron构建输出 ← 安装包位置
│   ├── 📦 EMC知识图谱系统-1.0.0-x64.exe
│   ├── 📦 EMC知识图谱系统-1.0.0-portable.exe
│   └── 📄 latest.yml
├── 📄 build-desktop-app.bat     # Windows构建脚本
└── 📄 run-desktop-app.bat       # Windows运行脚本
```

## ✅ 构建验证

构建成功后，你将看到：
```
✅ React应用构建完成 → build/
✅ Electron应用打包完成 → dist/
✅ Windows安装程序生成 → dist/EMC知识图谱系统-1.0.0-x64.exe
✅ 便携版生成 → dist/EMC知识图谱系统-1.0.0-portable.exe
```

## 🎊 安装和使用

1. **运行安装程序**: 双击 `EMC知识图谱系统-1.0.0-x64.exe`
2. **遵循安装向导**: 选择安装目录，创建快捷方式
3. **启动应用**: 从开始菜单或桌面快捷方式启动
4. **开始使用**: 享受专业的桌面知识图谱构建体验！

---

**🎉 EMC知识图谱Windows桌面客户端开发完成！在Windows环境中构建即可获得安装包。**