"""
Debug script to trace component processing
"""

import re
from jinja2 import Environment, FileSystemLoader
from jinja_roos_components import setup_components
from jinja_roos_components.extension import ComponentExtension

# Test template with nested components
test_template = '''
<c-card title="Test">
    <c-layout-flow gap="md">
        <p>Content</p>
    </c-layout-flow>
</c-card>
'''

# Create environment and setup
env = Environment(loader=FileSystemLoader('.'))
setup_components(env)

# Get the extension
ext = None
for extension in env.extensions.values():
    if isinstance(extension, ComponentExtension):
        ext = extension
        break

if ext:
    print("ComponentExtension found!")
    print(f"Component pattern: {ext.component_pattern.pattern}")
    
    # Test pattern matching
    matches = list(ext.component_pattern.finditer(test_template))
    print(f"\nFound {len(matches)} matches:")
    for i, match in enumerate(matches):
        print(f"\nMatch {i+1}:")
        print(f"  Full match: {match.group(0)[:50]}...")
        print(f"  Component name: {match.group(1)}")
        print(f"  Attributes: {match.group(2)}")
        print(f"  Content: {match.group(3)[:50] if match.group(3) else 'None'}...")
    
    # Test preprocessing
    print("\n--- Testing preprocessing ---")
    result = ext.preprocess(test_template, 'test', None)
    print(f"Preprocessed length: {len(result)}")
    print(f"Contains <c- tags: {'<c-' in result}")
    
    # Show first 200 chars of result
    print(f"\nFirst 200 chars of result:")
    print(result[:200])
else:
    print("ComponentExtension NOT found in environment!")

# Also test with the full environment
print("\n--- Testing with env.from_string ---")
template = env.from_string(test_template)
rendered = template.render()
print(f"Rendered length: {len(rendered)}")
print(f"Contains <c- tags: {'<c-' in rendered}")

# Check what's actually in the environment
print(f"\nEnvironment extensions: {list(env.extensions.keys())}")