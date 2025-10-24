"""AST manipulation helper utilities."""

import re
from typing import List, Dict, Any, Optional, Tuple


def extract_string_literal(text: str) -> Optional[str]:
    """Extract string from string literal (single or double quotes).

    Args:
        text: Text that may be a string literal

    Returns:
        String content without quotes, or None if not a string literal
    """
    text = text.strip()
    if (text.startswith("'") and text.endswith("'")) or \
       (text.startswith('"') and text.endswith('"')):
        return text[1:-1]
    return None


def is_string_literal(text: str) -> bool:
    """Check if text is a string literal.

    Args:
        text: Text to check

    Returns:
        True if text is a string literal
    """
    return extract_string_literal(text) is not None


def split_union_types(type_str: str) -> List[str]:
    """Split TypeScript union types.

    Args:
        type_str: Type string like "'primary' | 'secondary' | number"

    Returns:
        List of individual types
    """
    if '|' not in type_str:
        return [type_str.strip()]

    parts = []
    for part in type_str.split('|'):
        part = part.strip()
        if part:
            parts.append(part)
    return parts


def extract_enum_values(type_str: str) -> Tuple[List[str], List[str]]:
    """Extract enum values from union type.

    Args:
        type_str: Type string like "'primary' | 'secondary' | boolean"

    Returns:
        Tuple of (enum_values, other_types)

    Example:
        "'primary' | 'secondary' | boolean" ->
        (['primary', 'secondary'], ['boolean'])
    """
    parts = split_union_types(type_str)
    enum_values = []
    other_types = []

    for part in parts:
        literal = extract_string_literal(part)
        if literal is not None:
            enum_values.append(literal)
        else:
            other_types.append(part)

    return enum_values, other_types


def strip_comments(line: str) -> str:
    """Strip inline comments from line.

    Args:
        line: Line of code

    Returns:
        Line with comments removed
    """
    if '//' in line:
        line = line[:line.find('//')]
    return line


def extract_import_source(import_line: str) -> Optional[str]:
    """Extract source from import statement.

    Args:
        import_line: Import statement like "import { Button } from '@utrecht/component-library-react';"

    Returns:
        Import source like '@utrecht/component-library-react'
    """
    match = re.search(r"from\s+['\"]([^'\"]+)['\"]", import_line)
    if match:
        return match.group(1)
    return None


def extract_import_names(import_line: str) -> List[str]:
    """Extract imported names from import statement.

    Args:
        import_line: Import statement like "import { Button, Textbox } from '...';"

    Returns:
        List of imported names like ['Button', 'Textbox']
    """
    # Handle named imports
    match = re.search(r"import\s+\{([^}]+)\}", import_line)
    if match:
        imports = match.group(1)
        names = []
        for item in imports.split(','):
            item = item.strip()
            # Handle "Button as UtrechtButton"
            if ' as ' in item:
                item = item.split(' as ')[0].strip()
            names.append(item)
        return names

    # Handle default import
    match = re.search(r"import\s+(\w+)\s+from", import_line)
    if match:
        return [match.group(1)]

    return []


def normalize_type_name(type_str: str) -> str:
    """Normalize TypeScript type to Jinja-compatible type.

    Args:
        type_str: TypeScript type like "string", "ReactNode", "boolean"

    Returns:
        Normalized type
    """
    type_str = type_str.strip()

    # Map React types to simpler types
    type_mapping = {
        'ReactNode': 'string',
        'React.ReactNode': 'string',
        'string | ReactNode': 'string',
        'HTMLAttributes<HTMLButtonElement>': 'object',
        'PropsWithChildren': 'object',
    }

    return type_mapping.get(type_str, type_str)


def is_array_type(type_str: str) -> bool:
    """Check if type is an array type.

    Args:
        type_str: Type string

    Returns:
        True if type ends with []
    """
    return type_str.strip().endswith('[]')


def extract_array_element_type(type_str: str) -> str:
    """Extract element type from array type.

    Args:
        type_str: Type like "string[]"

    Returns:
        Element type like "string"
    """
    type_str = type_str.strip()
    if type_str.endswith('[]'):
        return type_str[:-2]
    return type_str
