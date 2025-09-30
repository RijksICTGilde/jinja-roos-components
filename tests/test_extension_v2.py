"""
Test the new HTML parsing based extension
"""

from jinja2 import Environment
from jinja_roos_components.extension_v2 import ComponentExtension as ComponentExtensionV2
from jinja_roos_components.components.registry import ComponentRegistry

# Create environment with the new extension
env = Environment()
env.add_extension(ComponentExtensionV2)

# Get the extension
ext = None
for extension in env.extensions.values():
    if isinstance(extension, ComponentExtensionV2):
        ext = extension
        break

# Test cases
test_cases = [
    # Simple nested
    ('<c-page><c-card>Content</c-card></c-page>', 'Simple nested'),
    
    # Double nested
    ('<c-page><c-layout-flow><c-card>Content</c-card></c-layout-flow></c-page>', 'Double nested'),
    
    # With attributes
    ('<c-page title="Test"><c-card outline="true">Content</c-card></c-page>', 'With attributes'),
    
    # Multiple siblings
    ('<c-page><c-card>Card 1</c-card><c-card>Card 2</c-card></c-page>', 'Multiple siblings'),
    
    # Mixed content
    ('<c-page><h1>Title</h1><c-card>Content</c-card></c-page>', 'Mixed content'),
    
    # Real example structure with whitespace
    ('''<c-page title="Test">
    <c-layout-flow gap="xl">
        <c-card outline="true">
            <c-layout-flow gap="md">
                <p>Content</p>
            </c-layout-flow>
        </c-card>
    </c-layout-flow>
</c-page>''', 'Real structure with whitespace'),

    # Complex nested structure
    ('''<c-page title="Project Aanmaken - ROOS" lang="nl">
    <c-layout-flow gap="xl">
        <!-- Header -->
        <c-card background="color" backgroundColor="hemelblauw" padding="lg">
            <h1 class="utrecht-heading-1">Project Aanmaken - ROOS</h1>
        </c-card>

        <!-- Form -->
        <c-card outline="true" padding="lg">
            <form method="POST" action="/api/projects/create-basic">
                <c-layout-flow gap="lg">
                    <div>
                        <label>Projectnaam</label>
                        <c-input name="project-name" type="text" required="true" />
                    </div>
                </c-layout-flow>
            </form>
        </c-card>
    </c-layout-flow>
</c-page>''', 'Complex real-world structure'),
]

print("Testing new HTML parsing based extension...")
print("=" * 60)

for test_html, description in test_cases:
    print(f"\n=== {description} ===")
    print(f"Input length: {len(test_html)} chars")
    
    try:
        # Preprocess
        result = ext.preprocess(test_html, 'test', None)
        
        # Check for remaining components
        import re
        remaining = re.findall(r'<c-[\w-]+', result)
        
        if remaining:
            print(f"❌ FAILED - Remaining components: {set(remaining)}")
            print(f"Result preview: {result[:200]}...")
        else:
            print(f"✅ PASSED - All components processed")
            print(f"Result length: {len(result)} chars")
            
            # Check that we have the expected Jinja tags
            includes = result.count('{% include')
            captures = result.count('{% set _captured_content_')
            print(f"   Generated: {includes} includes, {captures} capture blocks")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()