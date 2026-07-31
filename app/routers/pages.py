# pages.py
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "active": "home"})

@router.get("/search")
async def search_page(request: Request):
    return templates.TemplateResponse("search.html", {"request": request, "active": "search"})

@router.get("/about")
async def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "active": "about"})
