import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class RagTrace:
    trace_id: str
    question: str
    rewritten_query: Optional[str] = None
    
    dense_results: List[Dict[str, Any]] = field(default_factory=list)
    sparse_results: List[Dict[str, Any]] = field(default_factory=list)
    fusion_results: List[Dict[str, Any]] = field(default_factory=list)
    reranked_results: List[Dict[str, Any]] = field(default_factory=list)
    
    selected_context: List[Dict[str, Any]] = field(default_factory=list)
    evidence_status: str = "UNKNOWN"
    
    answer: str = ""
    citations: List[Dict[str, Any]] = field(default_factory=list)
    
    timings: Dict[str, float] = field(default_factory=lambda: {
        "query_rewrite_ms": 0.0,
        "dense_retrieval_ms": 0.0,
        "sparse_retrieval_ms": 0.0,
        "fusion_ms": 0.0,
        "reranking_ms": 0.0,
        "generation_ms": 0.0,
        "total_ms": 0.0
    })
    
    token_usage: Dict[str, int] = field(default_factory=lambda: {
        "input_tokens": 0,
        "output_tokens": 0
    })

class Tracer:
    def __init__(self, trace_id: str, question: str):
        self.trace = RagTrace(trace_id=trace_id, question=question)
        self.start_time = time.time()
        self.step_starts = {}

    def start_step(self, step_name: str):
        self.step_starts[step_name] = time.time()

    def end_step(self, step_name: str, timing_key: str):
        if step_name in self.step_starts:
            elapsed_ms = (time.time() - self.step_starts[step_name]) * 1000
            self.trace.timings[timing_key] = round(elapsed_ms, 2)
            
    def finalize(self):
        self.trace.timings["total_ms"] = round((time.time() - self.start_time) * 1000, 2)
        return self.trace
