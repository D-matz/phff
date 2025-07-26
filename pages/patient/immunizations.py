from app import app
from pages.settings import client
from pages.patient._base_patient import base_patient_nav, get_all_resources, page_name_immunizations
from typing import List
from fastapi import Request
from test.resources import Immunization
from datetime import datetime
from typing import List, Dict, Tuple

@app.get("/patient/{patient_id}/immunization", name=page_name_immunizations)
async def patient_immunization(patient_id: str):
    all_resources = await get_all_resources(patient_id)
    immunization_list = all_resources.immunizations
    form = ""
    ret = immunization_page(patient_id, immunization_list, form)
    return base_patient_nav(all_resources, ret, page_name_immunizations)

@app.get("/patient/{patient_id}/immunization/form/new", name="patient_immunization_form_new_get")
async def patient_immunization_form_new_get(request: Request, patient_id: str):
    all_resources = await get_all_resources(patient_id)
    immunization_list = all_resources.immunizations
    form = immunization_form(Immunization.model_construct(), patient_id)
    ret = immunization_page(patient_id, immunization_list, form)
    return base_patient_nav(all_resources, ret, page_name_immunizations)

@app.post("/patient/{patient_id}/immunization/form/new", name="patient_immunization_form_new_post")
async def patient_immunization_form_new_post(request: Request, patient_id: str, immunization: Immunization):
    fhirpy_immunization = client.resource('Immunization', **immunization.model_dump())
    await fhirpy_immunization.create()
    all_resources = await get_all_resources(patient_id)
    immunization_list = all_resources.immunizations
    form = ""
    ret = immunization_page(patient_id, immunization_list, form)
    return base_patient_nav(all_resources, ret, page_name_immunizations)

@app.get("/patient/{patient_id}/immunization/form/existing/{immunization_id}", name="patient_immunization_form_existing_get")
async def patient_immunization_form_existing_get(patient_id: str, immunization_id: str, request: Request):
    fhirpy_immunization = await client.reference('Immunization', immunization_id).to_resource()
    immunization: Immunization = Immunization.model_validate(fhirpy_immunization)
    all_resources = await get_all_resources(patient_id)
    immunization_list = all_resources.immunizations
    form = immunization_form(immunization, patient_id)
    ret = immunization_page(patient_id, immunization_list, form)
    return base_patient_nav(all_resources, ret, page_name_immunizations)

@app.post("/patient/{patient_id}/immunization/form/existing/{immunization_id}", name="patient_immunization_form_existing_post")
async def patient_immunization_form_existing_post(request: Request, patient_id: str, immunization_id: str, immunization: Immunization):
    fhirpy_immunization = client.resource('Immunization', **immunization.model_dump())
    await fhirpy_immunization.update()
    all_resources = await get_all_resources(patient_id)
    immunization_list = all_resources.immunizations
    form = ""
    ret = immunization_page(patient_id, immunization_list, form)
    return base_patient_nav(all_resources, ret, page_name_immunizations)

@app.post("/patient/{patient_id}/immunization/{immunization_id}/delete", name="patient_immunization_delete")
async def patient_immunization_delete(patient_id: str, immunization_id: str):
    fhirpy_immunization = await client.reference('Immunization', immunization_id).to_resource()
    await fhirpy_immunization.delete()
    all_resources = await get_all_resources(patient_id)
    immunization_list = all_resources.immunizations
    form = ""
    ret = immunization_page(patient_id, immunization_list, form)
    return base_patient_nav(all_resources, ret, page_name_immunizations)

def immunization_page(patient_id: str, immunization_list: List[Immunization], form_content: str):
    immunizations_byVaccine: Dict[Tuple[str, str], List[Immunization]] = {} 
    #point is to group all doses of a particular vaccine together
    #so doctor can see oh these were all the flu shots, these were all the hep shots, whatever
    #point of Tuple[str, str] is to group vaccines by system/code combo
    for imm in immunization_list:
        if imm.status == 'completed' or imm.status == 'Completed':
            #doctor only wants to see vaccinations actually done
            #think it's only lower case completed allowed but whatever
            imm_key = ('n/a', 'n/a')
            if imm.vaccineCode and imm.vaccineCode.coding and len(imm.vaccineCode.coding) > 0:
                first_coding = imm.vaccineCode.coding[0]
                if first_coding.system and first_coding.code:
                    imm_key = (first_coding.system, first_coding.code)
                    if imm_key in immunizations_byVaccine:
                        immunizations_byVaccine[imm_key].append(imm)
                    else:
                        immunizations_byVaccine[imm_key] = [imm]
    lines = []
    lines.append(f"""
    <style>
        .vaccine-group td{{
            padding: 4px;
        }}
            .vaccine-group td:first-child {{
            border-left: 5px solid;
        }}
                
        .spacer + .vaccine-group td:first-child,
        tbody .vaccine-group:first-child td:first-child {{
            border-top-left-radius: 8px;
        }}
        
        .vaccine-group:has(+ .spacer) td:first-child,
        tbody .vaccine-group:last-child td:first-child {{
            border-bottom-left-radius: 8px;
        }}
        
        .spacer {{
            height: 10px;
        }}
    </style>
    <h1>Immunization History</h1>
    <div id="immunization-page" class="color-color3" style="margin: 4px; padding: 4px; border: 2px solid; width: fit-content;">
    <table style="border-collapse: separate; border-spacing: 0;">
        <thead>
                <th style="text-align: left">Immunization</th>
                <th style="text-align: left">Date</th>
                <th style="text-align: left">Note</th>
                <th style="text-align: left"></th>
        </thead>                 
        <tbody>
    """)
    for vaccine_list in immunizations_byVaccine.values():
        first_of_vaccine = True #since we group vaccines together, only show name on first one
        for imm in vaccine_list:
            vaccineCode = ''
            if first_of_vaccine:
                if imm.vaccineCode.coding and len(imm.vaccineCode.coding):
                    vaccine_code_1 = imm.vaccineCode.coding[0]
                    if vaccine_code_1.display:
                        vaccineCode = vaccine_code_1.display
                    elif vaccine_code_1.code:
                        vaccineCode = vaccine_code_1.code
                    else:
                        vaccineCode = imm.vaccineCode.text
            first_of_vaccine = False
            lines.append(f"""
                    <tr class="color-color3-hover vaccine-group">
                        <td style="width: 150px;">{vaccineCode}</td>
                        <td style="width: 150px;">{imm.occurrenceDateTime[:10] if imm.occurrenceDateTime else ''}</td>
                        <td style="width: 400px; overflow: hidden">{imm.note[0].text if imm.note and len(imm.note) else ''}</td>
                        <td><button>edit</button></td>
                    </tr>""")
        lines.append('<tr class="spacer"></tr>')
    lines.append(f"""
        </tbody>
    </table>""")
    return(''.join(lines))


def immunization_form(immunization: Immunization, patient_id: str):
    return f"""
       
    """
