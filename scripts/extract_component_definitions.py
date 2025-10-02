"""
Extract component definitions from RVO components.

This script iterates over all components in rvo/components and extracts
their definitions, combining them into a single JSON file.


Prep:
- place rvo folder in main tree (https://github.com/nl-design-system/rvo)
"""

import json
from pathlib import Path
from typing import Dict, Any
import re

types_found = set()

def extract_component_definition(component_name:str, component_dir: Path) -> Dict[str, Any]:
    
    template_file = component_dir / 'src' / 'template.tsx'
    defaults_file = component_dir / 'src' / 'defaultArgs.ts'

    pattern = r"^(?P<attribute_name>[a-zA-Z]+)(?P<optional>\?)?:\s*(?P<attribute_type>.+);$"
    # example = "kind?: 'primary' | 'secondary' | 'tertiary' | 'quaternary' | 'subtle' | 'warning-subtle' | 'warning';"
    # argument_name = "kind", attribute_type = " 'primary' | 'secondary' | 'tertiary' | 'quaternary' | 'subtle' | 'warning-subtle' | 'warning'"

    # TODO: write logic here to parse out default values from file

    # TODO: now only first def found, might be more
    # at least one file, add alterting when more found!

    attributes = []
    interface_def = False
    with open(template_file) as f:
        for line in f.readlines():

            attribute_group = {}

            # strip everything after comments
            if '//' in line:
                line = line[0:line.find('//')]

            line = line.strip()

            if line.startswith('export interface'):
                if not line.endswith('}'):  # nothing in it
                    interface_def = True
                continue
            if interface_def and line.startswith('}'):
                interface_def = False
                break
            if line.startswith('/**'):  # comment line, TODO: assuming online single line comments
                continue

            if not interface_def:
                continue

            match = re.match(pattern, line)
            if match is None:
                print(line)

            attribute_group['name'] = match['attribute_name']
            attribute_types = [match['attribute_type']]

            if match['optional'] is None:  # ? not in line
                attribute_group['required'] = True
            else:
                attribute_group['required'] = False

            if attribute_types[0].startswith('('):
                attribute_group["func_type"] = attribute_types[0]
                attribute_types = ["func"]

            if '|' not in attribute_types[0] and (attribute_types[0][0]=="'" and attribute_types[0][-1]=="'"):
                attribute_group["enum_vals"] = [attribute_types[0][1:-1]]
                attribute_types = ["enum"]

            if '|' in attribute_types[0]:
                is_enum = False
                enum_vals = []
                types = []
                for part in attribute_types[0].split('|'):
                    part = part.strip()
                    is_string_literal = (part[0]== "'" and part[-1]=="'")
                    if is_string_literal:  # string literal
                        enum_vals.append(part[1:-1])
                        is_enum = True
                    else:
                        types.append(part)

                if is_enum:
                    types.append("enum")
                    attribute_group["enum_vals"] = enum_vals

                attribute_types = types
                    
            attribute_group["type"] = attribute_types

            for tp in attribute_types:
                if tp[-2::]=="[]":
                    types_found.add(tp[0:-2])
                else:
                    types_found.add(tp)

            attributes.append(attribute_group)

    return {
        "name": component_name,
        "attributes": attributes
    }


def main():
    """Main entry point for the script."""
    components_dir = Path(__file__).parent.parent / "rvo" / "components"
    output_file = Path(__file__).parent.parent / "component-definitions.json"

    # Collect all component definitions
    definitions = []
    skip = {
        'utils',
        'form-checkbox',  # multiline-comment in template
        'form-checkbox-group',  # multiline-comment in template
        'form-radio-button',  # multiline-comment in template
        'form-radio-button-group',  # multiline-comment in template
        'grid', # multi-line type in template
        'menubar',  # different folder structure in template
        'menubar-mobile',  # different folder structure in template
        'skeleton', # multi-line type in template
        'tabs',  # multiline-comment in template
    }

    # Iterate over all component directories
    for component_dir in sorted(components_dir.iterdir()):
        # Skip non-directories and special files
        if not component_dir.is_dir() or component_dir.name in skip:
            continue

        component_name = component_dir.name
        print(f"Processing component: {component_dir}")

        # Extract definition for this component
        definition = extract_component_definition(component_name, component_dir)
        definitions.append(definition)

    # Write all definitions to output file
    print(f"\nWriting definitions for {len(definitions)} components to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(definitions, f, indent=2, ensure_ascii=False)

    print("Done!")

    # TODO: this list should ideally be completely defined to the attribute level:
    # - nesting is missing (e.g. IconType, but also others)
    # - som
    print('types found:', len(types_found))
    for type in types_found:
        print(type)


if __name__ == "__main__":#
    main()
