import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from src.query_model import QueryModel
from src.rag_app.query_rag import query_rag
# IDE
# from query_model import QueryModel
# from rag_app.query_rag import query_rag

app = FastAPI()


class SubmitQueryRequest(BaseModel):
    query_text: str

@app.get("/")
def index():
    return {"Hello": "World"}


@app.get("/get_query")
def get_query_endpoint(query_id: str) -> QueryModel:
    query = QueryModel.get_item(query_id)
    return query


@app.post("/submit_query")
def submit_query_endpoint(request: SubmitQueryRequest) -> QueryModel:
    # Create the query item, and put it into the data-base.
    new_query = QueryModel(query_text=request.query_text)

    # Make a synchronous call to the worker (the RAG/AI MAE_App).
    query_response = query_rag(request.query_text)
    new_query.answer_text = query_response.response_text
    new_query.sources = query_response.sources
    new_query.is_complete = True
    new_query.put_item()

    return new_query


if __name__ == "__main__":
    # Run this as a server directly.
    port = 8000
    print(f"✅ Running the FastAPI server on port {port}.")
    uvicorn.run("app_api_handler:app", host="127.0.0.1", port=port)
