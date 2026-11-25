import time
import hashlib
from typing import Any, Optional, Dict
from threading import Lock

class TTLCache:
    """
    Thread-safe in-memory cache with Time-To-Live (TTL) expiration
    and Least Recently Used (LRU) eviction policy.
    Zero external dependencies required.
    """
    def __init__(self, maxsize: int = 1000, default_ttl: int = 3600):
        self.maxsize = maxsize
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self._hits = 0
        self._misses = 0

    def _generate_key(self, prefix: str, *args) -> str:
        """Create a consistent hash-based or normalized cache key."""
        raw = ":".join(str(a).strip().lower() for a in args)
        hashed = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        return f"{prefix}:{hashed}"

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache if present and not expired."""
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                self._misses += 1
                return None

            # Check if expired
            if time.time() > entry["expires_at"]:
                del self._cache[key]
                self._misses += 1
                return None

            # Refresh access timestamp (LRU)
            entry["last_accessed"] = time.time()
            self._hits += 1
            return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store value with expiration and evict oldest if maxsize reached."""
        ttl_seconds = ttl if ttl is not None else self.default_ttl
        expires_at = time.time() + ttl_seconds

        with self._lock:
            # If at capacity, evict oldest accessed entry
            if len(self._cache) >= self.maxsize and key not in self._cache:
                oldest_key = min(self._cache, key=lambda k: self._cache[k]["last_accessed"])
                del self._cache[oldest_key]

            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "last_accessed": time.time(),
                "created_at": time.time(),
            }

    def clear(self) -> None:
        """Empty all cached entries."""
        with self._lock:
            self._cache.clear()

    def stats(self) -> Dict[str, Any]:
        """Return cache health metrics and hit ratios."""
        with self._lock:
            # Purge expired keys for accurate count
            now = time.time()
            expired = [k for k, v in self._cache.items() if now > v["expires_at"]]
            for k in expired:
                del self._cache[k]

            total_lookups = self._hits + self._misses
            hit_ratio = round((self._hits / total_lookups) * 100, 1) if total_lookups > 0 else 0.0

            return {
                "size": len(self._cache),
                "maxsize": self.maxsize,
                "hits": self._hits,
                "misses": self._misses,
                "total_lookups": total_lookups,
                "hit_ratio_percent": hit_ratio,
            }

# Global cache instances
# Search cache: 2-hour TTL (7200s)
search_cache = TTLCache(maxsize=1000, default_ttl=7200)

# Geocode cache: 24-hour TTL (86400s) since coordinates are permanent
geocode_cache = TTLCache(maxsize=2000, default_ttl=86400)

def make_search_cache_key(query: str, lat: float, lng: float, radius: int, budget: int) -> str:
    """
    Rounds lat/lng to 3 decimal places (~100m radius precision)
    so nearby queries share the cached response seamlessly.
    """
    norm_lat = round(lat, 3)
    norm_lng = round(lng, 3)
    return search_cache._generate_key("search", query, norm_lat, norm_lng, radius, budget)

def make_geocode_cache_key(place: str) -> str:
    """Normalize place string for geocode cache."""
    return geocode_cache._generate_key("geocode", place)
