"""Parse switch statements to extract prop mappings."""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SwitchCase:
    """A single case in a switch statement."""
    values: List[str]  # Case values (can have multiple for fall-through)
    result: str  # What it resolves to


@dataclass
class SwitchMapping:
    """Mapping extracted from a switch statement."""
    switch_var: str  # Variable being switched on (e.g., 'kind')
    result_var: str  # Variable being assigned (e.g., 'appearance')
    cases: List[SwitchCase]


class SwitchParser:
    """Parser for switch statements in TypeScript/JavaScript."""

    def __init__(self):
        self.mappings: List[SwitchMapping] = []

    def extract_from_source(self, content: str) -> List[SwitchMapping]:
        """Extract switch mappings from source code.

        Args:
            content: Source code content

        Returns:
            List of SwitchMapping objects
        """
        self.mappings = []

        # Find switch statements
        # Pattern: let varname = undefined; switch (switchvar) { ... }
        pattern = r'let\s+(\w+)(?:\s*:\s*\w+(?:\s*\|\s*\w+)*)?\s*(?:=\s*undefined)?\s*;\s*switch\s*\((\w+)\)\s*\{'

        for match in re.finditer(pattern, content, re.MULTILINE):
            result_var = match.group(1)
            switch_var = match.group(2)

            # Extract the switch body
            switch_start = match.end()
            switch_body = self._extract_switch_body(content[switch_start:])

            if switch_body:
                cases = self._parse_switch_cases(switch_body, result_var)
                if cases:
                    self.mappings.append(SwitchMapping(
                        switch_var=switch_var,
                        result_var=result_var,
                        cases=cases
                    ))

        return self.mappings

    def _extract_switch_body(self, content: str) -> str:
        """Extract switch statement body.

        Args:
            content: Content starting after 'switch (var) {'

        Returns:
            Switch body content
        """
        brace_count = 1
        result = []

        for char in content:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    break
            result.append(char)

        return ''.join(result)

    def _parse_switch_cases(self, switch_body: str, result_var: str) -> List[SwitchCase]:
        """Parse cases from switch body.

        Args:
            switch_body: Switch statement body
            result_var: Variable being assigned

        Returns:
            List of SwitchCase objects
        """
        cases = []
        current_case_values = []

        lines = switch_body.split('\n')

        for line in lines:
            line = line.strip()

            # Match case statement: case 'value':
            case_match = re.match(r"case\s+['\"]([^'\"]+)['\"]:\s*$", line)
            if case_match:
                current_case_values.append(case_match.group(1))
                continue

            # Match assignment: varname = 'value';
            assign_match = re.match(rf"{result_var}\s*=\s*['\"]([^'\"]+)['\"];", line)
            if assign_match:
                result_value = assign_match.group(1)
                if current_case_values:
                    cases.append(SwitchCase(
                        values=current_case_values.copy(),
                        result=result_value
                    ))
                    current_case_values = []
                continue

            # Match break
            if line == 'break;':
                continue

        return cases

    def to_class_mappings(self, base_resolver, library: str, component: str, base_classes: List[str] = None) -> List:
        """Convert switch mappings to class mappings using base resolver.

        Args:
            base_resolver: BaseComponentResolver instance
            library: Component library (e.g., '@utrecht/component-library-react')
            component: Component name (e.g., 'Button')
            base_classes: Optional list of base classes to filter out

        Returns:
            List of class mapping objects
        """
        from .clsx_parser import ClassMapping

        if base_classes is None:
            base_classes = []

        class_mappings = []

        for switch_mapping in self.mappings:
            # For each case, resolve through the base component
            for case in switch_mapping.cases:
                # Build props dict with the result value
                props = {switch_mapping.result_var: case.result}

                # Resolve to get CSS classes
                resolution = base_resolver.resolve(library, component, props)

                if resolution and resolution.get('css_classes'):
                    # Create class mappings for each value that maps to this result
                    for value in case.values:
                        for css_class in resolution['css_classes']:
                            # Skip base classes and html tags
                            if css_class in base_classes or css_class == resolution.get('html_tag', ''):
                                continue

                            class_mappings.append(ClassMapping(
                                prop_name=switch_mapping.switch_var,
                                value=value,
                                css_class=css_class,
                                condition=f"{switch_mapping.switch_var} == '{value}'"
                            ))

        return class_mappings

    def to_jinja_conditionals(self, switch_mapping: SwitchMapping) -> List[str]:
        """Convert a switch mapping to Jinja conditionals.

        Args:
            switch_mapping: SwitchMapping object

        Returns:
            List of Jinja conditional strings
        """
        jinja_lines = []

        for i, case in enumerate(switch_mapping.cases):
            # Build condition for multiple values (OR)
            conditions = [f"{switch_mapping.switch_var} == '{val}'" for val in case.values]
            condition = ' or '.join(conditions)

            if i == 0:
                jinja_lines.append(f"{{% if {condition} %}}")
            else:
                jinja_lines.append(f"{{% elif {condition} %}}")

            jinja_lines.append(f"    {{% set {switch_mapping.result_var} = '{case.result}' %}}")

        if jinja_lines:
            jinja_lines.append("{% endif %}")

        return jinja_lines
