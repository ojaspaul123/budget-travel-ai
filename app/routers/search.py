from fastapi import APIRouter, HTTPException
from app.models.schemas import SearchRequest
from app.services.places_client import search_places
from app.services.ranker import score_by_budget
from app.services.ai_recommender import enrich_with_ai

router = APIRouter()

@router.post("/search")
async def search(request: SearchRequest):
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

    # Layer AI natural language recommendations over the budget-filtered spots
    ai_enrichment = await enrich_with_ai(
        query=request.query,
        places=ranked,
        budget_level=request.max_budget_level,
    )

    return {
        "count": len(ai_enrichment["enriched_places"]),
        "ai_summary": ai_enrichment["ai_summary"],
        "results": ai_enrichment["enriched_places"],
    }
    
    
    