"""
Enhanced HTML parser with component validation.

This module extends the base HTML parser to include strict validation
of components, attributes, and values according to the component registry.
"""

import logging
from typing import List, Dict, Any
from .html_parser import ComponentHTMLParser
from .validation import ComponentValidator, ComponentValidationError

logger = logging.getLogger(__name__)


class ValidatingComponentHTMLParser(ComponentHTMLParser):
    """
    Enhanced HTML parser that validates components during parsing.
    """
    
    def __init__(self, registry, strict_mode: bool = True):
        """
        Initialize validating parser.
        
        Args:
            registry: Component registry with definitions
            strict_mode: Whether to raise exceptions for validation errors
        """
        super().__init__(registry)
        self.validator = ComponentValidator(registry, strict_mode)
        self.strict_mode = strict_mode
        self.validation_errors = []
        
    def parse_components(self, source: str) -> List[Dict[str, Any]]:
        """Parse and validate component tags from HTML source."""
        self.validation_errors = []
        
        # Parse components first
        components = super().parse_components(source)
        
        # Validate each component
        for component in components:
            try:
                self.validator.validate_component(
                    component['component_name'],
                    component.get('attrs', {})
                )
            except ComponentValidationError as e:
                self.validation_errors.append({
                    'component': component['component_name'],
                    'position': component.get('start', 0),
                    'error': str(e)
                })
                
                if self.strict_mode:
                    # Include position information in the error
                    line_info = self._get_line_info(source, component.get('start', 0))
                    raise ComponentValidationError(f"{str(e)} (at line {line_info['line']}, column {line_info['column']})") from e
        
        return components
    
    def _get_line_info(self, source: str, position: int) -> Dict[str, int]:
        """Get line and column information for a position in the source."""
        lines = source[:position].split('\n')
        return {
            'line': len(lines),
            'column': len(lines[-1]) + 1 if lines else 1
        }
    
    def handle_starttag(self, tag: str, attrs: List[tuple]):
        """Override to add validation for unknown components."""
        if not tag.startswith('c-'):
            return
            
        component_name = tag[2:]  # Remove 'c-' prefix
        
        # Check if component exists
        if not self.registry.has_component(component_name):
            error_msg = f"Unknown component: 'c-{component_name}'. Available components: {', '.join(sorted(self.registry.list_components()))}"
            
            if self.strict_mode:
                # Try to find position information
                position = self.source.find(f'<{tag}', self.current_pos) if hasattr(self, 'source') else 0
                line_info = self._get_line_info(self.source, position) if hasattr(self, 'source') else {'line': 0, 'column': 0}
                raise ComponentValidationError(f"{error_msg} (at line {line_info['line']}, column {line_info['column']})")
            else:
                logger.warning(error_msg)
                return  # Skip processing this unknown component
        
        # Continue with normal processing
        super().handle_starttag(tag, attrs)
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of validation results."""
        return {
            'total_errors': len(self.validation_errors),
            'errors': self.validation_errors,
            'valid': len(self.validation_errors) == 0
        }


def create_validating_parser(registry, strict_mode: bool = True) -> ValidatingComponentHTMLParser:
    """
    Create a validating parser instance.
    
    Args:
        registry: Component registry
        strict_mode: Whether to raise exceptions for validation errors
        
    Returns:
        ValidatingComponentHTMLParser instance
    """
    return ValidatingComponentHTMLParser(registry, strict_mode)