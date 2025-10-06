#!/usr/bin/env python3
"""
Helper script to generate web-types.json for components from definitions.json.

This script reads component definitions from definitions.json and creates web-types.json
files that can be used for IDE autocompletion.

Usage:
    python create_component_web_types.py <component-name>
    python create_component_web_types.py checkbox
    python create_component_web_types.py --all  # Generate for all components without web-types
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

def load_definitions() -> Dict[str, Any]:
    """Load component definitions from definitions.json."""
    root_dir = Path(__file__).parent.parent
    definitions_path = root_dir / "src" / "jinja_roos_components" / "components" / "definitions.json"

    with open(definitions_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def camel_to_kebab(name: str) -> str:
    """Convert camelCase to kebab-case."""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()

def convert_attribute_to_web_types(attr: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a definitions.json attribute to web-types format."""
    # Convert camelCase attribute name to kebab-case
    attr_name = camel_to_kebab(attr['name'])

    web_type_attr = {
        "name": attr_name,
        "description": attr.get('description', ''),
        "value": {
            "required": attr.get('required', False)
        }
    }

    # Handle type
    attr_type = attr.get('type', 'string')
    if attr_type == 'enum':
        web_type_attr["value"]["type"] = "enum"
        web_type_attr["value"]["enum"] = attr.get('enum_values', [])
    else:
        web_type_attr["value"]["type"] = attr_type

    # Add default value if present
    default = attr.get('default')
    if default is not None and default != '':
        web_type_attr["value"]["default"] = default

    return web_type_attr

def generate_web_types_for_component(component_name: str, component_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate web-types definition for a component from definitions.json.
    """
    attributes = []

    # Convert all attributes from definitions.json
    for attr in component_def.get('attributes', []):
        web_type_attr = convert_attribute_to_web_types(attr)
        attributes.append(web_type_attr)

    # Generate the web-types structure
    web_types = {
        "name": f"c-{component_name}",
        "description": component_def.get('description', f"RVO {component_name.replace('-', ' ').title()} component"),
        "attributes": attributes
    }

    return web_types

def find_component_in_definitions(component_name: str, definitions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find a component definition by name in definitions.json."""
    # Check regular components
    for comp in definitions.get('components', []):
        if comp['name'] == component_name:
            return comp

    # Check aliases
    for alias in definitions.get('aliases', []):
        if alias['name'] == component_name:
            # For aliases, we need to merge with the target component
            target_name = alias.get('target_component')
            if target_name:
                for comp in definitions.get('components', []):
                    if comp['name'] == target_name:
                        # Create a merged definition
                        merged = comp.copy()
                        merged['name'] = component_name
                        merged['description'] = alias.get('description', comp['description'])

                        # Merge default attributes
                        default_attrs = alias.get('default_attributes', {})
                        if default_attrs:
                            # Update defaults in attributes
                            merged_attrs = []
                            for attr in comp['attributes']:
                                attr_copy = attr.copy()
                                if attr['name'] in default_attrs:
                                    attr_copy['default'] = default_attrs[attr['name']]
                                merged_attrs.append(attr_copy)
                            merged['attributes'] = merged_attrs

                        return merged

    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_component_web_types.py <component-name>")
        print("       python create_component_web_types.py --all")
        sys.exit(1)

    root_dir = Path(__file__).parent.parent
    components_dir = root_dir / "src" / "jinja_roos_components" / "templates" / "components"

    # Load definitions
    definitions = load_definitions()

    if sys.argv[1] == '--all':
        # Process all components and aliases from definitions.json
        all_components = []

        # Add all regular components
        for comp in definitions.get('components', []):
            all_components.append(comp['name'])

        # Add all aliases
        for alias in definitions.get('aliases', []):
            all_components.append(alias['name'])

        for component_name in sorted(all_components):
            template_path = components_dir / f"{component_name}.html.j2"
            web_types_path = template_path.with_suffix('.web-types.json')

            if not web_types_path.exists():
                print(f"Generating web-types for: {component_name}")

                # Find component in definitions
                component_def = find_component_in_definitions(component_name, definitions)
                if not component_def:
                    print(f"  Warning: No definition found for {component_name}, skipping")
                    continue

                web_types = generate_web_types_for_component(component_name, component_def)

                with open(web_types_path, 'w', encoding='utf-8') as f:
                    json.dump(web_types, f, indent=2, ensure_ascii=False)

                print(f"  Created: {web_types_path.name}")

        # Regenerate main web-types.json
        print("\nRegenerating main web-types.json...")
        import subprocess
        subprocess.run([sys.executable, str(root_dir / "scripts" / "generate_web_types.py")])

    else:
        component_name = sys.argv[1]

        # Find component in definitions
        component_def = find_component_in_definitions(component_name, definitions)
        if not component_def:
            print(f"Error: Component '{component_name}' not found in definitions.json")
            print(f"Available components: {', '.join(sorted([c['name'] for c in definitions.get('components', [])] + [a['name'] for a in definitions.get('aliases', [])]))}")
            sys.exit(1)

        print(f"Loading component definition from definitions.json: {component_name}")

        # Generate web-types
        web_types = generate_web_types_for_component(component_name, component_def)

        # Write to file
        template_path = components_dir / f"{component_name}.html.j2"
        output_path = template_path.with_suffix('.web-types.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(web_types, f, indent=2, ensure_ascii=False)

        print(f"Generated: {output_path}")
        print("\nGenerated web-types structure:")
        print(json.dumps(web_types, indent=2))
        print("\nYou can now customize this file if needed.")
        print("Run 'python scripts/generate_web_types.py' to update the main web-types.json")

if __name__ == "__main__":
    main()