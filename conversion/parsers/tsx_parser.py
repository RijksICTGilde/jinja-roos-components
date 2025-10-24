"""Parse React TSX component files."""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .interface_parser import InterfaceParser, AttributeInfo
from .defaultargs_parser import DefaultArgsParser
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
    imports: List[ImportInfo]
    jsx_content: str
    file_path: str


class TsxParser:
    """Parser for React TSX component files."""

    def __init__(self):
        self.interface_parser = InterfaceParser()
        self.defaultargs_parser = DefaultArgsParser()
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
        jsx_content = self._extract_jsx_return(tsx_content)

        return ComponentInfo(
            name=component_name,
            props_interface=props_interface,
            default_args=default_args,
            imports=self.imports,
            jsx_content=jsx_content,
            file_path=tsx_file_path
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

    def _extract_jsx_return(self, content: str) -> str:
        """Extract the JSX return statement from component.

        Args:
            content: File content

        Returns:
            JSX content as string
        """
        # Find the main component function/const
        # Look for patterns like: export const Button: React.FC = ({ ... }) => {
        # or: export const Button = ({ ... }) => {

        # Simple heuristic: find "return (" and extract until matching ")"
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
