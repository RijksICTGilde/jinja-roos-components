#!/usr/bin/env python3
"""
Tests for the select component.
Tests different ways to define options and various select configurations.
"""

import pytest
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from jinja_roos_components import setup_components


@pytest.fixture
def env():
    """Create a Jinja2 environment with the roos components extension."""
    environment = Environment(loader=FileSystemLoader([]))
    return setup_components(environment)


def parse_html(html):
    """Parse HTML string into BeautifulSoup object."""
    return BeautifulSoup(html, 'html.parser')


class TestSelectOptions:
    """Test different ways to define select options."""

    def test_options_as_simple_strings(self, env):
        """Test options defined as a list of strings."""
        template = '''
<c-select
    name="color"
    :options="['red', 'green', 'blue']"
/>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        assert select is not None
        assert select.get('name') == 'color'

        options = select.find_all('option')
        assert len(options) == 3

        assert options[0].get('value') == 'red'
        assert options[0].get_text(strip=True) == 'red'

        assert options[1].get('value') == 'green'
        assert options[1].get_text(strip=True) == 'green'

        assert options[2].get('value') == 'blue'
        assert options[2].get_text(strip=True) == 'blue'

    def test_options_as_objects_with_value_and_label(self, env):
        """Test options defined as objects with value and label properties."""
        template = '''
<c-select
    name="size"
    :options="[
        {'value': 'sm', 'label': 'Small'},
        {'value': 'md', 'label': 'Medium'},
        {'value': 'lg', 'label': 'Large'}
    ]"
/>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        options = soup.find_all('option')
        assert len(options) == 3

        assert options[0].get('value') == 'sm'
        assert options[0].get_text(strip=True) == 'Small'

        assert options[1].get('value') == 'md'
        assert options[1].get_text(strip=True) == 'Medium'

        assert options[2].get('value') == 'lg'
        assert options[2].get_text(strip=True) == 'Large'

    def test_options_from_variable(self, env):
        """Test options passed from a template variable."""
        template = '''
{% set colors = ['red', 'green', 'blue'] %}
<c-select
    name="color"
    :options="colors"
/>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        options = soup.find_all('option')
        assert len(options) == 3
        assert options[0].get('value') == 'red'
        assert options[1].get('value') == 'green'
        assert options[2].get('value') == 'blue'

    def test_options_from_context_variable(self, env):
        """Test options passed from render context."""
        template = '<c-select name="country" :options="countries" />'

        result = env.from_string(template).render(
            countries=['Netherlands', 'Belgium', 'Germany']
        )
        soup = parse_html(result)

        options = soup.find_all('option')
        assert len(options) == 3
        assert options[0].get('value') == 'Netherlands'
        assert options[1].get('value') == 'Belgium'
        assert options[2].get('value') == 'Germany'

    def test_options_with_object_variable(self, env):
        """Test options as objects passed from render context."""
        template = '<c-select name="priority" :options="priorities" />'

        result = env.from_string(template).render(
            priorities=[
                {'value': '1', 'label': 'Low'},
                {'value': '2', 'label': 'Medium'},
                {'value': '3', 'label': 'High'}
            ]
        )
        soup = parse_html(result)

        options = soup.find_all('option')
        assert len(options) == 3

        assert options[0].get('value') == '1'
        assert options[0].get_text(strip=True) == 'Low'

        assert options[1].get('value') == '2'
        assert options[1].get_text(strip=True) == 'Medium'

        assert options[2].get('value') == '3'
        assert options[2].get_text(strip=True) == 'High'

    def test_empty_options(self, env):
        """Test select with no options."""
        template = '<c-select name="empty" :options="[]" />'
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        assert select is not None
        assert select.get('name') == 'empty'

        options = select.find_all('option')
        assert len(options) == 0

    def test_options_without_colon_prefix(self, env):
        """Test options defined without the : prefix (as JSON string)."""
        template = '''
<c-select
    name="color"
    options='["red", "green", "blue"]'
