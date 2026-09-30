import math
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from ..core.logging import logger

class SearchRanker:
    """
    Aggregates chunk-level vector scores into file-level relevance rankings.
    Computes grounded relevance percentages and incorporates recency weighting.
    """

    @classmethod
    def aggregate_and_rank(
        cls,
        chunk_matches: List[Tuple[Dict[str, Any], float]],
        query: str,
        is_time_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        if not chunk_matches:
            return []

        # Group by file_id
        files_map: Dict[int, Dict[str, Any]] = {}

        for chunk_meta, score in chunk_matches:
            file_id = chunk_meta["file_id"]
            if file_id not in files_map:
                files_map[file_id] = {
                    "file_id": file_id,
                    "filename": chunk_meta["filename"],
                    "path": chunk_meta["path"],
                    "extension": chunk_meta["extension"],
                    "modified_at": chunk_meta.get("modified_at"),
                    "size": chunk_meta.get("size"),
                    "chunk_scores": [],
                    "best_chunk": chunk_meta["content"],
                    "best_score": score,
                    "chunks_matched": 0
                }

            files_map[file_id]["chunk_scores"].append(score)
            files_map[file_id]["chunks_matched"] += 1
            if score > files_map[file_id]["best_score"]:
                files_map[file_id]["best_score"] = score
                files_map[file_id]["best_chunk"] = chunk_meta["content"]

        # Calculate final file-level score
        ranked_results: List[Dict[str, Any]] = []

        now = datetime.now()

        for file_id, data in files_map.items():
            scores = data["chunk_scores"]
            max_score = data["best_score"]

            # Base score: heavily weighted towards best matching chunk + marginal gain for multiple chunk matches
            additional_chunks_boost = min(0.08, math.log1p(len(scores) - 1) * 0.04) if len(scores) > 1 else 0.0
            composite_score = min(0.99, max_score + additional_chunks_boost)

            # Recency boost if query is time-aware ("worked on recently", "recent")
            if is_time_sensitive and data.get("modified_at"):
                try:
                    mod_dt = datetime.fromisoformat(data["modified_at"])
                    diff_days = (now - mod_dt).days
                    if diff_days <= 1:
                        composite_score = min(0.99, composite_score + 0.15)
                    elif diff_days <= 7:
                        composite_score = min(0.99, composite_score + 0.10)
                    elif diff_days <= 30:
                        composite_score = min(0.99, composite_score + 0.05)
                except Exception:
                    pass

            # Format affinity boost (e.g. query explicitly asks for 'pdf' or 'code')
            query_clean = query.lower()
            ext = data["extension"].lower()
            if "pdf" in query_clean and ext == ".pdf":
                composite_score = min(0.99, composite_score + 0.12)
            elif any(w in query_clean for w in ["code", "cpp", "implementation", "program", "function"]) and ext in [".cpp", ".py", ".c", ".java", ".js", ".ts", ".tsx"]:
                composite_score = min(0.99, composite_score + 0.10)
            elif any(w in query_clean for w in ["notes", "document", "doc", "text"]) and ext in [".pdf", ".docx", ".txt", ".md"]:
                composite_score = min(0.99, composite_score + 0.06)

            # Boost exact filename match if query contains filename
            fname_clean = data["filename"].lower()
            if fname_clean in query_clean or query_clean in fname_clean:
                composite_score = max(composite_score, 0.98)

            ranked_results.append({
                "file_id": file_id,
                "filename": data["filename"],
                "path": data["path"],
                "extension": data["extension"],
                "score": round(composite_score, 3),
                "matched_content": data["best_chunk"][:600],
                "modified_at": data.get("modified_at"),
                "size": data.get("size"),
                "chunks_matched": data["chunks_matched"]
            })

        # Sort descending by composite score
        ranked_results.sort(key=lambda x: x["score"], reverse=True)
        return ranked_results
