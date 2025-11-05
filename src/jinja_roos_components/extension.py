"""
Jinja2 Component Extension v3 - Using Python's html.parser instead of regex

This version uses Python's built-in HTML parser for reliable component tag parsing.
"""

import re
from typing import Any, Dict, Optional, List, Tuple
from jinja2 import Environment
from jinja2.ext import Extension

from .registry import ComponentRegistry
from .html_parser import ComponentHTMLParser, convert_parsed_component


# Valid values for utility attributes (from _attribute_mixin.j2)
VALID_TEXT_STYLES = {
    'subtle', 'sm', 'md', 'lg', 'xl',
    'error', 'bold', 'italic', 'no-margins'
}

VALID_SPACING_SIZES = {
    'none', '3xs', '2xs', 'xs', 'sm', 'md', 'lg', 'xl',
    '2xl', '3xl', '4xl', '5xl'
}

VALID_SPACING_DIRECTIONS = {
    'inline-start', 'inline-end', 'block-start', 'block-end'
}


class ComponentExtension(Extension):
    """
    Jinja2 extension that preprocesses component syntax using proper HTML parsing.
    
    Transforms custom component tags into standard Jinja2 includes:
    <c-button variant="primary">Click me</c-button>
    -> {% include "components/button.html.j2" with context %}
    """
    
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)
        self.registry = ComponentRegistry()
        # Read strict_validation from environment globals if set
        self.strict_validation = environment.globals.get('_roos_strict_validation', False)
        
        # Patterns for different attribute types (with DOTALL flag for multiline)
        # Updated to handle nested quotes and complex content
        self.attr_patterns = {
            'string': re.compile(r'(\w+)="([^"\\]*(?:\\.[^"\\]*)*)"', re.DOTALL),  # attr="value" with escaped quotes
            'binding': re.compile(r':(\w+)="([^"\\]*(?:\\.[^"\\]*)*)"', re.DOTALL),  # :attr="value" (dynamic) with escaped quotes
            'event': re.compile(r'@(\w+)="([^"\\]*(?:\\.[^"\\]*)*)"', re.DOTALL),  # @event="handler" with escaped quotes
        }

    def preprocess(self, source: str, name: str, filename: Optional[str] = None) -> str:
        """
        Preprocess the template source to convert component syntax to Jinja2 includes.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.debug(f"Preprocessing template: {name}")
        try:
            # Process components from innermost to outermost
            result = self._process_components(source)
            logger.debug(f"Successfully processed template: {name}")
            return result
        except Exception as e:
            raise RuntimeError(f"Component processing failed for template {name} at {filename}: {e}") from e
    
    def _process_components(self, html: str) -> str:
        """
        Process all component tags in the HTML.
        Process from innermost to outermost to handle nesting correctly.

        Optimized: Single scan per depth level instead of per component
        """
        import logging
        logger = logging.getLogger(__name__)

        result = html
        max_depth = 100  # Safety limit
        current_depth = 0

        while current_depth < max_depth:
            # Find all components at current scan
            components = self._find_component_tags(result)

            if not components:
                break

            # Sort by depth (deepest first) and then by position (last first)
            # This ensures we process innermost components first
            components.sort(key=lambda x: (-x.get('depth', 0), -x['start']))

            # Get the deepest depth
            deepest_depth = components[0].get('depth', 0)

            # Get all components at the deepest level
            deepest_components = [c for c in components if c.get('depth', 0) == deepest_depth]

            logger.debug(f"Depth {current_depth}: Processing {len(deepest_components)} components at depth level {deepest_depth}")

            # Process content recursively for non-self-closing components
            for comp in deepest_components:
                if not comp['self_closing'] and comp.get('content'):
                    processed_content = self._process_components(comp['content'])
                    comp['content'] = processed_content

            # Sort by position (last first) to preserve positions during replacement
            deepest_components.sort(key=lambda x: -x['start'])

            # Process all components at this depth level
            for comp in deepest_components:
                replacement = self._process_single_component(comp, result)

                start = comp['start']
                end = comp.get('end', comp['tag_end'])

                result = result[:start] + replacement + result[end:]
                logger.debug(f"Replaced {comp['tag']} at position {start}")

            current_depth += 1

        if current_depth >= max_depth:
            logger.warning(f"Hit maximum depth ({max_depth}) while processing components")

        return result
    
    def _find_component_tags(self, html: str) -> List[Dict[str, Any]]:
        """
        Find all component tags using HTML parsing.
        Returns a list of component info dictionaries.
        """
        # Use appropriate parser based on validation settings
        if self.strict_validation:
            from .validating_parser import ValidatingComponentHTMLParser
            parser = ValidatingComponentHTMLParser(self.registry, strict_mode=True)
        else:
            parser = ComponentHTMLParser(self.registry)
            
        try:
            components = parser.parse_components(html)
            if not components:
                # No components found - this is fine, not an error
                return []
            return components
        except Exception as e:
            raise ValueError(f"Component HTML parsing failed: {e}.") from e
    
    def _find_component_tags_regex(self, html: str) -> List[Dict[str, Any]]:
        """
        Find all component tags using regex (fallback method).
        Returns a list of component info dictionaries.
        """
        # Pattern for opening tags (including self-closing)
        open_pattern = re.compile(r'<(c-[\w-]+)([^>]*?)(/?)\>')
        
        components = []
        tag_stack = []  # Track nesting depth
        
        # Find all opening tags
        for match in open_pattern.finditer(html):
            tag_name = match.group(1)
            attrs_str = match.group(2)
            self_closing = match.group(3) == '/'
            
            # Check if component exists
            component_name = tag_name[2:]  # Remove 'c-' prefix
            if not self.registry.has_component(component_name):
                raise ValueError(f"Unknown component '{tag_name}' found in template. Available components: {', '.join(sorted(self.registry.get_all_component_names()))}")
            
            component = {
                'tag': tag_name,
                'component_name': component_name,
                'attrs_str': attrs_str,
                'start': match.start(),
                'tag_end': match.end(),
                'self_closing': self_closing,
                'full_match': match.group(0),
                'depth': len(tag_stack)
            }
            
            if not self_closing:
                # Find matching end tag
                end_tag = f'</{tag_name}>'
                end_pos = html.find(end_tag, match.end())
                
                if end_pos != -1:
                    component['end'] = end_pos + len(end_tag)
                    component['content'] = html[match.end():end_pos]
                    
                    # Add to stack for depth tracking
                    tag_stack.append(tag_name)
                    
                    # Process the content to update depths of nested components
                    nested_open = open_pattern.search(component['content'])
                    if nested_open:
                        # Has nested components, will be processed in next iteration
                        pass
                else:
                    # No closing tag found, treat as self-closing
                    component['self_closing'] = True
                    component['content'] = ''
            else:
                component['content'] = ''
            
            components.append(component)
            
            # Update stack when we pass end tags
            if not self_closing and 'end' in component:
                # Check if we've passed any end tags
                content_after = html[match.end():component['end']]
                for closed_tag in tag_stack[:]:
                    if f'</{closed_tag}>' in content_after:
                        tag_stack.remove(closed_tag)
        
        return components
    
    def _process_single_component(self, component: Dict[str, Any], full_html: str) -> str:
        """
        Process a single component and return the Jinja2 include statement.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            component_tag = component.get('tag', 'unknown')
            component_name = component.get('component_name', 'unknown')
            start_pos = component.get('start', 0)
            
            logger.debug(f"Processing component: {component_tag} at position {start_pos}")
            logger.debug(f"Component full match: {component.get('full_match', '')}")
            
            # Parse attributes - handle both HTML parser format (dict) and regex format (string)
            if isinstance(component.get('attrs'), dict):
                # HTML parser format - attributes already parsed, but don't fix casing yet
                attrs = component['attrs']
            elif 'attrs_str' in component:
                # Regex parser format - need to parse string
                attrs = self._parse_attributes(component['attrs_str'])
            else:
                # No attributes
                attrs = {}
            
            # Resolve alias if needed
            actual_component_name = component_name
            final_attrs = attrs
            
            if self.registry.has_alias(component_name):
                logger.debug(f"Resolving alias: {component_name}")
                actual_component_name, final_attrs = self.registry.resolve_alias(component_name, attrs)
                logger.debug(f"Resolved alias {component_name} -> {actual_component_name} with attributes: {final_attrs}")
            
            # Now fix attribute casing using the actual component name
            final_attrs = self._fix_attribute_casing(final_attrs, actual_component_name)
            
            # Validate attributes against component definition (use actual component name)
            self._validate_component_attributes(actual_component_name, final_attrs, component['tag'])
            
            # Build and return the include statement
            result = convert_parsed_component({
                'component_name': actual_component_name,
                'attrs': final_attrs,
                'content': component.get('content', '') if not component['self_closing'] else ''
            })
            logger.debug(f"Generated include: {result[:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error processing component {component.get('tag', 'unknown')} at position {component.get('start', 0)}")
            logger.error(f"Component data: {component}")
            
            # Try to show context around the error
            start_pos = component.get('start', 0)
            context_start = max(0, start_pos - 50)
            context_end = min(len(full_html), start_pos + 150)
            context = full_html[context_start:context_end]
            logger.error(f"Context around error:\n{context}")
            
            raise ValueError(f"Error processing component {component.get('tag', 'unknown')}: {e}") from e
    
    def _fix_attribute_casing(self, attrs: Dict[str, Any], component_name: str) -> Dict[str, Any]:
        """
        Fix attribute casing issues caused by HTML parser converting to lowercase.
        Maps lowercased attributes back to their correct camelCase names.
        """
        component_def = self.registry.get_component(component_name)
        if not component_def:
            return attrs
        
        # Create mapping from lowercase to correct case
        case_mapping = {}
        for attr in component_def.attributes:
            case_mapping[attr.name.lower()] = attr.name
        
        # Add standard attributes that are always allowed
        case_mapping.update({
            'class': 'class',
            'id': 'id', 
            'style': 'style'
        })
        
        # Fix the casing
        fixed_attrs = {}
        for attr_name, attr_value in attrs.items():
            # Handle prefixed attributes (: and @)
            if attr_name.startswith(':') or attr_name.startswith('@'):
                prefix = attr_name[0]
                clean_name = attr_name[1:]
                correct_case = case_mapping.get(clean_name.lower(), clean_name)
                fixed_attrs[f"{prefix}{correct_case}"] = attr_value
            else:
                correct_case = case_mapping.get(attr_name.lower(), attr_name)
                fixed_attrs[correct_case] = attr_value
                
        return fixed_attrs

    def _validate_component_attributes(self, component_name: str, attrs: Dict[str, Any], component_tag: str) -> None:
        """
        Validate that all attributes used in a component are defined in the component registry.
        Raises ValueError for unknown attributes.
        """
        component_def = self.registry.get_component(component_name)
        if not component_def:
            # This should not happen since we check component existence earlier
            raise ValueError(f"Component definition not found for '{component_name}'")
        
        # Get all valid attribute names for this component
        valid_attrs = {attr.name for attr in component_def.attributes}

        # Add standard attributes that are always allowed
        standard_attrs = {
            'class',     # Custom CSS classes
            'id',        # HTML id (if not already defined in component)
            'style',     # Inline styles (rare but allowed)
        }
        valid_attrs.update(standard_attrs)

        # Add utility attributes from _attribute_mixin.j2 (available to all components)
        utility_attrs = {
            'text-style',  # Text styling utilities (bold, italic, etc.)
            'margin',      # Margin utilities
            'padding',     # Padding utilities
        }
        valid_attrs.update(utility_attrs)
        
        # Check each attribute in the component usage
        for attr_name in attrs.keys():
            if attr_name.startswith('_'):
                # Internal attributes (like _raw_content) are always allowed
                continue

            # Event attributes (@click, @change, etc.) are always allowed - handled by event mixin
            if attr_name.startswith('@'):
                continue

            # Clean attribute name (remove binding prefix)
            clean_attr_name = attr_name
            if attr_name.startswith(':'):
                clean_attr_name = attr_name[1:]

            # Allow generic HTML attributes (data-*, aria-*, hx-*, etc.)
            if self._is_generic_html_attribute(clean_attr_name):
                continue

            # Case-insensitive check since HTML parsers convert to lowercase
            valid_attrs_lower = {attr.lower() for attr in valid_attrs}
            clean_attr_lower = clean_attr_name.lower()

            if clean_attr_lower not in valid_attrs_lower:
                available_attrs = sorted(valid_attrs)
                raise ValueError(
                    f"Unknown attribute '{attr_name}' used in component '{component_tag}'. "
                    f"Available attributes for '{component_name}': {', '.join(available_attrs)}"
                )

            # Validate utility attribute values (text-style, margin, padding)
            if clean_attr_lower in ('text-style', 'margin', 'padding'):
                attr_value = attrs[attr_name]
                self._validate_utility_attribute(clean_attr_lower, attr_value, component_tag)

    def _is_generic_html_attribute(self, attr_name: str) -> bool:
        """Check if an attribute is a generic HTML attribute that should be allowed on all components."""
        # Check for common prefixes
        generic_prefixes = ['data-', 'aria-', 'hx-']
        for prefix in generic_prefixes:
            if attr_name.startswith(prefix):
                return True
        return False

    def _validate_utility_attribute(self, attr_name: str, attr_value: str, component_tag: str) -> None:
        """
        Validate utility attribute values (text-style, margin, padding).
        Raises ValueError if the value is invalid.
        """
        # Split multi-value attributes (space or comma separated)
        raw_value = attr_value.replace(',', ' ')
        values = raw_value.split()

        if attr_name == 'text-style':
            for value in values:
                if value not in VALID_TEXT_STYLES:
                    raise ValueError(
                        f"Invalid value '{value}' for 'text-style' attribute in component '{component_tag}'. "
                        f"Valid values: {', '.join(sorted(VALID_TEXT_STYLES))}"
                    )

        elif attr_name in ('margin', 'padding'):
            for value in values:
                # Check if it's a directional pattern (e.g., "inline-end-sm")
                if '-' in value and value.count('-') >= 2:
                    parts = value.split('-')
                    if len(parts) == 3:
                        direction = f"{parts[0]}-{parts[1]}"
                        size = parts[2]

                        if direction not in VALID_SPACING_DIRECTIONS:
                            raise ValueError(
                                f"Invalid direction '{direction}' in '{attr_name}' attribute value '{value}' "
                                f"in component '{component_tag}'. "
                                f"Valid directions: {', '.join(sorted(VALID_SPACING_DIRECTIONS))}"
                            )

                        if size not in VALID_SPACING_SIZES:
                            raise ValueError(
                                f"Invalid size '{size}' in '{attr_name}' attribute value '{value}' "
                                f"in component '{component_tag}'. "
                                f"Valid sizes: {', '.join(sorted(VALID_SPACING_SIZES))}"
                            )
                    else:
                        raise ValueError(
                            f"Invalid directional pattern '{value}' in '{attr_name}' attribute "
                            f"in component '{component_tag}'. "
                            f"Expected format: {{direction}}-{{size}} (e.g., 'inline-end-sm')"
                        )
                else:
                    # Simple size value
                    if value not in VALID_SPACING_SIZES:
                        raise ValueError(
                            f"Invalid value '{value}' for '{attr_name}' attribute in component '{component_tag}'. "
                            f"Valid values: {', '.join(sorted(VALID_SPACING_SIZES))} or directional patterns like 'inline-end-sm'"
                        )

    def _parse_attributes(self, attrs_str: str) -> Dict[str, Any]:
        """Parse component attributes from the attribute string."""
        attrs = {}
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Parsing attributes: '{attrs_str.strip()}'")
        
        try:
            # Use a more sophisticated parser for attributes
            # This handles nested quotes, arrays, objects, etc.
            pos = 0
            attrs_str = attrs_str.strip()
            
            while pos < len(attrs_str):
                # Skip whitespace
                while pos < len(attrs_str) and attrs_str[pos].isspace():
                    pos += 1
                
                if pos >= len(attrs_str):
                    break
                
                # Look for attribute patterns
                # Check for binding (:attr=)
                if attrs_str[pos] == ':':
                    pos += 1
                    attr_name, attr_value, new_pos = self._parse_single_attribute(attrs_str, pos, is_binding=True)
                    if attr_name:
                        attrs[f":{attr_name}"] = attr_value
                        logger.debug(f"Found binding attribute: {attr_name} = {attr_value[:50]}...")
                    pos = new_pos
                    
                # Check for event (@attr=)
                elif attrs_str[pos] == '@':
                    pos += 1
                    attr_name, attr_value, new_pos = self._parse_single_attribute(attrs_str, pos, is_event=True)
                    if attr_name:
                        attrs[f"@{attr_name}"] = attr_value
                        logger.debug(f"Found event attribute: {attr_name} = {attr_value}")
                    pos = new_pos
                    
                # Regular attribute
                else:
                    attr_name, attr_value, new_pos = self._parse_single_attribute(attrs_str, pos)
                    if attr_name:
                        attrs[attr_name] = attr_value
                        logger.debug(f"Found string attribute: {attr_name} = {attr_value}")
                    pos = new_pos
                    
                    # If we couldn't parse anything, skip this character to avoid infinite loop
                    if new_pos == pos:
                        pos += 1
            
            logger.debug(f"Parsed attributes: {attrs}")
            return attrs
            
        except Exception as e:
            logger.error(f"Error parsing attributes '{attrs_str}': {e}")
            raise ValueError(f"Component attribute parsing failed: {e}. Attributes: '{attrs_str}'") from e
    
    def _parse_single_attribute(self, attrs_str: str, start_pos: int, is_binding: bool = False, is_event: bool = False) -> Tuple[Optional[str], Optional[str], int]:
        """
        Parse a single attribute starting from start_pos.
        Returns (attribute_name, attribute_value, new_position).
        """
        import logging
        logger = logging.getLogger(__name__)
        
        pos = start_pos
        
        # Skip whitespace
        while pos < len(attrs_str) and attrs_str[pos].isspace():
            pos += 1
        
        # Parse attribute name
        name_start = pos
        while pos < len(attrs_str) and (attrs_str[pos].isalnum() or attrs_str[pos] in '-_'):
            pos += 1
        
        if pos == name_start:
            # No attribute name found
            return None, None, start_pos
        
        attr_name = attrs_str[name_start:pos]
        
        # Skip whitespace
        while pos < len(attrs_str) and attrs_str[pos].isspace():
            pos += 1
        
        # Check for = sign
        if pos >= len(attrs_str) or attrs_str[pos] != '=':
            # No = sign, not a valid attribute
            return None, None, start_pos
        
        pos += 1  # Skip =
        
        # Skip whitespace
        while pos < len(attrs_str) and attrs_str[pos].isspace():
            pos += 1
        
        # Parse attribute value
        if pos >= len(attrs_str):
            return None, None, start_pos
        
        if attrs_str[pos] == '"':
            # Parse quoted value - handle nested structures
            attr_value, new_pos = self._parse_quoted_value(attrs_str, pos)
            return attr_name, attr_value, new_pos
        else:
            # Unquoted value (shouldn't happen in our case)
            value_start = pos
            while pos < len(attrs_str) and not attrs_str[pos].isspace() and attrs_str[pos] not in '/>':
                pos += 1
            return attr_name, attrs_str[value_start:pos], pos
    
    def _parse_quoted_value(self, attrs_str: str, start_pos: int) -> Tuple[str, int]:
        """
        Parse a quoted value, handling nested quotes and complex structures.
        For binding attributes, this might contain JSON-like structures.
        """
        if attrs_str[start_pos] != '"':
            return "", start_pos
        
        pos = start_pos + 1  # Skip opening quote
        value_chars = []
        nesting_level = 0
        in_string = False
        escape_next = False
        
        while pos < len(attrs_str):
            char = attrs_str[pos]
            
            if escape_next:
                value_chars.append(char)
                escape_next = False
                pos += 1
                continue
            
            if char == '\\':
                # Check if this is escaping a quote in the HTML attribute
                if pos + 1 < len(attrs_str) and attrs_str[pos + 1] == '"':
                    # This is an escaped quote in the HTML attribute value
                    value_chars.append('\\')
                    value_chars.append('"')
                    pos += 2
                    continue
                else:
                    value_chars.append(char)
                    escape_next = True
                    pos += 1
                    continue
            
            # Track nesting for complex structures (arrays, objects)
            if not in_string:
                if char in '[{(':
                    nesting_level += 1
                elif char in ']})':
                    nesting_level -= 1
                elif char == '"' and nesting_level == 0:
                    # End of attribute value
                    return ''.join(value_chars), pos + 1
            
            # Handle strings within the value (for JSON-like structures)
            if char == "'" or (char == '"' and nesting_level > 0):
                # Toggle string state for nested quotes
                if not escape_next:
                    in_string = not in_string
            
            value_chars.append(char)
            pos += 1
        
        # If we get here, we didn't find a closing quote
        return ''.join(value_chars), pos
    


def setup_components(
    jinja_env: Environment,
    theme: Optional[str] = None,
    htmx: bool = False,
    user_css_files: Optional[list[str]] = None,
    user_js_files: Optional[list[str]] = None,
    static_url_prefix: str = "/static/dist/",
    strict_validation: bool = False
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
        strict_validation: Whether to enable strict component validation

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
    # Add the component extension with validation settings
    # Store strict_validation in the environment before adding extension
    jinja_env.globals['_roos_strict_validation'] = strict_validation
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

    # Add RVO color names for template use
    from .color_validation import get_available_colors
    jinja_env.globals['rvo_color_names'] = get_available_colors()
    
    # Add filters for component functionality
    def from_json_filter(value):
        """Parse JSON string into Python object."""
        import json
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value
    
    jinja_env.filters['from_json'] = from_json_filter
    
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