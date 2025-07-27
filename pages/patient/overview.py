from app import app, getClient
from fastapi import Request
from pages.patient._base_patient import base_patient_nav, get_all_resources, page_name_overview
from resources import Patient

@app.get("/patient/{patient_id}/overview", name=page_name_overview)
async def patient_overview(request: Request, patient_id: str):
    all_resources = await get_all_resources(request, patient_id)
    patient = all_resources.patient

    return base_patient_nav(request, all_resources, "<h1>overview</h1>", page_name_overview)