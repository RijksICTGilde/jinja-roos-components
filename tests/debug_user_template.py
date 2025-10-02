#!/usr/bin/env python3
"""
Debug exactly what happens with the user's template.
"""

import sys
import os
sys.path.insert(0, '/Users/robbertuittenbroek/IdeaProjects/jinja-roos-components/jinja-roos-components')

from jinja2 import Environment, FileSystemLoader
from jinja_roos_components.extension_dom import ComponentExtensionDOM

def debug_user_template():
    print("Debugging the exact user template...")
    
    # The exact user template
    user_template = '''<c-button 
    label="Verwijderen"
    kind="warning"
    size="sm"
    showIcon="before"
    icon="verwijderen"
    @click="showDeleteConfirmation('{{ project.name }}', '{{ project.display_name or project.name }}')" />'''
    
    # Add context around it like the user would have
    full_template = '''{% set project = {"name": "test-project", "display_name": "Test Project Display"} %}
''' + user_template
    
    print("Original user template:")
    print("-" * 50)
    print(full_template)
    print("-" * 50)
    
    # Set up preprocessing only (no full environment yet)
    template_dirs = [
        os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates'),
    ]
    env = Environment(loader=FileSystemLoader(template_dirs))
    extension = ComponentExtensionDOM(env)
    
    try:
        # Step 1: See what preprocessing produces
        preprocessed = extension.preprocess(full_template, "user_template")
        print("After preprocessing:")
        print("-" * 50)
        print(preprocessed)
        print("-" * 50)
        
        # Step 2: Try to render the preprocessed template
        template = env.from_string(preprocessed)
        result = template.render()
        
        print("Final rendered result:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        
        # Check if variables were resolved
        if "test-project" in result and "Test Project Display" in result:
            print("✅ Variables were resolved!")
        else:
            print("❌ Variables were NOT resolved")
            
        if "{{ project.name }}" in result:
            print("❌ Still contains unresolved variables")
        else:
            print("✅ No unresolved variables found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_user_template()