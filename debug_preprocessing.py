#!/usr/bin/env python3
"""
Debug the preprocessing step to see what's happening during component conversion.
"""

import sys
import os
sys.path.insert(0, '/Users/robbertuittenbroek/IdeaProjects/jinja-roos-components/jinja-roos-components')

from jinja2 import Environment, FileSystemLoader
from jinja_roos_components.extension_dom import ComponentExtensionDOM

def debug_preprocessing():
    print("Debugging preprocessing step...")
    
    # Your exact original example
    template_content = '''{% set project = {"name": "test-project", "display_name": "Test Project Display"} %}
<c-button 
    label="Verwijderen"
    kind="warning"
    size="sm"
    showIcon="before"
    icon="verwijderen"
    @click="showDeleteConfirmation('{{ project.name }}', '{{ project.display_name or project.name }}')" />'''
    
    # Set up environment with component extension
    template_dirs = [
        os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates'),
    ]
    env = Environment(loader=FileSystemLoader(template_dirs))
    
    # Add only the component extension for debugging
    extension = ComponentExtensionDOM(env)
    
    try:
        # Test preprocessing directly
        print("Original template:")
        print("-" * 50)
        print(template_content)
        print("-" * 50)
        
        preprocessed = extension.preprocess(template_content, "test_template")
        
        print("Preprocessed template:")
        print("-" * 50)
        print(preprocessed)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during preprocessing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_preprocessing()