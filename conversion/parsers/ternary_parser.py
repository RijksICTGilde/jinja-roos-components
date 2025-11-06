"""Parse ternary expressions in JSX props to extract conditional class mappings."""

import re
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class TernaryMapping:
    """Mapping extracted from a ternary expression."""
    prop_name: str  # Prop being set (e.g., 'hint')
    condition: str  # Condition expression (e.g., "kind === 'warning' || kind === 'warning-subtle'")
    true_value: str  # Value when true (e.g., 'warning')
    false_value: Optional[str]  # Value when false (e.g., 'undefined' or None)


class TernaryParser:
    """Parser for ternary expressions in JSX props."""

    def extract_from_base_props(self, props: dict) -> List[TernaryMapping]:
        """Extract ternary mappings from base component props.

        Args:
            props: Dictionary of prop_name -> prop_value

        Returns:
            List of TernaryMapping objects
        """
        mappings = []

        for prop_name, prop_value in props.items():
            if isinstance(prop_value, str) and '?' in prop_value:
                mapping = self._parse_ternary(prop_name, prop_value)
                if mapping:
                    mappings.append(mapping)

        return mappings

    def _parse_ternary(self, prop_name: str, expression: str) -> Optional[TernaryMapping]:
        """Parse a ternary expression.

        Args:
            prop_name: Name of the prop
            expression: Ternary expression like "condition ? true_val : false_val"

        Returns:
            TernaryMapping or None if not a valid ternary
        """
        # Pattern: condition ? true_value : false_value
        pattern = r'^(.+?)\s*\?\s*(.+?)\s*:\s*(.+?)$'
        match = re.match(pattern, expression.strip())

        if not match:
            return None

        condition = match.group(1).strip()
        true_value = match.group(2).strip().strip('\'"')
        false_value = match.group(3).strip()

        # Treat 'undefined' as None
        if false_value == 'undefined':
            false_value = None

        return TernaryMapping(
            prop_name=prop_name,
            condition=condition,
            true_value=true_value,
            false_value=false_value
        )

    def to_jinja_conditionals(self, mapping: TernaryMapping, name_mappings: dict = None) -> List[str]:
        """Convert a ternary mapping to Jinja conditionals.

        Args:
            mapping: TernaryMapping object
            name_mappings: Optional dict mapping original names to safe names

        Returns:
            List of Jinja conditional strings
        """
        name_mappings = name_mappings or {}
        jinja_lines = []

        # Convert JS condition to Jinja
        jinja_condition = self._convert_condition_to_jinja(mapping.condition, name_mappings)

        jinja_lines.append(f"{{% if {jinja_condition} %}}")
        jinja_lines.append(f"    {{% set {mapping.prop_name} = '{mapping.true_value}' %}}")
        if mapping.false_value:
            jinja_lines.append("{% else %}")
            jinja_lines.append(f"    {{% set {mapping.prop_name} = '{mapping.false_value}' %}}")
        jinja_lines.append("{% endif %}")

        return jinja_lines

    def _convert_condition_to_jinja(self, condition: str, name_mappings: dict) -> str:
        """Convert JavaScript condition to Jinja condition.

        Args:
            condition: JS condition
            name_mappings: Dict mapping original names to safe names

        Returns:
            Jinja condition
        """
        # Replace === with ==
        jinja_cond = condition.replace(' === ', ' == ')
        # Replace !== with !=
        jinja_cond = jinja_cond.replace(' !== ', ' != ')
        # Replace || with or
        jinja_cond = jinja_cond.replace(' || ', ' or ')
        # Replace && with and
        jinja_cond = jinja_cond.replace(' && ', ' and ')

        # Apply name mappings
        for original, mapped in sorted(name_mappings.items(), key=lambda x: len(x[0]), reverse=True):
            jinja_cond = re.sub(r'\b' + re.escape(original) + r'\b', mapped, jinja_cond)

        return jinja_cond
