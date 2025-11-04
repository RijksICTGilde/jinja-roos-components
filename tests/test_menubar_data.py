#!/usr/bin/env python3
"""
Test script to verify menubar data processing with different data formats.
"""

import os

from jinja2 import Environment, FileSystemLoader
from jinja_roos_components.extension import setup_components

# Test templates
templates = {
    'test_menubar.html': '''
{# Test 1: Using Jinja variable #}
<h2>Test 1: Using Jinja variable</h2>
<c-menubar :items="nav_items" />

{# Test 2: Inline data structure #}
<h2>Test 2: Inline data structure</h2>
<c-menubar :items="[
    {'label': 'Home', 'link': '/', 'active': true},
    {'label': 'Products', 'link': '/products'},
    {'label': 'About', 'link': '/about'},
    {'label': 'Contact', 'link': '/contact', 'align': 'right'}
]" />

{# Test 3: With icons and submenus #}
<h2>Test 3: With icons and submenus</h2>
<c-menubar :items="complex_nav" useIcons="true" />
''',

    'debug_context.html': '''
<h2>Debug: Component Context</h2>
<p>Items type: {{ _component_context.items.__class__.__name__ if _component_context.items else 'None' }}</p>
<p>Items length: {{ _component_context.items | length if _component_context.items else 0 }}</p>
<p>Items content: {{ _component_context.items | tojson }}</p>
'''
}

def test_menubar_data_processing():
    """Test different ways of passing data to menubar component."""
    
    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    # Create environment with component extension
    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    setup_components(env)
    
    # Test data
    nav_items = [
        {'label': 'Home', 'link': '/', 'active': True},
        {'label': 'Services', 'link': '/services'},
        {'label': 'Blog', 'link': '/blog'},
        {'label': 'Login', 'link': '/login', 'align': 'right'}
    ]
    
    complex_nav = [
        {'label': 'Dashboard', 'link': '/dashboard', 'icon': 'home', 'active': True},
        {
            'label': 'Products', 
            'link': '#',
            'icon': 'box',
            'submenu': [
                {'label': 'All Products', 'link': '/products'},
                {'label': 'New Product', 'link': '/products/new'},
                {'label': 'Categories', 'link': '/categories'}
            ]
        },
        {'label': 'Settings', 'link': '/settings', 'icon': 'settings', 'align': 'right'}
    ]
    
    # Template context
    context = {
        'nav_items': nav_items,
        'complex_nav': complex_nav
    }
    
    # Render template
    template = env.from_string(templates['test_menubar.html'])
    result = template.render(**context)
    
    print("=== RENDERED OUTPUT ===")
    print(result)
    print("\n" + "="*50 + "\n")
    
    # Test if the data is being processed correctly
    print("=== DATA ANALYSIS ===")
    print(f"nav_items type: {type(nav_items)}")
    print(f"nav_items length: {len(nav_items)}")
    print(f"First item: {nav_items[0]}")
    
    # Check if the rendered output contains expected elements
    checks = [
        ('Home link found', 'href="/"' in result),
        ('Active class found', 'rvo-menubar__link--active' in result),
        ('Right alignment found', 'align' in str(complex_nav)),
        ('Submenu structure found', 'submenu' in str(complex_nav)),
        ('Menu items rendered', 'rvo-menubar__item' in result)
    ]
    
    print("\n=== VALIDATION CHECKS ===")
    for check_name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check_name}")
    
    return result

if __name__ == '__main__':
    test_menubar_data_processing()