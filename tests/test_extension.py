import pytest

from jinja2 import Environment, FileSystemLoader
from jinja_roos_components.extension import ComponentExtension, setup_components


@pytest.fixture
def env():
    """Set up Jinja environment with ROOS components."""
    environment = Environment(loader=FileSystemLoader([]))
    setup_components(environment, strict_validation=True)
    return environment

def test_extension_jinja(env):
    """Test complex Jinja expressions with the actual extension."""

    # Create test template string
    template_str = '''
{% set service_def = {"icon": "calendar", "color": "blue"} %}
<c-icon icon="{{ service_def.icon }}" size="xl" color="{{ service_def.color }}" />
    '''

    # Render from string
    template = env.from_string(template_str)
    result = template.render()

    # Assertions
    assert result is not None, "Template should render"
    assert len(result) > 0, "Rendered output should not be empty"
    assert 'calendar' in result, "Jinja expression for icon should be evaluated"
    assert 'blue' in result, "Jinja expression for color should be evaluated"


def test_preprocessing_directly():
    """Test the preprocessing step directly."""

    # Create a minimal environment
    env = Environment()
    extension = ComponentExtension(env)

    # Test source
    source = '''{% set service_def = {"icon": "calendar", "color": "blue"} %}
<c-icon icon="{{ service_def.icon }}" size="xl" color="{{ service_def.color }}" />'''

    # Preprocess
    result = extension.preprocess(source, "test", None)

    # Assertions
    assert result is not None, "Preprocessing should return a result"
    assert 'service_def.icon' in result or 'service_def["icon"]' in result, \
        "Preprocessing should extract Jinja expressions from attributes"
    assert 'service_def.color' in result or 'service_def["color"]' in result, \
        "Preprocessing should extract Jinja expressions from attributes"
    assert '"{{ service_def.icon }}"' not in result, \
        "Preprocessing should not treat Jinja expressions as quoted strings"
    
def test_shorthand_boolean_notation(env):
    """Shorthand boolean notation is supported on boolean attributes"""

    # Create test template string
    template_str = '''
<c-button disabled label="my button" />
    '''

    # Should successfully parse shorthand boolean notation
    try:
        template = env.from_string(template_str)
        result = template.render()
    except Exception:
        assert False, 'should not error'

    assert "disabled" in result

def test_shorthand_boolean_notation_on_non_boolean_attr(env):
    """Shorthand notation is not supported on non-boolean attributes"""

    # Create test template string
    template_str = '''
<c-button label />
    '''

    # Should raise validation error for shorthand notation on string attribute
    with pytest.raises(RuntimeError) as exc_info:
        env.from_string(template_str)

    # Check error message mentions shorthand notation and provides type hint
    assert 'Shorthand notation is not supported' in str(exc_info.value)
    assert 'label' in str(exc_info.value)
    assert 'string value' in str(exc_info.value)

def test_attributes_passthrough(env):
    """data-* and aria-* attributes should passthrough"""

    # Create test template string with both data and aria attributes
    template_str = '''
<c-button label="Menu" data-component="nav-button" aria-expanded="false" data-boolean-attr/>
    '''

    # Should successfully parse and render with both attribute types
    template = env.from_string(template_str)
    result = template.render()

    # Verify both attribute types are in the output
    assert "data-component" in result
    assert "nav-button" in result
    assert "aria-expanded" in result
    assert "false" in result
    assert "data-boolean-attr" in result

def test_attributes_passthrough_select(env):
    """data-* and aria-* attributes should passthrough"""

    # Create test template string with both data and aria attributes
    template_str = '''
<c-select data-component="nav-button" aria-expanded="false" data-boolean-attr/>
    '''

    # Should successfully parse and render with both attribute types
    template = env.from_string(template_str)
    result = template.render()

    # Verify both attribute types are in the output
    assert "data-component" in result
    assert "nav-button" in result
    assert "aria-expanded" in result
    assert "false" in result
    assert "data-boolean-attr" in result


def test_text_input_field_passthrough_to_input(env):
    """Attributes on c-text-input-field should pass to the <input> element, not the wrapper"""

    template_str = '''
<c-text-input-field
    id="email"
    label="Email"
    data-testid="email-input"
    data-validate="email"
    @input="validate()"/>
    '''

    template = env.from_string(template_str)
    result = template.render()

    # Verify attributes are in the output
    assert "data-testid" in result
    assert "email-input" in result
    assert "data-validate" in result
    assert "oninput" in result  # @input converted to oninput
    assert "validate()" in result

    # Verify they're on the input element (look for pattern <input ... data-testid)
    # The input should have these attributes, not the wrapper div
    assert '<input' in result
    # Check that data-testid appears after <input and before />
    input_start = result.find('<input')
    input_end = result.find('/>', input_start)
    input_tag = result[input_start:input_end]
    assert 'data-testid="email-input"' in input_tag


