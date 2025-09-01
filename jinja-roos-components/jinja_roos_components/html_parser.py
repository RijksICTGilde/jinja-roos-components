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
            return
            
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
    
    def _parse_attributes(self, attrs_str: str) -> Dict[str, str]:
        """
        Parse attributes from a string, handling multi-line values and nested quotes.
        Uses character-by-character parsing to handle complex nested structures.
        """
        attrs = {}
        pos = 0
        
        while pos < len(attrs_str):
            # Skip whitespace
            while pos < len(attrs_str) and attrs_str[pos].isspace():
                pos += 1
            
            if pos >= len(attrs_str):
                break
            
            # Find attribute name (including : or @ prefix)
            name_start = pos
            if attrs_str[pos] in (':@'):
                pos += 1
            
            # Read the attribute name
            while pos < len(attrs_str) and (attrs_str[pos].isalnum() or attrs_str[pos] in '-_'):
                pos += 1
            
            if pos >= len(attrs_str):
                break
                
            attr_name = attrs_str[name_start:pos]
            
            # Skip whitespace and =
            while pos < len(attrs_str) and attrs_str[pos] in ' \t\n\r=':
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


def convert_parsed_component(component: Dict[str, Any]) -> str:
    """
    Convert a parsed component to its Jinja2 include equivalent.
    This replicates the component conversion logic from the original extension.
    """
    template_path = f"components/{component['component_name'].replace('-', '_')}.html.j2"
    
    # Build context from attributes
    context_items = []
    
    for key, value in component['attrs'].items():
        if key.startswith(':'):
            # Binding attribute - pass as expression
            attr_name = key[1:]  # Remove ':'
            context_items.append(f'"{attr_name}": ({value})')
        elif key.startswith('@'):
            # Event attribute - pass as string
            context_items.append(f"'{key}': \"{value}\"")
        else:
            # Regular string attribute
            escaped_value = value.replace('"', '\\"')
            context_items.append(f'"{key}": "{escaped_value}"')
    
    # Handle content
    if component.get('content') and component['content'].strip():
        # Generate unique variable for content
        import random
        import string
        var_suffix = ''.join(random.choices(string.ascii_lowercase, k=8))
        capture_var = f'_captured_content_{var_suffix}'
        
        content_part = f'"content": {capture_var}'
        context_str = ', '.join(context_items) if context_items else ''
        full_context = context_str + (", " if context_str else "") + content_part
        
        return (f'{{% set {capture_var} %}}{component["content"]}{{% endset %}}'
               f'{{% set _component_context = {{{full_context}}} %}}'
               f'{{% include "{template_path}" with context %}}')
    else:
        context_str = ', '.join(context_items)
        return f'{{% set _component_context = {{{context_str}}} %}}{{% include "{template_path}" with context %}}'