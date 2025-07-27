from app import app, getClient
from fastapi import Request
from pages.patient._base_patient import base_patient_nav, get_all_resources, page_name_immunizations
from typing import List
from resources import Immunization, ImmunizationRecommendation
from datetime import datetime
from typing import List, Dict, Tuple
from utils import cc_str, dt_str, hn_str
from pydantic import BaseModel

class ImmunizationAndRec(BaseModel):
    #combined class because rec needed to include 'next due' in form
    imm: Immunization
    rec: ImmunizationRecommendation

@app.get("/patient/{patient_id}/immunization", name=page_name_immunizations)
async def patient_immunization(request: Request, patient_id: str):
    all_resources = await get_all_resources(request, patient_id)
    immunization_list = all_resources.immunizations
    form = ""
    ret = immunization_page(patient_id, immunization_list, form)
    return base_patient_nav(request, all_resources, ret, page_name_immunizations)

@app.get("/patient/{patient_id}/immunization/form/new", name="patient_immunization_form_new_get")
async def patient_immunization_form_new_get(request: Request, patient_id: str):
    all_resources = await get_all_resources(request, patient_id)
    immunization_list = all_resources.immunizations
    form = immunization_form(ImmunizationAndRec(
        imm = Immunization.model_construct(),
        rec = ImmunizationRecommendation.model_construct()
        ), patient_id)
    ret = immunization_page(patient_id, immunization_list, form)
    return base_patient_nav(request, all_resources, ret, page_name_immunizations)

@app.post("/patient/{patient_id}/immunization/form/new", name="patient_immunization_form_new_post")
async def patient_immunization_form_new_post(request: Request, patient_id: str, immAndRec: ImmunizationAndRec):
    fhirpy_immunization = getClient(request).resource('Immunization', **immAndRec.imm.model_dump())
    await fhirpy_immunization.create()
    all_resources = await get_all_resources(request, patient_id)
    immunization_list = all_resources.immunizations
    form = ""
    ret = immunization_page(patient_id, immunization_list, form)
    return base_patient_nav(request, all_resources, ret, page_name_immunizations)

@app.get("/patient/{patient_id}/immunization/form/existing/{immunization_id}", name="patient_immunization_form_existing_get")
async def patient_immunization_form_existing_get(patient_id: str, immunization_id: str, request: Request):
    fhirpy_immunization = await getClient(request).reference('Immunization', immunization_id).to_resource()
    immunization: Immunization = Immunization.model_validate(fhirpy_immunization)
    all_resources = await get_all_resources(request, patient_id)
    immunization_list = all_resources.immunizations
    form = immunization_form(ImmunizationAndRec(
        imm = immunization,
        rec = ImmunizationRecommendation.model_construct()
        ), patient_id)
    ret = immunization_page(patient_id, immunization_list, form)
    return base_patient_nav(request, all_resources, ret, page_name_immunizations)

@app.post("/patient/{patient_id}/immunization/form/existing/{immunization_id}", name="patient_immunization_form_existing_post")
async def patient_immunization_form_existing_post(request: Request, patient_id: str, immunization_id: str, immAndRec: ImmunizationAndRec):
    fhirpy_immunization = getClient(request).resource('Immunization', **immAndRec.imm.model_dump())
    await fhirpy_immunization.update()
    all_resources = await get_all_resources(request, patient_id)
    immunization_list = all_resources.immunizations
    form = ""
    ret = immunization_page(patient_id, immunization_list, form)
    return base_patient_nav(request, all_resources, ret, page_name_immunizations)

