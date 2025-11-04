#!/usr/bin/env python3

"""
Test Jinja syntax handling in regular attributes after the fix.
"""

from jinja_roos_components.html_parser import ComponentHTMLParser, convert_parsed_component
from jinja_roos_components.registry import ComponentRegistry, ComponentDefinition, AttributeDefinition, AttributeType


def test_simple_variable_interpolation():
    """Test simple Jinja variable interpolation in attributes."""

    registry = ComponentRegistry()
    button_component = ComponentDefinition(
        name='button',
        description='Test button component',
        attributes=[
            AttributeDefinition('variant', AttributeType.STRING, default='primary'),
            AttributeDefinition('title', AttributeType.STRING),
        ]
    )
    registry.register_component(button_component)

    parser = ComponentHTMLParser(registry)
    components = parser.parse_components('<c-button variant="primary" title="{{ user.name }}" />')

    assert components, "Should parse components"
    result = convert_parsed_component(components[0])
    assert 'user.name' in result or 'user["name"]' in result, "Should extract Jinja expression"


def test_complex_expression():
    """Test complex Jinja expression in attributes."""

    registry = ComponentRegistry()
    button_component = ComponentDefinition(
        name='button',
        description='Test button component',
        attributes=[AttributeDefinition('data-value', AttributeType.STRING)]
    )
    registry.register_component(button_component)

    parser = ComponentHTMLParser(registry)
    components = parser.parse_components('<c-button data-value="{{ item.id or default_id }}" />')

    assert components, "Should parse components"
    result = convert_parsed_component(components[0])
    assert 'item.id or default_id' in result or 'item["id"] or default_id' in result, \
        "Should extract complex Jinja expression"


def test_regular_string_attribute():
    """Test regular string attribute without Jinja."""

    registry = ComponentRegistry()
    button_component = ComponentDefinition(
        name='button',
        description='Test button component',
        attributes=[AttributeDefinition('variant', AttributeType.STRING, default='primary')]
    )
    registry.register_component(button_component)

    parser = ComponentHTMLParser(registry)
    components = parser.parse_components('<c-button variant="secondary" />')

    assert components, "Should parse components"
    result = convert_parsed_component(components[0])
    assert '"secondary"' in result or "'secondary'" in result, "Should preserve string value"


def test_mixed_attributes():
    """Test mixed Jinja and regular attributes."""

    registry = ComponentRegistry()
    button_component = ComponentDefinition(
        name='button',
        description='Test button component',
        attributes=[
            AttributeDefinition('variant', AttributeType.STRING),
            AttributeDefinition('title', AttributeType.STRING),
        ]
    )
    registry.register_component(button_component)

    parser = ComponentHTMLParser(registry)
    components = parser.parse_components('<c-button variant="{{ button_type }}" title="Click me" />')

    assert components, "Should parse components"
    result = convert_parsed_component(components[0])
    assert 'button_type' in result or 'button["type"]' in result, \
        "Should extract Jinja expression from variant"
    assert '"Click me"' in result or "'Click me'" in result, \
        "Should preserve string value for title"