/>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        assert select is not None
        assert select.get('name') == 'color'

        options = select.find_all('option')
        assert len(options) == 3
        assert options[0].get('value') == 'red'
        assert options[1].get('value') == 'green'
        assert options[2].get('value') == 'blue'

    def test_options_objects_without_colon_prefix(self, env):
        """Test options as objects without the : prefix (as JSON string)."""
        template = '''
<c-select
    name="size"
    options='[{"value": "sm", "label": "Small"}, {"value": "md", "label": "Medium"}]'
/>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        options = soup.find_all('option')
        assert len(options) == 2

        assert options[0].get('value') == 'sm'
        assert options[0].get_text(strip=True) == 'Small'

        assert options[1].get('value') == 'md'
        assert options[1].get_text(strip=True) == 'Medium'


class TestSelectAttributes:
    """Test select element attributes."""

    def test_basic_attributes(self, env):
        """Test id and name attributes."""
        template = '<c-select id="my-select" name="field-name" :options="[]" />'
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        assert select.get('id') == 'my-select'
        assert select.get('name') == 'field-name'

    def test_disabled_attribute(self, env):
        """Test disabled state."""
        template = '<c-select name="test" :disabled="true" :options="[]" />'
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        assert select.has_attr('disabled')

        classes = select.get('class', [])
        assert 'utrecht-select--disabled' in classes

    def test_required_attribute(self, env):
        """Test required state."""
        template = '<c-select name="test" :required="true" :options="[]" />'
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        assert select.has_attr('required')

        classes = select.get('class', [])
        assert 'utrecht-select--required' in classes

    def test_invalid_attribute(self, env):
        """Test invalid state."""
        template = '<c-select name="test" :invalid="true" :options="[]" />'
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        assert select.get('aria-invalid') == 'true'

        classes = select.get('class', [])
        assert 'utrecht-select--invalid' in classes

    def test_focus_attribute(self, env):
        """Test focus state."""
        template = '<c-select name="test" :focus="true" :options="[]" />'
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        classes = select.get('class', [])
        assert 'utrecht-select--focus' in classes
        assert 'utrecht-select--focus-visible' in classes

    def test_custom_class(self, env):
        """Test custom CSS class."""
        template = '<c-select name="test" class="my-custom-class" :options="[]" />'
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        classes = select.get('class', [])
        assert 'my-custom-class' in classes
        assert 'utrecht-select' in classes


class TestSelectValue:
    """Test select value selection."""

    def test_value_attribute_with_strings(self, env):
        """Test pre-selecting a value with string options."""
        template = '''
<c-select
    name="color"
    value="green"
    :options="['red', 'green', 'blue']"
/>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        options = soup.find_all('option')

        # Red should not be selected
        red_option = [o for o in options if o.get('value') == 'red'][0]
        assert not red_option.has_attr('selected')

        # Green should be selected
        green_option = [o for o in options if o.get('value') == 'green'][0]
        assert green_option.has_attr('selected')

        # Blue should not be selected
        blue_option = [o for o in options if o.get('value') == 'blue'][0]
        assert not blue_option.has_attr('selected')

    def test_value_attribute_with_objects(self, env):
        """Test pre-selecting a value with object options."""
        template = '''
<c-select
    name="size"
    value="md"
    :options="[
        {'value': 'sm', 'label': 'Small'},
        {'value': 'md', 'label': 'Medium'},
        {'value': 'lg', 'label': 'Large'}
    ]"
/>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        options = soup.find_all('option')
        md_option = [o for o in options if o.get('value') == 'md'][0]
        assert md_option.has_attr('selected')

    def test_default_value(self, env):
        """Test default value when no value is set."""
        template = '''
<c-select
    name="color"
    defaultValue="blue"
    :options="['red', 'green', 'blue']"
/>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        options = soup.find_all('option')
        blue_option = [o for o in options if o.get('value') == 'blue'][0]
        assert blue_option.has_attr('selected')

    def test_value_overrides_default_value(self, env):
        """Test that value takes precedence over defaultValue."""
        template = '''
<c-select
    name="color"
    value="green"
    defaultValue="blue"
    :options="['red', 'green', 'blue']"
/>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        options = soup.find_all('option')

        # Green should be selected (value takes precedence)
        green_option = [o for o in options if o.get('value') == 'green'][0]
        assert green_option.has_attr('selected')

        # Blue should not be selected
        blue_option = [o for o in options if o.get('value') == 'blue'][0]
        assert not blue_option.has_attr('selected')


class TestSelectPlaceholder:
    """Test select placeholder functionality."""

    def test_placeholder_option(self, env):
        """Test placeholder renders as first disabled option."""
        template = '''
<c-select
    name="color"
    placeholder="Choose a color"
    :options="['red', 'green', 'blue']"
/>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        options = soup.find_all('option')
        # First option should be placeholder
        assert len(options) == 4  # 3 options + placeholder

        placeholder = options[0]
        assert placeholder.get('value') == ''
        assert placeholder.has_attr('disabled')
        assert placeholder.get_text(strip=True) == 'Choose a color'

    def test_placeholder_selected_when_no_value(self, env):
        """Test placeholder is selected when no value is set."""
        template = '''
<c-select
    name="color"
    placeholder="Select..."
    :options="['red', 'green', 'blue']"
/>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        options = soup.find_all('option')
        placeholder = options[0]
        assert placeholder.has_attr('selected')

    def test_placeholder_not_selected_when_value_set(self, env):
        """Test placeholder is not selected when value is set."""
        template = '''
