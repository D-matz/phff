from app import app
from pages._base_nav import base_nav
from fastapi import Request

@app.get("/lists", name="patient lists")
async def root(request: Request):
    return base_nav(request, "<h1>Patient Lists</h1>")