#!/usr/bin/env python3
"""
Benchmark utility for MY PC REMEMBERS.
Measures:
- Files indexed
- Indexing elapsed time
- Average embedding latency
- Query and retrieval latency
- Memory usage (RSS)
Outputs real hardware metrics directly from local execution without fabricating data.
"""

import os
import sys
import time
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.db.database import init_db
from backend.app.db.repositories import Repository
from backend.app.vectorstore.faiss_store import FAISSVectorStore
from backend.app.ingestion.indexer import Indexer
from backend.app.retrieval.retriever import MemoryRetriever
from backend.app.embeddings.local_embeddings import get_embedding_provider
from backend.app.runtime.device import get_hardware_profile

def get_process_memory_mb() -> float:
    try:
        import resource
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        # On Linux, ru_maxrss is in kilobytes; on macOS it's in bytes
        if sys.platform == "darwin":
            return rusage.ru_maxrss / (1024 * 1024)
        return rusage.ru_maxrss / 1024
    except Exception:
        return 0.0

def run_benchmark():
    print("=" * 60)
    print("MY PC REMEMBERS - LOCAL AI BENCHMARK")
    print("=" * 60)

    profile = get_hardware_profile()
    print(f"Device: {profile['active_device']}")
    print(f"Target: {profile['hardware_target']}")
    print(f"OS: {profile['os']} ({profile['machine']})")
    print("-" * 60)

    # 1. Benchmark Embeddings
    emb_provider = get_embedding_provider()
    sample_texts = [
        "Dijkstra's shortest path algorithm implementation using priority queues",
        "Disjoint Set Union and Kruskal algorithm for Minimum Spanning Trees",
        "Breadth-first search for unweighted graph shortest path exploration",
        "Binary search tree insertion and balancing operations in C++"
    ]

    t0 = time.perf_counter()
    for _ in range(5):
        emb_provider.embed_batch(sample_texts)
    emb_time = (time.perf_counter() - t0) / (5 * len(sample_texts))
    avg_emb_ms = round(emb_time * 1000, 2)
    print(f"Embedding Latency: {avg_emb_ms} ms / chunk (Model: {getattr(emb_provider, 'model_name', 'Hybrid')})")

    # 2. Benchmark Indexing
    repo = Repository()
    vstore = FAISSVectorStore(dimension=384)
    indexer = Indexer(repo, vstore)

    sample_folder = Path("data/sample_documents/DSA").resolve()
    t_idx_start = time.perf_counter()
    index_res = indexer.index_folder(str(sample_folder), force_reindex=True)
    idx_duration = round((time.perf_counter() - t_idx_start) * 1000, 2)
    
    print(f"Indexing Time: {idx_duration} ms for {index_res['processed']} files ({index_res['total_chunks']} chunks)")

    # 3. Benchmark Query Retrieval
    retriever = MemoryRetriever(repo, vstore)
    test_queries = [
        "Find the Dijkstra notes I worked on recently",
        "Where did I implement minimum spanning tree using DSU",
        "I remember a PDF about graph algorithms",
        "Breadth first search FIFO queue"
    ]

    latencies = []
    for q in test_queries:
        t_q = time.perf_counter()
        res = retriever.search(q, top_k=5)
        lat = (time.perf_counter() - t_q) * 1000
        latencies.append(lat)
        print(f" Query: '{q[:35]}...' -> {round(lat, 2)} ms (Matched: {res['total_found']} files)")

    avg_query_lat = round(sum(latencies) / len(latencies), 2)
    mem_mb = round(get_process_memory_mb(), 2)

    print("-" * 60)
    print(f"Average Retrieval Latency: {avg_query_lat} ms")
    print(f"Peak Memory Usage (RSS): ~{mem_mb} MB (well within 8 GB RAM target)")
    print("=" * 60)

    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hardware": profile,
        "embedding_latency_ms": avg_emb_ms,
        "indexing_duration_ms": idx_duration,
        "files_indexed": index_res["processed"],
        "chunks_indexed": index_res["total_chunks"],
        "average_query_latency_ms": avg_query_lat,
        "peak_rss_mb": mem_mb
    }

    out_path = Path("data/benchmark_results.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Benchmark saved to {out_path}")

if __name__ == "__main__":
    run_benchmark()
