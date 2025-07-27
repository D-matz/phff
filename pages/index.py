from app import app
from fastapi import Request
from pages._base_nav import base_nav

@app.get("/")
async def index(request: Request):
    return base_nav(request, "<h1>Welcome to Potato EMR</h1>")