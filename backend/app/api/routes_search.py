from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..schemas.search import SearchRequest, SearchResponse, SearchHistoryItem
from ..services.search_service import SearchService

router = APIRouter(prefix="/api/search", tags=["search"])

def get_search_service() -> SearchService:
    from ..main import search_service
    return search_service

@router.post("", response_model=SearchResponse)
async def search_memory(payload: SearchRequest):
    search_svc = get_search_service()
    if not payload.query or not payload.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    return search_svc.execute_search(payload)

@router.get("/history", response_model=List[SearchHistoryItem])
async def get_history(limit: int = 10):
    search_svc = get_search_service()
    history = search_svc.get_search_history(limit)
    return [
        SearchHistoryItem(
            id=item["id"],
            query=item["query"],
            result_count=item["result_count"],
            created_at=str(item["created_at"])
        )
        for item in history
    ]

@router.delete("/history")
async def clear_history():
    search_svc = get_search_service()
    search_svc.clear_history()
    return {"message": "Search history cleared"}
