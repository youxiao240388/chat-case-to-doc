FROM python:3.11-slim

LABEL maintainer="youxiao240388"
LABEL description="聊天案例文档生成器 - 从截图/PDF/文本自动生成排障案例文档"

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends \
      libpango-1.0-0 \
      libpangocairo-1.0-0 \
      libgdk-pixbuf-2.0-0 \
      libffi-dev \
      libcairo2 \
      libgl1 \
      fonts-noto-cjk \
      curl \
      git && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 安装 Python 依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ ./app/

# 创建运行目录
RUN mkdir -p /app/output/uploads /app/output/results

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "300", "app.main:app"]