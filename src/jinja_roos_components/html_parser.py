"""
HTML-based component parser using Python's built-in html.parser.
This replaces the regex-based approach for more reliable parsing.
"""

import html.parser
import re
from typing import List, Dict, Any, Optional, Tuple


class ComponentHTMLParser(html.parser.HTMLParser):
    """
    HTML parser that identifies component tags and their attributes.
    """
    
    def __init__(self, registry):
        super().__init__()
        self.registry = registry
        self.components = []
        self.tag_stack = []
        self.current_pos = 0
        self.source = ""
        
    def parse_components(self, source: str) -> List[Dict[str, Any]]:
        """Parse component tags from HTML source."""
        self.source = source
        self.components = []
        self.tag_stack = []
        self.current_pos = 0
        
        try:
            self.feed(source)
        except Exception as e:
            # DO NOT FAIL SILENTLY - raise the actual parsing error
            raise ValueError(f"HTML parser failed to process template source: {e}. Template content length: {len(source)} chars") from e
            
        # Sort components by position (innermost first for processing)
        return sorted(self.components, key=lambda x: x['depth'], reverse=True)
    
    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        """Handle opening tags."""
        if not tag.startswith('c-'):
            return

        component_name = tag[2:]  # Remove 'c-' prefix
        if not self.registry.has_component(component_name):
            # Get line number for better error messages
            line_num = self.source[:self.current_pos].count('\n') + 1
            col_num = self.current_pos - self.source.rfind('\n', 0, self.current_pos)

            available = ', '.join(sorted(self.registry.get_all_component_names())[:10])
            if len(self.registry.get_all_component_names()) > 10:
                available += '...'

            raise ValueError(
                f"Unknown component '<{tag}>' at line {line_num}, column {col_num}. "
                f"This component does not exist in the registry. "
                f"Available components: {available}. "
                f"This error prevents infinite loops when templates reference non-existent components."
            )
            
        # Find the actual position in source
        tag_start = self.source.find(f'<{tag}', self.current_pos)
        if tag_start == -1:
            return
            
        # Find end of opening tag - handle multi-line tags and nested quotes
        # We need to be careful with quotes inside attribute values
        tag_end = tag_start + len(f'<{tag}')
        in_quote = None
        escaped = False
        
        while tag_end < len(self.source):
            char = self.source[tag_end]
            
            # Handle escape sequences
            if escaped:
                escaped = False
                tag_end += 1
                continue
                
            if char == '\\':
                escaped = True
                tag_end += 1
                continue
            
            # Handle quotes
            if char in ('"', "'"):
                if in_quote is None:
                    in_quote = char
                elif in_quote == char:
                    in_quote = None
            
            # Found end of tag (not inside quotes)
            elif char == '>' and in_quote is None:
                tag_end += 1
                break
                
            tag_end += 1
        else:
            # Didn't find closing >
            return
        
        # Check if self-closing
        tag_content = self.source[tag_start:tag_end]
        self_closing = tag_content.endswith('/>')
        
        # Extract attributes from the tag content since HTMLParser's attrs might be incomplete
        # for multi-line attributes
        attrs_dict = {}
        if tag_content:
            # Extract the attributes part (between tag name and >)
            attrs_start = tag_start + len(f'<{tag}')
            attrs_end = tag_end - 1 if not self_closing else tag_end - 2
            attrs_str = self.source[attrs_start:attrs_end].strip()
            
            if attrs_str:
                # Parse attributes manually to handle multi-line and complex values
                attrs_dict = self._parse_attributes(attrs_str)
        
        component = {
            'tag': tag,
            'component_name': component_name,
            'attrs': attrs_dict,
            'start': tag_start,
            'tag_end': tag_end,
            'self_closing': self_closing,
            'full_match': tag_content,
            'depth': len(self.tag_stack),
            'content': ''
        }
        
        if not self_closing:
            # Add to stack for matching with end tag
            self.tag_stack.append(component)
        else:
            # Self-closing tag, add immediately
            self.components.append(component)
        
        self.current_pos = tag_end
    
    def handle_endtag(self, tag: str):
        """Handle closing tags."""
        if not tag.startswith('c-') or not self.tag_stack:
            return
            
        # Find matching opening tag
        for i in reversed(range(len(self.tag_stack))):
            if self.tag_stack[i]['tag'] == tag:
                component = self.tag_stack.pop(i)
                
                # Find the actual end tag position
                end_tag_start = self.source.find(f'</{tag}>', self.current_pos)
                if end_tag_start != -1:
                    end_tag_end = end_tag_start + len(f'</{tag}>')
                    component['end'] = end_tag_end
                    
                    # Extract content between tags
                    content_start = component['tag_end']
                    content_end = end_tag_start
                    component['content'] = self.source[content_start:content_end]
                    
                    self.current_pos = end_tag_end
                
                self.components.append(component)
                break
    
    def handle_data(self, data: str):
        """Handle text data between tags."""
        # Update current position to track where we are
        pos = self.source.find(data, self.current_pos)
        if pos != -1:
            self.current_pos = pos + len(data)
    
    def _find_matching_endif(self, text: str) -> Optional[int]:
        """
        Find the position after the matching {% endif %} for an {% if %} block.
        Returns the position after {% endif %}, or None if not found.
        """
        if_depth = 0
        pos = 0

        while pos < len(text):
            if text[pos:pos+2] == '{%':
                # Find the end of this block
                block_end = text.find('%}', pos + 2)
                if block_end == -1:
                    return None

                block_content = text[pos+2:block_end].strip()

                if block_content.startswith('if ') or block_content == 'if':
                    if_depth += 1
                elif block_content.startswith('endif'):
                    if_depth -= 1
                    if if_depth == 0:
                        return block_end + 2

                pos = block_end + 2
            else:
                pos += 1

        return None

    def _extract_jinja_block(self, attrs_str: str, pos: int) -> Tuple[str, int]:
        """
        Extract a Jinja block starting at pos.
        Handles {% ... %} and {{ ... }} blocks, including nested blocks.
        Returns tuple of (block_content, position_after_block).
        """
        if pos + 1 >= len(attrs_str):
            return "", pos

        if attrs_str[pos:pos+2] == '{%':
            end_tag = '%}'
        elif attrs_str[pos:pos+2] == '{{':
            end_tag = '}}'
        else:
            return "", pos

        start_tag = attrs_str[pos:pos+2]
        search_pos = pos + 2
        nesting = 1

        while search_pos < len(attrs_str) - 1 and nesting > 0:
            two_chars = attrs_str[search_pos:search_pos+2]
            if two_chars == start_tag:
                nesting += 1
                search_pos += 2
            elif two_chars == end_tag:
                nesting -= 1
                search_pos += 2
            else:
                search_pos += 1

        return attrs_str[pos:search_pos], search_pos

    def _parse_attributes(self, attrs_str: str) -> Dict[str, str]:
        """
        Parse attributes from a string, handling multi-line values and nested quotes.
        Uses character-by-character parsing to handle complex nested structures.
        Also handles Jinja blocks ({% ... %} and {{ ... }}) within attribute areas.

        Conditional attributes like {% if x %}attr="val"{% endif %} are stored with
        a special key format: __jinja_conditional_N__ where N is a counter.
        """
        attrs = {}
        pos = 0
        conditional_counter = 0

        while pos < len(attrs_str):
            # Skip whitespace
            while pos < len(attrs_str) and attrs_str[pos].isspace():
                pos += 1

            if pos >= len(attrs_str):
                break

            # Check for Jinja block that might wrap a conditional attribute
            if pos + 1 < len(attrs_str) and attrs_str[pos:pos+2] == '{%':
                block_content, block_end = self._extract_jinja_block(attrs_str, pos)

                # Check if this is an {% if %} block that contains an attribute
                if block_content.startswith('{%') and (' if ' in block_content[:50] or block_content[2:].strip().startswith('if ')):
                    # This looks like a conditional - find the matching {% endif %}
                    # and capture everything in between as a conditional attribute
                    remaining = attrs_str[pos:]
                    endif_match = self._find_matching_endif(remaining)
                    if endif_match:
                        full_conditional = remaining[:endif_match]
                        # Store the entire conditional block
                        attrs[f'__jinja_conditional_{conditional_counter}__'] = full_conditional
                        conditional_counter += 1
                        pos += endif_match
                        continue

                # Not a conditional, just skip this block
                pos = block_end
                continue

            # Find attribute name (including : or @ prefix)
            name_start = pos
            if attrs_str[pos] in (':@'):
                pos += 1

            # Read the attribute name - validate each character
            while pos < len(attrs_str):
                char = attrs_str[pos]

                if char.isalnum() or char in '-_':
                    # Valid attribute name character
                    pos += 1
                elif char in ' \t\n\r' or char == '=':
                    # Valid terminator for attribute name (whitespace or equals)
                    break
                else:
                    # Invalid character encountered while parsing attribute name
                    if pos == name_start:
                        # We haven't read any valid attribute name yet
                        context_start = max(0, pos - 20)
                        context_end = min(len(attrs_str), pos + 20)
                        context = attrs_str[context_start:context_end]
                        raise ValueError(
                            f"Invalid attribute syntax: unexpected character '{char}' at position {pos}. "
                            f"Expected attribute name to start with letter, number, or colon/at-sign. "
                            f"Context: ...{context}..."
                        )
                    else:
                        # We were reading an attribute name and hit an invalid character
                        context_start = max(0, pos - 20)
                        context_end = min(len(attrs_str), pos + 20)
                        context = attrs_str[context_start:context_end]
                        raise ValueError(
                            f"Invalid attribute syntax: unexpected character '{char}' at position {pos} "
                            f"while parsing attribute name. "
                            f"Context: ...{context}..."
                        )

            attr_name = attrs_str[name_start:pos]

            if pos >= len(attrs_str):
                # End of string after attribute name - it's a boolean attribute
                attrs[attr_name] = None
                break

            # Skip whitespace after attribute name
            while pos < len(attrs_str) and attrs_str[pos] in ' \t\n\r':
                pos += 1

            # Check if there's an = sign (attribute has a value) or not (boolean attribute)
            if pos >= len(attrs_str) or attrs_str[pos] != '=':
                # Boolean attribute (no value)
                attrs[attr_name] = None
                continue

            # Skip the = sign
            pos += 1

            # Skip whitespace after =
            while pos < len(attrs_str) and attrs_str[pos] in ' \t\n\r':
                pos += 1

            if pos >= len(attrs_str):
                attrs[attr_name] = ""
                break

            # Find attribute value - handle nested structures
            if attrs_str[pos] in ('"', "'"):
                # Quoted value - use stack to track nested brackets/quotes
                outer_quote = attrs_str[pos]
                pos += 1
                value_start = pos
                
                # Track nesting of brackets and quotes
                bracket_stack = []
                inner_quote = None
                
                while pos < len(attrs_str):
                    char = attrs_str[pos]
                    
                    # Handle quotes inside the value
                    if char in ('"', "'") and not bracket_stack:
                        # We're at the outer level
                        if char == outer_quote:
                            # Found closing outer quote
                            break
                    elif char in ('"', "'"):
                        # Quote inside brackets
                        if inner_quote is None:
                            inner_quote = char
                        elif inner_quote == char:
                            inner_quote = None
                    
                    # Track brackets (only when not in inner quotes)
                    elif not inner_quote:
                        if char in '[{(':
                            bracket_stack.append(char)
                        elif char in ']})':
                            if bracket_stack:
                                bracket_stack.pop()
                    
                    pos += 1
                
                attr_value = attrs_str[value_start:pos]
                if pos < len(attrs_str):
                    pos += 1  # Skip closing quote
            else:
                # Unquoted value
                value_start = pos
                while pos < len(attrs_str) and not attrs_str[pos].isspace():
                    pos += 1
                attr_value = attrs_str[value_start:pos]
            
            attrs[attr_name] = attr_value
        
        return attrs


