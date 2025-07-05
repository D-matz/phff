from app import app, client
from pages.patient._base_patient import base_patient_nav, get_all_resources
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.allergyintolerance import AllergyIntoleranceReaction
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from typing import List
from fastapi import Request
from resources.AllergyIntolerance import AllergyIntolerance
import json

@app.get("/patient/{patient_id}/allergy", name="patient_allergy")
async def patient_allergy(patient_id: str):
    all_resources = await get_all_resources(patient_id)
    allergies = all_resources.allergies
    form = f"""<div id="allergy-form"></div>"""
    ret = allergy_page(patient_id, allergies, form)
    return base_patient_nav(all_resources, ret)

@app.get("/patient/{patient_id}/allergy/form/new", name="patient_allergy_form_new_get")
async def patient_allergy_form_new_get(request: Request, patient_id: str):
    all_resources = await get_all_resources(patient_id)
    allergies = all_resources.allergies
    form = allergy_form(None, request, patient_id)
    ret = allergy_page(patient_id, allergies, form)
    return base_patient_nav(all_resources, ret)

@app.post("/patient/{patient_id}/allergy/form/new", name="patient_allergy_form_new_post")
async def patient_allergy_form_new_post(request: Request, patient_id: str, allergy: AllergyIntolerance):
    fhirpy_allergy = client.resource('AllergyIntolerance', **allergy.model_dump())
    ret = await fhirpy_allergy.save()
    print("ret", ret.serialize())
    all_resources = await get_all_resources(patient_id)
    allergies = all_resources.allergies
    form = allergy_form(allergy, request, patient_id) #really should maybe be with the server's saved allergy
    ret = allergy_page(patient_id, allergies, form)
    return base_patient_nav(all_resources, ret)

@app.get("/patient/{patient_id}/allergy/form/existing/{allergy_id}", name="patient_allergy_form_existing_get")
async def patient_allergy_form_existing_get(patient_id: str, allergy_id: str, request: Request):
    fhirpy_allergy = await client.reference('AllergyIntolerance', allergy_id).to_resource()
    allergy: AllergyIntolerance = AllergyIntolerance.model_validate(fhirpy_allergy)
    all_resources = await get_all_resources(patient_id)
    allergies = all_resources.allergies
    form = allergy_form(allergy, request, patient_id)
    ret = allergy_page(patient_id, allergies, form)
    return base_patient_nav(all_resources, ret)

@app.post("/patient/{patient_id}/allergy/form/existing/{allergy_id}", name="patient_allergy_form_existing_post")
async def patient_allergy_form_existing_post(request: Request, patient_id: str, allergy_id: str, allergy: AllergyIntolerance):
    fhirpy_allergy = client.resource('AllergyIntolerance', **allergy.model_dump())
    await fhirpy_allergy.save()
    all_resources = await get_all_resources(patient_id)
    allergies = all_resources.allergies
    form = allergy_form(allergy, request, patient_id) #really should maybe be with the server's saved allergy
    ret = allergy_page(patient_id, allergies, form)
    return base_patient_nav(all_resources, ret)


def allergy_page(patient_id: str, allergies: List[AllergyIntolerance], content: str):
    return f"""
        <button hx-target="body"
                hx-swap="outerHTML"
                hx-get="/patient/{patient_id}/allergy/form/new"
                hx-push-url="false"
                hx>Add New Allergy</button>
        <table>
            <thead>
                <th>Allergy</th>
                <th>Date</th>
                <th>Notes</th>
                <th></th>
            </thead>
            <tbody>
                {"".join(f"""<tr>
                                <td>{getsafe(lambda: allergy.code.coding[0].display)}</td>
                                <td>{getsafe(lambda: allergy.onsetDateTime)}</td>
                                <td>{getsafe(lambda: allergy.note[0].text)}</td>
                                <td>
                                    <button hx-target="body"
                                            hx-get="/patient/{patient_id}/allergy/form/existing/{allergy.id}"
                                            hx-push-url="false">
                                        edit
                                    </button>
                                </td>
                 </tr>""" for allergy in allergies)}
            </tbody>
        </table>
        {content}
    """


