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
