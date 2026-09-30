from backend.app.embeddings.local_embeddings import (
    DeterministicHybridEmbeddingProvider,
    get_embedding_provider
)

def test_deterministic_embedding_provider():
    provider = DeterministicHybridEmbeddingProvider(dim=384)
    assert provider.dimension == 384

    v1 = provider.embed_text("Dijkstra priority queue shortest path")
    assert len(v1) == 384

    v2 = provider.embed_text("Dijkstra priority queue shortest path")
    # Must be deterministic
    assert v1 == v2

    # Different text should produce different vector
    v3 = provider.embed_text("Completely unrelated culinary recipe with butter and flour")
    assert v1 != v3

def test_batch_embedding():
    provider = DeterministicHybridEmbeddingProvider(dim=384)
    texts = ["graph traversal", "shortest paths", "binary search"]
    batch = provider.embed_batch(texts)
    assert len(batch) == 3
    assert all(len(vec) == 384 for vec in batch)
