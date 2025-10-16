import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

PERSIST_DIRECTORY = "./storage"

KNOWLEDGE_BASE_DIR = "./knowledge_base"

def main():
    print("--- Starting Data Ingestion ---")

    print(f"Loading documents from: {KNOWLEDGE_BASE_DIR}")
    loader = DirectoryLoader(KNOWLEDGE_BASE_DIR, glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()
    if not documents:
        print("No documents found. Exiting.")
        return

    print(f"Loaded {len(documents)} document(s).")

    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    print(f"Split into {len(texts)} chunks.")

    print("Creating embeddings with OpenAI")
    embeddings = OpenAIEmbeddings()

    if os.path.exists(PERSIST_DIRECTORY):
        print("Deleting old vector store...")
        import shutil
        shutil.rmtree(PERSIST_DIRECTORY)

    print(f"Creating and persisting vector store at: {PERSIST_DIRECTORY}")
    db = Chroma.from_documents(
        texts, 
        embeddings, 
        persist_directory=PERSIST_DIRECTORY
    )
    db.persist()
    print("--- Ingestion Complete ---")

if __name__ == "__main__":
    main()