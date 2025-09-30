#!/usr/bin/env python3
"""
Test script to verify that aliases appear in documentation data.
"""

import sys
import os
from pathlib import Path

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent / 'jinja-roos-components'))

def test_docs_with_aliases():
    """Test that the documentation service includes aliases."""
    print("=== Testing Documentation with Aliases ===\n")
    
    # Import the docs service
    from examples.docs_service import get_components_data
    
    # Get components data
    components = get_components_data()
    
    print(f"Total components/aliases in docs: {len(components)}")
    
    # Find aliases and regular components
    aliases = [comp for comp in components if comp.get('is_alias', False)]
    regular_components = [comp for comp in components if not comp.get('is_alias', False)]
    
    print(f"Regular components: {len(regular_components)}")
    print(f"Aliases: {len(aliases)}")
    
    print("\n🔹 Aliases found in documentation:")
    for alias in aliases:
        target = alias.get('alias_target', 'unknown')
        defaults = alias.get('alias_defaults', {})
        defaults_str = ', '.join([f"{k}={v}" for k, v in defaults.items()]) if defaults else "none"
        print(f"   c-{alias['name']} -> c-{target} (defaults: {defaults_str})")
    
    print(f"\n🔸 Sample regular components:")
    for comp in regular_components[:5]:
        print(f"   c-{comp['name']}")
    
    # Test specific aliases
    print(f"\n📋 Testing specific alias examples:")
    
    test_aliases = ['h1', 'h3', 'ol', 'ul', 'li']
    for alias_name in test_aliases:
        alias = next((comp for comp in components if comp['name'] == alias_name), None)
        if alias:
            example = alias.get('example', 'No example')
            print(f"   c-{alias_name}: {example}")
        else:
            print(f"   c-{alias_name}: ❌ NOT FOUND")
    
    # Verify alias attributes have preset information
    print(f"\n🎯 Testing preset attribute information:")
    h1_alias = next((comp for comp in components if comp['name'] == 'h1'), None)
    if h1_alias:
        type_attr = next((attr for attr in h1_alias.get('attributes', []) if attr['name'] == 'type'), None)
        if type_attr:
            is_preset = type_attr.get('preset_by_alias', False)
            default_val = type_attr.get('default', None)
            print(f"   c-h1 'type' attribute: preset={is_preset}, default={default_val}")
        else:
            print(f"   c-h1 'type' attribute: ❌ NOT FOUND")
    
    print(f"\n✅ Documentation alias integration test completed!")
    print(f"📊 Summary: {len(aliases)} aliases + {len(regular_components)} components = {len(components)} total")


if __name__ == "__main__":
    try:
        test_docs_with_aliases()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()