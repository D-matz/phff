from app import app
from pages.settings import client
from pages.patient._base_patient import base_patient_nav, get_all_resources
from fhir.resources.R4B.patient import Patient

@app.get("/patient/{patient_id}/overview", name="patient_overview")
async def patient_overview(patient_id: str):
    all_resources = await get_all_resources(patient_id)
    patient = all_resources.patient
    print(f"Patient ID: {patient.id}")

    return base_patient_nav(all_resources, "<h1>overview</h1>")