#!/usr/bin/env python3

"""
Test Jinja syntax handling in regular attributes after the fix.
"""

from jinja_roos_components.html_parser import ComponentHTMLParser, convert_parsed_component
from jinja_roos_components.registry import ComponentRegistry, ComponentDefinition, AttributeDefinition, AttributeType

def test_jinja_in_regular_attributes():
    """Test that regular attributes with Jinja syntax are handled properly."""
    
    # Create a registry with a test component
    registry = ComponentRegistry()
    button_component = ComponentDefinition(
        name='button',
        description='Test button component',
        attributes=[
            AttributeDefinition('variant', AttributeType.STRING, default='primary'),
            AttributeDefinition('data-value', AttributeType.STRING),
            AttributeDefinition('title', AttributeType.STRING),
        ]
    )
    registry.register_component(button_component)
    
    # Create parser
    parser = ComponentHTMLParser(registry)
    
    # Test cases with different Jinja syntax patterns in regular attributes
    test_cases = [
        {
            'name': 'Simple variable interpolation',
            'html': '<c-button variant="primary" title="{{ user.name }}" />',
            'should_contain': '"title": user.name'
        },
        {
            'name': 'Complex expression',
            'html': '<c-button data-value="{{ item.id or default_id }}" />',
            'should_contain': '"data-value": item.id or default_id'
        },
        {
            'name': 'String concatenation',
            'html': '<c-button title="{{ prefix + suffix }}" />',
            'should_contain': '"title": prefix + suffix'
        },
        {
            'name': 'Regular string attribute (no Jinja)',
            'html': '<c-button variant="secondary" />',
            'should_contain': '"variant": "secondary"'
        },
        {
            'name': 'Mixed attributes',
            'html': '<c-button variant="{{ button_type }}" title="Click me" />',
            'should_contain': ['"variant": button_type', '"title": "Click me"']
        }
    ]
    
    print("Testing Jinja syntax handling in regular attributes...")
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        print(f"Input: {test_case['html']}")
        
        try:
            # Parse components
            components = parser.parse_components(test_case['html'])
            
            if not components:
                print("ERROR: No components found")
                continue
                
            # Convert the component
            result = convert_parsed_component(components[0])
            print(f"Output: {result}")
            
            # Check expectations
            should_contain = test_case['should_contain']
            if isinstance(should_contain, str):
                should_contain = [should_contain]
                
            for expected in should_contain:
                if expected in result:
                    print(f"✓ Contains expected: {expected}")
                else:
                    print(f"✗ Missing expected: {expected}")
                    
        except Exception as e:
            print(f"ERROR: {e}")
    
    print("\n=== Testing complete ===")

if __name__ == "__main__":
    test_jinja_in_regular_attributes()