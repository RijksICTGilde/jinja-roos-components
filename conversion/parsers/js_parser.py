"""Parse compiled JavaScript from component libraries to extract rendering logic."""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class JSXElement:
    """Represents a JSX element from compiled JavaScript."""
    tag: str  # HTML tag name
    classes: List[str]  # Base CSS classes (non-conditional)
    conditional_classes: List[Dict[str, str]]  # Conditional classes with their conditions
    attributes: Dict[str, str]  # Other attributes
    children: Optional['JSXElement'] = None  # Nested JSX element


@dataclass
class ComponentRenderInfo:
    """Information about how a component renders."""
    name: str
    elements: List[JSXElement]  # All JSX elements (may be nested)
    primary_element: JSXElement  # The main/inner element to use


class ComponentLibraryJSParser:
    """Parser for compiled JavaScript from component libraries."""

    def __init__(self, library_name: str = None):
        """Initialize parser.

        Args:
            library_name: Name of the library (e.g., '@utrecht/component-library-react')
        """
        self.library_name = library_name
        self.cache: Dict[str, ComponentRenderInfo] = {}

    def parse_component(self, js_content: str, component_name: str) -> Optional[ComponentRenderInfo]:
        """Parse a component's rendering logic from compiled JavaScript.

        Args:
            js_content: Compiled JavaScript content
            component_name: Name of the component to extract

        Returns:
            ComponentRenderInfo or None if not found
        """
        # Check cache
        cache_key = f"{component_name}:{hash(js_content)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Find the component definition
        component_def = self._extract_component_definition(js_content, component_name)
        if not component_def:
            return None

        # Extract JSX rendering calls
        jsx_elements = self._parse_jsx_calls(component_def)
        if not jsx_elements:
            return None

        # Determine primary element (innermost/actual HTML element)
        primary = self._determine_primary_element(jsx_elements)

        result = ComponentRenderInfo(
            name=component_name,
            elements=jsx_elements,
            primary_element=primary
        )

        # Cache result
        self.cache[cache_key] = result
        return result

    def _extract_component_definition(self, js_content: str, component_name: str) -> Optional[str]:
        """Extract the component definition from JavaScript.

        Args:
            js_content: JavaScript content
            component_name: Component name to find

        Returns:
            Component definition string or None
        """
        # Find the start of the component definition
        start_pattern = rf"var {component_name}\s*=\s*(?:/\*.*?\*/)?\s*forwardRef"
        start_match = re.search(start_pattern, js_content)

        if not start_match:
            # Try without forwardRef
            start_pattern = rf"var {component_name}\s*=\s*function"
            start_match = re.search(start_pattern, js_content)

        if not start_match:
            return None

        start_pos = start_match.start()

        # Find the end by looking for the displayName or next var declaration
        end_pattern = rf"{component_name}\.displayName|^\s*var [A-Z]"
        end_match = re.search(end_pattern, js_content[start_pos + 100:], re.MULTILINE)

        if end_match:
            end_pos = start_pos + 100 + end_match.start()
        else:
            # Fallback: take next 2000 characters
            end_pos = start_pos + 2000

        component_def = js_content[start_pos:end_pos]
        return component_def

    def _parse_jsx_calls(self, component_def: str) -> List[JSXElement]:
        """Parse jsx() calls from component definition.

        Args:
            component_def: Component function body

        Returns:
            List of JSXElement objects
        """
        elements = []

        # Find all jsx() calls using position-based parsing
        pos = 0
        while True:
            # Find next jsx( call
            jsx_start = component_def.find('jsx("', pos)
            if jsx_start == -1:
                break

            # Extract the tag name
            tag_start = jsx_start + 5  # len('jsx("')
            tag_end = component_def.find('"', tag_start)
            if tag_end == -1:
                break

            tag = component_def[tag_start:tag_end]

            # Find the props - could be wrapped in _objectSpread or direct object
            # Look for the pattern after the tag: jsx("tag", <props>)
            # Skip past the closing quote and comma
            search_start = tag_end + 1

            # Skip whitespace and comma
            while search_start < len(component_def) and component_def[search_start] in ', \n\t':
                search_start += 1

            # Check if it's _objectSpread
            if component_def[search_start:search_start + 13] == '_objectSpread':
                # Find the last object in the _objectSpread chain
                # Pattern: _objectSpread(..., {...actual props...})
                props_str = self._extract_objectspread_props(component_def, search_start)
            else:
                # Direct object
                props_start = component_def.find('{', search_start)
                if props_start == -1:
                    pos = tag_end
                    continue
                props_str, _ = self._extract_balanced_braces(component_def, props_start)

            if props_str:
                element = self._parse_jsx_element(tag, props_str)
                if element:
                    elements.append(element)
                    pos = search_start + len(props_str)
            else:
                pos = tag_end + 1

        return elements

    def _extract_objectspread_props(self, text: str, start: int) -> Optional[str]:
        """Extract the props object from _objectSpread call.

        The pattern is: _objectSpread$X(_objectSpread$X({}, restProps), {}, {actual props})
        We want the last object which contains the actual props.

        Args:
            text: Text to parse
            start: Start position (at _objectSpread)

        Returns:
            Props string or None
        """
        # Find all objects in the _objectSpread chain
        objects = []

        # Find opening paren of _objectSpread
        paren_start = text.find('(', start)
        if paren_start == -1:
            return None

        # Track all { } objects within the _objectSpread call
        pos = paren_start + 1
        depth = 1  # We're inside the opening paren

        while pos < len(text) and depth > 0:
            char = text[pos]

            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            elif char == '{':
                # Found an object - extract it
                obj_str, obj_end = self._extract_balanced_braces(text, pos)
                if obj_str and len(obj_str) > 2:  # Not empty {}
                    objects.append(obj_str)
                pos = obj_end - 1  # -1 because we'll increment below

            pos += 1

        # Return the last non-empty object (the actual props)
        for obj in reversed(objects):
            if obj != '{}' and 'className' in obj:
                return obj

        # Fallback to last object
        return objects[-1] if objects else None

    def _extract_balanced_braces(self, text: str, start: int) -> Tuple[str, int]:
        """Extract content within balanced braces.

        Args:
            text: Text to parse
            start: Starting position (should be at '{')

        Returns:
            Tuple of (content_including_braces, end_position)
        """
        if start >= len(text) or text[start] != '{':
            return None, start

        depth = 0
        in_string = False
        string_char = None
        escaped = False

        for i in range(start, len(text)):
            char = text[i]

            if escaped:
                escaped = False
                continue

            if char == '\\':
                escaped = True
                continue

            if char in ('"', "'") and not in_string:
                in_string = True
                string_char = char
            elif char == string_char and in_string:
                in_string = False
                string_char = None
            elif not in_string:
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        return text[start:i + 1], i + 1

        return None, start

    def _parse_jsx_element(self, tag: str, props_str: str) -> Optional[JSXElement]:
        """Parse a single JSX element's properties.

        Args:
            tag: HTML tag name
            props_str: Props object string from jsx() call

        Returns:
            JSXElement or None
        """
        # Extract className with clsx() call
        classes, conditional_classes = self._parse_clsx(props_str)

        # Extract other attributes
        attributes = self._extract_attributes(props_str)

        # Check for nested children jsx call
        children = None
        children_match = re.search(r'children:\s*jsx\("([^"]+)",\s*({[^}]*})\)', props_str)
        if children_match:
            child_tag = children_match.group(1)
            child_props = children_match.group(2)
            children = self._parse_jsx_element(child_tag, child_props)

        return JSXElement(
            tag=tag,
            classes=classes,
            conditional_classes=conditional_classes,
            attributes=attributes,
            children=children
        )

    def _parse_clsx(self, props_str: str) -> Tuple[List[str], List[Dict[str, str]]]:
        """Parse clsx() call to extract CSS classes.

        Args:
            props_str: Props string containing className with clsx()

        Returns:
            Tuple of (base_classes, conditional_classes)
        """
        base_classes = []
        conditional_classes = []

        # Find className: clsx(...)
        clsx_match = re.search(r'className:\s*clsx\(([^)]+(?:\([^)]*\))*)\)', props_str)
        if not clsx_match:
            return base_classes, conditional_classes

        clsx_content = clsx_match.group(1)

        # Split by commas (but not inside parens/quotes)
        parts = self._split_clsx_args(clsx_content)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Check if it's a string literal (base class)
            if part.startswith("'") or part.startswith('"'):
                class_name = part.strip("'\"")
                base_classes.append(class_name)

            # Check if it's a conditional (prop && 'class')
            elif '&&' in part:
                condition_match = re.match(r'([^&]+)\s*&&\s*[\'"](.*?)[\'"]', part)
                if condition_match:
                    condition = condition_match.group(1).strip()
                    class_name = condition_match.group(2)
                    conditional_classes.append({
                        'condition': condition,
                        'class': class_name
                    })

            # It's a variable (like className prop being passed through)
            else:
                # Skip variable references for now
                pass

        return base_classes, conditional_classes

    def _split_clsx_args(self, clsx_content: str) -> List[str]:
        """Split clsx arguments by commas, respecting nested structures.

        Args:
            clsx_content: Content inside clsx()

        Returns:
            List of argument strings
        """
        parts = []
        current = []
        depth = 0
        in_string = False
        string_char = None

        for char in clsx_content:
            if char in ('"', "'") and not in_string:
                in_string = True
                string_char = char
                current.append(char)
            elif char == string_char and in_string:
                in_string = False
                string_char = None
                current.append(char)
            elif char == '(' and not in_string:
                depth += 1
                current.append(char)
            elif char == ')' and not in_string:
                depth -= 1
                current.append(char)
            elif char == ',' and depth == 0 and not in_string:
                parts.append(''.join(current))
                current = []
            else:
                current.append(char)

        if current:
            parts.append(''.join(current))

        return parts

    def _extract_attributes(self, props_str: str) -> Dict[str, str]:
        """Extract non-className attributes from props.

        Args:
            props_str: Props object string

        Returns:
            Dictionary of attributes
        """
        attributes = {}

        # Look for simple attribute patterns: "attr-name": value
        attr_pattern = r'["\']([a-z-]+)["\']\s*:\s*([^,}\n]+)'

        for match in re.finditer(attr_pattern, props_str):
            attr_name = match.group(1)
            attr_value = match.group(2).strip()

            # Skip special props
            if attr_name in ('className', 'children', 'ref'):
                continue

            # Clean up the value
            if attr_value.endswith(','):
                attr_value = attr_value[:-1].strip()

            attributes[attr_name] = attr_value

        return attributes

    def _determine_primary_element(self, elements: List[JSXElement]) -> JSXElement:
        """Determine which element is the primary/actual HTML element.

        For nested structures like div > fieldset, we want the fieldset.

        Args:
            elements: List of JSX elements

        Returns:
            Primary element
        """
        if not elements:
            return None

        # If only one element, that's it
        if len(elements) == 1:
            element = elements[0]
            # But check if it has a child element
            if element.children:
                return element.children
            return element

        # For multiple elements, prefer the innermost one
        # or the one that's not a generic wrapper (not div/span)
        for element in reversed(elements):
            if element.tag not in ('div', 'span'):
                return element

        # Fallback to last element
        return elements[-1]


def parse_utrecht_library(component_name: str) -> Optional[ComponentRenderInfo]:
    """Parse a component from Utrecht component library.

    Args:
        component_name: Name of the component (e.g., 'Fieldset')

    Returns:
        ComponentRenderInfo or None if not found
    """
    # Find Utrecht component library
    from pathlib import Path

    # Look for it in RVO's node_modules
    utrecht_path = Path(__file__).parent.parent.parent.parent / 'rvo' / 'node_modules' / '@utrecht' / 'component-library-react'

    if not utrecht_path.exists():
        return None

    # Read the compiled ESM JavaScript
    esm_path = utrecht_path / 'dist' / 'index.esm.js'
    if not esm_path.exists():
        return None

    js_content = esm_path.read_text(encoding='utf-8')

    # Parse the component
    parser = ComponentLibraryJSParser('@utrecht/component-library-react')
    return parser.parse_component(js_content, component_name)
