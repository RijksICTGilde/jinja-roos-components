"""Parse clsx() calls from React components to extract CSS class logic."""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ClassMapping:
    """Mapping of prop/value to CSS class."""
    prop_name: str
    value: Optional[str]  # None for boolean props
    css_class: str
    condition: str  # The condition as it appears in clsx


class ClsxParser:
    """Parser for clsx() function calls."""

    def __init__(self):
        self.mappings: List[ClassMapping] = []
        self.base_classes: List[str] = []

    def parse_clsx_call(self, clsx_content: str) -> List[ClassMapping]:
        """Parse a clsx() function call to extract class mappings.

        Args:
            clsx_content: Content inside clsx()

        Returns:
            List of ClassMapping objects
        """
        self.mappings = []
        self.base_classes = []

        # Split by commas at the top level (not inside quotes or parentheses)
        arguments = self._split_arguments(clsx_content)

        for arg in arguments:
            arg = arg.strip()

            # Skip className variable
            if arg == 'className':
                continue

            # String literals - base classes
            if (arg.startswith("'") and arg.endswith("'")) or \
               (arg.startswith('"') and arg.endswith('"')):
                # Extract the base class name
                class_name = arg.strip('\'"')
                self.base_classes.append(class_name)
                continue

            # Object literal: { 'class-name': condition, ... }
            if arg.startswith('{') and arg.endswith('}'):
                self._parse_object_literal(arg)
                continue

            # Template literals without condition (bare): `class-${var}`
            if arg.startswith('`') and arg.endswith('`') and ' && ' not in arg:
                self._parse_bare_template_literal(arg)
                continue

            # Conditional expressions: condition && 'class-name'
            if ' && ' in arg:
                self._parse_conditional(arg)

        return self.mappings

    def _parse_object_literal(self, obj_str: str) -> None:
        """Parse object literal like { 'class-name': condition, ... }.

        Args:
            obj_str: Object literal string like "{ 'class': cond, ... }"
        """
        # Remove outer braces
        obj_content = obj_str.strip()[1:-1].strip()

        # Split by commas (respecting nested structures)
        entries = self._split_object_entries(obj_content)

        for entry in entries:
            # Parse key: value pair
            # Pattern: 'class-name': condition
            match = re.match(r"['\"]([^'\"]+)['\"]:\s*(.+)", entry.strip())
            if not match:
                continue

            class_name = match.group(1)
            condition = match.group(2).strip().rstrip(',')

            # Handle different condition types
            # 1. Equality comparison: prop === 'value' or prop === value
            if ' === ' in condition:
                prop_part, value_part = condition.split(' === ', 1)
                prop_name = prop_part.strip()
                value = value_part.strip().strip('"\'')
                self.mappings.append(ClassMapping(
                    prop_name=prop_name,
                    value=value,
                    css_class=class_name,
                    condition=condition
                ))
            # 2. Inequality comparison: prop !== 'value'
            elif ' !== ' in condition:
                prop_part, value_part = condition.split(' !== ', 1)
                prop_name = prop_part.strip()
                value_clean = value_part.strip().strip('"\'')
                value = f'!{value_clean}'  # Mark as negated
                self.mappings.append(ClassMapping(
                    prop_name=prop_name,
                    value=value,
                    css_class=class_name,
                    condition=condition
                ))
            # 3. Negated boolean: !prop
            elif condition.startswith('!'):
                prop_name = condition[1:].strip()
                self.mappings.append(ClassMapping(
                    prop_name=prop_name,
                    value='false',
                    css_class=class_name,
                    condition=condition
                ))
            # 4. Simple boolean: prop
            else:
                prop_name = condition.strip()
                self.mappings.append(ClassMapping(
                    prop_name=prop_name,
                    value='true',
                    css_class=class_name,
                    condition=condition
                ))

    def _split_object_entries(self, content: str) -> List[str]:
        """Split object entries by commas.

        Args:
            content: Object content without outer braces

        Returns:
            List of key: value entries
        """
        entries = []
        current = []
        in_string = False
        string_char = None
        paren_depth = 0

        for i, char in enumerate(content):
            # Track strings
            if char in ('"', "'") and (i == 0 or content[i-1] != '\\\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False

            # Track parentheses/brackets
            if not in_string:
                if char in '([{':
                    paren_depth += 1
                elif char in ')]}':
                    paren_depth -= 1

                # Split on comma at top level
                if char == ',' and paren_depth == 0:
                    entries.append(''.join(current).strip())
                    current = []
                    continue

            current.append(char)

        # Add last entry
        if current:
            entries.append(''.join(current).strip())

        return entries

    def _split_arguments(self, content: str) -> List[str]:
        """Split clsx arguments by commas at the top level.

        Args:
            content: clsx content

        Returns:
            List of argument strings
        """
        args = []
        current = []
        paren_depth = 0
        in_string = False
        string_char = None

        for i, char in enumerate(content):
            # Track strings
            if char in ('"', "'", '`') and (i == 0 or content[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False

            # Track parentheses/brackets
            if not in_string:
                if char in '([{':
                    paren_depth += 1
                elif char in ')]}':
                    paren_depth -= 1

                # Split on comma at top level
                if char == ',' and paren_depth == 0:
                    args.append(''.join(current).strip())
                    current = []
                    continue

            current.append(char)

        # Add last argument
        if current:
            args.append(''.join(current).strip())

        return args

    def _parse_conditional(self, expression: str) -> None:
        """Parse a conditional expression like 'prop === value && class-name'.

        Now also supports compound conditions like:
        'type === "unordered" && noMargin && "rvo-ul--no-margin"'

        Args:
            expression: Conditional expression
        """
        # Pattern: condition && 'class-name' or condition && `template-${var}`
        # For compound conditions: cond1 && cond2 && 'class-name'
        parts = expression.split(' && ')
        if len(parts) < 2:
            return

        # The last part is always the class name or template literal
        class_part = parts[-1].strip()

        # Everything before the last part forms the compound condition
        if len(parts) == 2:
            # Simple condition: condition && 'class'
            condition = parts[0].strip()
        else:
            # Compound condition: cond1 && cond2 && ... && 'class'
            # Join all conditions except the last part
            condition_parts = [p.strip() for p in parts[:-1]]
            condition = ' && '.join(condition_parts)

        # Check if it's a template literal
        if class_part.startswith('`') and class_part.endswith('`'):
            self._parse_template_literal(condition, class_part)
            return

        # Check if it's a string concatenation: 'prefix-' + variable
        if ' + ' in class_part:
            self._parse_string_concatenation(condition, class_part)
            return

        # Remove quotes from regular class names
        class_part = class_part.strip("'\"")

        # Parse the condition
        # Patterns:
        # 1. prop === 'value'
        # 2. prop === value
        # 3. prop !== 'value' (not equal)
        # 4. prop (boolean)
        # 5. !prop (negated boolean)
        # 6. Compound conditions: cond1 && cond2 (added for ul/ol components)

        # Compound condition check (has && in the condition itself)
        if ' && ' in condition:
            # This is a compound condition like "type === 'unordered' && noMargin"
            # Store it with a special marker so it can be converted to Jinja as-is
            self.mappings.append(ClassMapping(
                prop_name='__COMPOUND__',  # Special marker for compound conditions
                value='__COMPOUND__',
                css_class=class_part,
                condition=condition
            ))
            return

        # Not equal check
        if ' !== ' in condition:
            # For template literals, this is handled in _parse_template_literal
            # For regular classes with !==, we can't easily convert without enum values
            # Mark as needing template literal or skip
            return

        # Equality check
        elif ' === ' in condition:
            prop_part, value_part = condition.split(' === ', 1)
            prop_name = prop_part.strip()
            value = value_part.strip().strip("'\"")

            self.mappings.append(ClassMapping(
                prop_name=prop_name,
                value=value,
                css_class=class_part,
                condition=condition
            ))

        # Equality check (==)
        elif ' == ' in condition:
            prop_part, value_part = condition.split(' == ', 1)
            prop_name = prop_part.strip()
            value = value_part.strip().strip("'\"")

            self.mappings.append(ClassMapping(
                prop_name=prop_name,
                value=value,
                css_class=class_part,
                condition=condition
            ))

        # Boolean check (negated)
        elif condition.startswith('!'):
            prop_name = condition[1:].strip()
            self.mappings.append(ClassMapping(
                prop_name=prop_name,
                value='false',
                css_class=class_part,
                condition=condition
            ))

        # Boolean check (positive)
        elif ' ' not in condition and '(' not in condition:
            prop_name = condition.strip()
            self.mappings.append(ClassMapping(
                prop_name=prop_name,
                value='true',
                css_class=class_part,
                condition=condition
            ))

    def _parse_string_concatenation(self, condition: str, class_expr: str) -> None:
        """Parse string concatenation expression like 'prefix-' + variable.

        Converts string concatenation to template literal format for uniform handling.

        Args:
            condition: Condition like 'color'
            class_expr: Expression like "'rvo-paragraph--' + color"
        """
        # Split on ' + ' to get parts
        parts = class_expr.split(' + ')

        # Convert to template literal format
        # 'prefix-' + var → prefix-${var}
        template_parts = []
        for part in parts:
            part = part.strip()
            # Check if it's a quoted string
            if (part.startswith("'") and part.endswith("'")) or \
               (part.startswith('"') and part.endswith('"')):
                # Remove quotes and add as literal
                template_parts.append(part.strip("'\""))
            else:
                # It's a variable, wrap in ${}
                template_parts.append(f"${{{part}}}")

        # Join parts to create template pattern
        template_pattern = ''.join(template_parts)

        # Extract variable name (the first variable part)
        var_match = re.search(r'\$\{([^}]+)\}', template_pattern)
        if not var_match:
            return

        var_name = var_match.group(1).strip()

        # Store as template mapping
        self.mappings.append(ClassMapping(
            prop_name=var_name,
            value='__TEMPLATE__',
            css_class=template_pattern,
            condition=condition
        ))

    def _parse_bare_template_literal(self, template: str) -> None:
        """Parse bare template literal without a condition.

        Examples:
        - `rvo-progress-tracker__step--${state}`
        - `rvo-progress-tracker__step--${line !== 'substep-start' ? size : 'md'}`
        - `rvo-image-bg-progress-tracker-${stateImageCssClassname}-${size}--after`

        Args:
            template: Template literal like '`class-${var}`'
        """
        template_pattern = template.strip('`')

        # Find all ${...} expressions
        expressions = re.findall(r'\$\{([^}]+)\}', template_pattern)

        if not expressions:
            return

        # For each expression, determine what it is:
        # 1. Simple variable: ${state}
        # 2. Ternary: ${cond ? val1 : val2}
        # 3. Variable reference: ${someVar} where someVar is computed

        for expr in expressions:
            expr = expr.strip()

            # Check if it's a ternary operator
            if '?' in expr and ':' in expr:
                self._parse_ternary_template(template_pattern, expr)
                return  # Ternary templates need special handling

        # For simple variables or variable references, mark as template for expansion
        # Use the first expression as the prop_name (might need refinement)
        primary_var = expressions[0].strip()

        self.mappings.append(ClassMapping(
            prop_name=primary_var,
            value='__TEMPLATE__',
            css_class=template_pattern,
            condition='__ALWAYS__'  # Special marker for always-included templates
        ))

    def _parse_ternary_template(self, template_pattern: str, ternary_expr: str) -> None:
        """Parse template literal containing a ternary operator.

        Example: `class--${line !== 'substep-start' ? size : 'md'}`

        Args:
            template_pattern: Full template pattern
            ternary_expr: The ternary expression like "line !== 'substep-start' ? size : 'md'"
        """
        # Parse ternary: condition ? trueVal : falseVal
        parts = ternary_expr.split('?')
        if len(parts) != 2:
            return

        condition = parts[0].strip()
        value_parts = parts[1].split(':')
        if len(value_parts) != 2:
            return

        true_val = value_parts[0].strip()
        false_val = value_parts[1].strip().strip("'\"")

        # Extract the property being checked (e.g., 'line' from "line !== 'substep-start'")
        if ' !== ' in condition:
            prop_name, excluded_value = condition.split(' !== ')
            prop_name = prop_name.strip()
            excluded_value = excluded_value.strip().strip("'\"")

            # The true_val might be another variable (e.g., 'size')
            # Store as special ternary template mapping
            self.mappings.append(ClassMapping(
                prop_name='__TERNARY__',  # Special marker
                value=f"{condition}?{true_val}:{false_val}",
                css_class=template_pattern,
                condition=f"__TERNARY__{condition}?{true_val}:{false_val}"
            ))

    def _parse_template_literal(self, condition: str, template: str) -> None:
        """Parse template literal like `utrecht-button--icon-${showIcon}`.

        This creates a TemplateLiteralMapping that will be expanded later
        when we have access to the enum values.

        Args:
            condition: Condition like 'showIcon !== "no"'
            template: Template literal like '`utrecht-button--icon-${showIcon}`'
        """
        # Extract variable from template
        # Pattern: `prefix-${varname}` or `${varname}-suffix`
        var_match = re.search(r'\$\{([^}]+)\}', template)
        if not var_match:
            return

        var_name = var_match.group(1).strip()
        template_pattern = template.strip('`')

        # Store as a special mapping that needs enum expansion
        # We'll mark it with a special marker so we can expand it later
        self.mappings.append(ClassMapping(
            prop_name=var_name,
            value='__TEMPLATE__',  # Special marker
            css_class=template_pattern,
            condition=condition
        ))

    def extract_from_jsx(self, jsx_content: str) -> List[ClassMapping]:
        """Extract class mappings from JSX content containing clsx() calls.

        Args:
            jsx_content: JSX content string

        Returns:
            List of ClassMapping objects
        """
        all_mappings = []

        # Find all clsx() calls
        # Pattern: clsx(...)
        pattern = r'clsx\s*\(((?:[^()]+|\([^()]*\))*)\)'

        for match in re.finditer(pattern, jsx_content, re.MULTILINE | re.DOTALL):
            clsx_content = match.group(1)
            mappings = self.parse_clsx_call(clsx_content)
            all_mappings.extend(mappings)

        return all_mappings

    def group_by_prop(self, mappings: Optional[List[ClassMapping]] = None) -> Dict[str, List[ClassMapping]]:
        """Group mappings by property name.

        Args:
            mappings: Optional list of mappings (uses self.mappings if None)

        Returns:
            Dict mapping prop names to lists of ClassMapping objects
        """
        if mappings is None:
            mappings = self.mappings

        grouped = {}
        for mapping in mappings:
            if mapping.prop_name not in grouped:
                grouped[mapping.prop_name] = []
            grouped[mapping.prop_name].append(mapping)

        return grouped

    def expand_template_literals(self, mappings: List[ClassMapping], attributes: List) -> List[ClassMapping]:
        """Expand template literal mappings using attribute enum values.

        Args:
            mappings: List of class mappings (may contain template markers)
            attributes: List of AttributeInfo with enum values

        Returns:
            Expanded list of class mappings
        """
        # Import here to avoid circular dependency
        from ..parsers.interface_parser import AttributeInfo

        expanded = []

        for mapping in mappings:
            if mapping.value == '__TEMPLATE__':
                # Find the attribute to get enum values
                attr = next((a for a in attributes if a.name == mapping.prop_name), None)
                if not attr or not attr.enum_values:
                    # Can't expand without enum values, but keep the template literal
                    # so the class builder can handle it (e.g., for computed variables like iconName)
                    expanded.append(mapping)
                    continue

                # Parse condition to get excluded values
                excluded_values = self._parse_exclusion_condition(mapping.condition)

                # Expand template for each non-excluded enum value
                for enum_value in attr.enum_values:
                    if enum_value in excluded_values:
                        continue

                    # Replace ${varname} with the enum value
                    css_class = re.sub(
                        r'\$\{[^}]+\}',
                        enum_value,
                        mapping.css_class
                    )

                    # Preserve the original compound condition
                    # If the original condition is not just __ALWAYS__, keep it and append the enum check
                    if mapping.condition and mapping.condition != '__ALWAYS__':
                        # The original condition might be: "type === 'unordered' && bulletType === 'icon'"
                        # We need to add: " && bulletIcon == 'option-1'"
                        new_condition = f"{mapping.condition} && {mapping.prop_name} == '{enum_value}'"
                    else:
                        # No original condition, just the enum check
                        new_condition = f"{mapping.prop_name} == '{enum_value}'"

                    expanded.append(ClassMapping(
                        prop_name=mapping.prop_name,
                        value=enum_value,
                        css_class=css_class,
                        condition=new_condition
                    ))
            else:
                # Keep non-template mappings as-is
                expanded.append(mapping)

        return expanded

    def _parse_exclusion_condition(self, condition: str) -> List[str]:
        """Parse a !== condition to extract excluded values.

        Args:
            condition: Condition like "showIcon !== 'no'"

        Returns:
            List of excluded values
        """
        excluded = []

        if ' !== ' in condition:
            parts = condition.split(' !== ')
            if len(parts) == 2:
                value = parts[1].strip().strip("'\"")
                excluded.append(value)

        return excluded

    def to_jinja_conditionals(self, mappings: Optional[List[ClassMapping]] = None) -> List[str]:
        """Convert mappings to Jinja conditional statements.

        Args:
            mappings: Optional list of mappings (uses self.mappings if None)

        Returns:
            List of Jinja conditional strings
        """
        if mappings is None:
            mappings = self.mappings

        jinja_lines = []

        # Group by prop for better organization
        grouped = self.group_by_prop(mappings)

        for prop_name, prop_mappings in grouped.items():
            # Check if it's an enum (multiple values)
            if len(prop_mappings) > 1 and all(m.value not in ('true', 'false', None) for m in prop_mappings):
                # Enum-style if/elif
                for i, mapping in enumerate(prop_mappings):
                    if i == 0:
                        jinja_lines.append(f"{{% if {prop_name} == '{mapping.value}' %}}")
                    else:
                        jinja_lines.append(f"{{% elif {prop_name} == '{mapping.value}' %}}")
                    jinja_lines.append(f"    {{% set css_classes = css_classes + ['{mapping.css_class}'] %}}")
                jinja_lines.append("{% endif %}")

            else:
                # Boolean or single value
                for mapping in prop_mappings:
                    if mapping.value == 'true':
                        condition = prop_name
                    elif mapping.value == 'false':
                        condition = f"not {prop_name}"
                    elif mapping.value:
                        condition = f"{prop_name} == '{mapping.value}'"
                    else:
                        condition = prop_name

                    jinja_lines.append(
                        f"{{% if {condition} %}}{{% set css_classes = css_classes + ['{mapping.css_class}'] %}}{{% endif %}}"
                    )

        return jinja_lines
