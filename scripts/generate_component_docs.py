#!/usr/bin/env python3
"""
Generate component documentation HTML from the component registry.
This script reads all component definitions and creates a comprehensive HTML documentation file.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add parent directory to path to import jinja_roos_components
sys.path.insert(0, str(Path(__file__).parent.parent))

from jinja_roos_components.registry import ComponentRegistry, AttributeType
from jinja2 import Environment, FileSystemLoader
from jinja_roos_components import setup_components


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


def generate_example_code(component_name: str, attributes: List[Dict]) -> str:
    """Generate realistic example HTML code for a component."""
    
    # Component-specific examples with realistic content
    examples = {
        'button': '<c-button variant="primary">Click me</c-button>',
        'card': '<c-card title="Card Title">\n    <p>Card content goes here.</p>\n</c-card>',
        'input': '<c-input label="Email" type="email" placeholder="Enter your email" />',
        'select': '<c-select label="Choose option" :options="[\'Option 1\', \'Option 2\', \'Option 3\']" />',
        'checkbox': '<c-checkbox label="I agree to the terms" />',
        'radio': '<c-radio name="choice" value="option1" label="Option 1" />',
        'textarea': '<c-textarea label="Message" placeholder="Enter your message" />',
        'alert': '<c-alert variant="info">This is an information message</c-alert>',
        'tag': '<c-tag>Important</c-tag>',
        'link': '<c-link href="https://example.com">Visit our website</c-link>',
        'heading': '<c-heading level="2">Section Title</c-heading>',
        'list': '<c-list>\n    <c-list-item>First item</c-list-item>\n    <c-list-item>Second item</c-list-item>\n</c-list>',
        'page': '<c-page title="My Page">\n    <h1>Welcome to my page</h1>\n    <p>Page content here.</p>\n</c-page>',
        'header': '<c-header>\n    <h1>Site Header</h1>\n</c-header>',
        'footer': '<c-footer>\n    <p>&copy; 2025 My Company</p>\n</c-footer>',
        'hero': '<c-hero title="Welcome" subtitle="Get started with our amazing product" />',
        'grid': '<c-grid>\n    <div>Grid item 1</div>\n    <div>Grid item 2</div>\n</c-grid>',
        'layout-row': '<c-layout-row>\n    <div>Column 1</div>\n    <div>Column 2</div>\n</c-layout-row>',
        'layout-column': '<c-layout-column>\n    <div>Row 1</div>\n    <div>Row 2</div>\n</c-layout-column>',
        'layout-grid': '<c-layout-grid>\n    <div>Grid cell 1</div>\n    <div>Grid cell 2</div>\n</c-layout-grid>',
        'layout-flow': '<c-layout-flow>\n    <div>Flow item 1</div>\n    <div>Flow item 2</div>\n</c-layout-flow>',
        'icon': '<c-icon name="home" />',
        'menubar': '<c-menubar>\n    <c-menubar-item>Home</c-menubar-item>\n    <c-menubar-item>About</c-menubar-item>\n</c-menubar>',
        'tabs': '<c-tabs>\n    <c-tab title="Tab 1">Content 1</c-tab>\n    <c-tab title="Tab 2">Content 2</c-tab>\n</c-tabs>',
        'fieldset': '<c-fieldset legend="Personal Information">\n    <c-input label="Name" />\n    <c-input label="Email" type="email" />\n</c-fieldset>',
        'action-group': '<c-action-group>\n    <c-button variant="primary">Save</c-button>\n    <c-button variant="secondary">Cancel</c-button>\n</c-action-group>',
        'data-list': '<c-data-list>\n    <dt>Name</dt>\n    <dd>John Doe</dd>\n    <dt>Email</dt>\n    <dd>john@example.com</dd>\n</c-data-list>'
    }
    
    # Return specific example if available
    if component_name in examples:
        return examples[component_name]
    
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


def generate_documentation_html():
    """Generate HTML documentation for all components."""
    
    # Initialize component registry
    registry = ComponentRegistry()
    
    # Get all components
    components = []
    for name, definition in registry._components.items():
        component_data = {
            'name': name,
            'description': definition.description,
            'attributes': []
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
    
    # Sort components by name
    components.sort(key=lambda x: x['name'])
    
    # Generate HTML
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROOS Components Documentation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: #01689b;
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
        }
        header h1 {
            margin: 0;
        }
        .subtitle {
            opacity: 0.9;
            margin-top: 0.5rem;
        }
        nav {
            background: white;
            padding: 1rem;
            margin-bottom: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        nav h2 {
            margin-bottom: 1rem;
            color: #01689b;
        }
        nav ul {
            list-style: none;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 0.5rem;
        }
        nav a {
            color: #01689b;
            text-decoration: none;
            padding: 0.5rem;
            display: block;
            border-radius: 4px;
            transition: background 0.2s;
        }
        nav a:hover {
            background: #f0f8ff;
        }
        .component {
            background: white;
            padding: 2rem;
            margin-bottom: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .component h2 {
            color: #01689b;
            margin-bottom: 0.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e1e4e8;
        }
        .description {
            color: #666;
            margin-bottom: 1.5rem;
        }
        h3 {
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            color: #444;
        }
        .attributes-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1.5rem;
        }
        .attributes-table th {
            background: #f8f9fa;
            padding: 0.75rem;
            text-align: left;
            border: 1px solid #dee2e6;
            font-weight: 600;
        }
        .attributes-table td {
            padding: 0.75rem;
            border: 1px solid #dee2e6;
        }
        .attribute-name {
            font-family: 'Courier New', monospace;
            font-weight: 600;
            color: #d73502;
        }
        .attribute-type {
            font-family: 'Courier New', monospace;
            background: #f1f3f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }
        .attribute-required {
            background: #dc3545;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.8em;
        }
        .attribute-default {
            font-family: 'Courier New', monospace;
            color: #0969da;
        }
        .enum-values {
            font-family: 'Courier New', monospace;
            background: #fff3cd;
            padding: 4px 8px;
            border-radius: 3px;
            margin-top: 4px;
            display: inline-block;
            font-size: 0.9em;
        }
        pre {
            background: #f6f8fa;
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            border: 1px solid #d1d5da;
        }
        code {
            font-family: 'Courier New', monospace;
            background: #f6f8fa;
            padding: 2px 4px;
            border-radius: 3px;
        }
        .no-attributes {
            color: #666;
            font-style: italic;
        }
        footer {
            text-align: center;
            padding: 2rem;
            color: #666;
            border-top: 1px solid #e1e4e8;
            margin-top: 3rem;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>ROOS Components Documentation</h1>
            <p class="subtitle">Complete reference for all available components</p>
        </div>
    </header>
    
    <div class="container">
        <nav>
            <h2>Quick Navigation</h2>
            <div style="margin-bottom: 1.5rem; padding: 1rem; background: #fff3cd; border-radius: 6px; border: 1px solid #ffeaa7;">
                <h3 style="margin: 0 0 0.5rem 0; color: #856404;">Design System References</h3>
                <ul style="margin: 0; display: flex; flex-wrap: wrap; gap: 1rem;">
                    <li><a href="colors-reference.html" style="font-weight: bold; color: #007bc7;">🎨 Colors Reference</a></li>
                    <li><a href="icons-reference.html" style="font-weight: bold; color: #007bc7;">🔸 Icons Reference</a></li>
                    <li><a href="spacing-reference.html" style="font-weight: bold; color: #007bc7;">📏 Spacing & Sizing</a></li>
                </ul>
            </div>
            <h3>Components</h3>
            <ul>
                {% for component in components %}
                <li><a href="#{{ component.name }}">c-{{ component.name }}</a></li>
                {% endfor %}
            </ul>
        </nav>
        
        {% for component in components %}
        <div class="component" id="{{ component.name }}">
            <h2>&lt;c-{{ component.name }}&gt;</h2>
            <p class="description">{{ component.description or "No description available" }}</p>
            
            <h3>Attributes</h3>
            {% if component.attributes %}
            <table class="attributes-table">
                <thead>
                    <tr>
                        <th>Attribute</th>
                        <th>Type</th>
                        <th>Description</th>
                        <th>Default</th>
                        <th>Required</th>
                    </tr>
                </thead>
                <tbody>
                    {% for attr in component.attributes %}
                    <tr>
                        <td>
                            <span class="attribute-name">{{ attr.name }}</span>
                            {% if attr.enum_values %}
                            <br>
                            <span class="enum-values">{{ attr.enum_values|join(' | ') }}</span>
                            {% endif %}
                        </td>
                        <td><span class="attribute-type">{{ attr.type }}</span></td>
                        <td>{{ attr.description or "-" }}</td>
                        <td>
                            {% if attr.default is not none %}
                            <span class="attribute-default">{{ attr.default }}</span>
                            {% else %}
                            -
                            {% endif %}
                        </td>
                        <td>
                            {% if attr.required %}
                            <span class="attribute-required">required</span>
                            {% else %}
                            No
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p class="no-attributes">This component has no configurable attributes.</p>
            {% endif %}
            
            <h3>Example Usage</h3>
            <pre><code>{{ component.example | e }}</code></pre>
        </div>
        {% endfor %}
        
        <footer>
            <p>Generated on {{ generation_date }}</p>
            <p>ROOS Components v0.1.0</p>
        </footer>
    </div>
</body>
</html>'''
    
    # Setup Jinja2 for rendering the documentation template
    from jinja2 import Template
    template = Template(html_template)
    
    # Render the HTML with proper escaping
    html_output = template.render(
        components=components,
        generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    # Write to file
    output_path = Path(__file__).parent.parent / "examples" / "static" / "component-reference.html"
    output_path.write_text(html_output, encoding='utf-8')
    
    print(f"Component documentation generated: {output_path}")
    print(f"Documented {len(components)} components")
    
    # Also generate a simple index.html that lists all example files
    index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROOS Components Examples</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background: #f5f5f5;
        }
        h1 {
            color: #01689b;
        }
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li {
            margin: 0.5rem 0;
        }
        a {
            color: #01689b;
            text-decoration: none;
            font-weight: 500;
        }
        a:hover {
            text-decoration: underline;
        }
        .highlight {
            background: #fff3cd;
            padding: 0.25rem 0.5rem;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <h1>ROOS Components Examples</h1>
    
    <div class="card">
        <h2>Component Reference</h2>
        <p>Complete documentation for all available components:</p>
        <ul>
            <li><a href="component-reference.html" class="highlight">Component Reference Guide</a></li>
        </ul>
    </div>
    
    <div class="card">
        <h2>Live Examples</h2>
        <p>Run the FastAPI app to see components in action:</p>
        <pre><code>poetry install -E examples
poetry run uvicorn examples.fastapi_app:app --reload</code></pre>
        <p>Then visit <a href="http://localhost:8000">http://localhost:8000</a></p>
    </div>
    
    <div class="card">
        <h2>Template Examples</h2>
        <p>Browse the example templates in the <code>templates/</code> folder:</p>
        <ul>
            <li>simple-page.html.j2 - Basic page structure</li>
            <li>form-components.html.j2 - Form elements showcase</li>
            <li>layout-structure.html.j2 - Layout components</li>
            <li>complete-website-example.html.j2 - Full website example</li>
        </ul>
    </div>
</body>
</html>'''
    
    # Write index.html
    index_path = Path(__file__).parent.parent / "examples" / "static" / "index.html"
    index_path.write_text(index_html, encoding='utf-8')
    print(f"Index page generated: {index_path}")


if __name__ == "__main__":
    generate_documentation_html()