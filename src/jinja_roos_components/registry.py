"""
Component registry for managing component metadata and validation.
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class AttributeType(Enum):
    """Types of component attributes."""
    STRING = "string"
    BOOLEAN = "boolean" 
    NUMBER = "number"
    ENUM = "enum"
    OBJECT = "object"


@dataclass
class AttributeDefinition:
    """Definition of a component attribute."""
    name: str
    type: AttributeType
    required: bool = False
    default: Any = None
    description: str = ""
    enum_values: Optional[List[str]] = None
    
    def __post_init__(self) -> None:
        if self.type == AttributeType.ENUM and not self.enum_values:
            raise ValueError("Enum attributes must specify enum_values")


@dataclass
class ComponentAlias:
    """Definition of a component alias."""
    name: str  # Alias name (e.g., "h1")
    target_component: str  # Target component name (e.g., "header")
    default_attributes: Dict[str, Any] = field(default_factory=dict)  # Pre-filled attributes
    description: str = ""


@dataclass 
class ComponentDefinition:
    """Definition of a component."""
    name: str
    description: str
    attributes: List[AttributeDefinition] = field(default_factory=list)
    slots: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    allow_preview: bool = True  # Whether this component can be shown in preview
    requires_children: bool = False  # Whether this component needs child content
    preview_example: Optional[str] = None  # Specific example for preview (if different from main example)
    
    def get_attribute(self, name: str) -> Optional[AttributeDefinition]:
        """Get attribute definition by name."""
        for attr in self.attributes:
            if attr.name == name:
                return attr
        return None
    
    def has_attribute(self, name: str) -> bool:
        """Check if component has an attribute."""
        return self.get_attribute(name) is not None


class ComponentRegistry:
    """Registry for managing component definitions."""
    
    def __init__(self) -> None:
        self._components: Dict[str, ComponentDefinition] = {}
        self._aliases: Dict[str, ComponentAlias] = {}
        self._register_default_components()
        self._register_default_aliases()
        self._register_conversion_components()  # Auto-discover from conversion/definitions/
    
    def register_component(self, component: ComponentDefinition) -> None:
        """Register a new component."""
        self._components[component.name] = component
    
    def has_component(self, name: str) -> bool:
        """Check if a component is registered."""
        return name in self._components or name in self._aliases
    
    def get_component(self, name: str) -> Optional[ComponentDefinition]:
        """Get component definition by name."""
        # First check direct components
        if name in self._components:
            return self._components[name]
        
        # Then check if it's an alias
        if name in self._aliases:
            alias = self._aliases[name]
            return self._components.get(alias.target_component)
        
        return None
    
    def list_components(self) -> List[str]:
        """List all registered component names (including aliases)."""
        return list(self._components.keys()) + list(self._aliases.keys())
    
    def get_all_component_names(self) -> List[str]:
        """Get all registered component names (alias for list_components)."""
        return self.list_components()
    
    def get_component_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get component metadata as dictionary."""
        component = self.get_component(name)
        if not component:
            return None
            
        return {
            'name': component.name,
            'description': component.description,
            'attributes': [
                {
                    'name': attr.name,
                    'type': attr.type.value,
                    'required': attr.required,
                    'default': attr.default,
                    'description': attr.description,
                    'enum_values': attr.enum_values,
                }
                for attr in component.attributes
            ],
            'slots': component.slots,
            'examples': component.examples,
            'allow_preview': component.allow_preview,
            'requires_children': component.requires_children,
            'preview_example': component.preview_example,
        }
    
    def register_alias(self, alias: ComponentAlias) -> None:
        """Register a component alias."""
        self._aliases[alias.name] = alias
    
    def has_alias(self, name: str) -> bool:
        """Check if a name is an alias."""
        return name in self._aliases
    
    def get_alias(self, name: str) -> Optional[ComponentAlias]:
        """Get alias definition by name."""
        return self._aliases.get(name)
    
    def resolve_alias(self, alias_name: str, user_attributes: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Resolve an alias to its target component name and merged attributes.
        
        Args:
            alias_name: Name of the alias
            user_attributes: Attributes provided by user
            
        Returns:
            Tuple of (target_component_name, merged_attributes)
        """
        alias = self.get_alias(alias_name)
        if not alias:
            raise ValueError(f"Alias '{alias_name}' not found")
        
        # Merge default attributes with user attributes (user attributes take precedence)
        merged_attributes = alias.default_attributes.copy()
        merged_attributes.update(user_attributes)
        
        return alias.target_component, merged_attributes
    
    def _register_default_components(self) -> None:
        """Register the default RVO-based components from JSON definitions."""
        # Load definitions from JSON file
        definitions_path = Path(__file__).parent / "definitions.json"
        with open(definitions_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Register components from JSON
        for comp_data in data.get("components", []):
            # Convert attribute dictionaries to AttributeDefinition objects
            attributes = []
            for attr_data in comp_data.get("attributes", []):
                attr_type = AttributeType(attr_data["type"])
                attributes.append(AttributeDefinition(
                    name=attr_data["name"],
                    type=attr_type,
                    required=attr_data.get("required", False),
                    default=attr_data.get("default"),
                    description=attr_data.get("description", ""),
                    enum_values=attr_data.get("enum_values")
                ))

            # Create ComponentDefinition
            component = ComponentDefinition(
                name=comp_data["name"],
                description=comp_data["description"],
                attributes=attributes,
                slots=comp_data.get("slots", []),
                examples=comp_data.get("examples", []),
                allow_preview=comp_data.get("allow_preview", True),
                requires_children=comp_data.get("requires_children", False),
                preview_example=comp_data.get("preview_example")
            )
            self.register_component(component)
    
    def _register_default_aliases(self) -> None:
        """Register the default component aliases from JSON definitions."""
        # Load definitions from JSON file
        definitions_path = Path(__file__).parent / "definitions.json"
        with open(definitions_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Register aliases from JSON
        for alias_data in data.get("aliases", []):
            alias = ComponentAlias(
                name=alias_data["name"],
                target_component=alias_data["target_component"],
                default_attributes=alias_data.get("default_attributes", {}),
                description=alias_data.get("description", "")
            )
            self.register_alias(alias)

    def _register_conversion_components(self) -> None:
        """Auto-discover and register components from conversion/definitions/ directory."""
        # Find conversion definitions directory relative to this file
        # src/jinja_roos_components/registry.py -> ../../conversion/definitions/
        conversion_dir = Path(__file__).parent.parent.parent / "conversion" / "definitions"

        if not conversion_dir.exists():
            return  # No conversion definitions yet

        # Scan for all .json files
        for definition_file in conversion_dir.glob("*.json"):
            try:
                with open(definition_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Skip if component is already registered in main definitions.json
                component_name = data.get("name")
                if not component_name:
                    continue

                if component_name in self._components:
                    # Main definitions.json takes precedence
                    continue

                # Convert attributes from conversion format to ComponentDefinition format
                attributes = []
                for attr_data in data.get("attributes", []):
                    # Conversion files use "type" directly as string, we need AttributeType enum
                    attr_type_str = attr_data.get("type", "string")
                    try:
                        attr_type = AttributeType(attr_type_str)
                    except ValueError:
                        # Fallback to string if type is unknown
                        attr_type = AttributeType.STRING

                    attributes.append(AttributeDefinition(
                        name=attr_data["name"],
                        type=attr_type,
                        required=attr_data.get("required", False),
                        default=attr_data.get("default"),
                        description=attr_data.get("description", ""),
                        enum_values=attr_data.get("enum_values")  # Read enum_values from conversion definitions
                    ))

                # Create ComponentDefinition
                # Use a simple description based on the component name
                description = data.get("description", f"Auto-generated component: {component_name}")

                component = ComponentDefinition(
                    name=component_name,
                    description=description,
                    attributes=attributes,
                    slots=["content"],  # Default to content slot
                    examples=[],  # No examples in conversion format yet
                    allow_preview=True,
                    requires_children=False,
                    preview_example=None
                )

                self.register_component(component)

            except (json.JSONDecodeError, KeyError, TypeError) as e:
                # Skip invalid definition files
                continue

