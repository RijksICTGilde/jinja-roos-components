#!/usr/bin/env python3
"""
Test script to verify tag component icon functionality.
"""

import os
from jinja2 import Environment, FileSystemLoader
from jinja_roos_components.extension import setup_components


def test_tag_icon_before():
    """Test tag with icon placement before text."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template = '''
<c-tag
    content="New Feature"
    icon="delta"
    iconPlacement="before" />
'''

    template = env.from_string(test_template)
    result = template.render()

    # Check CSS class is present
    assert "rvo-tag--with-icon" in result, \
        "Should have with-icon CSS class"

    # Check icon span is rendered with before class
    assert 'rvo-link__icon--before' in result, \
        "Should render icon span with before class"

    # Check icon class includes correct icon name
    assert 'rvo-icon--delta' in result, \
        "Should render icon with correct name"

    # Verify icon appears before content
    icon_pos = result.find('rvo-icon--delta')
    content_pos = result.find('New Feature')
    assert icon_pos < content_pos, \
        "Icon should appear before content text"


def test_tag_icon_after():
    """Test tag with icon placement after text."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template = '''
<c-tag
    content="Important"
    icon="waarschuwing"
    iconPlacement="after" />
'''

    template = env.from_string(test_template)
    result = template.render()

    # Check CSS class is present
    assert "rvo-tag--with-icon" in result, \
        "Should have with-icon CSS class"

    # Check icon span is rendered with after class
    assert 'rvo-link__icon--after' in result, \
        "Should render icon span with after class"

    # Check icon class includes correct icon name
    assert 'rvo-icon--waarschuwing' in result, \
        "Should render icon with correct name"

    # Verify icon appears after content
    icon_pos = result.find('rvo-icon--waarschuwing')
    content_pos = result.find('Important')
    assert icon_pos > content_pos, \
        "Icon should appear after content text"


def test_tag_no_icon():
    """Test tag without icon attribute."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template = '''
<c-tag content="Simple Tag" />
'''

    template = env.from_string(test_template)
    result = template.render()

    # Note: Tag without icon AND without type should not have with-icon class
    assert "rvo-tag--with-icon" not in result, \
        "Should not have with-icon CSS class without icon or type"

    # Verify no custom icon span is rendered
    assert "rvo-icon rvo-icon--" not in result, \
        "Should not render custom icon span without icon attribute"

    # Verify tag still renders with content
    assert "Simple Tag" in result, \
        "Should still render tag with content"
    assert 'data-roos-component="tag"' in result, \
        "Should render tag element"


def test_tag_icon_without_placement():
    """Test tag with icon but no iconPlacement (should default to 'before')."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template = '''
<c-tag
    content="Recommended"
    icon="bevestiging" />
'''

    template = env.from_string(test_template)
    result = template.render()

    # Check defaults to "before" placement
    assert "rvo-tag--with-icon" in result, \
        "Should have with-icon CSS class"
    assert 'rvo-link__icon--before' in result, \
        "Should default to icon-before class when iconPlacement not specified"

    # Check icon span is rendered
    assert 'rvo-icon--bevestiging' in result, \
        "Should render icon with correct name"

    # Verify icon appears before content
    icon_pos = result.find('rvo-icon--bevestiging')
    content_pos = result.find('Recommended')
    assert icon_pos < content_pos, \
        "Icon should default to appearing before content text"


def test_tag_type_with_status_icon():
    """Test tag with type attribute (should render status icon)."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template = '''
<c-tag
    content="Error occurred"
    type="error" />
'''

    template = env.from_string(test_template)
    result = template.render()

    # Check CSS classes
    assert "rvo-tag--with-icon" in result, \
        "Should have with-icon CSS class for type"
    assert "rvo-tag--error" in result, \
        "Should have type-specific CSS class"

    # Check status icon is rendered
    assert 'rvo-status-icon' in result, \
        "Should render status icon for type"
    assert 'rvo-status-icon--foutmelding' in result, \
        "Should render correct status icon for error type"

    # Verify data attribute
    assert 'data-roos-type="error"' in result, \
        "Should have data-roos-type attribute"


def test_tag_icon_priority_over_type():
    """Test that custom icon takes priority over type status icon when both are provided."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template = '''
<c-tag
    content="Custom Icon Priority"
    type="error"
    icon="delta" />
'''

    template = env.from_string(test_template)
    result = template.render()

    # Check CSS classes
    assert "rvo-tag--with-icon" in result, \
        "Should have with-icon CSS class"
    assert "rvo-tag--error" in result, \
        "Should still have type-specific CSS class"

    # Verify custom icon is rendered (not status icon)
    assert 'rvo-icon--delta' in result, \
        "Should render custom icon (icon attribute takes priority)"

    # Verify status icon is NOT rendered
    assert 'rvo-status-icon--foutmelding' not in result, \
        "Should not render status icon when custom icon is provided"
    assert 'rvo-status-icon' not in result or 'rvo-icon' in result, \
        "Custom icon should take priority over type status icon"

    # Both attributes should be in data attributes
    assert 'data-roos-type="error"' in result, \
        "Should have data-roos-type attribute"
