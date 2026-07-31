# places_client.py
import httpx
from app.config import settings

FIELD_MASK = "places.id,places.displayName,places.formattedAddress,places.location,places.priceLevel,places.rating,places.types"

PRICE_LEVELS = [
    "PRICE_LEVEL_FREE",
    "PRICE_LEVEL_INEXPENSIVE",
    "PRICE_LEVEL_MODERATE",
    "PRICE_LEVEL_EXPENSIVE",
    "PRICE_LEVEL_VERY_EXPENSIVE",
]

async def search_places(query: str, lat: float, lng: float, radius: int = 5000):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://places.googleapis.com/v1/places:searchText",
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": settings.GOOGLE_MAPS_API_KEY,
                "X-Goog-FieldMask": FIELD_MASK,
            },
            json={
                "textQuery": query,
                "locationBias": {
                    "circle": {
                        "center": {"latitude": lat, "longitude": lng},
                        "radius": radius,
                    }
                },
                "priceLevels": ["PRICE_LEVEL_INEXPENSIVE", "PRICE_LEVEL_MODERATE"],
                "maxResultCount": 20,
            },
        )
        resp.raise_for_status()
        return resp.json().get("places", [])