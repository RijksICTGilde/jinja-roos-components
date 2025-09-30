#!/usr/bin/env python3
"""
FastAPI app for live jinja-roos-components documentation and template rendering.

Installation (from root directory):
    # With Poetry:
    poetry install -E examples
    
    # Or with pip:
    pip install -e ".[examples]"
    
Usage (from root directory):
    poetry run uvicorn examples.fastapi_app:app --reload
    # Or:
    uvicorn examples.fastapi_app:app --reload
    
    Then visit:
    - http://localhost:8000/ - Documentation homepage
    - http://localhost:8000/docs/components - Live components reference
    - http://localhost:8000/docs/colors - Live colors palette  
    - http://localhost:8000/docs/icons - Live icons library
    - http://localhost:8000/docs/spacing - Live spacing & sizing reference
    - http://localhost:8000/render?template=simple-page.html.j2 - Live template rendering
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, DebugUndefined
from jinja_roos_components import setup_components
import os
import sys
sys.path.append(os.path.dirname(__file__))
from docs_service import (
    extract_colors_from_tokens, 
    extract_icons_from_types, 
    extract_spacing_and_sizing,
    get_components_data,
    get_generation_date
)

app = FastAPI()

# Setup Jinja2 environment with templates from templates subfolder
template_dir = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(
    loader=FileSystemLoader(template_dir),
    undefined=DebugUndefined  # This will show helpful debug info for undefined variables
)

# Setup ROOS components
setup_components(env)

# Mount static files for CSS/JS assets at the expected path
css_static_dir = os.path.join(os.path.dirname(__file__), "..", "jinja_roos_components", "static")
if os.path.exists(css_static_dir):
    app.mount("/static/roos", StaticFiles(directory=css_static_dir), name="roos_static")

# Mount documentation static files
docs_static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(docs_static_dir):
    app.mount("/static", StaticFiles(directory=docs_static_dir), name="docs_static")

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

@app.get("/docs/colors", response_class=HTMLResponse)
async def docs_colors():
    """Live colors documentation."""
    try:
        colors = extract_colors_from_tokens()
        template = env.get_template("docs-colors.html.j2")
        html = template.render(
            colors=colors,
            generation_date=get_generation_date()
        )
        return HTMLResponse(content=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/docs/icons", response_class=HTMLResponse)
async def docs_icons():
    """Live icons documentation."""
    try:
        icons = extract_icons_from_types()
        template = env.get_template("docs-icons.html.j2")
        html = template.render(
            icons=icons,
            generation_date=get_generation_date()
        )
        return HTMLResponse(content=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/docs/spacing", response_class=HTMLResponse)
async def docs_spacing():
    """Live spacing and sizing documentation."""
    try:
        spacing_sizing = extract_spacing_and_sizing()
        template = env.get_template("docs-spacing.html.j2")
        html = template.render(
            spacing=spacing_sizing['spacing'],
            sizing=spacing_sizing['sizing'],
            generation_date=get_generation_date()
        )
        return HTMLResponse(content=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/docs/components", response_class=HTMLResponse)
async def docs_components():
    """Live components documentation."""
    try:
        components = get_components_data()
        
        # Process examples through Jinja to render actual components
        for component in components:
            if component.get('example') and component.get('allow_preview', True):
                try:
                    example_template = env.from_string(component['example'])
                    component['rendered_example'] = example_template.render()
                except Exception as e:
                    # If example fails to render, show a simple fallback
                    component['rendered_example'] = f'<p style="color: red; font-size: 0.9rem;">⚠️ Example not available: {component["name"]} component</p>'
            else:
                if not component.get('allow_preview', True):
                    component['rendered_example'] = f'<p style="color: #666; font-style: italic;">Preview not available for {component["name"]} component (generates full page structure)</p>'
                else:
                    component['rendered_example'] = f'<p style="color: #666;">No example available for {component["name"]}</p>'
        
        template = env.get_template("docs-components.html.j2")
        html = template.render(
            components=components,
            generation_date=get_generation_date()
        )
        return HTMLResponse(content=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the examples index page with live documentation links."""
    try:
        # Try to render a custom homepage template if it exists
        template = env.get_template("docs-home.html.j2")
        html = template.render(generation_date=get_generation_date())
        return HTMLResponse(content=html)
    except TemplateNotFound:
        # Fallback to dynamic homepage
        templates = [f for f in os.listdir(template_dir) if f.endswith('.j2') and not f.startswith('docs-')]
        template_links = [f'<li><a href="/render?template={t}">{t}</a></li>' for t in templates]
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ROOS Components Documentation</title>
            <link rel="stylesheet" href="/static/roos/dist/roos.css">
        </head>
        <body>
        <div style="max-width: 1200px; margin: 0 auto; padding: 2rem;">
            <h1 style="color: #01689b; margin-bottom: 2rem;">ROOS Components Documentation</h1>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-bottom: 3rem;">
                <div style="background: white; border: 1px solid #e1e4e8; border-radius: 8px; padding: 2rem;">
                    <h2 style="color: #01689b; margin-bottom: 1rem;">📖 Live Documentation</h2>
                    <p style="color: #666; margin-bottom: 1.5rem;">Browse the complete design system with live examples.</p>
                    <ul style="list-style: none; padding: 0;">
                        <li style="margin: 0.5rem 0;"><a href="/docs/components" style="color: #01689b; text-decoration: none; font-weight: 500;">🧩 Components Reference</a></li>
                        <li style="margin: 0.5rem 0;"><a href="/docs/colors" style="color: #01689b; text-decoration: none; font-weight: 500;">🎨 Colors Palette</a></li>
                        <li style="margin: 0.5rem 0;"><a href="/docs/icons" style="color: #01689b; text-decoration: none; font-weight: 500;">🔸 Icons Library</a></li>
                        <li style="margin: 0.5rem 0;"><a href="/docs/spacing" style="color: #01689b; text-decoration: none; font-weight: 500;">📏 Spacing & Sizing</a></li>
                    </ul>
                </div>
                
                <div style="background: white; border: 1px solid #e1e4e8; border-radius: 8px; padding: 2rem;">
                    <h2 style="color: #01689b; margin-bottom: 1rem;">🚀 Live Examples</h2>
                    <p style="color: #666; margin-bottom: 1.5rem;">See components in action with real templates.</p>
                    <ul style="list-style: none; padding: 0;">
                        {''.join(template_links)}
                    </ul>
                </div>
            </div>
            
            <footer style="text-align: center; color: #666; padding-top: 2rem; border-top: 1px solid #e1e4e8;">
                <p>ROOS Components v0.1.0 • Generated {get_generation_date()}</p>
            </footer>
        </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html)

# Documentation is now served from static files at /static/
# No need for specific endpoints - FastAPI's StaticFiles handles it automatically