from fastapi import FastAPI
from app.routers import search, geocode

app = FastAPI(
    title="Budget Travel AI",
    description="Find budget-friendly places using Google Places API",
    version="1.0.0",
)

app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(geocode.router, prefix="/api", tags=["geocode"])

@app.get("/")
def root():
    return {"message": "Budget Travel AI is running"}