#!/usr/bin/env python3

"""
Test complex Jinja expressions in regular attributes.
"""

from jinja_roos_components.html_parser import ComponentHTMLParser, convert_parsed_component
from jinja_roos_components.components.registry import ComponentRegistry, ComponentDefinition, AttributeDefinition, AttributeType

def test_complex_jinja_attributes():
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
    
    print(f"Testing: {test_html}")
    
    try:
        # Parse components
        components = parser.parse_components(test_html)
        
        if not components:
            print("ERROR: No components found")
            return
            
        print(f"Found component: {components[0]}")
        print(f"Attributes: {components[0]['attrs']}")
        
        # Convert the component
        result = convert_parsed_component(components[0])
        print(f"Output: {result}")
        
        # Check if expressions were properly extracted
        if 'service_def.icon' in result and 'service_def.color' in result:
            print("✓ Complex expressions properly extracted")
        else:
            print("✗ Complex expressions NOT extracted properly")
            if '"{{ service_def.icon }}"' in result:
                print("  - Found escaped Jinja syntax (should be unescaped)")
                
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

def test_regex_directly():
    """Test the regex pattern directly."""
    import re
    
    test_values = [
        '{{ service_def.icon }}',
        '{{ user.name }}', 
        '{{ item.id or default_id }}',
        '{{ ServiceAdapter.get_service_definition(service.enum).icon }}',
    ]
    
    pattern = re.compile(r'{{\s*(.+?)\s*}}')
    
    print("\nTesting regex pattern directly:")
    for value in test_values:
        match = pattern.search(value)
        if match:
            expr = match.group(1)
            print(f"  '{value}' -> '{expr}' ✓")
        else:
            print(f"  '{value}' -> NO MATCH ✗")

if __name__ == "__main__":
    test_complex_jinja_attributes()
    test_regex_directly()