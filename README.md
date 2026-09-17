# 🧳 Budget Travel AI

A modern, responsive full-stack web application that helps people find budget-friendly places (restaurants, cafes, stays, sights, and hidden gems) near any location — using live GPS detection or a typed place name — powered by the Google Places API and interactive Leaflet maps.

---

## 📌 What it does

Budget Travel AI lets a user:
- Detect their **live location** via browser GPS, or **type a place name** (e.g. "Patia Bhubaneswar", "Paris", "Agartala") and pick from suggested matches
- Search for any category of place (restaurants, cafes, stays, sights, street food, etc.)
- Filter results by **budget tier** — Free, Inexpensive ($), Moderate ($$), Expensive ($$$)
- Set a custom **search radius in km** (0.5 km to 25.0 km) with live map boundary visualization
- Explore results on an interactive **Leaflet map (Satellite Topo)** with custom glowing budget pins (🟢 Budget, 🟡 Moderate, 🔴 Origin)
- Click on any pin to view a **rich popup card** with star rating, review count, open/closed status, and direct 1-click **Google Maps directions**
- Filter places dynamically by **Category** and sort by **Rating ⭐, Review Count 👥, or Lowest Budget 💰**
- Save favorite spots to a **Trip Bucket List** with instant local persistence and directions

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

- **Backend**: Python 3.10+, FastAPI, httpx, uvicorn
- **Frontend**: HTML5, Vanilla CSS3 (Custom Dark Theme), Vanilla JavaScript (ES6+)
- **Mapping**: Leaflet.js, Esri World Topo Map (zero watermarks / zero tile keys required)
- **APIs**: Google Places API (New), Google Geocoding API
- **Deployment**: Vercel (1-Click Serverless Python + Static Frontend), Render

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

Open your browser at **`http://127.0.0.1:8000`** to use the application!

---

## 🚀 1-Click Deployment to Vercel

1. Push this repository to GitHub:
   ```bash
   git add .
   git commit -m "Deploy web app to Vercel"
   git push origin <your-branch>
   ```

2. Go to **[vercel.com/new](https://vercel.com/new)** and import your repository.

3. Under **Environment Variables**, add:
   - `GOOGLE_MAPS_API_KEY` = `your_google_maps_api_key_here`

4. Click **Deploy**. Vercel will automatically build the static frontend from `public/` and mount the serverless Python API from `app/main.py`.
