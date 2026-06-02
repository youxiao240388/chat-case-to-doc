FROM python:3.11-slim

LABEL maintainer="youxiao240388"
LABEL description="聊天案例文档生成器 - 从截图/PDF/文本自动生成排障案例文档"

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1

RUN apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends \
      libpango-1.0-0 \
      libpangocairo-1.0-0 \
      libgdk-pixbuf-2.0-0 \
      libffi-dev \
      libcairo2 \
      libglvnd0 \
      libgl1 \
      libegl1 \
      fonts-noto-cjk \
      curl \
      git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

RUN mkdir -p /app/output/uploads /app/output/results

HEALTHCHECK --interval=30s --timeout=5s \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "300", "app.main:app"]