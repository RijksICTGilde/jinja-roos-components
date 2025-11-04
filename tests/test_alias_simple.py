#!/usr/bin/env python3
"""
Simple test for component alias registry functionality.
"""

from jinja_roos_components.registry import ComponentRegistry


def test_registry_alias_registration():
    """Test that header aliases are registered."""
    registry = ComponentRegistry()

    header_aliases = [f"h{i}" for i in range(1, 7)]
    for alias in header_aliases:
        assert registry.has_alias(alias), f"Header alias {alias} should be registered"

def test_alias_resolution_header():
    """Test header alias resolution."""
    registry = ComponentRegistry()

    # Test h1 without user attributes
    target, attrs = registry.resolve_alias('h1', {})
    assert target == 'heading', f"h1 should resolve to 'heading', got {target}"
    assert 'type' in attrs, "h1 should set type attribute"

    # Test h1 with user attributes
    target, attrs = registry.resolve_alias('h1', {'class': 'title', 'id': 'main'})
    assert target == 'heading'
    assert 'type' in attrs
    assert attrs['class'] == 'title'
    assert attrs['id'] == 'main'

def test_component_lookup_with_aliases():
    """Test that has_component works for both real components and aliases."""
    registry = ComponentRegistry()

    # Test real component
    assert registry.has_component('button'), "button should be a component"
    assert not registry.has_alias('button'), "button should not be an alias"

    # Test alias
    assert registry.has_component('h1'), "h1 should be found as component"
    assert registry.has_alias('h1'), "h1 should be an alias"

    # Test non-existent
    assert not registry.has_component('nonexistent'), "nonexistent should not be found"
    assert not registry.has_alias('nonexistent'), "nonexistent should not be an alias"


def test_component_list_includes_aliases():
    """Test that list_components includes aliases."""
    registry = ComponentRegistry()

    all_components = registry.list_components()
    aliases_in_list = [name for name in all_components if registry.has_alias(name)]
    components_in_list = [name for name in all_components if not registry.has_alias(name)]

    assert len(all_components) > 0, "Should have components"
    assert len(aliases_in_list) > 0, "Should have aliases in list"
    assert len(components_in_list) > 0, "Should have real components in list"

    # Check specific aliases
    expected_aliases = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    for alias in expected_aliases:
        assert alias in all_components, f"Alias {alias} should be in component list"