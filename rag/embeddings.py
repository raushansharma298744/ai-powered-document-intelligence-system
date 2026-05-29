"""
Embeddings for RAG (Retrieval step).

LangChain + Google Generative AI:
  Documents → vectors so we can do semantic similarity search in FAISS.
"""

from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from rag.config import EMBEDDING_MODEL, get_google_api_key, is_groq_key


def get_embedding_model() -> Embeddings:
    """Embedding model used to index and query document chunks."""
    if is_groq_key():
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=get_google_api_key(),
    )

