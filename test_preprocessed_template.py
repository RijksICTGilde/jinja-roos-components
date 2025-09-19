#!/usr/bin/env python3
"""
Test rendering the exact preprocessed template to debug syntax errors.
"""

import sys
import os
sys.path.insert(0, '/Users/robbertuittenbroek/IdeaProjects/jinja-roos-components/jinja-roos-components')

from jinja2 import Environment, FileSystemLoader

def test_preprocessed_template():
    print("Testing preprocessed template...")
    
    # The exact preprocessed template from debug output
    preprocessed_template = '''{% set project = {"name": "test-project", "display_name": "Test Project Display"} %}
{% set _event_attr_utsvakky %}showDeleteConfirmation('{{ project.name }}', '{{ project.display_name or project.name }}'){% endset %}{% set _component_context = {"label": "Verwijderen", "kind": "warning", "size": "sm", "showIcon": "before", "icon": "verwijderen", '@click': _event_attr_utsvakky} %}{% include "components/button.html.j2" with context %}'''
    
    # Set up proper file system loader to find component templates
    template_dirs = [
        os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates'),
    ]
    env = Environment(loader=FileSystemLoader(template_dirs))
    
    try:
        template = env.from_string(preprocessed_template)
        result = template.render()
        
        print("Preprocessed template rendered successfully:")
        print("=" * 60)
        print(result)
        print("=" * 60)
        
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
    test_preprocessed_template()