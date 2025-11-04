#!/usr/bin/env python3
"""
Generate VSCode custom HTML data file from definitions.json.

This script creates a custom_data.json file that enables VSCode to provide
intellisense/autocomplete for custom components (c-button, c-icon, etc.).

See: https://github.com/microsoft/vscode-html-languageservice/blob/main/docs/customData.md
"""

import json
from pathlib import Path
from typing import Dict, Any


def load_definitions() -> Dict[str, Any]:
    """Load component definitions from definitions.json."""
    root_dir = Path(__file__).parent.parent
    definitions_path = root_dir / "src" / "jinja_roos_components" / "definitions.json"

    with open(definitions_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_attribute_definition(attr: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a definitions.json attribute to VSCode custom data format."""
    # Convert camelCase attribute name to kebab-case

    vscode_attr: Dict[str, Any] = {
        "name": attr['name']
    }

    # Add description if present
    description = attr.get('description', '')
    if description:
        vscode_attr["description"] = description

    # Handle enum types with values
    attr_type = attr.get('type', 'string')
    if attr_type == 'enum' and attr.get('enum_values'):
        vscode_attr["values"] = [
            {"name": value} for value in attr['enum_values']
        ]
    elif attr_type == 'boolean':
        vscode_attr["values"] = [
            {"name": value} for value in ('true', 'false')
        ]

    # Add default value in description if present
    default = attr.get('default')
    if default is not None and default != '':
        default_str = str(default).lower() if isinstance(default, bool) else str(default)
        if description:
            vscode_attr["description"] = f"{description} (default: `{default_str}`)"
        else:
            vscode_attr["description"] = f"Default: `{default_str}`"

    return vscode_attr


def create_tag_definition(component_name: str, component_def: Dict[str, Any]) -> Dict[str, Any]:
    """Create a VSCode tag definition from a component definition."""
    tag = {
        "name": f"c-{component_name}",
        "description": component_def.get('description', f"RVO {component_name} component")
    }

    # Convert attributes
    attributes = []
    for attr in component_def.get('attributes', []):
        vscode_attr = create_attribute_definition(attr)
        attributes.append(vscode_attr)

    if attributes:
        tag["attributes"] = attributes

    return tag


def generate_vscode_custom_data() -> Dict[str, Any]:
    """Generate the complete VSCode custom data structure."""
    definitions = load_definitions()

    custom_data = {
        "version": 1.1,
        "tags": []
    }

    # Add all components
    components_added = []
    for comp in definitions.get('components', []):
        tag = create_tag_definition(comp['name'], comp)
        custom_data["tags"].append(tag)
        components_added.append(comp['name'])

    # Add aliases
    for alias in definitions.get('aliases', []):
        alias_name = alias['name']
        target_name = alias.get('target_component')

        # Find the target component
        target_comp = None
        for comp in definitions.get('components', []):
            if comp['name'] == target_name:
                target_comp = comp
                break

        if not target_comp:
            print(f"Warning: Alias '{alias_name}' references unknown component '{target_name}'")
            continue

        # Create merged definition for alias
        merged_def = target_comp.copy()
        merged_def['description'] = alias.get('description', target_comp['description'])

        # Apply default attributes to the merged definition
        default_attrs = alias.get('default_attributes', {})
        if default_attrs:
            merged_attrs = []
            for attr in target_comp.get('attributes', []):
                attr_copy = attr.copy()
                if attr['name'] in default_attrs:
                    attr_copy['default'] = default_attrs[attr['name']]
                merged_attrs.append(attr_copy)
            merged_def['attributes'] = merged_attrs

        tag = create_tag_definition(alias_name, merged_def)
        custom_data["tags"].append(tag)
        components_added.append(alias_name)

    return custom_data, components_added


def main():
    """Generate VSCode custom data file."""
    print("Generating VSCode custom data from definitions.json...")
    print("=" * 60)

    custom_data, components_added = generate_vscode_custom_data()

    # Write to file
    root_dir = Path(__file__).parent.parent
    output_path = root_dir / "src" / "jinja_roos_components" / "custom_data.json"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(custom_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Generated custom_data.json with {len(custom_data['tags'])} tags")
    print(f"\n📄 Output file: {output_path}")
    print("\nComponents included:")
    for name in sorted(components_added):
        print(f"  - c-{name}")

    print("\n" + "=" * 60)
    print("To use in VSCode, add to your .vscode/settings.json:")
    print(json.dumps({
        "html.customData": ["./custom_data.json"]
    }, indent=2))
    print("=" * 60)


if __name__ == '__main__':
    main()
