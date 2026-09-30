from backend.app.ingestion.chunker import TextChunker

def test_chunker_small_text():
    chunker = TextChunker(target_tokens=100, overlap_tokens=20)
    text = "Short text under the target token limit."
    chunks = chunker.chunk_text(text)
    assert len(chunks) == 1
    assert chunks[0].content == text
    assert chunks[0].chunk_index == 0

def test_chunker_multi_paragraph():
    chunker = TextChunker(target_tokens=30, overlap_tokens=10)
    p1 = "Paragraph 1: Dijkstra algorithm finds shortest paths in a weighted graph using priority queues."
    p2 = "Paragraph 2: Kruskal algorithm finds minimum spanning trees using disjoint set union data structure."
    p3 = "Paragraph 3: Breadth-first search explores vertices level by level using a FIFO queue."
    full = f"{p1}\n\n{p2}\n\n{p3}"
    
    chunks = chunker.chunk_text(full)
    assert len(chunks) >= 2
    for idx, c in enumerate(chunks):
        assert c.chunk_index == idx
        assert len(c.content) > 0
