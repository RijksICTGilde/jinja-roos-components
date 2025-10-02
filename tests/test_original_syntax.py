#!/usr/bin/env python3
"""
Test the exact original syntax you provided to see if Jinja variables are resolved.
"""

import sys
import os
sys.path.insert(0, '/Users/robbertuittenbroek/IdeaProjects/jinja-roos-components/jinja-roos-components')

from jinja2 import Environment, DictLoader
from jinja_roos_components.extension_dom import setup_components_dom

def test_original_syntax():
    print("Testing the exact original syntax...")
    
    # Your exact original example
    template_content = '''
{% set project = {"name": "test-project", "display_name": "Test Project Display"} %}
<c-button 
    label="Verwijderen"
    kind="warning"
    size="sm"
    showIcon="before"
    icon="verwijderen"
    @click="showDeleteConfirmation('{{ project.name }}', '{{ project.display_name or project.name }}')" />
'''
    
    from jinja2 import FileSystemLoader
    import os
    
    # Set up proper file system loader to find component templates  
    template_dirs = [
        os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates'),
    ]
    env = Environment(loader=FileSystemLoader(template_dirs))
    env = setup_components_dom(env)
    
    try:
        template = env.from_string(template_content)
        result = template.render()
        
        print("Rendered result:")
        print("=" * 60)
        print(result)
        print("=" * 60)
        
        # Check if Jinja variables were resolved
        if "{{ project.name }}" in result:
            print("❌ Found unresolved Jinja variable: {{ project.name }}")
            return False
        
        if "{{ project.display_name" in result:
            print("❌ Found unresolved Jinja variable: {{ project.display_name }}")
            return False
            
        # Check if we got the expected resolved values
        if "test-project" in result and "Test Project Display" in result:
            print("✅ Jinja variables were properly resolved!")
            return True
        else:
            print("❌ Expected resolved values not found in output")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_original_syntax()
    if success:
        print("\n🎉 SUCCESS: The fix works! Jinja variables in event attributes are now resolved.")
    else:
        print("\n💥 FAILURE: Jinja variables in event attributes are still not being resolved.")
    sys.exit(0 if success else 1)