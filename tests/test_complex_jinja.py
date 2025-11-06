#!/usr/bin/env python3

"""
Test complex Jinja expressions in regular attributes.
"""

import re
from jinja_roos_components.html_parser import ComponentHTMLParser, convert_parsed_component
from jinja_roos_components.registry import ComponentRegistry, ComponentDefinition, AttributeDefinition, AttributeType


def test_complex_jinja_in_attributes():
    """Test that complex Jinja expressions in regular attributes are handled properly."""

    # Create a registry with icon component
    registry = ComponentRegistry()
    icon_component = ComponentDefinition(
        name='icon',
        description='Test icon component',
        attributes=[
            AttributeDefinition('icon', AttributeType.STRING),
            AttributeDefinition('size', AttributeType.STRING),
            AttributeDefinition('color', AttributeType.STRING),
        ]
    )
    registry.register_component(icon_component)

    # Create parser
    parser = ComponentHTMLParser(registry)

    # Test the problematic case
    test_html = '<c-icon icon="{{ service_def.icon }}" size="xl" color="{{ service_def.color }}" />'

    # Parse components
    components = parser.parse_components(test_html)

    assert components, "Should find components"
    assert len(components) > 0, "Should parse at least one component"

    # Convert the component
    result = convert_parsed_component(components[0])

    # Check if expressions were properly extracted
    assert 'service_def.icon' in result or 'service_def["icon"]' in result, \
        "Should extract service_def.icon expression"
    assert 'service_def.color' in result or 'service_def["color"]' in result, \
        "Should extract service_def.color expression"
    assert '"{{ service_def.icon }}"' not in result, \
        "Should not escape Jinja syntax"


def test_regex_pattern():
    """Test the regex pattern for Jinja expression extraction."""

    test_values = [
        '{{ service_def.icon }}',
        '{{ user.name }}',
        '{{ item.id or default_id }}',
        '{{ ServiceAdapter.get_service_definition(service.enum).icon }}',
    ]

    pattern = re.compile(r'{{\s*(.+?)\s*}}')

    for value in test_values:
        match = pattern.search(value)
        assert match is not None, f"Should match pattern: {value}"
        expr = match.group(1)
        assert len(expr) > 0, f"Should extract expression from: {value}"