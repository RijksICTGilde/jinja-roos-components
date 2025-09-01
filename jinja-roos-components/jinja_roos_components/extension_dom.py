"""
Jinja2 Component Extension using DOM-based parsing with BeautifulSoup.

This version uses BeautifulSoup for reliable HTML/XML parsing and manipulation,
avoiding all the position-tracking issues of the regex/string-based approach.
"""

import re
import logging
from typing import Any, Dict, Optional, List
from jinja2 import Environment
from jinja2.ext import Extension
from bs4 import BeautifulSoup, NavigableString, Tag
import random
import string

from .components.registry import ComponentRegistry

logger = logging.getLogger(__name__)


class ComponentExtensionDOM(Extension):
    """
    Jinja2 extension that preprocesses component syntax using BeautifulSoup DOM parsing.
    
    Transforms custom component tags into standard Jinja2 includes:
    <c-button variant="primary">Click me</c-button>
    -> {% include "components/button.html.j2" with context %}
    """
    
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)
        self.registry = ComponentRegistry()
        self._jinja_placeholders = {}
    
    def preprocess(self, source: str, name: str, filename: Optional[str] = None) -> str:
        """
        Preprocess the template source to convert component syntax to Jinja2 includes.
        """
        logger.debug(f"Preprocessing template: {name}")
        # Clear placeholders from any previous run
        self._jinja_placeholders.clear()
        
        try:
            # Use BeautifulSoup to parse the template
            # We need a parser that preserves case but doesn't break Jinja2
            # Use a custom approach: parse with xml but handle as HTML
            from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
            import warnings
            
            # First try with feature flag to preserve case
            soup = None
            # Try using html5lib if available (preserves case better)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", XMLParsedAsHTMLWarning)
                soup = BeautifulSoup(source, features='html.parser')
                # Note: html.parser lowercases attributes, but we'll handle this
                logger.debug("Using html.parser - will handle camelCase restoration")
            
            # Process all component tags
            self._process_components_in_soup(soup)
            
            # Convert back to string
            result = str(soup)
            
            # Remove XML declaration if present (from lxml-xml parser)
            if result.startswith('<?xml'):
                # Find the end of the XML declaration
                end_pos = result.find('?>')
                if end_pos != -1:
                    result = result[end_pos + 2:].lstrip()
            
            # BeautifulSoup might escape some Jinja2 tags, so we need to unescape them
            result = self._restore_jinja_tags(result)
            
            logger.debug(f"Successfully processed template: {name}")
            return result
            
        except Exception as e:
            logger.error(f"Component preprocessing failed for template {name}: {e}")
            raise RuntimeError(f"Component preprocessing failed for template '{name}': {e}") from e
    
    def _process_components_in_soup(self, soup: BeautifulSoup) -> None:
        """
        Process all component tags in the BeautifulSoup tree.
        Works from the deepest components up (bottom-up processing).
        """
        # Find all component tags (tags starting with 'c-')
        component_tags = soup.find_all(self._is_component_tag)
        
        # Process from deepest to shallowest (reverse document order often works)
        # But to ensure proper depth-first, we'll use a custom approach
        processed = set()
        
        while True:
            # Find a component that hasn't been processed yet
            found_any = False
            for tag in soup.find_all(self._is_component_tag):
                if id(tag) not in processed:
                    # Check if all child components have been processed
                    child_components = tag.find_all(self._is_component_tag)
                    if all(id(child) in processed for child in child_components):
                        # Process this component
                        self._process_single_component(tag)
                        processed.add(id(tag))
                        found_any = True
                        break
            
            if not found_any:
                break
    
    def _is_component_tag(self, tag) -> bool:
        """Check if a tag is a component tag (starts with 'c-')."""
        if not hasattr(tag, 'name'):
            return False
        return tag.name and tag.name.startswith('c-')
    
    def _process_single_component(self, tag: Tag) -> None:
        """
        Process a single component tag and replace it with Jinja2 include.
        """
        component_name = tag.name[2:]  # Remove 'c-' prefix
        
        # Check if component exists
        if not self.registry.has_component(component_name):
            available = ', '.join(sorted(self.registry.get_all_component_names()))
            raise ValueError(f"Unknown component '{tag.name}'. Available components: {available}")
        
        # Get component definition for validation
        component_def = self.registry.get_component(component_name)
        
        # Parse attributes
        attrs = self._parse_component_attributes(tag, component_def)
        
        # Get content if tag has children
        content = None
        if tag.contents:
            # Convert children to string
            content_parts = []
            for child in tag.contents:
                if isinstance(child, NavigableString):
                    content_parts.append(str(child))
                else:
                    content_parts.append(str(child))
            content = ''.join(content_parts).strip()
        
        # Build the Jinja2 include
        include_str = self._build_include(component_name, attrs, content)
        
        # Replace the tag with the include
        # We need to preserve the include as raw text, not parsed HTML
        # So we'll use a placeholder that we'll restore later
        placeholder = f"JINJA2_PLACEHOLDER_{self._generate_id()}"
        tag.replace_with(placeholder)
        
        # Store the mapping for later restoration
        self._jinja_placeholders[placeholder] = include_str
    
    def _parse_component_attributes(self, tag: Tag, component_def) -> Dict[str, Any]:
        """Parse and validate component attributes."""
        attrs = {}
        
        # Get valid attribute names from component definition
        # Create a mapping from lowercase to correct case for restoration
        valid_attrs = {attr.name.lower(): attr.name for attr in component_def.attributes}
        
        # Also map camelCase attributes that might have been lowercased
        # Add common camelCase patterns
        for attr in component_def.attributes:
            # If the attribute has uppercase letters, it's camelCase
            if any(c.isupper() for c in attr.name):
                # Add the all-lowercase version as a key
                valid_attrs[attr.name.lower()] = attr.name
        
        valid_attrs.update({
            'class': 'class',
            'id': 'id',
            'style': 'style'
        })
        
        # Parse tag attributes
        for attr_name, attr_value in tag.attrs.items():
            # BeautifulSoup sometimes returns lists for attributes
            # Convert to string if needed
            if isinstance(attr_value, list):
                attr_value = ' '.join(attr_value)
            elif attr_value is None:
                attr_value = ""
            else:
                attr_value = str(attr_value)
            
            # Handle binding (:attr) and event (@attr) prefixes
            if attr_name.startswith(':') or attr_name.startswith('@'):
                attrs[attr_name] = attr_value
            else:
                # Check if attribute is valid (case-insensitive)
                clean_name = attr_name.lower()
                if clean_name in valid_attrs:
                    # Use the correct case from the component definition
                    correct_name = valid_attrs[clean_name]
                    attrs[correct_name] = attr_value
                else:
                    available = sorted(set(valid_attrs.values()))
                    raise ValueError(
                        f"Unknown attribute '{attr_name}' used in component '{tag.name}'. "
                        f"Available attributes for '{component_def.name}': {', '.join(available)}"
                    )
        
        return attrs
    
    def _build_include(self, component_name: str, attrs: Dict[str, Any], content: Optional[str]) -> str:
        """Build the Jinja2 include statement from component name, attributes, and content."""
        template_path = f"components/{component_name}.html.j2"
        
        # Build context dictionary
        context_items = []
        
        for key, value in attrs.items():
            if key.startswith(':'):
                # Binding attribute - use the expression directly
                clean_key = key[1:]
                if value in ['true', 'false']:
                    context_items.append(f'"{clean_key}": {value.capitalize()}')
                else:
                    context_items.append(f'"{clean_key}": {value}')
            elif key.startswith('@'):
                # Event attribute - pass as string
                context_items.append(f"'{key}': \"{value}\"")
            else:
                # Regular string attribute
                # Convert value to string and escape quotes
                str_value = str(value) if value is not None else ""
                escaped_value = str_value.replace('"', '\\"')
                context_items.append(f'"{key}": "{escaped_value}"')
        
        # Handle content if present
        if content:
            # Generate unique variable name for captured content
            var_suffix = self._generate_id()
            capture_var = f'_captured_content_{var_suffix}'
            
            content_part = f'"content": {capture_var}'
            context_str = ', '.join(context_items) if context_items else ''
            full_context = context_str + (", " if context_str else "") + content_part
            
            return (f'{{% set {capture_var} %}}{content}{{% endset %}}'
                   f'{{% set _component_context = {{{full_context}}} %}}'
                   f'{{% include "{template_path}" with context %}}')
        else:
            context_str = ', '.join(context_items)
            return f'{{% set _component_context = {{{context_str}}} %}}{{% include "{template_path}" with context %}}'
    
    def _generate_id(self) -> str:
        """Generate a unique ID for variable names."""
        return ''.join(random.choices(string.ascii_lowercase, k=8))
    
    def _restore_jinja_tags(self, html: str) -> str:
        """Restore Jinja2 placeholders with actual Jinja2 tags."""
        # Keep replacing until no more placeholders remain
        # This handles nested placeholders (placeholders within placeholders)
        max_iterations = 10
        iteration = 0
        
        while 'JINJA2_PLACEHOLDER_' in html and iteration < max_iterations:
            replaced_any = False
            for placeholder, jinja_code in self._jinja_placeholders.items():
                if placeholder in html:
                    html = html.replace(placeholder, jinja_code)
                    replaced_any = True
            
            if not replaced_any:
                # No replacements made, but placeholders still exist
                # These must be orphaned placeholders
                logger.warning(f"Orphaned placeholders found after {iteration} iterations")
                break
                
            iteration += 1
        
        if iteration >= max_iterations:
            logger.warning(f"Hit max iterations ({max_iterations}) while replacing placeholders")
        
        # Also unescape any HTML entities that might have been created
        # BeautifulSoup might escape some characters
        import html as html_module
        html = html_module.unescape(html)
        
        return html


def setup_components_dom(
    jinja_env: Environment, 
    theme: Optional[str] = None,
    htmx: bool = False,
    user_css_files: Optional[list[str]] = None,
    user_js_files: Optional[list[str]] = None,
    static_url_prefix: str = "/static/dist/"
) -> Environment:
    """
    Setup ROOS Components with DOM-based parsing in a Jinja2 environment.
    
    Args:
        jinja_env: The Jinja2 environment to configure
        theme: Optional theme name to use
        htmx: Whether to include HTMX library
        user_css_files: List of additional CSS files to include
        user_js_files: List of additional JS files to include  
        static_url_prefix: URL prefix for static assets
        
    Returns:
        Configured Jinja2 environment
    """
    # Add the DOM-based component extension
    jinja_env.add_extension(ComponentExtensionDOM)
    
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
    css_files = [f"{static_url_prefix}roos.css"]
    js_files = [f"{static_url_prefix}roos.js"]
    
    # Add HTMX if requested
    if htmx:
        js_files.insert(0, "https://unpkg.com/htmx.org@1.9.12/dist/htmx.min.js")
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