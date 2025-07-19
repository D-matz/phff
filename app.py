#uvicorn potatoemr:app
#uvicorn potatoemr:app --reload

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(default_response_class=HTMLResponse)
#this RESTful app, on requests, responds with HTML
#https://martinfowler.com/articles/richardsonMaturityModel.html#level3

app.mount("/static", StaticFiles(directory="static"), name="static")

