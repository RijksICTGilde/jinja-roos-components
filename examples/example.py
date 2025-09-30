#!/usr/bin/env python3
"""
Simple example showing jinja-roos-components usage
"""

from jinja2 import Environment, DictLoader
from jinja_roos_components import setup_components

# Create example templates
templates = {
    'index.html': '''
{% extends "layouts/base.html.j2" %}

{% block title %}ROOS Components Example{% endblock %}

{% block content %}
<div style="max-width: 800px; margin: 2rem auto; padding: 0 1rem;">
    <h1>ROOS Components Demo</h1>
    
    <c-card title="Button Examples">
        <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem;">
            <c-button variant="primary">Primary</c-button>
            <c-button variant="secondary">Secondary</c-button>
            <c-button variant="danger">Danger</c-button>
            <c-button variant="ghost">Ghost</c-button>
            <c-button variant="link">Link</c-button>
        </div>
        
        <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem;">
            <c-button size="small">Small</c-button>
            <c-button size="medium">Medium</c-button>
            <c-button size="large">Large</c-button>
        </div>
        
        <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
            <c-button :disabled="true">Disabled</c-button>
            <c-button :loading="true">Loading</c-button>
            <c-button @click="alert('Button clicked!')">Clickable</c-button>
        </div>
    </c-card>
    
    <c-card title="Card Examples" style="margin-top: 2rem;">
        <p>This is a basic card with default styling.</p>
    </c-card>
    
    <c-card title="Elevated Card" :elevated="true" style="margin-top: 1rem;">
        <p>This card has an elevated shadow effect.</p>
    </c-card>
    
    <c-card :bordered="false" style="margin-top: 1rem;">
        <p>This card has no border.</p>
    </c-card>
</div>
{% endblock %}
    ''',
}

def main():
    # Setup Jinja2 environment
    env = Environment(loader=DictLoader(templates))
    
    # Setup ROOS components
    setup_components(
        env,
        theme="default",
        htmx=False,  # Set to True to enable HTMX
        user_css_files=[],
        user_js_files=[]
    )
    
    # Render template
    template = env.get_template('index.html')
    html = template.render()
    
    # Save to file
    with open('example_output.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("Example generated: example_output.html")
    print("Note: Run 'npm run build' first to generate CSS/JS assets")

if __name__ == '__main__':
    main()