"""
Storybook render API - renders Jinja2 components on demand.

Usage:
    uvicorn storybook.render_api:app --port 8100
"""

import re
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure the src directory is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from jinja2 import Environment, FileSystemLoader
from jinja_roos_components.extension import setup_components
from jinja_roos_components.registry import ComponentRegistry

app = FastAPI(title="ROOS Storybook Render API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Jinja2 environment once at startup
templates_dir = Path(__file__).resolve().parent.parent / "src" / "jinja_roos_components" / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))
setup_components(jinja_env, static_url_prefix="/static/roos/dist/")

# Registry for definitions endpoint + allowlist validation
registry = ComponentRegistry()
ALLOWED_COMPONENTS = frozenset(registry.get_all_component_names())

# Valid attribute name pattern
ATTR_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")


class RenderRequest(BaseModel):
    component: str
    attrs: dict[str, Any] = {}
    content: str = ""


class RenderResponse(BaseModel):
    html: str
    source: str = ""


def build_source(component: str, attrs: dict[str, Any], content: str) -> str:
    """Build the Jinja2 source code for display."""
    attrs_str = ""
    for key, value in attrs.items():
        if isinstance(value, bool):
            if value:
                attrs_str += f' {key}="{str(value).lower()}"'
        elif value is not None and value != "":
            attrs_str += f' {key}="{value}"'

    if content:
        return f"<c-{component}{attrs_str}>{content}</c-{component}>"
    return f"<c-{component}{attrs_str} />"


def escape_attr(value: str) -> str:
    """Escape attribute value for safe inclusion in HTML."""
    return str(value).replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def strip_template_syntax(value: str) -> str:
    """Remove Jinja2 template syntax to prevent SSTI."""
    return value.replace("{{", "").replace("}}", "").replace("{%", "").replace("%}", "")


@app.post("/api/render", response_model=RenderResponse)
def render_component(req: RenderRequest):
    """Render a Jinja2 component and return the HTML + source."""
    # Validate component name against registry allowlist
    if req.component not in ALLOWED_COMPONENTS:
        raise HTTPException(status_code=400, detail=f"Unknown component: {req.component}")

    # Validate attribute names
    for key in req.attrs:
        if not ATTR_NAME_RE.match(key):
            raise HTTPException(status_code=400, detail=f"Invalid attribute name: {key}")

    source = build_source(req.component, req.attrs, req.content)

    # Build template string with escaped values
    attrs_str = ""
    for key, value in req.attrs.items():
        if isinstance(value, bool):
            attrs_str += f' {key}="{str(value).lower()}"'
        elif value is not None and value != "":
            attrs_str += f' {key}="{escape_attr(value)}"'

    # Strip any Jinja2 template syntax from content to prevent SSTI
    content = strip_template_syntax(req.content) if req.content else ""

    if content:
        template_str = f"<c-{req.component}{attrs_str}>{content}</c-{req.component}>"
    else:
        template_str = f"<c-{req.component}{attrs_str} />"

    # Safe: component name is validated against allowlist, attrs are escaped,
    # content is stripped of template syntax. from_string is needed because
    # the component extension preprocesses <c-*> tags at parse time.
    template = jinja_env.from_string(template_str)  # nosec B703
    html = template.render()
    return RenderResponse(html=html, source=source)


@app.get("/api/definitions")
def get_definitions():
    """Return all component definitions for story generation."""
    result = {}
    for name in registry.get_all_component_names():
        meta = registry.get_component_metadata(name)
        if meta:
            result[name] = meta
    return result
