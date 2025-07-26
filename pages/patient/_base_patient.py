from app import app
from typing import List
from pydantic import BaseModel
from pages.settings import client
import base64
from resources import (
    AllergyIntolerance, Attachment, Condition, Immunization, Patient, MedicationRequest)
from pages._base_nav import base_nav

#the individual patient pages import their base link names from here
#because when patient page calls this base patient template,
#it uses name to say it's the active tab and should be highlighted
#they need to be defined here and not in the patient page to avoid circular import
page_name_allergy = "patient_allergy"
page_name_demographics = "demographics"
page_name_immunizations = "immunization"
page_name_overview = "overview"
page_name_photo = "photo"
page_name_medications = "medication"

class AllResources(BaseModel):
    patient: Patient
    allergies: List[AllergyIntolerance]
    conditions: List[Condition]
    medications: List[MedicationRequest]
    immunizations: List[Immunization]

async def get_all_resources(patient_id) -> AllResources:
    """Fetches a Patient resource and their related resources (AllergyIntolerance, etc).
    Useful because every patient page will need various resources for the sidebar,
    and this way we only make one request to FHIR server, which may be rate limited."""
    resources = await client.resources('Patient') \
    .search(_id=patient_id) \
    .revinclude('AllergyIntolerance', 'patient') \
    .revinclude('Condition', 'patient') \
    .revinclude('Immunization', 'patient') \
    .revinclude('MedicationRequest', 'subject') \
    .fetch_raw()

    # The 'resources' variable now contains a bundle with the Patient resource
    # and all the specified related resources.
    # You can now iterate through the bundle to access the different resources.

    if "entry" not in resources:
        #need to return error patient_id not in client.url server
        return None

    #this dummy patient.model_construct() is just because AllResources patient cant be None
    #but really a patient page should always have a patient resource, there should always be a patient from the bundle
    ret = AllResources(patient=Patient.model_construct(), allergies=[], conditions=[], immunizations=[], medications=[])
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
            elif resource_type == 'Immunization':
                ret.immunizations.append(Immunization.model_validate(resource.serialize()))
            elif resource_type == 'MedicationRequest':
                ret.medications.append(MedicationRequest.model_validate(resource.serialize()))
        except Exception as e:
            print(f"Error processing resource {resource_type}: {e}, for resource: {resource.serialize()}")
    return ret


