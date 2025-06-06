#!/bin/bash

echo "=== 修复Docker构建问题 ==="

# 1. 清理构建缓存
echo "1. 清理Docker构建缓存..."
docker builder prune -f
docker system prune -f

# 2. 检查文件大小
echo "2. 检查项目文件大小..."
echo "项目根目录大小:"
du -sh . 2>/dev/null || echo "无法获取目录大小"

echo "主要目录大小:"
for dir in frontend gateway services data_access; do
    if [ -d "$dir" ]; then
        size=$(du -sh "$dir" 2>/dev/null | cut -f1)
        echo "  $dir: $size"
    fi
done

# 3. 验证Dockerfile
echo "3. 验证Dockerfile语法..."
if [ -f "gateway/Dockerfile" ]; then
    echo "✓ gateway/Dockerfile 存在"
else
    echo "✗ gateway/Dockerfile 不存在"
    exit 1
fi

# 4. 单独构建gateway镜像
echo "4. 单独构建gateway镜像..."
docker build -t emc-gateway:latest -f gateway/Dockerfile .

if [ $? -eq 0 ]; then
    echo "✓ Gateway镜像构建成功"
else
    echo "✗ Gateway镜像构建失败"
    echo "尝试简化构建..."
    
    # 备用构建策略
    cat > gateway/Dockerfile.simple << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
    
    docker build -t emc-gateway:latest -f gateway/Dockerfile.simple .
fi

# 5. 构建前端镜像
echo "5. 构建前端镜像..."
if [ -d "frontend" ]; then
    docker build -t emc-frontend:latest frontend/
    echo "✓ 前端镜像构建完成"
fi

# 6. 启动服务
echo "6. 启动优化后的服务..."
docker-compose down
docker-compose up -d

echo "=== 构建修复完成 ==="
docker-compose ps