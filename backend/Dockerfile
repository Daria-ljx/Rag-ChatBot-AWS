FROM python:3.11-slim

# 工作目录设为 /app
WORKDIR /app

# 拷贝后端代码
COPY requirements.txt .

# 安装依赖
RUN pip install pysqlite3-binary && \
    pip install -r requirements.txt --no-cache-dir --timeout=300 --retries=10 \
    -i https://pypi.tuna.tsinghua.edu.cn/simple --verbose

COPY . .

# 从 .src 启动 FastAPI 应用
CMD ["python", "-m", "src.app_api_handler"]

