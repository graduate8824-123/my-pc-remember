import re
import time
from typing import List, Dict, Any, Optional
from ..core.logging import logger
from ..core.config import settings
from ..db.repositories import Repository
from ..embeddings.local_embeddings import get_embedding_provider
from ..vectorstore.faiss_store import FAISSVectorStore
from ..llm import get_llm_provider
from .ranker import SearchRanker

TIME_AWARE_PATTERNS = [
    r'\brecent(ly)?\b',
    r'\btoday\b',
    r'\byesterday\b',
    r'\blast\s+week\b',
    r'\bworked\s+on\b',
    r'\bmodified\b'
]

class MemoryRetriever:
    """
    Core Semantic & Natural Memory Retrieval Engine.
    Executes hybrid semantic vector search, time-aware ranking,
    and generates grounded explanations for each match.
    """

    def __init__(self, repo: Repository, vector_store: FAISSVectorStore):
        self.repo = repo
        self.vector_store = vector_store
        self.embedding_provider = get_embedding_provider()
        self.llm_provider = get_llm_provider()

    def search(
        self,
        query: str,
        top_k: int = 8,
        use_llm_explanation: bool = True
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()
        clean_query = query.strip()
        if not clean_query:
            return {
                "query": query,
                "results": [],
                "total_found": 0,
                "time_taken_ms": 0.0,
                "llm_available": self.llm_provider.is_available(),
                "mode": "empty"
            }

        # Check time awareness
        is_time_sensitive = any(re.search(pat, clean_query, re.IGNORECASE) for pat in TIME_AWARE_PATTERNS)

        # 1. Generate query embedding
        query_vector = self.embedding_provider.embed_text(clean_query)

        # 2. Vector search in FAISS
        # Retrieve more chunks (2.5x) to allow file grouping & diversification
        raw_matches = self.vector_store.search(query_vector, top_k=top_k * 3)

        chunk_matches = []
        for chunk_id, score in raw_matches:
            # Filter low relevance baseline
            if score < settings.SIMILARITY_THRESHOLD:
                continue
            chunk_data = self.repo.get_chunk_by_vector_id(chunk_id)
            if chunk_data:
                chunk_matches.append((chunk_data, score))

        # 3. Exact filename / keyword check fallback
        # If user typed "dijkstra.cpp" or "graph_notes.pdf", make sure it's surfaced
        tokens = re.findall(r'\b[\w\.\-]+\b', clean_query)
        for token in tokens:
            if "." in token: # potential file extension or filename
                cursor = self.repo.conn.cursor()
                cursor.execute("SELECT id, path, filename, extension, modified_at, size FROM files WHERE filename LIKE ?", (f"%{token}%",))
                for r in cursor.fetchall():
                    # Fetch first chunk for this file
                    c_cursor = self.repo.conn.cursor()
                    c_cursor.execute("SELECT id, content FROM chunks WHERE file_id = ? LIMIT 1", (r[0],))
                    c_row = c_cursor.fetchone()
                    if c_row:
                        chunk_matches.append(({
                            "chunk_id": c_row[0],
                            "file_id": r[0],
                            "filename": r[2],
                            "path": r[1],
                            "extension": r[3],
                            "modified_at": r[4],
                            "size": r[5],
                            "content": c_row[1]
                        }, 0.98))

        # 4. Group and rank at file level
        ranked_files = SearchRanker.aggregate_and_rank(chunk_matches, clean_query, is_time_sensitive)
        top_results = ranked_files[:top_k]

        # 5. Generate grounded explanations
        llm_is_online = self.llm_provider.is_available()

        for item in top_results:
            if use_llm_explanation and llm_is_online:
                try:
                    reason = self.llm_provider.explain_match(
                        query=clean_query,
                        filename=item["filename"],
                        matched_chunk=item["matched_content"]
                    )
                except Exception as e:
                    logger.warning(f"Error generating LLM explanation: {e}")
                    reason = "Relevant content found matching semantic context."
            else:
                reason = "Semantic match found in local index."
            item["reason"] = reason

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # 6. Log search in history
        self.repo.log_search(clean_query, len(top_results))

        mode = "semantic_rag" if llm_is_online else "semantic_vector"
        note = None
        if not llm_is_online:
            note = "Local language model unavailable. Showing semantic search results."

        return {
            "query": clean_query,
            "results": top_results,
            "total_found": len(top_results),
            "time_taken_ms": elapsed_ms,
            "llm_available": llm_is_online,
            "mode": mode,
            "note": note
        }
