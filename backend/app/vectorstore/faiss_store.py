import os
import json
from pathlib import Path
import numpy as np
from typing import List, Tuple, Optional
from .base import VectorStore
from ..core.logging import logger

class FAISSVectorStore(VectorStore):
    """
    Local FAISS Index for fast, memory-efficient nearest neighbor search on CPU.
    Uses IndexFlatIP with L2 normalized vectors for exact Cosine Similarity.
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = None
        self.id_map: List[int] = [] # index_pos -> chunk_id
        self._init_index()

    def _init_index(self):
        try:
            import faiss
            self.index = faiss.IndexFlatIP(self.dimension)
            self.id_map = []
        except Exception as e:
            logger.warning(f"FAISS could not be initialized ({e}). Using Numpy fallback store.")
            self.index = None

    @property
    def count(self) -> int:
        if self.index is not None:
            return self.index.ntotal
        return len(self.id_map)

    def add(self, vectors: List[List[float]], ids: List[int]) -> None:
        if not vectors or not ids:
            return
        
        arr = np.array(vectors, dtype=np.float32)
        # Normalize for cosine similarity
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        norm_arr = arr / norms

        if self.index is not None:
            try:
                self.index.add(norm_arr)
                self.id_map.extend(ids)
                return
            except Exception as e:
                logger.error(f"Error adding to FAISS: {e}")

        # Fallback in-memory tracking
        if not hasattr(self, "_fallback_vectors"):
            self._fallback_vectors = np.empty((0, self.dimension), dtype=np.float32)
        self._fallback_vectors = np.vstack([self._fallback_vectors, norm_arr])
        self.id_map.extend(ids)

    def search(self, query_vector: List[float], top_k: int = 8) -> List[Tuple[int, float]]:
        if self.count == 0:
            return []

        q_arr = np.array([query_vector], dtype=np.float32)
        q_norm = np.linalg.norm(q_arr)
        if q_norm > 0:
            q_arr = q_arr / q_norm

        top_k = min(top_k, self.count)

        if self.index is not None:
            try:
                scores, indices = self.index.search(q_arr, top_k)
                results: List[Tuple[int, float]] = []
                for score, idx in zip(scores[0], indices[0]):
                    if idx >= 0 and idx < len(self.id_map):
                        chunk_id = self.id_map[idx]
                        results.append((chunk_id, float(score)))
                return results
            except Exception as e:
                logger.error(f"FAISS search failed: {e}")

        # Fallback numpy cosine similarity
        if hasattr(self, "_fallback_vectors") and len(self._fallback_vectors) > 0:
            sims = np.dot(self._fallback_vectors, q_arr[0])
            top_indices = np.argsort(sims)[::-1][:top_k]
            return [(self.id_map[idx], float(sims[idx])) for idx in top_indices]

        return []

    def save(self, file_path: str) -> None:
        p = Path(file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        meta_path = p.with_suffix(".meta.json")

        if self.index is not None:
            try:
                import faiss
                faiss.write_index(self.index, str(p))
            except Exception as e:
                logger.error(f"Failed saving FAISS index: {e}")

        # Save ID map
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "id_map": self.id_map,
                "dimension": self.dimension,
                "count": self.count
            }, f)

    def load(self, file_path: str) -> bool:
        p = Path(file_path)
        meta_path = p.with_suffix(".meta.json")

        if not p.exists() or not meta_path.exists():
            return False

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                self.id_map = meta.get("id_map", [])
                self.dimension = meta.get("dimension", self.dimension)

            if self.index is not None:
                import faiss
                self.index = faiss.read_index(str(p))
                return True
        except Exception as e:
            logger.warning(f"Could not load FAISS index from {file_path}: {e}")
            self._init_index()
            return False
        return True

    def clear(self) -> None:
        self._init_index()
        if hasattr(self, "_fallback_vectors"):
            self._fallback_vectors = np.empty((0, self.dimension), dtype=np.float32)
