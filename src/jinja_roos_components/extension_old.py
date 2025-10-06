"""
Jinja2 Component Extension for ROOS Components.

This extension provides custom component syntax preprocessing, transforming
component tags like <c-button variant="primary">Click me</c-button> into
standard Jinja2 includes with proper context and validation.
"""

import re
from typing import Any, Dict, Optional
from jinja2 import Environment
from jinja2.ext import Extension

from .registry import ComponentRegistry


class ComponentExtension(Extension):
    """
    Jinja2 extension that preprocesses component syntax.
    
    Transforms custom component tags into standard Jinja2 includes:
    <c-button variant="primary">Click me</c-button>
    -> {% include "components/button.html.j2" with context %}
    """
    
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)
        self.registry = ComponentRegistry()
        
        # Regex pattern for component tags
        # Matches: <c-componentname attr="value" :attr="value" @event="handler">content</c-componentname>
        # Updated to support hyphens in component names
        self.component_pattern = re.compile(
            r'<c-([\w-]+)([^>]*?)(?:/>|>(.*?)</c-\1>)',
            re.DOTALL | re.MULTILINE
        )
        
        # Patterns for different attribute types
        self.attr_patterns = {
            'string': re.compile(r'(\w+)="([^"]*)"'),  # attr="value"
            'binding': re.compile(r':(\w+)="([^"]*)"'),  # :attr="value" (dynamic)
            'event': re.compile(r'@(\w+)="([^"]*)"'),  # @event="handler"
        }

    def preprocess(self, source: str, name: str, filename: Optional[str] = None) -> str:
        """
        Preprocess the template source to convert component syntax to Jinja2 includes.
        
        Args:
            source: The template source code
            name: Template name
            filename: Template filename (optional)
            
        Returns:
            Processed template source with components converted to includes
        """
        def replace_component(match: re.Match[str]) -> str:
            component_name = match.group(1)
            attrs_str = match.group(2) if match.group(2) else ""
            content = match.group(3) if match.group(3) else ""
            
            # Check if component exists
            if not self.registry.has_component(component_name):
                raise ValueError(f"Unknown component: c-{component_name}")
            
            # Parse attributes
            attrs = self._parse_attributes(attrs_str)
            
            # Process nested components in content first
            if content and content.strip():
                # Recursively process nested components
                processed_content = self.component_pattern.sub(replace_component, content.strip())
                # Store content as a special attribute that will be handled differently
                attrs['_raw_content'] = processed_content
            
            # Get component metadata for validation
            component_meta = self.registry.get_component(component_name)
            if component_meta:
                # Validate attributes (basic validation)
                self._validate_attributes(component_name, attrs, component_meta)
            
            # Build the include statement
            return self._build_include(component_name, attrs)
        
        return self.component_pattern.sub(replace_component, source)
    
    def _parse_attributes(self, attrs_str: str) -> Dict[str, Any]:
        """Parse component attributes from the attribute string."""
        attrs = {}
        
        # Parse binding attributes first: :attr="value" (these are evaluated as expressions)
        for match in self.attr_patterns['binding'].finditer(attrs_str):
            key, value = match.groups()
            attrs[f":{key}"] = value  # Prefix with : to indicate binding
        
        # Parse event attributes: @event="handler"
        for match in self.attr_patterns['event'].finditer(attrs_str):
            key, value = match.groups()
            attrs[f"@{key}"] = value  # Prefix with @ to indicate event
        
        # Remove binding and event attributes from string to avoid double-parsing
        clean_attrs_str = attrs_str
        for match in self.attr_patterns['binding'].finditer(attrs_str):
            clean_attrs_str = clean_attrs_str.replace(match.group(0), '')
        for match in self.attr_patterns['event'].finditer(attrs_str):
            clean_attrs_str = clean_attrs_str.replace(match.group(0), '')
        
        # Parse remaining string attributes: attr="value"
        for match in self.attr_patterns['string'].finditer(clean_attrs_str):
            key, value = match.groups()
            attrs[key] = value
            
        return attrs
    
    def _validate_attributes(self, component_name: str, attrs: Dict[str, Any], 
                           component_meta: Dict[str, Any]) -> None:
        """Basic attribute validation against component metadata."""
        # This is a placeholder for more sophisticated validation
        # In a full implementation, you'd validate:
        # - Required attributes are present
        # - Attribute types are correct
        # - Enum values are valid
        # - Custom validation rules
        pass
    
    def _build_include(self, component_name: str, attrs: Dict[str, Any]) -> str:
        """Build the Jinja2 include statement from component name and attributes."""
        template_path = f"components/{component_name}.html.j2"
        
        if not attrs:
            return f'{{% set _component_context = {{}} %}}{{% include "{template_path}" with context %}}'
        
        # Extract raw content if present
        raw_content = attrs.pop('_raw_content', None)
        
        # Build context dictionary
        context_items = []
        for key, value in attrs.items():
            if key.startswith(':'):
                # Binding attribute - use the expression directly
                clean_key = key[1:]  # Remove the : prefix
                # Wrap in quotes to make it a valid Python expression
                if value in ['true', 'false']:
                    # Boolean values
                    context_items.append(f'"{clean_key}": {value.capitalize()}')
                else:
                    # Other expressions - pass through
                    context_items.append(f'"{clean_key}": {value}')
            elif key.startswith('@'):
                # Event attribute - pass as string
                context_items.append(f"'{key}': \"{value}\"")
            else:
                # Regular string attribute
                # Escape quotes in the value
                escaped_value = value.replace('"', '\\"')
                context_items.append(f'"{key}": "{escaped_value}"')  # Quote the key!
        
        # Handle raw content separately using capture block
        if raw_content:
            context_str = ', '.join(context_items) if context_items else ''
            # Use capture to avoid escaping issues with content
            # Generate a unique variable name to avoid conflicts with nested components
            import random
            import string
            var_suffix = ''.join(random.choices(string.ascii_lowercase, k=8))
            capture_var = f'_captured_content_{var_suffix}'
            
            content_part = f'"content": {capture_var}'
            full_context = context_str + (", " if context_str else "") + content_part
            return (f'{{% set {capture_var} %}}{raw_content}{{% endset %}}'
                   f'{{% set _component_context = {{{full_context}}} %}}'
                   f'{{% include "{template_path}" with context %}}')
        else:
            context_str = ', '.join(context_items)
            return f'{{% set _component_context = {{{context_str}}} %}}{{% include "{template_path}" with context %}}'


