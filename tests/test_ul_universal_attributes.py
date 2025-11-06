#!/usr/bin/env python3
"""
Test universal HTML attributes (id, class) on the c-ul component.
This test verifies that id and class attributes are properly passed through
and rendered in the final HTML output.
"""

import pytest
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from jinja_roos_components import setup_components


class TestUlUniversalAttributes:
    """Test suite for universal HTML attributes on the ul component."""

    @pytest.fixture
    def env(self):
        """Create a Jinja2 environment with component support."""
        # Point to the actual templates directory
        templates_dir = Path(__file__).parent.parent / 'src' / 'jinja_roos_components' / 'templates'
        env = Environment(loader=FileSystemLoader(str(templates_dir)))
        setup_components(env)
        return env

    def test_ul_with_id_attribute(self, env):
        """Test that id attribute is properly rendered on ul component."""
        template_str = '<c-ul id="my-list"></c-ul>'
        template = env.from_string(template_str)
        result = template.render()

        # Check that id attribute is present in the output
        assert 'id="my-list"' in result, f"Expected id attribute in output, got: {result}"

    def test_ul_with_class_attribute(self, env):
        """Test that class attribute is properly rendered on ul component."""
        template_str = '<c-ul class="custom-class"></c-ul>'
        template = env.from_string(template_str)
        result = template.render()

        # Check that custom class is added to the class list
        assert 'custom-class' in result, f"Expected custom-class in output, got: {result}"
        # Also check that default classes are still present
        assert 'rvo-ul' in result, f"Expected default rvo-ul class in output, got: {result}"

    def test_ul_with_multiple_classes(self, env):
        """Test that multiple classes in class attribute are properly rendered."""
        template_str = '<c-ul class="class-one class-two class-three"></c-ul>'
        template = env.from_string(template_str)
        result = template.render()

        # Check that all custom classes are present
        assert 'class-one' in result, f"Expected class-one in output, got: {result}"
        assert 'class-two' in result, f"Expected class-two in output, got: {result}"
        assert 'class-three' in result, f"Expected class-three in output, got: {result}"

    def test_ul_with_id_and_class(self, env):
        """Test that both id and class attributes work together."""
        template_str = '<c-ul id="my-list" class="custom-class"></c-ul>'
        template = env.from_string(template_str)
        result = template.render()

        # Check that both attributes are present
        assert 'id="my-list"' in result, f"Expected id attribute in output, got: {result}"
        assert 'custom-class' in result, f"Expected custom-class in output, got: {result}"

    def test_ul_with_items_and_id(self, env):
        """Test that id attribute works with list items."""
        template_str = '<c-ul id="item-list" :items="[\'Item 1\', \'Item 2\', \'Item 3\']"></c-ul>'
        template = env.from_string(template_str)
        result = template.render()

        # Check that id is present
        assert 'id="item-list"' in result, f"Expected id attribute in output, got: {result}"
        # Check that items are rendered
        assert 'Item 1' in result, f"Expected Item 1 in output, got: {result}"
        assert 'Item 2' in result, f"Expected Item 2 in output, got: {result}"
        assert 'Item 3' in result, f"Expected Item 3 in output, got: {result}"

    def test_ul_with_jinja_variable_in_id(self, env):
        """Test that Jinja variables work in id attribute."""
        template_str = '''
        {% set list_id = "dynamic-list" %}
        <c-ul id="{{ list_id }}" class="test"></c-ul>
        '''
        template = env.from_string(template_str)
        result = template.render()

        # Check that the variable was interpolated
        assert 'id="dynamic-list"' in result, f"Expected id with interpolated variable in output, got: {result}"

    def test_ul_with_jinja_variable_in_class(self, env):
        """Test that Jinja variables work in class attribute."""
        template_str = '''
        {% set extra_class = "highlighted" %}
        <c-ul class="{{ extra_class }}"></c-ul>
        '''
        template = env.from_string(template_str)
        result = template.render()

        # Check that the variable was interpolated
        assert 'highlighted' in result, f"Expected class with interpolated variable in output, got: {result}"

    def test_ul_without_id_or_class(self, env):
        """Test that ul works normally without id or class attributes."""
        template_str = '<c-ul></c-ul>'
        template = env.from_string(template_str)
        result = template.render()

        # Check that default classes are present
        assert 'rvo-ul' in result, f"Expected default rvo-ul class in output, got: {result}"
        # Check that there's no empty id attribute
        assert 'id=""' not in result, f"Unexpected empty id attribute in output, got: {result}"

    def test_ol_with_id_and_class(self, env):
        """Test that id and class also work on ol component (ordered list variant)."""
        template_str = '<c-ol id="ordered-list" class="numbered"></c-ol>'
        template = env.from_string(template_str)
        result = template.render()

        # Check that both attributes are present
        assert 'id="ordered-list"' in result, f"Expected id attribute in output, got: {result}"
        assert 'numbered' in result, f"Expected numbered class in output, got: {result}"
        # Check that it's an ordered list
        assert 'rvo-ol' in result or '<ol' in result, f"Expected ordered list in output, got: {result}"

    def test_ul_with_other_universal_attributes(self, env):
        """Test that other universal HTML attributes (style) also work."""
        template_str = '<c-ul id="styled-list" style="color: red;"></c-ul>'
        template = env.from_string(template_str)
        result = template.render()

        # Check that all attributes are present
        assert 'id="styled-list"' in result, f"Expected id attribute in output, got: {result}"
        assert 'style="color: red;"' in result, f"Expected style attribute in output, got: {result}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])