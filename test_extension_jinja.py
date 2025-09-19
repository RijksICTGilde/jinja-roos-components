#!/usr/bin/env python3

"""
Test complex Jinja expressions using the actual extension.
"""

import sys
import os
sys.path.insert(0, '/Users/robbertuittenbroek/IdeaProjects/jinja-roos-components/jinja-roos-components')

from jinja2 import Environment, DictLoader
from jinja_roos_components import setup_components

def test_extension_jinja():
    """Test complex Jinja expressions with the actual extension."""
    
    templates = {
        'test.html': '''
{% set service_def = {"icon": "calendar", "color": "blue"} %}
<c-icon icon="{{ service_def.icon }}" size="xl" color="{{ service_def.color }}" />
        '''
    }
    
    # Create environment
    env = Environment(loader=DictLoader(templates))
    setup_components(env)
    
    try:
        # Get the template and inspect preprocessing
        template = env.get_template('test.html')
        
        # The preprocessor should have converted it already
        print("Template preprocessing test:")
        
        # Try to render
        result = template.render()
        print(f"Rendered successfully: {len(result)} characters")
        print(f"Result preview: {result[:200]}...")
        
        # Check if the result contains proper icon rendering
        if 'calendar' in result and 'blue' in result:
            print("✓ Jinja expressions were properly evaluated")
        else:
            print("✗ Jinja expressions may not have been evaluated correctly")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

def test_preprocessing_directly():
    """Test the preprocessing step directly."""
    
    from jinja_roos_components.extension import ComponentExtension
    
    # Create a minimal environment
    env = Environment()
    extension = ComponentExtension(env)
    
    # Test source
    source = '''{% set service_def = {"icon": "calendar", "color": "blue"} %}
<c-icon icon="{{ service_def.icon }}" size="xl" color="{{ service_def.color }}" />'''
    
    print("\nDirect preprocessing test:")
    print(f"Original: {source}")
    
    try:
        result = extension.preprocess(source, "test", None)
        print(f"Preprocessed: {result}")
        
        # Check if expressions are properly extracted
        if 'service_def.icon' in result and 'service_def.color' in result:
            print("✓ Preprocessing properly extracted expressions")
        elif '"{{ service_def.icon }}"' in result:
            print("✗ Preprocessing treated expressions as strings")
        else:
            print("? Could not determine preprocessing result")
            
    except Exception as e:
        print(f"ERROR in preprocessing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_extension_jinja()
    test_preprocessing_directly()