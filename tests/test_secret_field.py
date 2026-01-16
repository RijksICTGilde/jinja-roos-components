#!/usr/bin/env python3
"""
Tests for the secret-field component.
Tests the secret display functionality with show/hide toggle and copy functionality.
"""

import pytest
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from jinja_roos_components import setup_components


@pytest.fixture
def env():
    """Create a Jinja2 environment with the roos components extension."""
    environment = Environment(loader=FileSystemLoader([]))
    return setup_components(environment, strict_validation=True)


def parse_html(html):
    """Parse HTML string into BeautifulSoup object."""
    return BeautifulSoup(html, "html.parser")


class TestSecretFieldBasicRendering:
    """Test basic secret-field rendering."""

    def test_renders_without_errors(self, env):
        """Test secret-field component renders without errors."""
        template_str = '<c-secret-field value="my-secret" />'
        template = env.from_string(template_str)
        result = template.render()
        assert result is not None
        assert len(result) > 0

    def test_renders_with_component_attribute(self, env):
        """Test secret-field has data-roos-component attribute."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        secret_field = soup.find("div", {"data-roos-component": "secret-field"})
        assert secret_field is not None

    def test_has_base_css_class(self, env):
        """Test secret-field has base CSS class."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        secret_field = soup.find("div", class_="roos-secret-field")
        assert secret_field is not None


class TestSecretFieldStructure:
    """Test secret-field HTML structure."""

    def test_has_content_area(self, env):
        """Test secret-field has content area."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        content = soup.find("div", class_="roos-secret-field__content")
        assert content is not None

    def test_has_mask_element(self, env):
        """Test secret-field has mask element."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        mask = soup.find("span", class_="roos-secret-field__mask")
        assert mask is not None
        # Default mask length is 20 dots
        assert "•" in mask.get_text()

    def test_has_value_element(self, env):
        """Test secret-field has value element."""
        template_str = '<c-secret-field value="my-secret-value" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        value = soup.find("span", class_="roos-secret-field__value")
        assert value is not None
        assert "my-secret-value" in value.get_text()

    def test_has_actions_area(self, env):
        """Test secret-field has actions area."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        actions = soup.find("span", class_="roos-secret-field__actions")
        assert actions is not None


class TestSecretFieldButtons:
    """Test secret-field buttons."""

    def test_has_show_button(self, env):
        """Test secret-field has show button."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        show_btn = soup.find(class_="roos-secret-field__show-btn")
        assert show_btn is not None

    def test_has_hide_button(self, env):
        """Test secret-field has hide button."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        hide_btn = soup.find(class_="roos-secret-field__hide-btn")
        assert hide_btn is not None

    def test_has_copy_button_by_default(self, env):
        """Test secret-field has copy button by default."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        copy_btn = soup.find(class_="roos-secret-field__copy-btn")
        assert copy_btn is not None

    def test_copy_button_hidden_when_showCopy_false(self, env):
        """Test copy button is not rendered when showCopy is false."""
        template_str = '<c-secret-field value="my-secret" :showCopy="false" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        copy_btn = soup.find(class_="roos-secret-field__copy-btn")
        assert copy_btn is None

    def test_show_button_has_onclick(self, env):
        """Test show button has onclick handler with applyRules."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        show_btn = soup.find(class_="roos-secret-field__show-btn")
        button = show_btn.find("button") if show_btn.name != "button" else show_btn
        if button is None:
            button = show_btn
        onclick = button.get("onclick", "") if button else ""
        # Check the applyRules call is present
        assert "applyRules" in onclick or "applyRules" in str(show_btn)

    def test_hide_button_has_onclick(self, env):
        """Test hide button has onclick handler with applyRules."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        hide_btn = soup.find(class_="roos-secret-field__hide-btn")
        # Check the applyRules call is present
        assert "applyRules" in str(hide_btn)

    def test_copy_button_has_onclick(self, env):
        """Test copy button has onclick handler with copyToClipboard."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        copy_btn = soup.find(class_="roos-secret-field__copy-btn")
        # Check the copyToClipboard call is present
        assert "copyToClipboard" in str(copy_btn)


class TestSecretFieldMaskLength:
    """Test secret-field mask length configuration."""

    def test_default_mask_length(self, env):
        """Test default mask length is 20."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        mask = soup.find("span", class_="roos-secret-field__mask")
        dots = mask.get_text().count("•")
        assert dots == 20

    def test_custom_mask_length(self, env):
        """Test custom mask length."""
        template_str = '<c-secret-field value="my-secret" :maskLength="10" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        mask = soup.find("span", class_="roos-secret-field__mask")
        dots = mask.get_text().count("•")
        assert dots == 10


