#!/usr/bin/env python3
"""
Documentation data service for live template rendering.
Extracts colors, icons, spacing, and component data for live documentation.
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add parent directory to path to import jinja_roos_components
sys.path.insert(0, str(Path(__file__).parent.parent))

from jinja_roos_components.components.registry import ComponentRegistry, AttributeType


def get_attribute_type_string(attr_type: AttributeType) -> str:
    """Convert AttributeType enum to readable string."""
    type_map = {
        AttributeType.STRING: "string",
        AttributeType.BOOLEAN: "boolean", 
        AttributeType.NUMBER: "number",
        AttributeType.ENUM: "enum",
        AttributeType.OBJECT: "object"
    }
    return type_map.get(attr_type, "unknown")


def extract_colors_from_tokens() -> List[Dict[str, str]]:
    """Extract color variables from the JSON tokens file."""
    colors = []
    
    # Get the base path of the project
    base_path = Path(__file__).parent.parent
    color_tokens_path = base_path / "node_modules" / "@nl-rvo" / "design-tokens" / "src" / "brand" / "rvo" / "color.tokens.json"
    
    if not color_tokens_path.exists():
        return []
    
    with open(color_tokens_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract colors from the nested structure
    color_data = data.get('rvo', {}).get('color', {})
    
    # Define logical color order - primary colors first, neutrals last
    primary_colors = ['hemelblauw', 'logoblauw', 'lichtblauw', 'donkerblauw']
    accent_colors = ['groen', 'oranje', 'donkergeel', 'rood']
    neutral_colors = ['wit', 'grijs', 'zwart']
    
    color_order = {}
    order_index = 1
    
    # Primary blues first
    for color in primary_colors:
        color_order[color] = order_index
        order_index += 1
    
    # Accent colors second  
    for color in accent_colors:
        color_order[color] = order_index
        order_index += 1
        
    # Neutrals last
    for color in neutral_colors:
        color_order[color] = order_index
        order_index += 1
    
    for color_name, color_info in color_data.items():
        color_value = color_info.get('value', '')
        
        # Determine if it's a main color or variant
        is_variant = any(char.isdigit() for char in color_name)
        base_color = color_name.split('-')[0] if is_variant else color_name
        
        # Get sort order for base color
        sort_order = color_order.get(base_color, 99)
        
        colors.append({
            'name': color_name,
            'template_name': color_name.lower(),  # Lowercase for template usage
            'display_name': color_name.title(),
            'hex': color_value.upper(),
            'css_variable': f'--rvo-color-{color_name}',
            'base_color': base_color,
            'is_variant': is_variant,
            'sort_order': sort_order
        })
    
    # Sort by logical order, then by variant number
    colors.sort(key=lambda x: (x['sort_order'], x['name']))
    return colors


def extract_spacing_and_sizing() -> Dict[str, List[Dict[str, str]]]:
    """Extract spacing and sizing information from JSON tokens."""
    
    # Get the base path of the project
    base_path = Path(__file__).parent.parent
    space_tokens_path = base_path / "node_modules" / "@nl-rvo" / "design-tokens" / "src" / "brand" / "rvo" / "space.tokens.json"
    size_tokens_path = base_path / "node_modules" / "@nl-rvo" / "design-tokens" / "src" / "brand" / "rvo" / "size.tokens.json"
    
    spacing_sizing = {'spacing': [], 'sizing': []}
    
    # Load space tokens
    if space_tokens_path.exists():
        with open(space_tokens_path, 'r', encoding='utf-8') as f:
            space_data = json.load(f)
        
        space_values = space_data.get('rvo', {}).get('space', {})
        for name, info in space_values.items():
            spacing_sizing['spacing'].append({
                'name': name,
                'template_name': name.lower(),
                'display_name': name.upper(),
                'value': info.get('value', ''),
                'css_variable': f'--rvo-space-{name}'
            })
    
    # Load size tokens  
    if size_tokens_path.exists():
        with open(size_tokens_path, 'r', encoding='utf-8') as f:
            size_data = json.load(f)
        
        size_values = size_data.get('rvo', {}).get('size', {})
        for name, info in size_values.items():
            spacing_sizing['sizing'].append({
                'name': name,
                'template_name': name.lower(),
                'display_name': name.upper(),
                'value': info.get('value', ''),
                'css_variable': f'--rvo-size-{name}'
            })
    
    return spacing_sizing


def extract_icons_from_types() -> List[Dict[str, str]]:
    """Extract icon names from the TypeScript types file."""
    icons = []
    
    # Get the base path of the project
    base_path = Path(__file__).parent.parent
    types_path = base_path / "node_modules" / "@nl-rvo" / "assets" / "icons" / "types.ts"
    
    if not types_path.exists():
        return []
    
    with open(types_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract icon names from TypeScript union type
    pattern = r"\|\s*'([^']+)'"
    matches = re.findall(pattern, content)
    
    # Group icons by category (improved categorization)
    category_patterns = {
        'activiteiten': ['persoon', 'man', 'vrouw', 'kind', 'gesprek', 'presentatie', 'trouwen', 'wachtend', 'lopend', 'zittend'],
        'computer-internet': ['computer', 'laptop', 'internet', 'app', 'digitaal', 'cyber', 'data', 'website', 'wifi'],
        'transport': ['auto', 'fiets', 'bus', 'trein', 'vliegtuig', 'schip', 'motor', 'taxi', 'ambulance'],
        'gebouwen': ['huis', 'gebouw', 'school', 'kantoor', 'fabriek', 'flat', 'villa', 'gemeente', 'monument'],
        'natuur-milieu': ['boom', 'plant', 'water', 'dier', 'zon', 'weer', 'milieu', 'bloem', 'klimaat'],
        'interface': ['home', 'menu', 'zoek', 'info', 'plus', 'kruis', 'pijl', 'kalender', 'vinkje', 'refresh'],
        'medisch-zorg': ['hart', 'medicijn', 'arts', 'zorg', 'gezondheid', 'mondkapje', 'ehbo'],
        'financieel': ['geld', 'munt', 'betalen', 'belasting', 'budget', 'euro'],
        'overheid': ['nederland', 'gemeente', 'wet', 'stemmen', 'koninkrijk', 'rechtbank'],
        'voorwerpen': ['lamp', 'sleutel', 'koffer', 'klok', 'weegschaal', 'telefoon']
    }
    
    for icon_name in matches:
        if not icon_name:  # Skip empty string
            continue
            
        # Determine category
        category = 'algemeen'
        icon_lower = icon_name.lower()
        
        for cat, keywords in category_patterns.items():
            if any(keyword in icon_lower for keyword in keywords):
                category = cat
                break
        
        icons.append({
            'name': icon_name,
            'template_name': icon_name.lower(),  # Lowercase for template usage
            'display_name': icon_name.replace('-', ' ').title(),
            'category': category,
            'category_display': category.replace('-', ' ').title()
        })
    
    # Sort by category then name for consistent ordering
    icons.sort(key=lambda x: (x['category'], x['name']))
    return icons


def generate_example_code(component_name: str, attributes: List[Dict]) -> str:
    """Generate realistic example HTML code for a component."""
    
    # Get examples from the component registry
    from jinja_roos_components.components.registry import ComponentRegistry
    registry = ComponentRegistry()
    component_def = registry.get_component(component_name)
    
    if component_def and component_def.examples:
        # Use the first example from the component definition
        return component_def.examples[0]
    
    # Generate basic example with realistic attributes
    attrs = []
    content = "Content here"
    
    # Look for common attributes and provide realistic values
    for attr in attributes[:3]:
        if attr['name'] == 'title':
            attrs.append('title="Example Title"')
            content = None  # Self-closing or title-based
        elif attr['name'] == 'label':
            attrs.append('label="Example Label"')
            content = None
        elif attr['name'] == 'variant' and attr.get('enum_values'):
            attrs.append(f'variant="{attr["enum_values"][0]}"')
        elif attr['name'] == 'type' and attr.get('enum_values'):
            attrs.append(f'type="{attr["enum_values"][0]}"')
        elif attr['type'] == 'boolean':
            attrs.append(f':{attr["name"]}="true"')
        elif attr['type'] == 'enum' and attr.get('enum_values'):
            attrs.append(f'{attr["name"]}="{attr["enum_values"][0]}"')
    
    # Build the example
    if content:
        if attrs:
            return f"<c-{component_name} {' '.join(attrs)}>{content}</c-{component_name}>"
        else:
            return f"<c-{component_name}>{content}</c-{component_name}>"
    else:
        # Self-closing tag
        if attrs:
            return f"<c-{component_name} {' '.join(attrs)} />"
        else:
            return f"<c-{component_name} />"


def get_components_data() -> List[Dict[str, Any]]:
    """Get all components data from the registry including aliases."""
    
    # Initialize component registry
    registry = ComponentRegistry()
    
    # Get all components
    components = []
    
    # First, add all real components
    for name, definition in registry._components.items():
        component_data = {
            'name': name,
            'description': definition.description,
            'attributes': [],
            'is_alias': False,
            'alias_target': None,
            'alias_defaults': None,
            'allow_preview': definition.allow_preview,
            'requires_children': definition.requires_children,
            'preview_example': definition.preview_example
        }
        
        # Process attributes
        for attr in definition.attributes:
            attr_data = {
                'name': attr.name,
                'type': get_attribute_type_string(attr.type),
                'description': attr.description,
                'required': attr.required,
                'default': attr.default,
                'enum_values': attr.enum_values
            }
            component_data['attributes'].append(attr_data)
        
        # Generate example code
        component_data['example'] = generate_example_code(name, component_data['attributes'])
        
        components.append(component_data)
    
    # Then, add all aliases
    for alias_name, alias_def in registry._aliases.items():
        target_component = registry.get_component(alias_def.target_component)
        
        if target_component:
            component_data = {
                'name': alias_name,
                'description': f"{alias_def.description} (Alias for c-{alias_def.target_component})",
                'attributes': [],
                'is_alias': True,
                'alias_target': alias_def.target_component,
                'alias_defaults': alias_def.default_attributes,
                'allow_preview': target_component.allow_preview,
                'requires_children': target_component.requires_children,
                'preview_example': target_component.preview_example
            }
            
            # Process attributes from target component but show merged defaults
            for attr in target_component.attributes:
                # Check if this attribute has a default from the alias
                default_value = alias_def.default_attributes.get(attr.name, attr.default)
                
                attr_data = {
                    'name': attr.name,
                    'type': get_attribute_type_string(attr.type),
                    'description': attr.description,
                    'required': attr.required,
                    'default': default_value,
                    'enum_values': attr.enum_values,
                    'preset_by_alias': attr.name in alias_def.default_attributes
                }
                component_data['attributes'].append(attr_data)
            
            # Generate example code for alias
            component_data['example'] = generate_alias_example_code(alias_name, alias_def, component_data['attributes'])
            
            components.append(component_data)
    
    # Sort components by name (aliases and real components together)
    components.sort(key=lambda x: x['name'])
    return components


def generate_alias_example_code(alias_name: str, alias_def, attributes: List[Dict]) -> str:
    """Generate example code specifically for component aliases."""
    
    # Specific examples for our aliases
    alias_examples = {
        'h1': '<c-h1>Main Title</c-h1>',
        'h2': '<c-h2 class="subtitle">Section Title</c-h2>',
        'h3': '<c-h3>Subsection Title</c-h3>',
        'h4': '<c-h4>Minor Heading</c-h4>',
        'h5': '<c-h5>Small Heading</c-h5>',
        'h6': '<c-h6>Smallest Heading</c-h6>',
    }
    
    if alias_name in alias_examples:
        return alias_examples[alias_name]
    
    # Fallback to generic alias example
    return f'<c-{alias_name}>Example content</c-{alias_name}>'


def get_generation_date() -> str:
    """Get current date formatted for documentation."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")