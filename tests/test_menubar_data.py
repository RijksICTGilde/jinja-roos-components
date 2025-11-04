#!/usr/bin/env python3
"""
Test script to verify menubar data processing with different data formats.
"""

import os
from jinja2 import Environment, FileSystemLoader
from jinja_roos_components.extension import setup_components


def test_menubar_with_variable_data():
    """Test menubar with data passed as Jinja variable."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    setup_components(env)

    # Test data
    nav_items = [
        {'label': 'Home', 'link': '/', 'active': True},
        {'label': 'Services', 'link': '/services'},
        {'label': 'Blog', 'link': '/blog'},
        {'label': 'Login', 'link': '/login', 'align': 'right'}
    ]

    template_str = '<c-menubar :items="nav_items" />'
    template = env.from_string(template_str)
    result = template.render(nav_items=nav_items)

    assert result, "Should render output"
    assert 'href="/"' in result, "Should contain home link"


def test_menubar_with_inline_data():
    """Test menubar with inline data structure."""

    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    setup_components(env)

    template_str = '''<c-menubar :items="[
        {'label': 'Home', 'link': '/', 'active': true},
        {'label': 'Products', 'link': '/products'},
        {'label': 'About', 'link': '/about'}
    ]" />'''

    template = env.from_string(template_str)
    result = template.render()

    assert result, "Should render output"
    assert len(result) > 0, "Should have content"


def test_menubar_with_complex_nav():
    """Test menubar with icons and submenus."""

    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    setup_components(env)

    complex_nav = [
        {'label': 'Dashboard', 'link': '/dashboard', 'icon': 'home', 'active': True},
        {
            'label': 'Products',
            'link': '#',
            'icon': 'box',
            'submenu': [
                {'label': 'All Products', 'link': '/products'},
                {'label': 'New Product', 'link': '/products/new'}
            ]
        }
    ]

    template_str = '<c-menubar :items="complex_nav" useIcons="true" />'
    template = env.from_string(template_str)
    result = template.render(complex_nav=complex_nav)

    assert result, "Should render output"
    assert len(result) > 0, "Should have content"