import streamlit as st
import requests
import os

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

st.set_page_config(page_title="RAG Chatbot", page_icon="💬", layout="centered")

st.title("💬 RAG Chatbot")
st.markdown("Chat with Lijiaxin RAG-powered knowledge base in real time.")

# Create
if "messages" not in st.session_state:
    st.session_state.messages = []

# show the chat messages
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    if role == "user":
        st.chat_message("user").markdown(content)
    else:
        st.chat_message("assistant").markdown(content)

# chatbot input box
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
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

                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    err_msg = f"❌ Error {response.status_code}: {response.text}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})
            except requests.exceptions.RequestException as e:
                st.error(f"🚨 Request failed: {e}")
                st.session_state.messages.append({"role": "assistant", "content": str(e)})