def test_select_field_passthrough_to_select(env):
    """Attributes on c-select-field should pass to the <select> element, not the wrapper"""

    template_str = '''
<c-select-field
    id="country"
    label="Country"
    @change="updateRegions()"
    data-testid="country-selector"
    data-region="true">
    <option value="nl">Netherlands</option>
</c-select-field>
    '''

    template = env.from_string(template_str)
    result = template.render()

    # Verify attributes are in the output
    assert "data-testid" in result
    assert "country-selector" in result
    assert "data-region" in result
    assert "onchange" in result  # @change converted to onchange
    assert "updateRegions()" in result

    # Verify they're on the select element
    assert '<select' in result
    select_start = result.find('<select')
    select_end = result.find('>', select_start)
    select_tag = result[select_start:select_end]
    assert 'data-testid="country-selector"' in select_tag


def test_date_input_field_passthrough_to_input(env):
    """Attributes on c-date-input-field should pass to the <input> element, not the wrapper"""

    template_str = '''
<c-date-input-field
    id="birthdate"
    label="Birthdate"
    data-testid="birthdate-input"
    @blur="validateAge()"/>
    '''

    template = env.from_string(template_str)
    result = template.render()

    # Verify attributes are in the output
    assert "data-testid" in result
    assert "birthdate-input" in result
    assert "onblur" in result  # @blur converted to onblur
    assert "validateAge()" in result

    # Verify they're on the input element
    assert '<input' in result
    input_start = result.find('<input')
    input_end = result.find('/>', input_start)
    input_tag = result[input_start:input_end]
    assert 'data-testid="birthdate-input"' in input_tag


def test_file_input_field_passthrough_to_input(env):
    """Attributes on c-file-input-field should pass to the <input> element, not the wrapper"""

    template_str = '''
<c-file-input-field
    id="upload"
    label="Upload File"
    data-testid="file-upload"
    @change="handleFileSelect()"/>
    '''

    template = env.from_string(template_str)
    result = template.render()

    # Verify attributes are in the output
    assert "data-testid" in result
    assert "file-upload" in result
    assert "onchange" in result  # @change converted to onchange
    assert "handleFileSelect()" in result

    # Verify they're on the input element
    assert '<input' in result
    input_start = result.find('<input')
    input_end = result.find('>', input_start)
    input_tag = result[input_start:input_end]
    assert 'data-testid="file-upload"' in input_tag


def test_textarea_field_passthrough_to_textarea(env):
    """Attributes on c-textarea-field should pass to the <textarea> element, not the wrapper"""

    template_str = '''
<c-textarea-field
    id="notes"
    label="Notes"
    data-testid="notes-textarea"
    @input="autoSave()"/>
    '''

    template = env.from_string(template_str)
    result = template.render()

    # Verify attributes are in the output
    assert "data-testid" in result
    assert "notes-textarea" in result
    assert "oninput" in result  # @input converted to oninput
    assert "autoSave()" in result

    # Verify they're on the textarea element
    assert '<textarea' in result
    textarea_start = result.find('<textarea')
    textarea_end = result.find('>', textarea_start)
    textarea_tag = result[textarea_start:textarea_end]
    assert 'data-testid="notes-textarea"' in textarea_tag


def test_checkbox_field_passthrough_to_wrapper(env):
    """Attributes on c-checkbox-field (multi-input) should pass to the wrapper, not individual inputs"""

    template_str = '''
<c-checkbox-field
    id="preferences"
    label="Preferences"
    data-testid="prefs-group"
    @change="savePreferences()"
    options='[{"id": "opt1", "label": "Option 1", "value": "1"}]'/>
    '''

    template = env.from_string(template_str)
    result = template.render()

    # Verify attributes are in the output
    assert "data-testid" in result
    assert "prefs-group" in result
    assert "onchange" in result  # @change converted to onchange
    assert "savePreferences()" in result

    # Verify they're on the wrapper div with role="group"
    assert 'role="group"' in result
    # Find the div with role="group" and verify it has the data attributes
    group_start = result.find('role="group"')
    # Search backwards to find the opening <div
    div_start = result.rfind('<div', 0, group_start)
    # Search forward to find the closing >
    div_end = result.find('>', group_start)
    div_tag = result[div_start:div_end]
    assert 'data-testid="prefs-group"' in div_tag


def test_radio_button_field_passthrough_to_wrapper(env):
    """Attributes on c-radio-button-field (multi-input) should pass to the wrapper, not individual inputs"""

    template_str = '''
<c-radio-button-field
    id="choice"
    label="Choice"
    data-testid="choice-group"
    options='[{"id": "opt1", "label": "Option 1", "value": "1"}]'/>
    '''

    template = env.from_string(template_str)
    result = template.render()

    # Verify attributes are in the output
    assert "data-testid" in result
    assert "choice-group" in result

    # Verify they're on the wrapper div with role="group"
    assert 'role="group"' in result
    group_start = result.find('role="group"')
    div_start = result.rfind('<div', 0, group_start)
    div_end = result.find('>', group_start)
    div_tag = result[div_start:div_end]
    assert 'data-testid="choice-group"' in div_tag
