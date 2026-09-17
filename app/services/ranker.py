PRICE_SCORE = {
    "PRICE_LEVEL_FREE": 0,
    "PRICE_LEVEL_INEXPENSIVE": 1,
    "PRICE_LEVEL_MODERATE": 2,
    "PRICE_LEVEL_EXPENSIVE": 3,
    "PRICE_LEVEL_VERY_EXPENSIVE": 4,
}

PRICE_LABELS = {
    0: ("Free", "🆓"),
    1: ("Inexpensive", "$"),
    2: ("Moderate", "$$"),
    3: ("Expensive", "$$$"),
    4: ("Very Expensive", "$$$$"),
}

def format_place(p: dict) -> dict:
    """Formats raw Google Places API response into a clean dictionary."""
    price_level_raw = p.get("priceLevel", "")
    score = PRICE_SCORE.get(price_level_raw, 1)  # Default moderate-inexpensive if unlisted
    label, symbol = PRICE_LABELS.get(score, ("Moderate", "$$"))

    # Extract location
    loc = p.get("location", {})
    lat = loc.get("latitude")
    lng = loc.get("longitude")

    # Extract primary category
    primary_type_obj = p.get("primaryTypeDisplayName")
    if isinstance(primary_type_obj, dict):
        category = primary_type_obj.get("text")
    else:
        types = p.get("types", [])
        category = types[0].replace("_", " ").title() if types else "Place"

    # Extract opening hours status
    opening_hours = p.get("regularOpeningHours", {})
    open_now = opening_hours.get("openNow") if isinstance(opening_hours, dict) else None

    # Construct Google Maps URI fallback if missing
    gmaps_url = p.get("googleMapsUri")
    if not gmaps_url and lat is not None and lng is not None:
        gmaps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"

    return {
        "id": p.get("id"),
        "name": p.get("displayName", {}).get("text", "Unknown Place"),
        "address": p.get("formattedAddress", "No address available"),
        "rating": p.get("rating", 0.0),
        "user_rating_count": p.get("userRatingCount", 0),
        "price_level": label,
        "price_symbol": symbol,
        "price_score": score,
        "category": category,
        "open_now": open_now,
        "google_maps_url": gmaps_url,
        "website_url": p.get("websiteUri"),
        "location": {"latitude": lat, "longitude": lng} if lat and lng else None,
        "types": p.get("types", []),
    }

def score_by_budget(places: list, max_budget_level: int = 1):
    """
    Filters places to only those within the user's budget level,
    then formats and sorts by rating (highest first).
    """
    filtered = []
    for p in places:
        raw_price = p.get("priceLevel", "")
        # If price level is unknown, we allow it if budget is at least inexpensive (level >= 1)
        score = PRICE_SCORE.get(raw_price, 1 if max_budget_level >= 1 else 99)
        if score <= max_budget_level:
            filtered.append(format_place(p))

    return sorted(filtered, key=lambda p: (p.get("rating") or 0.0, p.get("user_rating_count") or 0), reverse=True)