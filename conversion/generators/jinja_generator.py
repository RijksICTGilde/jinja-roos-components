"""Generate Jinja templates from parsed React components."""

import re
from typing import List, Dict, Any, Optional
from ..parsers.interface_parser import AttributeInfo
from .class_builder import ClassBuilder


class JinjaGenerator:
    """Generator for Jinja2 templates."""

    # Reserved names in Python/Jinja that should be avoided
    RESERVED_NAMES = {
        'items', 'keys', 'values', 'update', 'get', 'pop', 'clear',
        'copy', 'setdefault', 'popitem', 'fromkeys',
        'list', 'dict', 'set', 'tuple', 'str', 'int', 'float', 'bool',
        'len', 'range', 'sum', 'min', 'max', 'all', 'any',
        'filter', 'map', 'zip', 'sorted', 'reversed',
        'type', 'input', 'output', 'file', 'object',
        'loop'  # Jinja loop variable
    }

    def __init__(self, component_name: str):
        """Initialize generator.

        Args:
            component_name: Name of the component
        """
        self.component_name = component_name
        self.class_builder = ClassBuilder()
        self.variables: List[str] = []
        self.todo_comments: List[Dict[str, str]] = []
        self.name_mappings: Dict[str, str] = {}  # Maps original names to safe names

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
        array_mappings: Dict[str, Dict] = None,
        add_children_support: bool = False,
        custom_content_template: Optional[str] = None,
        component_refs: Dict[str, Dict] = None
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
            add_children_support: Whether to add children/content support as fallback
            custom_content_template: Optional custom Jinja template for content rendering

        Returns:
            Generated Jinja template as string
        """
        # Store nested components and array mappings for use in content generation
        self.nested_components = nested_components or []
        self.array_mappings = array_mappings or {}
        self.add_children_support = add_children_support

        # Special handling for composition components
        # (components with no own attributes that just wrap other components)
        if not attributes and nested_components and len(nested_components) > 0:
            return self._generate_composition_template(nested_components, default_args, content_elements)

        lines = []

        # Add header comment
        lines.append(self._generate_header())

        # Generate variable declarations
        lines.append(self._generate_variables(attributes, default_args))

        # Generate component variable declarations (like iconMarkup = Icon(...))
        if component_refs:
            comp_var_lines = self._generate_component_variables(component_refs, nested_components or [])
            if comp_var_lines:
                lines.append(comp_var_lines)

        # Generate CSS class building logic
        self.class_builder.add_base_classes(base_classes)
        lines.append(self.class_builder.generate_jinja_code(name_mappings=self.name_mappings))

        # Add utility classes from text-style, margin, padding attributes
        lines.append(self._generate_utility_classes())

        # Add custom classes from class attribute
        lines.append(self._generate_custom_classes())

        # If there's a wrapper, generate separate wrapper classes
        if wrapper_info:
            lines.append(self._generate_wrapper_classes(wrapper_info))

        # Generate content from custom template, content_elements, or default
        if custom_content_template:
            # Use custom content template from customization
            content = custom_content_template
        elif content_elements:
            # Generate from content elements
            content = self._generate_content_from_elements(content_elements, attributes)
        # else: keep the content parameter value

        # Generate HTML element (with wrapper if needed)
        # TODO: Use component_structure for arbitrary depth nesting in future
        dynamic_tag = component_structure.get('dynamic_tag') if component_structure else None
        lines.append(self._generate_html_element(html_tag, attributes, content, wrapper_info, dynamic_tag))

        return '\n'.join(lines)

    def _get_safe_variable_name(self, attr_name: str) -> str:
        """Get a safe variable name, avoiding Python/Jinja reserved names.

        Args:
            attr_name: Original attribute name

        Returns:
            Safe variable name
        """
        if attr_name in self.RESERVED_NAMES:
            # Add prefix to avoid conflict
            safe_name = f"{attr_name}_attr" if attr_name in ['type', 'filter', 'map'] else f"list_{attr_name}"
            self.name_mappings[attr_name] = safe_name
            return safe_name
        return attr_name

    def _get_mapped_name(self, attr_name: str) -> str:
        """Get the mapped variable name if it exists, otherwise return original.

        Args:
            attr_name: Original attribute name

        Returns:
            Mapped variable name or original
        """
        return self.name_mappings.get(attr_name, attr_name)

    def _apply_name_mappings(self, text: str) -> str:
        """Apply name mappings to variable names in text.

        Args:
            text: Text containing variable names

        Returns:
            Text with mapped variable names
        """
        import re
        result = text
        # Sort by length descending to avoid partial matches
        for original, mapped in sorted(self.name_mappings.items(), key=lambda x: len(x[0]), reverse=True):
            # Match whole words only
            result = re.sub(r'\b' + re.escape(original) + r'\b', mapped, result)
        return result

    def _generate_header(self) -> str:
        """Generate header comment.

        Returns:
            Header comment
        """
        return f"""{{% import 'components/_generic_attributes.j2' as attrs %}}
{{% import 'components/_attribute_mixin.j2' as attributes %}}
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

            # Get safe variable name (avoid reserved names)
            safe_name = self._get_safe_variable_name(attr.name)

            # Get default value
            default = self._get_default_value(attr, default_args)

            # Generate variable declaration
            # Special case: React 'children' prop maps to '_component_context.content' in Jinja
            if attr.name == 'children':
                # Children is nested content, accessed via .content not .children
                # Use .get() for consistency - more reliable than | default filter
                var_line = f"{{% set children = _component_context.get('content', '') %}}"
            elif default is not None:
                # Format default value
                default_str = self._format_default_value(default, attr)
                # Use .get(key, default) for all cases - more reliable than Jinja's | default filter
                # .get() returns None when key is missing, and Jinja's default filter doesn't replace None
                # Using .get(key, default) ensures the default is applied by Python, not Jinja
                var_line = f"{{% set {safe_name} = _component_context.get('{attr.name}', {default_str}) %}}"
            else:
                # No default - use .get() for dict-safe access
                var_line = f"{{% set {safe_name} = _component_context.get('{attr.name}') %}}"

            lines.append(var_line)
            self.variables.append(safe_name)

        return '\n'.join(lines)

    def _generate_component_variables(self, component_refs: Dict[str, Dict], nested_components: List[Dict]) -> str:
        """Generate component variable declarations like {% set iconMarkup %}<c-icon...>{% endset %}.

        Args:
            component_refs: Dict of variable names to component reference info
            nested_components: List of nested component metadata

        Returns:
            Jinja set blocks for component variables
        """
        lines = []

        # First pass: Generate computed string variables and variable transforms (dependencies for component refs)
        for var_name, ref_info in component_refs.items():
            if ref_info.get('type') == 'computed_string':
                # Generate list-based class building
                conditionals = ref_info.get('conditionals', [])
                if conditionals:
                    # Generate: {% set var_classes = [] %}
                    lines.append(f"{{% set {var_name}_classes = [] %}}")

                    # Generate conditional additions
                    for cond_info in conditionals:
                        condition = self._convert_js_condition_to_jinja(cond_info['condition'])
                        value = cond_info['value']
                        lines.append(f"{{% if {condition} %}}{{% set {var_name}_classes = {var_name}_classes + ['{value}'] %}}{{% endif %}}")

                    # Generate final join
                    lines.append(f"{{% set {var_name} = {var_name}_classes | join(' ') %}}")

            elif ref_info.get('type') == 'variable_transform':
                # Variable transforms are handled by the class builder as computed vars
                # (added in _build_class_logic before this method is called)
                # So we skip them here to avoid duplicates
                pass

        # Second pass: Generate component references (may depend on computed strings)
        for var_name, ref_info in component_refs.items():
            # Handle component references
            if not ref_info.get('component'):
                continue

            component_name = ref_info['component']
            props = ref_info.get('props', {})

            # Find the nested component tag name
            tag_name = None
            for nested in nested_components:
                if nested['component_class'] == component_name:
                    tag_name = nested['tag_name']
                    break

            if not tag_name:
                # Component not found in nested components, skip
                continue

            # Generate component tag with props
            attrs_list = []
            for prop_name, prop_value in props.items():
                # Translate React prop names to HTML attribute names
                # className → class (React uses className, HTML/Jinja uses class)
                # htmlFor → for (if we encounter it)
                # Keep other names as-is
                attr_name = self._translate_react_prop_to_html_attr(prop_name)

                # Convert prop value to Jinja expression
                # Simple variable reference: icon → {{ icon }}
                # String literal: 'value' → "value"
                if prop_value.startswith("'") and prop_value.endswith("'"):
                    # String literal
                    attrs_list.append(f'{attr_name}="{prop_value[1:-1]}"')
                else:
                    # Variable or expression
                    attrs_list.append(f'{attr_name}="{{{{ {prop_value} }}}}"')

            attrs_str = ' '.join(attrs_list)

            # Generate {% set varName %}<c-component ...></c-component>{% endset %}
            lines.append(f"{{% set {var_name} %}}<{tag_name} {attrs_str}></{tag_name}>{{% endset %}}")

        return '\n'.join(lines)

    def _convert_js_condition_to_jinja(self, js_condition: str) -> str:
        """Convert JavaScript condition to Jinja2 condition.

        Args:
            js_condition: JavaScript condition (e.g., "showIcon === 'before'")

        Returns:
            Jinja2 condition (e.g., "showIcon == 'before'")
        """
        jinja_condition = js_condition
        # Convert comparison operators
        jinja_condition = jinja_condition.replace('===', '==')
        jinja_condition = jinja_condition.replace('!==', '!=')
        # Convert logical operators
        jinja_condition = jinja_condition.replace('&&', 'and')
        jinja_condition = jinja_condition.replace('||', 'or')
        # Convert negation (careful with order - do this after !== conversion)
        jinja_condition = re.sub(r'\!(\w+)', r'not \1', jinja_condition)
        return jinja_condition

    def _translate_react_prop_to_html_attr(self, prop_name: str) -> str:
        """Translate React prop names to HTML attribute names.

        Args:
            prop_name: React prop name (e.g., 'className', 'htmlFor')

        Returns:
            HTML attribute name (e.g., 'class', 'for')
        """
        # Map of React prop names to HTML attribute names
        translation_map = {
            'className': 'class',
            'htmlFor': 'for',
        }
        return translation_map.get(prop_name, prop_name)

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

    def _generate_utility_classes(self) -> str:
        """Generate code to add utility classes from attribute mixin.

        Returns:
            Jinja code to add utility classes
        """
        return """{# Add utility classes from text-style, margin, padding attributes #}
{% set utility_classes = attributes.render_utility_classes(_component_context) %}
{% if utility_classes %}
    {% set css_classes = css_classes + utility_classes.split() %}
{% endif %}"""

    def _generate_custom_classes(self) -> str:
        """Generate code to add custom classes from class attribute.

        Returns:
            Jinja code to add custom classes
        """
        return """{# Add custom classes from class attribute #}
{% if _component_context.get('class') %}
    {% set css_classes = css_classes + _component_context['class'].split() %}
{% endif %}"""

    def _generate_wrapper_classes(self, wrapper_info: Dict) -> str:
        """Generate wrapper classes variable.

        Args:
            wrapper_info: Wrapper element info (tag and classes)

        Returns:
            Jinja variable declaration for wrapper classes
        """
        classes_str = ', '.join(f"'{cls}'" for cls in wrapper_info['classes'])
        return f"{{% set wrapper_classes = [{classes_str}] %}}"

    def _generate_html_element(self, tag: str, attributes: List[AttributeInfo], content: str, wrapper_info: Optional[Dict] = None, dynamic_tag: Optional[Dict] = None) -> str:
        """Generate HTML element with attributes.

        Args:
            tag: HTML tag name or component name
            attributes: List of attributes
            content: Inner content
            wrapper_info: Optional wrapper element info
            dynamic_tag: Optional dynamic tag info for conditional tag rendering

        Returns:
            HTML element string
        """
        # Handle dynamic tag selection (e.g., ul vs ol based on condition)
        if dynamic_tag:
            return self._generate_dynamic_tag_element(dynamic_tag, attributes, content, wrapper_info)

        # Check if tag is a React component (PascalCase) instead of HTML tag
        is_component = tag and tag[0].isupper()

        # If it's a component with a wrapper, we need to generate the component tag from content
        # The content should have the component's props parsed
        if is_component and wrapper_info:
            # The content should already be parsed with the component tag
            # Just wrap it in the wrapper
            return self._generate_wrapper_with_content(wrapper_info, content)

        lines = []

        # If there's a wrapper, generate wrapper opening tag
        if wrapper_info:
            wrapper_tag = wrapper_info['tag']
            wrapper_attrs = ['class="{{ wrapper_classes | join(\' \') }}"']

            # Add wrapper attributes (like role="presentation")
            if 'attributes' in wrapper_info:
                for attr_name, attr_value in wrapper_info['attributes'].items():
                    if isinstance(attr_value, bool):
                        if attr_value:
                            wrapper_attrs.append(attr_name)
                    else:
                        wrapper_attrs.append(f'{attr_name}="{attr_value}"')

            wrapper_attrs.append(f'data-roos-component="{self.component_name}"')

            # Add event handlers and extra attributes via mixin
            wrapper_attrs.append('{{ attrs.render_extra_attributes(_component_context) }}')

            wrapper_opening = f'<{wrapper_tag} {" ".join(wrapper_attrs)}>'
            lines.append(wrapper_opening)

        # Inner element opening tag
        inner_attrs = [
            'class="{{ css_classes | join(\' \') }}"'
        ]

        # Add data-roos-component only if there's no wrapper (wrapper has it)
        if not wrapper_info:
            inner_attrs.append(f'data-roos-component="{self.component_name}"')

        # Add HTML attributes based on tag type
        # Map of tag -> list of relevant attributes
        tag_specific_attrs = {
            'a': ['href', 'target', 'role', 'rel', 'download'],
            'input': ['type', 'placeholder', 'value', 'name', 'disabled', 'required', 'readonly', 'checked', 'min', 'max', 'step'],
            'button': ['type', 'disabled', 'name', 'value'],
            'select': ['name', 'disabled', 'required', 'multiple'],
            'textarea': ['name', 'placeholder', 'disabled', 'required', 'readonly', 'rows', 'cols'],
            'img': ['src', 'alt', 'width', 'height'],
            'form': ['action', 'method', 'enctype'],
        }

        # Common attributes for all tags
        common_attrs = ['id', 'title', 'tabindex']

        # Get relevant attributes for this tag
        relevant_attrs = tag_specific_attrs.get(tag, []) + common_attrs

        for attr in attributes:
            # Skip if this attribute is a pass-through attribute (will be handled separately)
            if hasattr(attr, '_passthrough_target'):
                continue
            if attr.name in relevant_attrs:
                attr_str = self._generate_html_attribute(attr)
                if attr_str:
                    inner_attrs.append(attr_str)

        # Add pass-through attributes (attributes with _passthrough_target metadata)
        for attr in attributes:
            # Check if this attribute has pass-through metadata and targets the current element
            if hasattr(attr, '_passthrough_target') and attr._passthrough_target == tag:
                # Get the target attribute name (might be different from the variable name)
                target_attr_name = getattr(attr, '_passthrough_attribute', attr.name)
                attr_str = self._generate_html_attribute_custom(attr, target_attr_name)
                if attr_str:
                    inner_attrs.append(attr_str)

        # Add event handlers via mixin
        inner_attrs.append('{{ attrs.render_extra_attributes(_component_context) }}')

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
            # Check if children attribute exists (added via add_children_support customization)
            has_children = any(attr.name == 'children' for attr in attributes)
            if has_children:
                # Render children variable with safe filter (allows HTML markup)
                lines.append(f"{indent}{{{{ children | safe }}}}")
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

    def _generate_wrapper_with_content(self, wrapper_info: Dict, content: str) -> str:
        """Generate wrapper element with content inside.

        Args:
            wrapper_info: Wrapper element info
            content: Pre-generated content (should be component tag)

        Returns:
            Wrapper HTML with content
        """
        lines = []

        # Generate wrapper opening tag
        wrapper_tag = wrapper_info['tag']
        wrapper_attrs = ['class="{{ wrapper_classes | join(\' \') }}"']

        # Add wrapper attributes (like role="presentation")
        if 'attributes' in wrapper_info:
            for attr_name, attr_value in wrapper_info['attributes'].items():
                if isinstance(attr_value, bool):
                    if attr_value:
                        wrapper_attrs.append(attr_name)
                else:
                    wrapper_attrs.append(f'{attr_name}="{attr_value}"')

        wrapper_attrs.append(f'data-roos-component="{self.component_name}"')

        # Add event handlers and extra attributes via mixin
        wrapper_attrs.append('{{ attrs.render_extra_attributes(_component_context) }}')

        wrapper_opening = f'<{wrapper_tag} {" ".join(wrapper_attrs)}>'
        lines.append(wrapper_opening)

        # Add content (should be the component tag)
        if content:
            lines.append(f'    {content}')

        # Close wrapper
        lines.append(f'</{wrapper_tag}>')

        return '\n'.join(lines)

    def _generate_wrapped_component_element(self, component_name: str, attributes: List[AttributeInfo], content: str, wrapper_info: Optional[Dict]) -> str:
        """Generate wrapped component element (e.g., <li> wrapping <c-link>).

        Args:
            component_name: Component name (e.g., 'Link')
            attributes: List of component attributes
            content: Inner content
            wrapper_info: Wrapper element info

        Returns:
            HTML string with wrapper and component tag
        """
        lines = []

        # Generate wrapper opening tag
        if wrapper_info:
            wrapper_tag = wrapper_info['tag']
            wrapper_attrs = ['class="{{ wrapper_classes | join(\' \') }}"']

            # Add wrapper attributes (like role="presentation")
            if 'attributes' in wrapper_info:
                for attr_name, attr_value in wrapper_info['attributes'].items():
                    if isinstance(attr_value, bool):
                        if attr_value:
                            wrapper_attrs.append(attr_name)
                    else:
                        wrapper_attrs.append(f'{attr_name}="{attr_value}"')

            wrapper_attrs.append(f'data-roos-component="{self.component_name}"')

            # Add event handlers and extra attributes via mixin
            wrapper_attrs.append('{{ attrs.render_extra_attributes(_component_context) }}')

            wrapper_opening = f'<{wrapper_tag} {" ".join(wrapper_attrs)}>'
            lines.append(wrapper_opening)

        # Generate component tag
        component_tag_name = self._to_kebab_case(component_name)
        component_tag_name = f'c-{component_tag_name}'

        # Find component in nested_components to get tag name
        for comp in self.nested_components:
            if comp['component_class'] == component_name:
                component_tag_name = comp['tag_name']
                break

        # Build component attributes from the component's attributes
        component_attrs = []

        # Add role, href, aria-selected, and other attributes that are defined
        for attr in attributes:
            # Skip function props
            if attr.is_function:
                continue

            var_name = self._get_mapped_name(attr.name)

            # Special handling for specific attributes
            # Skip 'label' - it will be used as inner content, not an attribute
            if attr.name == 'label':
                continue
            elif attr.name in ['href', 'selected']:
                if 'boolean' in attr.types:
                    # For boolean: selected="{{ selected }}"
                    component_attrs.append(f'{attr.name}="{{{{ {var_name} }}}}"')
                else:
                    component_attrs.append(f'{attr.name}="{{{{ {var_name} }}}}"')

        # Add fixed attributes for Link component
        # role="tab", aria-selected based on selected, noUnderline, active, weight
        component_attrs.insert(0, 'role="tab"')

        # aria-selected should be string "true" or "false"
        if any(a.name == 'selected' for a in attributes):
            component_attrs.append('aria-selected="{{ \'true\' if selected else \'false\' }}"')

        # Add class with clsx logic
        component_attrs.append('class="{{ css_classes | join(\' \') }}"')

        # noUnderline always true for tabs
        component_attrs.append('noUnderline="true"')

        # active based on selected
        if any(a.name == 'selected' for a in attributes):
            component_attrs.append('active="{{ selected }}"')
            component_attrs.append('weight="{{ \'bold\' if selected else \'normal\' }}"')

        # Build tag
        lines.append(f'    <{component_tag_name}')
        for attr in component_attrs:
            lines.append(f'        {attr}')
        # Content - use double braces to escape in f-string
        if content:
            lines.append(f'    >{content}</{component_tag_name}>')
        else:
            lines.append(f'    >{{{{ label }}}}</{component_tag_name}>')

        # Close wrapper
        if wrapper_info:
            lines.append(f'</{wrapper_info["tag"]}>')

        return '\n'.join(lines)

    def _generate_dynamic_tag_element(self, dynamic_tag: Dict, attributes: List[AttributeInfo], content: str, wrapper_info: Optional[Dict] = None) -> str:
        """Generate HTML element with dynamic tag selection.

        Args:
            dynamic_tag: Dynamic tag info with condition and tag options
            attributes: List of attributes
            content: Inner content
            wrapper_info: Optional wrapper element info

        Returns:
            HTML element string with conditional tag
        """
        lines = []

        # Generate tag_name variable from condition
        # Convert React condition to Jinja: type === 'unordered' → type == 'unordered'
        condition = dynamic_tag['condition'].replace(' === ', ' == ').replace(' !== ', ' != ')
        # Apply name mappings to condition (e.g., type → type_attr)
        condition = self._apply_name_mappings(condition)
        true_tag = dynamic_tag['true_tag']
        false_tag = dynamic_tag['false_tag']

        # Add tag selection variable before wrapper/content
        lines.append(f"{{% set tag_name = '{true_tag}' if {condition} else '{false_tag}' %}}")

        # If there's a wrapper, generate wrapper opening tag
        if wrapper_info:
            wrapper_tag = wrapper_info['tag']
            wrapper_attrs = ['class="{{ wrapper_classes | join(\' \') }}"']

            # Add wrapper attributes (like role="presentation")
            if 'attributes' in wrapper_info:
                for attr_name, attr_value in wrapper_info['attributes'].items():
                    if isinstance(attr_value, bool):
                        if attr_value:
                            wrapper_attrs.append(attr_name)
                    else:
                        wrapper_attrs.append(f'{attr_name}="{attr_value}"')

            wrapper_attrs.append(f'data-roos-component="{self.component_name}"')

            # Add event handlers and extra attributes via mixin
            wrapper_attrs.append('{{ attrs.render_extra_attributes(_component_context) }}')

            wrapper_opening = f'<{wrapper_tag} {" ".join(wrapper_attrs)}>'
            lines.append(wrapper_opening)

        # Inner element opening tag with dynamic tag
        inner_attrs = [
            'class="{{ css_classes | join(\' \') }}"'
        ]

        # Add data-roos-component only if there's no wrapper
        if not wrapper_info:
            inner_attrs.append(f'data-roos-component="{self.component_name}"')

        # Add common HTML attributes
        common_attrs = ['id', 'type', 'disabled', 'required', 'readonly', 'placeholder']
        for attr in attributes:
            if hasattr(attr, '_passthrough_target'):
                continue
            if attr.name in common_attrs:
                attr_str = self._generate_html_attribute(attr)
                if attr_str:
                    inner_attrs.append(attr_str)

        # Add pass-through attributes
        for attr in attributes:
            if hasattr(attr, '_passthrough_target'):
                # For dynamic tags, we don't know the tag name at generation time
                # so we skip the tag check and add all pass-through attrs
                target_attr_name = getattr(attr, '_passthrough_attribute', attr.name)
                attr_str = self._generate_html_attribute_custom(attr, target_attr_name)
                if attr_str:
                    inner_attrs.append(attr_str)

        # Add event handlers via mixin
        inner_attrs.append('{{ attrs.render_extra_attributes(_component_context) }}')

        # Build dynamic opening tag
        opening_tag = "<{{ tag_name }}"
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
            # Check if children attribute exists
            has_children = any(attr.name == 'children' for attr in attributes)
            if has_children:
                lines.append(f"{indent}{{{{ children | safe }}}}")
            else:
                lines.append(f"{indent}{{# Content #}}")

        # Closing tags
        if wrapper_info:
            lines.append("    </{{ tag_name }}>")
            lines.append(f"</{wrapper_info['tag']}>")
        else:
            lines.append("</{{ tag_name }}>")

        return '\n'.join(lines)

    def _generate_html_attribute(self, attr: AttributeInfo) -> Optional[str]:
        """Generate HTML attribute string.

        Args:
            attr: Attribute info

        Returns:
            Attribute string or None
        """
        # Get the mapped variable name (for reserved words)
        var_name = self._get_mapped_name(attr.name)

        if 'boolean' in attr.types:
            # Boolean attributes
            return f"{{% if {var_name} %}}{attr.name}{{% endif %}}"
        else:
            # Value attributes
            return f'{attr.name}="{{{{ {var_name} }}}}"'

    def _generate_html_attribute_custom(self, attr: AttributeInfo, target_attr_name: str) -> Optional[str]:
        """Generate HTML attribute string with custom attribute name.

        Args:
            attr: Attribute info
            target_attr_name: The name to use for the HTML attribute (can differ from attr.name)

        Returns:
            Attribute string or None
        """
        # Get the mapped variable name (for reserved words)
        var_name = self._get_mapped_name(attr.name)

        if 'boolean' in attr.types:
            # Boolean attributes
            return f"{{% if {var_name} %}}{target_attr_name}{{% endif %}}"
        else:
            # Value attributes - only render if the variable has a value
            return f'{{% if {var_name} %}}{target_attr_name}="{{{{ {var_name} }}}}"{{% endif %}}'

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

            elif element.type == 'jsx_fragment':
                # JSX fragment - parse and inline the content
                # The element.jsx_content contains JSX like:
                # <>
                #   {showIcon === 'before' && iconMarkup}
                #   {children || content}
                #   {showIcon === 'after' && iconMarkup}
                # </>
                jsx_content = element.jsx_content

                # Strip JSX fragment markers <> and </>
                jsx_content = jsx_content.strip()
                if jsx_content.startswith('<>'):
                    jsx_content = jsx_content[2:]
                if jsx_content.endswith('</>'):
                    jsx_content = jsx_content[:-3]
                jsx_content = jsx_content.strip()

                # Parse individual JSX expressions from the fragment
                # The content is like: {expr1}\n{expr2}\n{expr3}
                import re
                expression_pattern = r'\{([^}]+)\}'

                fragment_parts = []
                for match in re.finditer(expression_pattern, jsx_content):
                    expression = match.group(1).strip()

                    # Convert common React patterns to Jinja
                    # Pattern: condition && value
                    if ' && ' in expression:
                        cond, value = expression.split(' && ', 1)
                        cond = cond.strip()
                        value = value.strip()

                        # Convert React syntax to Jinja
                        cond_jinja = cond.replace(' === ', ' == ').replace(' !== ', ' != ')

                        fragment_parts.append(f"{{% if {cond_jinja} %}}{{{{{value}}}}}{{% endif %}}")

                    # Pattern: value1 || value2  (fallback)
                    elif ' || ' in expression:
                        values = [v.strip() for v in expression.split(' || ')]
                        # Generate nested fallback: value1 or value2 or ...
                        jinja_expr = ' or '.join(values)
                        fragment_parts.append(f"{{{{ {jinja_expr} | safe }}}}")

                    # Simple variable
                    else:
                        fragment_parts.append(f"{{{{ {expression} | safe }}}}")

                fragment_content = '\n    '.join(fragment_parts)
                parts.append(fragment_content)

            elif element.type == 'component':
                # Nested component (e.g., Link inside a wrapper)
                component_tag = self._inline_component(element, attributes)
                parts.append(component_tag)

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

            elif element.type == 'content_function':
                # Content processing function
                # e.g., const contentMarkup = parseContentMarkup(children || content)
                # In Jinja: {% set contentMarkup = children or content %}
                # Then output with: {{ contentMarkup | safe }}
                var_name = element.content
                args = element.component_props.get('_function_args', 'children or content')

                # Convert React || to Jinja or
                jinja_args = args.replace(' || ', ' or ')

                # Output variable with safe filter (to allow HTML markup)
                parts.append(f"{{{{ {jinja_args} | safe }}}}")

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

        # Extract children (inner content)
        children_content = None
        if '_children' in props:
            children_data = props['_children']
            if isinstance(children_data, dict):
                # New format: {'value': ..., 'type': ...}
                children_value = children_data['value']
                # Strip {braces} if it's a JSX expression
                if children_value.startswith('{') and children_value.endswith('}'):
                    children_content = children_value[1:-1]
                else:
                    children_content = children_value
            else:
                # Old format: just a string
                children_content = children_data

        # Convert props to Jinja attributes
        attrs = []
        for prop_name, prop_data in props.items():
            # Skip special props
            if prop_name in ['_children', '_spread', 'content']:
                continue

            # Skip event handlers (onClick, onChange, etc.)
            if prop_name.startswith('on') and len(prop_name) > 2 and prop_name[2].isupper():
                continue

            # Get the prop value and type
            if isinstance(prop_data, dict):
                prop_value = prop_data['value']
                prop_type = prop_data['type']
            else:
                # Old format - assume expression
                prop_value = prop_data
                prop_type = 'expression'

            # Convert className to class
            attr_name = 'class' if prop_name == 'className' else prop_name

            # Convert the value based on type
            if prop_type == 'string':
                # String literal - keep as-is
                attrs.append(f'{attr_name}="{prop_value}"')
            elif prop_type == 'expression':
                # Expression - convert to Jinja
                jinja_value = self._convert_jsx_expression_to_jinja(prop_value)
                if jinja_value:
                    attrs.append(f'{attr_name}="{jinja_value}"')

        # Build the tag
        attr_str = ' '.join(attrs) if attrs else ''
        if children_content:
            # Component with content
            if attr_str:
                return f'<{tag_name} {attr_str}>{{{{ {children_content} }}}}</{tag_name}>'
            else:
                return f'<{tag_name}>{{{{ {children_content} }}}}</{tag_name}>'
        else:
            # Self-closing or empty component
            if attr_str:
                return f'<{tag_name} {attr_str}></{tag_name}>'
            else:
                return f'<{tag_name}></{tag_name}>'

    def _convert_jsx_expression_to_jinja(self, expr: str) -> Optional[str]:
        """Convert a JSX expression to Jinja.

        Handles:
        - clsx() calls: clsx('a', b && 'c') → "a {% if b %}c{% endif %}"
        - Ternary: a ? 'b' : 'c' → {{ 'b' if a else 'c' }}
        - Boolean literals: true/false → true/false
        - Variable references: var → {{ var }}

        Args:
            expr: JSX expression

        Returns:
            Jinja expression or None if can't convert
        """
        import re

        # Handle clsx() calls
        if expr.startswith('clsx('):
            return self._convert_clsx_to_jinja(expr)

        # Handle ternary operator
        if ' ? ' in expr and ' : ' in expr:
            return self._convert_ternary_to_jinja(expr)

        # Handle boolean literals
        if expr == 'true':
            return '{{ true }}'
        elif expr == 'false':
            return '{{ false }}'

        # Handle simple variable references
        if re.match(r'^\w+$', expr):
            return f'{{{{ {expr} }}}}'

        # Default: wrap in Jinja expression
        return f'{{{{ {expr} }}}}'

    def _convert_clsx_to_jinja(self, clsx_expr: str) -> str:
        """Convert clsx() call to Jinja class string.

        Examples:
        - clsx('a', 'b') → "a b"
        - clsx('a', selected && 'active') → "a {% if selected %}active{% endif %}"
        - clsx('a', selected ? 'active' : 'inactive') → "a {{ 'active' if selected else 'inactive' }}"

        Args:
            clsx_expr: clsx() expression

        Returns:
            Jinja class string
        """
        import re

        # Extract arguments from clsx(...)
        match = re.match(r'clsx\((.*)\)$', clsx_expr, re.DOTALL)
        if not match:
            return f'{{{{ {clsx_expr} }}}}'

        args_str = match.group(1)

        # Split by commas (but not inside parentheses/quotes)
        args = []
        current_arg = ''
        depth = 0
        in_string = False
        string_char = None

        for char in args_str:
            if char in ('"', "'") and not in_string:
                in_string = True
                string_char = char
                current_arg += char
            elif char == string_char and in_string:
                in_string = False
                current_arg += char
            elif char in '([{' and not in_string:
                depth += 1
                current_arg += char
            elif char in ')]}' and not in_string:
                depth -= 1
                current_arg += char
            elif char == ',' and depth == 0 and not in_string:
                args.append(current_arg.strip())
                current_arg = ''
            else:
                current_arg += char

        if current_arg.strip():
            args.append(current_arg.strip())

        # Convert each argument
        parts = []
        for arg in args:
            arg = arg.strip()

            # String literal - just use the value
            if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                parts.append(arg[1:-1])  # Remove quotes

            # Conditional: var && 'class'
            elif ' && ' in arg:
                condition, class_name = arg.split(' && ', 1)
                condition = condition.strip()
                class_name = class_name.strip().strip("'").strip('"')
                parts.append(f'{{% if {condition} %}}{class_name}{{% endif %}}')

            # Ternary: var ? 'a' : 'b'
            elif ' ? ' in arg and ' : ' in arg:
                jinja_ternary = self._convert_ternary_to_jinja(arg)
                parts.append(jinja_ternary)

            # Object/complex expression - wrap in Jinja
            else:
                parts.append(f'{{{{ {arg} }}}}')

        return ' '.join(parts)

    def _convert_ternary_to_jinja(self, ternary_expr: str) -> str:
        """Convert JavaScript ternary to Jinja.

        Example: selected ? 'bold' : 'normal' → {{ 'bold' if selected else 'normal' }}

        Args:
            ternary_expr: Ternary expression

        Returns:
            Jinja expression
        """
        import re

        # Pattern: condition ? true_value : false_value
        match = re.match(r'(.+?)\s*\?\s*(.+?)\s*:\s*(.+)$', ternary_expr)
        if not match:
            return f'{{{{ {ternary_expr} }}}}'

        condition = match.group(1).strip()
        true_val = match.group(2).strip()
        false_val = match.group(3).strip()

        # Remove quotes from string literals
        if (true_val.startswith("'") and true_val.endswith("'")) or (true_val.startswith('"') and true_val.endswith('"')):
            true_val = true_val
        if (false_val.startswith("'") and false_val.endswith("'")) or (false_val.startswith('"') and false_val.endswith('"')):
            false_val = false_val

        return f'{{{{ {true_val} if {condition} else {false_val} }}}}'

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

            # Apply name mappings to condition (e.g., items → list_items)
            if condition:
                condition = self._apply_name_mappings(condition)

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
                    # Use mapped name if the array name is a reserved word
                    safe_array_name = self._get_mapped_name(map_element.array_name)
                    lines.append(f"        {{% for {map_element.item_var} in {safe_array_name} %}}")
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
        has_condition = bool(element.condition)
        # Use mapped name if the array name is a reserved word
        safe_array_name = self._get_mapped_name(element.array_name)
        if has_condition:
            jinja_condition = self._convert_condition_to_jinja(element.condition)
            # Check if it's a negated condition
            if jinja_condition.startswith('not ('):
                # It's an elif case
                lines.append(f"{{% elif {safe_array_name} %}}")
            else:
                lines.append(f"{{% if {jinja_condition} %}}")

        # Generate the for-loop
        lines.append(f"        {{% for {element.item_var} in {safe_array_name} %}}")

        # Generate the nested component tag
        component_tag = self._generate_nested_component_tag(element)
        lines.append(f"            {component_tag}")

        lines.append("        {% endfor %}")

        # Add children fallback if add_children_support is enabled and there's a condition
        if has_condition and self.add_children_support:
            # Check if children attribute exists
            has_children = any(attr.name == 'children' for attr in attributes)
            if has_children:
                lines.append("        {% elif children %}")
                lines.append("        {{ children | safe }}")
                lines.append("        {% endif %}")

        return '\n'.join(lines)

    def _generate_nested_component_tag(self, element) -> str:
        """Generate nested component tag with attributes.

        Args:
            element: ContentElement with component info

        Returns:
            Component tag string like <c-component-name attr="value"></c-component-name>
            or raw HTML like <option value="...">content</option>
        """
        # Check if this is an HTML element (lowercase name) vs React Component (PascalCase)
        is_html_element = element.component_name and element.component_name[0].islower()

        # Find the component metadata
        component_meta = None
        for comp in self.nested_components:
            if comp['component_class'] == element.component_name:
                component_meta = comp
                break

        if is_html_element:
            # Raw HTML element like option, div, span, etc.
            tag_name = element.component_name
        elif not component_meta:
            # Fallback: convert component name to tag
            tag_name = self._to_kebab_case(element.component_name)
            tag_name = f'c-{tag_name}'
        else:
            tag_name = component_meta['tag_name']

        # Build attributes
        attrs = []
        children_content = None

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
                # Skip special props
                if prop_name == '_children':
                    children_content = prop_value
                    continue
                # Skip React-specific props like 'key'
                if prop_name == 'key':
                    continue

                # Skip event handlers (onClick, onChange, etc.) - these are JavaScript callbacks
                if prop_name.startswith('on') and prop_name[2:3].isupper():
                    continue

                # Convert prop value to Jinja
                jinja_value = self._convert_prop_value_to_jinja(prop_value, element)
                attrs.append(f'{prop_name}="{{{{ {jinja_value} }}}}"')

        # Build the tag
        if is_html_element:
            # For HTML elements, use simpler single-line format
            attr_str = ' '.join(attrs) if attrs else ''
            opening = f'<{tag_name} {attr_str}>' if attr_str else f'<{tag_name}>'

            if children_content:
                return f'{opening}{{{{ {children_content} }}}}</{tag_name}>'
            else:
                return f'{opening}</{tag_name}>'
        else:
            # For component tags, use multi-line format
            if attrs:
                attr_str = '\n                '.join(attrs)
                opening = f'<{tag_name}\n                {attr_str}\n            >'
            else:
                opening = f'<{tag_name}>'

            if children_content:
                return f'{opening}{{{{ {children_content} }}}}</{tag_name}>'
            else:
                return f'{opening}</{tag_name}>'

    def _convert_prop_value_to_jinja(self, prop_value: str, element) -> str:
        """Convert a React prop value expression to Jinja.

        Handles:
        - Loop index comparisons: currentTab === index → loop.index0 == activeTab
        - State variables: currentTab → activeTab (maps useState state to prop)
        - Item variable references: tab.label → tab.label (unchanged)
        - JavaScript operators: === → ==, !== → !=

        Args:
            prop_value: React prop value expression
            element: ContentElement with loop context (item_var, etc.)

        Returns:
            Jinja-compatible expression
        """
        import re

        # Check if this contains 'index' variable (from .map((item, index) =>))
        # Pattern: someVar === index or index === someVar
        index_comparison = re.search(r'(\w+)\s*===\s*index|index\s*===\s*(\w+)', prop_value)
        if index_comparison:
            # Extract the variable being compared to index
            var_name = index_comparison.group(1) or index_comparison.group(2)

            # Map common state variables to their prop equivalents
            # currentTab (state) → activeTab (prop)
            state_to_prop = {
                'currentTab': 'activeTab',
                'currentStep': 'activeStep',
                'currentPage': 'activePage',
            }

            var_name = state_to_prop.get(var_name, var_name)

            # Convert to Jinja: loop.index0 == varName
            # (loop.index0 is 0-based, matching JavaScript's behavior)
            converted = f'loop.index0 == {var_name}'
            return converted

        # Replace JavaScript operators with Jinja equivalents
        jinja_value = prop_value.replace(' === ', ' == ').replace(' !== ', ' != ')

        # Replace item variable references if needed
        if hasattr(element, 'item_var') and element.item_var:
            # Keep item_var references as-is (they're already correct for Jinja)
            pass

        return jinja_value

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

    def _generate_composition_template(self, nested_components: List[Dict], default_args: Dict[str, Any], content_elements: List) -> str:
        """Generate template for composition components.

        Composition components are wrappers that have no own attributes,
        they just pass props through to nested components.

        Args:
            nested_components: List of nested component metadata
            default_args: Default values
            content_elements: Content elements from JSX parsing

        Returns:
            Generated Jinja template
        """
        lines = []

        # Header
        lines.append(self._generate_header())
        lines.append("{# This is a composition component that wraps nested components #}")
        lines.append("")

        # Collect all unique props from nested components
        all_props = set()
        for comp in nested_components:
            all_props.update(comp.get('props', []))

        # Generate variables for all props
        for prop_name in sorted(all_props):
            # Skip children as it's handled specially
            if prop_name == 'children':
                continue

            # Get default from default_args if available
            default = default_args.get(prop_name)
            if default is not None:
                if isinstance(default, bool):
                    default_str = "true" if default else "false"
                elif isinstance(default, str):
                    default_str = f"'{default}'"
                else:
                    default_str = str(default)
                # Use .get(key, default) for consistency - more reliable than | default filter
                lines.append(f"{{% set {prop_name} = _component_context.get('{prop_name}', {default_str}) %}}")
            else:
                lines.append(f"{{% set {prop_name} = _component_context.get('{prop_name}') %}}")

        lines.append("")

        # Generate content from content elements
        # For composition components, this should render the nested component structure
        if content_elements:
            content = self._generate_composition_content(content_elements, nested_components)
            lines.append(content)
        else:
            lines.append("{# TODO_CONVERSION: No content elements found for composition component #}")

        return '\n'.join(lines)

    def _generate_composition_content(self, content_elements: List, nested_components: List[Dict]) -> str:
        """Generate content for composition component from content elements.

        This handles the special case where the JSX shows nested component usage
        like <Field {...fieldArgs}><Select {...selectArgs} /></Field>

        Args:
            content_elements: Content elements from JSX parsing
            nested_components: Nested component metadata

        Returns:
            Generated Jinja content with nested component tags
        """
        # For now, generate a simple nested structure based on nested_components
        # This is a simplified version - a full implementation would parse the actual JSX structure

        if len(nested_components) == 2:
            # Common pattern: outer and inner component (e.g., Field wrapping Select)
            outer_comp = nested_components[0]
            inner_comp = nested_components[1]

            outer_tag = outer_comp['tag_name']
            inner_tag = inner_comp['tag_name']

            # Generate attributes for outer component
            outer_props = outer_comp.get('props', [])
            outer_attrs = []
            for prop in outer_props:
                if prop not in ['children', 'className']:
                    outer_attrs.append(f'{prop}="{{{{ {prop} }}}}"')

            # Generate attributes for inner component
            inner_props = inner_comp.get('props', [])
            inner_attrs = []
            for prop in inner_props:
                if prop not in ['children', 'className']:
                    inner_attrs.append(f'{prop}="{{{{ {prop} }}}}"')

            # Build nested structure
            lines = [f"<{outer_tag}"]
            for attr in outer_attrs:
                lines.append(f"    {attr}")
            lines.append("    {{ attrs.render_extra_attributes(_component_context) }}>")

            lines.append(f"    <{inner_tag}")
            for attr in inner_attrs:
                lines.append(f"        {attr}")
            lines.append(f"    ></{inner_tag}>")

            lines.append(f"</{outer_tag}>")

            return '\n'.join(lines)

        # Fallback: just list the components as placeholders
        lines = [f"{{{{% TODO_CONVERSION: Render composition with {len(nested_components)} nested components %}}}}"]
        return '\n'.join(lines)