def parse_component_attributes(attrs_str: str) -> Dict[str, str]:
    """
    Parse component attributes from attribute string.
    This handles the complex attribute parsing that was done in the extension.
    """
    if not attrs_str.strip():
        return {}
    
    attrs = {}
    
    # Pattern for attributes: name="value" or :name="value" or @name="value"
    # Handle both quoted and unquoted values
    pattern = re.compile(r'([@:]?)(\w+(?:-\w+)*)=(["\'])([^"\']*?)\3')
    
    for match in pattern.finditer(attrs_str):
        prefix = match.group(1)
        name = match.group(2)
        quote = match.group(3)
        value = match.group(4)
        
        # Add prefix to name if present
        full_name = f"{prefix}{name}" if prefix else name
        attrs[full_name] = value
    
    # Also handle boolean attributes (attributes without values)
    bool_pattern = re.compile(r'\b(\w+(?:-\w+)*)\b(?!\s*=)')
    for match in bool_pattern.finditer(attrs_str):
        attr_name = match.group(1)
        if attr_name not in attrs and not any(attr_name in key for key in attrs.keys()):
            attrs[attr_name] = ""
    
    return attrs


def _parse_conditional_attr(conditional_block: str) -> Optional[Tuple[str, str, str]]:
    """
    Parse a conditional attribute block like {% if x %}attr="value"{% endif %}.
    Returns tuple of (condition, attr_name, attr_value) or None if parsing fails.
    """
    # Extract the condition from {% if condition %}
    if_match = re.match(r'\{%\s*if\s+(.+?)\s*%\}', conditional_block)
    if not if_match:
        return None
    condition = if_match.group(1)

    # Find the content between {% if %} and {% endif %}
    if_end = conditional_block.find('%}')
    endif_start = conditional_block.rfind('{%')
    if if_end == -1 or endif_start == -1:
        return None

    inner_content = conditional_block[if_end + 2:endif_start].strip()

    # Parse the attribute from the inner content
    attr_match = re.match(r'([\w-]+)\s*=\s*"([^"]*)"', inner_content)
    if not attr_match:
        attr_match = re.match(r"([\w-]+)\s*=\s*'([^']*)'", inner_content)
    if not attr_match:
        return None

    attr_name = attr_match.group(1)
    attr_value = attr_match.group(2)

    return (condition, attr_name, attr_value)


