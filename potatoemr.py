#uvicorn potatoemr:app
#uvicorn potatoemr:app --reload

from app import app
from pages._base_nav import base_nav
from pages.settings import client
from fhir.resources import __version__, __fhir_version__
from pages import registerPatient, calendar, settings
from pages.patient import allergy, demographics, overview

print("===============================================================================")
print("🥔🥔🥔 Welcome to PotatoEMR 🥔🥔🥔")
print("app.py using fhirpy client for fhir server", client.url)
print("app.py using fhir.resources package", __version__)
print("===============================================================================")

@app.get("/")
async def index():
    return base_nav("<h1>Welcome to Potato EMR</h1>")