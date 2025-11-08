import argparse
import glob
from tqdm import tqdm
import os
import shutil
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from src.rag_app.get_embedding_function import get_embedding_function


CHROMA_PATH = os.path.abspath("src/data/chroma")
DATA_SOURCE_PATH = os.path.abspath("src/data/source")


def calculate_chunk_ids(chunks):

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata["source"]
        page = chunk.metadata["page"]
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the chunk meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


def add_to_chroma(chunks):
    # Load the existing database.
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function()
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    for chunk in chunks[:3]:
        print(f"✅ Chunk Page Sample: {chunk.metadata['id']}\n{chunk.page_content}\n\n")

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"✅ Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if new_chunks:
        print(f"✅ Adding {len(new_chunks)} new documents to Chroma DB...")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]

        for i in tqdm(range(0, len(new_chunks), 10), ncols=100):
            batch = new_chunks[i:i + 10]
            batch_ids = new_chunk_ids[i:i + 10]
            db.add_documents(batch, ids=batch_ids)
    else:
        print("✅ No new documents to add")


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


def load_documents_split_to_chunks():
    # File-by-file loading, chunking, to avoid reading all PDFs at once
    folders = glob.glob(os.path.join(DATA_SOURCE_PATH, "*"))
    for folder in folders:
        loader = DirectoryLoader(
            folder,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader
        )
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=120, # 20%
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)

        add_to_chroma(chunks)  # Each file is written to DB immediately after chunking to save memory
        del documents, chunks  # Active Memory Release

    print("✅ All documents processed and added to Chroma DB.")


def main():

    # Check if the database should be cleared (using the --clear flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✅ Clearing Database")
        clear_database()

    # Create (or update) the data store.
    load_documents_split_to_chunks()


if __name__ == "__main__":
    main()
