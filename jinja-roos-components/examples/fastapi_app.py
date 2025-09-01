#!/usr/bin/env python3
"""
Minimal FastAPI app to render jinja-roos-components templates.

Installation (from root directory):
    # With Poetry:
    poetry install -E examples
    
    # Or with pip:
    pip install -e ".[examples]"
    
Usage (from root directory):
    poetry run uvicorn examples.fastapi_app:app --reload
    # Or:
    uvicorn examples.fastapi_app:app --reload
    
    Then visit: http://localhost:8000/render?template=simple-page.html.j2
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from jinja_roos_components import setup_components
import os

app = FastAPI()

# Setup Jinja2 environment with templates from templates subfolder
template_dir = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(template_dir))

# Setup ROOS components
setup_components(env)

# Mount static files for CSS/JS assets at the expected path
static_dir = os.path.join(os.path.dirname(__file__), "..", "jinja_roos_components", "static")
if os.path.exists(static_dir):
    app.mount("/static/roos", StaticFiles(directory=static_dir), name="static")

@app.get("/render", response_class=HTMLResponse)
async def render_template(template: str = Query(..., description="Template name from templates folder")):
    """Render a template from the templates folder."""
    try:
        tmpl = env.get_template(template)
        html = tmpl.render()
        return HTMLResponse(content=html)
    except TemplateNotFound:
        raise HTTPException(status_code=404, detail=f"Template '{template}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the examples index page."""
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        # Fallback to simple template list
        templates = [f for f in os.listdir(template_dir) if f.endswith('.j2')]
        links = [f'<li><a href="/render?template={t}">{t}</a></li>' for t in templates]
        html = f"""
        <html>
        <head><title>Available Templates</title></head>
        <body>
            <h1>Available Templates</h1>
            <ul>{''.join(links)}</ul>
        </body>
        </html>
        """
        return HTMLResponse(content=html)

@app.get("/component-reference", response_class=HTMLResponse)
@app.get("/component-reference.html", response_class=HTMLResponse)
async def component_reference():
    """Serve the component reference documentation."""
    ref_path = os.path.join(os.path.dirname(__file__), "component-reference.html")
    if os.path.exists(ref_path):
        with open(ref_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(content="<h1>Component reference not found</h1><p>Run: <code>poetry run python scripts/generate_component_docs.py</code></p>", status_code=404)