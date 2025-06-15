# EMC知识图谱系统 - Docker部署指南

## 🚀 快速启动

### 方法1: 使用Docker Compose（推荐）
```bash
# 启动系统
./docker-run.sh

# 或者手动执行
docker-compose -f docker-compose.app.yml up -d
```

### 方法2: 手动Docker命令
```bash
# 启动系统
./docker-manual.sh

# 或者手动执行
docker build -f Dockerfile.app -t emc-knowledge-graph:latest .
docker run -d --name emc-kg-system -p 5000:5000 emc-knowledge-graph:latest
```

## 🛠️ Docker Desktop WSL集成设置

如果遇到 "docker command not found" 错误：

1. **安装Docker Desktop**
   - 下载并安装 [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/install/)

2. **启用WSL集成**
   - 打开Docker Desktop
   - 进入 Settings → Resources → WSL Integration
   - 启用 "Enable integration with my default WSL distro"
   - 选择你使用的WSL发行版（如Ubuntu）
   - 点击 "Apply & Restart"

3. **重启WSL**
   ```cmd
   wsl --shutdown
   ```
   然后重新打开WSL终端

4. **验证Docker可用**
   ```bash
   docker --version
   docker-compose --version
   ```

## 📊 系统功能

访问 http://localhost:5000 使用以下功能：

- 📁 **文件上传** - 拖拽或选择多文件上传
- 📂 **文件管理** - Obsidian风格管理界面  
- ✏️ **文件编辑** - 在线编辑TXT/MD文件
- 🗑️ **文件删除** - 单个和批量删除
- 🤖 **实体提取** - KAG-DeepSeek AI引擎
- 🌐 **知识图谱** - 交互式可视化展示

## 🔧 管理命令

```bash
# 查看运行状态
docker-compose -f docker-compose.app.yml ps

# 查看日志
docker-compose -f docker-compose.app.yml logs -f

# 停止服务
docker-compose -f docker-compose.app.yml down

# 重启服务
docker-compose -f docker-compose.app.yml restart

# 重新构建
docker-compose -f docker-compose.app.yml build --no-cache
docker-compose -f docker-compose.app.yml up -d
```

## 📁 数据持久化

系统使用以下卷来保存数据：
- `./uploads` - 上传的文件
- `./files_db.json` - 文件数据库

即使容器重启，你的数据也会保留。

## 🐛 故障排除

### 端口占用
```bash
# 查看端口占用
lsof -i :5000
# 或
netstat -tlnp | grep :5000

# 杀死占用进程
sudo kill -9 <PID>
```

### 重置容器
```bash
# 完全重置
docker-compose -f docker-compose.app.yml down -v
docker rmi emc-knowledge-graph:latest
./docker-run.sh
```

### 查看详细日志
```bash
# 容器日志
docker logs emc-kg-system

# 实时日志
docker logs -f emc-kg-system
```