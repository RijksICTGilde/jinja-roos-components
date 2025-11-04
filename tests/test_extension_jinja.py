#!/usr/bin/env python3

"""
Test complex Jinja expressions using the actual extension.
"""

import os
from jinja2 import Environment, FileSystemLoader
from jinja_roos_components import setup_components
from jinja_roos_components.extension import ComponentExtension


def test_extension_jinja():
    """Test complex Jinja expressions with the actual extension."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    # Create environment with component extension
    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    setup_components(env)

    # Create test template string
    template_str = '''
{% set service_def = {"icon": "calendar", "color": "blue"} %}
<c-icon icon="{{ service_def.icon }}" size="xl" color="{{ service_def.color }}" />
    '''

    # Render from string
    template = env.from_string(template_str)
    result = template.render()

    # Assertions
    assert result is not None, "Template should render"
    assert len(result) > 0, "Rendered output should not be empty"
    assert 'calendar' in result, "Jinja expression for icon should be evaluated"
    assert 'blue' in result, "Jinja expression for color should be evaluated"


def test_preprocessing_directly():
    """Test the preprocessing step directly."""

    # Create a minimal environment
    env = Environment()
    extension = ComponentExtension(env)

    # Test source
    source = '''{% set service_def = {"icon": "calendar", "color": "blue"} %}
<c-icon icon="{{ service_def.icon }}" size="xl" color="{{ service_def.color }}" />'''

    # Preprocess
    result = extension.preprocess(source, "test", None)

    # Assertions
    assert result is not None, "Preprocessing should return a result"
    assert 'service_def.icon' in result or 'service_def["icon"]' in result, \
        "Preprocessing should extract Jinja expressions from attributes"
    assert 'service_def.color' in result or 'service_def["color"]' in result, \
        "Preprocessing should extract Jinja expressions from attributes"
    assert '"{{ service_def.icon }}"' not in result, \
        "Preprocessing should not treat Jinja expressions as quoted strings"