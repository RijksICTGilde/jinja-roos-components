#!/usr/bin/env python3
"""
Extract design tokens from @nl-rvo/design-tokens package.
Extracts colors, spacing, sizing, and icons for documentation generation.
"""

import json
import re
from pathlib import Path
from typing import List, Dict


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


def update_definitions_file():
    """Update the definitions.json file with extracted design token data."""
    # Get paths
    definitions_path = Path(__file__).parent / "design_tokens.json"

    if not definitions_path.exists():
        definitions = {}
    else:
        # Load existing definitions
        with open(definitions_path, 'r', encoding='utf-8') as f:
            definitions = json.load(f)

    # Extract colors from design tokens
    colors_data = extract_colors_from_tokens()
    if not colors_data:
        print("❌ No colors found in design tokens. Make sure @nl-rvo/design-tokens is installed.")
        return False

    # Extract icons from types
    icons_data = extract_icons_from_types()
    if not icons_data:
        print("❌ No icons found in types. Make sure @nl-rvo/assets is installed.")
        return False

    # Update the colors and icons sections with full metadata
    definitions['colors'] = colors_data
    definitions['icons'] = icons_data

    # Write back to file
    with open(definitions_path, 'w', encoding='utf-8') as f:
        json.dump(definitions, f, indent=2, ensure_ascii=False)

    print(f"✓ Updated definitions.json with {len(colors_data)} colors")
    print(f"✓ Updated definitions.json with {len(icons_data)} icons")
    return True


if __name__ == '__main__':
    """Run extraction when executed directly."""
    print("Extracting design tokens from @nl-rvo packages...")
    print("=" * 60)

    colors = extract_colors_from_tokens()
    print(f"✓ Extracted {len(colors)} colors")

    spacing_sizing = extract_spacing_and_sizing()
    print(f"✓ Extracted {len(spacing_sizing['spacing'])} spacing tokens")
    print(f"✓ Extracted {len(spacing_sizing['sizing'])} sizing tokens")

    icons = extract_icons_from_types()
    print(f"✓ Extracted {len(icons)} icons")

    print("\n" + "=" * 60)
    print("Updating definitions.json with design token metadata...")
    print("=" * 60)

    if update_definitions_file():
        print("\n✅ Successfully updated definitions.json!")
        print("   - Colors: hex values, display names, and sorting")
        print("   - Icons: names, categories, and display names")
        print("   The @nl-rvo packages are no longer needed at runtime.")
    else:
        print("\n❌ Failed to update definitions.json")

    print("\nDone!")