<c-select
    name="color"
    placeholder="Select..."
    value="red"
    :options="['red', 'green', 'blue']"
/>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        options = soup.find_all('option')
        placeholder = options[0]
        assert not placeholder.has_attr('selected')

        # Red should be selected instead
        red_option = [o for o in options if o.get('value') == 'red'][0]
        assert red_option.has_attr('selected')


class TestSelectDataAttributes:
    """Test data attributes on select element."""

    def test_data_default_value(self, env):
        """Test data-default-value attribute."""
        template = '''
<c-select
    name="test"
    defaultValue="test-value"
    :options="[]"
/>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        assert select.get('data-default-value') == 'test-value'

    def test_data_value(self, env):
        """Test data-value attribute."""
        template = '''
<c-select
    name="test"
    value="current-value"
    :options="[]"
/>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        assert select.get('data-value') == 'current-value'

    def test_component_data_attribute(self, env):
        """Test component wrapper has data-roos-component attribute."""
        template = '<c-select name="test" :options="[]" />'
        result = env.from_string(template).render()
        soup = parse_html(result)

        wrapper = soup.find('div', {'data-roos-component': 'select'})
        assert wrapper is not None


class TestSelectEvents:
    """Test event handlers on select element."""

    def test_onchange_event(self, env):
        """Test @change event handler."""
        template = '''
<c-select
    name="test"
    :options="['a', 'b', 'c']"
    @change="handleChange()"
/>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        assert select.get('onchange') == 'handleChange()'

    def test_onchange_with_parameters(self, env):
        """Test @change event with parameters."""
        template = '''
<c-select
    name="status"
    :options="['active', 'inactive']"
    @change="updateStatus('user-123', this.value)"
/>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        assert "updateStatus('user-123', this.value)" in select.get('onchange', '')


class TestSelectCSSClasses:
    """Test CSS class generation."""

    def test_base_classes(self, env):
        """Test base CSS classes are applied."""
        template = '<c-select name="test" :options="[]" />'
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        classes = select.get('class', [])
        assert 'utrecht-select' in classes
        assert 'utrecht-select--html-select' in classes

    def test_multiple_state_classes(self, env):
        """Test multiple state classes can be applied together."""
        template = '''
<c-select
    name="test"
    :disabled="true"
    :required="true"
    :invalid="true"
    :options="[]"
/>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        classes = select.get('class', [])
        assert 'utrecht-select--disabled' in classes
        assert 'utrecht-select--required' in classes
        assert 'utrecht-select--invalid' in classes


class TestSelectWrapper:
    """Test select wrapper element."""

    def test_wrapper_element(self, env):
        """Test select is wrapped in a div with proper class."""
        template = '<c-select name="test" :options="[]" />'
        result = env.from_string(template).render()
        soup = parse_html(result)

        wrapper = soup.find('div', class_='rvo-select-wrapper')
        assert wrapper is not None

        select = wrapper.find('select')
        assert select is not None
        assert select.get('name') == 'test'


class TestSelectContentBlock:
    """Test select with content block (option elements)."""

    def test_simple_option_elements(self, env):
        """Test select with simple option elements in content."""
        template = '''
<c-select name="status">
    <option value="active">Active</option>
    <option value="inactive">Inactive</option>
    <option value="pending">Pending</option>
</c-select>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        assert select is not None
        assert select.get('name') == 'status'

        options = select.find_all('option')
        assert len(options) == 3

        assert options[0].get('value') == 'active'
        assert options[0].get_text(strip=True) == 'Active'

        assert options[1].get('value') == 'inactive'
        assert options[1].get_text(strip=True) == 'Inactive'

        assert options[2].get('value') == 'pending'
        assert options[2].get_text(strip=True) == 'Pending'

    def test_option_elements_with_selected(self, env):
        """Test content option elements with selected attribute."""
        template = '''
<c-select name="color">
    <option value="red">Red</option>
    <option value="green" selected>Green</option>
    <option value="blue">Blue</option>
</c-select>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        options = soup.find_all('option')

        # Green should have selected attribute from content
        green_option = [o for o in options if o.get('value') == 'green'][0]
        assert green_option.has_attr('selected')

    def test_option_elements_with_disabled(self, env):
        """Test content option elements with disabled attribute."""
        template = '''
