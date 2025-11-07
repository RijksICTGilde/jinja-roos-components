"""
Icon validation system for ROOS components.

This module reads icon definitions from the definitions.json file
and provides validation for icon attributes.
"""

import json
from pathlib import Path
from typing import Set, Optional
import logging

logger = logging.getLogger(__name__)


class IconValidator:
    """Validates icons against the RVO icon system."""
    
    def __init__(self):
        self._icons: Optional[Set[str]] = None
        self._definitions_path: Optional[Path] = None

    def _load_icons(self) -> Set[str]:
        """Load icons from the overall_definitions.json file."""
        if self._icons is not None:
            return self._icons

        icons = set()

        # Find the definitions file
        definitions_file = Path(__file__).parent / 'overall_definitions.json'
        if not definitions_file.exists():
            logger.warning("Could not find overall_definitions.json file, skipping icon validation")
            return icons

        try:
            with open(definitions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract icon names from the JSON
            # Icons can be either an array of strings or an array of objects
            icon_list = data.get("icons", [])
            if isinstance(icon_list, list) and icon_list:
                if isinstance(icon_list[0], dict):
                    # New format: array of icon objects with metadata
                    icons.update(icon['name'] for icon in icon_list)
                else:
                    # Old format: array of icon name strings
                    icons.update(icon_list)

            # Also allow empty string (default/no icon)
            icons.add("")

            logger.debug(f"Loaded {len(icons)} icons from {definitions_file}")

        except Exception as e:
            logger.warning(f"Failed to load icons from {definitions_file}: {e}")

        self._icons = icons
        return icons
        
    def is_valid_icon(self, icon: str) -> bool:
        """Check if an icon is valid in the RVO icon system."""
        icons = self._load_icons()
        return icon in icons
        
    def get_available_icons(self) -> Set[str]:
        """Get all available icons."""
        return self._load_icons().copy()
        
    def get_icon_suggestions(self, invalid_icon: str, max_suggestions: int = 5) -> list[str]:
        """Get icon suggestions for an invalid icon."""
        icons = self._load_icons()
        
        if not invalid_icon:
            return list(sorted(icons))[:max_suggestions]
            
        # Simple similarity matching - icons that contain the invalid icon as a substring
        # or have similar prefixes
        suggestions = []
        invalid_lower = invalid_icon.lower()
        
        # First, look for exact substring matches
        for icon in icons:
            if icon and invalid_lower in icon.lower():
                suggestions.append(icon)
                
        # If no substring matches, try prefix matching
        if not suggestions:
            for icon in icons:
                if icon and icon.lower().startswith(invalid_lower[:3]):
                    suggestions.append(icon)
                    
        # If still no matches, try common icon patterns and translations
        if not suggestions:
            # Common English to Dutch translations for icons
            translations = {
                'search': 'zoek',
                'download': 'downloaden', 
                'upload': 'upload',
                'calendar': 'kalender',
                'phone': 'telefoon',
                'print': 'printer',
                'save': 'save',
                'delete': 'verwijderen',
                'edit': 'bewerken',
                'settings': 'instellingen'
            }
            
            # Check if the invalid icon has a known translation
            dutch_equivalent = translations.get(invalid_lower)
            if dutch_equivalent and dutch_equivalent in icons:
                suggestions.append(dutch_equivalent)
            
            # If still no matches, try common icon patterns
            if not suggestions:
                common_patterns = ['home', 'menu', 'info', 'mail', 'user', 'kalender', 'downloaden']
                for pattern in common_patterns:
                    for icon in icons:
                        if icon and pattern in icon.lower():
                            suggestions.append(icon)
                            if len(suggestions) >= max_suggestions:
                                break
                    if len(suggestions) >= max_suggestions:
                        break
                    
        return sorted(suggestions)[:max_suggestions]


# Global instance
_icon_validator = IconValidator()


def validate_icon(icon: str) -> bool:
    """Validate an icon value."""
    return _icon_validator.is_valid_icon(icon)


def get_available_icons() -> Set[str]:
    """Get all available icons."""
    return _icon_validator.get_available_icons()


def get_icon_suggestions(invalid_icon: str) -> list[str]:
    """Get suggestions for an invalid icon."""
    return _icon_validator.get_icon_suggestions(invalid_icon)


def get_icons_metadata() -> list[dict]:
    """
    Get full icon metadata for documentation purposes.
    Returns list of icon objects with name, category, display_name, etc.
    """
    definitions_file = _icon_validator._find_definitions_file()
    if not definitions_file:
        return []

    try:
        with open(definitions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("icons", [])
    except Exception:
        return []