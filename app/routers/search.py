from fastapi import APIRouter, HTTPException
from app.models.schemas import SearchRequest
from app.services.places_client import search_places
from app.services.ranker import score_by_budget
from app.services.ai_recommender import enrich_with_ai
from app.services.cache import search_cache, make_search_cache_key

router = APIRouter()

@router.post("/search")
async def search(request: SearchRequest):
    # 1. Check in-memory TTL cache first
    cache_key = make_search_cache_key(
        query=request.query,
        lat=request.lat,
        lng=request.lng,
        radius=request.radius,
        budget=request.max_budget_level,
    )

    cached_response = search_cache.get(cache_key)
    if cached_response is not None:
        return {
            **cached_response,
            "cached": True,
        }

    # 2. Cache miss: Fetch from Google Places API
    try:
        places = await search_places(
            query=request.query,
            lat=request.lat,
            lng=request.lng,
            radius=request.radius,
        )
    except Exception as e:
        print("PLACES API ERROR:", repr(e))
        raise HTTPException(status_code=502, detail=f"Places API error: {str(e)}")

    ranked = score_by_budget(places, request.max_budget_level)

    # 3. Layer AI natural language recommendations over the budget-filtered spots
    ai_enrichment = await enrich_with_ai(
        query=request.query,
        places=ranked,
        budget_level=request.max_budget_level,
    )

    response_data = {
        "count": len(ai_enrichment["enriched_places"]),
        "ai_summary": ai_enrichment["ai_summary"],
        "results": ai_enrichment["enriched_places"],
    }

    # 4. Save to cache
    search_cache.set(cache_key, response_data)

    return {
        **response_data,
        "cached": False,
    }
