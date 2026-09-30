from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "indexed_files" in data
    assert data["local_mode"] is True

def test_api_index_status():
    res = client.get("/api/index/status")
    assert res.status_code == 200
    data = res.json()
    assert "total_files" in data
    assert "indexed_folders" in data

def test_api_settings():
    res = client.get("/api/settings")
    assert res.status_code == 200
    data = res.json()
    assert "privacy_notice" in data
    assert "embedding_provider" in data

def test_api_search():
    res = client.post("/api/search", json={"query": "Dijkstra algorithm", "top_k": 5})
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == "Dijkstra algorithm"
    assert "results" in data
    assert "time_taken_ms" in data
