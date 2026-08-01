# 🧳 AI Budget Travel

A full-stack web app that helps people find budget-friendly places (restaurants, hotels, cafes, and more) near any location — using live GPS detection or a typed place name — powered by the Google Places API.

**Live demo:** [budget-travel-ai-l4rdys7qqqgkqmgatsjrcm.streamlit.app](https://budget-travel-ai-l4rdys7qqqgkqmgatsjrcm.streamlit.app/)

---

## 📌 What it does

Budget Travel AI lets a user:
- Detect their **live location** via browser GPS, or **type a place name** (e.g. "Kolkata") and pick from suggested matches
- Search for any category of place (restaurants, hotels, cafes, etc.)
- Filter results by **budget level** — Free, Inexpensive, Moderate, Expensive, Very Expensive
- Set a custom **search radius**
- View results on an interactive **map**, ranked by rating within the chosen budget
- See each place's name, address, rating, and price level in a clean card layout

Under the hood, it combines:
- A **FastAPI** backend that calls the Google Places API (New) and applies budget-based filtering/ranking
- A **Streamlit** frontend for the interactive UI
- Geocoding (place name → coordinates) to support both GPS and manual location search

---

## 🗂️ Project Structure

```
budget-travel-ai/
├── app/
│   ├── main.py                 # FastAPI entry point, registers routers
│   ├── config.py                # Loads GOOGLE_MAPS_API_KEY from environment
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response models
│   ├── routers/
│   │   ├── search.py            # POST /api/search endpoint
│   │   └── geocode.py           # GET /api/geocode endpoint
│   └── services/
│       ├── places_client.py     # Calls Google Places API (New)
│       ├── geocode_client.py    # Converts place name → lat/lng
│       └── ranker.py            # Filters & ranks places by budget level
├── streamlit_app.py             # Streamlit frontend (UI, forms, map, results)
├── requirements.txt             # Python dependencies
├── .env                         # Local API key (not committed)
└── .gitignore
```

**Architecture flow:**
```
User (browser) → Streamlit frontend → FastAPI backend → Google Places / Geocoding API
                                    ↓
                          Budget filter + ranking
                                    ↓
                     Results returned to Streamlit → Map + cards
```

---

## 👥 Who uses it

- **Budget travelers and students** looking for affordable food, stays, or activities in an unfamiliar area
- **Digital nomads / backpackers** who want to filter by price level before committing to a place
- **Local explorers** who just want a quick way to find cheap spots nearby without scrolling through a full-price map app
- **Recruiters/portfolio reviewers** — as a demonstration of full-stack API integration, external API usage, and deployment skills

---

## 🌍 Real-world impact

- Removes the friction of manually cross-checking prices across multiple listings — budget filtering happens automatically via Google's `priceLevel` data
- Makes travel planning more accessible for people on tight budgets, especially useful in high-cost tourist areas
- Demonstrates a practical, low-cost way to combine a free-tier mapping API with a lightweight full-stack architecture — a pattern reusable for many other location-based tools (event finders, accessibility mapping, etc.)

---

## 🐛 Issues faced & how they were fixed

| Issue | Root Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: app` when running files directly | Ran scripts as `python app/services/file.py` instead of as a package | Used `python -m app.services.file` to run within the package structure |
| Backend crashed with `AttributeError: no attribute 'router'` | `geocode.py` was empty/incomplete after a partial edit | Replaced the entire file with the complete, correct code instead of patching |
| `502 Bad Gateway` on search | `places_client.py` was missing the `import httpx` line | Restored the full import statement |
| Geocoding always returned `"matches": []` | 1) Geocoding API not enabled in Google Cloud, 2) API key restricted to Places API only | Enabled Geocoding API and added it to the key's allowed API restrictions |
| `REQUEST_DENIED` — billing required | Google requires an active billing account for Places/Geocoding APIs, even within free-tier limits | Explained the (no-charge-by-default) billing requirement; offered a free alternative (OpenStreetMap Nominatim) as a fallback with no API key needed |
| Deployed Streamlit app crashed with `ModuleNotFoundError: streamlit_geolocation` | `requirements.txt` was frozen before the package was installed, so it never got pushed | Re-ran `pip freeze > requirements.txt` and pushed the update |
| Deployed frontend couldn't reach the backend (`404`/connection errors) | `streamlit_app.py` was still pointing to `127.0.0.1:8000`, which only exists on localhost | Deployed the FastAPI backend separately on **Render** and updated the frontend to call the public Render URL |
| Backend `/docs` returned "Not Found" entirely | Render Web Service was never actually created — only the setup wizard had been reached | Walked through creating the service properly: connected the GitHub repo, set build/start commands, added the environment variable, and deployed |
| API key exposure risk | API keys were shared in plaintext during development/debugging | Regenerated the exposed keys and moved all key handling to environment variables / hosting provider dashboards only |

---

## 🚀 Future improvements

- **AI-powered recommendations**: Layer an LLM on top of the filtered results to generate natural-language suggestions ("best for a quick solo lunch," "good for groups on a tight budget") instead of just a sorted list
- **Full itinerary planning**: Chain multiple searches into a day plan using the Distance Matrix API for travel time between stops
- **User accounts & saved searches**: Let users save favorite places or past searches
- **Caching**: Cache repeated Places API calls to reduce cost and improve response time
- **Better error handling & offline fallback**: Graceful degradation if the Google API is rate-limited or briefly unavailable
- **Mobile-first redesign**: Optimize the Streamlit layout further for phone screens, since budget travelers often search on the go
- **Reviews/photos**: Pull in a place's top review snippet or photo (mindful of the higher-cost Atmosphere-tier API fields)
- **Multi-language support**: Useful for international budget travelers

---

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, httpx
- **Frontend**: Streamlit, streamlit-geolocation
- **APIs**: Google Places API (New), Google Geocoding API
- **Hosting**: Render (backend), Streamlit Community Cloud (frontend)

---

## ⚙️ Running locally

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd budget-travel-ai

# 2. Set up virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
echo GOOGLE_MAPS_API_KEY=your_key_here > .env

# 5. Run the backend
uvicorn app.main:app --reload

# 6. In a second terminal, run the frontend
streamlit run streamlit_app.py
```
