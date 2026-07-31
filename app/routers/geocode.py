from fastapi import APIRouter
from app.services.geocode_client import geocode_place

router = APIRouter()

@router.get("/geocode")
async def geocode(place: str):
    matches = await geocode_place(place)
    return {"matches": matches}