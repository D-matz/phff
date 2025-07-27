from app import app, getClient
from pages.patient._base_patient import base_patient_nav, get_all_resources, page_name_allergy
from typing import List
from fastapi import Request
from resources import AllergyIntolerance

vs_allergyIntolerance_code: list[dict[str, str]] = [
        { "system": "http://snomed.info/sct", "code": "91930004", "display": "Allergy to eggs" },
        { "system": "http://snomed.info/sct", "code": "91932001", "display": "Allergy to peanuts" },
        { "system": "http://snomed.info/sct", "code": "91936005", "display": "Allergy to latex" },
        { "system": "http://snomed.info/sct", "code": "300916003", "display": "Allergy to penicillin" },
        { "system": "http://snomed.info/sct", "code": "300913006", "display": "Allergy to sulfonamide" },
        { "system": "http://snomed.info/sct", "code": "26743006", "display": "House dust mite allergy" },
        { "system": "http://snomed.info/sct", "code": "441952005", "display": "Allergy to tree pollen" },
        { "system": "http://snomed.info/sct", "code": "414285001", "display": "Allergy to grass pollen" },
        { "system": "http://snomed.info/sct", "code": "419474003", "display": "Allergy to cat dander" },
        { "system": "http://snomed.info/sct", "code": "294259002", "display": "Allergy to penicillin V" },
        { "system": "http://snomed.info/sct", "code": "420246004", "display": "Allergy to ragweed" },
        { "system": "http://snomed.info/sct", "code": "300914000", "display": "Allergy to cephalosporin antibiotic" },
        { "system": "http://snomed.info/sct", "code": "277132007", "display": "Allergy to latex (finding)" },
        { "system": "http://snomed.info/sct", "code": "227493005", "display": "Cashew nut allergy" },
        { "system": "http://snomed.info/sct", "code": "300915001", "display": "Allergy to aminopenicillin antibiotic" },
        { "system": "http://snomed.info/sct", "code": "300918004", "display": "Allergy to penicillin G" },
        { "system": "http://snomed.info/sct", "code": "294163004", "display": "Allergy to codeine" },
        { "system": "http://snomed.info/sct", "code": "235719002", "display": "Allergy to iodine" },
        { "system": "http://snomed.info/sct", "code": "235719002", "display": "Allergy to iodine" },
        { "system": "http://snomed.info/sct", "code": "300917000", "display": "Allergy to cephalothin" },
        { "system": "http://snomed.info/sct", "code": "300919007", "display": "Allergy to penicillamine" },
        { "system": "http://snomed.info/sct", "code": "300921000", "display": "Allergy to penicillin antibiotic" }
    ]

vs_criticality: list[dict[str, str]] = [
    {
        "code": "low",
        "system": "http://hl7.org/fhir/allergy-intolerance-criticality",
        "display": "Low Risk",
        "definition": "Worst case result of a future exposure is not assessed to be life-threatening or having high potential for organ system failure."
    },
    {
        "code": "high",
        "system": "http://hl7.org/fhir/allergy-intolerance-criticality",
        "display": "High Risk",
        "definition": "Worst case result of a future exposure is assessed to be life-threatening or having high potential for organ system failure."
    },
    {
        "code": "unable-to-assess",
        "system": "http://hl7.org/fhir/allergy-intolerance-criticality",
        "display": "Unable to Assess Risk",
        "definition": "Unable to assess the worst case result of a future exposure."
    }
]

vs_category: list[dict[str, str]] = [
    {
        "code": "food",
        "system": "http://hl7.org/fhir/allergy-intolerance-category",
        "display": "Food",
        "definition": "Any substance consumed to provide nutritional support for the body."
    },
    {
        "code": "medication",
        "system": "http://hl7.org/fhir/allergy-intolerance-category",
        "display": "Medication",
        "definition": "Substances administered to achieve a physiological effect."
    },
    {
        "code": "environment",
        "system": "http://hl7.org/fhir/allergy-intolerance-category",
        "display": "Environment",
        "definition": "Any substances that are encountered in the environment, including any substance not already classified as food, medication, or biologic."
    },
    {
        "code": "biologic",
        "system": "http://hl7.org/fhir/allergy-intolerance-category",
        "display": "Biologic",
        "definition": "A preparation that is synthesized from living organisms or their products, especially a human or animal protein, such as a hormone or antitoxin, that is used as a diagnostic, preventive, or therapeutic agent. Examples of biologic medications include: vaccines; allergenic extracts, which are used for both diagnosis and treatment (for example, allergy shots); gene therapies; cellular therapies. There are other biologic products, such as tissues, which are not typically associated with allergies."
    }
]

