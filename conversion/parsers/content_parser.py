"""Parse JSX content/children rendering logic."""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ContentElement:
    """Represents a content element in JSX."""
    type: str  # 'conditional', 'fallback', 'text', 'component', 'variable', 'array_map', 'fallback_chain', 'children_passthrough', 'conditional_component'
    condition: Optional[str] = None  # For conditional rendering
    content: Optional[str] = None  # The actual content
    component_name: Optional[str] = None  # For component elements
    component_props: Optional[Dict] = None  # Props for components
    fallback_chain: Optional[List] = None  # For || operators (can be List[str] or List[Dict])
    fallback_value: Optional[str] = None  # Fallback value when condition is false (for conditional_component)
    # For array_map type:
    array_name: Optional[str] = None  # Name of array being mapped
    item_var: Optional[str] = None  # Variable name for each item
    is_spread: bool = False  # Whether props are spread ({...item})


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

    def _normalize_jsx_expression(self, expression: str) -> str:
        """Normalize JSX expression for consistent parsing.

        WARNING: This removes newlines and collapses whitespace, which may affect
        intentional formatting if the expression contains string literals with
        meaningful whitespace. However, for JSX code expressions (conditions,
        function calls, etc.), this is generally safe and necessary for robust parsing.

        Args:
            expression: Raw JSX expression

        Returns:
            Normalized expression with consistent whitespace
        """
        # Remove newlines and tabs (JSX code doesn't need them)
        normalized = expression.replace('\n', ' ').replace('\t', ' ')

        # Collapse multiple spaces to single space
        # NOTE: This may affect intentional double spaces in string literals
        normalized = re.sub(r'\s+', ' ', normalized)

        # Ensure consistent spacing around operators for easier parsing
        normalized = normalized.replace('||', ' || ')
        normalized = normalized.replace('&&', ' && ')

        # Clean up any extra spaces created
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

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

            # Normalize the expression for consistent parsing
            # This handles newlines, extra spaces, etc. in JSX code
            expression = self._normalize_jsx_expression(expression)

            # Check for fallback rendering first (highest priority for complex patterns)
            # Pattern: (children && ...) || (steps && ...)
            if ' || ' in expression:  # Now we can safely check with spaces
                self._parse_fallback(expression)
            # Check for ternary operator: condition ? value : fallback
            elif ' ? ' in expression and ' : ' in expression:
                self._parse_ternary(expression)
            # Check for .map() patterns (but not if already handled by fallback)
            elif '.map(' in expression:
                # Try to parse as array map
                map_element = self._parse_array_map(expression)
                if map_element:
                    self.elements.append(map_element)
                    continue
            # Check for conditional rendering: condition && element
            elif ' && ' in expression:
                self._parse_conditional(expression)
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

        NOTE: Expects normalized expression (from _normalize_jsx_expression).
        Operators like || and && should have consistent spacing.

        Args:
            expression: Normalized expression like "children || label" or
                       "(children && React.Children.map(...)) || (steps && steps.map(...))"
        """
        # Split on || (expression is already normalized, so spacing is consistent)
        parts = [p.strip() for p in expression.split(' || ')]

        # Check if this is a complex fallback with .map() patterns
        has_map = any('.map(' in part for part in parts)
        has_react_children = any('React.Children.map' in part for part in parts)

        if has_map or has_react_children:
            # Parse as complex fallback chain with conditional rendering
            parsed_parts = []

            for part in parts:
                if 'React.Children.map' in part:
                    # Extract condition variable from: "(children && React.Children.map(...))"
                    condition_match = re.match(r'\(?(\w+)\s+&&', part)
                    condition = condition_match.group(1) if condition_match else 'children'

                    parsed_parts.append({
                        'type': 'children_passthrough',
                        'condition': condition
                    })
                elif '.map(' in part:
                    # Parse array map
                    map_element = self._parse_array_map(part)
                    if map_element:
                        # Extract clean condition (remove wrapping parentheses if present)
                        condition = map_element.condition or map_element.array_name
                        condition = condition.strip('()')  # Remove any wrapping parens

                        parsed_parts.append({
                            'type': 'array_map',
                            'element': map_element,
                            'condition': condition
                        })

            # Create fallback chain element for if/elif generation
            if parsed_parts:
                self.elements.append(ContentElement(
                    type='fallback_chain',
                    fallback_chain=parsed_parts
                ))
                return

        # Simple fallback without .map() - handle as before
        self.elements.append(ContentElement(
            type='fallback',
            fallback_chain=parts
        ))

    def _parse_array_map(self, expression: str) -> Optional[ContentElement]:
        """Parse array.map() expression.

        Args:
            expression: Expression like "steps.map((step) => <Component {...step} />)"
                       or "steps && steps.map((step) => <Component {...step} />)"

        Returns:
            ContentElement with type='array_map' or None
        """
        # Pattern: arrayName.map((itemVar, index?) => <ComponentName .../>)
        # First, check for condition before .map() like "steps && steps.map(...)"
        condition = None
        map_expr = expression

        if ' && ' in expression:
            parts = expression.split(' && ', 1)
            if '.map(' in parts[1]:
                condition = parts[0].strip()
                map_expr = parts[1].strip()

        # Extract array name, item variable, and component
        # Pattern: arrayName.map((itemVar) => or arrayName.map((itemVar, index) =>
        map_pattern = r'(\w+)\.map\(\s*\((\w+)(?:,\s*\w+)?\)\s*=>\s*<(\w+)\s*([^/>]*?)\s*/?>.*?\)'

        match = re.search(map_pattern, map_expr, re.DOTALL)
        if not match:
            # Try React.Children.map pattern
            children_pattern = r'React\.Children\.map\((\w+),\s*\((\w+)(?:,\s*\w+)?\)\s*=>\s*.*?<(\w+)\s*([^/>]*?)\s*/?>.*?\)'
            match = re.search(children_pattern, map_expr, re.DOTALL)
            if match:
                array_name = match.group(1)
                item_var = match.group(2)
                component_name = match.group(3)
                props_str = match.group(4).strip()
            else:
                return None
        else:
            array_name = match.group(1)
            item_var = match.group(2)
            component_name = match.group(3)
            props_str = match.group(4).strip()

        # Check for prop spreading: {...itemVar}
        is_spread = f'...{item_var}' in props_str or f'...(child as any).props' in props_str

        # Parse component props if not spread
        component_props = {}
        if not is_spread and props_str:
            component_props = self._parse_component_props(props_str)

        return ContentElement(
            type='array_map',
            component_name=component_name,
            array_name=array_name,
            item_var=item_var,
            is_spread=is_spread,
            component_props=component_props,
            condition=condition
        )

    def resolve_component_references(self, source_content: str) -> Dict[str, Dict]:
        """Resolve component variable references to their definitions.

        For example, if iconMarkup = <Icon .../>, return the Icon component info.
        Also handles conditional assignments:
          let labelMarkup = label;
          if (condition) {
            labelMarkup = <Component .../>
          }

        Args:
            source_content: Full source file content

        Returns:
            Dict mapping variable names to component info
        """
        references = {}

        # Pattern 1: const varName = <ComponentName .../>
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

        # Pattern 2: Conditional assignment with component
        # let varName: type = defaultValue;
        # if (condition) {
        #   varName = <ComponentName .../>;
        # }
        conditional_pattern = r'let\s+(\w+)(?::\s*[^=]+)?\s*=\s*([^;]+);[\s\S]*?if\s*\(([^)]+)\)\s*\{[\s]*\1\s*=\s*<(\w+)\s+([^/>]*)/>[\s]*;?[\s]*\}'

        for match in re.finditer(conditional_pattern, source_content):
            var_name = match.group(1)
            default_value = match.group(2).strip()
            condition = match.group(3).strip()
            component_name = match.group(4)
            props_str = match.group(5).strip()

            # Parse props
            props = self._parse_component_props(props_str)

            references[var_name] = {
                'type': 'conditional',
                'default': default_value,
                'condition': condition,
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
