from app import app
from pages._base_nav import base_nav
from pages.settings import client
from resources.Patient import Patient
from fastapi import Request


@app.get("/registerPatient", name="registerPatient_get")
async def root():
    return base_nav("<h1>register patient</h1>")

@app.post("/registerPatient", name="registerPatient_post")
async def register_patient(patient: Patient, request: Request):
    fhirpy_patient = client.resource('Patient', **patient.model_dump())
    await fhirpy_patient.create()
    return base_nav("<h1>Patient registered successfully</h1>")