class TestSecretFieldLabels:
    """Test secret-field button labels."""

    def test_default_show_label(self, env):
        """Test default show label is 'Tonen'."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        show_btn = soup.find(class_="roos-secret-field__show-btn")
        assert "Tonen" in str(show_btn)

    def test_default_hide_label(self, env):
        """Test default hide label is 'Verbergen'."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        hide_btn = soup.find(class_="roos-secret-field__hide-btn")
        assert "Verbergen" in str(hide_btn)

    def test_default_copy_label(self, env):
        """Test default copy label is 'Kopieren'."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        copy_label = soup.find(class_="roos-secret-field__copy-label")
        assert copy_label is not None
        assert "Kopieren" in copy_label.get_text()

    def test_default_copied_label(self, env):
        """Test default copied label is 'Gekopieerd!'."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        copied_label = soup.find(class_="roos-secret-field__copied-label")
        assert copied_label is not None
        assert "Gekopieerd!" in copied_label.get_text()

    def test_custom_show_label(self, env):
        """Test custom show label."""
        template_str = '<c-secret-field value="my-secret" showLabel="Show" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        show_btn = soup.find(class_="roos-secret-field__show-btn")
        assert "Show" in str(show_btn)

    def test_custom_hide_label(self, env):
        """Test custom hide label."""
        template_str = '<c-secret-field value="my-secret" hideLabel="Hide" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        hide_btn = soup.find(class_="roos-secret-field__hide-btn")
        assert "Hide" in str(hide_btn)

    def test_custom_copy_label(self, env):
        """Test custom copy label."""
        template_str = '<c-secret-field value="my-secret" copyLabel="Copy" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        copy_label = soup.find(class_="roos-secret-field__copy-label")
        assert "Copy" in copy_label.get_text()


class TestSecretFieldSize:
    """Test secret-field size variants."""

    def test_default_size_is_sm(self, env):
        """Test default size is sm."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        secret_field = soup.find("div", class_="roos-secret-field")
        classes = secret_field.get("class", [])
        assert "roos-secret-field--sm" in classes

    def test_size_md(self, env):
        """Test size md variant."""
        template_str = '<c-secret-field value="my-secret" size="md" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        secret_field = soup.find("div", class_="roos-secret-field")
        classes = secret_field.get("class", [])
        assert "roos-secret-field--md" in classes

    def test_size_lg(self, env):
        """Test size lg variant."""
        template_str = '<c-secret-field value="my-secret" size="lg" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        secret_field = soup.find("div", class_="roos-secret-field")
        classes = secret_field.get("class", [])
        assert "roos-secret-field--lg" in classes


class TestSecretFieldContentWidth:
    """Test secret-field content width variants."""

    def test_default_content_width_is_lg(self, env):
        """Test default content width is lg."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        secret_field = soup.find("div", class_="roos-secret-field")
        classes = secret_field.get("class", [])
        assert "roos-secret-field--width-lg" in classes

    def test_content_width_xs(self, env):
        """Test content width xs variant."""
        template_str = '<c-secret-field value="my-secret" contentWidth="xs" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        secret_field = soup.find("div", class_="roos-secret-field")
        classes = secret_field.get("class", [])
        assert "roos-secret-field--width-xs" in classes

    def test_content_width_sm(self, env):
        """Test content width sm variant."""
        template_str = '<c-secret-field value="my-secret" contentWidth="sm" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        secret_field = soup.find("div", class_="roos-secret-field")
        classes = secret_field.get("class", [])
        assert "roos-secret-field--width-sm" in classes

    def test_content_width_lg(self, env):
        """Test content width lg variant."""
        template_str = '<c-secret-field value="my-secret" contentWidth="lg" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        secret_field = soup.find("div", class_="roos-secret-field")
        classes = secret_field.get("class", [])
        assert "roos-secret-field--width-lg" in classes

    def test_content_width_xl(self, env):
        """Test content width xl variant."""
        template_str = '<c-secret-field value="my-secret" contentWidth="xl" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        secret_field = soup.find("div", class_="roos-secret-field")
        classes = secret_field.get("class", [])
        assert "roos-secret-field--width-xl" in classes

    def test_content_width_auto(self, env):
        """Test content width auto variant."""
        template_str = '<c-secret-field value="my-secret" contentWidth="auto" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        secret_field = soup.find("div", class_="roos-secret-field")
        classes = secret_field.get("class", [])
        assert "roos-secret-field--width-auto" in classes


