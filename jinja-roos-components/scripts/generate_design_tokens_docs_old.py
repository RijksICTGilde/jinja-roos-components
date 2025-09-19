#!/usr/bin/env python3
"""
Extract colors and icons from the ROOS design token files and generate HTML documentation 
using our component system.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import json

# Add parent directory to path to import jinja_roos_components
sys.path.insert(0, str(Path(__file__).parent.parent))

from jinja2 import Environment, FileSystemLoader
from jinja_roos_components import setup_components


def extract_colors_from_css(css_file_path: str) -> List[Dict[str, str]]:
    """Extract color variables from CSS file."""
    colors = []
    
    with open(css_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match CSS color variables: --rvo-color-name: #hexvalue;
    color_pattern = r'--rvo-color-([^:]+):\s*([#A-Fa-f0-9]{6,8}|[#A-Fa-f0-9]{3});'
    matches = re.findall(color_pattern, content)
    
    for name, hex_value in matches:
        # Clean up the name and ensure hex value is properly formatted
        clean_name = name.strip()
        clean_hex = hex_value.upper()
        if not clean_hex.startswith('#'):
            clean_hex = '#' + clean_hex
        
        # Skip numbered variants for now to reduce clutter
        if any(char.isdigit() for char in clean_name.split('-')[-1]):
            continue
            
        colors.append({
            'name': clean_name,
            'variable': f'--rvo-color-{clean_name}',
            'hex': clean_hex,
            'display_name': clean_name.replace('-', ' ').title()
        })
    
    # Sort by name for consistent ordering
    colors.sort(key=lambda x: x['name'])
    return colors


def extract_icons_from_types(types_file_path: str) -> List[Dict[str, str]]:
    """Extract icon names from the TypeScript types file."""
    icons = []
    
    with open(types_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract icon names from TypeScript union type
    # Pattern matches: | 'icon-name'
    pattern = r"\|\s*'([^']+)'"
    matches = re.findall(pattern, content)
    
    # Group icons by category (rough categorization based on name patterns)
    category_patterns = {
        'activiteiten': ['persoon', 'man', 'vrouw', 'kind', 'gesprek', 'presentatie', 'trouwen'],
        'computer-internet': ['computer', 'laptop', 'internet', 'app', 'digitaal', 'cyber', 'data'],
        'transport': ['auto', 'fiets', 'bus', 'trein', 'vliegtuig', 'schip', 'motor'],
        'gebouwen': ['huis', 'gebouw', 'school', 'kantoor', 'fabriek', 'flat', 'villa'],
        'natuur': ['boom', 'plant', 'water', 'dier', 'zon', 'weer', 'milieu'],
        'interface': ['home', 'menu', 'zoek', 'info', 'plus', 'kruis', 'pijl', 'kalender'],
        'medisch': ['hart', 'medicijn', 'arts', 'zorg', 'gezondheid'],
        'financieel': ['geld', 'munt', 'betalen', 'belasting', 'budget'],
        'overheid': ['nederland', 'gemeente', 'wet', 'stemmen', 'koninkrijk']
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
            'display_name': icon_name.replace('-', ' ').title(),
            'category': category,
            'css_class': f'rvo-icon-{icon_name}'
        })
    
    # Sort by category then name for consistent ordering
    icons.sort(key=lambda x: (x['category'], x['name']))
    return icons


def generate_colors_page(colors: List[Dict[str, str]], base_path: Path) -> str:
    """Generate Jinja2 template for colors page using our component system."""
    
    template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROOS Colors Reference</title>
    <link rel="stylesheet" href="/static/roos/dist/roos.css">
</head>
<body>

<c-page title="ROOS Colors Reference" class="rvo-max-width-layout--lg">
    
    <c-link href="component-reference.html" class="rvo-link--back">
        ← Back to Components Reference
    </c-link>
    
    <div class="rvo-layout-row rvo-layout-gap--md">
        <div class="rvo-layout-column rvo-layout-column--span-12">
            
            <c-heading type="h2" textContent="Color Palette" />
            <p>These are the official colors from the ROOS design system. Use the CSS custom properties in your components.</p>
            
            <div class="color-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; margin-top: 2rem;">
                {% for color in colors %}
                <c-card padding="md" class="color-card" style="border: 1px solid #e1e4e8;">
                    <div class="color-swatch" style="
                        height: 80px; 
                        background-color: {{ color.hex }}; 
                        border-radius: 4px; 
                        margin-bottom: 1rem;
                        border: 1px solid #dee2e6;
                    "></div>
                    
                    <c-heading type="h4" textContent="{{ color.display_name }}" style="margin-bottom: 0.5rem; color: #01689b;" />
                    
                    <code style="
                        font-family: 'Courier New', monospace; 
                        font-size: 0.8rem; 
                        color: #666; 
                        display: block; 
                        margin-bottom: 0.25rem;
                        word-break: break-all;
                    ">{{ color.variable }}</code>
                    
                    <code style="
                        font-family: 'Courier New', monospace; 
                        font-size: 0.9rem; 
                        background: #f1f3f4; 
                        padding: 2px 6px; 
                        border-radius: 3px; 
                        display: inline-block;
                    ">{{ color.hex }}</code>
                </c-card>
                {% endfor %}
            </div>
            
        </div>
    </div>
    
    <footer style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #e1e4e8; text-align: center; color: #666;">
        <p>Generated on {{ generation_date }}</p>
        <p>ROOS Components v0.1.0 - {{ colors|length }} colors available</p>
    </footer>
    
</c-page>

</body>
</html>'''

    return template_content


def generate_icons_page(icons: List[Dict[str, str]], base_path: Path) -> str:
    """Generate Jinja2 template for icons page using our component system."""
    
    # Group icons by category
    categories = {}
    for icon in icons:
        category = icon['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(icon)
    
    template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROOS Icons Reference</title>
    <link rel="stylesheet" href="/static/roos/dist/roos.css">
</head>
<body>

<c-page title="ROOS Icons Reference" class="rvo-max-width-layout--lg">
    
    <c-link href="component-reference.html" class="rvo-link--back">
        ← Back to Components Reference
    </c-link>
    
    <div class="rvo-layout-row rvo-layout-gap--md">
        <div class="rvo-layout-column rvo-layout-column--span-12">
            
            <c-heading type="h2" textContent="Icon Library" />
            <p>All available icons from the ROOS design system. Use the icon name in the <code>icon</code> attribute of the icon component.</p>
            
            {% for category, category_icons in categories.items() %}
            <section style="margin-bottom: 3rem;">
                <c-heading type="h3" textContent="{{ category.replace('-', ' ').title() }}" />
                
                <div class="icon-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; margin-top: 1rem;">
                    {% for icon in category_icons %}
                    <c-card padding="md" class="icon-card" style="border: 1px solid #e1e4e8; transition: transform 0.2s;">
                        <div style="
                            height: 60px; 
                            display: flex; 
                            align-items: center; 
                            justify-content: center; 
                            background: #f8f9fa; 
                            border-radius: 4px; 
                            margin-bottom: 1rem;
                        ">
                            <c-icon icon="{{ icon.name }}" size="xl"/>
                        </div>
                        
                        <c-heading type="h5" textContent="{{ icon.display_name }}" style="margin-bottom: 0.5rem; color: #01689b; font-size: 0.9rem;" />
                        
                        <code style="
                            font-family: 'Courier New', monospace; 
                            font-size: 0.75rem; 
                            color: #666; 
                            display: block; 
                            margin-bottom: 0.5rem;
                            word-break: break-all;
                        ">icon="{{ icon.name }}"</code>
                        
                        <code style="
                            font-family: 'Courier New', monospace; 
                            font-size: 0.7rem; 
                            background: #f1f3f4; 
                            padding: 4px 6px; 
                            border-radius: 3px; 
                            word-break: break-all;
                        ">&lt;c-icon icon="{{ icon.name }}" /&gt;</code>
                    </c-card>
                    {% endfor %}
                </div>
            </section>
            {% endfor %}
            
        </div>
    </div>
    
    <footer style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #e1e4e8; text-align: center; color: #666;">
        <p>Generated on {{ generation_date }}</p>
        <p>ROOS Components v0.1.0 - {{ icons|length }} icons in {{ categories.keys()|length }} categories</p>
    </footer>
    
</c-page>

</body>
</html>'''

    return template_content


def main():
    """Main function to extract colors and icons and generate template files."""
    
    # Get the base path of the project
    base_path = Path(__file__).parent.parent
    examples_dir = base_path / "examples"
    static_dir = examples_dir / "static"
    
    # Paths to the source files
    design_tokens_path = base_path / "node_modules" / "@nl-rvo" / "design-tokens" / "dist" / "index.css"
    types_path = base_path / "node_modules" / "@nl-rvo" / "assets" / "icons" / "types.ts"
    
    # Check if files exist
    if not design_tokens_path.exists():
        print(f"Error: Design tokens file not found: {design_tokens_path}")
        return 1
    
    if not types_path.exists():
        print(f"Error: Types file not found: {types_path}")
        return 1
    
    # Extract colors and icons
    print("Extracting colors...")
    colors = extract_colors_from_css(str(design_tokens_path))
    print(f"Found {len(colors)} colors")
    
    print("Extracting icons...")
    icons = extract_icons_from_types(str(types_path))
    print(f"Found {len(icons)} icons")
    
    # Group icons by category for display
    categories = {}
    for icon in icons:
        category = icon['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(icon)
    
    # Generate template files
    print("Generating colors template...")
    colors_template = generate_colors_page(colors, base_path)
    colors_file = examples_dir / "templates" / "colors-reference.html.j2"
    colors_file.parent.mkdir(parents=True, exist_ok=True)
    colors_file.write_text(colors_template, encoding='utf-8')
    print(f"Colors template generated: {colors_file}")
    
    print("Generating icons template...")
    icons_template = generate_icons_page(icons, base_path)
    icons_file = examples_dir / "templates" / "icons-reference.html.j2"
    icons_file.write_text(icons_template, encoding='utf-8')
    print(f"Icons template generated: {icons_file}")
    
    # Now render the templates to HTML using our component system
    print("Rendering templates to HTML...")
    
    # Setup Jinja2 environment with our components
    env = Environment(loader=FileSystemLoader([
        str(examples_dir / "templates"),
        str(base_path / "jinja_roos_components" / "templates")
    ]))
    setup_components(env)
    
    # Render colors page
    colors_template_obj = env.get_template("colors-reference.html.j2")
    colors_html = colors_template_obj.render(
        colors=colors,
        generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    colors_html_file = static_dir / "colors-reference.html"
    colors_html_file.write_text(colors_html, encoding='utf-8')
    print(f"Colors HTML generated: {colors_html_file}")
    
    # Render icons page
    icons_template_obj = env.get_template("icons-reference.html.j2")
    icons_html = icons_template_obj.render(
        icons=icons,
        categories=categories,
        generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    icons_html_file = static_dir / "icons-reference.html"
    icons_html_file.write_text(icons_html, encoding='utf-8')
    print(f"Icons HTML generated: {icons_html_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())