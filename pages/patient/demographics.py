from app import app
from pages.settings import client
from pages.patient._base_patient import base_patient_nav, get_all_resources
from resources.Patient import Patient
from fhir.resources.coding import Coding

@app.get("/patient/{patient_id}/demographics", name="patient_demographics_get")
async def patient_demographics_get(patient_id: str):
    all_resources = await get_all_resources(patient_id)
    patient = all_resources.patient
    return base_patient_nav(all_resources, demographics_form(patient))

@app.post("/patient/{patient_id}/demographics", name="patient_demographics_post")
async def patient_demographics_post(patient_id: str, patient: Patient):
    fhirpy_patient = client.resource('Patient', **patient.model_dump(mode='json'))
    await fhirpy_patient.update()
    all_resources = await get_all_resources(patient_id)
    patient = all_resources.patient
    return base_patient_nav(all_resources, demographics_form(patient))

def demographics_form(patient: Patient) -> str:
    phone = None
    for telecom in patient.telecom:
        if telecom.system == "phone":
            phone = telecom.value
            break
    email = None
    for telecom in patient.telecom:
        if telecom.system == "email":
            email = telecom.value
            break
    us_core_race = None
    for extension in patient.extension:
        print(extension.url)
        if extension.url == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race":
            us_core_race = Coding(**extension.extension[0].valueCoding)
    us_core_ethnicity = None
    for extension in patient.extension:
        if extension.url == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity":
            us_core_ethnicity = Coding(**extension.extension[0].valueCoding)

    print(us_core_race)
    print(us_core_ethnicity)
    return f"""<h1>Demographics</h1>
    <form
        hx-ext="form-json" 
        hx-post="{app.url_path_for("patient_demographics_post", patient_id=patient.id)}" 
        hx-target="body" 
        hx-swap="outerHTML">
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
                        {''.join(f'<option value="{v}"{" selected" if patient and patient.gender == v else ""}>{v}</option>' for v in Patient.model_fields["gender"].json_schema_extra["enum_values"])}
                    </select>
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
                <td><label for="maritalStatusDisplay">Marital Status:</label></td>
                <td>
                    <input id="maritalStatusDisplay" name="maritalStatus.coding[0].display" list="marital-status-display-list" value="{patient.maritalStatus.coding[0].display if patient.maritalStatus else ''}" 
                    onblur="setValueAndSystem(this, document.getElementById('codeSystem'), document.getElementById('codeValue'), document.getElementById('codeText'))">
                    <datalist id="marital-status-display-list">
                        {''.join(
                            f'<option value="{item["display"]}" data-system="{item["system"]}" data-value="{item["code"]}"></option>'
                            for item in (patient.valueset_maritalStatus if patient else [])
                        )}
                    </datalist>
                    <input type="hidden" id="codeSystem" name="maritalStatus.coding[0].system" value="{patient.maritalStatus.coding[0].system if patient.maritalStatus else ''}">
                    <input type="hidden" id="codeValue" name="maritalStatus.coding[0].code" value="{patient.maritalStatus.coding[0].code if patient.maritalStatus else ''}">
                    <input type="hidden" id="codeText" name="maritalStatus.text" value="{patient.maritalStatus.text if patient.maritalStatus else ''}">
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
        <button type="submit">Update Demographics</button>
    </form>
    """