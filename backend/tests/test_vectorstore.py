import tempfile
import os
from backend.app.vectorstore.faiss_store import FAISSVectorStore

def test_vectorstore_add_and_search():
    store = FAISSVectorStore(dimension=4)
    v1 = [1.0, 0.0, 0.0, 0.0]
    v2 = [0.0, 1.0, 0.0, 0.0]
    store.add([v1, v2], [101, 102])
    assert store.count == 2

    # Query closest to v1
    results = store.search([0.9, 0.1, 0.0, 0.0], top_k=2)
    assert len(results) == 2
    assert results[0][0] == 101 # chunk 101 should rank highest
    assert results[0][1] > results[1][1]

def test_vectorstore_persistence():
    with tempfile.TemporaryDirectory() as tmp_dir:
        index_file = os.path.join(tmp_dir, "test.index")
        store = FAISSVectorStore(dimension=4)
        store.add([[1.0, 0.0, 0.0, 0.0]], [42])
        store.save(index_file)

        # New instance loading
        store2 = FAISSVectorStore(dimension=4)
        loaded = store2.load(index_file)
        assert loaded is True
        assert store2.count == 1
        results = store2.search([1.0, 0.0, 0.0, 0.0], top_k=1)
        assert results[0][0] == 42
