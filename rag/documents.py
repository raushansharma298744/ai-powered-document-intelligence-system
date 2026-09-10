"""
Document ingestion for RAG (Indexing step — part 1).

LangChain:
  - PyPDFLoader: extract text from PDFs
  - RecursiveCharacterTextSplitter: chunk text for retrieval
"""

from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.config import CHUNK_OVERLAP, CHUNK_SIZE, DATA_DIR


def save_uploaded_pdf(uploaded_file) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / uploaded_file.name
    path.write_bytes(uploaded_file.getbuffer())
    return path


def load_pdfs(uploaded_files) -> List[Document]:
    """Load all uploaded PDFs into LangChain Document objects."""
    documents: List[Document] = []

    for uploaded in uploaded_files:
        pdf_path = save_uploaded_pdf(uploaded)
        pages = PyMuPDFLoader(str(pdf_path)).load()
        for page in pages:
            page.metadata["source"] = uploaded.name
        documents.extend(pages)

    if not documents:
        raise ValueError("No text extracted from PDF(s).")
    return documents


def split_into_chunks(documents: List[Document]) -> List[Document]:
    """
    Split documents into overlapping chunks.

    Why chunk? LLMs have limited context; retrieval needs small, focused passages.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        add_start_index=True,
    )
    chunks = splitter.split_documents(documents)
    if not chunks:
        raise ValueError("No text could be extracted from the PDF. It might be a scanned document without OCR.")
        
    for i, chunk in enumerate(chunks):
        doc_name = chunk.metadata.get("source", "unknown")
        # Ensure it's a simple filename
        doc_name = Path(doc_name).name
        chunk.metadata["chunk_id"] = f"{doc_name}_chunk_{i}"
    return chunks
