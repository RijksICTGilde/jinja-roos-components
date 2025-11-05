"""Build CSS class logic for Jinja templates."""

from typing import List, Dict, Any, Optional


class ClassBuilder:
    """Builder for CSS class conditionals in Jinja."""

    def __init__(self):
        self.class_conditionals: List[str] = []
        self.base_classes: List[str] = []
        self.template_classes: List[Dict[str, Any]] = []  # Classes with variable interpolation
        self.computed_vars: List[Dict[str, str]] = []  # Computed variables (ternary, switch, etc.)

    def add_base_classes(self, classes: List[str]) -> None:
        """Add base CSS classes (always applied).

        Args:
            classes: List of base class names
        """
        # Avoid duplicates
        for cls in classes:
            if cls not in self.base_classes:
                self.base_classes.append(cls)

    def add_conditional_class(self, class_name: str, condition: str) -> None:
        """Add a conditional CSS class.

        Args:
            class_name: CSS class name
            condition: Jinja condition (e.g., "kind == 'primary'")
        """
        self.class_conditionals.append({
            'class': class_name,
            'condition': condition
        })

    def add_enum_classes(self, var_name: str, value_map: Dict[str, List[str]]) -> None:
        """Add classes based on enum values.

        Args:
            var_name: Variable name (e.g., 'kind')
            value_map: Dict mapping values to class lists
        """
        for value, classes in value_map.items():
            condition = f"{var_name} == '{value}'"
            for class_name in classes:
                self.add_conditional_class(class_name, condition)

    def add_boolean_class(self, var_name: str, class_name: str, negate: bool = False) -> None:
        """Add class based on boolean variable.

        Args:
            var_name: Variable name (e.g., 'disabled')
            class_name: CSS class to add
            negate: If True, add class when variable is False
        """
        if negate:
            condition = f"not {var_name}"
        else:
            condition = var_name

        self.add_conditional_class(class_name, condition)

    def add_template_class(self, template_pattern: str, condition: Optional[str] = None) -> None:
        """Add a class with variable interpolation.

        Args:
            template_pattern: Class pattern with ${var} placeholders (e.g., 'class--${state}')
            condition: Optional condition (None means always include)
        """
        self.template_classes.append({
            'template': template_pattern,
            'condition': condition
        })

    def add_computed_var(self, var_name: str, expression: str) -> None:
        """Add a computed variable (from ternary or switch).

        Args:
            var_name: Variable name to assign
            expression: Jinja expression to compute the value
        """
        self.computed_vars.append({
            'name': var_name,
            'expression': expression
        })

    def add_size_classes(self, var_name: str = 'size', prefix: str = '', suffix: str = '') -> None:
        """Add size-based classes (common pattern).

        Args:
            var_name: Variable name (default: 'size')
            prefix: Class name prefix
            suffix: Class name suffix
        """
        # Common sizes
        sizes = ['xs', 'sm', 'md', 'lg', 'xl']

        for size in sizes:
            class_name = f"{prefix}{size}{suffix}".strip('-')
            condition = f"{var_name} == '{size}'"
            self.add_conditional_class(class_name, condition)

    def generate_jinja_code(self, array_var_name: str = 'css_classes', name_mappings: dict = None) -> str:
        """Generate Jinja template code for class building.

        Args:
            array_var_name: Name of the Jinja array variable
            name_mappings: Optional dict mapping original names to safe names (for reserved words)

        Returns:
            Jinja template code as string
        """
        name_mappings = name_mappings or {}
        lines = []

        # Generate computed variables first
        for comp_var in self.computed_vars:
            lines.append(f"{{% set {comp_var['name']} = {comp_var['expression']} %}}")

        # Initialize array with base classes
        if self.base_classes:
            classes_str = ', '.join(f"'{c}'" for c in self.base_classes)
            lines.append(f"{{% set {array_var_name} = [{classes_str}] %}}")
        else:
            lines.append(f"{{% set {array_var_name} = [] %}}")

        # Add template classes (with variable interpolation)
        for tpl_class in self.template_classes:
            template = tpl_class['template']
            condition = tpl_class['condition']

            # Convert ${var} to Jinja {{var}} syntax and build class string
            jinja_class = self._convert_template_to_jinja(template, name_mappings)

            if condition and condition != '__ALWAYS__':
                # Convert React condition to Jinja
                jinja_condition = self._convert_condition_to_jinja(condition, name_mappings)
                lines.append(f"{{% if {jinja_condition} %}}")
                lines.append(f"    {{% set {array_var_name} = {array_var_name} + [{jinja_class}] %}}")
                lines.append("{% endif %}")
            else:
                # Always include
                lines.append(f"{{% set {array_var_name} = {array_var_name} + [{jinja_class}] %}}")

        # Add conditional classes
        for item in self.class_conditionals:
            class_name = item['class']
            condition = item['condition']
            # Apply name mappings to condition
            mapped_condition = self._apply_name_mappings(condition, name_mappings)
            lines.append(
                f"{{% if {mapped_condition} %}}{{% set {array_var_name} = {array_var_name} + ['{class_name}'] %}}{{% endif %}}"
            )

        return '\n'.join(lines)

    def _apply_name_mappings(self, text: str, name_mappings: dict) -> str:
        """Apply name mappings to variable names in text.

        Args:
            text: Text containing variable names
            name_mappings: Dict mapping original names to safe names

        Returns:
            Text with mapped variable names
        """
        import re
        result = text
        # Sort by length descending to avoid partial matches
        for original, mapped in sorted(name_mappings.items(), key=lambda x: len(x[0]), reverse=True):
            # Match whole words only
            result = re.sub(r'\b' + re.escape(original) + r'\b', mapped, result)
        return result

    def _convert_template_to_jinja(self, template: str, name_mappings: dict = None) -> str:
        """Convert React template literal to Jinja string concatenation.

        Args:
            template: Template like 'class--${var}'
            name_mappings: Optional dict mapping original names to safe names

        Returns:
            Jinja expression like "'class--' + var"
        """
        import re
        name_mappings = name_mappings or {}

        # Find all ${...} expressions
        parts = []
        last_end = 0

        for match in re.finditer(r'\$\{([^}]+)\}', template):
            # Add the literal part before this expression
            if match.start() > last_end:
                literal = template[last_end:match.start()]
                if literal:
                    parts.append(f"'{literal}'")

            # Add the variable expression (convert ternary if needed)
            var_expr = match.group(1)
            converted_expr = self._convert_ternary_to_jinja(var_expr, name_mappings)
            parts.append(converted_expr)

            last_end = match.end()

        # Add any remaining literal part
        if last_end < len(template):
            literal = template[last_end:]
            if literal:
                parts.append(f"'{literal}'")

        # Join with +
        if len(parts) == 1:
            return parts[0]
        return ' + '.join(parts)

    def _convert_condition_to_jinja(self, condition: str, name_mappings: dict = None) -> str:
        """Convert React condition to Jinja condition.

        Args:
            condition: React condition
            name_mappings: Optional dict mapping original names to safe names

        Returns:
            Jinja condition
        """
        name_mappings = name_mappings or {}
        # Replace !== with !=
        jinja_cond = condition.replace(' !== ', ' != ')
        # Replace === with ==
        jinja_cond = jinja_cond.replace(' === ', ' == ')
        # Apply name mappings
        jinja_cond = self._apply_name_mappings(jinja_cond, name_mappings)
        return jinja_cond

    def _convert_ternary_to_jinja(self, expr: str, name_mappings: dict = None) -> str:
        """Convert JavaScript ternary expression to Jinja conditional expression.

        Args:
            expr: Expression like "line !== 'substep-start' ? size : 'md'"
            name_mappings: Optional dict mapping original names to safe names

        Returns:
            Jinja expression like "('md' if line == 'substep-start' else size)"
        """
        import re
        name_mappings = name_mappings or {}

        # Check if expression contains ternary operator
        if '?' not in expr or ':' not in expr:
            # No ternary, apply name mappings and return
            return self._apply_name_mappings(expr, name_mappings)

        # Parse ternary: condition ? trueVal : falseVal
        # Split on ? first
        parts = expr.split('?')
        if len(parts) != 2:
            return expr  # Invalid ternary, return as-is

        condition = parts[0].strip()
        value_parts = parts[1].split(':')
        if len(value_parts) != 2:
            return expr  # Invalid ternary, return as-is

        true_val = value_parts[0].strip()
        false_val = value_parts[1].strip()

        # Convert condition to Jinja syntax (with name mappings)
        jinja_condition = self._convert_condition_to_jinja(condition, name_mappings)

        # Apply name mappings to values
        true_val = self._apply_name_mappings(true_val, name_mappings)
        false_val = self._apply_name_mappings(false_val, name_mappings)

        # Handle !== by flipping the condition
        if ' !== ' in condition:
            # For !== we need to flip: "a !== b ? x : y" becomes "(y if a == b else x)"
            jinja_condition = jinja_condition.replace(' != ', ' == ')
            return f"({false_val} if {jinja_condition} else {true_val})"
        else:
            # Normal condition: "a === b ? x : y" becomes "(x if a == b else y)"
            return f"({true_val} if {jinja_condition} else {false_val})"

    def generate_compact_jinja(self, array_var_name: str = 'css_classes') -> str:
        """Generate more compact Jinja code (one-liners where possible).

        Args:
            array_var_name: Name of the Jinja array variable

        Returns:
            Compact Jinja template code
        """
        lines = []

        # Base classes
        if self.base_classes:
            classes_str = ', '.join(f"'{c}'" for c in self.base_classes)
            lines.append(f"{{% set {array_var_name} = [{classes_str}] %}}")
        else:
            lines.append(f"{{% set {array_var_name} = [] %}}")

        # Group conditionals by similar patterns
        grouped = self._group_conditionals()

        for group in grouped:
            if group['type'] == 'single':
                # Single conditional
                item = group['items'][0]
                lines.append(
                    f"{{% if {item['condition']} %}}{{% set {array_var_name} = {array_var_name} + ['{item['class']}'] %}}{{% endif %}}"
                )
            elif group['type'] == 'enum':
                # Enum-based (if/elif chain)
                var_name = group['var_name']
                first = True
                for item in group['items']:
                    value = item['value']
                    class_name = item['class']

                    if first:
                        lines.append(f"{{% if {var_name} == '{value}' %}}")
                        first = False
                    else:
                        lines.append(f"{{% elif {var_name} == '{value}' %}}")

                    lines.append(f"    {{% set {array_var_name} = {array_var_name} + ['{class_name}'] %}}")

                lines.append("{% endif %}")

        return '\n'.join(lines)

    def _group_conditionals(self) -> List[Dict[str, Any]]:
        """Group conditionals by pattern for more compact output.

        Returns:
            List of grouped conditionals
        """
        groups = []
        enum_groups: Dict[str, List[Dict]] = {}

        for item in self.class_conditionals:
            condition = item['condition']

            # Check if it's an enum pattern (var == 'value')
            if " == '" in condition and condition.count('==') == 1:
                var_name = condition.split(" == ")[0].strip()
                value = condition.split(" == ")[1].strip().strip("'\"")

                if var_name not in enum_groups:
                    enum_groups[var_name] = []

                enum_groups[var_name].append({
                    'value': value,
                    'class': item['class']
                })
            else:
                # Single conditional
                groups.append({
                    'type': 'single',
                    'items': [item]
                })

        # Add enum groups
        for var_name, items in enum_groups.items():
            if len(items) > 1:
                groups.append({
                    'type': 'enum',
                    'var_name': var_name,
                    'items': items
                })
            else:
                groups.append({
                    'type': 'single',
                    'items': [{
                        'class': items[0]['class'],
                        'condition': f"{var_name} == '{items[0]['value']}'"
                    }]
                })

        return groups

    def reset(self) -> None:
        """Reset the builder state."""
        self.class_conditionals = []
        self.base_classes = []
