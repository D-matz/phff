from app import app
from pages._base_nav import base_nav

@app.get("/settings", name="settings")
async def root():
    return base_nav("<h1>settings</h1>")