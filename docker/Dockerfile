# 阶段 1: 构建阶段
FROM python:3.11-slim AS builder

WORKDIR /app

# 安装编译依和编译工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 阶段 2: 生产阶段
FROM python:3.11-slim AS production

WORKDIR /app

# 创建非 root 用户运行应用
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 复制从构建阶段安装的依赖
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# 复制应用代码
COPY backend/ ./backend/
COPY .env ./

# 创建上传目录并设置权限
RUN mkdir -p uploads && chown -R appuser:appuser /app /home/appuser

# 切换到非 root 用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health')" || exit 1

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "backend/app_v2.py"]