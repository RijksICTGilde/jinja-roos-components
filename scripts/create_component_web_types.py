#!/usr/bin/env python3
"""
Helper script to generate web-types.json for a component by analyzing its template.

This script parses a Jinja2 component template and creates a basic web-types.json
file that can be further customized.

Usage:
    python create_component_web_types.py <component-name>
    python create_component_web_types.py checkbox
    python create_component_web_types.py --all  # Generate for all components without web-types
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

def extract_component_variables(template_content: str) -> List[Tuple[str, str, str]]:
    """
    Extract variable definitions from Jinja2 template.
    Returns list of (variable_name, default_value, likely_type).
    """
    variables = []
    
    # Pattern to match {% set var = _component_context.var | default(...) %}
    pattern = r"{%\s*set\s+(\w+)\s*=\s*_component_context\.(\w+)\s*\|\s*default\((.*?)\)"
    
    for match in re.finditer(pattern, template_content):
        var_name = match.group(2)  # Use the context variable name, not the local one
        default_value = match.group(3).strip()
        
        # Determine type from default value
        if default_value in ('true', 'false', 'True', 'False'):
            var_type = 'boolean'
            default_value = default_value.lower()
        elif default_value.startswith(("'", '"')):
            var_type = 'string'
            default_value = default_value.strip("'\"")
        elif default_value.replace('.', '').replace('-', '').isdigit():
            var_type = 'number'
        elif default_value == '[]':
            var_type = 'array'
        elif default_value == '{}':
            var_type = 'object'
        else:
            var_type = 'string'
            default_value = default_value.strip("'\"")
        
        variables.append((var_name, default_value, var_type))
    
    return variables

def guess_enum_values(var_name: str, template_content: str) -> Optional[List[str]]:
    """
    Try to guess enum values from template logic.
    """
    # Common enum patterns
    known_enums = {
        'size': ['xs', 'sm', 'md', 'lg', 'xl'],
        'kind': ['primary', 'secondary', 'tertiary', 'quaternary', 'subtle', 'warning'],
        'type': ['button', 'submit', 'reset'],
        'padding': ['none', 'xs', 'sm', 'md', 'lg', 'xl'],
        'gap': ['xs', 'sm', 'md', 'lg', 'xl', '2xl', '3xl'],
        'align': ['left', 'center', 'right'],
        'verticalAlign': ['top', 'middle', 'bottom'],
    }
    
    if var_name in known_enums:
        return known_enums[var_name]
    
    # Try to find if/elif patterns in template
    enum_pattern = rf"if\s+{var_name}\s*==\s*['\"]([^'\"]+)['\"]"
    matches = re.findall(enum_pattern, template_content)
    if matches:
        return list(set(matches))
    
    return None

def camel_to_kebab(name: str) -> str:
    """Convert camelCase to kebab-case."""
    # Insert hyphen before capital letters and convert to lowercase
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()

def create_attribute_definition(var_name: str, default_value: str, var_type: str, 
                               template_content: str) -> Dict[str, Any]:
    """
    Create an attribute definition for web-types.
    """
    # Convert camelCase to kebab-case for HTML attributes
    attr_name = camel_to_kebab(var_name)
    
    # Generate description based on variable name
    description_parts = var_name.replace('_', ' ').split()
    description = ' '.join(word.capitalize() for word in description_parts)
    
    # Check if this might be an enum
    enum_values = guess_enum_values(var_name, template_content)
    
    # Determine if required (heuristic: common required fields)
    required = var_name in ['id', 'name', 'label', 'value']
    
    attribute = {
        "name": attr_name,
        "description": f"{description} for the component",
        "value": {
            "required": required
        }
    }
    
    if enum_values:
        attribute["value"]["type"] = "enum"
        attribute["value"]["enum"] = enum_values
        if default_value and default_value in enum_values:
            attribute["value"]["default"] = default_value
    else:
        attribute["value"]["type"] = var_type
        if default_value and default_value not in ('', '[]', '{}', 'None', 'null'):
            attribute["value"]["default"] = default_value
    
    return attribute

def generate_web_types_for_component(component_name: str, template_path: Path) -> Dict[str, Any]:
    """
    Generate web-types definition for a component.
    """
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Extract variables
    variables = extract_component_variables(template_content)
    
    # Create attributes list
    attributes = []
    for var_name, default_value, var_type in variables:
        attr_def = create_attribute_definition(var_name, default_value, var_type, template_content)
        attributes.append(attr_def)
    
    # Check for event handlers in template
    if '@click' in template_content or 'onclick' in template_content:
        attributes.append({
            "name": "@click",
            "description": "Click event handler",
            "value": {
                "type": "string",
                "required": False
            }
        })
    
    # Generate the web-types structure
    web_types = {
        "name": f"c-{component_name}",
        "description": f"RVO {component_name.replace('-', ' ').title()} component",
        "attributes": attributes
    }
    
    return web_types

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_component_web_types.py <component-name>")
        print("       python create_component_web_types.py --all")
        sys.exit(1)
    
    root_dir = Path(__file__).parent
    components_dir = root_dir / "jinja_roos_components" / "templates" / "components"
    
    if sys.argv[1] == '--all':
        # Process all components without web-types
        template_files = components_dir.glob("*.html.j2")
        for template_path in sorted(template_files):
            component_name = template_path.stem.replace('.html', '')
            web_types_path = template_path.with_suffix('.web-types.json')
            
            if not web_types_path.exists():
                print(f"Generating web-types for: {component_name}")
                web_types = generate_web_types_for_component(component_name, template_path)
                
                with open(web_types_path, 'w', encoding='utf-8') as f:
                    json.dump(web_types, f, indent=2, ensure_ascii=False)
                
                print(f"  Created: {web_types_path.name}")
        
        # Regenerate main web-types.json
        import subprocess
        subprocess.run([sys.executable, "generate_web_types.py"], cwd=root_dir)
        
    else:
        component_name = sys.argv[1]
        template_path = components_dir / f"{component_name}.html.j2"
        
        if not template_path.exists():
            print(f"Error: Template not found: {template_path}")
            sys.exit(1)
        
        print(f"Analyzing template: {template_path}")
        
        # Generate web-types
        web_types = generate_web_types_for_component(component_name, template_path)
        
        # Write to file
        output_path = template_path.with_suffix('.web-types.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(web_types, f, indent=2, ensure_ascii=False)
        
        print(f"Generated: {output_path}")
        print("\nGenerated web-types structure:")
        print(json.dumps(web_types, indent=2))
        print("\nYou can now customize this file to:")
        print("  - Add more detailed descriptions")
        print("  - Mark additional required fields")
        print("  - Add doc-url for documentation links")
        print("  - Refine enum values")
        print("\nRun 'python generate_web_types.py' to update the main web-types.json")

if __name__ == "__main__":
    main()