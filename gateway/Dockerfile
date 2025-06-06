# 优化的Gateway Dockerfile - 实用高效版本
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（无需更换镜像源）
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY gateway/ ./gateway/
COPY services/ ./services/
COPY data_access/ ./data_access/
COPY utils/ ./utils/

# 创建非root用户
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]