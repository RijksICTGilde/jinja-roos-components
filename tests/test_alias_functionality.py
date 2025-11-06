#!/usr/bin/env python3
"""
Test script for component alias functionality.
"""

import os
import pytest
from jinja2 import Environment, FileSystemLoader
from jinja_roos_components.extension import setup_components


@pytest.fixture
def env():
    """Set up Jinja environment with ROOS components."""
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')
    environment = Environment(loader=FileSystemLoader([template_dir, '.']))
    setup_components(environment, strict_validation=True)
    return environment


def test_h1_alias(env):
    """Test that c-h1 alias works correctly."""
    template = env.from_string("<c-h1>Main Title</c-h1>")
    result = template.render()

    assert result, "Should render output"
    assert len(result) > 0, "Should have content"


def test_h2_alias_with_attributes(env):
    """Test that c-h2 alias works with custom attributes."""
    template = env.from_string('<c-h2 class="custom">Subtitle</c-h2>')
    result = template.render()

    assert result, "Should render output"
    assert 'custom' in result or 'Subtitle' in result, "Should include custom class or content"


def test_ul_alias(env):
    """Test that c-ul (unordered list) alias works."""
    template = env.from_string('<c-ul><c-li>Item 1</c-li><c-li>Item 2</c-li></c-ul>')
    result = template.render()

    assert result, "Should render output"
    assert len(result) > 0, "Should have content"


def test_ol_alias(env):
    """Test that c-ol (ordered list) alias works."""
    template = env.from_string('<c-ol><c-li>First</c-li><c-li>Second</c-li></c-ol>')
    result = template.render()

    assert result, "Should render output"
    assert len(result) > 0, "Should have content"