def convert_parsed_component(component: Dict[str, Any]) -> str:
    """
    Convert a parsed component to its Jinja2 include equivalent.
    This is the consolidated component conversion logic used by both html_parser and extension.
    """
    component_name = component['component_name']
    attrs = component.get('attrs', {})
    template_path = f"components/{component_name}.html.j2"

    if not attrs and not (component.get('content') and component['content'].strip()):
        return f'{{% set _component_context = {{}} %}}{{% include "{template_path}" with context %}}'

    # Get component definition for attribute type checking
    from .registry import ComponentRegistry, AttributeType
    registry = ComponentRegistry()
    component_def = registry.get_component(component_name)

    # Extract raw content if present
    raw_content = None
    if component.get('content') and component['content'].strip():
        raw_content = component['content']

    # Separate conditional attributes from regular attributes
    conditional_attrs = []
    regular_attrs = {}
    for key, value in attrs.items():
        if key.startswith('__jinja_conditional_') and key.endswith('__'):
            # Parse the conditional block to extract condition and attribute
            parsed = _parse_conditional_attr(value)
            if parsed:
                conditional_attrs.append(parsed)
        else:
            regular_attrs[key] = value

    # Build context dictionary from regular attributes
    context_items = []
    event_templates = []

    for key, value in regular_attrs.items():
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
            # Event attribute - need to render Jinja variables if present
            if '{{' in value or '{%' in value:
                # Create a temporary variable to render the Jinja expressions
                import random
                import string
                var_suffix = ''.join(random.choices(string.ascii_lowercase, k=8))
                temp_var = f'_event_attr_{var_suffix}'
                # Create a template that renders the event attribute with current context
                event_templates.append(f'{{% set {temp_var} %}}{value}{{% endset %}}')
                context_items.append(f"'{key}': {temp_var}")
            else:
                # No Jinja syntax, pass as regular string
                escaped_value = value.replace('"', '\\"')
                context_items.append(f"'{key}': \"{escaped_value}\"")
        else:
            # Regular string attribute
            # Check attribute type for special handling
            attr_def = component_def.get_attribute(key) if component_def else None

            # Handle BOOLEAN attributes - auto-convert string boolean values
            if attr_def and attr_def.type == AttributeType.BOOLEAN:
                # Handle shorthand notation (None value means true)
                if value is None:
                    context_items.append(f'"{key}": True')
                else:
                    # Convert common string boolean values to actual booleans
                    value_lower = value.lower().strip()
                    if value_lower in ('false', '0', '', 'no', 'off'):
                        context_items.append(f'"{key}": False')
                    elif value_lower in ('true', '1', 'yes', 'on'):
                        context_items.append(f'"{key}": True')
                    else:
                        # Unknown value for boolean - treat as truthy if non-empty
                        context_items.append(f'"{key}": {bool(value)}')

            elif attr_def and attr_def.type == AttributeType.OBJECT:
                # Object attribute - handle JSON string parsing
                if '{{' in value or '{%' in value:
                    # Contains Jinja expressions that should evaluate to JSON
                    import random
                    import string
                    var_suffix = ''.join(random.choices(string.ascii_lowercase, k=8))
                    temp_var = f'_attr_{var_suffix}'
                    parsed_var = f'_parsed_{var_suffix}'
                    # First capture the rendered JSON string, then parse it
                    event_templates.append(f'{{% set {temp_var} %}}{value}{{% endset %}}')
                    event_templates.append(f'{{% set {parsed_var} = {temp_var} | from_json %}}')
                    context_items.append(f'"{key}": {parsed_var}')
                else:
                    # Static JSON string - parse it directly
                    try:
                        import json
                        # Try to parse as JSON to validate
                        parsed_obj = json.loads(value)
                        # If successful, use the from_json filter in template
                        escaped_json = value.replace('"', '\\"')
                        context_items.append(f'"{key}": "{escaped_json}" | from_json')
                    except json.JSONDecodeError:
                        # Invalid JSON, treat as regular string
                        escaped_value = value.replace('"', '\\"')
                        context_items.append(f'"{key}": "{escaped_value}"')
            elif value is not None and ('{{' in value or '{%' in value):
                # Regular attribute with Jinja expressions
                import random
                import string
                var_suffix = ''.join(random.choices(string.ascii_lowercase, k=8))
                temp_var = f'_attr_{var_suffix}'
                # Create a template that renders the attribute with current context
                event_templates.append(f'{{% set {temp_var} %}}{value}{{% endset %}}')
                context_items.append(f'"{key}": {temp_var}')
            elif value is None:
                # Handle shorthand notation for passthrough attributes (data-*, aria-*, etc.)
                # Render as empty string so template can output just the attribute name
                context_items.append(f'"{key}": ""')
            else:
                # Regular string value
                escaped_value = value.replace('"', '\\"')
                context_items.append(f'"{key}": "{escaped_value}"')
    
    # Build the event template processing parts
    event_templates_str = ''.join(event_templates)

    # Build conditional attribute updates
    # These will be evaluated at runtime after the base context is set
    # We set the attribute directly on the dict using Jinja's namespace or update syntax
    conditional_updates = []
    for condition, attr_name, attr_value in conditional_attrs:
        # Check if attr_value contains Jinja expressions
        if '{{' in attr_value or '{%' in attr_value:
            # Need to render the value first, then use _component_context.update()
            import random
            import string
            var_suffix = ''.join(random.choices(string.ascii_lowercase, k=8))
            temp_var = f'_cond_attr_{var_suffix}'
            conditional_updates.append(
                f'{{% if {condition} %}}'
                f'{{% set {temp_var} %}}{attr_value}{{% endset %}}'
                f'{{%- set _ = _component_context.__setitem__("{attr_name}", {temp_var}) -%}}'
                f'{{% endif %}}'
            )
        else:
            escaped_value = attr_value.replace('"', '\\"')
            conditional_updates.append(
                f'{{% if {condition} %}}'
                f'{{%- set _ = _component_context.__setitem__("{attr_name}", "{escaped_value}") -%}}'
                f'{{% endif %}}'
            )
    conditional_str = ''.join(conditional_updates)

    # Handle raw content separately using capture block
    if raw_content:
        context_str = ', '.join(context_items) if context_items else ''
        # Generate a unique variable name to avoid conflicts with nested components
        import random
        import string
        var_suffix = ''.join(random.choices(string.ascii_lowercase, k=8))
        capture_var = f'_captured_content_{var_suffix}'

        content_part = f'"content": {capture_var}'
        full_context = context_str + (", " if context_str else "") + content_part
        return (f'{event_templates_str}'
               f'{{% set {capture_var} %}}{raw_content}{{% endset %}}'
               f'{{% set _component_context = {{{full_context}}} %}}'
               f'{conditional_str}'
               f'{{% include "{template_path}" with context %}}')
    else:
        context_str = ', '.join(context_items)
        return (f'{event_templates_str}'
               f'{{% set _component_context = {{{context_str}}} %}}'
               f'{conditional_str}'
               f'{{% include "{template_path}" with context %}}') 