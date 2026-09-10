from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import shutil
from pathlib import Path

from rag import (
    create_indexes,
    load_pdfs,
    split_into_chunks,
)
from rag.pipeline import RAGPipeline

app = FastAPI(title="DocuMind AI API")

# Configure CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        app_state["rag_chain"] = RAGPipeline(vectorstore, bm25store)
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
        pipeline = app_state["rag_chain"]
        result = pipeline.run(request.question, history)
        
        # Update history
        app_state["chat_history"].extend([
            {"role": "user", "content": request.question},
            {"role": "assistant", "content": result["answer"]}
        ])
        
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear")
async def clear_chat():
    app_state["chat_history"] = []
    return {"message": "Chat history cleared"}
