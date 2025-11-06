"""
Component validation system for strict error handling.

This module provides comprehensive validation for component usage,
including unknown components, invalid attributes, and enum value validation.
"""

import logging
from typing import Dict, Any, List, Optional
from .registry import ComponentRegistry, AttributeType

logger = logging.getLogger(__name__)


# Valid values for utility attributes (from _attribute_mixin.j2)
VALID_TEXT_STYLES = {
    'subtle', 'sm', 'md', 'lg', 'xl',
    'error', 'bold', 'italic', 'no-margins'
}

VALID_SPACING_SIZES = {
    'none', '3xs', '2xs', 'xs', 'sm', 'md', 'lg', 'xl',
    '2xl', '3xl', '4xl', '5xl'
}

VALID_SPACING_DIRECTIONS = {
    'inline-start', 'inline-end', 'block-start', 'block-end'
}


class ComponentValidationError(Exception):
    """Exception raised when component validation fails."""
    pass


class ComponentValidator:
    """Validates component usage against registry definitions."""
    
    def __init__(self, registry: ComponentRegistry, strict_mode: bool = True):
        """
        Initialize validator.
        
        Args:
            registry: Component registry with definitions
            strict_mode: Whether to raise exceptions for validation errors
        """
        self.registry = registry
        self.strict_mode = strict_mode
        
    def validate_component(self, component_name: str, attributes: Dict[str, Any]) -> None:
        """
        Validate a component and its attributes.
        
        Args:
            component_name: Name of the component (without 'c-' prefix)
            attributes: Dictionary of component attributes
            
        Raises:
            ComponentValidationError: If validation fails and strict_mode is True
        """
        # 1. Check if component exists
        if not self.registry.has_component(component_name):
            error_msg = f"Unknown component: 'c-{component_name}'. Available components: {', '.join(sorted(self.registry.list_components()))}"
            if self.strict_mode:
                raise ComponentValidationError(error_msg)
            else:
                logger.warning(error_msg)
                return
        
        component_def = self.registry.get_component(component_name)
        if not component_def:
            return
            
        # 2. Validate each attribute
        for attr_name, attr_value in attributes.items():
            self._validate_attribute(component_name, attr_name, attr_value, component_def)
            
        # 3. Check for required attributes
        self._validate_required_attributes(component_name, attributes, component_def)
    
    def _validate_attribute(self, component_name: str, attr_name: str, attr_value: Any, component_def) -> None:
        """Validate a single attribute."""
        # Check if attribute exists
        attr_def = component_def.get_attribute(attr_name)
        if not attr_def:
            # Skip common HTML attributes and Vue.js directives
            if self._is_allowed_generic_attribute(attr_name):
                # Validate utility attribute values if applicable
                if attr_name in ('text-style', 'margin', 'padding'):
                    self._validate_utility_attribute(component_name, attr_name, attr_value)
                return

            available_attrs = [attr.name for attr in component_def.attributes]
            error_msg = f"Unknown attribute '{attr_name}' for component 'c-{component_name}'. Available attributes: {', '.join(sorted(available_attrs))}"
            if self.strict_mode:
                raise ComponentValidationError(error_msg)
            else:
                logger.warning(error_msg)
                return

        # Validate attribute value based on type
        self._validate_attribute_value(component_name, attr_name, attr_value, attr_def)
    
    def _validate_attribute_value(self, component_name: str, attr_name: str, attr_value: Any, attr_def) -> None:
        """Validate attribute value based on its type definition."""
        # Check for None value (shorthand notation)
        if attr_value is None:
            # Shorthand notation is only allowed for boolean attributes
            if attr_def.type == AttributeType.BOOLEAN:
                # Shorthand notation for boolean attributes means true
                return

            # For non-boolean attributes, shorthand notation is not supported
            type_hint = {
                AttributeType.STRING: 'a string value (e.g., title="My Title")',
                AttributeType.NUMBER: 'a number value (e.g., count="5")',
                AttributeType.ENUM: f'one of: {", ".join(attr_def.enum_values)}' if attr_def.enum_values else 'a valid enum value',
                AttributeType.OBJECT: 'an object value'
            }.get(attr_def.type, 'a value')

            error_msg = f"Shorthand notation is not supported for attribute '{attr_name}' in component 'c-{component_name}'. Please provide {type_hint}."
            if self.strict_mode:
                raise ComponentValidationError(error_msg)
            else:
                logger.warning(error_msg)
                return

        # Skip validation for jinja template expressions
        if isinstance(attr_value, str) and ('{{' in attr_value or '{%' in attr_value):
            return
        if attr_def.type == AttributeType.ENUM:
            # For enum types, validate the value is in allowed values
            if attr_def.enum_values and attr_value not in attr_def.enum_values:
                error_msg = f"Invalid value '{attr_value}' for attribute '{attr_name}' in component 'c-{component_name}'. Allowed values: {', '.join(attr_def.enum_values)}"
                if self.strict_mode:
                    raise ComponentValidationError(error_msg)
                else:
                    logger.warning(error_msg)
        
        elif attr_def.type == AttributeType.STRING and (attr_name == 'color' or attr_name.endswith('Color')):
            # Special validation for color attributes (color, iconColor, backgroundColor, etc.)
            from .color_validation import validate_color, get_color_suggestions
            if attr_value and not validate_color(attr_value):
                suggestions = get_color_suggestions(attr_value)
                suggestion_text = f" Did you mean: {', '.join(suggestions[:3])}?" if suggestions else ""
                error_msg = f"Invalid color '{attr_value}' for attribute '{attr_name}' in component 'c-{component_name}'.{suggestion_text}"
                if self.strict_mode:
                    raise ComponentValidationError(error_msg)
                else:
                    logger.warning(error_msg)
        
        elif attr_def.type == AttributeType.STRING and attr_name == 'icon':
            # Special validation for icon attributes
            from .icon_validation import validate_icon, get_icon_suggestions
            if attr_value and not validate_icon(attr_value):
                suggestions = get_icon_suggestions(attr_value)
                suggestion_text = f" Did you mean: {', '.join(suggestions[:3])}?" if suggestions else ""
                error_msg = f"Invalid icon '{attr_value}' for attribute '{attr_name}' in component 'c-{component_name}'.{suggestion_text}"
                if self.strict_mode:
                    raise ComponentValidationError(error_msg)
                else:
                    logger.warning(error_msg)
        
        elif attr_def.type == AttributeType.BOOLEAN:
            # Boolean attributes should be 'true', 'false', or boolean-like
            if isinstance(attr_value, str) and attr_value.lower() not in ['true', 'false', '']:
                error_msg = f"Invalid boolean value '{attr_value}' for attribute '{attr_name}' in component 'c-{component_name}'. Expected: 'true' or 'false'"
                if self.strict_mode:
                    raise ComponentValidationError(error_msg)
                else:
                    logger.warning(error_msg)
        
        elif attr_def.type == AttributeType.NUMBER:
            # Try to parse as number
            if isinstance(attr_value, str):
                try:
                    float(attr_value)
                except ValueError:
                    error_msg = f"Invalid number value '{attr_value}' for attribute '{attr_name}' in component 'c-{component_name}'"
                    if self.strict_mode:
                        raise ComponentValidationError(error_msg)
                    else:
                        logger.warning(error_msg)
    
    def _validate_required_attributes(self, component_name: str, attributes: Dict[str, Any], component_def) -> None:
        """Check that all required attributes are present."""
        for attr_def in component_def.attributes:
            if attr_def.required and attr_def.name not in attributes:
                error_msg = f"Missing required attribute '{attr_def.name}' for component 'c-{component_name}'"
                if self.strict_mode:
                    raise ComponentValidationError(error_msg)
                else:
                    logger.warning(error_msg)

    def _validate_utility_attribute(self, component_name: str, attr_name: str, attr_value: str) -> None:
        """
        Validate utility attribute values (text-style, margin, padding).
        Raises ComponentValidationError if the value is invalid.
        """
        # Skip validation for jinja template expressions
        if isinstance(attr_value, str) and ('{{' in attr_value or '{%' in attr_value):
            return

        # Split multi-value attributes (space or comma separated)
        raw_value = attr_value.replace(',', ' ')
        values = raw_value.split()

        if attr_name == 'text-style':
            for value in values:
                if value not in VALID_TEXT_STYLES:
                    error_msg = f"Invalid value '{value}' for 'text-style' attribute in component 'c-{component_name}'. Valid values: {', '.join(sorted(VALID_TEXT_STYLES))}"
                    if self.strict_mode:
                        raise ComponentValidationError(error_msg)
                    else:
                        logger.warning(error_msg)

        elif attr_name in ('margin', 'padding'):
            for value in values:
                # Check if it's a directional pattern (e.g., "inline-end-sm")
                if '-' in value and value.count('-') >= 2:
                    parts = value.split('-')
                    if len(parts) == 3:
                        direction = f"{parts[0]}-{parts[1]}"
                        size = parts[2]

                        if direction not in VALID_SPACING_DIRECTIONS:
                            error_msg = f"Invalid direction '{direction}' in '{attr_name}' attribute value '{value}' in component 'c-{component_name}'. Valid directions: {', '.join(sorted(VALID_SPACING_DIRECTIONS))}"
                            if self.strict_mode:
                                raise ComponentValidationError(error_msg)
                            else:
                                logger.warning(error_msg)

                        if size not in VALID_SPACING_SIZES:
                            error_msg = f"Invalid size '{size}' in '{attr_name}' attribute value '{value}' in component 'c-{component_name}'. Valid sizes: {', '.join(sorted(VALID_SPACING_SIZES))}"
                            if self.strict_mode:
                                raise ComponentValidationError(error_msg)
                            else:
                                logger.warning(error_msg)
                    else:
                        error_msg = f"Invalid directional pattern '{value}' in '{attr_name}' attribute in component 'c-{component_name}'. Expected format: {{direction}}-{{size}} (e.g., 'inline-end-sm')"
                        if self.strict_mode:
                            raise ComponentValidationError(error_msg)
                        else:
                            logger.warning(error_msg)
                else:
                    # Simple size value
                    if value not in VALID_SPACING_SIZES:
                        error_msg = f"Invalid value '{value}' for '{attr_name}' attribute in component 'c-{component_name}'. Valid values: {', '.join(sorted(VALID_SPACING_SIZES))} or directional patterns like 'inline-end-sm'"
                        if self.strict_mode:
                            raise ComponentValidationError(error_msg)
                        else:
                            logger.warning(error_msg)

    def _is_allowed_generic_attribute(self, attr_name: str) -> bool:
        """Check if an attribute is a common HTML or framework attribute that should be allowed."""
        allowed_generic = {
            # Common HTML attributes
            'id', 'class', 'style', 'data-*', 'aria-*', 'role', 'tabindex',
            # Vue.js directives and bindings
            'v-if', 'v-else', 'v-else-if', 'v-show', 'v-for', 'v-model',
            'v-bind', 'v-on', '@click', '@change', '@input', '@submit',
            # Vue.js binding syntax
            ':class', ':style', ':id', ':disabled', ':checked', ':value',
            # Event handlers
            'onclick', 'onchange', 'oninput', 'onsubmit', 'onload',
            # Form attributes
            'name', 'value', 'checked', 'disabled', 'readonly', 'required',
            'placeholder', 'maxlength', 'minlength', 'pattern', 'autocomplete',
            # Link attributes
            'href', 'target', 'rel', 'download',
            # Image attributes
            'src', 'alt', 'width', 'height',
            # Utility attributes from _attribute_mixin.j2 (available to all components)
            'text-style', 'margin', 'padding',
        }

        # Check exact matches
        if attr_name in allowed_generic:
            return True

        # Check patterns (data-*, aria-*, @hx-*, hx-*, etc.)
        patterns = ['data-', 'aria-', 'v-', '@', ':', 'hx-']
        for pattern in patterns:
            if attr_name.startswith(pattern):
                return True

        return False


