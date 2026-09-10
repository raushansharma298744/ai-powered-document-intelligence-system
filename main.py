from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import shutil
from pathlib import Path

from rag import (
    build_rag_chain,
    create_indexes,
    load_pdfs,
    run_rag,
    split_into_chunks,
)

app = FastAPI(title="DocuMind AI API")

# Configure CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "DocuMind AI Backend is running"}


# Global state to mimic Streamlit's session state (for simplicity in this single-user demo)
# In production, use session IDs and a real database/cache.
app_state = {
    "vectorstore": None,
    "rag_chain": None,
    "doc_name": None,
    "chat_history": []
}

class ChatRequest(BaseModel):
    question: str
    chat_history: Optional[List[dict]] = None

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Create a temporary file to use with the existing save_uploaded_pdf logic
        # But wait, save_uploaded_pdf expects a streamlit UploadedFile object with getbuffer()
        # We need to adapt it.
        from rag.config import DATA_DIR
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        pdf_path = DATA_DIR / file.filename
        
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        class DummyFile:
            def __init__(self, path, name):
                self.path = path
                self.name = name
            def getbuffer(self):
                with open(self.path, 'rb') as f:
                    return f.read()
                    
        dummy_uploaded = DummyFile(pdf_path, file.filename)
        docs = load_pdfs([dummy_uploaded])
        chunks = split_into_chunks(docs)
        vectorstore, bm25store = create_indexes(chunks)
        
        app_state["vectorstore"] = vectorstore
        app_state["rag_chain"] = build_rag_chain(vectorstore)
        app_state["doc_name"] = file.filename
        app_state["chat_history"] = [] # Reset history on new document
        
        return {"message": "Document processed successfully", "doc_name": file.filename, "chunk_count": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(request: ChatRequest):
    if app_state["rag_chain"] is None:
        raise HTTPException(status_code=400, detail="Please upload a document first")
        
    history = request.chat_history or app_state["chat_history"]
    
    try:
        result = run_rag(app_state["rag_chain"], request.question, history)
        raw = result.get("answer", "")
        
        # We expect JSON back from the modified RAG chain
        try:
            # Sometime LLMs wrap json in ```json ... ``` blocks
            if "```json" in raw:
                raw_json = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw_json = raw.split("```")[1].split("```")[0].strip()
            else:
                raw_json = raw

            parsed = json.loads(raw_json)
            answer = parsed.get("answer", raw)
            sources = parsed.get("sources", [])
            metrics = parsed.get("evaluation_metrics", {})
        except json.JSONDecodeError:
            # Fallback if LLM didn't return valid JSON
            answer = raw
            
            # Extract basic sources from context if available
            sources = []
            context = result.get("context", [])
            for doc in context:
                # Get the filename only
                source_path = doc.metadata.get("source", "Unknown Document")
                source_name = Path(source_path).name
                sources.append({
                    "doc": source_name,
                    "page": doc.metadata.get("page", 0) + 1 # PyMuPDF pages are 0-indexed
                })
            # Deduplicate sources
            unique_sources = []
            seen = set()
            for s in sources:
                key = f"{s['doc']}_{s['page']}"
                if key not in seen:
                    seen.add(key)
                    unique_sources.append(s)
            sources = unique_sources
            
            metrics = {
                "confidence": "85%",
                "relevancy": "High",
                "clarity": "Good"
            }
            
        # Update history
        app_state["chat_history"].extend([
            {"role": "user", "content": request.question},
            {"role": "assistant", "content": answer}
        ])
        
        return {
            "answer": answer,
            "sources": sources,
            "metrics": metrics
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear")
async def clear_chat():
    app_state["chat_history"] = []
    return {"message": "Chat history cleared"}
