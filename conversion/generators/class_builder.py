"""Build CSS class logic for Jinja templates."""

from typing import List, Dict, Any, Optional


class ClassBuilder:
    """Builder for CSS class conditionals in Jinja."""

    def __init__(self):
        self.class_conditionals: List[str] = []
        self.base_classes: List[str] = []

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

    def generate_jinja_code(self, array_var_name: str = 'css_classes') -> str:
        """Generate Jinja template code for class building.

        Args:
            array_var_name: Name of the Jinja array variable

        Returns:
            Jinja template code as string
        """
        lines = []

        # Initialize array with base classes
        if self.base_classes:
            classes_str = ', '.join(f"'{c}'" for c in self.base_classes)
            lines.append(f"{{% set {array_var_name} = [{classes_str}] %}}")
        else:
            lines.append(f"{{% set {array_var_name} = [] %}}")

        # Add conditional classes
        for item in self.class_conditionals:
            class_name = item['class']
            condition = item['condition']
            lines.append(
                f"{{% if {condition} %}}{{% set {array_var_name} = {array_var_name} + ['{class_name}'] %}}{{% endif %}}"
            )

        return '\n'.join(lines)

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
