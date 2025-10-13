"""
Jinja ROOS Components - Modern, self-contained Jinja2 component library.

This package provides a complete component system for Jinja2 templates with:
- Custom component syntax (e.g., <c-button variant="primary">Click me</c-button>)
- Built-in CSS, JavaScript, and asset management
- Type-safe component validation
- Easy integration with FastAPI, Flask, and other frameworks
"""

from .extension import ComponentExtension, setup_components
from .extension_dom import ComponentExtensionDOM, setup_components_dom
from .registry import ComponentRegistry

__version__ = "0.1.0"
__all__ = ["ComponentExtension", "setup_components", "ComponentRegistry", "ComponentExtensionDOM", "setup_components_dom"]


def get_static_files_path() -> str:
    """Get the path to static files for serving assets."""
    import os
    return os.path.join(os.path.dirname(__file__), "static")


def get_templates_path() -> str:
    """Get the path to component templates."""
    import os
    return os.path.join(os.path.dirname(__file__), "templates")