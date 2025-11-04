#!/usr/bin/env python3
"""
Test script to verify that aliases appear in documentation data.
"""

from examples.docs_service import get_components_data


def test_docs_includes_aliases():
    """Test that the documentation service includes aliases."""

    components = get_components_data()

    # Find aliases and regular components
    aliases = [comp for comp in components if comp.get('is_alias', False)]
    regular_components = [comp for comp in components if not comp.get('is_alias', False)]

    assert len(components) > 0, "Should have components in documentation"
    assert len(aliases) > 0, "Should have aliases in documentation"
    assert len(regular_components) > 0, "Should have regular components in documentation"


def test_specific_aliases_present():
    """Test that specific aliases are present in documentation."""

    components = get_components_data()
    component_names = [comp['name'] for comp in components]

    test_aliases = ['h1', 'h3', 'ol', 'ul', 'li']
    for alias_name in test_aliases:
        assert alias_name in component_names, f"Alias {alias_name} should be in documentation"


def test_alias_has_target():
    """Test that aliases have target information."""

    components = get_components_data()
    aliases = [comp for comp in components if comp.get('is_alias', False)]

    for alias in aliases:
        assert 'alias_target' in alias, f"Alias {alias['name']} should have alias_target"
        assert alias['alias_target'], f"Alias {alias['name']} should have non-empty alias_target"


def test_h1_alias_preset_information():
    """Test that h1 alias has preset attribute information."""

    components = get_components_data()
    h1_alias = next((comp for comp in components if comp['name'] == 'h1'), None)

    assert h1_alias is not None, "h1 alias should be in documentation"
    assert h1_alias.get('is_alias', False), "h1 should be marked as alias"

    # Check if type attribute exists and has preset information
    type_attr = next((attr for attr in h1_alias.get('attributes', []) if attr['name'] == 'type'), None)
    assert type_attr is not None, "h1 should have type attribute in documentation"