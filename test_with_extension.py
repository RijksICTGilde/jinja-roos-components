#!/usr/bin/env python3
"""
Test with the component extension to see if that's causing the issue.
"""

import sys
import os
sys.path.insert(0, '/Users/robbertuittenbroek/IdeaProjects/jinja-roos-components/jinja-roos-components')

from jinja2 import Environment, FileSystemLoader
from jinja_roos_components.extension_dom import setup_components_dom

def test_with_extension():
    print("Testing with component extension...")
    
    # Use the exact preprocessed template that works
    preprocessed_template = '''{% set project = {"name": "test-project", "display_name": "Test Project Display"} %}
{% set _event_attr_wtcvovln %}showDeleteConfirmation('{{ project.name }}', '{{ project.display_name or project.name }}'){% endset %}{% set _component_context = {"label": "Verwijderen", "kind": "warning", "size": "sm", "showIcon": "before", "icon": "verwijderen", '@click': _event_attr_wtcvovln} %}{% include "components/button.html.j2" with context %}'''
    
    template_dirs = [
        os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates'),
    ]
    env = Environment(loader=FileSystemLoader(template_dirs))
    env = setup_components_dom(env)  # This adds the component extension
    
    try:
        template = env.from_string(preprocessed_template)
        result = template.render()
        
        print("Template rendered successfully with extension:")
        print("=" * 60)
        print(result)
        print("=" * 60)
        
        if "test-project" in result and "Test Project Display" in result:
            print("✅ Extension doesn't interfere with rendering!")
            return True
        else:
            print("❌ Expected values not found")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_with_extension()