import httpx

async def geocode_place(place_name: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": place_name, "format": "json", "limit": 5},
            headers={"User-Agent": "BudgetTravelAI/1.0"},  # Nominatim requires a User-Agent
            timeout=8.0,
        )
        resp.raise_for_status()
        results = resp.json()

        return [
            {
                "formatted_address": r["display_name"],
                "lat": float(r["lat"]),
                "lng": float(r["lon"]),
            }
            for r in results
        ]