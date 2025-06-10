FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 更新包管理器并安装系统依赖（改进的错误处理）
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    build-essential \
    libffi-dev \
    libssl-dev \
    python3-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y

# 复制并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY gateway/ ./gateway/
COPY services/ ./services/
RUN mkdir -p ./data_access

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "gateway.main"]