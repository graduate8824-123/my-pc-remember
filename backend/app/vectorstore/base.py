from abc import ABC, abstractmethod
from typing import List, Tuple

class VectorStore(ABC):
    """
    Abstract interface for local vector store.
    Decoupled from specific backend implementations (FAISS, NumPy, NPU-accelerated).
    """

    @abstractmethod
    def add(self, vectors: List[List[float]], ids: List[int]) -> None:
        """Adds normalized vectors associated with chunk IDs."""
        pass

    @abstractmethod
    def search(self, query_vector: List[float], top_k: int = 8) -> List[Tuple[int, float]]:
        """Searches for top_k nearest neighbors. Returns list of (chunk_id, similarity_score)."""
        pass

    @abstractmethod
    def save(self, file_path: str) -> None:
        """Persists the vector index to local storage."""
        pass

    @abstractmethod
    def load(self, file_path: str) -> bool:
        """Loads the vector index from local storage. Returns True if successful."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clears all vectors from the index."""
        pass

    @property
    @abstractmethod
    def count(self) -> int:
        """Total vectors indexed."""
        pass
