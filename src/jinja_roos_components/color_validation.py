"""
Color validation system for ROOS components.

This module reads color definitions from the definitions.json file
and provides validation for color attributes.
"""

import json
from pathlib import Path
from typing import Set, Optional
import logging

logger = logging.getLogger(__name__)


class ColorValidator:
    """Validates colors against the ROOS color system."""
    
    def __init__(self):
        self._colors: Optional[Set[str]] = None
        self._definitions_path: Optional[Path] = None

    def _load_colors(self) -> Set[str]:
        """Load colors from the overall_definitions.json file."""
        if self._colors is not None:
            return self._colors

        colors = set()

        # Find the definitions file
        definitions_file = Path(__file__).parent / 'overall_definitions.json'
        if not definitions_file.exists():
            logger.warning("Could not find overall_definitions.json file, skipping color validation")
            return colors

        try:
            with open(definitions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract color names from the JSON
            # Colors can be either an array of strings or an array of objects
            color_list = data.get("colors", [])
            if isinstance(color_list, list) and color_list:
                if isinstance(color_list[0], dict):
                    # New format: array of color objects with metadata
                    colors.update(color['name'] for color in color_list)
                else:
                    # Old format: array of color name strings
                    colors.update(color_list)

            # Also allow empty string (default/no color)
            colors.add("")

            logger.debug(f"Loaded {len(colors)} colors from {definitions_file}")

        except Exception as e:
            logger.warning(f"Failed to load colors from {definitions_file}: {e}")

        self._colors = colors
        return colors
        
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


def get_colors_metadata() -> list[dict]:
    """
    Get full color metadata for documentation purposes.
    Returns list of color objects with name, hex, display_name, etc.
    """
    definitions_file = Path(__file__).parent / 'overall_definitions.json'


    try:
        with open(definitions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("colors", [])
    except Exception:
        return []