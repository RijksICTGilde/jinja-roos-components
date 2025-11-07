"""Detect nested/child components used within a React component."""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from .tsx_parser import TsxParser
from ..utils.file_helpers import read_file, file_exists


class NestedComponentDetector:
    """Detector for locally-defined child components."""

    def __init__(self):
        self.tsx_parser = TsxParser()

    def detect_nested_components(
        self,
        imports: List,
        jsx_content: str,
        source_file_path: str
    ) -> List[Dict[str, Any]]:
        """Detect nested components from imports and JSX usage.

        Args:
            imports: List of ImportInfo objects from tsx_parser
            jsx_content: JSX content string
            source_file_path: Path to the source TSX file

        Returns:
            List of nested component info dicts with:
                - name: Component name (kebab-case for tag name)
                - source_path: Relative path to component file
                - interface: Interface name (e.g., 'IProgressTrackerStepProps')
                - tag_name: Suggested Jinja tag name (e.g., 'c-progress-tracker-step')
                - props: List of prop names
        """
        nested_components = []
        source_path = Path(source_file_path)

        # Find local component imports (paths starting with './')
        local_imports = self._find_local_component_imports(imports)

        for import_info in local_imports:
            # Check if this component is used in JSX
            if self._is_component_used_in_jsx(import_info['component'], jsx_content):
                # Try to load the nested component's file
                component_file = self._resolve_component_path(
                    import_info['source'],
                    source_path
                )

                props_list = []
                interface_name = import_info.get('interface', '')

                if component_file and file_exists(component_file):
                    # Parse the nested component to get its props
                    try:
                        component_info = self.tsx_parser.parse_component(component_file, None)
                        if component_info.props_interface:
                            props_list = [prop.name for prop in component_info.props_interface]
                            # Get interface name from the first prop's interface if available
                            if not interface_name:
                                interface_name = f"I{import_info['component']}Props"
                    except Exception:
                        # If parsing fails, continue with what we have
                        pass

                # Convert component name to kebab-case for tag naming
                tag_name = self._to_kebab_case(import_info['component'])

                # Extract relative path from 'rvo' onwards
                resolved_path = self._extract_relative_path(component_file) if component_file else None

                nested_components.append({
                    'name': tag_name,
                    'component_class': import_info['component'],
                    'source_path': import_info['source'],
                    'resolved_path': resolved_path,
                    'interface': interface_name,
                    'tag_name': f'c-{tag_name}',
                    'props': props_list
                })

        return nested_components

    def _find_local_component_imports(self, imports: List) -> List[Dict[str, str]]:
        """Find imports from local files (relative paths).

        Args:
            imports: List of ImportInfo objects

        Returns:
            List of dicts with component name, source path, and interface
        """
        local_imports = []

        for import_info in imports:
            # Check if source is a relative path
            if import_info.source.startswith('./') or import_info.source.startswith('../'):
                # Extract component names and interfaces
                for name in import_info.names:
                    # Check if it's a component (PascalCase) or interface (starts with 'I')
                    if name[0].isupper():
                        component_data = {
                            'component': name,
                            'source': import_info.source
                        }

                        # Check for interface import (e.g., IProgressTrackerStepProps)
                        if name.startswith('I') and name.endswith('Props'):
                            component_data['interface'] = name
                        else:
                            # Look for associated interface in the same import
                            interface_name = f'I{name}Props'
                            if interface_name in import_info.names:
                                component_data['interface'] = interface_name

                        local_imports.append(component_data)

        return local_imports

    def _is_component_used_in_jsx(self, component_name: str, jsx_content: str) -> bool:
        """Check if a component is used in JSX.

        Args:
            component_name: Component name (e.g., 'ProgressTrackerStep')
            jsx_content: JSX content string

        Returns:
            True if component is found in JSX
        """
        # Pattern: <ComponentName or <ComponentName> or <ComponentName/>
        pattern = rf'<{component_name}[\s/>]'
        return bool(re.search(pattern, jsx_content))

    def _resolve_component_path(self, import_path: str, source_file: Path) -> Optional[str]:
        """Resolve relative import path to absolute file path.

        Args:
            import_path: Relative import path (e.g., './progress-tracker-step/template')
            source_file: Path to the source file

        Returns:
            Absolute path to component file or None
        """
        # Get the directory of the source file
        source_dir = source_file.parent

        # Handle different import path formats
        # './progress-tracker-step/template' → './progress-tracker-step/template.tsx'
        # '../form-field-textinput/src/template' → '../form-field-textinput/src/template.tsx'

        # Remove .ts/.tsx extension if present
        if import_path.endswith(('.ts', '.tsx')):
            component_path = Path(import_path)
        else:
            component_path = Path(f'{import_path}.tsx')

        # Resolve relative to source directory
        resolved_path = (source_dir / component_path).resolve()

        if resolved_path.exists():
            return str(resolved_path)

        # Try without .tsx if that didn't work
        resolved_path = (source_dir / import_path).resolve()
        if resolved_path.exists():
            return str(resolved_path)

        return None

    def _to_kebab_case(self, pascal_case: str) -> str:
        """Convert PascalCase to kebab-case.

        Args:
            pascal_case: PascalCase string (e.g., 'ProgressTrackerStep')

        Returns:
            kebab-case string (e.g., 'progress-tracker-step')
        """
        # Insert hyphens before uppercase letters (except first)
        kebab = re.sub(r'(?<!^)(?=[A-Z])', '-', pascal_case)
        return kebab.lower()

    def _extract_relative_path(self, source_file: str) -> str:
        """Extract relative path from 'rvo' folder onwards.

        Args:
            source_file: Full path to source file

        Returns:
            Relative path starting from 'rvo' folder
        """
        # Find 'rvo' in the path and extract from there onwards
        parts = source_file.split('/')
        try:
            rvo_index = parts.index('rvo')
            return '/'.join(parts[rvo_index:])
        except ValueError:
            # If 'rvo' not found, return the full path as fallback
            return source_file
