#!/usr/bin/env python3
"""
Generate aggregated web-types.json from individual component web-types files.

This script scans the components directory for *.web-types.json files and
combines them into a single web-types.json file that IntelliJ can use for
autocompletion and validation of Jinja2 components.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any

def find_component_web_types(components_dir: Path) -> List[Path]:
    """Find all web-types.json files in the components directory."""
    return list(components_dir.glob("*.web-types.json"))

def load_component_web_type(file_path: Path) -> Dict[str, Any]:
    """Load a single component web-type definition."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_main_web_types(components: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate the main web-types.json structure."""
    return {
        "$schema": "https://raw.githubusercontent.com/JetBrains/web-types/master/schema/web-types.json",
        "name": "jinja-roos-components",
        "version": "1.0.0",
        "description": "RVO Design System components for Jinja2 templates",
        "contributions": {
            "html": {
                "elements": components,
                "description-markup": "markdown",
                "types-syntax": "typescript"
            }
        }
    }

def add_component_defaults(component: Dict[str, Any]) -> Dict[str, Any]:
    """Add default values and structure to component definition."""
    # Ensure component has required fields
    if "name" not in component:
        raise ValueError(f"Component missing 'name' field")
    
    # Add default description if missing
    if "description" not in component:
        component["description"] = f"RVO {component['name']} component"
    
    # Ensure attributes exist
    if "attributes" not in component:
        component["attributes"] = []
    
    return component

def main():
    # Setup paths
    root_dir = Path(__file__).parent
    components_dir = root_dir / "jinja_roos_components" / "templates" / "components"
    output_file = root_dir / "web-types.json"
    
    # Find all component web-types files
    web_type_files = find_component_web_types(components_dir)
    
    if not web_type_files:
        print(f"No web-types.json files found in {components_dir}")
        return
    
    print(f"Found {len(web_type_files)} component web-type definitions")
    
    # Load all component definitions
    components = []
    for file_path in sorted(web_type_files):
        try:
            print(f"  Loading: {file_path.name}")
            component = load_component_web_type(file_path)
            component = add_component_defaults(component)
            components.append(component)
        except Exception as e:
            print(f"  ERROR loading {file_path.name}: {e}")
            continue
    
    # Generate main web-types structure
    web_types = generate_main_web_types(components)
    
    # Write output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(web_types, f, indent=2, ensure_ascii=False)
    
    print(f"\nGenerated {output_file}")
    print(f"Total components: {len(components)}")
    
    # Also generate a package.json entry if needed
    package_json_path = root_dir / "package.json"
    if package_json_path.exists():
        with open(package_json_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        # Add web-types reference if not present
        if "web-types" not in package_data:
            package_data["web-types"] = "./web-types.json"
            with open(package_json_path, 'w', encoding='utf-8') as f:
                json.dump(package_data, f, indent=2, ensure_ascii=False)
            print(f"Updated package.json with web-types reference")

if __name__ == "__main__":
    main()