#!/usr/bin/env python3
"""
Test rendering the button template directly to isolate issues.
"""

import sys
import os
sys.path.insert(0, '/Users/robbertuittenbroek/IdeaProjects/jinja-roos-components/jinja-roos-components')

from jinja2 import Environment, FileSystemLoader

def test_button_template():
    print("Testing button template directly...")
    
    # Set up proper file system loader to find component templates
    template_dirs = [
        os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates'),
    ]
    env = Environment(loader=FileSystemLoader(template_dirs))
    
    # Test context similar to what our preprocessing generates
    test_context = {
        '_component_context': {
            'label': 'Verwijderen',
            'kind': 'warning', 
            'size': 'sm',
            'showIcon': 'before',
            'icon': 'verwijderen',
            '@click': 'showDeleteConfirmation("test-project", "Test Project Display")'
        }
    }
    
    try:
        template = env.get_template('components/button.html.j2')
        result = template.render(**test_context)
        
        print("Button template rendered successfully:")
        print("=" * 60)
        print(result)
        print("=" * 60)
        
        if 'test-project' in result and 'Test Project Display' in result:
            print("✅ Event attribute values are correctly rendered!")
            return True
        else:
            print("❌ Expected values not found in output")
            return False
            
    except Exception as e:
        print(f"❌ Error rendering button template: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_button_template()