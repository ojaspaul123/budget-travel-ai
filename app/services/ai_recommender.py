# app/services/ai_recommender.py
import json
import httpx
from app.config import settings

AI_VIBE_CATEGORIES = [
    "Quick Solo Lunch",
    "Group Hangout on Budget",
    "Quiet Study & Work Spot",
    "Hidden Local Gem",
    "Best Value Dining",
    "Late-Night Budget Bite",
]

def _heuristic_recommendations(query: str, places: list, budget_level: int) -> dict:
    """
    Intelligent zero-config fallback engine that assigns natural language
    recommendation badges and context based on category, rating, reviews, and price.
    """
    if not places:
        return {
            "ai_summary": "No places to evaluate for this search criteria.",
            "enriched_places": [],
        }

    enriched = []
    for idx, p in enumerate(places):
        category = (p.get("category") or "").lower()
        rating = p.get("rating") or 0.0
        review_count = p.get("user_rating_count") or 0
        price_score = p.get("price_score", 1)
        name = p.get("name", "This place")

        # Contextual logic for badges
        if "cafe" in category or "coffee" in category or "bakery" in category:
            badge = "Quiet Study & Work Spot"
            reason = f"Cozy cafe vibe with affordable beverages, ideal for laptop work or a relaxing solo break."
        elif "fast food" in category or "snack" in category or "street food" in category or "sandwich" in category:
            badge = "Quick Solo Lunch"
            reason = f"Fast counter service and pocket-friendly bites, perfect for solo dining under time constraints."
        elif review_count > 500 and rating >= 4.3:
            badge = "Best Value Dining"
            reason = f"Over {review_count:,} reviews with a {rating}★ score — a proven local favorite delivering maximum bang for your buck."
        elif review_count < 150 and rating >= 4.4:
            badge = "Hidden Local Gem"
            reason = f"High {rating}★ customer satisfaction without overwhelming tourist crowds — an authentic, affordable find."
        elif price_score == 0:
            badge = "Free Admission & Sights"
            reason = f"Zero cost entry or activities, perfect for stretching your travel budget further."
        elif idx % 2 == 0:
            badge = "Group Hangout on Budget"
            reason = f"Spacious seating and shareable meal portions that keep per-person spend remarkably low."
        else:
            badge = "Quick Solo Lunch"
            reason = f"Dependable, budget-friendly menu with quick meal options for cost-conscious travelers."

        p_copy = dict(p)
        p_copy["ai_badge"] = badge
        p_copy["ai_reason"] = reason
        enriched.append(p_copy)

    top_place = enriched[0].get("name", "top spots")
    budget_label = "budget-friendly" if budget_level <= 1 else "moderate-value"
    
    summary = (
        f"Found {len(enriched)} {budget_label} spots for '{query}'. "
        f"Top-rated {top_place} leads with great affordability, with curated options "
        f"tailored for quick solo bites, quiet working corners, and group outings."
    )

    return {
        "ai_summary": summary,
        "enriched_places": enriched,
    }


async def enrich_with_ai(query: str, places: list, budget_level: int = 1) -> dict:
    """
    Enriches places with LLM (Gemini Flash) natural language recommendations.
    Gracefully falls back to heuristic engine if API key is absent or call fails.
    """
    if not places:
        return {"ai_summary": "", "enriched_places": []}

    # Only process up to top 15 places to keep response fast and token-efficient
    top_candidates = places[:15]
    other_places = places[15:]

    if not settings.GEMINI_API_KEY:
        res = _heuristic_recommendations(query, top_candidates, budget_level)
        return {
            "ai_summary": res["ai_summary"],
            "enriched_places": res["enriched_places"] + other_places,
        }

    # Prepare prompt for Gemini Flash
    candidates_data = [
        {
            "id": p.get("id"),
            "name": p.get("name"),
            "category": p.get("category"),
            "rating": p.get("rating"),
            "reviews": p.get("user_rating_count"),
            "price_level": p.get("price_level"),
            "address": p.get("address"),
        }
        for p in top_candidates
    ]

    prompt = f"""You are Budget Travel AI's concierge.
A budget traveler searched for "{query}".
Analyze these places and return a JSON object with:
1. "summary": A 2-sentence conversational natural language overview comparing the top spots and advising what's best for solo lunch vs groups vs study/chill.
2. "insights": A list of items, each having:
   - "id": The place id
   - "ai_badge": Choose the most fitting short tag from: ["Quick Solo Lunch", "Group Hangout on Budget", "Quiet Study & Work Spot", "Hidden Local Gem", "Best Value Dining", "Pocket-Friendly Treats"]
   - "ai_reason": Exactly 1 punchy sentence explaining why a budget traveler will love it.

Places to analyze:
{json.dumps(candidates_data)}

Return ONLY valid JSON with keys "summary" and "insights". Do not include Markdown fences."""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1000}
        }

        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

            raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            # Clean possible markdown wrap
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            parsed = json.loads(raw_text.strip())
            summary = parsed.get("summary", "")
            insights_map = {item.get("id"): item for item in parsed.get("insights", [])}

            enriched = []
            for p in top_candidates:
                p_copy = dict(p)
                p_id = p.get("id")
                ins = insights_map.get(p_id, {})
                p_copy["ai_badge"] = ins.get("ai_badge") or "Best Value Dining"
                p_copy["ai_reason"] = ins.get("ai_reason") or "Affordable option matching your budget criteria."
                enriched.append(p_copy)

            return {
                "ai_summary": summary,
                "enriched_places": enriched + other_places,
            }

    except Exception as e:
        print(f"Gemini API unavailable ({e}), using heuristic AI recommender.")
        res = _heuristic_recommendations(query, top_candidates, budget_level)
        return {
            "ai_summary": res["ai_summary"],
            "enriched_places": res["enriched_places"] + other_places,
        }
