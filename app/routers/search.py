from fastapi import APIRouter, HTTPException
from app.models.schemas import SearchRequest
from app.services.places_client import search_places
from app.services.ranker import score_by_budget

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
        print("PLACES API ERROR:", repr(e))  # ← add this line
        raise HTTPException(status_code=502, detail=f"Places API error: {str(e)}")

    ranked = score_by_budget(places, request.max_budget_level)

    return {
        "count": len(ranked),
        "results": ranked,
    }
    
    
    