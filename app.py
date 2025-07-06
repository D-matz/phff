#uvicorn potatoemr:app
#uvicorn potatoemr:app --reload

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fhirpy import AsyncFHIRClient
from fhir.resources import __version__, __fhir_version__
from fastapi.staticfiles import StaticFiles

app = FastAPI(default_response_class=HTMLResponse)
#this RESTful app, on requests, responds with HTML
#https://martinfowler.com/articles/richardsonMaturityModel.html#level3

app.mount("/static", StaticFiles(directory="static"), name="static")

client = AsyncFHIRClient(
    'https://hapi.fhir.org/baseR4/',
#    'https://r4.smarthealthit.org/',
#    'https://server.fire.ly',
    authorization='Bearer TOKEN',
)

print("===============================================================================")
print("🥔🥔🥔 Welcome to PotatoEMR 🥔🥔🥔")
print("app.py using fhirpy client for fhir server", client.url)
print("app.py using fhir.resources package", __version__)
print("===============================================================================")
