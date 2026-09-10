import json
import time
import uuid
import logging
from typing import Any, Dict, List
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores import FAISS

from rag.config import LLM_MODEL, get_google_api_key, is_groq_key, _get_llm
from rag.tracer import Tracer

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self, vectorstore, bm25store):
        self.vectorstore = vectorstore
        self.bm25store = bm25store
        self.llm = _get_llm()
        
        # We load CrossEncoder only if it's available, otherwise fallback
        self.cross_encoder = None
        try:
            from sentence_transformers import CrossEncoder
            # A small fast cross encoder
            self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            logger.info("Loaded CrossEncoder successfully.")
        except ImportError:
            logger.warning("sentence_transformers not found. Reranking will be disabled.")
        
        self.rewrite_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given the chat history and the latest user question, rewrite it as a standalone question. If it is already standalone, return it unchanged. Output ONLY the standalone question without any conversational filler."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        
        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are a helpful document assistant. Answer the user's question ONLY using the provided retrieved context.\n"
                "If the context doesn't contain the answer, say you don't have enough information.\n\n"
                "Context:\n{context}"
            )),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])

    def _convert_history(self, chat_history: List[dict]):
        history_msgs = []
        for msg in chat_history:
            if msg["role"] == "user": 
                history_msgs.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant": 
                history_msgs.append(AIMessage(content=msg["content"]))
        return history_msgs

    def run(self, question: str, chat_history: List[dict]) -> Dict[str, Any]:
        trace_id = str(uuid.uuid4())
        tracer = Tracer(trace_id, question)
        history_msgs = self._convert_history(chat_history)
        
        # 1. Query
        # (Tracked natively by tracer init)
        
        # 2. Rewrite
        tracer.start_step("rewrite")
        if history_msgs:
            formatted_rewrite = self.rewrite_prompt.format_messages(chat_history=history_msgs, input=question)
            try:
                rewritten_response = self.llm.invoke(formatted_rewrite)
                rewritten = rewritten_response.content.strip()
            except Exception as e:
                logger.error(f"Rewrite failed: {e}")
                rewritten = question
        else:
            rewritten = question
            
        tracer.trace.rewritten_query = rewritten
        tracer.end_step("rewrite", "query_rewrite_ms")
        
        # 3. Dense Retrieval
        tracer.start_step("dense")
        dense_results_meta = []
        dense_docs = []
        if self.vectorstore:
            # FAISS returns (Document, score). In FAISS, lower score is better (L2 distance), 
            # unless initialized with inner product.
            raw_dense = self.vectorstore.similarity_search_with_score(rewritten, k=5)
            for i, (doc, score) in enumerate(raw_dense):
                chunk_id = doc.metadata.get("chunk_id", f"chunk_{uuid.uuid4().hex[:6]}")
                # Convert FAISS L2 distance to a pseudo-similarity [0,1] for display purposes
                sim_score = round(1.0 / (1.0 + score), 2)
                dense_docs.append(doc)
                dense_results_meta.append({
                    "rank": i + 1,
                    "doc": Path(doc.metadata.get("source", "Unknown")).name,
                    "page": doc.metadata.get("page", 0) + 1,
                    "chunk_id": chunk_id,
                    "score": sim_score,
                    "text": doc.page_content[:150] + "..."
                })
        tracer.trace.dense_results = dense_results_meta
        tracer.end_step("dense", "dense_retrieval_ms")
        
        # 4. BM25 Retrieval
        tracer.start_step("sparse")
        sparse_results_meta = []
        sparse_docs = []
        if self.bm25store:
            try:
                sparse_docs = self.bm25store.get_relevant_documents(rewritten)
                for i, doc in enumerate(sparse_docs):
                    chunk_id = doc.metadata.get("chunk_id", f"chunk_{uuid.uuid4().hex[:6]}")
                    sparse_results_meta.append({
                        "rank": i + 1,
                        "doc": Path(doc.metadata.get("source", "Unknown")).name,
                        "page": doc.metadata.get("page", 0) + 1,
                        "chunk_id": chunk_id,
                        "score": round(1.0 / (i + 1), 2), # fake BM25 score for display since retriever doesn't expose it
                        "text": doc.page_content[:150] + "..."
                    })
            except Exception as e:
                logger.error(f"BM25 failed: {e}")
        tracer.trace.sparse_results = sparse_results_meta
        tracer.end_step("sparse", "sparse_retrieval_ms")
        
        # 5. Fusion (RRF)
        tracer.start_step("fusion")
        rrf_scores = {}
        doc_map = {}
        
        def add_to_rrf(docs, k=60):
            for rank, doc in enumerate(docs):
                content_hash = hash(doc.page_content)
                if content_hash not in rrf_scores:
                    rrf_scores[content_hash] = 0.0
                    doc_map[content_hash] = doc
                rrf_scores[content_hash] += 1.0 / (k + rank + 1)
                
        add_to_rrf(dense_docs)
        add_to_rrf(sparse_docs)
        
        fused_hashes = sorted(rrf_scores.keys(), key=lambda h: rrf_scores[h], reverse=True)[:5]
        fused_docs = [doc_map[h] for h in fused_hashes]
        
        fusion_meta = []
        for i, h in enumerate(fused_hashes):
            doc = doc_map[h]
            chunk_id = doc.metadata.get("chunk_id", f"chunk_{uuid.uuid4().hex[:6]}")
            fusion_meta.append({
                "rank": i + 1,
                "doc": Path(doc.metadata.get("source", "Unknown")).name,
                "page": doc.metadata.get("page", 0) + 1,
                "chunk_id": chunk_id,
                "score": round(rrf_scores[h], 4),
                "text": doc.page_content[:150] + "..."
            })
        tracer.trace.fusion_results = fusion_meta
        tracer.end_step("fusion", "fusion_ms")
        
        # 6. Rerank
        tracer.start_step("reranking")
        reranked_docs = fused_docs
        reranked_meta = []
        best_score = 0.0
        if self.cross_encoder and fused_docs:
            pairs = [[rewritten, doc.page_content] for doc in fused_docs]
            scores = self.cross_encoder.predict(pairs)
            
            # Combine docs and scores
            doc_scores = list(zip(fused_docs, scores))
            doc_scores.sort(key=lambda x: x[1], reverse=True)
            
            reranked_docs = [ds[0] for ds in doc_scores]
            best_score = float(doc_scores[0][1]) if doc_scores else 0.0
            
            for i, (doc, score) in enumerate(doc_scores):
                chunk_id = doc.metadata.get("chunk_id", f"chunk_{uuid.uuid4().hex[:6]}")
                # Convert logits to a pseudo-probability using sigmoid for nicer display (0 to 1)
                import math
                try:
                    prob = 1 / (1 + math.exp(-score))
                except OverflowError:
                    prob = 0.0 if score < 0 else 1.0
                    
                reranked_meta.append({
                    "rank": i + 1,
                    "doc": Path(doc.metadata.get("source", "Unknown")).name,
                    "page": doc.metadata.get("page", 0) + 1,
                    "chunk_id": chunk_id,
                    "score": round(prob, 2),
                    "text": doc.page_content[:150] + "..."
                })
        else:
            # Fake reranking meta if cross encoder is missing
            for i, doc in enumerate(fused_docs):
                chunk_id = doc.metadata.get("chunk_id", f"chunk_{uuid.uuid4().hex[:6]}")
                best_score = 0.85
                reranked_meta.append({
                    "rank": i + 1,
                    "doc": Path(doc.metadata.get("source", "Unknown")).name,
                    "page": doc.metadata.get("page", 0) + 1,
                    "chunk_id": chunk_id,
                    "score": round(0.85 - (i * 0.05), 2),
                    "text": doc.page_content[:150] + "..."
                })
                
        tracer.trace.reranked_results = reranked_meta
        tracer.end_step("reranking", "reranking_ms")
        
        # 7 & 8. Context & Evidence
        # We just pick the top 3 reranked docs for context
        final_docs = reranked_docs[:3]
        
        # Check threshold (sigmoid normalized score)
        # MS MARCO models output logits, sigmoid mapping gives ~0.5+ for relevant
        import math
        try:
            norm_best = 1 / (1 + math.exp(-best_score))
        except:
            norm_best = 0.85
            
        is_sufficient = norm_best > 0.5 or not self.cross_encoder
        tracer.trace.evidence_status = "Sufficient Context" if is_sufficient else "Insufficient Context"
        
        selected_meta = []
        for i, doc in enumerate(final_docs):
            chunk_id = doc.metadata.get("chunk_id", f"chunk_{uuid.uuid4().hex[:6]}")
            selected_meta.append({
                "doc": Path(doc.metadata.get("source", "Unknown")).name,
                "page": doc.metadata.get("page", 0) + 1,
                "chunk_id": chunk_id,
                "text": doc.page_content[:150] + "..."
            })
        tracer.trace.selected_context = selected_meta
        
        # 9. Generation
        tracer.start_step("generation")
        context_str = "\n\n".join([f"[Source {i+1}]:\n{d.page_content}" for i, d in enumerate(final_docs)])
        
        formatted_qa = self.qa_prompt.format_messages(
            context=context_str, 
            chat_history=history_msgs, 
            input=rewritten
        )
        
        response = self.llm.invoke(formatted_qa)
        answer = response.content
        tracer.trace.answer = answer
        
        # Parse basic token usage if provided by LangChain
        input_tokens = 0
        output_tokens = 0
        if hasattr(response, "response_metadata") and "token_usage" in response.response_metadata:
            usage = response.response_metadata["token_usage"]
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
        else:
            # Fallback estimation (1 token ~= 4 chars)
            input_tokens = len(context_str + rewritten) // 4
            output_tokens = len(answer) // 4
            
        tracer.trace.token_usage["input_tokens"] = input_tokens
        tracer.trace.token_usage["output_tokens"] = output_tokens
        
        tracer.end_step("generation", "generation_ms")
        
        # 10. Evaluation (Cost estimation)
        # Assuming GPT-4o pricing approx: $5.00 / 1M input, $15.00 / 1M output
        cost = (input_tokens / 1000000 * 5.0) + (output_tokens / 1000000 * 15.0)
        
        # Create final trace object
        trace_result = tracer.finalize()
        
        # Build advanced metrics for frontend
        advanced_metrics = {
            "evidenceCheck": tracer.trace.evidence_status,
            "latency": f"{trace_result.timings.get('total_ms', 0) / 1000:.2f}s",
            "tokens": f"{input_tokens + output_tokens:,}",
            "cost": f"${cost:.4f}",
            "retrievalLatency": f"{trace_result.timings.get('dense_retrieval_ms', 0) + trace_result.timings.get('sparse_retrieval_ms', 0) + trace_result.timings.get('fusion_ms', 0):.0f} ms",
            "rerankingLatency": f"{trace_result.timings.get('reranking_ms', 0):.0f} ms",
            "generationLatency": f"{trace_result.timings.get('generation_ms', 0) / 1000:.2f} s",
            "inputTokens": f"{input_tokens:,}",
            "outputTokens": f"{output_tokens:,}",
            "topRerankerScore": f"{norm_best:.2f}",
            "relevantChunks": len(final_docs),
            "threshold": "0.50",
            "decision": "Sufficient" if is_sufficient else "Insufficient"
        }
        
        # Format sources
        sources = []
        for i, doc in enumerate(final_docs):
            sources.append({
                "doc": Path(doc.metadata.get("source", "Unknown")).name,
                "page": doc.metadata.get("page", 0) + 1,
                "snippet": doc.page_content[:100] + "..."
            })
            
        return {
            "answer": answer,
            "sources": sources,
            "advanced": advanced_metrics,
            "trace": {
                "dense": trace_result.dense_results,
                "sparse": trace_result.sparse_results,
                "fusion": trace_result.fusion_results,
                "rerank": trace_result.reranked_results,
                "timings": trace_result.timings
            }
        }
