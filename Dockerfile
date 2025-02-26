FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY app/ ./app/

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 设置环境变量
ENV FLASK_APP=app
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 5000
# 启动命令
CMD ["gunicorn", "app:create_app()", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120"]
