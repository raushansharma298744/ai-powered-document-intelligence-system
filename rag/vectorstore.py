"""
Vector store for RAG (Indexing step — part 2).

LangChain FAISS + Google embeddings:
  Chunks → vectors → local index for fast semantic search.
"""

from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from rag.config import TOP_K, VECTORSTORE_DIR
from rag.embeddings import get_embedding_model


def create_vectorstore(chunks: List[Document]) -> FAISS:
    """Embed chunks and build a new FAISS index (saved to disk)."""
    embeddings = get_embedding_model()
    store = FAISS.from_documents(chunks, embeddings)
    VECTORSTORE_DIR.parent.mkdir(parents=True, exist_ok=True)
    store.save_local(str(VECTORSTORE_DIR))
    return store


def load_vectorstore() -> Optional[FAISS]:
    """Load persisted FAISS index if it exists."""
    if not VECTORSTORE_DIR.exists():
        return None
    embeddings = get_embedding_model()
    return FAISS.load_local(
        str(VECTORSTORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def get_retriever(vectorstore: FAISS):
    """Semantic retriever — finds top-k chunks similar to the user question."""
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K},
    )
