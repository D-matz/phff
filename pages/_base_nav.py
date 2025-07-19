def base_nav(content: str):
    """every page shows this nav bar on top"""
    return f"""
    <!DOCTYPE html>
    <html lang="en" style="height: 100%; margin: 0; padding: 0;">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="htmx-config" content='{{"includeIndicatorStyles": false}}'>
            <title>PotatoEMR</title>
            <link rel="icon" href="data:image/svg+xml,&lt;svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'&gt;&lt;text y='1em' font-size='80'&gt;🥔&lt;/text&gt;&lt;/svg&gt;">
            <link rel="stylesheet" href="/static/colors.css">
            <link rel="stylesheet" href="/static/style.css">
            <script src="/static/htmx.js"></script>
            <script src="/static/form-json.js"></script>
            <script src="/static/setSystemAndCode.js"></script>
            <script src="/static/dragElt.js"></script>
        </head>
        <body style="height: 100%; margin: 0; padding: 0;display: flex; flex-direction: column;">
            <nav hx-boost="true" id="main-nav" class="color-color1"
            style="display: flex; padding: 4px; position: relative; border-bottom: 2px solid; line-height: 1.2em; gap: 0.5em;">
                <a href="/">PotatoEMR🥔</a>


    <details style="position:relative;">
      <summary style="cursor:pointer; list-style:none; text-decoration: underline;">Search Patient</summary>
      <div class="color-color1" style="position:absolute; z-index: 1; border:8px solid; padding: 4px;">

<input type="text" id="search" name="query" placeholder="patient search"
                    hx-post="/searchPatient"
                    hx-trigger="input changed delay:300ms, keyup[key=='Enter']"
                    hx-target="#search-results"
                    hx-indicator="#search-patient-container"
                    hx-sync="this:replace">
                <div id="search-patient-container" class="htmx-indicator" style="width: 700px; height: 260px">
                    <div id="search-results"></div>
                </div>

      </div>
    </details>
                <a href="/registerPatient">Register Patient</a>
                <a href="/calendar">Calendar</a>
                <a href="/settings">Settings</a>
            </nav>
            <div id="main-content" class="color-color3" style="flex: 1; overflow: auto;">
                {content}
            </div>
        </body>
    </html>
    """


from app import app
from pages.settings import client
from test.resources import Patient
from fastapi import Form

@app.post("/searchPatient", name="searchPatient")
async def searchPatient(query: str = Form(...)):
    if query == "":
        return ""

    resources = client.resources('Patient')  # Return lazy search set
    resources = resources.search(name=query).limit(10)

    # Fetch resources asynchronously without blocking the event loop
    patients = await resources.fetch()  # Returns list of AsyncFHIRResource

    if len(patients) == 0:
        return f'<div style="padding: 4px;">No results found for {query}</div>'
    resp = """<div style="padding: 4px;">
                <table>
                    <tbody id="search-results">"""
    for fhirpy_patient in patients:
        try:
            patient_resource = Patient.model_validate(fhirpy_patient.serialize())
            resp += f"""
            <tr
            style="cursor: pointer;"
            hx-get="/patient/{patient_resource.id}/overview"
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
    resp += "</tbody></table></div>"
    return resp