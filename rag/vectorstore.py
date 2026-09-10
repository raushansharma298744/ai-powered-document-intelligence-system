"""
Vector store for RAG (Indexing step — part 2).

LangChain FAISS + Google embeddings:
  Chunks → vectors → local index for fast semantic search.
BM25:
  Chunks → sparse index for keyword search.
"""

import pickle
from pathlib import Path
from typing import List, Optional, Tuple

from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

from rag.config import TOP_K, VECTORSTORE_DIR
from rag.embeddings import get_embedding_model


BM25_FILE = VECTORSTORE_DIR.parent / "bm25_index.pkl"


def create_indexes(chunks: List[Document]) -> Tuple[FAISS, BM25Retriever]:
    """Embed chunks and build new FAISS and BM25 indexes (saved to disk)."""
    embeddings = get_embedding_model()
    store = FAISS.from_documents(chunks, embeddings)
    VECTORSTORE_DIR.parent.mkdir(parents=True, exist_ok=True)
    store.save_local(str(VECTORSTORE_DIR))
    
    # Create and save BM25 retriever
    bm25_retriever = BM25Retriever.from_documents(chunks)
    bm25_retriever.k = TOP_K
    with open(BM25_FILE, "wb") as f:
        pickle.dump(bm25_retriever, f)
        
    return store, bm25_retriever


def load_indexes() -> Tuple[Optional[FAISS], Optional[BM25Retriever]]:
    """Load persisted FAISS and BM25 indexes if they exist."""
    if not VECTORSTORE_DIR.exists():
        return None, None
    
    embeddings = get_embedding_model()
    store = FAISS.load_local(
        str(VECTORSTORE_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )
    
    bm25_retriever = None
    if BM25_FILE.exists():
        with open(BM25_FILE, "rb") as f:
            bm25_retriever = pickle.load(f)
            
    return store, bm25_retriever


def get_retriever(vectorstore: FAISS):
    """Semantic retriever — finds top-k chunks similar to the user question."""
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K},
    )
