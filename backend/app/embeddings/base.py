from abc import ABC, abstractmethod
from typing import List

class EmbeddingProvider(ABC):
    """
    Abstract hardware-agnostic base class for embedding models.
    Can be backed by CPU, Apple Silicon, or Snapdragon NPU backends.
    """

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Embed a single string."""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of strings."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Vector dimension."""
        pass
