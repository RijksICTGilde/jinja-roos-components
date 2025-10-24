"""Parse JSX attribute expressions to extract conditional logic."""

import re
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class JsxAttrMapping:
    """Mapping extracted from a JSX attribute expression."""
    attr_name: str  # e.g., 'hint'
    prop_name: str  # e.g., 'kind'
    condition: str  # e.g., "kind === 'warning' || kind === 'warning-subtle'"
    value: str  # e.g., 'warning'


class JsxAttrParser:
    """Parser for JSX attribute expressions."""

    def __init__(self):
        self.mappings: List[JsxAttrMapping] = []

    def extract_from_jsx(self, jsx_content: str) -> List[JsxAttrMapping]:
        """Extract attribute mappings from JSX.

        Args:
            jsx_content: JSX content string

        Returns:
            List of JsxAttrMapping objects
        """
        self.mappings = []

        # Find JSX attributes with ternary expressions
        # Pattern: attrname={condition ? 'value' : undefined}
        pattern = r'(\w+)=\{([^}]+\?[^}]+:[^}]+)\}'

        for match in re.finditer(pattern, jsx_content):
            attr_name = match.group(1)
            expression = match.group(2).strip()

            # Parse ternary expression
            mapping = self._parse_ternary(attr_name, expression)
            if mapping:
                self.mappings.append(mapping)

        return self.mappings

    def _parse_ternary(self, attr_name: str, expression: str) -> Optional[JsxAttrMapping]:
        """Parse a ternary expression.

        Args:
            attr_name: Attribute name
            expression: Ternary expression like "kind === 'warning' ? 'warning' : undefined"

        Returns:
            JsxAttrMapping or None
        """
        # Pattern: condition ? value : else_value
        parts = expression.split('?')
        if len(parts) != 2:
            return None

        condition = parts[0].strip()
        value_parts = parts[1].split(':')
        if len(value_parts) != 2:
            return None

        true_value = value_parts[0].strip().strip("'\"")
        false_value = value_parts[1].strip()

        # Only handle cases where false value is undefined/null
        if false_value not in ('undefined', 'null'):
            return None

        # Extract prop name from condition
        prop_name = self._extract_prop_from_condition(condition)
        if not prop_name:
            return None

        return JsxAttrMapping(
            attr_name=attr_name,
            prop_name=prop_name,
            condition=condition,
            value=true_value
        )

    def _extract_prop_from_condition(self, condition: str) -> Optional[str]:
        """Extract primary prop name from condition.

        Args:
            condition: Condition like "kind === 'warning' || kind === 'warning-subtle'"

        Returns:
            Prop name or None
        """
        # Look for pattern: propname === 'value'
        match = re.search(r'(\w+)\s*===', condition)
        if match:
            return match.group(1)

        # Look for simple prop name
        match = re.search(r'^(\w+)$', condition.strip())
        if match:
            return match.group(1)

        return None

    def to_class_mappings(self, base_resolver, library: str, component: str, base_classes: List[str] = None):
        """Convert JSX attr mappings to class mappings using base resolver.

        Args:
            base_resolver: BaseComponentResolver instance
            library: Component library
            component: Component name
            base_classes: Optional base classes to filter

        Returns:
            List of ClassMapping objects
        """
        from .clsx_parser import ClassMapping

        if base_classes is None:
            base_classes = []

        class_mappings = []

        for jsx_mapping in self.mappings:
            # Build props dict with the attribute value
            props = {jsx_mapping.attr_name: jsx_mapping.value}

            # Resolve to get CSS classes
            resolution = base_resolver.resolve(library, component, props)

            if resolution and resolution.get('css_classes'):
                # Parse condition to extract prop values
                values = self._extract_values_from_condition(jsx_mapping.condition)

                for value in values:
                    for css_class in resolution['css_classes']:
                        # Skip base classes
                        if css_class in base_classes:
                            continue

                        class_mappings.append(ClassMapping(
                            prop_name=jsx_mapping.prop_name,
                            value=value,
                            css_class=css_class,
                            condition=f"{jsx_mapping.prop_name} == '{value}'"
                        ))

        return class_mappings

    def _extract_values_from_condition(self, condition: str) -> List[str]:
        """Extract prop values from condition.

        Args:
            condition: Condition like "kind === 'warning' || kind === 'warning-subtle'"

        Returns:
            List of values like ['warning', 'warning-subtle']
        """
        values = []

        # Find all === comparisons with string literals
        pattern = r"===\s*['\"]([^'\"]+)['\"]"
        for match in re.finditer(pattern, condition):
            values.append(match.group(1))

        return values
