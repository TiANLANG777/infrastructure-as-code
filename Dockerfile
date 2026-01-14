FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖 (Postgres 驱动有时候需要 gcc)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制核心代码和数据
COPY app.py .
COPY templates ./templates
COPY weather.csv . 

# 暴露端口 (Web)
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