@app.get("/patient/{patient_id}/allergy", name=page_name_allergy)
async def patient_allergy(request: Request, patient_id: str):
    all_resources = await get_all_resources(request, patient_id)
    allergies = all_resources.allergies
    form = ""
    ret = allergy_page(patient_id, allergies, form)
    return base_patient_nav(request, all_resources, ret, page_name_allergy)

@app.get("/patient/{patient_id}/allergy/form/new", name="patient_allergy_form_new_get")
async def patient_allergy_form_new_get(request: Request, patient_id: str):
    all_resources = await get_all_resources(request, patient_id)
    allergies = all_resources.allergies
    form = allergy_form(AllergyIntolerance.model_construct(), request, patient_id)
    ret = allergy_page(patient_id, allergies, form)
    return base_patient_nav(request, all_resources, ret, page_name_allergy)

@app.post("/patient/{patient_id}/allergy/form/new", name="patient_allergy_form_new_post")
async def patient_allergy_form_new_post(request: Request, patient_id: str, allergy: AllergyIntolerance):
    fhirpy_allergy = getClient(request).resource('AllergyIntolerance', **allergy.model_dump())
    await fhirpy_allergy.create()
    all_resources = await get_all_resources(request, patient_id)
    allergies = all_resources.allergies
    form = ""
    ret = allergy_page(patient_id, allergies, form)
    return base_patient_nav(request, all_resources, ret, page_name_allergy)

@app.get("/patient/{patient_id}/allergy/form/existing/{allergy_id}", name="patient_allergy_form_existing_get")
async def patient_allergy_form_existing_get(patient_id: str, allergy_id: str, request: Request):
    fhirpy_allergy = await getClient(request).reference('AllergyIntolerance', allergy_id).to_resource()
    allergy: AllergyIntolerance = AllergyIntolerance.model_validate(fhirpy_allergy)
    all_resources = await get_all_resources(request, patient_id)
    allergies = all_resources.allergies
    form = allergy_form(allergy, request, patient_id)
    ret = allergy_page(patient_id, allergies, form)
    return base_patient_nav(request, all_resources, ret, page_name_allergy)

@app.post("/patient/{patient_id}/allergy/form/existing/{allergy_id}", name="patient_allergy_form_existing_post")
async def patient_allergy_form_existing_post(request: Request, patient_id: str, allergy_id: str, allergy: AllergyIntolerance):
    fhirpy_allergy = getClient(request).resource('AllergyIntolerance', **allergy.model_dump())
    await fhirpy_allergy.update()
    all_resources = await get_all_resources(request, patient_id)
    allergies = all_resources.allergies
    form = ""
    ret = allergy_page(patient_id, allergies, form)
    return base_patient_nav(request, all_resources, ret, page_name_allergy)

@app.post("/patient/{patient_id}/allergy/{allergy_id}/delete", name="patient_allergy_delete")
async def patient_allergy_delete(request: Request, patient_id: str, allergy_id: str):
    fhirpy_allergy = await getClient(request).reference('AllergyIntolerance', allergy_id).to_resource()
    await fhirpy_allergy.delete()
    all_resources = await get_all_resources(request, patient_id)
    allergies = all_resources.allergies
    form = ""
    ret = allergy_page(patient_id, allergies, form)
    return base_patient_nav(request, all_resources, ret, page_name_allergy)

def allergy_page(patient_id: str, allergies: List[AllergyIntolerance], form_content: str):
    return f"""
        <h1>Allergies</h1>
        <div id="allergy-page" class="color-color3" style="margin: 4px; padding: 4px; border: 2px solid; width: fit-content;">
            <div style="display: flex; align-items: center; gap: 1em;">
                <h3>Allergies</h3>
                <button hx-target="body"
                        hx-swap="outerHTML"
                        hx-get="/patient/{patient_id}/allergy/form/new"
                        hx-push-url="false">
                            Add New Allergy
                        </button>
            </div>
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
                                    <td>
                                        <div style="width:200px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{getsafe(lambda: allergy.note[0].text)}</div>
                                    </td>
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
            {form_content}
        </div>
    """


