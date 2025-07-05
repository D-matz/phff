from app import app
from pages._base_nav import base_nav

@app.get("/calendar", name="calendar")
async def root():
    return base_nav("<h1>calendar</h1>")