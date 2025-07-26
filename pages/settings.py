from fhirpy import AsyncFHIRClient
from enum import Enum
from app import app
from pages._base_nav import base_nav
from pydantic import BaseModel, Field

class FHIRServers(Enum):
    HAPI = "https://hapi.fhir.org/baseR4/"
    SMART_HEALTH_IT = "https://r4.smarthealthit.org/"
    FIRELY = "https://server.fire.ly"

client = AsyncFHIRClient(
    FHIRServers.SMART_HEALTH_IT.value,
    authorization='Bearer TOKEN',
)

class SettingsModel(BaseModel):
    fhir_server: str = Field(..., description="FHIR server URL")

@app.get("/settings", name="settings")
async def settings_get():
    return settings_page()

@app.post("/settings", name="settings")
async def settings_post(settings: SettingsModel):
    client.url = settings.fhir_server
    print(f"FHIR server changed to: {client.url}")
    return settings_page()

def settings_page():
    return base_nav(f"""
    <div style="margin: 16px">
        <h1>Settings</h1>
        <form style="padding: 16px;"
            hx-ext="form-json"
            hx-trigger="change"
            hx-post="/settings"
            hx-target="body"
            hx-swap="innerHTML">
            <label for="fhir_server">FHIR Server:</label>
            <select id="fhir_server" name="fhir_server">
                {''.join(f'<option value="{server.value}"{" selected" if server.value == client.url else ""}>{server.value}</option>'
                for server in FHIRServers)}
            </select>
        </form>
    </div>""")


