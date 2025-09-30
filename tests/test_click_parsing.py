#!/usr/bin/env python3
"""
Isolated test to debug Jinja variable parsing in @click attributes for ROOS components.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jinja-roos-components'))

from jinja2 import Environment, FileSystemLoader
from jinja_roos_components.extension import ComponentExtension

def test_click_parsing():
    """Test @click attribute parsing with Jinja variables"""
    
    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')
    
    env = Environment(
        loader=FileSystemLoader([template_dir, '.']),
        extensions=[ComponentExtension]
    )
    
    # Test template with @click containing Jinja variables
    test_template_source = """
{# Test template for @click parsing #}
{% set project = {'name': 'test-project', 'display_name': 'Test Project'} %}

{# Debug: Show what the component context contains #}
<c-button 
    label="Verwijderen"
    kind="warning"
    size="sm"
    showIcon="before"
    icon="verwijderen"
    @click="showDeleteConfirmation('{{ project.name }}', '{{ project.display_name or project.name }}')" />

{# Also test the temp variable mechanism directly #}
{% set _event_attr_test %}showDeleteConfirmation('{{ project.name }}', '{{ project.display_name or project.name }}'){% endset %}
<p>Direct temp var test: {{ _event_attr_test }}</p>
"""

    print("=== TESTING JINJA VARIABLES IN @CLICK ATTRIBUTES ===")
    print(f"Input template:\n{test_template_source}")
    print("\n" + "="*60)
    
    try:
        # Parse and render the template
        template = env.from_string(test_template_source)
        result = template.render()
        
        print(f"Rendered output:\n{result}")
        print("\n" + "="*60)
        
        # Check if Jinja variables were resolved
        if "{{ project.name }}" in result:
            print("❌ FAILED: Jinja variables NOT resolved in @click attribute")
            print("Expected: @click=\"showDeleteConfirmation('test-project', 'Test Project')\"")
            print("Actual: Contains literal {{ project.name }}")
            return False
        elif "'test-project'" in result and "'Test Project'" in result:
            print("✅ SUCCESS: Jinja variables correctly resolved in @click attribute")
            return True
        else:
            print("❓ UNCLEAR: Unexpected output format")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_case():
    """Test simpler case first"""
    
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')
    
    env = Environment(
        loader=FileSystemLoader([template_dir, '.']),
        extensions=[ComponentExtension]
    )
    
    # Simple test
    simple_template = """
{% set name = 'test-value' %}
<c-button label="Test" @click="doSomething('{{ name }}')" />
"""

    print("\n=== TESTING SIMPLE CASE ===")
    print(f"Input: {simple_template}")
    
    try:
        template = env.from_string(simple_template)
        result = template.render()
        
        print(f"Output: {result}")
        
        if "'test-value'" in result:
            print("✅ Simple case works")
        else:
            print("❌ Simple case fails")
            
    except Exception as e:
        print(f"❌ Simple case error: {e}")

if __name__ == "__main__":
    print("Testing Jinja variable resolution in ROOS @click attributes...")
    
    # Test simple case first
    test_simple_case()
    
    # Test the actual problematic case
    success = test_click_parsing()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Tests failed - need to fix the extension")
        sys.exit(1)