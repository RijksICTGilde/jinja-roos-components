"""Parse JSX structure for standalone components without base libraries."""

import re
from typing import Dict, List, Any, Optional


class JsxStructureParser:
    """Parser for extracting HTML structure from JSX when no base component is used."""

    def parse_root_element(self, jsx_content: str, dynamic_tag: dict = None) -> Dict[str, Any]:
        """Parse the root JSX element to extract tag, classes, and attributes.

        Detects wrapper patterns (e.g., <div><select>...</select></div>)
        and extracts both wrapper and primary element information.

        Args:
            jsx_content: JSX return statement content
            dynamic_tag: Optional dict with dynamic tag info from tsx_parser

        Returns:
            Dictionary with:
                - html_tag: HTML tag name (e.g., 'div', 'select')
                - css_classes: List of CSS class names
                - attributes: Dict of HTML attributes
                - needs_review: List of items needing manual review
                - wrapper: Optional wrapper info if wrapper pattern detected
                - dynamic_tag: Optional dynamic tag info if detected
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

        root_tag = tag_match.group(1)
        root_attrs_str = tag_match.group(2).strip()

        # Parse root element attributes
        root_classes, root_attrs, root_needs_review = self._parse_attributes(root_attrs_str)

        # Check if this matches a dynamic tag variable
        resolved_dynamic_tag = None
        if dynamic_tag and root_tag == dynamic_tag.get('variable_name'):
            # This is a dynamic tag! Use the conditional info
            resolved_dynamic_tag = dynamic_tag

        # Check for wrapper pattern: simple div/span with only className
        # wrapping a more complex element
        if root_tag in ('div', 'span') and self._is_simple_wrapper(root_attrs_str):
            # Try to detect nested element
            nested_result = self._parse_nested_element(jsx_content, tag_match.end())
            if nested_result:
                # Wrapper pattern detected!
                return {
                    'html_tag': nested_result['html_tag'],
                    'css_classes': nested_result['css_classes'],
                    'attributes': nested_result['attributes'],
                    'needs_review': nested_result['needs_review'],
                    'wrapper': {
                        'tag': root_tag,
                        'classes': root_classes
                    },
                    'dynamic_tag': resolved_dynamic_tag
                }

        # No wrapper pattern - return root element info
        return {
            'html_tag': root_tag,
            'css_classes': root_classes,
            'attributes': root_attrs,
            'needs_review': root_needs_review,
            'dynamic_tag': resolved_dynamic_tag
        }

    def _is_simple_wrapper(self, attrs_str: str) -> bool:
        """Check if element is a simple wrapper (only has className, no complex attributes).

        Args:
            attrs_str: Attributes string

        Returns:
            True if this looks like a simple wrapper element
        """
        # Simple wrapper has only className (static or dynamic)
        # No other meaningful attributes
        has_classname = 'className=' in attrs_str

        # Count number of attributes (rough heuristic)
        attr_count = len(re.findall(r'\w+\s*=', attrs_str))

        # Simple wrapper: has className and few/no other attrs
        return has_classname and attr_count <= 1

    def _parse_nested_element(self, jsx_content: str, start_pos: int) -> Optional[Dict]:
        """Parse nested element after root tag.

        Args:
            jsx_content: Full JSX content
            start_pos: Position after root opening tag

        Returns:
            Dict with nested element info or None
        """
        # Skip whitespace
        pos = start_pos
        while pos < len(jsx_content) and jsx_content[pos] in ' \n\t':
            pos += 1

        # Look for nested opening tag
        nested_match = re.match(r'<([a-zA-Z][a-zA-Z0-9]*)\s*([^>]*?)>', jsx_content[pos:], re.DOTALL)
        if not nested_match:
            return None

        nested_tag = nested_match.group(1)
        nested_attrs_str = nested_match.group(2).strip()

        # Parse nested element attributes
        nested_classes, nested_attrs, nested_needs_review = self._parse_attributes(nested_attrs_str)

        return {
            'html_tag': nested_tag,
            'css_classes': nested_classes,
            'attributes': nested_attrs,
            'needs_review': nested_needs_review
        }

    def _parse_attributes(self, attributes_str: str) -> tuple:
        """Parse attributes string to extract classes, attributes, and review items.

        Args:
            attributes_str: Attributes string from opening tag

        Returns:
            Tuple of (css_classes, attributes, needs_review)
        """
        css_classes = []
        attributes = {}
        needs_review = []

        if not attributes_str:
            return css_classes, attributes, needs_review

        # Extract static className attribute
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
            needs_review.append('Dynamic className expression found - needs clsx parsing')

        return css_classes, attributes, needs_review

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
