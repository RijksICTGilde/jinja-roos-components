#!/usr/bin/env python3
"""
Test script to verify that @click attributes with Jinja syntax are parsed correctly.
"""

import sys
import os
sys.path.insert(0, '/Users/robbertuittenbroek/IdeaProjects/jinja-roos-components/jinja-roos-components')

from jinja2 import Environment, DictLoader
from jinja_roos_components.extension_dom import setup_components_dom

# Test template with your exact example - testing string interpolation in events
test_template = '''
{% set project = {"name": "test-project", "display_name": "Test Project Display"} %}
<c-button 
    label="Verwijderen"
    kind="warning"
    size="sm"
    showIcon="before"
    icon="verwijderen"
    @click="'showDeleteConfirmation(\\'{{ project.name }}\\', \\'{{ project.display_name or project.name }}\\')'" />
'''

# Also test with expression evaluation
test_template_expr = '''
{% set project = {"name": "test-project", "display_name": "Test Project Display"} %}
<c-button 
    label="Test"
    @click="'alert(' + project.name + ')'" />
'''

# Expected output should have the variables resolved in the onclick attribute
expected_patterns = [
    "showDeleteConfirmation('test-project'",
    "Test Project Display')"
]

def test_event_parsing():
    print("Testing event attribute parsing...")
    
    # Create Jinja environment
    env = Environment(loader=DictLoader({}))
    
    # Setup components
    env = setup_components_dom(env)
    
    try:
        # Parse and render the template
        template = env.from_string(test_template)
        result = template.render()
        
        print("Rendered template:")
        print("=" * 50)
        print(result)
        print("=" * 50)
        
        # Check if the variables were resolved
        success = True
        for pattern in expected_patterns:
            if pattern not in result:
                print(f"❌ Expected pattern not found: {pattern}")
                success = False
            else:
                print(f"✅ Found expected pattern: {pattern}")
        
        if "{{ project.name }}" in result or "{{ project.display_name" in result:
            print("❌ Found unresolved Jinja variables in result")
            success = False
        else:
            print("✅ No unresolved Jinja variables found")
            
        return success
        
    except Exception as e:
        print(f"❌ Error during template rendering: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_event_parsing()
    if success:
        print("\n🎉 Test passed! Event attributes are working correctly.")
    else:
        print("\n💥 Test failed! Event attributes are not working correctly.")
    sys.exit(0 if success else 1)