def setup_components(
    jinja_env: Environment, 
    theme: Optional[str] = None,
    htmx: bool = False,
    user_css_files: Optional[list[str]] = None,
    user_js_files: Optional[list[str]] = None,
    static_url_prefix: str = "/static/dist/"
) -> Environment:
    """
    Setup ROOS Components in a Jinja2 environment.
    
    Args:
        jinja_env: The Jinja2 environment to configure
        theme: Optional theme name to use
        htmx: Whether to include HTMX library
        user_css_files: List of additional CSS files to include
        user_js_files: List of additional JS files to include  
        static_url_prefix: URL prefix for static assets
        
    Returns:
        Configured Jinja2 environment
        
    Example:
        ```python
        from jinja2 import Environment, FileSystemLoader
        from jinja_roos_components import setup_components
        
        env = Environment(loader=FileSystemLoader('templates'))
        setup_components(
            env, 
            theme="operations",
            htmx=True,
            user_css_files=['/static/custom.css'],
            user_js_files=['/static/custom.js']
        )
        ```
    """
    # Add the component extension
    jinja_env.add_extension(ComponentExtension)
    
    # Add component templates directory to loader paths
    import os
    component_templates_path = os.path.join(
        os.path.dirname(__file__), 'templates'
    )
    
    # If the environment has a FileSystemLoader, add our templates path
    if hasattr(jinja_env.loader, 'searchpath'):
        if isinstance(jinja_env.loader.searchpath, list):
            jinja_env.loader.searchpath.append(component_templates_path)
        else:
            # Convert single path to list and add our path
            jinja_env.loader.searchpath = [jinja_env.loader.searchpath, component_templates_path]
    
    # Add global functions and variables for component usage
    jinja_env.globals['get_component_assets'] = lambda: _get_component_assets(
        static_url_prefix, htmx, user_css_files, user_js_files
    )
    jinja_env.globals['roos_theme'] = theme or 'default'
    jinja_env.globals['roos_htmx'] = htmx
    
    return jinja_env


def _get_component_assets(
    static_url_prefix: str = "/static/dist/",
    htmx: bool = False,
    user_css_files: Optional[list[str]] = None,
    user_js_files: Optional[list[str]] = None
) -> Dict[str, Any]:
    """Get the URLs for component CSS and JS assets."""
    # In a real implementation, this would:
    # 1. Read the webpack manifest to get hashed filenames
    # 2. Return proper URLs based on configuration
    
    css_files = [f"{static_url_prefix}roos.css"]
    js_files = [f"{static_url_prefix}roos.js"]
    
    # Add HTMX if requested
    if htmx:
        js_files.insert(0, "https://unpkg.com/htmx.org@1.9.12/dist/htmx.min.js")
        # Optionally add HTMX extensions
        js_files.append("https://unpkg.com/htmx.org@1.9.12/dist/ext/response-targets.js")
    
    # Add user-provided files
    if user_css_files:
        css_files.extend(user_css_files)
    if user_js_files:
        js_files.extend(user_js_files)
    
    return {
        'css_files': css_files,
        'js_files': js_files,
        'htmx_enabled': htmx,
    }