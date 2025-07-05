from app import app
from pages._base_nav import base_nav

@app.get("/registerPatient", name="registerPatient")
async def root():
    return base_nav("<h1>register patient</h1>")