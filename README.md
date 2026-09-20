# 🧳 Budget Travel AI

A modern, responsive full-stack web application that helps people find budget-friendly places (restaurants, cafes, stays, sights, and hidden gems) near any location — using live GPS detection or a typed place name — powered by the Google Places API and interactive Leaflet maps.

**Live demo:** [budget-travel-ai-1wl373osl-ojaspaul123s-projects.vercel.app](https://ai-budget-travel.vercel.app/)

---

## 📌 What it does

Budget Travel AI lets a user:

* Detect their live location via browser GPS, or type a place name (e.g. "Patia Bhubaneswar", "Paris", "Agartala") and pick from suggested matches
* Search for any category of place (restaurants, cafes, stays, sights, street food, etc.)
* Filter results by budget tier — Free, Inexpensive (₹), Moderate (₹₹), Expensive (₹₹₹)
* Set a custom search radius in km (0.5 km to 25.0 km) with live map boundary visualization
* Explore results on an interactive Leaflet map (Satellite Topo) with custom glowing budget pins (🟢 Budget, 🟡 Moderate, 🔴 Origin)
* Click on any pin to view a rich popup card with star rating, review count, open/closed status, and direct 1-click Google Maps directions
* Filter places dynamically by Category and sort by Rating ⭐, Review Count 👥, or Lowest Budget 💰
* Save favorite spots to a Trip Bucket List with instant local persistence and directions

---

## 🎯 What This Project Does

Budget Travel AI solves a simple but common problem: figuring out what's actually affordable nearby without manually cross-checking prices across multiple apps. It combines live location detection (or a typed place search), Google's Places data, and an interactive map into one flow — search, filter by budget tier, sort by what matters, and save favorites — all without leaving a single page.

At its core, the app:
- Resolves a location (GPS or typed name) into coordinates
- Queries Google Places for nearby spots within a configurable radius
- Tags and filters results by budget tier and category
- Renders everything on a live Leaflet map with custom pins and rich popups
- Lets users curate a personal "Trip Bucket List" that persists locally

---

## 👥 Who This Is For

- **Budget travelers and backpackers** who want to filter out anything outside their price range before they even look at a place
- **Students and early-career travelers** exploring a new city on a tight budget
- **Locals** looking for a fast way to find cheap eats or hangout spots nearby, without scrolling a full-price map app
- **Digital nomads** planning short stays and wanting a quick affordability-first overview of an area
- **Developers/recruiters reviewing the project** — as a demonstration of full-stack API integration, third-party mapping, and serverless deployment

---

## 🌍 Real-World Impact

- Cuts the time and friction of comparing prices across scattered listings — budget filtering happens automatically using Google's price-level data
- Makes unfamiliar cities more approachable for cost-conscious travelers, especially in expensive tourist areas where prices vary wildly block to block
- The Trip Bucket List turns one-off searches into an actual trip-planning habit, rather than a single disposable lookup
- Demonstrates a reusable pattern — GPS/geocoding + a free-tier mapping library + a lightweight serverless backend — that applies to other location-based tools (accessibility mapping, local event finders, safety-check apps, etc.)

---

## 🐛 Issues Faced & How They Were Fixed

| Issue | Root Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: app` when running backend files directly | Ran scripts as `python app/services/file.py` instead of as part of the package | Ran them as modules instead: `python -m app.services.file` |
| Backend crashed with `AttributeError: no attribute 'router'` | A router file was left empty/incomplete after a partial edit | Replaced the entire file with complete code rather than patching line-by-line |
| `502 Bad Gateway` on search requests | `places_client.py` was missing its `import httpx` line | Restored the full import statement |
| Geocoding always returned no matches | Geocoding API wasn't enabled in Google Cloud, and the API key was restricted to Places API only | Enabled the Geocoding API and added it to the key's allowed API restrictions |
| `REQUEST_DENIED` on API calls | Google requires an active billing account linked to the project, even within free-tier limits | Verified billing was properly linked; documented that free-tier usage doesn't auto-charge, with budget alerts as a safeguard |
| Deployed frontend couldn't reach the backend | Frontend was still pointing at `127.0.0.1` (localhost-only), which doesn't exist once deployed | Deployed the backend separately (Render), then pointed the frontend at the public backend URL |
| Backend `/docs` returned "Not Found" after deployment | The hosting service's web service was never actually created — only the setup wizard had been reached | Walked through creating the service properly: connected the GitHub repo, set correct build/start commands, added environment variables, and redeployed |
| Exposed API keys during development | Keys were pasted into chat/logs while debugging | Regenerated every exposed key immediately and moved all key handling to environment variables / hosting dashboards only, never hardcoded or shared in plaintext |

---

## 🚀 Future Improvements

- **AI-powered recommendations**: Layer an LLM over the filtered results to suggest places in natural language ("best for a quick solo lunch," "good for groups on a budget") instead of a plain sorted list
- **Full itinerary planning**: Chain multiple searches into a day plan using a distance/travel-time API between stops
- **User accounts**: Sync the Trip Bucket List across devices instead of relying on local persistence only
- **Caching**: Cache repeated Places API responses to cut cost and improve load times
- **Offline-friendly fallback**: Graceful degradation if the Places API is rate-limited or briefly unreachable
- **Reviews & photos**: Surface a top review snippet or photo per place (mindful of the higher-cost API tier this requires)
- **Multi-language support**: Useful for international travelers exploring non-English-speaking regions
- **Route optimization**: Suggest an efficient order to visit multiple saved bucket-list spots

---

## 🗂️ Project Structure

```
budget-travel-ai/
├── app/
│   ├── main.py                 # FastAPI entry point & static file server
│   ├── config.py                # Loads GOOGLE_MAPS_API_KEY from environment
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response models
│   ├── routers/
│   │   ├── search.py            # POST /api/search endpoint
│   │   └── geocode.py           # GET /api/geocode endpoint
│   └── services/
│       ├── places_client.py     # Calls Google Places API (New)
│       ├── geocode_client.py    # Converts place name → lat/lng
│       └── ranker.py            # Filters & ranks places by budget tier
├── public/
│   ├── index.html               # Modern responsive SPA frontend
│   ├── style.css                # Premium dark glassmorphism design system
│   └── app.js                   # Map rendering, search, filters & trip bucket list
├── vercel.json                  # 1-Click Vercel deployment config
├── requirements.txt             # Lightweight Python dependencies
├── .env                         # Local API key (not committed)
└── .gitignore
```

---

## 🛠️ Tech Stack

* **Backend**: Python 3.10+, FastAPI, httpx, uvicorn
* **Frontend**: HTML5, Vanilla CSS3 (Custom Dark Theme), Vanilla JavaScript (ES6+)
* **Mapping**: Leaflet.js, Esri World Topo Map (zero watermarks / zero tile keys required)
* **APIs**: Google Places API (New), Google Geocoding API
* **Deployment**: Vercel (1-Click Serverless Python + Static Frontend), Render

---

## ⚙️ Running Locally

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

# 5. Run the web app (Backend + Frontend together)
python -m uvicorn app.main:app --reload
```

Open your browser at `http://127.0.0.1:8000` to use the application!
