#!/usr/bin/env python3
"""
Test script to verify alert component icon functionality.
"""

import os
from jinja2 import Environment, FileSystemLoader
from jinja_roos_components.extension import setup_components


def test_alert_icon():
    """Test that alert components get the correct icon based on kind"""

    # Set up Jinja environment with ROOS components
    template_dir = os.path.join(os.path.dirname(__file__), 'jinja-roos-components', 'jinja_roos_components', 'templates')

    env = Environment(loader=FileSystemLoader([template_dir, '.']))
    env = setup_components(env)

    # Test info alert
    test_template = '''
<c-alert
    kind="info"
    heading="Information"
    content="This is an info alert"
/>
'''

    template = env.from_string(test_template)
    result = template.render()

    assert "rvo-icon-info" in result, \
        "Info alert should have rvo-icon-info class"
    assert "rvo-status-icon-info" in result, \
        "Info alert should have rvo-status-icon-info class"

    # Test warning alert
    test_template = '''
<c-alert
    kind="warning"
    heading="Warning"
    content="This is a warning alert"
/>
'''

    template = env.from_string(test_template)
    result = template.render()

    assert "rvo-icon-waarschuwing" in result, \
        "Warning alert should have rvo-icon-waarschuwing class"
    assert "rvo-status-icon-waarschuwing" in result, \
        "Warning alert should have rvo-status-icon-waarschuwing class"

    # Test error alert
    test_template = '''
<c-alert
    kind="error"
    heading="Error"
    content="This is an error alert"
/>
'''

    template = env.from_string(test_template)
    result = template.render()

    assert "rvo-icon-foutmelding" in result, \
        "Error alert should have rvo-icon-foutmelding class"
    assert "rvo-status-icon-foutmelding" in result, \
        "Error alert should have rvo-status-icon-foutmelding class"

    # Test success alert
    test_template = '''
<c-alert
    kind="success"
    heading="Success"
    content="This is a success alert"
/>
'''

    template = env.from_string(test_template)
    result = template.render()

    assert "rvo-icon-bevestiging" in result, \
        "Success alert should have rvo-icon-bevestiging class"
    assert "rvo-status-icon-bevestiging" in result, \
        "Success alert should have rvo-status-icon-bevestiging class"
