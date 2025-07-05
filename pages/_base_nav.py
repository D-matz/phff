def base_nav(content: str):
    """every page shows this nav bar on top"""
    return f"""
    <!DOCTYPE html>
    <html lang="en" style="height: 100%; margin: 0; padding: 0;">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>PotatoEMR</title>
            <link rel="icon" href="data:image/svg+xml,&lt;svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'&gt;&lt;text y='1em' font-size='80'&gt;🥔&lt;/text&gt;&lt;/svg&gt;">
            <script src="/static/htmx.js"></script>
            <script src="/static/form-json.js"></script>
            <script src="/static/setSystemAndValue.js"></script>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                }}
            </style>
        </head>
        <body style="height: 100%; margin: 0; padding: 0;display: flex; flex-direction: column; overscroll-behavior: none;">
            <nav style="padding: 2px;">
                <a href="/">Home</a>
                <input type="text" id="search" name="query" placeholder="patient search"
                    hx-post="/searchPatient"
                    hx-trigger="input changed delay:300ms, keyup[key=='Enter']"
                    hx-target="#search-results"
                    hx-indicator="#loading"
                    hx-sync="this:replace">
                <a href="/registerPatient">Register Patient</a>
                <a href="/calendar">Calendar</a>
                <a href="/settings">Settings</a>
            </nav>
            <div id="loading" class="htmx-indicator">Loading...</div>
            <div>
                <table>
                    <thead>
                    <tr>
                    <th>Id</th>
                    <th>Name</th>
                    <th>Birthdate</th>
                    </tr>
                    </thead>
                    <tbody id="search-results"></tbody>
                </table>
            </div>
            <div style="flex: 1; background-color: red; overflow: auto;">
                {content}
            </div>
        </body>
    </html>
    """