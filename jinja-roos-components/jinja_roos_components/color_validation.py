"""
Color validation system for ROOS components.

This module reads color definitions from the colors.html.j2 template
and provides validation for color attributes.
"""

import os
import re
from typing import Set, Optional
import logging

logger = logging.getLogger(__name__)


class ColorValidator:
    """Validates colors against the ROOS color system."""
    
    def __init__(self):
        self._colors: Optional[Set[str]] = None
        self._colors_file_path = None
        
    def _load_colors(self) -> Set[str]:
        """Load colors from the colors.html.j2 template file."""
        if self._colors is not None:
            return self._colors
            
        colors = set()
        
        # Find the colors template file
        colors_file = self._find_colors_file()
        if not colors_file:
            logger.warning("Could not find colors.html.j2 file, skipping color validation")
            return colors
            
        try:
            with open(colors_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract color names from the Jinja template
            # Pattern matches: 'colorname': 'value',
            pattern = r"'([^']+)':\s*'var\(--rvo-color-[^']+\)'"
            matches = re.findall(pattern, content)
            
            colors.update(matches)
            
            # Also allow empty string (default/no color)
            colors.add("")
            
            logger.debug(f"Loaded {len(colors)} colors from {colors_file}")
            
        except Exception as e:
            logger.warning(f"Failed to load colors from {colors_file}: {e}")
            
        self._colors = colors
        return colors
        
    def _find_colors_file(self) -> Optional[str]:
        """Find the colors.html.j2 template file."""
        if self._colors_file_path:
            return self._colors_file_path
            
        # Try to find it relative to this module
        current_dir = os.path.dirname(__file__)
        possible_paths = [
            os.path.join(current_dir, 'templates', 'shared', 'colors.html.j2'),
            os.path.join(current_dir, '..', 'templates', 'shared', 'colors.html.j2'),
            os.path.join(current_dir, 'shared', 'colors.html.j2'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self._colors_file_path = path
                return path
                
        return None
        
    def is_valid_color(self, color: str) -> bool:
        """Check if a color is valid in the RVO color system."""
        colors = self._load_colors()
        return color in colors
        
    def get_available_colors(self) -> Set[str]:
        """Get all available colors."""
        return self._load_colors().copy()
        
    def get_color_suggestions(self, invalid_color: str, max_suggestions: int = 5) -> list[str]:
        """Get color suggestions for an invalid color."""
        colors = self._load_colors()
        
        if not invalid_color:
            return list(sorted(colors))[:max_suggestions]
            
        # Simple similarity matching - colors that start with the same prefix
        # or contain the invalid color as a substring
        suggestions = []
        invalid_lower = invalid_color.lower()
        
        for color in colors:
            if color and invalid_lower in color.lower():
                suggestions.append(color)
                
        # If no substring matches, try prefix matching
        if not suggestions:
            for color in colors:
                if color and color.lower().startswith(invalid_lower[:3]):
                    suggestions.append(color)
                    
        return sorted(suggestions)[:max_suggestions]


# Global instance
_color_validator = ColorValidator()


def validate_color(color: str) -> bool:
    """Validate a color value."""
    return _color_validator.is_valid_color(color)


def get_available_colors() -> Set[str]:
    """Get all available colors."""
    return _color_validator.get_available_colors()


def get_color_suggestions(invalid_color: str) -> list[str]:
    """Get suggestions for an invalid color."""
    return _color_validator.get_color_suggestions(invalid_color)