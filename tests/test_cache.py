import time
import pytest
from app.services.cache import TTLCache, make_search_cache_key, make_geocode_cache_key

def test_cache_set_and_get():
    cache = TTLCache(maxsize=10, default_ttl=60)
    cache.set("key1", {"data": "test_value"})
    
    result = cache.get("key1")
    assert result == {"data": "test_value"}
    
    stats = cache.stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 0

def test_cache_miss():
    cache = TTLCache(maxsize=10, default_ttl=60)
    result = cache.get("nonexistent_key")
    assert result is None
    
    stats = cache.stats()
    assert stats["hits"] == 0
    assert stats["misses"] == 1

def test_cache_ttl_expiration():
    # Cache with 1-second TTL
    cache = TTLCache(maxsize=10, default_ttl=1)
    cache.set("short_key", "temporary", ttl=1)
    
    assert cache.get("short_key") == "temporary"
    
    # Wait for TTL to expire
    time.sleep(1.1)
    assert cache.get("short_key") is None

def test_cache_lru_eviction():
    # Max size = 2
    cache = TTLCache(maxsize=2, default_ttl=60)
    cache.set("a", 1)
    time.sleep(0.01)
    cache.set("b", 2)
    time.sleep(0.01)
    
    # Access 'a' so 'b' becomes the least recently used
    _ = cache.get("a")
    time.sleep(0.01)
    
    # Adding 'c' should evict 'b'
    cache.set("c", 3)
    
    assert cache.get("a") == 1
    assert cache.get("b") is None  # evicted
    assert cache.get("c") == 3

def test_search_cache_key_normalization():
    # Minor lat/lng variations within 0.0004 (~40m) should produce identical cache keys
    key1 = make_search_cache_key("cafe", 20.3601, 85.8242, 5000, 1)
    key2 = make_search_cache_key("cafe", 20.3604, 85.8244, 5000, 1)
    assert key1 == key2

    # Different query or budget should yield different keys
    key3 = make_search_cache_key("restaurant", 20.3601, 85.8242, 5000, 1)
    key4 = make_search_cache_key("cafe", 20.3601, 85.8242, 5000, 2)
    assert key1 != key3
    assert key1 != key4

def test_geocode_cache_key():
    key1 = make_geocode_cache_key("Patia, Bhubaneswar")
    key2 = make_geocode_cache_key("  patia, bhubaneswar  ")
    assert key1 == key2

def test_cache_clear():
    cache = TTLCache(maxsize=5, default_ttl=60)
    cache.set("k1", 100)
    cache.set("k2", 200)
    assert cache.stats()["size"] == 2
    
    cache.clear()
    assert cache.stats()["size"] == 0
    assert cache.get("k1") is None
