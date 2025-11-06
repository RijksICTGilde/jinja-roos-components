"""Load and apply component customizations during conversion."""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.extract_design_tokens import (
    extract_colors_from_tokens,
    extract_icons_from_types
)


class CustomizationLoader:
    """Loads and resolves component customizations."""

    def __init__(self):
        self.customizations_dir = Path(__file__).parent
        self.tokens = self._load_tokens()
        self._token_cache = {}

    def _load_tokens(self) -> Dict:
        """Load token reference definitions."""
        tokens_file = self.customizations_dir / "_tokens.json"
        if not tokens_file.exists():
            return {}

        with open(tokens_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def has_customization(self, component_name: str) -> bool:
        """Check if a component has customizations."""
        custom_file = self.customizations_dir / f"{component_name}.json"
        return custom_file.exists()

    def load_customization(self, component_name: str) -> Optional[Dict]:
        """Load customization for a component."""
        custom_file = self.customizations_dir / f"{component_name}.json"
        if not custom_file.exists():
            return None

        with open(custom_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def resolve_token_reference(self, reference: str) -> List[str]:
        """Resolve a token reference like 'all_rvo_colors' to actual values.

        Args:
            reference: Token reference name (e.g., "all_rvo_colors")

        Returns:
            List of actual values
        """
        # Check cache first
        if reference in self._token_cache:
            return self._token_cache[reference]

        # Get token definition
        token_def = self.tokens.get(reference)
        if not token_def:
            raise ValueError(f"Unknown token reference: {reference}")

        if token_def['type'] == 'static':
            # Static list of values
            values = token_def['values']
        elif token_def['type'] == 'reference':
            # Extract from source
            values = self._extract_from_source(
                token_def['source'],
                token_def['extract_field']
            )
        else:
            raise ValueError(f"Unknown token type: {token_def['type']}")

        # Cache for future use
        self._token_cache[reference] = values
        return values

    def _extract_from_source(self, source_function: str, extract_field: str) -> List[str]:
        """Extract values from a source function.

        Args:
            source_function: Function name like "extract_colors_from_tokens"
            extract_field: Field to extract like "template_name"

        Returns:
            List of extracted values
        """
        # Map function names to actual functions
        extractors = {
            'extract_colors_from_tokens': extract_colors_from_tokens,
            'extract_icons_from_types': extract_icons_from_types
        }

        extractor = extractors.get(source_function)
        if not extractor:
            raise ValueError(f"Unknown source function: {source_function}")

        # Call the extraction function
        data = extractor()

        # If extraction failed (returns empty), try fallback from definitions.json
        if not data and source_function == 'extract_colors_from_tokens':
            data = self._extract_colors_from_definitions()

        # Extract the specified field
        return [item[extract_field] for item in data if extract_field in item]

    def _extract_colors_from_definitions(self) -> List[Dict[str, str]]:
        """Fallback: Extract colors from definitions.json if token extraction fails.

        Returns:
            List of color dicts with template_name field
        """
        definitions_path = Path(__file__).parent.parent.parent / "src" / "jinja_roos_components" / "definitions.json"
        if not definitions_path.exists():
            return []

        with open(definitions_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract colors and format them like the extractor would
        colors = []
        for color in data.get('colors', []):
            colors.append({
                'name': color['name'],
                'template_name': color['name'].lower(),
                'display_name': color['name'].title(),
                'hex': color.get('value', ''),
            })

        return colors

    def apply_customizations(self, component_name: str, attributes: List[Any]) -> List[Any]:
        """Apply customizations to component attributes.

        Args:
            component_name: Name of the component
            attributes: List of AttributeInfo objects

        Returns:
            Modified list of attributes
        """
        customization = self.load_customization(component_name)
        if not customization:
            return attributes

        # Apply attribute overrides
        attribute_overrides = customization.get('attribute_overrides', {})
        for attr in attributes:
            if attr.name in attribute_overrides:
                override = attribute_overrides[attr.name]

                # Handle enum value expansion
                if 'values' in override and isinstance(override['values'], str):
                    # It's a token reference
                    expanded_values = self.resolve_token_reference(override['values'])
                    attr.enum_values = expanded_values

                # Update other properties if specified
                if 'required' in override:
                    attr.required = override['required']
                if 'description' in override:
                    attr.description = override['description']
                if 'default' in override:
                    attr.default = override['default']

        # Apply attribute additions
        attribute_additions = customization.get('attribute_additions', {})
        if attribute_additions:
            # Import here to avoid circular dependency
            from conversion.parsers.interface_parser import AttributeInfo

            for attr_name, attr_def in attribute_additions.items():
                # Check if it already exists
                if any(a.name == attr_name for a in attributes):
                    continue

                # Create new attribute
                new_attr = AttributeInfo(
                    name=attr_name,
                    types=[attr_def.get('type', 'string')],
                    required=attr_def.get('required', False),
                    description=attr_def.get('description', ''),
                    enum_values=None,
                    is_function=False
                )

                # Handle enum values
                if attr_def.get('type') == 'enum' and 'values' in attr_def:
                    if isinstance(attr_def['values'], str):
                        # Token reference
                        new_attr.enum_values = self.resolve_token_reference(attr_def['values'])
                    else:
                        # Direct list
                        new_attr.enum_values = attr_def['values']

                attributes.append(new_attr)

        return attributes

    def get_customization_notes(self, component_name: str) -> List[str]:
        """Get notes about customizations for a component.

        Args:
            component_name: Name of the component

        Returns:
            List of note strings
        """
        customization = self.load_customization(component_name)
        if not customization:
            return []

        notes = customization.get('notes', [])
        if isinstance(notes, str):
            return [notes]
        return notes

    def get_aliases(self, component_name: str) -> List[str]:
        """Get aliases for a component from customization file.

        Args:
            component_name: Name of the component

        Returns:
            List of alias strings (empty list if no aliases defined)
        """
        customization = self.load_customization(component_name)
        if not customization:
            return []

        aliases = customization.get('aliases', [])
        # Support both string and list formats
        if isinstance(aliases, str):
            return [aliases]
        return aliases

    def apply_default_overrides(self, component_name: str, default_args: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default value overrides from customization.

        Args:
            component_name: Name of the component
            default_args: Original default args

        Returns:
            Modified default args
        """
        customization = self.load_customization(component_name)
        if not customization:
            return default_args

        # Get default overrides
        default_overrides = customization.get('default_overrides', {})
        if not default_overrides:
            return default_args

        # Apply overrides
        modified_args = default_args.copy()
        for key, value in default_overrides.items():
            modified_args[key] = value

        return modified_args

    def get_children_support_config(self, component_name: str) -> Optional[Dict]:
        """Get children/content support configuration from customization.

        This allows adding children support to components that don't have it in React.

        Args:
            component_name: Name of the component

        Returns:
            Dict with children support config or None
        """
        customization = self.load_customization(component_name)
        if not customization:
            return None

        return customization.get('add_children_support')

    def get_pass_through_attributes(self, component_name: str) -> List[Dict[str, Any]]:
        """Get pass-through attributes from customization.

        Pass-through attributes are custom attributes that should be added to the component
        and rendered on a specific target element (e.g., 'name' attribute on the select element).

        Args:
            component_name: Name of the component

        Returns:
            List of pass-through attribute definitions
        """
        customization = self.load_customization(component_name)
        if not customization:
            return []

        return customization.get('pass_through_attributes', [])

    def get_custom_content_template(self, component_name: str) -> Optional[str]:
        """Get custom content template from customization.

        This allows overriding the default content rendering with custom Jinja logic.

        Args:
            component_name: Name of the component

        Returns:
            Custom content template string or None
        """
        customization = self.load_customization(component_name)
        if not customization:
            return None

        return customization.get('custom_content_template')
