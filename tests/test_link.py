#!/usr/bin/env python3
"""
Test script to verify link component icon functionality.
"""

import os
from jinja2 import Environment, FileSystemLoader
from jinja_roos_components.extension import setup_components


def test_link_icon_before():
    """Test link with icon placement before text."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template = '''
<c-link
    href="/page"
    content="Read more"
    icon="arrow-right"
    iconPlacement="before" />
'''

    template = env.from_string(test_template)
    result = template.render()

    # Check CSS class is present
    assert "rvo-link--with-icon" in result, \
        "Should have with-icon CSS class"

    # Check icon span is rendered with before class
    assert 'rvo-link__icon--before' in result, \
        "Should render icon span with before class"

    # Check icon class includes correct icon name
    assert 'rvo-icon-arrow-right' in result, \
        "Should render icon with correct name"

    # Verify icon appears before content
    icon_pos = result.find('rvo-icon-arrow-right')
    content_pos = result.find('Read more')
    assert icon_pos < content_pos, \
        "Icon should appear before content text"

    # Verify data attributes
    assert 'data-roos-icon="arrow-right"' in result, \
        "Should have data-roos-icon attribute"
    assert 'data-roos-icon-placement="before"' in result, \
        "Should have data-roos-icon-placement attribute"


def test_link_icon_after():
    """Test link with icon placement after text."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template = '''
<c-link
    href="/next"
    content="Continue"
    icon="chevron-right"
    iconPlacement="after" />
'''

    template = env.from_string(test_template)
    result = template.render()

    # Check CSS class is present
    assert "rvo-link--with-icon" in result, \
        "Should have with-icon CSS class"

    # Check icon span is rendered with after class
    assert 'rvo-link__icon--after' in result, \
        "Should render icon span with after class"

    # Check icon class includes correct icon name
    assert 'rvo-icon-chevron-right' in result, \
        "Should render icon with correct name"

    # Verify icon appears after content
    icon_pos = result.find('rvo-icon-chevron-right')
    content_pos = result.find('Continue')
    assert icon_pos > content_pos, \
        "Icon should appear after content text"

    # Verify data attributes
    assert 'data-roos-icon="chevron-right"' in result, \
        "Should have data-roos-icon attribute"
    assert 'data-roos-icon-placement="after"' in result, \
        "Should have data-roos-icon-placement attribute"


def test_link_no_icon():
    """Test link without icon attribute."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template = '''
<c-link
    href="/about"
    content="About Us" />
'''

    template = env.from_string(test_template)
    result = template.render()

    # Verify no icon CSS class
    assert "rvo-link--with-icon" not in result, \
        "Should not have with-icon CSS class without icon"

    # Verify no icon span is rendered
    assert "rvo-link__icon--before" not in result, \
        "Should not render icon span with before class without icon"
    assert "rvo-link__icon--after" not in result, \
        "Should not render icon span with after class without icon"
    assert "utrecht-icon rvo-icon" not in result, \
        "Should not render icon span without icon attribute"

    # Verify no data attributes for icon
    assert 'data-roos-icon=' not in result, \
        "Should not have data-roos-icon attribute without icon"

    # Verify link still renders with content
    assert "About Us" in result, \
        "Should still render link with content"
    assert '<a href="/about"' in result, \
        "Should render anchor element with href"


def test_link_icon_without_placement():
    """Test link with icon but no iconPlacement (should default to 'before')."""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template = '''
<c-link
    href="/download"
    content="Download"
    icon="download" />
'''

    template = env.from_string(test_template)
    result = template.render()

    # Check defaults to "before" placement
    assert "rvo-link--with-icon" in result, \
        "Should have with-icon CSS class"
    assert 'rvo-link__icon--before' in result, \
        "Should default to icon-before class when iconPlacement not specified"

    # Check icon span is rendered
    assert 'rvo-icon-download' in result, \
        "Should render icon with correct name"

    # Verify icon appears before content
    icon_pos = result.find('rvo-icon-download')
    content_pos = result.find('Download')
    assert icon_pos < content_pos, \
        "Icon should default to appearing before content text"

    # Verify data attributes default to "before"
    assert 'data-roos-icon="download"' in result, \
        "Should have data-roos-icon attribute"
    assert 'data-roos-icon-placement="before"' in result, \
        "Should default to before placement in data attribute"
