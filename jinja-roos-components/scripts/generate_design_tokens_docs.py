#!/usr/bin/env python3
"""
Generate comprehensive design tokens documentation from the ROOS source files.
This script reads JSON token files and creates HTML documentation using our component system.
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

from jinja2 import Environment, FileSystemLoader
from jinja_roos_components import setup_components


def extract_colors_from_tokens(color_tokens_path: str) -> List[Dict[str, str]]:
    """Extract color variables from the JSON tokens file."""
    colors = []
    
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


def extract_spacing_and_sizing(space_tokens_path: str, size_tokens_path: str) -> Dict[str, List[Dict[str, str]]]:
    """Extract spacing and sizing information from JSON tokens."""
    
    # Load space tokens
    with open(space_tokens_path, 'r', encoding='utf-8') as f:
        space_data = json.load(f)
    
    # Load size tokens  
    with open(size_tokens_path, 'r', encoding='utf-8') as f:
        size_data = json.load(f)
    
    space_tokens = []
    space_values = space_data.get('rvo', {}).get('space', {})
    for name, info in space_values.items():
        space_tokens.append({
            'name': name,
            'template_name': name.lower(),
            'display_name': name.upper(),
            'value': info.get('value', ''),
            'css_variable': f'--rvo-space-{name}'
        })
    
    size_tokens = []
    size_values = size_data.get('rvo', {}).get('size', {})
    for name, info in size_values.items():
        size_tokens.append({
            'name': name,
            'template_name': name.lower(),
            'display_name': name.upper(),
            'value': info.get('value', ''),
            'css_variable': f'--rvo-size-{name}'
        })
    
    return {
        'spacing': space_tokens,
        'sizing': size_tokens
    }


def extract_icons_from_types(types_file_path: str) -> List[Dict[str, str]]:
    """Extract icon names from the TypeScript types file."""
    icons = []
    
    with open(types_file_path, 'r', encoding='utf-8') as f:
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


def generate_colors_page_template() -> str:
    """Generate Jinja2 template for colors page using our component system."""
    
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROOS Colors Reference</title>
    <link rel="stylesheet" href="/static/roos/dist/roos.css">
</head>
<body>
<c-page title="ROOS Colors Reference" class="rvo-max-width-layout--lg">
    
    <div class="rvo-layout-row rvo-layout-gap--md">
        <div class="rvo-layout-column rvo-layout-column--span-12">
            
            <c-link href="component-reference.html" class="rvo-link--back">
                ← Back to Components Reference
            </c-link>
            
            <c-heading type="h2" textContent="Color Palette" style="margin-top: 2rem;" />
            <p>Essential colors organized by primary, accent, and neutral tones.</p>
            
            {% set color_groups = colors | groupby('base_color') %}
            {% for base_color, color_list in color_groups %}
            
            <section style="margin-bottom: 2.5rem;">
                <c-heading type="h3" textContent="{{ base_color.title() }}" style="margin-bottom: 1rem; color: #01689b;" />
                
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem;">
                    {% for color in color_list %}
                    <div style="background: white; border: 1px solid #e1e4e8; border-radius: 8px; padding: 1rem;">
                        <div style="
                            height: 60px; 
                            background-color: {{ color.hex }}; 
                            border-radius: 4px; 
                            margin-bottom: 0.75rem;
                            border: 1px solid rgba(0,0,0,0.1);
                            position: relative;
                        ">
                            <span style="
                                position: absolute;
                                bottom: 4px;
                                right: 6px;
                                background: rgba(255,255,255,0.95); 
                                padding: 2px 4px; 
                                border-radius: 2px; 
                                font-size: 0.7rem; 
                                font-weight: 600;
                                color: #333;
                                font-family: monospace;
                            ">{{ color.hex }}</span>
                        </div>
                        
                        <div style="font-weight: 600; margin-bottom: 0.25rem; color: #333;">{{ color.display_name }}</div>
                        <div style="font-size: 0.8rem; color: #666; font-family: monospace;">color="{{ color.template_name }}"</div>
                    </div>
                    {% endfor %}
                </div>
            </section>
            {% endfor %}
            
        </div>
    </div>
    
    <footer style="margin-top: 3rem; padding: 2rem 0; border-top: 1px solid #e1e4e8; text-align: center; color: #666; font-size: 0.9rem;">
        <p>ROOS Components v0.1.0 • {{ colors|length }} colors • Generated {{ generation_date }}</p>
    </footer>
    
</c-page>
</body>
</html>
'''


def generate_icons_page_template() -> str:
    """Generate Jinja2 template for icons page using our component system."""
    
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROOS Icons Reference</title>
    <link rel="stylesheet" href="/static/roos/dist/roos.css">
</head>
<body>
<c-page title="ROOS Icons Reference" class="rvo-max-width-layout--lg">
    
    <div class="rvo-layout-row rvo-layout-gap--md">
        <div class="rvo-layout-column rvo-layout-column--span-12">
            
            <c-link href="component-reference.html" class="rvo-link--back">
                ← Back to Components Reference
            </c-link>
            
            <c-heading type="h2" textContent="Icon Library" style="margin-top: 2rem;" />
            <p>Essential icons organized by category. Available in 5 sizes.</p>
            
            {% set icon_groups = icons | groupby('category') %}
            {% for category, category_icons in icon_groups %}
            
            <section style="margin-bottom: 2.5rem;">
                <c-heading type="h3" textContent="{{ category_icons[0].category_display }}" style="margin-bottom: 1rem; color: #01689b;" />
                <p style="color: #666; margin-bottom: 1rem; font-size: 0.9rem;">{{ category_icons|length }} icons</p>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 0.75rem;">
                    {% for icon in category_icons %}
                    <div style="background: white; border: 1px solid #e1e4e8; border-radius: 6px; padding: 0.75rem; text-align: center;">
                        <div style="
                            height: 50px; 
                            display: flex; 
                            align-items: center; 
                            justify-content: center; 
                            background: #f8f9fa; 
                            border-radius: 4px; 
                            margin-bottom: 0.5rem;
                        ">
                            <c-icon icon="{{ icon.name }}" size="lg"/>
                        </div>
                        
                        <div style="font-weight: 600; margin-bottom: 0.25rem; color: #333; font-size: 0.8rem;">{{ icon.display_name }}</div>
                        <div style="font-size: 0.7rem; color: #666; font-family: monospace; word-break: break-all;">{{ icon.template_name }}</div>
                    </div>
                    {% endfor %}
                </div>
            </section>
            {% endfor %}
            
        </div>
    </div>
    
    <footer style="margin-top: 3rem; padding: 2rem 0; border-top: 1px solid #e1e4e8; text-align: center; color: #666; font-size: 0.9rem;">
        <p>ROOS Components v0.1.0 • {{ icons|length }} icons • Generated {{ generation_date }}</p>
    </footer>
    
</c-page>
</body>
</html>
'''


def generate_spacing_page_template() -> str:
    """Generate Jinja2 template for spacing/sizing page using our component system."""
    
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROOS Spacing & Sizing Reference</title>
    <link rel="stylesheet" href="/static/roos/dist/roos.css">
</head>
<body>
<c-page title="ROOS Spacing & Sizing Reference" class="rvo-max-width-layout--lg">
    
    <div class="rvo-layout-row rvo-layout-gap--md">
        <div class="rvo-layout-column rvo-layout-column--span-12">
            
            <c-link href="component-reference.html" class="rvo-link--back">
                ← Back to Components Reference
            </c-link>
            
            <!-- Spacing Section -->
            <section style="margin-top: 2rem;">
                <c-heading type="h2" textContent="Spacing Scale" />
                <p>Consistent spacing for margins, padding, and gaps.</p>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; margin-top: 1.5rem;">
                    {% for space in spacing %}
                    <div style="background: white; border: 1px solid #e1e4e8; border-radius: 8px; padding: 1rem;">
                        <div style="margin-bottom: 0.75rem;">
                            <div style="
                                height: 30px; 
                                background: #007BC7;
                                border-radius: 2px;
                                width: {{ space.value }};
                                max-width: 100%;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                color: white;
                                font-size: 0.7rem;
                                font-weight: 600;
                                font-family: monospace;
                            ">{{ space.value }}</div>
                        </div>
                        
                        <div style="font-weight: 600; margin-bottom: 0.25rem; color: #333;">{{ space.display_name }}</div>
                        <div style="font-size: 0.8rem; color: #666; font-family: monospace;">padding="{{ space.template_name }}"</div>
                    </div>
                    {% endfor %}
                </div>
            </section>
            
            <!-- Sizing Section -->
            <section style="margin-top: 3rem;">
                <c-heading type="h2" textContent="Sizing Scale" />
                <p>Consistent sizing for element dimensions.</p>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; margin-top: 1.5rem;">
                    {% for size in sizing %}
                    <div style="background: white; border: 1px solid #e1e4e8; border-radius: 8px; padding: 1rem; text-align: center;">
                        <div style="margin-bottom: 0.75rem; display: flex; align-items: center; justify-content: center; height: 60px;">
                            <div style="
                                width: {{ size.value }}; 
                                height: {{ size.value }}; 
                                background: #007BC7;
                                border-radius: 2px;
                                max-width: 100%;
                                max-height: 100%;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                color: white;
                                font-size: 0.7rem;
                                font-weight: 600;
                                font-family: monospace;
                            ">{{ size.value }}</div>
                        </div>
                        
                        <div style="font-weight: 600; margin-bottom: 0.25rem; color: #333;">{{ size.display_name }}</div>
                        <div style="font-size: 0.8rem; color: #666; font-family: monospace;">size="{{ size.template_name }}"</div>
                    </div>
                    {% endfor %}
                </div>
            </section>
            
        </div>
    </div>
    
    <footer style="margin-top: 3rem; padding: 2rem 0; border-top: 1px solid #e1e4e8; text-align: center; color: #666; font-size: 0.9rem;">
        <p>ROOS Components v0.1.0 • {{ spacing|length }} spacing & {{ sizing|length }} sizing tokens • Generated {{ generation_date }}</p>
    </footer>
    
</c-page>
</body>
</html>
'''


def main():
    """Main function to extract design tokens and generate comprehensive documentation."""
    
    # Get the base path of the project
    base_path = Path(__file__).parent.parent
    static_dir = base_path / "examples" / "static"
    templates_dir = base_path / "examples" / "templates"
    
    # Ensure directories exist
    static_dir.mkdir(parents=True, exist_ok=True)
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    # Paths to the source files
    color_tokens_path = base_path / "node_modules" / "@nl-rvo" / "design-tokens" / "src" / "brand" / "rvo" / "color.tokens.json"
    space_tokens_path = base_path / "node_modules" / "@nl-rvo" / "design-tokens" / "src" / "brand" / "rvo" / "space.tokens.json"
    size_tokens_path = base_path / "node_modules" / "@nl-rvo" / "design-tokens" / "src" / "brand" / "rvo" / "size.tokens.json"
    types_path = base_path / "node_modules" / "@nl-rvo" / "assets" / "icons" / "types.ts"
    
    # Check if files exist
    missing_files = []
    for path, name in [(color_tokens_path, "color tokens"), (space_tokens_path, "space tokens"), 
                       (size_tokens_path, "size tokens"), (types_path, "icon types")]:
        if not path.exists():
            missing_files.append(f"{name}: {path}")
    
    if missing_files:
        print("Error: Required files not found:")
        for file in missing_files:
            print(f"  - {file}")
        return 1
    
    # Extract all design tokens
    print("Extracting colors...")
    colors = extract_colors_from_tokens(str(color_tokens_path))
    print(f"Found {len(colors)} colors")
    
    print("Extracting spacing and sizing...")
    spacing_sizing = extract_spacing_and_sizing(str(space_tokens_path), str(size_tokens_path))
    print(f"Found {len(spacing_sizing['spacing'])} spacing tokens, {len(spacing_sizing['sizing'])} sizing tokens")
    
    print("Extracting icons...")
    icons = extract_icons_from_types(str(types_path))
    print(f"Found {len(icons)} icons")
    
    # Generate template files
    print("Generating templates...")
    
    # Colors template
    colors_template = generate_colors_page_template()
    colors_template_file = templates_dir / "colors-reference.html.j2"
    colors_template_file.write_text(colors_template, encoding='utf-8')
    
    # Icons template
    icons_template = generate_icons_page_template()
    icons_template_file = templates_dir / "icons-reference.html.j2"
    icons_template_file.write_text(icons_template, encoding='utf-8')
    
    # Spacing template
    spacing_template = generate_spacing_page_template()
    spacing_template_file = templates_dir / "spacing-reference.html.j2"
    spacing_template_file.write_text(spacing_template, encoding='utf-8')
    
    print(f"Templates generated in: {templates_dir}")
    
    # Setup Jinja2 environment with our components
    env = Environment(loader=FileSystemLoader([
        str(templates_dir),
        str(base_path / "jinja_roos_components" / "templates")
    ]))
    setup_components(env)
    
    # Render HTML files
    print("Rendering HTML files...")
    
    generation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Colors page
    colors_template_obj = env.get_template("colors-reference.html.j2")
    colors_html = colors_template_obj.render(
        colors=colors,
        generation_date=generation_date
    )
    colors_html_file = static_dir / "colors-reference.html"
    colors_html_file.write_text(colors_html, encoding='utf-8')
    print(f"Colors page: {colors_html_file}")
    
    # Icons page  
    icons_template_obj = env.get_template("icons-reference.html.j2")
    icons_html = icons_template_obj.render(
        icons=icons,
        generation_date=generation_date
    )
    icons_html_file = static_dir / "icons-reference.html"
    icons_html_file.write_text(icons_html, encoding='utf-8')
    print(f"Icons page: {icons_html_file}")
    
    # Spacing page
    spacing_template_obj = env.get_template("spacing-reference.html.j2")
    spacing_html = spacing_template_obj.render(
        spacing=spacing_sizing['spacing'],
        sizing=spacing_sizing['sizing'],
        generation_date=generation_date
    )
    spacing_html_file = static_dir / "spacing-reference.html"
    spacing_html_file.write_text(spacing_html, encoding='utf-8')
    print(f"Spacing page: {spacing_html_file}")
    
    print("\n✅ Design tokens documentation generated successfully!")
    print(f"📊 Statistics:")
    print(f"   • {len(colors)} colors")
    print(f"   • {len(icons)} icons")
    print(f"   • {len(spacing_sizing['spacing'])} spacing tokens")
    print(f"   • {len(spacing_sizing['sizing'])} sizing tokens")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())