"""
Embeddings for RAG (Retrieval step).

LangChain + Google Generative AI:
  Documents → vectors so we can do semantic similarity search in FAISS.
"""

from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

import os

from rag.config import EMBEDDING_MODEL, get_google_api_key, is_groq_key


def get_embedding_model() -> Embeddings:
    """Embedding model used to index and query document chunks."""
    if is_groq_key():
        try:
            return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        except Exception as exc:
            # Common failure: missing `sentence_transformers` package when using
            # HuggingFace-based embeddings. If a Google API key is available,
            # fall back to Google embeddings; otherwise raise a clear error.
            msg = str(exc).lower()
            if "sentence_transformers" in msg or "sentence-transformers" in msg or isinstance(exc, ImportError):
                google_key = os.getenv("GOOGLE_API_KEY")
                if google_key:
                    return GoogleGenerativeAIEmbeddings(
                        model=EMBEDDING_MODEL, google_api_key=google_key
                    )
                raise ImportError(
                    "HuggingFace embeddings require the sentence-transformers package. "
                    "Install it with `pip install sentence-transformers`, or set a valid "
                    "`GOOGLE_API_KEY` in your .env to use Google embeddings instead."
                ) from exc
            # Re-raise unexpected errors
            raise
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=get_google_api_key(),
    )

