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
    
def test_shorthand_boolean_attribute():
    """Test that shorthand boolean notation is properly parsed in the middle of attributes"""

    registry = ComponentRegistry()
    button_component = ComponentDefinition(
        name='button',
        description='Test button component',
        attributes=[
            AttributeDefinition('variant', AttributeType.STRING),
            AttributeDefinition('disabled', AttributeType.BOOLEAN),
        ]
    )
    registry.register_component(button_component)

    parser = ComponentHTMLParser(registry)
    components = parser.parse_components("""
<c-button disabled title="my button"/>
                                         """)

    assert len(components) == 1
    assert len(components[0]['attrs']) == 2
    assert components[0]['attrs']['disabled'] == None
    assert components[0]['attrs']['title'] == 'my button'

def test_shorthand_attribute_at_end():
    """Test that shorthand notation at the end of the tag is properly parsed"""

    registry = ComponentRegistry()
    button_component = ComponentDefinition(
        name='button',
        description='Test button component',
        attributes=[
            AttributeDefinition('title', AttributeType.STRING),
            AttributeDefinition('disabled', AttributeType.BOOLEAN),
        ]
    )
    registry.register_component(button_component)

    parser = ComponentHTMLParser(registry)

    # Test with self-closing tag
    components = parser.parse_components('<c-button title="my button" disabled />')

    assert len(components) == 1
    assert len(components[0]['attrs']) == 2
    assert components[0]['attrs']['title'] == 'my button'
    assert components[0]['attrs']['disabled'] == None

    # Test with regular closing tag
    components = parser.parse_components('<c-button title="my button" disabled>content</c-button>')

    assert len(components) == 1
    assert len(components[0]['attrs']) == 2
    assert components[0]['attrs']['title'] == 'my button'
    assert components[0]['attrs']['disabled'] == None

def test_attribute_case_preservation():
    """Test that attribute name capitalization is preserved"""

    registry = ComponentRegistry()
    button_component = ComponentDefinition(
        name='button',
        description='Test button component',
        attributes=[
            AttributeDefinition('dataId', AttributeType.STRING),
        ]
    )
    registry.register_component(button_component)

    parser = ComponentHTMLParser(registry)
    components = parser.parse_components('<c-button dataId="test123" />')

    assert len(components) == 1
    attrs = components[0]['attrs']
    assert 'dataId' in attrs
    assert attrs['dataId'] == 'test123'

def test_binding_attribute_case_preservation():
    """Test that binding attributes (starting with :) preserve capitalization"""

    registry = ComponentRegistry()
    button_component = ComponentDefinition(
        name='button',
        description='Test button component',
        attributes=[
            AttributeDefinition('isActive', AttributeType.BOOLEAN),
        ]
    )
    registry.register_component(button_component)

    parser = ComponentHTMLParser(registry)
    components = parser.parse_components('<c-button :isActive="active_state" />')

    assert len(components) == 1
    attrs = components[0]['attrs']
    assert ':isActive' in attrs
    assert attrs[':isActive'] == 'active_state'

def test_event_attribute_case_preservation():
    """Test that event attributes (starting with @) preserve capitalization"""

    registry = ComponentRegistry()
    button_component = ComponentDefinition(
        name='button',
        description='Test button component',
        attributes=[
            AttributeDefinition('onClick', AttributeType.STRING),
        ]
    )
    registry.register_component(button_component)

    parser = ComponentHTMLParser(registry)
    components = parser.parse_components('<c-button @onClick="handleClick()" />')

    assert len(components) == 1
    attrs = components[0]['attrs']
    assert '@onClick' in attrs
    assert attrs['@onClick'] == 'handleClick()'
    