"""RAG configuration — models, paths, and retrieval settings."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

# --- Google Generative AI (LangChain integration) ---
# Must use "models/..." prefix — text-embedding-004 causes 400 "unexpected model name format"
EMBEDDING_MODEL = "models/gemini-embedding-001"
LLM_MODEL = "gemini-3-flash-preview"

# --- RAG tuning ---
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 4  # number of chunks retrieved per query

# --- Local storage ---
DATA_DIR = Path("data")
VECTORSTORE_DIR = Path("vectorstore") / "faiss_index"


def get_google_api_key() -> str:
    # Prefer a Grok key if provided, fall back to Google key for backward compatibility
    key = os.getenv("GROK_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ValueError(
            "API key is missing. Set GROK_API_KEY or GOOGLE_API_KEY in your .env file."
        )
    return key


def is_groq_key() -> bool:
    try:
        return get_google_api_key().startswith("gsk_")
    except Exception:
        return False

