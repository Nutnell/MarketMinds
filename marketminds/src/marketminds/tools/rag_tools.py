from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from langchain_chroma import Chroma  # ✅ Updated import
from langchain_openai import OpenAIEmbeddings
import os


class RAGInput(BaseModel):
    """Input schema for the RAG Tool."""
    query: str = Field(..., description="The specific question or topic to search for in the knowledge base.")


class RAGTool(BaseTool):
    name: str = "Knowledge Base Search"
    description: str = "Searches the company's internal knowledge base for information on investment strategies and philosophies."
    args_schema: Type[BaseModel] = RAGInput

    def __init__(self, persist_directory: str = None, **kwargs):
        super().__init__(**kwargs)

        self._persist_directory = persist_directory or os.getenv("CHROMA_DB_DIR", "/tmp/chroma_db")

        os.makedirs(self._persist_directory, exist_ok=True)

        self._embeddings = OpenAIEmbeddings()
        self._vector_store = Chroma(
            persist_directory=self._persist_directory,
            embedding_function=self._embeddings
        )

    def _run(self, query: str) -> str:
        """The tool's main execution logic."""
        try:
            retriever = self._vector_store.as_retriever(search_kwargs={'k': 3})
            relevant_docs = retriever.invoke(query)

            if not relevant_docs:
                return "No relevant information found in the knowledge base for that query."

            formatted_docs = [
                f"Source: {doc.metadata.get('source', 'N/A')}\nContent: {doc.page_content}"
                for doc in relevant_docs
            ]
            return "\n\n---\n\n".join(formatted_docs)

        except Exception as e:
            return f"Error searching knowledge base: {e}"