class TestSecretFieldValueType:
    """Test secret-field value type variants."""

    def test_default_value_type_is_text(self, env):
        """Test default value type is text (no pre/code)."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        value = soup.find("span", class_="roos-secret-field__value")
        code = value.find("pre", class_="roos-secret-field__code")
        assert code is None

    def test_value_type_json(self, env):
        """Test value type json renders in pre/code block."""
        template_str = '<c-secret-field value=\'{"key": "value"}\' valueType="json" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        value = soup.find("span", class_="roos-secret-field__value")
        code = value.find("pre", class_="roos-secret-field__code")
        assert code is not None
        assert '{"key": "value"}' in code.get_text()


class TestSecretFieldCustomClass:
    """Test secret-field custom CSS classes."""

    def test_custom_class_attribute(self, env):
        """Test custom class attribute is applied."""
        template_str = '<c-secret-field value="my-secret" class="my-custom-class" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        secret_field = soup.find("div", class_="roos-secret-field")
        classes = secret_field.get("class", [])
        assert "my-custom-class" in classes

    def test_className_attribute(self, env):
        """Test className attribute is applied."""
        template_str = '<c-secret-field value="my-secret" className="another-class" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        secret_field = soup.find("div", class_="roos-secret-field")
        classes = secret_field.get("class", [])
        assert "another-class" in classes


class TestSecretFieldFieldId:
    """Test secret-field fieldId attribute."""

    def test_custom_field_id(self, env):
        """Test custom field ID is applied."""
        template_str = '<c-secret-field value="my-secret" fieldId="custom-id" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        secret_field = soup.find("div", class_="roos-secret-field")
        field_id = secret_field.get("data-field-id")
        assert field_id == "custom-id"

    def test_auto_generated_field_id(self, env):
        """Test auto-generated field ID when not provided."""
        template_str = '<c-secret-field value="my-secret" />'
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        secret_field = soup.find("div", class_="roos-secret-field")
        field_id = secret_field.get("data-field-id")
        assert field_id is not None
        assert field_id.startswith("secret-")


class TestSecretFieldWithContext:
    """Test secret-field with template context variables."""

    def test_value_from_context(self, env):
        """Test value passed from render context using Jinja syntax."""
        template_str = '<c-secret-field value="{{ secret_value }}" />'
        result = env.from_string(template_str).render(secret_value="context-secret")
        soup = parse_html(result)

        value = soup.find("span", class_="roos-secret-field__value")
        assert "context-secret" in value.get_text()

    def test_jinja_variable_in_value(self, env):
        """Test Jinja variable syntax in value."""
        template_str = """
{% set my_secret = 'variable-secret' %}
<c-secret-field value="{{ my_secret }}" />
"""
        result = env.from_string(template_str).render()
        soup = parse_html(result)

        value = soup.find("span", class_="roos-secret-field__value")
        assert "variable-secret" in value.get_text()