def allergy_form(allergy: AllergyIntolerance, request: Request, patient_id: str):
    submit_url = request.url.path
    return f"""
    <form id="allergy-form" 
          hx-ext="form-json" 
          hx-post="{submit_url}" 
          hx-target="body" 
          hx-swap="outerHTML"
          class="color-color3"
          style="padding: 4px; border-radius: 8px; border: 8px solid; position: absolute; top: 100px; right: 100px; cursor: move; min-width: 600px; z-index: 1;">
        <script>
            dragElt(document.getElementById('allergy-form'))
        </script>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1em;">
            <b>{allergy.code.coding[0].display if allergy and allergy.code and allergy.code.coding and len(allergy.code.coding) > 0 and allergy.code.coding[0].display else ''}</b>
            <button type="button" onclick="document.getElementById('allergy-form')?.remove();">
                X
            </button>
        </div>
        <table>
            <tr>
                <td style="vertical-align: top;">
                    <table>
                        <tr>
                            <td>
                                <label for="codeDisplay">Allergy:</label>
                            </td>
                            <td>
                                <input id="codeDisplay" name="code.coding[0].display" list="allergy-display-list" value="{allergy.code.coding[0].display if allergy and allergy.code and allergy.code.coding and len(allergy.code.coding) > 0 and allergy.code.coding[0].display else ''}" 
                                onblur="setSystemAndCode(this, document.getElementById('codeSystem'), document.getElementById('codeCode'), document.getElementById('codeText'))">
                                <datalist id="allergy-display-list">
                                    {''.join(
                                        f'<option value="{item["display"]}" data-system="{item["system"]}" data-code="{item["code"]}"></option>'
                                        for item in (vs_allergyIntolerance_code if allergy else [])
                                    )}
                                </datalist>
                                <input type="hidden" id="codeSystem" name="code.coding[0].system" value="{allergy.code.coding[0].system if allergy and allergy.code and allergy.code.coding and len(allergy.code.coding) > 0 and allergy.code.coding[0].system else ''}">
                                <input type="hidden" id="codeCode" name="code.coding[0].code" value="{allergy.code.coding[0].code if allergy and allergy.code and allergy.code.coding and len(allergy.code.coding) > 0 and allergy.code.coding[0].code else ''}">
                                <input type="hidden" id="codeText" name="code.text" value="{allergy.code.text if allergy and allergy.code and allergy.code.text else ''}">
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <label for="reaction0">Reactions:</label>
                            </td>
                            <td>
                                <div style="display: flex; flex-direction: column;">
                                    <input id="reaction0" name="reaction[0].manifestation[0].text" value="{allergy.reaction[0].manifestation[0].text if allergy and allergy.reaction and allergy.reaction[0].manifestation and len(allergy.reaction[0].manifestation) > 0 else ''}">
                                    <input id="reaction1" name="reaction[0].manifestation[1].text" value="{allergy.reaction[0].manifestation[1].text if allergy and allergy.reaction and allergy.reaction[0].manifestation and len(allergy.reaction[0].manifestation) > 1 else ''}">
                                    <input id="reaction2" name="reaction[0].manifestation[2].text" value="{allergy.reaction[0].manifestation[2].text if allergy and allergy.reaction and allergy.reaction[0].manifestation and len(allergy.reaction[0].manifestation) > 2 else ''}">
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <label for="criticality">Severity</label>
                            </td>
                            <td>
                                <select id="criticality" name="criticality">
                                    <option value="">--</option>
                                    {''.join(f'<option value="{v["code"]}"{" selected" if allergy and allergy.criticality == v["code"] else ""}>{v["code"]}</option>' for v in vs_criticality)}
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <label for="category">Type</label>
                            </td>
                            <td>
                                <select id="category" name="category[]">
                                    <option value="">--</option>
                                    {''.join(f'<option value="{v["code"]}"{" selected" if allergy and allergy.category and allergy.category[0] == v["code"] else ""}>{v["code"]}</option>' for v in vs_category)}
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <label for="onsetDateTime">Onset</label>
                            </td>
                            <td>
                                <input type="date" id="onsetDateTime" name="onsetDateTime" value="{allergy.onsetDateTime if allergy and allergy.onsetDateTime else ''}">
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <label for="recordedDate">Recorded</label>
                            </td>
                            <td>
                                <input type="date" id="recordedDate" name="recordedDate" value="{allergy.recordedDate if allergy and allergy.recordedDate else ''}">
                            </td>
                        </tr>
                    </table>
                </td>
                <td>
                    <table>
                        <tr>
                            <td>
                                <label for="note">Note</label>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <textarea id="note" name="note[0].text" rows="16" cols="40" style="width:100%">{allergy.note[0].text if allergy and allergy.note and allergy.note[0] and allergy.note[0].text else ''}</textarea>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
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
        <div style="margin-top:1em;">
            <button type="submit">Submit</button>
            <button type="button" onclick="document.getElementById('allergy-form')?.remove();">
              Cancel
            </button>
            {f"""<button type="button"
                    hx-post="/patient/{patient_id}/allergy/{allergy.id}/delete" 
                    hx-confirm="Are you sure you want to delete this allergy?"
                    hx-push-url="false">
                Delete
            </button>"""
            if allergy.id else ''}
        </div>
    </form>
    """

def getsafe(fn, default="-"):
    try:
        return fn() or default
    except Exception:
        return default