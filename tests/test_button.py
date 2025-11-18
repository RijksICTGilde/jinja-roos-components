#!/usr/bin/env python3
"""
Test script to verify button component icon functionality.
"""

import os
from jinja2 import Environment, FileSystemLoader
from jinja_roos_components.extension import setup_components


def test_button_icon_before():
    """Test button with icon placement before text."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template = '''
<c-button
    label="Save"
    icon="save"
    iconPlacement="before" />
'''

    template = env.from_string(test_template)
    result = template.render()

    # Check CSS class is present
    assert "utrecht-button--icon-before" in result, \
        "Should have icon-before CSS class"

    # Check icon span is rendered
    assert 'class="utrecht-icon rvo-icon rvo-icon-save' in result, \
        "Should render icon span with correct icon name"

    # Verify icon appears before label
    icon_pos = result.find('rvo-icon-save')
    label_pos = result.find('Save')
    assert icon_pos < label_pos, \
        "Icon should appear before label text"


def test_button_icon_after():
    """Test button with icon placement after text."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template = '''
<c-button
    label="Next"
    icon="arrow-right"
    iconPlacement="after" />
'''

    template = env.from_string(test_template)
    result = template.render()

    # Check CSS class is present
    assert "utrecht-button--icon-after" in result, \
        "Should have icon-after CSS class"

    # Check icon span is rendered
    assert 'class="utrecht-icon rvo-icon rvo-icon-arrow-right' in result, \
        "Should render icon span with correct icon name"

    # Verify icon appears after label
    icon_pos = result.find('rvo-icon-arrow-right')
    label_pos = result.find('Next')
    assert icon_pos > label_pos, \
        "Icon should appear after label text"


def test_button_no_icon():
    """Test button without icon attribute."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template = '''
<c-button label="Click Me" />
'''

    template = env.from_string(test_template)
    result = template.render()

    # Verify no icon CSS classes
    assert "utrecht-button--icon-before" not in result, \
        "Should not have icon-before CSS class without icon"
    assert "utrecht-button--icon-after" not in result, \
        "Should not have icon-after CSS class without icon"

    # Verify no icon span is rendered
    assert "utrecht-icon rvo-icon" not in result, \
        "Should not render icon span without icon attribute"

    # Verify button still renders with label
    assert "Click Me" in result, \
        "Should still render button with label"
    assert '<button' in result, \
        "Should render button element"


def test_button_icon_without_placement():
    """Test button with icon but no iconPlacement (should default to 'before')."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template = '''
<c-button
    label="Download"
    icon="download" />
'''

    template = env.from_string(test_template)
    result = template.render()

    # Check defaults to "before" placement
    assert "utrecht-button--icon-before" in result, \
        "Should default to icon-before CSS class when iconPlacement not specified"

    # Check icon span is rendered
    assert 'class="utrecht-icon rvo-icon rvo-icon-download' in result, \
        "Should render icon span with correct icon name"

    # Verify icon appears before label
    icon_pos = result.find('rvo-icon-download')
    label_pos = result.find('Download')
    assert icon_pos < label_pos, \
        "Icon should default to appearing before label text"
