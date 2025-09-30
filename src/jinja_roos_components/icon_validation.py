"""
Icon validation system for ROOS components.

This module reads icon definitions from the types.ts file
and provides validation for icon attributes.
"""

import os
import re
from typing import Set, Optional
import logging

logger = logging.getLogger(__name__)


class IconValidator:
    """Validates icons against the RVO icon system."""
    
    def __init__(self):
        self._icons: Optional[Set[str]] = None
        self._types_file_path = None
        
    def _load_icons(self) -> Set[str]:
        """Load icons from the types.ts file."""
        if self._icons is not None:
            return self._icons
            
        icons = set()
        
        # Find the types.ts file
        types_file = self._find_types_file()
        if not types_file:
            logger.warning("Could not find types.ts file, skipping icon validation")
            return icons
            
        try:
            with open(types_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract icon names from TypeScript union type
            # Pattern matches: | 'icon-name'
            pattern = r"\|\s*'([^']+)'"
            matches = re.findall(pattern, content)
            
            icons.update(matches)
            
            # Also allow empty string (default/no icon)
            icons.add("")
            
            logger.debug(f"Loaded {len(icons)} icons from {types_file}")
            
        except Exception as e:
            logger.warning(f"Failed to load icons from {types_file}: {e}")
            
        self._icons = icons
        return icons
        
    def _find_types_file(self) -> Optional[str]:
        """Find the types.ts file."""
        if self._types_file_path:
            return self._types_file_path
            
        # Try to find it relative to this module
        current_dir = os.path.dirname(__file__)
        possible_paths = [
            os.path.join(current_dir, 'static', 'dist', '@nl-rvo', 'assets', 'icons', 'types.ts'),
            os.path.join(current_dir, '..', 'static', 'dist', '@nl-rvo', 'assets', 'icons', 'types.ts'),
            os.path.join(current_dir, 'static', 'dist', '@nl-rvo', 'assets', 'icons', 'types.ts'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self._types_file_path = path
                return path
                
        return None
        
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