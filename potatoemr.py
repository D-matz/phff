#uvicorn potatoemr:app
#uvicorn potatoemr:app --reload

from app import app
from pages._base_nav import base_nav
from pages import registerPatient, calendar, settings, searchPatient
from pages.patient import overview, allergy

@app.get("/")
async def index():
    return base_nav("<h1>Welcome to Potato EMR</h1>")