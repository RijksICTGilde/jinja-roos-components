"""Parse TypeScript interfaces from React component files."""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from ..utils.ast_helpers import (
    strip_comments,
    extract_enum_values,
    is_string_literal,
    is_array_type,
    extract_array_element_type,
    normalize_type_name,
)


@dataclass
class AttributeInfo:
    """Information about a component attribute/prop."""
    name: str
    types: List[str]
    required: bool
    enum_values: Optional[List[str]] = None
    description: str = ""
    is_function: bool = False
    function_signature: Optional[str] = None


class InterfaceParser:
    """Parser for TypeScript interfaces in React components."""

    INTERFACE_PATTERN = re.compile(r'export\s+interface\s+(\w+)')
    ATTRIBUTE_PATTERN = re.compile(r'^(?P<name>[a-zA-Z_]\w*)(?P<optional>\?)?\s*:\s*(?P<type>.+?);?\s*$')

    def __init__(self):
        self.interfaces: Dict[str, List[AttributeInfo]] = {}

    def parse_file(self, content: str) -> Dict[str, List[AttributeInfo]]:
        """Parse all interfaces from file content.

        Args:
            content: File content as string

        Returns:
            Dictionary mapping interface names to attribute lists
        """
        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check for interface definition
            interface_match = self.INTERFACE_PATTERN.search(line)
            if interface_match and not line.strip().endswith('}'):
                interface_name = interface_match.group(1)
                i += 1

                # Parse interface body
                attributes = self._parse_interface_body(lines, i)
                self.interfaces[interface_name] = attributes

                # Skip to end of interface
                while i < len(lines) and not lines[i].strip().startswith('}'):
                    i += 1

            i += 1

        return self.interfaces

    def _parse_interface_body(self, lines: List[str], start_idx: int) -> List[AttributeInfo]:
        """Parse the body of an interface definition.

        Args:
            lines: All lines of the file
            start_idx: Index to start parsing from

        Returns:
            List of AttributeInfo objects
        """
        attributes = []
        i = start_idx

        while i < len(lines):
            line = lines[i].strip()

            # End of interface
            if line.startswith('}'):
                break

            # Skip empty lines and comments
            if not line or line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                i += 1
                continue

            # Skip lines that don't look like attributes
            if line.startswith('export') or line.startswith('import'):
                i += 1
                continue

            # Remove inline comments
            line = strip_comments(line)
            if not line:
                i += 1
                continue

            # Try to match attribute pattern
            attr = self._parse_attribute_line(line)
            if attr:
                attributes.append(attr)

            i += 1

        return attributes

    def _parse_attribute_line(self, line: str) -> Optional[AttributeInfo]:
        """Parse a single attribute line.

        Args:
            line: Line containing attribute definition

        Returns:
            AttributeInfo object or None if line couldn't be parsed
        """
        match = self.ATTRIBUTE_PATTERN.match(line)
        if not match:
            return None

        name = match.group('name')
        optional = match.group('optional')
        type_str = match.group('type').strip()

        # Remove trailing semicolon
        if type_str.endswith(';'):
            type_str = type_str[:-1].strip()

        required = optional is None

        # Check if it's a function type
        if type_str.startswith('('):
            return AttributeInfo(
                name=name,
                types=['function'],
                required=required,
                is_function=True,
                function_signature=type_str
            )

        # Parse enum values and other types
        enum_values, other_types = extract_enum_values(type_str)

        types = []
        if enum_values:
            types.append('enum')
        types.extend(other_types)

        # Normalize types
        types = [normalize_type_name(t) for t in types]

        return AttributeInfo(
            name=name,
            types=types,
            required=required,
            enum_values=enum_values if enum_values else None
        )

    def get_interface(self, name: str) -> Optional[List[AttributeInfo]]:
        """Get parsed interface by name.

        Args:
            name: Interface name

        Returns:
            List of AttributeInfo objects or None
        """
        return self.interfaces.get(name)

    def get_props_interface(self) -> Optional[List[AttributeInfo]]:
        """Get the main props interface (usually ends with 'Props').

        Returns:
            List of AttributeInfo objects or None
        """
        # Try common naming patterns
        for pattern in ['Props', 'IProps', 'ComponentProps']:
            for name in self.interfaces:
                if name.endswith(pattern):
                    return self.interfaces[name]

        # If only one interface, return it
        if len(self.interfaces) == 1:
            return list(self.interfaces.values())[0]

        return None