def allergy_form(allergy: AllergyIntolerance | None, request: Request, patient_id: str):
    #print(allergy.model_dump_json(indent=2))
    submit_url = request.url.path
    return f"""
    <form id="allergy-form" hx-ext="form-json" hx-post="{submit_url}" hx-target="body" hx-swap="outerHTML">
        <div>
            <label for="codeDisplay">Allergy:</label>
            <input id="codeDisplay" name="code.coding[0].display" list="allergy-display-list" value="{allergy.code.coding[0].display if allergy and allergy.code and allergy.code.coding and len(allergy.code.coding) > 0 and allergy.code.coding[0].display else ''}" 
            onblur="setValueAndSystem(this, document.getElementById('codeSystem'), document.getElementById('codeValue'), document.getElementById('codeText'))">
            <datalist id="allergy-display-list">
                {''.join(
                    f'<option value="{item["display"]}" data-system="{item["system"]}" data-value="{item["code"]}"></option>'
                    for item in (allergy.valueset_code if allergy else [])
                )}
            </datalist>
            <input type="hidden" id="codeSystem" name="code.coding[0].system" value="{allergy.code.coding[0].system if allergy and allergy.code and allergy.code.coding and len(allergy.code.coding) > 0 and allergy.code.coding[0].system else ''}">
            <input type="hidden" id="codeValue" name="code.coding[0].code" value="{allergy.code.coding[0].code if allergy and allergy.code and allergy.code.coding and len(allergy.code.coding) > 0 and allergy.code.coding[0].code else ''}">
            <input type="hidden" id="codeText" name="code.text" value="{allergy.code.text if allergy and allergy.code and allergy.code.text else ''}">
        </div>
        <div>
            <label for="reaction0">Reactions:</label>
            <input id="reaction0" name="reaction[0].manifestation[0].text" value="{allergy.reaction[0].manifestation[0].text if allergy and allergy.reaction and allergy.reaction[0].manifestation and len(allergy.reaction[0].manifestation) > 0 else ''}">
            <input id="reaction1" name="reaction[0].manifestation[1].text" value="{allergy.reaction[0].manifestation[1].text if allergy and allergy.reaction and allergy.reaction[0].manifestation and len(allergy.reaction[0].manifestation) > 1 else ''}">
            <input id="reaction2" name="reaction[0].manifestation[2].text" value="{allergy.reaction[0].manifestation[2].text if allergy and allergy.reaction and allergy.reaction[0].manifestation and len(allergy.reaction[0].manifestation) > 2 else ''}">
        </div>
        <div>
            <label for="criticality">Severity</label>
            <select id="criticality" name="criticality">
                <option value="">--</option>
                {''.join(f'<option value="{v}"{" selected" if allergy and allergy.criticality == v else ""}>{v}</option>' for v in AllergyIntolerance.model_fields["criticality"].json_schema_extra["enum_values"])}
            </select>
        </div>
        <div>
            <label for="category">Type</label>
            <select id="category" name="category[]">
                <option value="">--</option>
                {''.join(f'<option value="{v}"{" selected" if allergy and allergy.category and allergy.category[0] == v else ""}>{v}</option>' for v in AllergyIntolerance.model_fields["category"].json_schema_extra["enum_values"])}
            </select>
        </div>
        <div>
            <label for="onsetDateTime">Onset</label>
            <input type="date" id="onsetDateTime" name="onsetDateTime" value="{allergy.onsetDateTime if allergy and allergy.onsetDateTime else ''}">
        </div>
        <div>
            <label for="recordedDate">Recorded</label>
            <input type="date" id="recordedDate" name="recordedDate" value="{allergy.recordedDate if allergy and allergy.recordedDate else ''}">
        </div>
        <div>
            <label for="note">Note</label>
            <textarea id="note" name="note[0].text" rows="10" cols="20">{allergy.note[0].text if allergy and allergy.note and allergy.note[0] and allergy.note[0].text else ''}</textarea>            
        </div>
        
        <input type="hidden" name="patient.reference" value="Patient/{patient_id}">
        {f'<input type="hidden" name="id" value="{allergy.id}">' if allergy and allergy.id else ''}
        
        {f'<input type="hidden" name="meta.versionId" value="{allergy.meta.versionId}">' if allergy and allergy.meta and allergy.meta.versionId else ''}
        {f'<input type="hidden" name="meta.lastUpdated" value="{allergy.meta.lastUpdated}">' if False and allergy and allergy.meta and allergy.meta.lastUpdated else ''}
        {f'<input type="hidden" name="meta.source" value="{allergy.meta.source}">' if allergy and allergy.meta and allergy.meta.source else ''}
        {f'<input type="hidden" name="meta.profile[]" value="{allergy.meta.profile[0]}">' if allergy and allergy.meta and allergy.meta.profile else ''}
                
        {f'<input type="hidden" name="clinicalStatus.coding[0].system" value="{allergy.clinicalStatus.coding[0].system}">' if allergy and allergy.clinicalStatus and allergy.clinicalStatus.coding and allergy.clinicalStatus.coding[0].system else ''}
        {f'<input type="hidden" name="clinicalStatus.coding[0].code" value="{allergy.clinicalStatus.coding[0].code}">' if allergy and allergy.clinicalStatus and allergy.clinicalStatus.coding and allergy.clinicalStatus.coding[0].code else ''}
        {f'<input type="hidden" name="clinicalStatus.coding[0].display" value="{allergy.clinicalStatus.coding[0].display}">' if allergy and allergy.clinicalStatus and allergy.clinicalStatus.coding and allergy.clinicalStatus.coding[0].display else ''}
        
        {f'<input type="hidden" name="verificationStatus.coding[0].system" value="{allergy.verificationStatus.coding[0].system}">' if allergy and allergy.verificationStatus and allergy.verificationStatus.coding and allergy.verificationStatus.coding[0].system else ''}
        {f'<input type="hidden" name="verificationStatus.coding[0].code" value="{allergy.verificationStatus.coding[0].code}">' if allergy and allergy.verificationStatus and allergy.verificationStatus.coding and allergy.verificationStatus.coding[0].code else ''}
        {f'<input type="hidden" name="verificationStatus.coding[0].display" value="{allergy.verificationStatus.coding[0].display}">' if allergy and allergy.verificationStatus and allergy.verificationStatus.coding and allergy.verificationStatus.coding[0].display else ''}
        
        {f'<input type="hidden" name="type" value="{allergy.type}">' if allergy and allergy.type else ''}
        
        <button type="submit">Submit</button>
    </form>
    """

def getsafe(fn, default="-"):
    try:
        return fn() or default
    except Exception:
        return default