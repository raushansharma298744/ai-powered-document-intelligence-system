# RAG Document QA System

A **Retrieval-Augmented Generation (RAG)** application built with **LangChain** and **Google Generative AI** (Gemini + embeddings).

## RAG pipeline

```
PDF Upload → Text extraction → Chunking → Embeddings (Google GenAI)
    → FAISS vector store → Semantic retrieval → Gemini answer (with context)
```

| Step | Technology |
|------|------------|
| Load | LangChain `PyPDFLoader` |
| Chunk | LangChain `RecursiveCharacterTextSplitter` |
| Embed | `GoogleGenerativeAIEmbeddings` (`models/gemini-embedding-001`) |
| Store | LangChain `FAISS` |
| Retrieve | LangChain retriever (similarity, top-k) |
| Generate | `ChatGoogleGenerativeAI` (`gemini-3-flash-preview`) |
| Orchestration | `create_history_aware_retriever` + `create_retrieval_chain` |

## Project structure

```
├── app.py                 # Streamlit UI
├── rag/
│   ├── config.py          # Models & paths
│   ├── documents.py       # Load + chunk (indexing)
│   ├── embeddings.py      # Google GenAI embeddings
│   ├── vectorstore.py     # FAISS index
│   └── chain.py           # LangChain RAG chain + memory
├── requirements.txt
└── .env.example
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` → `.env` and set your API key. Prefer `GROK_API_KEY` for Grok, or
fall back to `GOOGLE_API_KEY` for Google Gemini:

```
GROK_API_KEY=your_grok_key_here
OR
GOOGLE_API_KEY=your_google_key_here
```

## Run

```bash
streamlit run app.py
```

1. Upload PDF(s) in the sidebar  
2. Click **Build RAG index**  
3. Ask questions — answers use **retrieved chunks** + **Gemini**

## Why LangChain for RAG?

- Standard **retriever → chain → LLM** pattern  
- **History-aware retrieval** for follow-up questions  
- Swappable vector stores and models  
- Production-style composition without boilerplate API calls  
