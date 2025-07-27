from app import app, FHIRServers
from pages._base_nav import base_nav
from pydantic import BaseModel, Field
from os import listdir
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Form
from starlette.responses import RedirectResponse

@app.get("/settings", name="settings")
async def settings_get(request: Request):
    return base_nav(request, f"""
    <div style="margin: 16px">
        <h1>Settings</h1>
        <form style="padding: 16px;"
            method="post"
            action="/settings"
            onchange="this.submit()">
            {''.join(f"""
            <div>
                <label for="{cookieName}">{cookie_list[cookieName]['label']}</label>
                <select id="{cookieName}" name="{cookieName}">
                    {''.join(f'<option value="{cookie_opt}"{" selected" if cookie_opt == request.cookies[cookieName] else ""}>{cookie_opt}</option>'
                    for cookie_opt in cookie_list[cookieName]['opts'])}
                </select>
            </div>
            """ 
            for cookieName in cookie_list.keys())}
        </form>
    </div>""")

@app.post("/settings", name="settings_post")
async def settings_post(
    request: Request,
    fhir_server_url: str = Form(None),
    css_colors_filename: str = Form(None)):
    
    response = RedirectResponse(url="/settings", status_code=303)
    
    if fhir_server_url:
        response.set_cookie(
            key="fhir_server_url", 
            value=fhir_server_url,
            max_age=60*60*24*360,
            httponly=True,
        )
    
    if css_colors_filename:
        response.set_cookie(
            key="css_colors_filename", 
            value=css_colors_filename,
            max_age=60*60*24*360,
            httponly=True,
        )
    
    return response

app_dir = Path(__file__).parent.parent
colors_dir = app_dir / "static" / "colors"
css_colors_filename_list = [f.removesuffix('.css') for f in listdir(colors_dir)]
css_colors_filename_list.sort()

server_list = [s.value for s in list(FHIRServers)]
server_list.sort()

cookie_list = {
    "fhir_server_url": {
        'opts': server_list,
        'label': "FHIR Server",
    },
    "css_colors_filename": {
        'opts': css_colors_filename_list,
        'label': 'Color Theme',
    },
}