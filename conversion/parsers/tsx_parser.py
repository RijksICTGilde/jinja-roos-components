"""Parse React TSX component files."""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .interface_parser import InterfaceParser, AttributeInfo
from .defaultargs_parser import DefaultArgsParser
from .component_defaults_parser import ComponentDefaultsParser
from ..utils.ast_helpers import extract_import_source, extract_import_names


@dataclass
class ImportInfo:
    """Information about an import statement."""
    source: str
    names: List[str]
    is_default: bool = False
    aliases: Dict[str, str] = None  # Maps alias_name -> original_name (e.g., "FieldsetUtrecht" -> "Fieldset")


@dataclass
class ComponentInfo:
    """Parsed information about a React component."""
    name: str
    props_interface: Optional[List[AttributeInfo]]
    default_args: Dict[str, Any]
    actual_defaults: Dict[str, Any]  # Defaults actually used in component destructuring
    example_values: Dict[str, Any]   # Values only in defaultArgs (examples for stories)
    imports: List[ImportInfo]
    jsx_content: str
    file_path: str
    dynamic_tag: Optional[Dict[str, Any]] = None  # Info about dynamic tag selection (e.g., TagName = cond ? 'div' : 'span')


class TsxParser:
    """Parser for React TSX component files."""

    def __init__(self):
        self.interface_parser = InterfaceParser()
        self.defaultargs_parser = DefaultArgsParser()
        self.component_defaults_parser = ComponentDefaultsParser()
        self.imports: List[ImportInfo] = []

    def parse_component(self, tsx_file_path: str, defaultargs_file_path: Optional[str] = None) -> ComponentInfo:
        """Parse a React component file.

        Args:
            tsx_file_path: Path to the TSX template file
            defaultargs_file_path: Optional path to defaultArgs file

        Returns:
            ComponentInfo object with parsed data
        """
        from ..utils.file_helpers import read_file, file_exists

        # Read the TSX file
        tsx_content = read_file(tsx_file_path)

        # Parse imports
        self.imports = self._parse_imports(tsx_content)

        # Parse interfaces
        self.interface_parser.parse_file(tsx_content)
        props_interface = self.interface_parser.get_props_interface()

        # Parse default args if file provided
        default_args = {}
        if defaultargs_file_path and file_exists(defaultargs_file_path):
            defaultargs_content = read_file(defaultargs_file_path)
            default_args = self.defaultargs_parser.parse_file(defaultargs_content)

        # Extract component name
        component_name = self._extract_component_name(tsx_file_path)

        # Extract JSX content (the return statement)
        jsx_content = self._extract_jsx_return(tsx_content, component_name)

        # Distinguish between actual defaults and example values
        actual_defaults, example_values = self.component_defaults_parser.parse_component_function(
            tsx_content, component_name, default_args
        )

        # Detect dynamic tag assignments
        dynamic_tag = self._detect_dynamic_tag(tsx_content)

        return ComponentInfo(
            name=component_name,
            props_interface=props_interface,
            default_args=default_args,
            actual_defaults=actual_defaults,
            example_values=example_values,
            imports=self.imports,
            jsx_content=jsx_content,
            file_path=tsx_file_path,
            dynamic_tag=dynamic_tag
        )

    def _parse_imports(self, content: str) -> List[ImportInfo]:
        """Parse import statements from file content.

        Args:
            content: File content

        Returns:
            List of ImportInfo objects
        """
        imports = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if not line.startswith('import'):
                continue

            source = extract_import_source(line)
            if not source:
                continue

            names = extract_import_names(line)
            is_default = ' as ' in line or ('{' not in line and 'from' in line)

            # Extract aliases for named imports
            aliases = {}
            if '{' in line:
                match = re.search(r'\{([^}]+)\}', line)
                if match:
                    imports_str = match.group(1)
                    for item in imports_str.split(','):
                        item = item.strip()
                        if ' as ' in item:
                            parts = item.split(' as ')
                            original = parts[0].strip()
                            alias = parts[1].strip()
                            aliases[alias] = original

            imports.append(ImportInfo(
                source=source,
                names=names,
                is_default=is_default,
                aliases=aliases if aliases else None
            ))

        return imports

    def _extract_component_name(self, file_path: str) -> str:
        """Extract component name from file path.

        Args:
            file_path: Path to component file

        Returns:
            Component name
        """
        from pathlib import Path

        # Get parent directory name as component name
        path = Path(file_path)
        # Navigate up from template.tsx -> src -> component-name
        if path.name == 'template.tsx':
            component_name = path.parent.parent.name
        else:
            component_name = path.stem

        return component_name

    def _extract_jsx_return(self, content: str, component_name: str) -> str:
        """Extract the JSX return statement from component.

        Args:
            content: File content
            component_name: Name of the component to extract (e.g., 'button')

        Returns:
            JSX content as string
        """
        import re

        # Convert component name to PascalCase for matching
        pascal_name = ''.join(word.capitalize() for word in component_name.split('-'))

        # Find the main component function/const
        # Look for patterns like:
        # 1. export const Button: React.FC = ({ ... }) => { return (...) }
        # 2. export const Button = ({ ... }) => { return (...) }
        # 3. export const Button = ({ ... }) => (...)  <-- immediate return

        # First, find the component declaration
        component_pattern = rf'export\s+const\s+{pascal_name}[:\s=].*?(?:\)\s*=>\s*\(|\)\s*=>\s*\{{)'
        component_match = re.search(component_pattern, content, re.DOTALL)

        if not component_match:
            # Fallback to old behavior if we can't find the specific component
            return self._extract_jsx_return_fallback(content)

        # Get content starting from the component declaration
        component_start = component_match.start()
        component_content = content[component_start:]

        # First try arrow function with immediate JSX return: ) => (
        arrow_return_match = re.search(r'\)\s*=>\s*\(', component_content)
        if arrow_return_match and arrow_return_match.start() < 500:  # Should be near the start
            start = arrow_return_match.end() - 1  # Start at the '('
            jsx = self._extract_until_matching_paren(component_content[start:])
            return jsx.strip()

        # Fallback to explicit return statement
        return_match = re.search(r'return\s*\(', component_content)
        if not return_match:
            # Try without parentheses
            return_match = re.search(r'return\s*<', component_content)
            if not return_match:
                return ""

        start = return_match.end()
        if component_content[start - 1] == '(':
            start -= 1

        # Extract until matching closing
        if component_content[start] == '(':
            jsx = self._extract_until_matching_paren(component_content[start:])
        else:
            # Extract until end of JSX (find semicolon or closing brace)
            jsx = self._extract_jsx_element(component_content[start:])

        return jsx.strip()

    def _extract_jsx_return_fallback(self, content: str) -> str:
        """Fallback JSX extraction when component name matching fails."""
        import re

        # First try arrow function with immediate JSX return: ) => (
        arrow_return_match = re.search(r'\)\s*=>\s*\(', content)
        if arrow_return_match:
            start = arrow_return_match.end() - 1  # Start at the '('
            jsx = self._extract_until_matching_paren(content[start:])
            return jsx.strip()

        # Fallback to explicit return statement
        return_match = re.search(r'return\s*\(', content)
        if not return_match:
            # Try without parentheses
            return_match = re.search(r'return\s*<', content)
            if not return_match:
                return ""

        start = return_match.end()
        if content[start - 1] == '(':
            start -= 1

        # Extract until matching closing
        if content[start] == '(':
            jsx = self._extract_until_matching_paren(content[start:])
        else:
            # Extract until end of JSX (find semicolon or closing brace)
            jsx = self._extract_jsx_element(content[start:])

        return jsx.strip()

    def _extract_until_matching_paren(self, content: str) -> str:
        """Extract content until matching closing parenthesis.

        Args:
            content: Content starting with '('

        Returns:
            Content including parentheses
        """
        count = 0
        result = []

        for char in content:
            result.append(char)
            if char == '(':
                count += 1
            elif char == ')':
                count -= 1
                if count == 0:
                    break

        return ''.join(result)

    def _extract_jsx_element(self, content: str) -> str:
        """Extract a JSX element.

        Args:
            content: Content starting with '<'

        Returns:
            JSX element content
        """
        # Simple extraction: find matching closing tag or self-closing tag
        # This is a simplified version - a full parser would handle this better

        tag_count = 0
        result = []
        in_string = False
        string_char = None

        for i, char in enumerate(content):
            result.append(char)

            # Track strings to avoid counting tags inside strings
            if char in ('"', "'", '`') and (i == 0 or content[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False

            if not in_string:
                if char == '<' and i + 1 < len(content) and content[i + 1] != '/':
                    tag_count += 1
                elif char == '<' and i + 1 < len(content) and content[i + 1] == '/':
                    tag_count -= 1
                elif char == '/' and i + 1 < len(content) and content[i + 1] == '>':
                    tag_count -= 1

                if tag_count == 0 and len(result) > 1:
                    break

        return ''.join(result)

    def get_base_component_imports(self) -> List[ImportInfo]:
        """Get imports that are likely base/parent components.

        Returns:
            List of ImportInfo for base component libraries
        """
        base_patterns = [
            '@utrecht',
            '@nl-rvo',
            'component-library',
        ]

        base_imports = []
        for import_info in self.imports:
            for pattern in base_patterns:
                if pattern in import_info.source:
                    base_imports.append(import_info)
                    break

        return base_imports

    def _detect_dynamic_tag(self, content: str) -> Optional[Dict[str, Any]]:
        """Detect dynamic tag assignment patterns like: const TagName = condition ? 'tag1' : 'tag2'

        Args:
            content: File content

        Returns:
            Dictionary with dynamic tag info or None
            {
                'variable_name': 'ListTag',
                'condition': 'type === "unordered"',
                'true_tag': 'ul',
                'false_tag': 'ol'
            }
        """
        # Pattern: const TagName = condition ? 'tag1' : 'tag2';
        # Supports single or double quotes
        pattern = r'const\s+([A-Z][a-zA-Z0-9]*)\s*=\s*([^?]+)\s*\?\s*["\']([a-z][a-z0-9]*)["\']?\s*:\s*["\']([a-z][a-z0-9]*)["\']'

        match = re.search(pattern, content)
        if match:
            return {
                'variable_name': match.group(1),
                'condition': match.group(2).strip(),
                'true_tag': match.group(3),
                'false_tag': match.group(4)
            }

        return None