@app.post("/patient/{patient_id}/immunization/{immunization_id}/delete", name="patient_immunization_delete")
async def patient_immunization_delete(request: Request, patient_id: str, immunization_id: str):
    fhirpy_immunization = await getClient(request).reference('Immunization', immunization_id).to_resource()
    await fhirpy_immunization.delete()
    all_resources = await get_all_resources(request, patient_id)
    immunization_list = all_resources.immunizations
    form = ""
    ret = immunization_page(patient_id, immunization_list, form)
    return base_patient_nav(request, all_resources, ret, page_name_immunizations)

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
    {form_content}
    <style>
        .spacer {{
            height: 10px;
        }}
             
        .vaccine-group td{{
            padding: 4px;
            border-bottom: 1px solid;
        }}
            .vaccine-group td:first-child {{
            border-left: 3px solid;
        }}
                
        .spacer + .vaccine-group td:first-child,
        tbody .vaccine-group:first-child td:first-child {{
            border-top-left-radius: 8px;
        }}
        
        .vaccine-group:has(+ .spacer) td:first-child,
        tbody .vaccine-group:last-child td:first-child {{
            border-bottom-left-radius: 8px;
        }}
            
        .vaccine-group:first-child td,
        .spacer + .vaccine-group td {{
            border-top: 1px solid;
        }}
    </style>
    <h1>Immunization History</h1>
    <div id="immunization-page" class="color-color3" style="margin: 4px; padding: 4px; border: 2px solid; width: fit-content;">
    <table style="border-collapse: separate; border-spacing: 0;">
        <thead>
                <th style="text-align: left; padding-left: 8px;">Immunization</th>
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
                        <td>
                            <button hx-target="body"
                                    hx-swap="outerHTML"
                                    hx-get="{app.url_path_for("patient_immunization_form_existing_get", patient_id=patient_id, immunization_id=imm.id)}"
                                    hx-push-url="false">
                                        Edit
                                    </button>
                        </td>
                    </tr>""")
        lines.append('<tr class="spacer"></tr>')
    lines.append(f"""
        </tbody>
    </table>""")
    return(''.join(lines))


def immunization_form(immAndRec: ImmunizationAndRec, patient_id: str):
    imm = immAndRec.imm
    print("from existing date is", imm.occurrenceDateTime)
    rec = immAndRec.rec
    return f"""
       <form id="immunization-form" 
          hx-ext="form-json" 
          hx-post="{app.url_path_for("patient_immunization_form_existing_post", patient_id=patient_id, immunization_id=imm.id)}" 
          hx-target="body" 
          hx-swap="outerHTML"
          class="color-color3 shadow"
          style="position: absolute; top: 20vh; right: 20vw; width: 70vw; cursor: move; padding: 4px; border: 2px solid; border-radius: 8px; z-index: 1;">
        <script>
            dragElt(document.getElementById('immunization-form'))
        </script>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1em;">
                <b>{cc_str(imm.vaccineCode)}</b>
                <button type="button" onclick="document.getElementById('immunization-form')?.remove();">
                    X
                </button>
            </div>
            <style>
                .vaccine-form label,
                .vaccine-form input {{
                    display: block;
                    width: 300px;
                }}
            </style>
            <div class="vaccine-form" style="display: flex; flex-wrap: wrap; gap: 1em;">
                <div>
                    <label for="vaccineCode">Name:</label>
                    <input id="vaccineCode" name= value="">
                </div>
                <div>
                    <label for="occurrenceDateTime">Date:</label>
                    <input type="datetime-local" id="occurrenceDateTime" name="occurrenceDateTime" value="{dt_str(imm.occurrenceDateTime)}">
                </div>
                <div>
                    <label for="???">Next Due:</label>
                    <input type="datetime-local" id="???" name="???" value="{''}">
                </div>
                <div>
                    <label for="">Given By:</label>
                    <input name="" value="{imm.performer[0].actor if imm.performer and len(imm.performer) else ''}">
                </div>
                <div>
                    <label for="lotNumber">Lot #:</label>
                    <input id="lotNumber" name="lotNumber" value="{imm.lotNumber}">
                </div>
                <div>
                    <label for="x">Dose:</label>
                    <input id="doseQuantity" name="doseQuantity.value" value="{imm.doseQuantity.value if imm.doseQuantity else ''}">
                </div>
                <div>
                    <label for="site">Site:</label>
                    <input id="site" name="site" value="{cc_str(imm.site)}">
                </div>
                <div>
                    <label for="route">Route:</label>
                    <input id="route" name="route" value="{cc_str(imm.route)}">
                </div>
                <div>
                    <label for="manufacturer">Manufacturer:</label>
                    <input id="manufacturer" name="manufacturer" value="{imm.manufacturer}">
                </div>
                <div>
                    <label for="x">Location:</label>
                    <input value="{imm.location}">
                </div>
                <div>
                    <label for="x">Expires:</label>
                    <input value="{imm.expirationDate}">
                </div>
                <div>
                    <label for="x">Comment:</label>
                    <input value="{imm.note[0].text if imm.note and len(imm.note) else ''}"
                      style="width: 100%">
                </div>
            </div>
        </form>
    """