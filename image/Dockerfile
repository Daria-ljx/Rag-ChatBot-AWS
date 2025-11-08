FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# 安装 Python 依赖（含 SQLite 支持）
RUN pip install pysqlite3-binary && \
    pip install -r requirements.txt --no-cache-dir --timeout=300 --retries=10 \
    -i https://pypi.tuna.tsinghua.edu.cn/simple --verbose

COPY . .

# FastAPI(8000) + Streamlit(8501)
EXPOSE 8000
EXPOSE 8501


ENV IS_USING_IMAGE_RUNTIME=True
ENV PYTHONPATH=/app


# Running FastAPI + Streamlit at the same time
CMD ["bash", "-c", "uvicorn src.app_api_handler:app --host 0.0.0.0 --port 8000 & streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]
