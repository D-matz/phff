from app import app, getClient
from pages._base_nav import base_nav
from resources import Patient
from fastapi import Request


@app.get("/registerPatient", name="registerPatient_get")
async def root(request: Request):
    return base_nav(request, "<h1>register patient</h1>")

@app.post("/registerPatient", name="registerPatient_post")
async def register_patient(patient: Patient, request: Request):
    fhirpy_patient = getClient(request).resource('Patient', **patient.model_dump())
    await fhirpy_patient.create()
    return base_nav(request, "<h1>Patient registered successfully</h1>")