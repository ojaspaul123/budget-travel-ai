from fastapi import APIRouter
from app.services.geocode_client import geocode_place
from app.services.cache import geocode_cache, make_geocode_cache_key

router = APIRouter()

@router.get("/geocode")
async def geocode(place: str):
    cache_key = make_geocode_cache_key(place)
    cached_matches = geocode_cache.get(cache_key)
    if cached_matches is not None:
        return {
            "matches": cached_matches,
            "cached": True,
        }

    matches = await geocode_place(place)
    if matches:
        geocode_cache.set(cache_key, matches)

    return {
        "matches": matches,
        "cached": False,
    }
