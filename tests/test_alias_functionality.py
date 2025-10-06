#!/usr/bin/env python3
"""
Test script for component alias functionality.
"""

from jinja2 import Environment, DictLoader
from jinja_roos_components.extension import setup_components

def test_header_aliases():
    """Test that header aliases (c-h1 to c-h6) work correctly."""
    print("Testing header aliases...")
    
    # Setup Jinja environment
    env = Environment(
        loader=DictLoader({})
    )
    setup_components(env, strict_validation=True)
    
    # Test h1 alias
    template_h1 = env.from_string("<c-h1>Main Title</c-h1>")
    result_h1 = template_h1.render()
    print(f"c-h1 result: {result_h1[:100]}...")
    
    # Test h2 with additional attributes
    template_h2 = env.from_string('<c-h2 class="custom">Subtitle</c-h2>')
    result_h2 = template_h2.render()
    print(f"c-h2 with class result: {result_h2[:100]}...")
    
    # Test h3
    template_h3 = env.from_string("<c-h3>Section Title</c-h3>")
    result_h3 = template_h3.render()
    print(f"c-h3 result: {result_h3[:100]}...")


def test_list_aliases():
    """Test that list aliases (c-ol, c-ul, c-li) work correctly."""
    print("\nTesting list aliases...")
    
    # Setup Jinja environment
    env = Environment(
        loader=DictLoader({})
    )
    setup_components(env, strict_validation=True)
    
    # Test unordered list
    template_ul = env.from_string('<c-ul><c-li>Item 1</c-li><c-li>Item 2</c-li></c-ul>')
    result_ul = template_ul.render()
    print(f"c-ul result: {result_ul[:100]}...")
    
    # Test ordered list
    template_ol = env.from_string('<c-ol><c-li>First</c-li><c-li>Second</c-li></c-ol>')
    result_ol = template_ol.render()
    print(f"c-ol result: {result_ol[:100]}...")
    
    # Test with additional attributes
    template_ul_custom = env.from_string('<c-ul class="custom-list"><c-li>Custom item</c-li></c-ul>')
    result_ul_custom = template_ul_custom.render()
    print(f"c-ul with class result: {result_ul_custom[:100]}...")


def test_alias_validation():
    """Test that aliases work with validation system."""
    print("\nTesting alias validation...")
    
    # Setup Jinja environment with strict validation
    env = Environment(
        loader=DictLoader({})
    )
    setup_components(env, strict_validation=True)
    
    # Test valid alias usage
    try:
        template = env.from_string('<c-h1 class="title">Valid Title</c-h1>')
        result = template.render()
        print("✓ Valid alias usage works")
    except Exception as e:
        print(f"✗ Valid alias usage failed: {e}")
    
    # Test invalid attribute (should fail with strict validation)
    try:
        template = env.from_string('<c-h1 invalidattr="test">Invalid Title</c-h1>')
        result = template.render()
        print("✗ Invalid attribute validation failed - should have raised error")
    except Exception as e:
        print(f"✓ Invalid attribute correctly rejected: {type(e).__name__}")


def test_registry_functionality():
    """Test that the registry correctly handles aliases."""
    print("\nTesting registry functionality...")
    
    from jinja_roos_components.registry import ComponentRegistry
    
    registry = ComponentRegistry()
    
    # Test alias registration
    print(f"Has h1 alias: {registry.has_alias('h1')}")
    print(f"Has ol alias: {registry.has_alias('ol')}")
    print(f"Has nonexistent alias: {registry.has_alias('nonexistent')}")
    
    # Test alias resolution
    if registry.has_alias('h1'):
        target, attrs = registry.resolve_alias('h1', {'class': 'custom'})
        print(f"h1 resolves to: {target} with attrs: {attrs}")
    
    if registry.has_alias('ol'):
        target, attrs = registry.resolve_alias('ol', {})
        print(f"ol resolves to: {target} with attrs: {attrs}")
    
    # Test component listing includes aliases
    components = registry.list_components()
    aliases = [name for name in components if registry.has_alias(name)]
    print(f"Found {len(aliases)} aliases: {', '.join(sorted(aliases))}")


if __name__ == "__main__":
    print("=== Component Alias Functionality Test ===\n")
    
    try:
        test_registry_functionality()
        test_header_aliases()
        test_list_aliases()
        test_alias_validation()
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()