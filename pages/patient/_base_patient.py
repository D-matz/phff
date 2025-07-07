from typing import List
from pydantic import BaseModel
from pages.settings import client
import base64
from resources.Patient import Patient
from resources.AllergyIntolerance import AllergyIntolerance
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.medicationrequest import MedicationRequest
from fhir.resources.R4B.attachment import Attachment
from pages._base_nav import base_nav

class AllResources(BaseModel):
    patient: Patient
    allergies: List[AllergyIntolerance]
    conditions: List[Condition]
    medications: List[MedicationRequest]

async def get_all_resources(patient_id) -> AllResources:
    """Fetches a Patient resource and their related resources (AllergyIntolerance, etc).
    Useful because every patient page will need various resources for the sidebar,
    and this way we only make one request to FHIR server, which may be rate limited."""
    resources = await client.resources('Patient') \
    .search(_id=patient_id) \
    .revinclude('AllergyIntolerance', 'patient') \
    .revinclude('Condition', 'patient') \
    .revinclude('MedicationRequest', 'subject') \
    .fetch_raw()

    # The 'resources' variable now contains a bundle with the Patient resource
    # and all the specified related resources.
    # You can now iterate through the bundle to access the different resources.

    #this dummy patient.model_construct() is just because AllResources patient cant be None
    #but really a patient page should always have a patient resource, there should always be a patient from the bundle
    ret = AllResources(patient=Patient.model_construct(), allergies=[], conditions=[], medications=[])
    for entry in resources.entry:
        resource = entry.resource
        resource_type = resource.resource_type
        try:
            if resource_type == 'Patient':
                ret.patient = Patient.model_validate(resource.serialize())
            elif resource_type == 'AllergyIntolerance':
                ret.allergies.append(AllergyIntolerance.model_validate(resource.serialize()))
            elif resource_type == 'Condition':
                ret.conditions.append(Condition.model_validate(resource.serialize()))
            elif resource_type == 'MedicationRequest':
                ret.medications.append(MedicationRequest.model_validate(resource.serialize()))
        except Exception as e:
            print(f"Error processing resource {resource_type}: {e}, for resource: {resource.serialize()}")
    return ret


def base_patient_nav(all_resources: AllResources, content: str) -> str:
    """every page for a specific patient shows this sidebar on the left"""
    patient: Patient = all_resources.patient
    allergies: list[AllergyIntolerance] = all_resources.allergies
    conditions: list[Condition] = all_resources.conditions
    medications: list[MedicationRequest] = all_resources.medications
    photo_src = get_patient_photo_src(patient)
    return(base_nav(
        f"""
        <div style="height: 100%; display: flex;">
            <nav id="patient-sidebar" class="color-color2" style="height: 100%; padding: 4px; width: 200px; min-width: 200px; box-sizing: border-box; overflow: auto; border-right: 2px solid;">
                { f"""<img src="{photo_src}" alt="Patient Photo" style="width: 150px; height: 150px; margin: auto; display: block; object-fit: cover;">"""
                 if photo_src else
                f"""<svg width="150px" height="150px" style="margin: auto; display: block;">
                    <path fill="#ccc" d="M 104.68731,56.689353 C 102.19435,80.640493 93.104981,97.26875 74.372196,97.26875 55.639402,97.26875 46.988823,82.308034 44.057005,57.289941 41.623314,34.938838 55.639402,15.800152 74.372196,15.800152 c 18.732785,0 32.451944,18.493971 30.315114,40.889201 z"></path>
                    <path fill="#ccc" d="M 92.5675 89.6048 C 90.79484 93.47893 89.39893 102.4504 94.86478 106.9039 C 103.9375 114.2963 106.7064 116.4723 118.3117 118.9462 C 144.0432 124.4314 141.6492 138.1543 146.5244 149.2206 L 4.268444 149.1023 C 8.472223 138.6518 6.505799 124.7812 32.40051 118.387 C 41.80992 116.0635 45.66513 113.8823 53.58659 107.0158 C 58.52744 102.7329 57.52583 93.99267 56.43084 89.26926 C 52.49275 88.83011 94.1739 88.14054 92.5675 89.6048 z"></path>
                </svg>""" }
                { "".join(
                    [f"""<p>{' '.join(
                        [str(g) for g in (name.given or []) if g] +
                        ([str(name.family)] if name.family else [])
                    ) or "Unnamed"}</p>"""
                    for name in patient.name])
                 if patient.name else "Unnamed Patient" }
                <p>{patient.birthDate}</p>
                <p>MRN: {patient.id}</p>
                <div>
                    <p>Allergies:</p>
                    {"".join(
                        f"""<p>{
                            " ".join(coding.display if coding.display else coding.code
                                     for coding in allergy.code.coding)
                            if allergy.code and allergy.code.coding else "unknown allergy"
                        }</p>""" for allergy in allergies
                    )}
                </div>
                <div>
                    <p>Medications:</p>
                   {"".join(
                        f"""<p>{
                            " ".join(coding.display if coding.display else coding.code
                                     for coding in medication.medicationCodeableConcept.coding)
                            if medication.medicationCodeableConcept else "unknown medication"
                        }</p>""" for medication in medications
                    )}
                </div>
                <div>
                    <p>Problem list:</p>
                    {"".join(
                        f"""<p>{
                            " ".join(coding.display if coding.display else coding.code
                                     for coding in condition.code.coding)
                            if condition.code else "Unknown"
                        }</p>""" for condition in conditions
                    )}
                </div>
                <p>immunizations</p>
                <p>lab results</p>
                <p>vitals</p>
                <p>diagnoses</p>
                <p>procedures</p>
                <p>notes</p>
            </nav>
            <div style="flex: 1; display: flex; flex-direction: column; height: 100%;">
                <nav hx-boost="true" id="patient-nav" class="color-color2" style="padding: 4px; border-bottom: 2px solid;">
                    <a href="/patient/{patient.id}/overview">Overview</a>
                    <a href="/patient/{patient.id}/demographics">Demographics</a>
                    <a href="/patient/{patient.id}/allergy">Allergies</a>
                    <a href="/patient/{patient.id}/medication">Medication</a>
                    <a href="/patient/{patient.id}/immunization">Immunization</a>
                </nav>
                <div style="padding: 8px; flex: 1; min-height: 0;">
                    <div id="patient-content" class="color-color3" style="height: 100%; overflow: auto;">
                        {content}
                    </div>
                </div>
            </div>
        </div>
        """))


def get_patient_photo_src(patient) -> str | None:
    """
    Convert patient photo to appropriate src string using FHIR Attachment
    Returns URL if available, otherwise base64 data URL, or None if no photo
    """
    if not patient or not patient.photo or len(patient.photo) == 0:
        return None
    photo: Attachment = patient.photo[0]
    if photo.url and photo.url.strip():
        return photo.url
    if photo.data and len(photo.data) > 0 and photo.contentType and photo.contentType.strip():
        base64_string = base64.b64encode(photo.data).decode('utf-8')
        return f"data:{photo.contentType};base64,{base64_string}"
    return None