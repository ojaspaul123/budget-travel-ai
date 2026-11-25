from fastapi.testclient import TestClient
from app.main import app
from app.services.cache import search_cache, geocode_cache

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "cache" in data

def test_cache_stats_endpoint():
    response = client.get("/api/cache/stats")
    assert response.status_code == 200
    data = response.json()
    assert "search_cache" in data
    assert "geocode_cache" in data
    assert data["search_cache"]["maxsize"] == 1000

def test_cache_clear_endpoint():
    search_cache.set("test_key", {"dummy": 123})
    assert search_cache.get("test_key") is not None
    
    response = client.post("/api/cache/clear")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
    assert search_cache.get("test_key") is None
