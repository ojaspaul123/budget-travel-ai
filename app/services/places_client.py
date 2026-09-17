# places_client.py
import httpx
from app.config import settings

FIELD_MASK = (
    "places.id,"
    "places.displayName,"
    "places.formattedAddress,"
    "places.location,"
    "places.priceLevel,"
    "places.rating,"
    "places.userRatingCount,"
    "places.googleMapsUri,"
    "places.websiteUri,"
    "places.regularOpeningHours,"
    "places.primaryTypeDisplayName,"
    "places.types"
)

async def search_places(query: str, lat: float, lng: float, radius: int = 5000):
    payload = {
        "textQuery": query,
        "locationBias": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": radius,
            }
        },
        "maxResultCount": 20,
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            "https://places.googleapis.com/v1/places:searchText",
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": settings.GOOGLE_MAPS_API_KEY,
                "X-Goog-FieldMask": FIELD_MASK,
            },
            json=payload,
        )
        resp.raise_for_status()
        return resp.json().get("places", [])
