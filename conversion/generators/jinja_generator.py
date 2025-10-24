"""Generate Jinja templates from parsed React components."""

from typing import List, Dict, Any, Optional
from ..parsers.interface_parser import AttributeInfo
from .class_builder import ClassBuilder


class JinjaGenerator:
    """Generator for Jinja2 templates."""

    def __init__(self, component_name: str):
        """Initialize generator.

        Args:
            component_name: Name of the component
        """
        self.component_name = component_name
        self.class_builder = ClassBuilder()
        self.variables: List[str] = []
        self.todo_comments: List[Dict[str, str]] = []

    def generate_template(
        self,
        attributes: List[AttributeInfo],
        default_args: Dict[str, Any],
        html_tag: str,
        base_classes: List[str],
        content: str = "",
        content_elements: List = None
    ) -> str:
        """Generate complete Jinja template.

        Args:
            attributes: List of component attributes
            default_args: Default values for attributes
            html_tag: HTML tag name
            base_classes: Base CSS classes
            content: Optional inner content (legacy)
            content_elements: List of ContentElement objects

        Returns:
            Generated Jinja template as string
        """
        lines = []

        # Add header comment
        lines.append(self._generate_header())

        # Generate variable declarations
        lines.append(self._generate_variables(attributes, default_args))

        # Generate CSS class building logic
        self.class_builder.add_base_classes(base_classes)
        lines.append(self.class_builder.generate_jinja_code())

        # Generate content from content_elements if provided
        if content_elements:
            content = self._generate_content_from_elements(content_elements, attributes)

        # Generate HTML element
        lines.append(self._generate_html_element(html_tag, attributes, content))

        return '\n'.join(lines)

    def _generate_header(self) -> str:
        """Generate header comment.

        Returns:
            Header comment
        """
        return f"""{{% import 'components/_event_mixin.j2' as events %}}
{'{#'} Auto-generated from React component: {self.component_name}
   Manual edits: wrap in MANUAL_START/MANUAL_END tags to preserve {'#}'}"""

    def _generate_variables(self, attributes: List[AttributeInfo], default_args: Dict[str, Any]) -> str:
        """Generate Jinja variable declarations.

        Args:
            attributes: List of attributes
            default_args: Default values

        Returns:
            Jinja variable declarations
        """
        lines = []

        for attr in attributes:
            # Skip function attributes
            if attr.is_function:
                continue

            # Get default value
            default = self._get_default_value(attr, default_args)

            # Generate variable declaration
            var_line = f"{{% set {attr.name} = _component_context.{attr.name}"

            if default is not None:
                # Format default value
                default_str = self._format_default_value(default, attr)
                var_line += f" | default({default_str})"

            var_line += " %}"

            lines.append(var_line)
            self.variables.append(attr.name)

        return '\n'.join(lines)

    def _get_default_value(self, attr: AttributeInfo, default_args: Dict[str, Any]) -> Any:
        """Get default value for an attribute.

        Args:
            attr: Attribute info
            default_args: Default arguments dict

        Returns:
            Default value or None
        """
        if attr.name in default_args:
            return default_args[attr.name]

        # Use type-based defaults
        if 'boolean' in attr.types:
            return False
        if 'number' in attr.types:
            return None  # Don't default numbers
        if 'enum' in attr.types and attr.enum_values:
            return attr.enum_values[0]

        return None

    def _format_default_value(self, value: Any, attr: AttributeInfo) -> str:
        """Format a default value for Jinja.

        Args:
            value: Default value
            attr: Attribute info

        Returns:
            Formatted value string
        """
        if value is None:
            return "none"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, str):
            return f"'{value}'"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, list):
            items = ', '.join(f"'{item}'" if isinstance(item, str) else str(item) for item in value)
            return f"[{items}]"

        return "none"

    def _generate_html_element(self, tag: str, attributes: List[AttributeInfo], content: str) -> str:
        """Generate HTML element with attributes.

        Args:
            tag: HTML tag name
            attributes: List of attributes
            content: Inner content

        Returns:
            HTML element string
        """
        lines = []

        # Opening tag
        attrs = [
            'class="{{ css_classes | join(\' \') }}"',
            f'data-roos-component="{self.component_name}"'
        ]

        # Add common HTML attributes
        for attr in attributes:
            if attr.name in ['id', 'type', 'disabled', 'required', 'readonly', 'placeholder']:
                attr_str = self._generate_html_attribute(attr)
                if attr_str:
                    attrs.append(attr_str)

        # Add event handlers via mixin
        attrs.append('{{ events.render_extra_attributes(_component_context) }}')

        # Build tag
        opening_tag = f"<{tag}"
        for attr in attrs:
            opening_tag += f"\n    {attr}"
        opening_tag += ">"

        lines.append(opening_tag)

        # Content
        if content:
            lines.append(f"    {content}")
        else:
            # Default content placeholder
            lines.append("    {# Content #}")

        # Closing tag
        lines.append(f"</{tag}>")

        return '\n'.join(lines)

    def _generate_html_attribute(self, attr: AttributeInfo) -> Optional[str]:
        """Generate HTML attribute string.

        Args:
            attr: Attribute info

        Returns:
            Attribute string or None
        """
        if 'boolean' in attr.types:
            # Boolean attributes
            return f"{{% if {attr.name} %}}{attr.name}{{% endif %}}"
        else:
            # Value attributes
            return f'{attr.name}="{{{{ {attr.name} }}}}"'

    def _generate_content_from_elements(self, content_elements: List, attributes: List[AttributeInfo]) -> str:
        """Generate Jinja content from content elements.

        Args:
            content_elements: List of ContentElement objects
            attributes: List of AttributeInfo

        Returns:
            Generated content string
        """
        parts = []

        for element in content_elements:
            if element.type == 'conditional':
                # Convert React conditional to Jinja
                jinja_condition = self._convert_condition_to_jinja(element.condition)
                content_part = self._generate_element_content(element, attributes)
                parts.append(f"{{% if {jinja_condition} %}}{content_part}{{% endif %}}")

            elif element.type == 'ternary':
                # Convert React ternary to Jinja inline if
                # children ? parseContentMarkup(children) : fields → {{ _component_context.content if _component_context.content else '...' }}
                condition = self._convert_condition_to_jinja(element.condition)
                if element.fallback_chain and len(element.fallback_chain) == 2:
                    true_val = element.fallback_chain[0].strip()
                    false_val = element.fallback_chain[1].strip()

                    # Convert condition variable (e.g., 'children' → '_component_context.content')
                    if condition == 'children':
                        condition = '_component_context.content'

                    # Convert true value (e.g., 'parseContentMarkup(children)' → '_component_context.content')
                    if 'parseContentMarkup(children)' in true_val:
                        true_val = '_component_context.content | safe'
                    elif true_val == 'children':
                        true_val = '_component_context.content | safe'

                    # Convert false value - if it's complex, add TODO
                    if 'fields' in false_val and '.map(' in false_val:
                        # Complex expression - need to handle separately
                        parts.append(f"{{{{ {condition} if {condition} else '' }}}}")
                        parts.append("{# TODO_CONVERSION: Handle fields.map rendering #}")
                    else:
                        parts.append(f"{{{{ {true_val} if {condition} else {false_val} }}}}")
                else:
                    # Fallback if parsing failed
                    parts.append("{# TODO_CONVERSION: Ternary expression not fully parsed #}")

            elif element.type == 'fallback':
                # Convert React fallback (||) to Jinja
                # children || label → {{ _component_context.content if _component_context.content else label }}
                if element.fallback_chain:
                    # Replace 'children' with '_component_context.content' in the fallback chain
                    converted_chain = []
                    for item in element.fallback_chain:
                        if item.strip() == 'children':
                            converted_chain.append('_component_context.content')
                        else:
                            converted_chain.append(item.strip())

                    # Build fallback expression
                    fallback_expr = converted_chain[0]
                    for fb in converted_chain[1:]:
                        fallback_expr = f"{fallback_expr} if {fallback_expr} else {fb}"
                    parts.append(f"{{{{ {fallback_expr} | safe }}}}")

            elif element.type == 'variable':
                # Simple variable reference
                parts.append(f"{{{{ {element.content} }}}}")

        return ''.join(parts)

    def _convert_condition_to_jinja(self, condition: str) -> str:
        """Convert React condition to Jinja condition.

        Args:
            condition: React condition like "showIcon === 'before'"

        Returns:
            Jinja condition like "showIcon == 'before'"
        """
        # Replace === with ==
        jinja_cond = condition.replace(' === ', ' == ')
        # Replace !== with !=
        jinja_cond = jinja_cond.replace(' !== ', ' != ')
        return jinja_cond

    def _generate_element_content(self, element, attributes: List[AttributeInfo]) -> str:
        """Generate content for a single element.

        Args:
            element: ContentElement object
            attributes: List of AttributeInfo

        Returns:
            Generated content string
        """
        # Check if it's a nested component
        if element.component_name:
            return self._inline_component(element, attributes)

        # Otherwise, just reference the variable
        return f"{{{{ {element.content} }}}}"

    def _inline_component(self, element, attributes: List[AttributeInfo]) -> str:
        """Inline a nested component.

        For Icon component, we inline it as a span element.
        For Utrecht components, we auto-detect and inline them.

        Args:
            element: ContentElement with component info
            attributes: List of AttributeInfo

        Returns:
            Inlined component HTML
        """
        if element.component_name == 'Icon':
            return self._inline_icon_component(element, attributes)

        # Try to auto-inline Utrecht components
        inlined = self._try_inline_utrecht_component(element, attributes)
        if inlined:
            return inlined

        # For other components, just add a TODO comment
        return f"{{{{# TODO_CONVERSION: Inline {element.component_name} component #}}}}"

    def _try_inline_utrecht_component(self, element, attributes: List[AttributeInfo]) -> Optional[str]:
        """Try to inline a Utrecht component using auto-detection.

        Args:
            element: ContentElement with component info
            attributes: List of AttributeInfo

        Returns:
            Inlined HTML or None if not a Utrecht component
        """
        try:
            from ..parsers.js_parser import parse_utrecht_library

            # Parse the Utrecht component
            component_info = parse_utrecht_library(element.component_name)
            if not component_info:
                return None

            # Get the primary element (actual HTML tag)
            primary = component_info.primary_element

            # Build the HTML tag with classes
            classes = ' '.join(primary.classes)

            # Get the content - usually it's just a variable reference
            # For FieldsetLegend, it's {legend}
            content_var = element.content if element.content else 'content'

            # Build the HTML element
            html = f'<{primary.tag} class="{classes}">{{{{ {content_var} }}}}</{primary.tag}>'

            return html

        except Exception:
            # Auto-inlining failed
            return None

    def _inline_icon_component(self, element, attributes: List[AttributeInfo]) -> str:
        """Inline Icon component as HTML.

        Based on the Icon component source, it renders as:
        <span class="utrecht-icon rvo-icon rvo-icon-{icon} rvo-icon--{size} rvo-icon--{color}" role="img" aria-label="..."></span>

        Args:
            element: ContentElement with Icon component info
            attributes: List of AttributeInfo

        Returns:
            Inlined icon HTML
        """
        props = element.component_props or {}

        # Get prop values, converting {varname} to {{ varname }}
        # Remove TypeScript type casts like "as any"
        icon_var = props.get('icon', 'icon').replace(' as any', '').strip()
        size_var = props.get('size', 'size').strip()
        aria_label_var = props.get('ariaLabel', 'iconAriaLabel').strip()

        # Build the span element
        # Note: Icon component defaults color to 'hemelblauw' if not specified
        icon_html = (
            f'<span class="utrecht-icon rvo-icon rvo-icon-{{{{ {icon_var} }}}} '
            f'rvo-icon--{{{{ {size_var} }}}} rvo-icon--hemelblauw" '
            f'role="img" aria-label="{{{{ {aria_label_var} | title }}}}"></span>'
        )

        return icon_html

    def add_todo_comment(self, description: str, source_file: str, source_line: int, action: str = "") -> None:
        """Add a TODO comment for manual review.

        Args:
            description: Description of what needs review
            source_file: Source file path
            source_line: Line number in source
            action: Action the developer should take
        """
        self.todo_comments.append({
            'description': description,
            'source': f"{source_file}:{source_line}",
            'action': action
        })

    def generate_todo_comment(self, todo: Dict[str, str]) -> str:
        """Generate a formatted TODO comment.

        Args:
            todo: Todo dict with description, source, action

        Returns:
            Formatted comment string
        """
        lines = [
            f"{{# TODO_CONVERSION: {todo['description']}"
        ]

        if 'pattern' in todo:
            lines.append(f"   Pattern: {todo['pattern']}")

        lines.append(f"   Source: {todo['source']}")

        if todo.get('action'):
            lines.append(f"   Action: {todo['action']}")

        lines.append("#}")

        return '\n'.join(lines)
