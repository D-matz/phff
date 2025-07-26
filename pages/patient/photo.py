from app import app
from pages.settings import client
from pages.patient._base_patient import base_patient_nav, get_all_resources, page_name_photo
from resources import Patient, Attachment
from fhirpy.base.exceptions import OperationOutcome
import html
import json

@app.get("/patient/{patient_id}/photo", name=page_name_photo)
async def patient_photo_get(patient_id: str):
    all_resources = await get_all_resources(patient_id)
    patient: Patient = all_resources.patient
    return base_patient_nav(all_resources, photo_form(patient), page_name_photo)


@app.post("/patient/{patient_id}/photo", name="patient_photo_post")
async def patient_photo_post(patient_id: str, patient: Patient):
    if not patient.photo: return "weird patient/patient_id/photo should always post a photo"
    new_photo = patient.photo.pop()
    patient.photo.insert(0, new_photo)
    #move new photo to beginning of list
    #just because our convention is to use photo[0] for profile
    #so the photo user just submitted will show up as profile pic
    fhirpy_patient = client.resource('Patient', **patient.model_dump(mode='json'))
    errors = None
    try:
        await fhirpy_patient.update()
    except OperationOutcome as e:
        errors = get_html_response_simple(e)
    #we might get a 413 file too large error on user's image
    #in that case for error message, pass on fhir server's html response in an iframe
    all_resources = await get_all_resources(patient_id)
    ret_patient: Patient = all_resources.patient
    return base_patient_nav(all_resources, photo_form(ret_patient, errors=errors), page_name_photo)

@app.post("/patient/{patient_id}/photo/choose/{photo_index}", name="patient_photo_choose")
async def patient_photo_choose(patient_id: str, photo_index: int):
    """
    sets photo at chosen index to go to index 0
    which for _base_patient purposes makes it profile pic
    """
    all_resources = await get_all_resources(patient_id)
    patient: Patient = all_resources.patient
    if not patient.photo: return "weird you should not be able to post to patient photo choose if the patient has zero photos"
    #might be more clever to add patient resource to posted form
    #to save this await fhir server request to get patient
    chosen_photo = patient.photo.pop(photo_index)  # Remove and get item at index 3
    patient.photo.insert(0, chosen_photo) 
    fhirpy_patient = client.resource('Patient', **patient.model_dump(mode='json'))
    await fhirpy_patient.update()
    all_resources = await get_all_resources(patient_id)
    patient: Patient = all_resources.patient
    return base_patient_nav(all_resources, photo_form(patient), page_name_photo)

def photo_form(patient: Patient, errors: str | None = None) -> str:
    photo = None
    if patient.photo:
        photo = patient.photo[0].url if len(patient.photo) > 0 else None

    lines = []
    lines.append(f"""

<style>
.grow-hover {{ transition: transform 0.2s ease-in-out; }}
.grow-hover:hover {{ transform: scale(1.05); }}
</style>

    <div id="photo-container" class="htmx-indicator">
        <script src="/static/setAttachmentFromFile.js"></script>
        <form id="photo-form"
            data-formjsondefault='{html.escape(json.dumps(patient.model_dump(mode='json')))}'
            hx-ext="form-json"
            hx-post="{app.url_path_for("patient_photo_post", patient_id=patient.id)}" 
            hx-target="body" 
            hx-swap="outerHTML"
            hx-indicator="#photo-container">
        """)
    #hidden inputs with existing photo list
    if patient.photo:
        for index, photo in enumerate(patient.photo):
            lines.append(f"""
            <input type="hidden" name="photo[{index}].contentType" value="{photo.contentType if photo.contentType else ''}">
            <input type="hidden" name="photo[{index}].data" value="{photo.data if photo.data else ''}">
            """)
    #hidden input with new photo content/data, set by photo-input setAttachmentFromFile
    new_photo_number = len(patient.photo) if patient.photo else 0
    lines.append(f"""
            <input id="photo-contentType" type="hidden" name="photo[{new_photo_number}].contentType">
            <input id="photo-data" type="hidden" name="photo[{new_photo_number}].data">
        </form>
        
        <div class="color-color3-hover" style="border: dashed 2px; width: fit-content; padding: 4px;">
            <label for="photo-input" style="cursor: pointer; display: block;">
                Patient Photo<br>
                drag file from computer<br>
                or click choose file
            </label>
            <input type="file" id="photo-input" accept="image/*" style="cursor: pointer"
                onchange="setAttachmentFromFile(this,
                    document.getElementById('photo-contentType'),
                    document.getElementById('photo-data'),
                    document.getElementById('photo-form'));">
            <!--note that this input is outside of the form,
            but setting it sets data/contentType in the form,
            and submits the form-->
        </div>
        <script src="/static/drop-file.js" onload="initDropZone('photo-input', 'main-content')"></script>

        {f"""<iframe src="data:text/html,{errors}" style="border: none;" width="300" height="200"></iframe>""" if errors else ''}

        """)
    if patient.photo:
        lines.append('<div style="display: flex; flex-wrap: wrap; gap: 10px; padding: 20px;">')
        for index, photo in enumerate(patient.photo):
            lines.append(f"""
            <img src="{get_photo_src(photo)}" alt="Patient Photo" style="width: 200px; height: 200px; object-fit: contain; cursor: pointer;"
            title="photo {index} - click to set as profile picture" class="grow-hover"
            hx-trigger="click"
            hx-push-url="false"
            hx-post="{app.url_path_for("patient_photo_choose", patient_id=patient.id, photo_index=index)}" 
            hx-target="body" 
            hx-swap="outerHTML"
            hx-indicator="#photo-container">
            """)
        lines.append('</div>')
    else:
        lines.append(f"<p>no photos uploaded</p>")
    lines.append('</div>')
    return "".join(lines)


def get_photo_src(photo: Attachment) -> str | None:
    """
    Convert patient photo to appropriate src string using FHIR Attachment
    Returns URL if available, otherwise base64 data URL, or None if no photo
    """
    if photo.url and photo.url.strip():
        return photo.url
    if photo.data and len(photo.data) > 0 and photo.contentType and photo.contentType.strip():
        return f"data:{photo.contentType};base64,{photo.data}"
    return None


def get_html_response_simple(operation_outcome: OperationOutcome):
    """
    Get error without trying to detect if it's html or not
    return diagnostics first, then div, then whole resource
    """
    resource = operation_outcome.resource
    issues = resource.get("issue", [])
    if issues:
        diagnostics = issues[0].get("diagnostics")
        if diagnostics:
            return diagnostics
    div_content = resource.get("text", {}).get("div")
    if div_content:
        return div_content
    return json.dumps(resource, indent=2)