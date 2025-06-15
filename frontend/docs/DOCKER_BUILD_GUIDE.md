# 🐳 EMC知识图谱 Docker构建指南

使用Docker构建Windows桌面客户端，确保环境干净和一致性。

## 🚀 快速开始

### 在Windows环境中：

#### 方法1: 使用Docker构建脚本
```bash
# 双击运行
docker-build-windows.bat
```

#### 方法2: 使用Docker Compose
```bash
docker-compose up emc-desktop-builder
```

#### 方法3: 手动Docker命令
```bash
# 1. 构建Docker镜像
docker build -f Dockerfile.desktop -t emc-knowledge-graph-builder .

# 2. 运行构建容器
docker run --rm -v "$(pwd)/dist:/app/dist" emc-knowledge-graph-builder
```

## 📦 Docker构建环境

### 基础镜像: `node:18-alpine`
- **Node.js**: v18 (LTS)
- **npm**: 最新版本
- **electron-builder**: 全局安装
- **Wine**: 用于在Linux中构建Windows应用

### 构建过程:
1. **安装依赖**: `npm install --legacy-peer-deps`
2. **构建React**: `npm run build`
3. **构建Electron**: `npm run dist`
4. **输出文件**: 保存到 `dist/` 目录

## 📁 构建输出

构建完成后，`dist/` 目录将包含：

```
📁 dist/
├── 📦 EMC知识图谱系统-1.0.0-x64.exe        # Windows NSIS安装程序
├── 📦 EMC知识图谱系统-1.0.0-portable.exe    # 便携版可执行文件  
├── 📄 latest.yml                          # 自动更新配置
└── 📁 win-unpacked/                       # 解压的应用目录
```

## 🛠️ Docker服务定义

### 生产构建服务
```yaml
emc-desktop-builder:
  - 构建Windows桌面安装包
  - 输出到 dist/ 目录
  - 一次性构建任务
```

### 开发服务 (可选)
```yaml
emc-dev:
  - 运行React开发服务器
  - 端口: 3003
  - 支持热重载
```

## 📋 前置要求

### Docker环境:
- ✅ Docker Desktop 已安装
- ✅ Docker Desktop 正在运行
- ✅ WSL2 集成已启用 (Windows)

### 系统要求:
- **Windows**: Docker Desktop for Windows
- **内存**: 至少 4GB 可用内存
- **磁盘**: 至少 2GB 可用空间

## 🔧 故障排除

### 常见问题:

#### 1. Docker命令未找到
```bash
# 检查Docker是否正确安装
docker --version

# 在WSL中启用Docker集成
# Docker Desktop -> Settings -> Resources -> WSL Integration
```

#### 2. 构建过程中内存不足
```bash
# 增加Docker内存限制
# Docker Desktop -> Settings -> Resources -> Memory (推荐4GB+)
```

#### 3. 网络连接问题
```bash
# 使用国内镜像源
npm config set registry https://registry.npmmirror.com
```

#### 4. Wine构建错误
```bash
# 在Alpine中，Wine可能有兼容性问题
# 解决方案：使用 ubuntu:20.04 基础镜像
```

## 🎯 高级配置

### 自定义构建参数

编辑 `package.json` 中的 `build` 配置：

```json
{
  "build": {
    "win": {
      "target": [
        {"target": "nsis", "arch": ["x64"]},
        {"target": "portable", "arch": ["x64"]}
      ]
    }
  }
}
```

### 多架构构建

```bash
# 构建x64和arm64版本
docker run --rm \
  -v "$(pwd)/dist:/app/dist" \
  -e "CSC_IDENTITY_AUTO_DISCOVERY=false" \
  emc-knowledge-graph-builder \
  npm run dist -- --win --x64 --arm64
```

## 🚀 部署和分发

### 1. 安装程序分发
```bash
# 上传 EMC知识图谱系统-1.0.0-x64.exe 到文件服务器
# 用户下载并运行安装程序
```

### 2. 便携版分发
```bash  
# 上传 EMC知识图谱系统-1.0.0-portable.exe
# 用户直接运行，无需安装
```

### 3. 自动更新
```bash
# 配置 latest.yml 文件到更新服务器
# 应用程序将自动检查和下载更新
```

## ✅ 验证构建

构建成功的标志：

```bash
✅ Docker镜像构建完成
✅ React应用构建完成 → build/
✅ Electron应用打包完成 → dist/
✅ Windows安装程序生成 → *.exe
✅ 文件大小合理 (150-200MB)
```

## 🎉 使用构建的应用

1. **双击安装程序**: `EMC知识图谱系统-1.0.0-x64.exe`
2. **遵循安装向导**: 选择安装目录
3. **启动应用**: 从开始菜单启动
4. **享受桌面体验**: 完整的Windows原生应用功能

---

**🎊 Docker构建环境确保了干净、一致、可重复的构建过程！**