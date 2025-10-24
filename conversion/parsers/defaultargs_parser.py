"""Parse defaultArgs from React component files."""

import re
from typing import Dict, Any, Optional
from ..utils.ast_helpers import extract_string_literal


class DefaultArgsParser:
    """Parser for defaultArgs.ts files."""

    def __init__(self):
        self.defaults: Dict[str, Any] = {}

    def parse_file(self, content: str) -> Dict[str, Any]:
        """Parse default arguments from file content.

        Args:
            content: File content as string

        Returns:
            Dictionary mapping property names to default values
        """
        # Find the defaultArgs object
        # Pattern: export const defaultArgs: IButtonProps = { ... }
        pattern = r'export\s+const\s+defaultArgs[^=]*=\s*\{'
        match = re.search(pattern, content)

        if not match:
            return {}

        # Extract the object content
        start = match.end() - 1  # Include the opening brace
        obj_content = self._extract_object(content[start:])

        # Parse the object content
        self.defaults = self._parse_object_content(obj_content)
        return self.defaults

    def _extract_object(self, content: str) -> str:
        """Extract object literal content between braces.

        Args:
            content: Content starting with '{'

        Returns:
            Object content including braces
        """
        brace_count = 0
        result = []

        for char in content:
            result.append(char)
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    break

        return ''.join(result)

    def _parse_object_content(self, obj_str: str) -> Dict[str, Any]:
        """Parse object literal content to extract key-value pairs.

        Args:
            obj_str: Object literal as string

        Returns:
            Dictionary of parsed values
        """
        result = {}

        # Remove outer braces and split by lines
        obj_str = obj_str.strip()[1:-1]  # Remove { and }
        lines = obj_str.split('\n')

        for line in lines:
            line = line.strip()

            # Skip empty lines, comments, and closing braces
            if not line or line.startswith('//') or line.startswith('/*'):
                continue

            # Remove trailing comma
            if line.endswith(','):
                line = line[:-1].strip()

            # Parse key: value pairs
            parsed = self._parse_property_line(line)
            if parsed:
                key, value = parsed
                result[key] = value

        return result

    def _parse_property_line(self, line: str) -> Optional[tuple[str, Any]]:
        """Parse a single property line.

        Args:
            line: Line like "kind: 'primary'" or "disabled: false"

        Returns:
            Tuple of (key, value) or None
        """
        # Match pattern: key: value
        match = re.match(r'^(\w+)\s*:\s*(.+)$', line)
        if not match:
            return None

        key = match.group(1)
        value_str = match.group(2).strip()

        # Remove trailing comma
        if value_str.endswith(','):
            value_str = value_str[:-1].strip()

        # Parse the value
        value = self._parse_value(value_str)
        return key, value

    def _parse_value(self, value_str: str) -> Any:
        """Parse a JavaScript/TypeScript value to Python value.

        Args:
            value_str: Value as string

        Returns:
            Parsed Python value
        """
        value_str = value_str.strip()

        # String literals
        string_val = extract_string_literal(value_str)
        if string_val is not None:
            return string_val

        # Boolean values
        if value_str == 'true':
            return True
        if value_str == 'false':
            return False

        # Null/undefined
        if value_str in ('null', 'undefined'):
            return None

        # Numbers
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass

        # Arrays (simple parsing)
        if value_str.startswith('[') and value_str.endswith(']'):
            arr_content = value_str[1:-1].strip()
            if not arr_content:
                return []
            # Simple comma-separated values
            items = [self._parse_value(item.strip()) for item in arr_content.split(',')]
            return items

        # Objects (return as string for now - can be enhanced)
        if value_str.startswith('{'):
            return value_str

        # Default: return as string
        return value_str

    def get_default(self, name: str, fallback: Any = None) -> Any:
        """Get default value for a property.

        Args:
            name: Property name
            fallback: Value to return if not found

        Returns:
            Default value or fallback
        """
        return self.defaults.get(name, fallback)

    def has_default(self, name: str) -> bool:
        """Check if property has a default value.

        Args:
            name: Property name

        Returns:
            True if default exists
        """
        return name in self.defaults
