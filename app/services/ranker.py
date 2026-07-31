PRICE_SCORE = {
    "PRICE_LEVEL_FREE": 0,
    "PRICE_LEVEL_INEXPENSIVE": 1,
    "PRICE_LEVEL_MODERATE": 2,
    "PRICE_LEVEL_EXPENSIVE": 3,
    "PRICE_LEVEL_VERY_EXPENSIVE": 4,
}

def score_by_budget(places: list, max_budget_level: int = 1):
    """
    Filters places to only those within the user's budget level,
    then sorts by rating (highest first).
    """
    filtered = [
        p for p in places
        if PRICE_SCORE.get(p.get("priceLevel", ""), 99) <= max_budget_level
    ]
    return sorted(filtered, key=lambda p: p.get("rating", 0), reverse=True)


if __name__ == "__main__":
    sample = [
        {"displayName": {"text": "Cheap Cafe"}, "priceLevel": "PRICE_LEVEL_INEXPENSIVE", "rating": 4.2},
        {"displayName": {"text": "Fancy Bistro"}, "priceLevel": "PRICE_LEVEL_EXPENSIVE", "rating": 4.8},
        {"displayName": {"text": "Local Diner"}, "priceLevel": "PRICE_LEVEL_INEXPENSIVE", "rating": 4.5},
    ]
    ranked = score_by_budget(sample, max_budget_level=1)
    for p in ranked:
        print(p["displayName"]["text"], "-", p["rating"])