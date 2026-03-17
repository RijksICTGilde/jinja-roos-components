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

from jinja2 import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment
from jinja_roos_components.extension import setup_components
from jinja_roos_components.registry import ComponentRegistry

app = FastAPI(title="ROOS Storybook Render API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Jinja2 environment once at startup (sandboxed for safety)
templates_dir = Path(__file__).resolve().parent.parent / "src" / "jinja_roos_components" / "templates"
jinja_env = SandboxedEnvironment(loader=FileSystemLoader(str(templates_dir)))
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


# Attributes that contain component markup and must not be escaped
HTML_CONTENT_ATTRS = frozenset({"footer", "content"})


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

    # Pre-render any HTML content attributes that contain <c-*> component tags
    has_component_attrs = any(
        key in HTML_CONTENT_ATTRS and isinstance(value, str) and "<c-" in value
        for key, value in req.attrs.items()
    )

    if has_component_attrs:
        # Render directly via the component template to avoid quote-escaping issues
        context = {}
        for key, value in req.attrs.items():
            if key in HTML_CONTENT_ATTRS and isinstance(value, str) and "<c-" in value:
                # Pre-render component markup in this attribute
                sanitized = strip_template_syntax(value)
                tpl = jinja_env.from_string(sanitized)  # nosec B703
                context[key] = tpl.render()
            else:
                context[key] = value
        # Add content as the 'content' key
        if req.content:
            content = strip_template_syntax(req.content)
            if "<c-" in content:
                tpl = jinja_env.from_string(content)  # nosec B703
                context["content"] = tpl.render()
            else:
                context["content"] = content
        # Render the component template directly with _component_context
        template = jinja_env.get_template(f"components/{req.component}.html.j2")
        html = template.render(_component_context=context)
    else:
        # Standard path: build <c-*> tag string for the preprocessor
        attrs_str = ""
        for key, value in req.attrs.items():
            if isinstance(value, bool):
                attrs_str += f' {key}="{str(value).lower()}"'
            elif value is not None and value != "":
                attrs_str += f' {key}="{escape_attr(value)}"'

        content = strip_template_syntax(req.content) if req.content else ""

        if content:
            template_str = f"<c-{req.component}{attrs_str}>{content}</c-{req.component}>"
        else:
            template_str = f"<c-{req.component}{attrs_str} />"

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
