from dataclasses import dataclass
from typing import List
from langchain.prompts import ChatPromptTemplate
from langchain_aws import ChatBedrock
# IDE
# from rag_app.get_chroma_db import get_chroma_db
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
    model = ChatBedrock(model_id=BEDROCK_MODEL_ID)

    results = db.similarity_search_with_score(query_text, k=3)

    if not results or len(results) == 0:
        no_response = model.invoke(f"You are a helpful assistant. User said: {query_text}")
        no_response_text = no_response.content
        print(f"✅ Response: {no_response_text}")
        return QueryResponse(query_text=query_text, response_text=no_response_text, sources=[])

    top_doc, top_score = results[0]

    # Setting the threshold (the smaller the more similar)
    threshold = 0.4

    if top_score > threshold:
        # Score is too high => User's question is not relevant to the documentation
        no_rag_response = model.invoke(f"You are a helpful assistant. User said: {query_text}")
        no_rag_response_text = no_rag_response.content
        print(f"✅ Response: {no_rag_response_text}")
        return QueryResponse(query_text=query_text, response_text=no_rag_response_text, sources=[])

    # Otherwise, RAG generation proceeds normally
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)

    model = ChatBedrock(model_id=BEDROCK_MODEL_ID)
    response = model.invoke(prompt)
    response_text = response.content

    sources = [doc.metadata["id"] for doc, _score in results]

    print(f"✅ Response: {response_text}")
    print(f"✅ Sources: {sources}")

    return QueryResponse(
        query_text=query_text,
        response_text=response_text,
        sources=sources
    )


if __name__ == "__main__":
    query_rag("How can I contact Maybank?")
    query_rag("Hi")
