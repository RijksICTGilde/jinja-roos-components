"""Parse JSX content/children rendering logic."""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ContentElement:
    """Represents a content element in JSX."""
    type: str  # 'conditional', 'fallback', 'text', 'component', 'variable'
    condition: Optional[str] = None  # For conditional rendering
    content: Optional[str] = None  # The actual content
    component_name: Optional[str] = None  # For component elements
    component_props: Optional[Dict] = None  # Props for components
    fallback_chain: Optional[List[str]] = None  # For || operators


class ContentParser:
    """Parser for JSX content rendering logic."""

    def __init__(self):
        self.elements: List[ContentElement] = []

    def extract_from_jsx(self, jsx_content: str) -> List[ContentElement]:
        """Extract content elements from JSX.

        Args:
            jsx_content: JSX content string

        Returns:
            List of ContentElement objects
        """
        self.elements = []

        # Find the main component's opening and closing tags
        # Extract everything between them
        content_match = self._extract_component_children(jsx_content)
        if not content_match:
            return []

        # Parse the children content
        children_content = content_match.strip()
        self._parse_children(children_content)

        return self.elements

    def _extract_component_children(self, jsx_content: str) -> Optional[str]:
        """Extract children content from the main JSX element.

        Args:
            jsx_content: Full JSX content

        Returns:
            Children content or None
        """
        # Pattern: <Component ...> children </Component>
        # Find the outermost component
        match = re.search(r'<(\w+)[^>]*>(.*)</\1>', jsx_content, re.DOTALL)
        if match:
            return match.group(2)

        return None

    def _parse_children(self, content: str) -> None:
        """Parse children content for rendering elements.

        Args:
            content: Children content string
        """
        # Find all JSX expressions with balanced braces: {expression}
        pos = 0
        while pos < len(content):
            # Find next opening brace
            start = content.find('{', pos)
            if start == -1:
                break

            # Extract balanced braces
            expression, end_pos = self._extract_balanced_expression(content, start)
            if not expression:
                pos = start + 1
                continue

            pos = end_pos

            # Remove outer braces and strip
            expression = expression[1:-1].strip()

            # Check for ternary operator: condition ? value : fallback
            if ' ? ' in expression and ' : ' in expression:
                self._parse_ternary(expression)
            # Check for conditional rendering: condition && element
            elif ' && ' in expression:
                self._parse_conditional(expression)
            # Check for fallback rendering: a || b || c
            elif ' || ' in expression:
                self._parse_fallback(expression)
            # Simple variable reference
            else:
                self.elements.append(ContentElement(
                    type='variable',
                    content=expression
                ))

    def _extract_balanced_expression(self, content: str, start: int) -> tuple:
        """Extract a balanced {expression} from content.

        Args:
            content: Full content string
            start: Position of opening brace

        Returns:
            Tuple of (expression including braces, end position)
        """
        if content[start] != '{':
            return None, start

        depth = 0
        in_string = False
        string_char = None
        result = []

        for i in range(start, len(content)):
            char = content[i]
            result.append(char)

            # Track string boundaries
            if char in ('"', "'", '`') and (i == 0 or content[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False

            if not in_string:
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        return ''.join(result), i + 1

        return ''.join(result), len(content)

    def _parse_conditional(self, expression: str) -> None:
        """Parse conditional rendering expression.

        Args:
            expression: Expression like "legend && <FieldsetLegend>{legend}</FieldsetLegend>"
        """
        parts = expression.split(' && ', 1)  # Split only on first && to preserve nested content
        if len(parts) != 2:
            return

        condition = parts[0].strip()
        content = parts[1].strip()

        # Check if content is a JSX element
        if content.startswith('<'):
            # Parse the JSX element
            component_info = self._parse_jsx_element(content)
            if component_info:
                self.elements.append(ContentElement(
                    type='conditional',
                    condition=condition,
                    content=component_info.get('children'),
                    component_name=component_info.get('component'),
                    component_props=component_info.get('props')
                ))
                return

        # Otherwise it's a variable reference
        self.elements.append(ContentElement(
            type='conditional',
            condition=condition,
            content=content
        ))

    def _parse_ternary(self, expression: str) -> None:
        """Parse ternary expression.

        Args:
            expression: Expression like "children ? parseContentMarkup(children) : fields && fields.map(...)"
        """
        # For now, we'll treat ternary as a fallback with the true and false values
        # Split on ? to get condition and rest
        parts = expression.split(' ? ', 1)
        if len(parts) != 2:
            return

        condition = parts[0].strip()
        rest = parts[1].strip()

        # Split on : to get true and false values
        # Be careful with nested expressions
        true_false = rest.split(' : ', 1)
        if len(true_false) != 2:
            return

        true_value = true_false[0].strip()
        false_value = true_false[1].strip()

        # For template rendering, we'll create a special ternary element
        # which the generator can convert to Jinja's inline if
        self.elements.append(ContentElement(
            type='ternary',
            condition=condition,
            content=true_value,
            fallback_chain=[true_value, false_value]
        ))

    def _parse_jsx_element(self, jsx: str) -> Optional[Dict]:
        """Parse a JSX element to extract component name, props, and children.

        Args:
            jsx: JSX string like "<FieldsetLegend>{legend}</FieldsetLegend>"

        Returns:
            Dict with component, props, and children keys
        """
        # Match opening tag: <ComponentName props>
        match = re.match(r'<([A-Z]\w*)\s*([^>]*)>(.*?)</\1>', jsx, re.DOTALL)
        if not match:
            # Try self-closing tag
            match = re.match(r'<([A-Z]\w*)\s*([^/>]*)/>', jsx)
            if not match:
                return None

            component_name = match.group(1)
            props_str = match.group(2).strip()
            children = None
        else:
            component_name = match.group(1)
            props_str = match.group(2).strip()
            children_str = match.group(3).strip()

            # Extract variable from {variable}
            children = None
            if children_str.startswith('{') and children_str.endswith('}'):
                children = children_str[1:-1].strip()

        # Parse props
        props = self._parse_component_props(props_str) if props_str else {}

        return {
            'component': component_name,
            'props': props,
            'children': children
        }

    def _parse_fallback(self, expression: str) -> None:
        """Parse fallback rendering expression.

        Args:
            expression: Expression like "children || label"
        """
        parts = [p.strip() for p in expression.split(' || ')]

        self.elements.append(ContentElement(
            type='fallback',
            fallback_chain=parts
        ))

    def resolve_component_references(self, source_content: str) -> Dict[str, Dict]:
        """Resolve component variable references to their definitions.

        For example, if iconMarkup = <Icon .../>, return the Icon component info.

        Args:
            source_content: Full source file content

        Returns:
            Dict mapping variable names to component info
        """
        references = {}

        # Pattern: const varName = <ComponentName .../>
        pattern = r'const\s+(\w+)\s*=\s*<(\w+)\s+([^/>]*)/>'

        for match in re.finditer(pattern, source_content):
            var_name = match.group(1)
            component_name = match.group(2)
            props_str = match.group(3).strip()

            # Parse props
            props = self._parse_component_props(props_str)

            references[var_name] = {
                'component': component_name,
                'props': props
            }

        return references

    def _parse_component_props(self, props_str: str) -> Dict:
        """Parse component props from string.

        Args:
            props_str: Props string like 'icon={icon} size={size}'

        Returns:
            Dict of prop names to values
        """
        props = {}

        # Pattern: propName={value} or propName="value"
        pattern = r'(\w+)=(?:\{([^}]+)\}|"([^"]+)")'

        for match in re.finditer(pattern, props_str):
            prop_name = match.group(1)
            # Get either the {...} value or "..." value
            prop_value = match.group(2) if match.group(2) else match.group(3)
            props[prop_name] = prop_value

        return props
