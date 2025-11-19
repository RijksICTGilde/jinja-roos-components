#!/usr/bin/env python3
"""
Test script to verify link component icon functionality.
"""

import os
from jinja2 import Environment, FileSystemLoader
from jinja_roos_components.extension import setup_components


def test_icon():
    """Test icon"""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template = '''
<c-icon
    icon="home"
/>
'''

    template = env.from_string(test_template)
    result = template.render()

    assert "rvo-icon" in result, \
        "Should have rvo icon CSS class"

    assert 'rvo-icon-home' in result, \
        "Should have correct icon in css"

    assert 'background-color:' not in result, \
        "Should not define background color"
    

def test_icon_color():
    """Test icon"""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    test_template = '''
<c-icon
    icon="home"
    color="hemelblauw"
/>
'''

    template = env.from_string(test_template)
    result = template.render()

    assert "rvo-icon--hemelblauw" in result, \
        "Should have rvo icon color class"
