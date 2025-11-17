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

        # Remove outer braces
        obj_str = obj_str.strip()[1:-1]  # Remove { and }

        # Parse line by line, handling multi-line values
        i = 0
        lines = obj_str.split('\n')

        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines, comments
            if not line or line.startswith('//') or line.startswith('/*'):
                i += 1
                continue

            # Check if this line starts a key: value pair
            key_match = re.match(r'^(\w+)\s*:\s*(.*)$', line)
            if key_match:
                key = key_match.group(1)
                value_start = key_match.group(2).strip()

                # Check if value is multi-line (array or object)
                if value_start.startswith('[') and not value_start.rstrip(',').endswith(']'):
                    # Multi-line array - collect until we find the closing ]
                    full_value = value_start
                    i += 1
                    bracket_count = value_start.count('[') - value_start.count(']')

                    while i < len(lines) and bracket_count > 0:
                        next_line = lines[i]
                        full_value += '\n' + next_line
                        bracket_count += next_line.count('[') - next_line.count(']')
                        i += 1

                    # Remove trailing comma
                    full_value = full_value.rstrip().rstrip(',')
                    result[key] = self._parse_value(full_value)
                    continue

                elif value_start.startswith('{') and not value_start.rstrip(',').endswith('}'):
                    # Multi-line object - collect until we find the closing }
                    full_value = value_start
                    i += 1
                    brace_count = value_start.count('{') - value_start.count('}')

                    while i < len(lines) and brace_count > 0:
                        next_line = lines[i]
                        full_value += '\n' + next_line
                        brace_count += next_line.count('{') - next_line.count('}')
                        i += 1

                    # Remove trailing comma
                    full_value = full_value.rstrip().rstrip(',')
                    result[key] = self._parse_value(full_value)
                    continue
                else:
                    # Single-line value
                    value = value_start.rstrip(',')
                    result[key] = self._parse_value(value)

            i += 1

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

        # Arrays
        if value_str.startswith('[') and value_str.endswith(']'):
            arr_content = value_str[1:-1].strip()
            if not arr_content:
                return []

            # Parse array items, handling nested objects and arrays
            items = []
            current_item = ''
            depth = 0  # Track nesting depth of {}, []

            for char in arr_content:
                if char in '{[':
                    depth += 1
                    current_item += char
                elif char in '}]':
                    depth -= 1
                    current_item += char
                elif char == ',' and depth == 0:
                    # Top-level comma - end of item
                    if current_item.strip():
                        items.append(self._parse_value(current_item.strip()))
                    current_item = ''
                else:
                    current_item += char

            # Don't forget the last item
            if current_item.strip():
                items.append(self._parse_value(current_item.strip()))

            return items

        # Objects - parse to dictionary
        if value_str.startswith('{') and value_str.endswith('}'):
            obj_content = value_str[1:-1].strip()
            if not obj_content:
                return {}

            # Parse object properties
            obj_dict = {}
            current_prop = ''
            depth = 0

            for char in obj_content:
                if char in '{[':
                    depth += 1
                    current_prop += char
                elif char in '}]':
                    depth -= 1
                    current_prop += char
                elif char == ',' and depth == 0:
                    # Top-level comma - end of property
                    if current_prop.strip():
                        prop_match = re.match(r'^\s*(\w+)\s*:\s*(.+)$', current_prop.strip())
                        if prop_match:
                            prop_name = prop_match.group(1)
                            prop_value = self._parse_value(prop_match.group(2).strip())
                            obj_dict[prop_name] = prop_value
                    current_prop = ''
                else:
                    current_prop += char

            # Don't forget the last property
            if current_prop.strip():
                prop_match = re.match(r'^\s*(\w+)\s*:\s*(.+)$', current_prop.strip())
                if prop_match:
                    prop_name = prop_match.group(1)
                    prop_value = self._parse_value(prop_match.group(2).strip())
                    obj_dict[prop_name] = prop_value

            return obj_dict

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
