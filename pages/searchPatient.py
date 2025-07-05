from app import app, client
from fhir.resources.R4B.patient import Patient
from fastapi import Form

@app.post("/searchPatient", name="searchPatient")
async def searchPatient(query: str = Form(...)):
    print("search for " + query)

    if query == "":
        return "<tr><td colspan='3'>Empty query</td></tr>"

    resources = client.resources('Patient')  # Return lazy search set
    resources = resources.search(name=query).limit(10)

    # Fetch resources asynchronously without blocking the event loop
    patients = await resources.fetch()  # Returns list of AsyncFHIRResource

    if len(patients) == 0:
        return f"<tr><td colspan='3'>No results found for {query}</td></tr>"
    resp = ""
    for fhirpy_patient in patients:
        try:
            patient_resource = Patient.model_validate(fhirpy_patient.serialize())
            resp += f"""
            <tr hx-get="/patient/{patient_resource.id}/overview"
            hx-target="body"
            hx-swap="innerHTML"
            hx-push-url="true">
                <td>{patient_resource.id}</td>
                <td>{patient_resource.name[0].family} {patient_resource.name[0].given}</td>
                <td>{patient_resource.birthDate}</td>
            </tr>
            """
        except Exception as ex:
            print(ex, fhirpy_patient.serialize())
            resp += f"<tr><td colspan='3'>Error searching {query}</td></tr>"
    return resp