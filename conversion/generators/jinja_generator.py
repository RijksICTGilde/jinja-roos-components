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
        content_elements: List = None,
        wrapper_info: Optional[Dict] = None,
        component_structure: Optional[Dict] = None,
        nested_components: List[Dict] = None,
        array_mappings: Dict[str, Dict] = None
    ) -> str:
        """Generate complete Jinja template.

        Args:
            attributes: List of component attributes
            default_args: Default values for attributes
            html_tag: HTML tag name
            base_classes: Base CSS classes
            content: Optional inner content (legacy)
            content_elements: List of ContentElement objects
            wrapper_info: Optional wrapper element info (tag and classes)
            component_structure: Optional full component structure (for future use with arbitrary nesting)
            nested_components: List of nested component metadata
            array_mappings: Dict mapping array attributes to component info

        Returns:
            Generated Jinja template as string
        """
        # Store nested components and array mappings for use in content generation
        self.nested_components = nested_components or []
        self.array_mappings = array_mappings or {}

        lines = []

        # Add header comment
        lines.append(self._generate_header())

        # Generate variable declarations
        lines.append(self._generate_variables(attributes, default_args))

        # Generate CSS class building logic
        self.class_builder.add_base_classes(base_classes)
        lines.append(self.class_builder.generate_jinja_code())

        # If there's a wrapper, generate separate wrapper classes
        if wrapper_info:
            lines.append(self._generate_wrapper_classes(wrapper_info))

        # Generate content from content_elements if provided
        if content_elements:
            content = self._generate_content_from_elements(content_elements, attributes)

        # Generate HTML element (with wrapper if needed)
        # TODO: Use component_structure for arbitrary depth nesting in future
        lines.append(self._generate_html_element(html_tag, attributes, content, wrapper_info))

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
            # Special case: React 'children' prop maps to '_component_context.content' in Jinja
            if attr.name == 'children':
                # Children is nested content, accessed via .content not .children
                var_line = f"{{% set children = _component_context.content | default('') %}}"
            elif default is not None:
                # Format default value
                default_str = self._format_default_value(default, attr)
                var_line = f"{{% set {attr.name} = _component_context.{attr.name} | default({default_str}) %}}"
            else:
                # No default - use .get() for dict-safe access
                var_line = f"{{% set {attr.name} = _component_context.get('{attr.name}') %}}"

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
            value = default_args[attr.name]
            # For array attributes, if the value is a string reference (like 'defaultSteps'),
            # treat it as an example value and use empty array instead
            if 'array' in attr.types and isinstance(value, str):
                return []
            return value

        # Use type-based defaults
        if 'boolean' in attr.types:
            return False
        if 'array' in attr.types:
            return []  # Arrays default to empty list
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

    def _generate_wrapper_classes(self, wrapper_info: Dict) -> str:
        """Generate wrapper classes variable.

        Args:
            wrapper_info: Wrapper element info (tag and classes)

        Returns:
            Jinja variable declaration for wrapper classes
        """
        classes_str = ', '.join(f"'{cls}'" for cls in wrapper_info['classes'])
        return f"{{% set wrapper_classes = [{classes_str}] %}}"

    def _generate_html_element(self, tag: str, attributes: List[AttributeInfo], content: str, wrapper_info: Optional[Dict] = None) -> str:
        """Generate HTML element with attributes.

        Args:
            tag: HTML tag name
            attributes: List of attributes
            content: Inner content
            wrapper_info: Optional wrapper element info

        Returns:
            HTML element string
        """
        lines = []

        # If there's a wrapper, generate wrapper opening tag
        if wrapper_info:
            wrapper_tag = wrapper_info['tag']
            wrapper_opening = f'<{wrapper_tag} class="{{{{ wrapper_classes | join(\' \') }}}}" data-roos-component="{self.component_name}">'
            lines.append(wrapper_opening)

        # Inner element opening tag
        inner_attrs = [
            'class="{{ css_classes | join(\' \') }}"'
        ]

        # Add data-roos-component only if there's no wrapper (wrapper has it)
        if not wrapper_info:
            inner_attrs.append(f'data-roos-component="{self.component_name}"')

        # Add common HTML attributes
        for attr in attributes:
            if attr.name in ['id', 'type', 'disabled', 'required', 'readonly', 'placeholder']:
                attr_str = self._generate_html_attribute(attr)
                if attr_str:
                    inner_attrs.append(attr_str)

        # Add event handlers via mixin
        inner_attrs.append('{{ events.render_extra_attributes(_component_context) }}')

        # Build inner tag
        opening_tag = f"<{tag}"
        for attr in inner_attrs:
            indent = "        " if wrapper_info else "    "
            opening_tag += f"\n{indent}{attr}"
        opening_tag += ">"

        if wrapper_info:
            lines.append("    " + opening_tag)
        else:
            lines.append(opening_tag)

        # Content
        indent = "        " if wrapper_info else "    "
        if content:
            lines.append(f"{indent}{content}")
        else:
            # Default content placeholder
            lines.append(f"{indent}{{# Content #}}")

        # Closing tags
        if wrapper_info:
            lines.append(f"    </{tag}>")
            lines.append(f"</{wrapper_info['tag']}>")
        else:
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

            elif element.type == 'array_map':
                # Convert array.map() to Jinja for-loop with nested component
                loop_content = self._generate_array_map_loop(element, attributes)
                parts.append(loop_content)

            elif element.type == 'fallback_chain':
                # Generate if/elif structure from fallback chain
                chain_content = self._generate_fallback_chain(element, attributes)
                parts.append(chain_content)

            elif element.type == 'children_passthrough':
                # Simple children passthrough
                if element.condition:
                    parts.append(f"{{% if {element.condition} %}}")
                parts.append("{{ children | safe }}")
                if element.condition:
                    parts.append("{% endif %}")

            elif element.type == 'conditional_component':
                # Conditional component rendering
                # e.g., let labelMarkup = label; if (state === 'incomplete' || ...) { labelMarkup = <Link .../> }
                jinja_condition = self._convert_condition_to_jinja(element.condition)

                # Try to inline/convert the component
                component_html = self._inline_component(element, attributes)

                # Generate fallback (default value)
                fallback = f"{{{{ {element.fallback_value} }}}}"

                # Build if/else structure
                parts.append(f"{{% if {jinja_condition} %}}")
                parts.append(f"    {component_html}")
                parts.append("{% else %}")
                parts.append(f"    {fallback}")
                parts.append("{% endif %}")

        return '\n'.join(parts) if any('\n' in p for p in parts) else ''.join(parts)

    def _convert_condition_to_jinja(self, condition: str) -> str:
        """Convert React condition to Jinja condition.

        Args:
            condition: React condition like "showIcon === 'before'" or
                      "state === 'incomplete' || state === 'doing'"

        Returns:
            Jinja condition like "showIcon == 'before'" or
                      "state == 'incomplete' or state == 'doing'"
        """
        # Replace === with ==
        jinja_cond = condition.replace(' === ', ' == ')
        # Replace !== with !=
        jinja_cond = jinja_cond.replace(' !== ', ' != ')
        # Replace || with or
        jinja_cond = jinja_cond.replace(' || ', ' or ')
        # Replace && with and
        jinja_cond = jinja_cond.replace(' && ', ' and ')
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
        For other components (like Link), generate component tags.

        Args:
            element: ContentElement with component info
            attributes: List of AttributeInfo

        Returns:
            Inlined component HTML or component tag
        """
        if element.component_name == 'Icon':
            return self._inline_icon_component(element, attributes)

        # Try to generate a component tag for known converted components FIRST
        # This takes precedence over Utrecht inlining for components like Link
        component_tag = self._try_generate_component_tag(element)
        if component_tag:
            return component_tag

        # Try to auto-inline Utrecht components (only if not a known component)
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

    def _try_generate_component_tag(self, element) -> Optional[str]:
        """Try to generate a component tag for a known converted component.

        Args:
            element: ContentElement with component info

        Returns:
            Component tag string or None if component not found
        """
        # Convert component name to kebab-case (Link → link)
        component_name_kebab = self._to_kebab_case(element.component_name)

        # Check if this component exists (basic check - could be improved)
        # For now, just generate the tag for common components like Link
        known_components = ['link', 'button', 'heading', 'paragraph']

        if component_name_kebab not in known_components:
            return None

        # Build component tag with props
        tag_name = f'c-{component_name_kebab}'
        props = element.component_props or {}

        # Extract content prop (if any) - this becomes inner content, not an attribute
        content_value = props.get('content', None)

        # Convert props to Jinja attributes
        attrs = []
        for prop_name, prop_value in props.items():
            # Skip content (it's inner content, not an attribute)
            if prop_name == 'content':
                continue
            # Handle className -> class
            elif prop_name == 'className':
                attrs.append(f'class="{prop_value}"')
            # Handle href (for links)
            elif prop_name == 'href':
                attrs.append(f'href="{{{{ {prop_value} }}}}"')
            # Event handlers: onClick → @click, onMouseDown → @mousedown, etc.
            elif prop_name.startswith('on'):
                # Convert onClick to @click (remove 'on' prefix and lowercase the first char of event name)
                event_name = prop_name[2:]  # Remove 'on' prefix
                event_name = event_name[0].lower() + event_name[1:]  # Lowercase first char: Click → click
                attrs.append(f'@{event_name}="{{{{ {prop_value} }}}}"')
            # Regular props
            else:
                attrs.append(f'{prop_name}="{{{{ {prop_value} }}}}"')

        # Build the tag
        attr_str = ' '.join(attrs) if attrs else ''
        if content_value:
            # Component with content
            if attr_str:
                return f'<{tag_name} {attr_str}>{{{{ {content_value} }}}}</{tag_name}>'
            else:
                return f'<{tag_name}>{{{{ {content_value} }}}}</{tag_name}>'
        else:
            # Self-closing or empty component
            if attr_str:
                return f'<{tag_name} {attr_str}></{tag_name}>'
            else:
                return f'<{tag_name}></{tag_name}>'

    def _generate_fallback_chain(self, element, attributes: List[AttributeInfo]) -> str:
        """Generate if/elif structure from fallback chain.

        Args:
            element: ContentElement with type='fallback_chain'
            attributes: List of AttributeInfo

        Returns:
            Jinja if/elif/endif structure
        """
        lines = []

        for i, part in enumerate(element.fallback_chain):
            part_type = part.get('type')
            condition = part.get('condition')

            # Generate if or elif
            if i == 0:
                lines.append(f"    {{% if {condition} %}}")
            else:
                lines.append(f"    {{% elif {condition} %}}")

            # Generate content based on type
            if part_type == 'children_passthrough':
                lines.append("        {{ children | safe }}")
            elif part_type == 'array_map':
                # Get the array_map element
                map_element = part.get('element')
                if map_element:
                    # Generate for-loop without the wrapping if (already in if/elif)
                    lines.append(f"        {{% for {map_element.item_var} in {map_element.array_name} %}}")
                    component_tag = self._generate_nested_component_tag(map_element)
                    lines.append(f"            {component_tag}")
                    lines.append("        {% endfor %}")

        lines.append("    {% endif %}")
        return '\n'.join(lines)

    def _generate_array_map_loop(self, element, attributes: List[AttributeInfo]) -> str:
        """Generate Jinja for-loop from array.map() element.

        Args:
            element: ContentElement with type='array_map'
            attributes: List of AttributeInfo

        Returns:
            Jinja for-loop string with nested component
        """
        lines = []

        # Wrap in conditional if element has a condition
        if element.condition:
            jinja_condition = self._convert_condition_to_jinja(element.condition)
            # Check if it's a negated condition
            if jinja_condition.startswith('not ('):
                # It's an elif case
                lines.append(f"{{% elif {element.array_name} %}}")
            else:
                lines.append(f"{{% if {jinja_condition} %}}")

        # Generate the for-loop
        lines.append(f"        {{% for {element.item_var} in {element.array_name} %}}")

        # Generate the nested component tag
        component_tag = self._generate_nested_component_tag(element)
        lines.append(f"            {component_tag}")

        lines.append("        {% endfor %}")

        return '\n'.join(lines)

    def _generate_nested_component_tag(self, element) -> str:
        """Generate nested component tag with attributes.

        Args:
            element: ContentElement with component info

        Returns:
            Component tag string like <c-component-name attr="value"></c-component-name>
        """
        # Find the component metadata
        component_meta = None
        for comp in self.nested_components:
            if comp['component_class'] == element.component_name:
                component_meta = comp
                break

        if not component_meta:
            # Fallback: convert component name to tag
            tag_name = self._to_kebab_case(element.component_name)
            tag_name = f'c-{tag_name}'
        else:
            tag_name = component_meta['tag_name']

        # Build attributes
        attrs = []

        if element.is_spread:
            # Props are spread from array item - need to know which props to include
            if element.array_name in self.array_mappings:
                mapping = self.array_mappings[element.array_name]
                item_props = mapping.get('item_props', [])

                # Generate attribute for each prop
                for prop in item_props:
                    # Skip function props
                    if prop.startswith('on'):
                        continue
                    attrs.append(f'{prop}="{{{{ {element.item_var}.{prop} }}}}"')
        else:
            # Explicit props from component_props
            for prop_name, prop_value in element.component_props.items():
                # Convert prop value to Jinja
                jinja_value = prop_value.replace(element.item_var, f'{element.item_var}')
                attrs.append(f'{prop_name}="{{{{ {jinja_value} }}}}"')

        # Build the tag
        if attrs:
            attr_str = '\n                '.join(attrs)
            return f'<{tag_name}\n                {attr_str}\n            ></{tag_name}>'
        else:
            return f'<{tag_name}></{tag_name}>'

    def _to_kebab_case(self, pascal_case: str) -> str:
        """Convert PascalCase to kebab-case.

        Args:
            pascal_case: PascalCase string

        Returns:
            kebab-case string
        """
        import re
        kebab = re.sub(r'(?<!^)(?=[A-Z])', '-', pascal_case)
        return kebab.lower()

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
