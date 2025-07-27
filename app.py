#uvicorn potatoemr:app
#uvicorn potatoemr:app --reload

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from enum import Enum
from fhirpy import AsyncFHIRClient, __version__ as fpv, __copyright__ as fpc

app = FastAPI(default_response_class=HTMLResponse)
#this RESTful app, on requests, responds with HTML
#https://martinfowler.com/articles/richardsonMaturityModel.html#level3

app.mount("/static", StaticFiles(directory="static"), name="static")

class FHIRServers(Enum):
    HAPI = "https://hapi.fhir.org/baseR4/"
    SMART_HEALTH_IT = "https://r4.smarthealthit.org/"
    FIRELY = "https://server.fire.ly"

def getClient(request: Request):
    return AsyncFHIRClient(request.cookies.get("fhir_server_url", list(FHIRServers)[0].value), authorization='Bearer TOKEN')

print("===============================================================================")
print("🥔🥔🥔 Welcome to PotatoEMR 🥔🥔🥔")
print(f"using fhirpy {fpv} {fpc}")
print(f"FHIR Server urls {', '.join([server.value for server in FHIRServers])}")
print(f"settings from pages/settings.py")
print("===============================================================================")
