from dataclasses import dataclass
from typing import List
from langchain.prompts import ChatPromptTemplate
from langchain_aws import ChatBedrock
from src.rag_app.get_chroma_db import get_chroma_db

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

BEDROCK_MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"


@dataclass
class QueryResponse:
    query_text: str
    response_text: str
    sources: List[str]


def query_rag(query_text: str) -> QueryResponse:
    db = get_chroma_db()
    if db:
        print("✅ Connect to DB successfully.")
    model = ChatBedrock(model_id=BEDROCK_MODEL_ID)

    # Search the DB
    results = db.similarity_search_with_score(query_text, k=3)

    if not results:
        # 没有找到文档，直接用LLM回答
        no_response = model.invoke(f"You are a helpful assistant. User said: {query_text}")
        print(f"✅ Response: (No RAG) {no_response.content}")
        return QueryResponse(query_text=query_text, response_text=no_response.content, sources=[])

    # 提取分数并计算平均分
    scores = [score for _, score in results]
    avg_score = sum(scores) / len(scores)
    min_score = min(scores)
    threshold = avg_score * 1.3  # 动态阈值
    # min_absolute_threshold = 0.5  #embeddin

    print(f"[DEBUG] Retrieved scores: {scores}, min_score: {min_score:.3f}, dynamic_threshold: {threshold:.3f}")

    # Chroma 距离越小越相似，所以 min_score < threshold 表示匹配度高
    if min_score < threshold:
        # 使用 RAG 上下文生成答案
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)
        print(prompt)

        response = model.invoke(prompt)
        response_text = response.content
        sources = [doc.metadata.get("id", None) for doc, _ in results]

        print(f"✅ Response: {response_text}\n✅ Sources: {sources}")
        return QueryResponse(query_text=query_text, response_text=response_text, sources=sources)
    else:
        # 匹配度低，直接用 LLM 回答
        response = model.invoke(f"You are a helpful assistant. User said: {query_text}")
        print(f"⚠️ Low similarity, skipping RAG. Response: {response.content}")
        return QueryResponse(query_text=query_text, response_text=response.content, sources=[])


if __name__ == "__main__":
    # query_rag("How much does a landing page cost to develop?")
    query_rag("How can i contact Maybank?")