FROM python:3.11-slim

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=48001 \
    REMOTION_WORKSPACE=/app/data \
    REMOTION_OUTPUT_DIR=/app/data/output \
    REMOTION_STORE_DIR=/app/data/store \
    REMOTION_ENGINE_DIR=/app/remotion_engine \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# 安装系统基础依赖：Node.js 20, Chromium, FFmpeg, 中文字体, tini (PID 1 僵尸进程回收)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    chromium \
    ffmpeg \
    tini \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fonts-liberation \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && fc-cache -f \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 预安装 Remotion Node 依赖（充分利用 Docker 层缓存）
WORKDIR /app/remotion_engine
COPY remotion_engine/package.json remotion_engine/package-lock.json ./
RUN npm config set registry https://mirrors.huaweicloud.com/repository/npm/ && \
    npm install --no-audit --no-fund

WORKDIR /app

# 拷贝全量源码
COPY . .

# 创建持久化数据目录
RUN mkdir -p /app/data/output /app/data/store

EXPOSE 48001

# 容器健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-48001}/healthz || exit 1

# 容器入口与进程管理（tini 回收僵尸 Chromium 进程）
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["sh", "-c", "exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-48001}"]

