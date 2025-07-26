def base_nav(content: str):
    """every page shows this nav bar on top
    it links to /, registerPatient, calendar, settings,
    and implements searchPatient"""
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

        <form id="search-patient-form"
            hx-post="/searchPatient"
            hx-target="#search-results"
            hx-indicator="#search-patient-container"
            hx-sync="this:replace"
            hx-trigger="input delay:300ms, input from:#search-birthdate">
            <div id="search-fields" style="display: flex; flex-wrap: wrap; column-gap: 30px;">
                <div>
                    <label for="search-name">Name:</label>
                    <input type="text" name="search_name" id="search-name" placeholder="Name">
                </div>
                <div>
                    <label for="search-id">MRN:</label>
                    <input type="text" name="search_id" id="search-id" placeholder="MRN">
                </div>
                <div>
                    <label for="search-birthdate">Birth Date:</label>
                    <input type="date" name="search_birthdate" id="search-birthdate">                 
                </div>
                <div>
                    <label for="search-email">Email:</label>
                    <input type="email" name="search_email" id="search-email" placeholder="Email">
                </div>
                <div>
                    <label for="search-phone">Phone:</label>
                    <input type="tel" name="search_phone" id="search-phone" placeholder="Phone">
                </div>
            </div>
        </form>
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
async def searchPatient(
    search_name: str = Form(''),
    search_id: str = Form(''),
    search_birthdate: str = Form(''),
    search_email: str = Form(''),
    search_phone: str = Form('')):
    if not (search_name or search_id or search_birthdate or search_email or search_phone):
        return "" #empty form
    
    search_params = {}
    if search_name:
        search_params['name'] = search_name
    if search_id:
        search_params['_id'] = search_id
    if search_birthdate:
        search_params['birthdate'] = search_birthdate
    if search_email:
        search_params['email'] = search_email
    if search_phone:
        search_params['phone'] = search_phone

    print(search_params)
    resources = client.resources('Patient')  # Return lazy search set
    resources = resources.search(**search_params).limit(10)

    # Fetch resources asynchronously without blocking the event loop
    patients = await resources.fetch()  # Returns list of AsyncFHIRResource

    error_fields = f"""
        {f'Name={search_name},' if search_name else ''}
        {f'MRN={search_id},' if search_id else ''}
        {f'Birth Date={search_birthdate},' if search_birthdate else ''}
        {f'Email={search_email},' if search_email else ''}
        {f'Phone={search_phone},' if search_phone else ''}
    """
    error_fields = error_fields[:-1] #remove trailing comma, probably better ways oh well
    if len(patients) == 0:
        return f'<div style="padding: 4px;">No results found for {error_fields}</div>'
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
            resp += f"<tr><td colspan='3'>Error searching {error_fields}</td></tr>"
    resp += "</tbody></table></div>"
    return resp