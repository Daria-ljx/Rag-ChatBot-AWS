FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir --timeout=300 --retries=10 \
    -i https://pypi.tuna.tsinghua.edu.cn/simple --verbose

COPY . .

EXPOSE 8501

# 以 streamlit 启动前端应用
CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true", "--logger.level=debug"]