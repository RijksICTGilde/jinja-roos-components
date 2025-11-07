import pytest

from jinja2 import Environment, FileSystemLoader
from jinja_roos_components.extension import setup_components


@pytest.fixture
def env():
    """Set up Jinja environment with ROOS components."""
    environment = Environment(loader=FileSystemLoader([]))
    setup_components(environment, strict_validation=True)
    return environment


def test_action_group(env):
    """Test action-group component renders without errors."""
    template_str = '<c-action-group />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_alert(env):
    """Test alert component renders without errors."""
    template_str = '<c-alert />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_b(env):
    """Test b component renders without errors."""
    template_str = '<c-b />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_button(env):
    """Test button component renders without errors."""
    template_str = '<c-button label="Test" />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_card(env):
    """Test card component renders without errors."""
    template_str = '<c-card />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_checkbox_field(env):
    """Test checkbox-field component renders without errors."""
    template_str = '<c-checkbox-field label="Test" />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_checkbox(env):
    """Test checkbox component renders without errors."""
    template_str = '<c-checkbox />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_data_list(env):
    """Test data-list component renders without errors."""
    template_str = '<c-data-list />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_date_input_field(env):
    """Test date-input-field component renders without errors."""
    template_str = '<c-date-input-field label="Test" />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_div(env):
    """Test div component renders without errors."""
    template_str = '<c-div />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_em(env):
    """Test em component renders without errors."""
    template_str = '<c-em />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_fieldset(env):
    """Test fieldset component renders without errors."""
    template_str = '<c-fieldset />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_file_input_field(env):
    """Test file-input-field component renders without errors."""
    template_str = '<c-file-input-field label="Test" />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_footer(env):
    """Test footer component renders without errors."""
    template_str = '<c-footer />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0

# TODO: this gets stuck and hangs!
# def test_form_field_select_no_args(env):
#     """Test form-field-select component renders without errors."""
#     template_str = '<c-form-field-select />'
#     template = env.from_string(template_str)
#     result = template.render()
#     assert result is not None
#     assert len(result) > 0


# TODO: fix this test
# def test_form_field_select(env):
#     """Test form-field-select component renders without errors."""
#     template_str = '<c-form-field-select name="brand"/>'
#     template = env.from_string(template_str)
#     result = template.render()
#     assert result is not None
#     assert len(result) > 0


# TODO: fix this test
# def test_form_field(env):
#     """Test form-field component renders without errors."""
#     template_str = '<c-form-field label="Test" />'
#     template = env.from_string(template_str)
#     result = template.render()
#     assert result is not None
#     assert len(result) > 0


def test_form_fieldset(env):
    """Test form-fieldset component renders without errors."""
    template_str = '<c-form-fieldset />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_form_select(env):
    """Test form-select component renders without errors."""
    template_str = '<c-form-select />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_grid(env):
    """Test grid component renders without errors."""
    template_str = '<c-grid />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_header(env):
    """Test header component renders without errors."""
    template_str = '<c-header />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_heading(env):
    """Test heading component renders without errors."""
    template_str = '<c-heading />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_hero(env):
    """Test hero component renders without errors."""
    template_str = '<c-hero />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_horizontal_rule(env):
    """Test horizontal-rule component renders without errors."""
    template_str = '<c-horizontal-rule />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_i(env):
    """Test i component renders without errors."""
    template_str = '<c-i />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_icon(env):
    """Test icon component renders without errors."""
    template_str = '<c-icon icon="home" />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_input(env):
    """Test input component renders without errors."""
    template_str = '<c-input />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


# TODO: fix this test
# def test_label(env):
#     """Test label component renders without errors."""
#     template_str = '<c-label />'
#     template = env.from_string(template_str)
#     result = template.render()
#     assert result is not None
#     assert len(result) > 0


def test_layout_column(env):
    """Test layout-column component renders without errors."""
    template_str = '<c-layout-column />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_layout_flow(env):
    """Test layout-flow component renders without errors."""
    template_str = '<c-layout-flow />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


# TODO: fix this test
# def test_layout_grid(env):
#     """Test layout-grid component renders without errors."""
#     template_str = '<c-layout-grid />'
#     template = env.from_string(template_str)
#     result = template.render()
#     assert result is not None
#     assert len(result) > 0


def test_layout_row(env):
    """Test layout-row component renders without errors."""
    template_str = '<c-layout-row />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_li(env):
    """Test li component renders without errors."""
    template_str = '<c-li />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_link(env):
    """Test link component renders without errors."""
    template_str = '<c-link />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_list_item(env):
    """Test list-item component renders without errors."""
    template_str = '<c-list-item />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_list(env):
    """Test list component renders without errors."""
    template_str = '<c-list />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_max_width_layout(env):
    """Test max-width-layout component renders without errors."""
    template_str = '<c-max-width-layout />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_menubar(env):
    """Test menubar component renders without errors."""
    template_str = '<c-menubar />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_ol(env):
    """Test ol component renders without errors."""
    template_str = '<c-ol />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_ordered_unordered_list(env):
    """Test ordered-unordered-list component renders without errors."""
    template_str = '<c-ordered-unordered-list />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_page(env):
    """Test page component renders without errors."""
    template_str = '<c-page />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_paragraph(env):
    """Test paragraph component renders without errors."""
    template_str = '<c-paragraph />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


# TODO: fix this test
# def test_progress_tracker_step(env):
#     """Test progress-tracker-step component renders without errors."""
#     template_str = '<c-progress-tracker-step />'
#     template = env.from_string(template_str)
#     result = template.render()
#     assert result is not None
#     assert len(result) > 0


def test_progress_tracker(env):
    """Test progress-tracker component renders without errors."""
    template_str = '<c-progress-tracker />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_radio_button_field(env):
    """Test radio-button-field component renders without errors."""
    template_str = '<c-radio-button-field label="Test" />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_radio(env):
    """Test radio component renders without errors."""
    template_str = '<c-radio label="my radio"/>'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_select_field(env):
    """Test select-field component renders without errors."""
    template_str = '<c-select-field label="Test" />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_select(env):
    """Test select component renders without errors."""
    template_str = '<c-select />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_small(env):
    """Test small component renders without errors."""
    template_str = '<c-small />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_span(env):
    """Test span component renders without errors."""
    template_str = '<c-span />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_status_icon(env):
    """Test status-icon component renders without errors."""
    template_str = '<c-status-icon type="info" size="md" />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_strong(env):
    """Test strong component renders without errors."""
    template_str = '<c-strong />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_tabs(env):
    """Test tabs component renders without errors."""
    template_str = '<c-tabs />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_tag(env):
    """Test tag component renders without errors."""
    template_str = '<c-tag content="my content" />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_text_input_field(env):
    """Test text-input-field component renders without errors."""
    template_str = '<c-text-input-field label="Test" />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_textarea_field(env):
    """Test textarea-field component renders without errors."""
    template_str = '<c-textarea-field label="Test" />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_textarea(env):
    """Test textarea component renders without errors."""
    template_str = '<c-textarea />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0


def test_ul(env):
    """Test ul component renders without errors."""
    template_str = '<c-ul />'
    template = env.from_string(template_str)
    result = template.render()
    assert result is not None
    assert len(result) > 0
