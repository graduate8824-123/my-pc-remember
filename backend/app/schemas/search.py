from pydantic import BaseModel, Field
from typing import List, Optional

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: Optional[int] = 8
    use_llm_explanation: Optional[bool] = True
    time_filter: Optional[str] = None  # "recent", "today", "week", "month", or None

class SearchResultItem(BaseModel):
    file_id: int
    filename: str
    path: str
    extension: str
    score: float # 0.0 to 1.0 (or percentage: e.g. 0.94 -> 94%)
    matched_content: str
    reason: str
    modified_at: Optional[str] = None
    size: Optional[int] = None
    chunks_matched: int = 1

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    total_found: int
    time_taken_ms: float
    llm_available: bool
    mode: str # "semantic_rag", "semantic_vector", "exact_filename", "keyword"
    note: Optional[str] = None

class SearchHistoryItem(BaseModel):
    id: int
    query: str
    result_count: int
    created_at: str
