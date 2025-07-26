from app import app
from pages.settings import client
from pages.patient._base_patient import base_patient_nav, get_all_resources, page_name_overview
from test.resources import Patient

@app.get("/patient/{patient_id}/overview", name=page_name_overview)
async def patient_overview(patient_id: str):
    all_resources = await get_all_resources(patient_id)
    patient = all_resources.patient

    return base_patient_nav(all_resources, "<h1>overview</h1>", page_name_overview)