<c-select name="size">
    <option value="xs">Extra Small</option>
    <option value="sm" disabled>Small (Out of Stock)</option>
    <option value="md">Medium</option>
</c-select>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        options = soup.find_all('option')

        # Small option should be disabled
        sm_option = [o for o in options if o.get('value') == 'sm'][0]
        assert sm_option.has_attr('disabled')

    def test_optgroup_elements(self, env):
        """Test select with optgroup elements in content."""
        template = '''
<c-select name="food">
    <optgroup label="Fruits">
        <option value="apple">Apple</option>
        <option value="banana">Banana</option>
    </optgroup>
    <optgroup label="Vegetables">
        <option value="carrot">Carrot</option>
        <option value="potato">Potato</option>
    </optgroup>
</c-select>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        assert select is not None

        optgroups = select.find_all('optgroup')
        assert len(optgroups) == 2

        assert optgroups[0].get('label') == 'Fruits'
        assert optgroups[1].get('label') == 'Vegetables'

        fruits = optgroups[0].find_all('option')
        assert len(fruits) == 2
        assert fruits[0].get('value') == 'apple'
        assert fruits[1].get('value') == 'banana'

        vegetables = optgroups[1].find_all('option')
        assert len(vegetables) == 2
        assert vegetables[0].get('value') == 'carrot'
        assert vegetables[1].get('value') == 'potato'

    def test_content_with_jinja_variables(self, env):
        """Test content block with Jinja variables."""
        template = '''
{% set statuses = [
    {'value': 'draft', 'label': 'Draft'},
    {'value': 'published', 'label': 'Published'},
    {'value': 'archived', 'label': 'Archived'}
] %}
<c-select name="status">
    {% for status in statuses %}
    <option value="{{ status.value }}">{{ status.label }}</option>
    {% endfor %}
</c-select>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        options = select.find_all('option')

        assert len(options) == 3
        assert options[0].get('value') == 'draft'
        assert options[0].get_text(strip=True) == 'Draft'
        assert options[1].get('value') == 'published'
        assert options[1].get_text(strip=True) == 'Published'
        assert options[2].get('value') == 'archived'
        assert options[2].get_text(strip=True) == 'Archived'

    def test_options_attribute_takes_precedence_over_content(self, env):
        """Test that options attribute takes precedence over content block."""
        template = '''
<c-select name="test" :options="['option1', 'option2']">
    <option value="ignored1">This should be ignored</option>
    <option value="ignored2">This should also be ignored</option>
</c-select>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        options = select.find_all('option')

        # Should only have 2 options from the options attribute
        assert len(options) == 2
        assert options[0].get('value') == 'option1'
        assert options[1].get('value') == 'option2'

        # Should not have the ignored options
        ignored_values = [o.get('value') for o in options]
        assert 'ignored1' not in ignored_values
        assert 'ignored2' not in ignored_values

    def test_content_with_placeholder(self, env):
        """Test content block combined with placeholder."""
        template = '''
<c-select name="country" placeholder="Select a country">
    <option value="nl">Netherlands</option>
    <option value="be">Belgium</option>
    <option value="de">Germany</option>
</c-select>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        options = select.find_all('option')

        # Should have 4 options: 1 placeholder + 3 content options
        assert len(options) == 4

        # First option should be placeholder
        placeholder = options[0]
        assert placeholder.get('value') == ''
        assert placeholder.has_attr('disabled')
        assert placeholder.get_text(strip=True) == 'Select a country'

        # Other options should be from content
        assert options[1].get('value') == 'nl'
        assert options[2].get('value') == 'be'
        assert options[3].get('value') == 'de'

    def test_empty_content_block(self, env):
        """Test select with empty content block."""
        template = '''
<c-select name="empty">
</c-select>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        select = soup.find('select')
        assert select is not None

        options = select.find_all('option')
        # Should have no options
        assert len(options) == 0

    def test_content_preserves_html_attributes(self, env):
        """Test that content preserves all HTML attributes on option elements."""
        template = '''
<c-select name="test">
    <option value="1" data-color="red" class="special">Option 1</option>
    <option value="2" data-color="blue">Option 2</option>
</c-select>
'''
        result = env.from_string(template).render()
        soup = parse_html(result)

        options = soup.find_all('option')

        # First option should preserve data and class attributes
        assert options[0].get('data-color') == 'red'
        assert 'special' in options[0].get('class', [])

        # Second option should preserve data attribute
        assert options[1].get('data-color') == 'blue'
