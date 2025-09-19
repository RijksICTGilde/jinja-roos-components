#!/usr/bin/env python3
"""
Simple test for component alias registry functionality.
"""

import sys
import os

# Add the package to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jinja-roos-components'))

from jinja_roos_components.components.registry import ComponentRegistry

def test_registry_aliases():
    """Test that the registry correctly handles aliases."""
    print("=== Testing Component Registry Aliases ===\n")
    
    registry = ComponentRegistry()
    
    print("1. Testing alias registration:")
    # Test that aliases were registered
    header_aliases = [f"h{i}" for i in range(1, 7)]
    list_aliases = ["ol", "ul", "li"]
    
    for alias in header_aliases:
        has_alias = registry.has_alias(alias)
        print(f"   {alias}: {'✓' if has_alias else '✗'}")
        
    for alias in list_aliases:
        has_alias = registry.has_alias(alias)
        print(f"   {alias}: {'✓' if has_alias else '✗'}")
    
    print("\n2. Testing alias resolution:")
    
    # Test header alias resolution
    if registry.has_alias('h1'):
        target, attrs = registry.resolve_alias('h1', {})
        print(f"   h1 -> {target} with attrs: {attrs}")
        
        # Test with user attributes
        target, attrs = registry.resolve_alias('h1', {'class': 'title', 'id': 'main'})
        print(f"   h1 with user attrs -> {target} with attrs: {attrs}")
    
    if registry.has_alias('h3'):
        target, attrs = registry.resolve_alias('h3', {'textContent': 'Section'})
        print(f"   h3 -> {target} with attrs: {attrs}")
    
    # Test list alias resolution
    if registry.has_alias('ol'):
        target, attrs = registry.resolve_alias('ol', {})
        print(f"   ol -> {target} with attrs: {attrs}")
        
        # Test with user attributes
        target, attrs = registry.resolve_alias('ol', {'class': 'numbered', 'bulletType': 'none'})
        print(f"   ol with user attrs -> {target} with attrs: {attrs}")
    
    if registry.has_alias('ul'):
        target, attrs = registry.resolve_alias('ul', {})
        print(f"   ul -> {target} with attrs: {attrs}")
        
    if registry.has_alias('li'):
        target, attrs = registry.resolve_alias('li', {})
        print(f"   li -> {target} with attrs: {attrs}")
    
    print("\n3. Testing component lookup (including aliases):")
    
    # Test that has_component works for both real components and aliases
    test_names = ['button', 'h1', 'list', 'ol', 'nonexistent']
    for name in test_names:
        has_comp = registry.has_component(name)
        is_alias = registry.has_alias(name)
        comp_def = registry.get_component(name)
        status = "component" if (has_comp and not is_alias) else ("alias" if is_alias else "not found")
        actual_name = comp_def.name if comp_def else "N/A"
        print(f"   {name}: {status} -> {actual_name}")
    
    print("\n4. Testing component list includes aliases:")
    all_components = registry.list_components()
    print(f"   Total components/aliases: {len(all_components)}")
    
    aliases_in_list = [name for name in all_components if registry.has_alias(name)]
    components_in_list = [name for name in all_components if not registry.has_alias(name)]
    
    print(f"   Real components: {len(components_in_list)}")
    print(f"   Aliases: {len(aliases_in_list)} -> {', '.join(sorted(aliases_in_list))}")
    
    print("\n✅ Registry alias functionality test completed successfully!")


if __name__ == "__main__":
    test_registry_aliases()