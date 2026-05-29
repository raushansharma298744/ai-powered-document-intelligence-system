"""RAG package — Retrieval-Augmented Generation with LangChain + Google GenAI."""

from rag.chain import build_rag_chain, run_rag
from rag.documents import load_pdfs, split_into_chunks
from rag.vectorstore import create_vectorstore, load_vectorstore

__all__ = [
    "load_pdfs",
    "split_into_chunks",
    "create_vectorstore",
    "load_vectorstore",
    "build_rag_chain",
    "run_rag",
]
