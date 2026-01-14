# 使用轻量级 Python 镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖 (编译 Pandas/Scikit-learn 需要 gcc)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制所有代码和数据
COPY app.py .
COPY templates ./templates
COPY weather.csv .

# ⬇️⬇️⬇️ 关键修改：直接用 python 运行，不要用 uvicorn ⬇️⬇️⬇️
CMD ["python", "app.py"]