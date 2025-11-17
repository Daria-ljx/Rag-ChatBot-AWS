import streamlit as st
import requests
import os
import logging

# -------------------------------
# Logging 配置
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# -------------------------------
# 后端 URL 配置
# -------------------------------
# 从环境变量获取 backend URL，如果没有则默认 localhost
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")
logging.info(f"Using backend URL: {FASTAPI_URL}")

# -------------------------------
# Streamlit 页面配置
# -------------------------------
st.set_page_config(page_title="RAG Chatbot", page_icon="💬", layout="centered")
st.title("💬 RAG Chatbot")
st.markdown("Chat with Lijiaxin RAG-powered knowledge base in real time.")

# -------------------------------
# 会话状态初始化
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示聊天记录
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    if role == "user":
        st.chat_message("user").markdown(content)
    else:
        st.chat_message("assistant").markdown(content)

# -------------------------------
# 用户输入处理
# -------------------------------
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            logging.info(f"User submitted query: {prompt}")
            try:
                response = requests.post(
                    f"{FASTAPI_URL}/submit_query",
                    json={"query_text": prompt},
                    timeout=120
                )
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("answer_text", "No answer returned.")
                    st.markdown(answer)

                    logging.info(f"Backend returned answer: {answer}")
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    err_msg = f"❌ Error {response.status_code}: {response.text}"
                    st.error(err_msg)
                    logging.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})
            except requests.exceptions.RequestException as e:
                err_msg = f"🚨 Request failed: {e}"
                st.error(err_msg)
                logging.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": str(e)})