def base_patient_nav(all_resources: AllResources, content: str, activeTab: str) -> str:
    """every page for a specific patient shows sidebar on left and links on top
    patient page content goes in under them in patient-content
    both navs have hx-boost for links and loading indicator on patient-content
    page should say it's the active tab, so template can highlight page link in nav"""
    patient: Patient = all_resources.patient
    allergies: list[AllergyIntolerance] = all_resources.allergies
    conditions: list[Condition] = all_resources.conditions
    medications: list[MedicationRequest] = all_resources.medications
    immunizations: list[Immunization] = all_resources.immunizations
    def tab_link(tab_name, label):
        """if this tab name is active tab, make same color as patient page"""
        if tab_name == activeTab:
            style = 'class="color-color3" style="margin-top: 2px; margin-bottom: -2px; border-radius: 12px 12px 0 0; border: 2px solid; border-bottom: 0px; padding: 2px;"'
        else:
            style = 'class="color-color2-hover" style="padding: 4px; padding-top: 6px;"'
        return f'<a {style} href="{app.url_path_for(tab_name, patient_id=patient.id)}">{label}</a>'
    
    return(base_nav(
        f"""
        <div style="height: 100%; display: flex;">
            <nav hx-boost="true" hx-indicator="#patient-content" 
                id="patient-sidebar" class="color-color2" style="height: 100%; padding: 4px; width: 200px; min-width: 200px; box-sizing: border-box; overflow: auto; border-right: 2px solid;">

                <a href="{app.url_path_for(page_name_photo, patient_id=patient.id)}"
                    title="patient photo - click to change">
                    { f"""<img src="{get_patient_photo_src(patient)}" alt="Patient Photo" style="width: 150px; height: 150px; margin: auto; display: block; object-fit: cover; border-radius: 5px;">"""
                    if patient.photo else
                    f"""<svg width="150px" height="150px" style="margin: auto; display: block; border-radius: 5px;">
                        <path fill="#ccc" d="M 104.68731,56.689353 C 102.19435,80.640493 93.104981,97.26875 74.372196,97.26875 55.639402,97.26875 46.988823,82.308034 44.057005,57.289941 41.623314,34.938838 55.639402,15.800152 74.372196,15.800152 c 18.732785,0 32.451944,18.493971 30.315114,40.889201 z"></path>
                        <path fill="#ccc" d="M 92.5675 89.6048 C 90.79484 93.47893 89.39893 102.4504 94.86478 106.9039 C 103.9375 114.2963 106.7064 116.4723 118.3117 118.9462 C 144.0432 124.4314 141.6492 138.1543 146.5244 149.2206 L 4.268444 149.1023 C 8.472223 138.6518 6.505799 124.7812 32.40051 118.387 C 41.80992 116.0635 45.66513 113.8823 53.58659 107.0158 C 58.52744 102.7329 57.52583 93.99267 56.43084 89.26926 C 52.49275 88.83011 94.1739 88.14054 92.5675 89.6048 z"></path>
                    </svg>""" }
                </a>

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
                            " ".join(coding.display if coding.display else (coding.code if coding.code else '')
                                     for coding in allergy.code.coding)
                            if allergy.code and allergy.code.coding else "unknown allergy"
                        }</p>""" for allergy in allergies
                    )}
                </div>
                <div>
                    <p>Medications:</p>
                   {"".join(
                        f"""<p>{
                            " ".join(coding.display if coding.display else (coding.code if coding.code else '')
                                     for coding in med.medicationCodeableConcept.coding)
                            if med.medicationCodeableConcept and med.medicationCodeableConcept.coding else "unknown medication"
                        }</p>""" for med in medications
                    )}
                </div>
                <div>
                    <p>Problem list:</p>
                    {"".join(
                        f"""<p>{
                            " ".join(coding.display if coding.display else (coding.code if coding.code else '')
                                     for coding in cond.code.coding)
                            if cond.code and cond.code.coding else "Unknown"
                        }</p>""" for cond in conditions
                    )}
                </div>
                <!--"nobody got time to read immunization history"
                <div>
                    <p>Immunization history:</p>
                    {"".join(
                        f"""<p>{
                            " ".join(coding.display if coding.display else (coding.code if coding.code else '')
                                     for coding in imm.vaccineCode.coding)
                            if imm.vaccineCode and imm.vaccineCode.coding else "unknown medication"
                        }</p>""" for imm in immunizations
                    )}
                </div>
                -->
                <p>lab results</p>
                <p>vitals</p>
                <p>diagnoses</p>
                <p>procedures</p>
                <p>notes</p>
            </nav>
            <div style="flex: 1; display: flex; flex-direction: column; height: 100%;">
                <nav hx-boost="true" hx-indicator="#patient-content" 
                    id="patient-nav" class="color-color2" 
                    style="padding-left: 2px; display: flex; position: relative; border-bottom: 2px solid; line-height: 1.2em;">
                    {tab_link(page_name_overview, "Overview")}
                    {tab_link(page_name_demographics, "Demographics")}
                    {tab_link(page_name_allergy, "Allergies")}
                    {tab_link(page_name_allergy, "Medications")}
                    {tab_link(page_name_immunizations, "Immunization History")}
                </nav>
                <div style="padding: 8px; flex: 1; min-height: 0;">
                    <div id="patient-content"
                    class="htmx-indicator color-color3"
                    style="height: 100%; overflow: auto;">
                        {content}
                    </div>
                </div>
            </div>
        </div>
        """))

def get_patient_photo_src(patient: Patient) -> str | None:
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
        return f"data:{photo.contentType};base64,{photo.data}"
    return None