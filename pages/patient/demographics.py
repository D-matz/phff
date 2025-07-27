from app import app, getClient
from fastapi import Request
from pages.patient._base_patient import base_patient_nav, get_all_resources, page_name_demographics
from resources import Patient, Coding
import json
import html

vs_patient_maritalStatus: list[dict[str, str]] = [
    { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "A", "display": "Annulled" },
    { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "D", "display": "Divorced" },
    { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "I", "display": "Interlocutory" },
    { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "L", "display": "Legally Separated" },
    { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "M", "display": "Married" },
    { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "C", "display": "Common Law" },
    { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "P", "display": "Polygamous" },
    { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "T", "display": "Domestic partner" },
    { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "U", "display": "Unmarried" },
    { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "S", "display": "Never Married" },
    { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "W", "display": "Widowed" },
    { "system": "http://terminology.hl7.org/CodeSystem/v3-NullFlavor", "code": "UNK", "display": "Unknown" }
]

vs_patient_administrativeGender: list[dict[str, str]] = [
    {
        "code": "male",
        "system": "http://hl7.org/fhir/administrative-gender",
        "display": "Male"
    },
    {
        "code": "female",
        "system": "http://hl7.org/fhir/administrative-gender",
        "display": "Female"
    },
    {
        "code": "other",
        "system": "http://hl7.org/fhir/administrative-gender",
        "display": "Other"
    },
    {
        "code": "unknown",
        "system": "http://hl7.org/fhir/administrative-gender",
        "display": "Unknown"
    }
]

vs_patient_extension_race: list[dict[str, str]] = [
    {
    "system": "urn:oid:2.16.840.1.113883.6.238",
    "code": "1002-5",
    "display": "American Indian or Alaska Native"
    },
    {
    "system": "urn:oid:2.16.840.1.113883.6.238",
    "code": "2028-9",
    "display": "Asian"
    },
    {
    "system": "urn:oid:2.16.840.1.113883.6.238",
    "code": "2054-5",
    "display": "Black or African American"
    },
    {
    "system": "urn:oid:2.16.840.1.113883.6.238",
    "code": "2076-8",
    "display": "Native Hawaiian or Other Pacific Islander"
    },
    {
    "system": "urn:oid:2.16.840.1.113883.6.238",
    "code": "2106-3",
    "display": "White"
    }
]

vs_patient_extension_ethnicity: list[dict[str, str]] = [
    {
        "system": "urn:oid:2.16.840.1.113883.6.238",
        "code": "2135-2",
        "display": "Hispanic or Latino"
    },
    {
        "system": "urn:oid:2.16.840.1.113883.6.238",
        "code": "2186-5",
        "display": "Not Hispanic or Latino"
    }
]


@app.get("/patient/{patient_id}/demographics", name=page_name_demographics)
async def patient_demographics_get(request: Request, patient_id: str):
    all_resources = await get_all_resources(request, patient_id)
    patient = all_resources.patient
    return base_patient_nav(request, all_resources, demographics_form(patient, render_inputs_as_p=True), page_name_demographics)

@app.get("/patient/{patient_id}/demographics/form", name="patient_demographics_form_get")
async def patient_demographics_form_get(request: Request, patient_id: str):
    all_resources = await get_all_resources(request, patient_id)
    patient = all_resources.patient
    return base_patient_nav(request, all_resources, demographics_form(patient, render_inputs_as_p=False), page_name_demographics)

@app.post("/patient/{patient_id}/demographics/form", name="patient_demographics_form_post")
async def patient_demographics_form_post(request: Request, patient_id: str, patient: Patient):
    print("POST has data", patient.model_dump(mode='json'))
    fhirpy_patient = getClient(request).resource('Patient', **patient.model_dump(mode='json'))
    print("fhirpy_patient", fhirpy_patient.serialize())
    ret = await fhirpy_patient.update()
    print("ret is", ret.serialize())
    all_resources = await get_all_resources(request, patient_id)
    patient = all_resources.patient
    return base_patient_nav(request, all_resources, demographics_form(patient, render_inputs_as_p=True), page_name_demographics)

