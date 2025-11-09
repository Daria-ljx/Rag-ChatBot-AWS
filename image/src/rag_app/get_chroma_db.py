import os
from langchain_community.vectorstores import Chroma
# IDE
# from rag_app.get_embedding_function import get_embedding_function
from src.rag_app.get_embedding_function import get_embedding_function


# Global variables: ensure that the database instance is initialised only once
CHROMA_DB_INSTANCE = None


def get_runtime_chroma_path():
    base_path = "data/chroma"
    return os.path.abspath(base_path)


def get_chroma_db():
    global CHROMA_DB_INSTANCE

    if CHROMA_DB_INSTANCE is None:
        chroma_path = get_runtime_chroma_path()

        # make sure file's path exist
        os.makedirs(chroma_path, exist_ok=True)

        # Initialising a Chroma instance
        CHROMA_DB_INSTANCE = Chroma(
            persist_directory=chroma_path,
            embedding_function=get_embedding_function(),
        )

        print(f"✅ Initialized ChromaDB at: {chroma_path}")

    return CHROMA_DB_INSTANCE