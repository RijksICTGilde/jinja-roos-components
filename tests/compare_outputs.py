#!/usr/bin/env python3
"""
Compare the output from preprocessing vs manual template to find the difference.
"""

import sys
import os
sys.path.insert(0, '/Users/robbertuittenbroek/IdeaProjects/jinja-roos-components/jinja-roos-components')

from jinja2 import Environment, FileSystemLoader
from jinja_roos_components.extension_dom import ComponentExtensionDOM

def compare_outputs():
    print("Comparing preprocessing output vs manual template...")
    
    # Your exact original example
    template_content = '''{% set project = {"name": "test-project", "display_name": "Test Project Display"} %}
<c-button 
    label="Verwijderen"
    kind="warning"
    size="sm"
    showIcon="before"
    icon="verwijderen"
    @click="showDeleteConfirmation('{{ project.name }}', '{{ project.display_name or project.name }}')" />'''
    
    template_dirs = [
        os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates'),
    ]
    env = Environment(loader=FileSystemLoader(template_dirs))
    extension = ComponentExtensionDOM(env)
    
    try:
        # Get preprocessing output
        preprocessed = extension.preprocess(template_content, "test_template")
        
        print("Preprocessed output:")
        print(repr(preprocessed))  # Use repr to see exact characters
        print("\nPreprocessed output (readable):")
        print(preprocessed)
        
    except Exception as e:
        print(f"❌ Error during preprocessing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_outputs()