def demographics_form(patient: Patient, render_inputs_as_p: bool) -> str:
    phone = None
    if patient.telecom:
        for telecom in patient.telecom:
            if telecom.system == "phone":
                phone = telecom.value
                break
    email = None
    if patient.telecom:
        for telecom in patient.telecom:
            if telecom.system == "email":
                email = telecom.value
                break
    us_core_race = 0
    us_core_race_ombCategory = 0
    us_core_race_url = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race"
    us_core_race_ombCategory_url = "ombCategory"
    print("try to find race extension")
    if patient.extension:
        for i in range(len(patient.extension)):
            ext = patient.extension[i]
            print(ext.url)
            if ext.url == us_core_race_url:
                us_core_race = i
                if ext.extension:
                    for j in range(len(ext.extension)):
                        race_ext = ext.extension[j]
                        if race_ext.url == us_core_race_ombCategory_url:
                            us_core_race_ombCategory = j
                            print(race_ext.valueCoding)

    print("us_core_race:", us_core_race, "us_core_race_ombCategory:", us_core_race_ombCategory)

    us_core_ethnicity = 0
    if us_core_race == 0:
        us_core_ethnicity = 1
    us_core_ethnicity_ombCategory = 0
    us_core_ethnicity_url = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity"
    us_core_ethnicity_ombCategory_url = "ombCategory"
    print("try to find ethnicity extension")
    if patient.extension:
        for i in range(len(patient.extension)):
            ext = patient.extension[i]
            print(ext.url)
            if ext.url == us_core_ethnicity_url:
                us_core_ethnicity = i
                if ext.extension:
                    for j in range(len(ext.extension)):
                        ethnicity_ext = ext.extension[j]
                        if ethnicity_ext.url == us_core_ethnicity_ombCategory_url:
                            us_core_ethnicity_ombCategory = j
                            print(ethnicity_ext.valueCoding)

    print("us_core_ethnicity:", us_core_ethnicity, "us_core_ethnicity_ombCategory:", us_core_ethnicity_ombCategory)

    return f"""
    <h1>Demographics</h1>
    <form id="demographics-form"
        data-formjsondefault='{html.escape(json.dumps(patient.model_dump(mode='json')))}'
        hx-ext="form-json" 
        hx-post="{app.url_path_for("patient_demographics_form_post", patient_id=patient.id)}" 
        hx-target="body" 
        hx-swap="outerHTML"
        hx-indicator="#demographics-form"
        class="htmx-indicator {'render-input-as-p' if render_inputs_as_p else ''}">
        <table>
            <tr>
                <td><label for="patient_id">MRN:</label></td>
                <td><input type="text" id="patient_id" name="id" value="{patient.id}" readonly size="40"></td>
            </tr>
            <tr>
                <td><label for="first_name">Name:</label></td>
                <td>
                    <input type="text" id="first_name" name="name[0].given[0]" value="{(patient.name[0].given[0] if patient.name and patient.name[0].given and len(patient.name[0].given) > 0 else '')}" placeholder="First">
                    <input type="text" id="middle_name" name="name[0].given[1]" value="{(patient.name[0].given[1] if patient.name and patient.name[0].given and len(patient.name[0].given) > 1 else '')}" placeholder="Middle">
                    <input type="text" id="family_name" name="name[0].family" value="{(patient.name[0].family if patient.name and patient.name[0].family else '')}" placeholder="Last">
                </td>
            </tr>
            <tr>
                <td><label for="birth_date">Birth Date:</label></td>
                <td><input type="date" id="birth_date" name="birthDate" value="{patient.birthDate if patient.birthDate else ''}"></td>
            </tr>
            <tr>
                <td><label for="gender">Gender:</label></td>
                <td>
                    <select id="gender" name="gender">
                        <option value="">--</option>
                        {''.join(f'<option value="{v["code"]}"{" selected" if patient and patient.gender == v["code"] else ""}>{v["display"]}</option>' for v in vs_patient_administrativeGender)}
                    </select>
                </td>
            </tr>
            <tr>
                <td><label for="us_core_race">Race:</label></td>
                <td>
                    <select id="us_core_race" name="extension[{us_core_race}].extension[{us_core_race_ombCategory}].valueCoding.display" 
                            onchange="setSystemAndCode(this, document.getElementById('us_core_race_System'), document.getElementById('us_core_race_Code'), null)">
                        <option value="">--</option>
                        {''.join(
                            f'<option value="{item["display"]}" data-system="{item["system"]}" data-code="{item["code"]}" {"selected" if getsafe(lambda: patient.extension[us_core_race].extension[us_core_race_ombCategory].valueCoding.display) == item["display"] else ""}>{item["display"]}</option>'
                            for item in (vs_patient_extension_race)
                        )}
                    </select>

                    <input type="hidden" id="us_core_race_System" name="extension[{us_core_race}].extension[{us_core_race_ombCategory}].valueCoding.system" 
                        value="{ getsafe(lambda: patient.extension[us_core_race].extension[us_core_race_ombCategory].valueCoding.system) }">
                    <input type="hidden" id="us_core_race_Code" name="extension[{us_core_race}].extension[{us_core_race_ombCategory}].valueCoding.code" 
                        value="{ getsafe(lambda: patient.extension[us_core_race].extension[us_core_race_ombCategory].valueCoding.code) }">
                   <input type="hidden" id="us_core_race_url" name="extension[{us_core_race}].url" 
                        value="{ us_core_race_url }">
                   <input type="hidden" id="us_core_race_ombCategory_url" name="extension[{us_core_race}].extension[{us_core_race_ombCategory}].url" 
                        value="{ us_core_race_ombCategory_url }">
                </td>
            </tr>
            <tr>
                <td><label for="us_core_ethnicity">Ethnicity:</label></td>
                <td>
                    <select id="us_core_ethnicity" name="extension[{us_core_ethnicity}].extension[{us_core_ethnicity_ombCategory}].valueCoding.display" 
                            onchange="setSystemAndCode(this, document.getElementById('us_core_ethnicity_System'), document.getElementById('us_core_ethnicity_Code'), null)">
                        <option value="">--</option>
                        {''.join(
                            f'<option value="{item["display"]}" data-system="{item["system"]}" data-code="{item["code"]}" {"selected" if getsafe(lambda: patient.extension[us_core_ethnicity].extension[us_core_ethnicity_ombCategory].valueCoding.display) == item["display"] else ""}>{item["display"]}</option>'
                            for item in (vs_patient_extension_ethnicity)
                        )}
                    </select>

                    <input type="hidden" id="us_core_ethnicity_System" name="extension[{us_core_ethnicity}].extension[{us_core_ethnicity_ombCategory}].valueCoding.system" 
                        value="{ getsafe(lambda: patient.extension[us_core_ethnicity].extension[us_core_ethnicity_ombCategory].valueCoding.system) }">
                    <input type="hidden" id="us_core_ethnicity_Code" name="extension[{us_core_ethnicity}].extension[{us_core_ethnicity_ombCategory}].valueCoding.code" 
                        value="{ getsafe(lambda: patient.extension[us_core_ethnicity].extension[us_core_ethnicity_ombCategory].valueCoding.code) }">
                   <input type="hidden" id="us_core_ethnicity_url" name="extension[{us_core_ethnicity}].url" 
                        value="{ us_core_ethnicity_url }">
                   <input type="hidden" id="us_core_ethnicity_ombCategory_url" name="extension[{us_core_ethnicity}].extension[{us_core_ethnicity_ombCategory}].url" 
                        value="{ us_core_ethnicity_ombCategory_url }">
                </td>
            </tr>

            <tr>
                <td><label for="address_line">Address:</label></td>
                <td>
                    <input type="text" id="address_line" name="address[0].line[0]" value="{(patient.address[0].line[0] if patient.address and patient.address[0].line and len(patient.address[0].line) > 0 else '')}" placeholder="Street">
                    <input type="text" id="address_city" name="address[0].city" value="{(patient.address[0].city if patient.address and patient.address[0].city else '')}" placeholder="City">
                    <input type="text" id="address_state" name="address[0].state" value="{(patient.address[0].state if patient.address and patient.address[0].state else '')}" placeholder="State">
                    <input type="text" id="address_postalCode" name="address[0].postalCode" value="{(patient.address[0].postalCode if patient.address and patient.address[0].postalCode else '')}" placeholder="Postal Code">
                </td>
            </tr>
            <tr>
                <td><label for="phone">Phone:</label></td>
                <td><input type="text" id="phone" name="telecom[0].value" value="{phone if phone else ''}"></td>
                <input type="hidden" name="telecom[0].system" value="phone">
            </tr>
            <tr>
                <td><label for="email">Email:</label></td>
                <td><input type="text" id="email" name="telecom[1].value" value="{email if email else ''}"></td>
                <input type="hidden" name="telecom[1].system" value="email">
            </tr>
            <tr>
                <td><label for="maritalStatus_Display">Marital Status:</label></td>
                <td>
                    <select id="maritalStatus_Display" name="maritalStatus.coding[0].display" 
                        onchange="setSystemAndCode(this, document.getElementById('maritalStatus_System'), document.getElementById('maritalStatus_Code'), document.getElementById('maritalStatus_Text'))">
                    <option value="">--</option>
                        {''.join(
                            f'<option value="{item["display"]}" data-system="{item["system"]}" data-code="{item["code"]}" {"selected" if patient.maritalStatus and patient.maritalStatus.coding and patient.maritalStatus.coding[0].display == item["display"] else ""}>{item["display"]}</option>'
                            for item in (vs_patient_maritalStatus if patient else [])
                        )}
                    </select>
                    <input type="hidden" id="maritalStatus_System" name="maritalStatus.coding[0].system" value="{patient.maritalStatus.coding[0].system if patient.maritalStatus and patient.maritalStatus.coding else ''}">
                    <input type="hidden" id="maritalStatus_Code" name="maritalStatus.coding[0].code" value="{patient.maritalStatus.coding[0].code if patient.maritalStatus and patient.maritalStatus.coding else ''}">
                    <input type="hidden" id="maritalStatus_Text" name="maritalStatus.text" value="{patient.maritalStatus.text if patient.maritalStatus else ''}">
                </td>
            </tr>
            <tr>
                <td label for="contact">Emergency Contact:</td>
                <td>
                    <input type="text" id="contact_name" name="contact[0].name.given[0]" value="{(patient.contact[0].name.given[0] if patient.contact and patient.contact[0].name and patient.contact[0].name.given and len(patient.contact[0].name.given) > 0 else '')}" placeholder="First">
                    <input type="text" id="contact_family" name="contact[0].name.family" value="{(patient.contact[0].name.family if patient.contact and patient.contact[0].name and patient.contact[0].name.family else '')}" placeholder="Last">
                </td>
            </tr>
        </table>
        {
            f"""<button type="button"
            hx-get="{app.url_path_for("patient_demographics_form_get", patient_id=patient.id)}">
                Edit
            </button>"""
            if render_inputs_as_p else
            f"""<button type="submit">Save</button>
                <button type="button"
                hx-get="{app.url_path_for(page_name_demographics, patient_id=patient.id)}">
                    Cancel
                </button>"""
        }
    </form>
    """

def getsafe(fn, default="-"):
    try:
        print("fn is", fn())
        return fn() or default
    except Exception:
        return default