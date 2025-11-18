import streamlit as st
import requests
import os
import sys
import logging


# -------------------------------
# Logging Configuration
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# -------------------------------
# Backend URL Configuration
# -------------------------------
# Retrieve the backend URL from the environment variable; if absent, default to localhost.
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")
logging.info(f"Using backend URL: {FASTAPI_URL}")

# -------------------------------
# Streamlit Page Configuration
# -------------------------------
st.set_page_config(page_title="RAG Chatbot", page_icon="💬", layout="centered")
st.title("💬 RAG Chatbot")
st.markdown("Chat with Lijiaxin RAG-powered knowledge base in real time.")

# -------------------------------
# Session State Initialisation
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    if role == "user":
        st.chat_message("user").markdown(content)
    else:
        st.chat_message("assistant").markdown(content)

# -------------------------------
# User input processing
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
                logging.info(f"Request sent to backend: {FASTAPI_URL}/submit_query")
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