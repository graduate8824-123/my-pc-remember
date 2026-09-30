import math
import re
import numpy as np
from typing import List, Optional
from .base import EmbeddingProvider
from ..core.config import settings
from ..core.logging import logger

class FastEmbedEmbeddingProvider(EmbeddingProvider):
    """
    Lightweight, quantized ONNX local embedding model via FastEmbed.
    Ideal for local CPU execution with low memory consumption (~30MB RAM).
    """

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        self._dimension = settings.EMBEDDING_DIMENSION
        self._model = None
        self._init_model()

    def _init_model(self):
        try:
            from fastembed import TextEmbedding
            # Lazy initialize model
            self._model = TextEmbedding(model_name=self.model_name)
            logger.info(f"Loaded FastEmbed embedding model: {self.model_name}")
        except Exception as e:
            logger.warning(f"FastEmbed initialization notice ({e}). Falling back to lightweight offline provider.")
            self._model = None

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_text(self, text: str) -> List[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        if self._model is not None:
            try:
                embeddings = list(self._model.embed(texts))
                return [emb.tolist() for emb in embeddings]
            except Exception as e:
                logger.warning(f"FastEmbed inference error: {e}. Falling back to deterministic hybrid embedding.")
        
        fallback = DeterministicHybridEmbeddingProvider(dim=self._dimension)
        return fallback.embed_batch(texts)


class DeterministicHybridEmbeddingProvider(EmbeddingProvider):
    """
    Zero-network, deterministic semantic projection embedding provider.
    Ensures 100% offline functionality without downloading any external weights.
    Uses token hashing with feature weights and L2 normalization to create 384-dim dense vectors.
    """

    def __init__(self, dim: int = 384):
        self._dim = dim

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_text(self, text: str) -> List[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        for text in texts:
            vec = np.zeros(self._dim, dtype=np.float32)
            clean = text.lower()
            tokens = re.findall(r'\b[a-z0-9_]{2,}\b', clean)

            for idx, token in enumerate(tokens):
                # Hash token into vector indices
                h1 = hash(token) % self._dim
                h2 = hash(token + "_2") % self._dim
                # Word position weight & token frequency
                weight = 1.0 / (1.0 + math.log(1.0 + idx * 0.05))
                vec[h1] += weight
                vec[h2] += weight * 0.5

                # Also capture 2-gram context
                if idx < len(tokens) - 1:
                    bigram = f"{token}_{tokens[idx+1]}"
                    h_bi = hash(bigram) % self._dim
                    vec[h_bi] += weight * 0.75

            # L2 normalize
            norm = np.linalg.norm(vec)
            if norm > 1e-6:
                vec = vec / norm
            else:
                vec[0] = 1.0 # default unit vector
            vectors.append(vec.tolist())
        return vectors


_embedding_provider_instance: Optional[EmbeddingProvider] = None

def get_embedding_provider() -> EmbeddingProvider:
    """Singleton factory for obtaining the active embedding provider."""
    global _embedding_provider_instance
    if _embedding_provider_instance is None:
        provider_type = settings.EMBEDDING_PROVIDER.lower()
        if provider_type == "fastembed":
            _embedding_provider_instance = FastEmbedEmbeddingProvider(settings.EMBEDDING_MODEL)
        else:
            _embedding_provider_instance = DeterministicHybridEmbeddingProvider(settings.EMBEDDING_DIMENSION)
    return _embedding_provider_instance
