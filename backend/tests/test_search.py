from backend.app.retrieval.ranker import SearchRanker

def test_search_ranker_aggregation():
    matches = [
        ({"file_id": 1, "filename": "graph_notes.pdf", "path": "/docs/graph_notes.pdf", "extension": ".pdf", "content": "Dijkstra priority queue shortest path"}, 0.85),
        ({"file_id": 1, "filename": "graph_notes.pdf", "path": "/docs/graph_notes.pdf", "extension": ".pdf", "content": "Graph relaxation algorithm"}, 0.70),
        ({"file_id": 2, "filename": "kruskal.cpp", "path": "/docs/kruskal.cpp", "extension": ".cpp", "content": "Kruskal MST using DSU"}, 0.60),
    ]
    ranked = SearchRanker.aggregate_and_rank(matches, "Find Dijkstra notes", is_time_sensitive=False)
    assert len(ranked) == 2
    assert ranked[0]["file_id"] == 1
    assert ranked[0]["filename"] == "graph_notes.pdf"
    assert ranked[0]["score"] > ranked[1]["score"]
    assert ranked[0]["chunks_matched"] == 2

def test_search_ranker_format_boost():
    matches = [
        ({"file_id": 1, "filename": "notes.pdf", "path": "/notes.pdf", "extension": ".pdf", "content": "graph search"}, 0.60),
        ({"file_id": 2, "filename": "notes.cpp", "path": "/notes.cpp", "extension": ".cpp", "content": "graph search"}, 0.60),
    ]
    ranked_pdf = SearchRanker.aggregate_and_rank(matches, "I want a PDF with graph", is_time_sensitive=False)
    assert ranked_pdf[0]["filename"] == "notes.pdf"

    ranked_code = SearchRanker.aggregate_and_rank(matches, "Show me code for graph", is_time_sensitive=False)
    assert ranked_code[0]["filename"] == "notes.cpp"
