"""Resolve base/parent components to HTML templates."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import js_parser for automatic component detection
from .js_parser import parse_utrecht_library


@dataclass
class PropMapping:
    """Mapping for a single prop to CSS classes or attributes."""
    prop_name: str
    value_mappings: Dict[str, Any]  # value -> classes or attributes
    attr_name: Optional[str] = None  # HTML attribute name if different


@dataclass
class BaseComponentMapping:
    """Mapping for a base component to HTML."""
    library: str
    component_name: str
    html_tag: str
    base_classes: List[str]
    prop_mappings: Dict[str, Dict[str, Any]]  # prop_name -> value -> result


class BaseComponentResolver:
    """Resolver for base/parent component libraries."""

    def __init__(self, mappings_file: Optional[str] = None):
        """Initialize resolver with mappings.

        Args:
            mappings_file: Path to JSON mappings file
        """
        if mappings_file is None:
            mappings_file = str(Path(__file__).parent.parent / 'mappers' / 'base_component_mappings.json')

        self.mappings: Dict[str, Dict[str, BaseComponentMapping]] = {}
        self._load_mappings(mappings_file)

    def _load_mappings(self, mappings_file: str) -> None:
        """Load mappings from JSON file.

        Args:
            mappings_file: Path to mappings file
        """
        try:
            with open(mappings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for library, components in data.items():
                self.mappings[library] = {}
                for comp_name, comp_data in components.items():
                    self.mappings[library][comp_name] = BaseComponentMapping(
                        library=library,
                        component_name=comp_name,
                        html_tag=comp_data['html_tag'],
                        base_classes=comp_data.get('base_classes', []),
                        prop_mappings=comp_data.get('prop_mappings', {})
                    )
        except FileNotFoundError:
            # No mappings file yet - will be created
            pass

    def resolve(self, library: str, component_name: str, props: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve a base component to HTML template data.

        Args:
            library: Library name (e.g., '@utrecht/component-library-react')
            component_name: Component name (e.g., 'Button')
            props: Component props as dict

        Returns:
            Dictionary with:
                - html_tag: HTML tag name
                - css_classes: List of CSS class conditionals
                - attributes: Dict of HTML attributes
                - needs_review: List of items needing manual review
        """
        # Prefer manual JSON mappings when available (more accurate than auto-detection)
        if library in self.mappings and component_name in self.mappings[library]:
            # Use manual mappings - fall through to the code below
            pass
        # Try auto-detection for Utrecht components without manual mappings
        elif library == '@utrecht/component-library-react':
            auto_result = self._auto_detect_component(component_name, props)
            if auto_result:
                return auto_result
        # No mappings found
        else:
            return {
                'html_tag': 'div',
                'css_classes': [],
                'attributes': {},
                'needs_review': [f'Unknown base component: {library}/{component_name}']
            }

        mapping = self.mappings[library][component_name]

        # Start with base classes
        css_classes = mapping.base_classes.copy()
        attributes = {}
        needs_review = []

        # Process each prop
        for prop_name, prop_value in props.items():
            if prop_name in mapping.prop_mappings:
                prop_mapping = mapping.prop_mappings[prop_name]

                # Handle different mapping types
                if isinstance(prop_mapping, dict):
                    # Value-based mapping
                    result = self._resolve_prop_value(prop_name, prop_value, prop_mapping)

                    if 'classes' in result:
                        css_classes.extend(result['classes'])
                    if 'attributes' in result:
                        attributes.update(result['attributes'])
                    if 'needs_review' in result:
                        needs_review.extend(result['needs_review'])
            else:
                # Unmapped prop - may need review
                if not prop_name.startswith('on') and prop_name not in ['className', 'children', 'style']:
                    needs_review.append(f'Unmapped prop: {prop_name}')

        return {
            'html_tag': mapping.html_tag,
            'css_classes': css_classes,
            'attributes': attributes,
            'needs_review': needs_review
        }

    def _resolve_prop_value(self, prop_name: str, prop_value: Any, mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve a single prop value using its mapping.

        Args:
            prop_name: Property name
            prop_value: Property value
            mapping: Mapping configuration

        Returns:
            Dict with classes, attributes, needs_review
        """
        result = {
            'classes': [],
            'attributes': {},
            'needs_review': []
        }

        # Check if it's a value mapping (enum-like)
        if isinstance(mapping, dict) and 'values' in mapping:
            value_map = mapping['values']
            str_value = str(prop_value)

            if str_value in value_map:
                value_result = value_map[str_value]

                if isinstance(value_result, list):
                    # List of classes
                    result['classes'] = value_result
                elif isinstance(value_result, dict):
                    if 'classes' in value_result:
                        result['classes'] = value_result['classes']
                    if 'attributes' in value_result:
                        result['attributes'] = value_result['attributes']
                elif isinstance(value_result, str):
                    # Single class
                    result['classes'] = [value_result]
            else:
                result['needs_review'].append(f'Unknown value for {prop_name}: {prop_value}')

        # Check if it's a boolean mapping
        elif isinstance(mapping, dict) and 'boolean' in mapping:
            bool_config = mapping['boolean']
            if prop_value:
                if 'true_classes' in bool_config:
                    result['classes'] = bool_config['true_classes']
                if 'true_attributes' in bool_config:
                    result['attributes'] = bool_config['true_attributes']
            else:
                if 'false_classes' in bool_config:
                    result['classes'] = bool_config['false_classes']
                if 'false_attributes' in bool_config:
                    result['attributes'] = bool_config['false_attributes']

        # Direct attribute mapping
        elif isinstance(mapping, dict) and 'attribute' in mapping:
            attr_name = mapping['attribute']
            result['attributes'][attr_name] = prop_value

        return result

    def is_base_component(self, library: str, component_name: str) -> bool:
        """Check if a component is a known base component.

        Args:
            library: Library name
            component_name: Component name

        Returns:
            True if component is mapped or can be auto-detected
        """
        # Check manual mappings first
        if library in self.mappings and component_name in self.mappings[library]:
            return True

        # For Utrecht, always return True as we can auto-detect
        if library == '@utrecht/component-library-react':
            return True

        return False

    def get_supported_libraries(self) -> List[str]:
        """Get list of supported base component libraries.

        Returns:
            List of library names
        """
        return list(self.mappings.keys())

    def _auto_detect_component(self, component_name: str, props: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Auto-detect component structure from compiled JavaScript.

        Args:
            component_name: Component name to detect
            props: Component props

        Returns:
            Resolution dict or None if detection failed
        """
        try:
            # Use js_parser to parse the component
            component_info = parse_utrecht_library(component_name)
            if not component_info:
                return None

            # Use the primary element (the actual HTML element, not wrapper divs)
            primary = component_info.primary_element

            # Build base classes from the primary element
            css_classes = primary.classes.copy()

            # Add conditional classes
            for cond_class in primary.conditional_classes:
                # Convert JS condition to something we can track
                # For now, we'll skip conditionals in base classes
                # They'll be handled by clsx parser in the RVO component
                pass

            # Extract attributes
            attributes = {}
            for attr_name, attr_value in primary.attributes.items():
                # Skip special React props
                if attr_name not in ('ref', 'children', 'className'):
                    attributes[attr_name] = attr_value

            # Check if there are any className props from RVO
            # The outermost element might have className from the RVO component
            if component_info.elements:
                outer_elem = component_info.elements[0]
                # Look for additional classes from the outer wrapper
                # These are typically passed via the className prop
                for cls in outer_elem.classes:
                    if cls and cls not in css_classes:
                        css_classes.append(cls)

            # Check if there's a wrapper structure (outer element is different from primary)
            wrapper_info = None
            if component_info.elements and len(component_info.elements) > 0:
                outer_elem = component_info.elements[0]
                # If outer element is a wrapper (div/span) and primary is not, preserve the structure
                if outer_elem.tag in ('div', 'span') and outer_elem.tag != primary.tag:
                    wrapper_info = {
                        'tag': outer_elem.tag,
                        'classes': outer_elem.classes.copy()
                    }

            return {
                'html_tag': primary.tag,
                'css_classes': css_classes,
                'attributes': attributes,
                'needs_review': [],
                'wrapper': wrapper_info  # Include wrapper info if present
            }

        except Exception as e:
            # Auto-detection failed, return None to fall back to manual mappings
            return None
