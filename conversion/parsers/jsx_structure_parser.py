"""Parse JSX structure for standalone components without base libraries."""

import re
from typing import Dict, List, Any, Optional


class JsxStructureParser:
    """Parser for extracting HTML structure from JSX when no base component is used."""

    def parse_root_element(self, jsx_content: str) -> Dict[str, Any]:
        """Parse the root JSX element to extract tag, classes, and attributes.

        Args:
            jsx_content: JSX return statement content

        Returns:
            Dictionary with:
                - html_tag: HTML tag name (e.g., 'div', 'section')
                - css_classes: List of CSS class names
                - attributes: Dict of HTML attributes
                - needs_review: List of items needing manual review
        """
        # Strip outer parentheses if present
        jsx_content = jsx_content.strip()
        if jsx_content.startswith('('):
            jsx_content = jsx_content[1:].strip()
        if jsx_content.endswith(')'):
            jsx_content = jsx_content[:-1].strip()

        # Extract the opening tag of the root element
        # Pattern: <tagname ...attributes>
        tag_match = re.match(r'<([a-zA-Z][a-zA-Z0-9]*)\s*([^>]*?)>', jsx_content, re.DOTALL)

        if not tag_match:
            return {
                'html_tag': 'div',
                'css_classes': [],
                'attributes': {},
                'needs_review': ['Could not parse root JSX element']
            }

        tag_name = tag_match.group(1)
        attributes_str = tag_match.group(2).strip()

        # Parse attributes
        css_classes = []
        attributes = {}
        needs_review = []

        if attributes_str:
            # Extract className attribute
            class_match = re.search(r'className=["\']([^"\']+)["\']', attributes_str)
            if class_match:
                class_str = class_match.group(1)
                css_classes = [cls.strip() for cls in class_str.split() if cls.strip()]

            # Extract other static attributes (id, data-*, aria-*, etc.)
            # Pattern: attrName="value" or attrName='value'
            attr_pattern = r'(\w+(?:-\w+)*)=["\']([^"\']+)["\']'
            for match in re.finditer(attr_pattern, attributes_str):
                attr_name = match.group(1)
                attr_value = match.group(2)

                # Skip className (already processed) and JSX-specific attributes
                if attr_name not in ('className', 'key', 'ref'):
                    attributes[attr_name] = attr_value

            # Check for dynamic className expressions like className={clsx(...)}
            if 'className={' in attributes_str:
                needs_review.append('Dynamic className expression found - may need clsx parsing')

        return {
            'html_tag': tag_name,
            'css_classes': css_classes,
            'attributes': attributes,
            'needs_review': needs_review
        }

    def extract_static_props(self, jsx_content: str, component_name: str) -> Dict[str, str]:
        """Extract static props passed to a component.

        Args:
            jsx_content: JSX content
            component_name: Name of the component to find (e.g., 'FieldsetUtrecht')

        Returns:
            Dictionary of prop names to values
        """
        # Find the component tag in JSX: <ComponentName ...props>
        pattern = rf'<{component_name}\s+([^>]*?)(?:>|/>)'
        match = re.search(pattern, jsx_content, re.DOTALL)

        if not match:
            return {}

        props_str = match.group(1).strip()
        if not props_str:
            return {}

        # Parse props
        props = {}
        # Pattern for prop="value" or prop='value'
        prop_pattern = r'(\w+)=["\']([^"\']+)["\']'

        for match in re.finditer(prop_pattern, props_str):
            prop_name = match.group(1)
            prop_value = match.group(2)
            props[prop_name] = prop_value

        return props
