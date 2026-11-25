import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import search, geocode
from app.services.cache import search_cache, geocode_cache

app = FastAPI(
    title="Budget Travel AI",
    description="Find budget-friendly places using Google Places API and AI recommendations",
    version="1.1.0",
)

# Allow CORS for Vercel and local frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(geocode.router, prefix="/api", tags=["geocode"])

# Health check endpoint
@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "message": "Budget Travel AI API is running",
        "cache": {
            "search_entries": search_cache.stats()["size"],
            "geocode_entries": geocode_cache.stats()["size"],
        },
    }

# Cache statistics and monitoring endpoint
@app.get("/api/cache/stats")
def cache_stats():
    return {
        "search_cache": search_cache.stats(),
        "geocode_cache": geocode_cache.stats(),
    }

# Cache invalidation endpoint
@app.post("/api/cache/clear")
def clear_cache():
    search_cache.clear()
    geocode_cache.clear()
    return {"status": "ok", "message": "All server-side caches cleared successfully"}

# Serve Frontend static assets from public/ directory
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(static_dir, "index.html"))
