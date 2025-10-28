"""Parse actual default values from React component function signatures.

This parser distinguishes between:
- Real defaults: Values used in component destructuring (e.g., legend = defaultArgs.legend)
- Example values: Values only in defaultArgs but not used in destructuring
"""

import re
from typing import Dict, Any, Optional, Tuple


class ComponentDefaultsParser:
    """Parser for extracting actual default values from component functions."""

    def __init__(self):
        self.actual_defaults: Dict[str, Any] = {}
        self.example_values: Dict[str, Any] = {}

    def parse_component_function(self, content: str, component_name: str, defaultargs_values: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Parse component function to extract actual defaults.

        Args:
            content: File content (template.tsx)
            component_name: Name of the component (e.g., 'Fieldset')
            defaultargs_values: Values from defaultArgs.ts

        Returns:
            Tuple of (actual_defaults, example_values)
        """
        # Find the component function
        # Pattern: export const ComponentName: React.FC<Props> = ({...}) => {
        # Or: export const ComponentName = ({...}) => {
        pattern = rf'export\s+const\s+{component_name}\s*[^=]*=\s*\(\s*\{{([^}}]+)\}}'
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            # Try alternative pattern without export
            pattern = rf'const\s+{component_name}\s*[^=]*=\s*\(\s*\{{([^}}]+)\}}'
            match = re.search(pattern, content, re.DOTALL)

        if not match:
            # Couldn't find component function - all defaultArgs are examples
            self.example_values = defaultargs_values.copy()
            return {}, defaultargs_values

        # Extract destructuring parameters
        params_str = match.group(1)

        # Parse each parameter
        self.actual_defaults = {}
        params_with_defaults = set()

        for param in self._parse_destructuring_params(params_str):
            param_name, default_expr = param
            params_with_defaults.add(param_name)

            if default_expr:
                # Has a default in destructuring
                # Check if it references defaultArgs
                if 'defaultArgs.' in default_expr:
                    # Extract the value from defaultArgs
                    ref_name = default_expr.replace('defaultArgs.', '').strip()
                    if ref_name in defaultargs_values:
                        self.actual_defaults[param_name] = defaultargs_values[ref_name]
                else:
                    # Direct default value (e.g., disabled = false)
                    self.actual_defaults[param_name] = self._parse_inline_default(default_expr)

        # Values in defaultArgs but not in destructuring are examples
        self.example_values = {
            key: val for key, val in defaultargs_values.items()
            if key not in params_with_defaults
        }

        return self.actual_defaults, self.example_values

    def _parse_destructuring_params(self, params_str: str) -> list[Tuple[str, Optional[str]]]:
        """Parse destructuring parameters.

        Args:
            params_str: Content inside { } from destructuring

        Returns:
            List of (param_name, default_expression) tuples
        """
        results = []

        # Split by comma, but be careful with nested structures
        lines = params_str.split('\n')

        for line in lines:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('//') or line.startswith('/*'):
                continue

            # Remove trailing comma
            if line.endswith(','):
                line = line[:-1].strip()

            # Check if parameter has a default: param = default
            if '=' in line:
                parts = line.split('=', 1)
                param_name = parts[0].strip()
                default_expr = parts[1].strip()
                results.append((param_name, default_expr))
            else:
                # No default
                param_name = line.strip()
                if param_name:  # Skip empty
                    results.append((param_name, None))

        return results

    def _parse_inline_default(self, expr: str) -> Any:
        """Parse an inline default expression.

        Args:
            expr: Expression like 'false', 'true', "'text'", etc.

        Returns:
            Parsed Python value
        """
        expr = expr.strip()

        # Boolean
        if expr == 'true':
            return True
        if expr == 'false':
            return False

        # Null/undefined
        if expr in ('null', 'undefined'):
            return None

        # String
        if (expr.startswith("'") and expr.endswith("'")) or \
           (expr.startswith('"') and expr.endswith('"')):
            return expr[1:-1]

        # Number
        try:
            if '.' in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            pass

        # Default: return as string
        return expr

    def is_example_value(self, name: str) -> bool:
        """Check if a value is only an example (not used in component).

        Args:
            name: Parameter name

        Returns:
            True if it's only an example value
        """
        return name in self.example_values

    def get_actual_default(self, name: str) -> Optional[Any]:
        """Get actual default value if it exists.

        Args:
            name: Parameter name

        Returns:
            Default value or None
        """
        return self.actual_defaults.get(name)
