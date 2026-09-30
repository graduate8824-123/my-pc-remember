from typing import Dict, Any, List
from ..core.logging import logger
from ..db.repositories import Repository
from ..vectorstore.faiss_store import FAISSVectorStore
from ..retrieval.retriever import MemoryRetriever
from ..schemas.search import SearchRequest, SearchResponse

class SearchService:
    """
    Search Coordinator service.
    Directs incoming user queries to the MemoryRetriever.
    """

    def __init__(self, repo: Repository, vector_store: FAISSVectorStore):
        self.repo = repo
        self.vector_store = vector_store
        self.retriever = MemoryRetriever(repo, vector_store)

    def execute_search(self, request: SearchRequest) -> SearchResponse:
        logger.info(f"Executing search query: '{request.query}'")
        raw = self.retriever.search(
            query=request.query,
            top_k=request.top_k or 8,
            use_llm_explanation=request.use_llm_explanation if request.use_llm_explanation is not None else True
        )
        return SearchResponse(**raw)

    def get_search_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.repo.get_recent_searches(limit)

    def clear_history(self) -> None:
        self.repo.clear_search_history()
