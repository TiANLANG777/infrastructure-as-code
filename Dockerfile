# 使用官方 Python 轻量级镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 1. 先复制依赖文件并安装，利用 Docker 缓存层
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. 复制应用代码和模板
COPY app.py .
COPY templates ./templates

# 暴露应用端口 (FastAPI 默认 8000)
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
