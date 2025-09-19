#!/usr/bin/env python3
"""
Simple test to understand how event attributes are currently being processed.
"""

import sys
import os
sys.path.insert(0, '/Users/robbertuittenbroek/IdeaProjects/jinja-roos-components/jinja-roos-components')

from jinja2 import Environment, DictLoader
from jinja_roos_components.extension_dom import setup_components_dom

def test_current_behavior():
    print("Testing current event attribute behavior...")
    
    # Simple test with a literal string
    template_literal = '''
<c-button label="Test" @click="alert('hello')" />
'''

    # Test with variable reference
    template_with_var = '''
{% set message = "world" %}
<c-button label="Test" @click="alert(message)" />
'''
    
    env = Environment(loader=DictLoader({}))
    env = setup_components_dom(env)
    
    print("\n1. Testing literal string:")
    try:
        result = env.from_string(template_literal).render()
        print("Result:", result)
    except Exception as e:
        print("Error:", e)
    
    print("\n2. Testing variable reference:")
    try:
        result = env.from_string(template_with_var).render()
        print("Result:", result)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_current_behavior()