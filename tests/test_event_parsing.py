#!/usr/bin/env python3
"""
Test script to verify that @click attributes with Jinja syntax are parsed correctly.
"""

import os
from jinja2 import Environment, FileSystemLoader
from jinja_roos_components.extension import setup_components


def test_event_attribute_jinja_interpolation():
    """Test that Jinja variables in @click attributes are resolved."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    # Create environment with component extension
    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template = '''
{% set project = {"name": "test-project", "display_name": "Test Project Display"} %}
<c-button
    label="Verwijderen"
    kind="warning"
    size="sm"
    iconPlacement="before"
    icon="verwijderen"
    @click="'showDeleteConfirmation('{{ project.name }}', '{{ project.display_name or project.name }}')'" />
'''

    # Parse and render the template
    template = env.from_string(test_template)
    result = template.render()

    # Check if the variables were resolved
    assert "showDeleteConfirmation('test-project'" in result, \
        "Should resolve project.name in @click attribute"
    assert "Test Project Display')" in result, \
        "Should resolve project.display_name in @click attribute"
    assert "{{ project.name }}" not in result, \
        "Should not have unresolved Jinja variables"
    assert "{{ project.display_name" not in result, \
        "Should not have unresolved Jinja variables"


def test_event_attribute_expression():
    """Test event attribute with expression evaluation."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template_expr = '''
{% set project = {"name": "test-project", "display_name": "Test Project Display"} %}
<c-button
    label="Test"
    @click="'alert(' + project.name + ')'" />
'''

    template = env.from_string(test_template_expr)
    result = template.render()

    assert result is not None, "Should render template"
    assert len(result) > 0, "Should have output"