"""Generate component definition JSON files."""

import json
from datetime import datetime
from typing import List, Dict, Any
from ..parsers.interface_parser import AttributeInfo
from ..utils.file_helpers import compute_hash


class DefinitionGenerator:
    """Generator for component definition JSON files."""

    def __init__(self, component_name: str):
        """Initialize generator.

        Args:
            component_name: Name of the component
        """
        self.component_name = component_name

    def generate_definition(
        self,
        attributes: List[AttributeInfo],
        default_args: Dict[str, Any],
        source_file: str,
        source_content: str,
        base_components: List[Dict[str, str]],
        nested_components: List[str],
        manual_review_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate component definition.

        Args:
            attributes: List of component attributes
            default_args: Default values
            source_file: Path to source file
            source_content: Content of source file (for hash)
            base_components: List of base component info
            nested_components: List of nested component names
            manual_review_items: Items requiring manual review

        Returns:
            Definition dictionary
        """
        return {
            "name": self.component_name,
            "source_file": source_file,
            "converted_at": datetime.utcnow().isoformat() + "Z",
            "conversion_hash": compute_hash(source_content),
            "base_components": base_components,
            "nested_components": nested_components,
            "attributes": self._convert_attributes(attributes, default_args),
            "manual_review_items": manual_review_items
        }

    def _convert_attributes(self, attributes: List[AttributeInfo], default_args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert AttributeInfo list to definition format.

        Args:
            attributes: List of AttributeInfo
            default_args: Default values dict

        Returns:
            List of attribute definitions
        """
        result = []

        for attr in attributes:
            # Skip function attributes
            if attr.is_function:
                continue

            attr_def = {
                "name": attr.name,
                "type": self._determine_primary_type(attr),
                "required": attr.required,
                "description": attr.description or f"{attr.name} attribute"
            }

            # Add enum values if present
            if attr.enum_values:
                attr_def["enum_values"] = attr.enum_values

            # Add default value if present
            if attr.name in default_args:
                attr_def["default"] = default_args[attr.name]
            elif not attr.required:
                # Provide sensible defaults
                attr_def["default"] = self._get_type_default(attr)

            result.append(attr_def)

        return result

    def _determine_primary_type(self, attr: AttributeInfo) -> str:
        """Determine primary type for attribute.

        Args:
            attr: Attribute info

        Returns:
            Primary type string
        """
        if 'enum' in attr.types:
            return 'enum'

        # Filter out 'enum' and get first remaining type
        other_types = [t for t in attr.types if t != 'enum']

        if not other_types:
            return 'string'

        primary_type = other_types[0]

        # Map to definition type
        type_map = {
            'string': 'string',
            'number': 'number',
            'boolean': 'boolean',
            'object': 'object',
            'function': 'function'
        }

        return type_map.get(primary_type, 'string')

    def _get_type_default(self, attr: AttributeInfo) -> Any:
        """Get default value based on type.

        Args:
            attr: Attribute info

        Returns:
            Default value
        """
        if 'boolean' in attr.types:
            return False
        if 'number' in attr.types:
            return 0
        if 'enum' in attr.types and attr.enum_values:
            return attr.enum_values[0]

        return ""

    def write_definition(self, definition: Dict[str, Any], output_path: str) -> None:
        """Write definition to JSON file.

        Args:
            definition: Definition dictionary
            output_path: Path to output file
        """
        from ..utils.file_helpers import write_file

        json_content = json.dumps(definition, indent=2, ensure_ascii=False)
        write_file(output_path, json_content)

    def generate_review_document(
        self,
        manual_review_items: List[Dict[str, Any]],
        automation_percentage: float
    ) -> str:
        """Generate markdown review document.

        Args:
            manual_review_items: Items requiring review
            automation_percentage: Percentage of automation achieved

        Returns:
            Markdown document as string
        """
        lines = [
            f"# {self.component_name.title()} Conversion Review",
            "",
            f"## Automatic Conversion: {automation_percentage:.0f}%",
            f"## Manual Review Required: {100 - automation_percentage:.0f}%",
            ""
        ]

        if manual_review_items:
            lines.extend([
                "### Items Requiring Review:",
                ""
            ])

            for i, item in enumerate(manual_review_items, 1):
                severity = item.get('severity', 'medium')
                issue = item.get('issue', 'Unknown issue')
                source_line = item.get('source_line', '?')
                pattern = item.get('pattern', '')

                lines.append(f"{i}. **{issue}** (line {source_line})")
                lines.append(f"   - Severity: {severity}")

                if pattern:
                    lines.append(f"   - Pattern: `{pattern}`")

                if 'action' in item:
                    lines.append(f"   - Action: {item['action']}")

                lines.append("")
        else:
            lines.append("No manual review items! ✅")
            lines.append("")

        return '\n'.join(lines)