def validate_template_components(template_source: str, registry: ComponentRegistry, strict_mode: bool = True) -> List[Dict[str, Any]]:
    """
    Validate all components in a template.
    
    Args:
        template_source: The template source code
        registry: Component registry
        strict_mode: Whether to raise exceptions for errors
        
    Returns:
        List of validation results
        
    Raises:
        ComponentValidationError: If validation fails and strict_mode is True
    """
    from .html_parser import ComponentHTMLParser
    
    validator = ComponentValidator(registry, strict_mode)
    parser = ComponentHTMLParser(registry)
    
    try:
        components = parser.parse_components(template_source)
        
        validation_results = []
        for component in components:
            try:
                validator.validate_component(
                    component['component_name'], 
                    component.get('attrs', {})
                )
                validation_results.append({
                    'component': component['component_name'],
                    'valid': True,
                    'errors': []
                })
            except ComponentValidationError as e:
                validation_results.append({
                    'component': component['component_name'], 
                    'valid': False,
                    'errors': [str(e)]
                })
                if strict_mode:
                    raise
                    
        return validation_results
        
    except Exception as e:
        error_msg = f"Template parsing failed: {e}"
        if strict_mode:
            raise ComponentValidationError(error_msg) from e
        else:
            logger.error(error_msg)
            return []