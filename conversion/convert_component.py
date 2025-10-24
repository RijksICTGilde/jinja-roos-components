#!/usr/bin/env python3
"""Main script to convert React components to Jinja templates."""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from conversion.parsers.tsx_parser import TsxParser
from conversion.parsers.base_component_resolver import BaseComponentResolver
from conversion.parsers.clsx_parser import ClsxParser
from conversion.parsers.switch_parser import SwitchParser
from conversion.parsers.jsx_attr_parser import JsxAttrParser
from conversion.parsers.content_parser import ContentParser
from conversion.generators.jinja_generator import JinjaGenerator
from conversion.generators.class_builder import ClassBuilder
from conversion.generators.definition_generator import DefinitionGenerator
from conversion.customizations.customization_loader import CustomizationLoader
from conversion.utils.file_helpers import (
    read_file,
    write_file,
    get_rvo_components_dir,
    get_output_template_dir,
    get_conversion_dir,
    file_exists
)


class ComponentConverter:
    """Converter for React components to Jinja templates."""

    def __init__(self, component_name: str, output_name: str = None, aliases: List[str] = None):
        """Initialize converter.

        Args:
            component_name: Name of component to convert from RVO (or full path)
            output_name: Custom name for the output component (defaults to component_name)
            aliases: List of alias names to register for this component
        """
        # Handle full path or just component name
        component_path = Path(component_name)
        if component_path.is_absolute():
            # Extract just the component name from the path
            self.component_name = component_path.name
        else:
            self.component_name = component_name

        self.output_name = output_name or self.component_name
        self.aliases = aliases or []
        self.tsx_parser = TsxParser()
        self.base_resolver = BaseComponentResolver()
        self.clsx_parser = ClsxParser()
        self.switch_parser = SwitchParser()
        self.jsx_attr_parser = JsxAttrParser()
        self.content_parser = ContentParser()
        self.customization_loader = CustomizationLoader()
        self.jinja_generator = JinjaGenerator(self.output_name)
        self.definition_generator = DefinitionGenerator(self.output_name)
        self.manual_review_items = []

    def convert(self) -> None:
        """Run the full conversion process."""
        print(f"\n🔄 Converting component: {self.component_name}")
        if self.output_name != self.component_name:
            print(f"   Output name: {self.output_name}")
        if self.aliases:
            print(f"   Aliases: {', '.join(self.aliases)}")
        print("=" * 60)

        # Step 1: Locate source files
        print("\n📁 Locating source files...")
        tsx_file, defaultargs_file = self._locate_source_files()
        print(f"   ✓ TSX: {tsx_file}")
        if defaultargs_file:
            print(f"   ✓ Defaults: {defaultargs_file}")

        # Step 2: Parse component
        print("\n📖 Parsing React component...")
        component_info = self.tsx_parser.parse_component(tsx_file, defaultargs_file)
        print(f"   ✓ Found {len(component_info.props_interface or [])} attributes")
        print(f"   ✓ Found {len(component_info.default_args)} default values")
        print(f"   ✓ Found {len(component_info.imports)} imports")

        # Step 2a: Apply customizations if they exist
        if self.customization_loader.has_customization(self.component_name):
            print("\n🎨 Applying customizations...")
            component_info.props_interface = self.customization_loader.apply_customizations(
                self.component_name,
                component_info.props_interface or []
            )
            customization_notes = self.customization_loader.get_customization_notes(self.component_name)
            print(f"   ✓ Customizations applied")
            for note in customization_notes:
                print(f"   ℹ {note}")

        # Step 3: Detect base components
        print("\n🔍 Detecting base components...")
        base_components = self._detect_base_components(component_info)
        if base_components:
            for bc in base_components:
                print(f"   ✓ {bc['library']}/{bc['component']}")
        else:
            print("   ℹ No base components detected")

        # Step 4: Extract clsx mappings
        print("\n🔍 Extracting CSS class logic from clsx()...")
        class_mappings = self._extract_clsx_mappings(component_info)
        print(f"   ✓ Found {len(class_mappings)} initial clsx mappings")

        # Step 4a: Expand template literals in clsx mappings
        class_mappings = self.clsx_parser.expand_template_literals(
            class_mappings,
            component_info.props_interface or []
        )
        print(f"   ✓ Expanded to {len(class_mappings)} total clsx mappings")

        # Step 5: Resolve base to HTML first to get base classes
        print("\n🏗  Resolving base components...")
        html_tag, base_classes = self._resolve_base_component(component_info, base_components, class_mappings)
        print(f"   ✓ HTML tag: <{html_tag}>")
        print(f"   ✓ Base classes: {', '.join(base_classes)}")

        # Step 4b: Extract switch statement mappings (after getting base classes to filter)
        print("\n🔀 Extracting switch statement logic...")
        switch_mappings = self._extract_switch_mappings(component_info, base_components, base_classes)
        class_mappings.extend(switch_mappings)
        print(f"   ✓ Found {len(switch_mappings)} switch mappings")

        # Step 4c: Extract JSX attribute expressions (like hint={...})
        print("\n📋 Extracting JSX attribute logic...")
        jsx_attr_mappings = self._extract_jsx_attr_mappings(component_info, base_components, base_classes)
        class_mappings.extend(jsx_attr_mappings)
        print(f"   ✓ Found {len(jsx_attr_mappings)} JSX attr mappings (total: {len(class_mappings)})")

        # Step 6: Build class logic
        print("\n🎨 Building CSS class logic...")
        self._build_class_logic(component_info, base_classes, class_mappings)
        print(f"   ✓ Class builder configured")

        # Step 6a: Extract content rendering logic
        print("\n📝 Extracting content rendering logic...")
        content_elements = self._extract_content(component_info, tsx_file)
        print(f"   ✓ Found {len(content_elements)} content elements")

        # Step 7: Generate Jinja template
        print("\n📝 Generating Jinja template...")
        jinja_content = self._generate_jinja_template(component_info, html_tag, base_classes, content_elements)
        output_file = get_output_template_dir() / f"{self.output_name}.html.j2"
        write_file(output_file, jinja_content)
        print(f"   ✓ Written to: {output_file}")

        # Step 8: Generate definition
        print("\n📋 Generating component definition...")
        definition = self._generate_definition(component_info, base_components, tsx_file)
        definition_file = get_conversion_dir() / "definitions" / f"{self.output_name}.json"
        self.definition_generator.write_definition(definition, str(definition_file))
        print(f"   ✓ Written to: {definition_file}")

        # Step 9: Generate review document
        print("\n📄 Generating review document...")
        automation_pct = self._calculate_automation_percentage()
        review_doc = self.definition_generator.generate_review_document(
            self.manual_review_items,
            automation_pct
        )
        review_file = get_conversion_dir() / "review" / f"{self.output_name}_review.md"
        write_file(review_file, review_doc)
        print(f"   ✓ Written to: {review_file}")

        # Step 10: Register aliases if provided
        if self.aliases:
            print("\n🏷  Registering aliases...")
            self._register_aliases()
            print(f"   ✓ Registered {len(self.aliases)} alias(es): {', '.join(self.aliases)}")

        # Summary
        print("\n" + "=" * 60)
        print(f"✅ Conversion complete!")
        print(f"   Automation: {automation_pct:.0f}%")
        print(f"   Manual review items: {len(self.manual_review_items)}")
        print("\n📦 Output files:")
        print(f"   - Template: {output_file}")
        print(f"   - Definition: {definition_file}")
        print(f"   - Review: {review_file}")
        print()

    def _locate_source_files(self) -> tuple[str, str | None]:
        """Locate source TSX and defaultArgs files.

        Returns:
            Tuple of (tsx_file_path, defaultargs_file_path)
        """
        rvo_dir = get_rvo_components_dir()
        component_dir = rvo_dir / self.component_name

        if not component_dir.exists():
            raise FileNotFoundError(f"Component directory not found: {component_dir}")

        tsx_file = component_dir / "src" / "template.tsx"
        if not tsx_file.exists():
            raise FileNotFoundError(f"Template file not found: {tsx_file}")

        defaultargs_file = component_dir / "src" / "defaultArgs.ts"
        if not defaultargs_file.exists():
            defaultargs_file = None

        return str(tsx_file), str(defaultargs_file) if defaultargs_file else None

    def _detect_base_components(self, component_info) -> List[Dict[str, str]]:
        """Detect base components from imports.

        Only detects the outermost/root base component, not nested ones.

        Args:
            component_info: Parsed component information

        Returns:
            List of base component info dicts (usually just one - the root)
        """
        base_imports = self.tsx_parser.get_base_component_imports()
        candidate_components = []

        # Build list of all base component candidates with their JSX names
        for import_info in base_imports:
            for name in import_info.names:
                if self.base_resolver.is_base_component(import_info.source, name):
                    # Find the actual name used in JSX (could be an alias)
                    jsx_name = name
                    if import_info.aliases:
                        # Check if this component has an alias
                        for alias_name, original_name in import_info.aliases.items():
                            if original_name == name:
                                jsx_name = alias_name
                                break

                    candidate_components.append({
                        'library': import_info.source,
                        'component': name,  # Keep original name for resolution
                        'jsx_name': jsx_name  # Name as used in JSX
                    })

        if not candidate_components:
            return []

        # Find the root component by looking for the first opening tag in JSX
        jsx_content = component_info.jsx_content.strip()
        # Skip opening parenthesis if present
        if jsx_content.startswith('('):
            jsx_content = jsx_content[1:].strip()

        # Find first component tag: <ComponentName
        import re
        match = re.match(r'<([A-Z][A-Za-z0-9]*)', jsx_content)
        if not match:
            # No component found, return all candidates
            return candidate_components

        root_component_name = match.group(1)

        # Return only the component that matches the root
        base_components = []
        for candidate in candidate_components:
            if candidate['jsx_name'] == root_component_name:
                base_components.append(candidate)
                break  # Only one root component

        return base_components if base_components else candidate_components

    def _resolve_base_component(self, component_info, base_components, class_mappings=None) -> tuple[str, List[str]]:
        """Resolve base component to HTML tag and classes.

        Args:
            component_info: Parsed component information
            base_components: List of base component info
            class_mappings: Optional clsx mappings to check

        Returns:
            Tuple of (html_tag, base_classes)
        """
        if not base_components:
            return 'div', []

        # Use first base component
        first_base = base_components[0]
        resolution = self.base_resolver.resolve(
            first_base['library'],
            first_base['component'],
            component_info.default_args
        )

        # Track items needing review, but filter out props handled by clsx
        if resolution.get('needs_review'):
            # Get prop names that have clsx mappings
            mapped_props = set()
            if class_mappings:
                for mapping in class_mappings:
                    mapped_props.add(mapping.prop_name)

            for issue in resolution['needs_review']:
                # Check if it's an "unmapped prop" issue
                if issue.startswith('Unmapped prop:'):
                    prop_name = issue.split(':')[1].strip()
                    # Skip if handled by clsx
                    if prop_name in mapped_props:
                        continue

                self.manual_review_items.append({
                    'issue': issue,
                    'severity': 'medium',
                    'source_line': 0
                })

        return resolution['html_tag'], resolution['css_classes']

    def _extract_clsx_mappings(self, component_info):
        """Extract class mappings from clsx() calls.

        Args:
            component_info: Parsed component information

        Returns:
            List of ClassMapping objects
        """
        return self.clsx_parser.extract_from_jsx(component_info.jsx_content)

    def _extract_switch_mappings(self, component_info, base_components, base_classes):
        """Extract class mappings from switch statements.

        Args:
            component_info: Parsed component information
            base_components: List of base component info
            base_classes: Base CSS classes to filter out

        Returns:
            List of ClassMapping objects
        """
        # Read the full source file (not just JSX)
        source_content = read_file(component_info.file_path)

        # Extract switch mappings
        switch_mappings = self.switch_parser.extract_from_source(source_content)

        if not switch_mappings or not base_components:
            return []

        # Convert switch mappings to class mappings using base resolver
        first_base = base_components[0]
        return self.switch_parser.to_class_mappings(
            self.base_resolver,
            first_base['library'],
            first_base['component'],
            base_classes
        )

    def _extract_jsx_attr_mappings(self, component_info, base_components, base_classes):
        """Extract class mappings from JSX attribute expressions.

        Args:
            component_info: Parsed component information
            base_components: List of base component info
            base_classes: Base CSS classes to filter out

        Returns:
            List of ClassMapping objects
        """
        # Extract JSX attribute mappings
        jsx_mappings = self.jsx_attr_parser.extract_from_jsx(component_info.jsx_content)

        if not jsx_mappings or not base_components:
            return []

        # Convert to class mappings using base resolver
        first_base = base_components[0]
        return self.jsx_attr_parser.to_class_mappings(
            self.base_resolver,
            first_base['library'],
            first_base['component'],
            base_classes
        )

    def _build_class_logic(self, component_info, base_classes: List[str], class_mappings: List) -> None:
        """Build CSS class logic for component.

        Args:
            component_info: Parsed component information
            base_classes: Base CSS classes
            class_mappings: Extracted class mappings from clsx
        """
        # Add base classes to Jinja generator
        self.jinja_generator.class_builder.add_base_classes(base_classes)

        # Add conditional classes from clsx mappings
        for mapping in class_mappings:
            if mapping.value == 'true':
                # Boolean prop
                self.jinja_generator.class_builder.add_boolean_class(
                    mapping.prop_name,
                    mapping.css_class
                )
            elif mapping.value == 'false':
                # Negated boolean prop
                self.jinja_generator.class_builder.add_boolean_class(
                    mapping.prop_name,
                    mapping.css_class,
                    negate=True
                )
            else:
                # Value-based (enum)
                self.jinja_generator.class_builder.add_conditional_class(
                    mapping.css_class,
                    f"{mapping.prop_name} == '{mapping.value}'"
                )

    def _extract_content(self, component_info, tsx_file: str):
        """Extract content rendering logic from component.

        Args:
            component_info: Parsed component information
            tsx_file: Path to TSX file

        Returns:
            List of ContentElement objects
        """
        # Extract content elements from JSX
        content_elements = self.content_parser.extract_from_jsx(component_info.jsx_content)

        # Read full source to resolve component references
        source_content = read_file(tsx_file)
        component_refs = self.content_parser.resolve_component_references(source_content)

        # Attach component reference info to elements
        for element in content_elements:
            if element.type in ('conditional', 'variable') and element.content:
                if element.content in component_refs:
                    element.component_name = component_refs[element.content]['component']
                    element.component_props = component_refs[element.content]['props']

        return content_elements

    def _generate_jinja_template(self, component_info, html_tag: str, base_classes: List[str], content_elements: List = None) -> str:
        """Generate Jinja template content.

        Args:
            component_info: Parsed component information
            html_tag: HTML tag name
            base_classes: Base CSS classes
            content_elements: List of ContentElement objects

        Returns:
            Jinja template as string
        """
        return self.jinja_generator.generate_template(
            component_info.props_interface or [],
            component_info.default_args,
            html_tag,
            base_classes,
            content_elements=content_elements or []
        )

    def _generate_definition(self, component_info, base_components, source_file: str) -> Dict:
        """Generate component definition.

        Args:
            component_info: Parsed component information
            base_components: List of base components
            source_file: Path to source file

        Returns:
            Definition dictionary
        """
        source_content = read_file(source_file)

        return self.definition_generator.generate_definition(
            component_info.props_interface or [],
            component_info.default_args,
            source_file,
            source_content,
            base_components,
            [],  # TODO: Extract nested components
            self.manual_review_items
        )

    def _calculate_automation_percentage(self) -> float:
        """Calculate automation percentage.

        Returns:
            Percentage (0-100)
        """
        # Simple heuristic: fewer review items = higher automation
        if not self.manual_review_items:
            return 95.0  # Never claim 100%

        # Deduct 5% per review item, minimum 50%
        percentage = 95.0 - (len(self.manual_review_items) * 5.0)
        return max(percentage, 50.0)

    def _register_aliases(self) -> None:
        """Register component aliases in definitions.json."""
        import json
        from pathlib import Path

        # Get path to main definitions.json in src/jinja_roos_components
        definitions_path = Path(__file__).parent.parent / "src" / "jinja_roos_components" / "definitions.json"

        # Load existing definitions
        with open(definitions_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Ensure aliases array exists
        if "aliases" not in data:
            data["aliases"] = []

        # Add each alias
        for alias_name in self.aliases:
            # Check if alias already exists
            existing_alias = next((a for a in data["aliases"] if a["name"] == alias_name), None)

            if existing_alias:
                # Update existing alias to point to new target
                existing_alias["target_component"] = self.output_name
                existing_alias["description"] = f"Alias for {self.output_name}"
                print(f"   ⚠ Updated existing alias: {alias_name}")
            else:
                # Add new alias
                new_alias = {
                    "name": alias_name,
                    "target_component": self.output_name,
                    "default_attributes": {},
                    "description": f"Alias for {self.output_name}"
                }
                data["aliases"].append(new_alias)

        # Write back to file with pretty formatting
        with open(definitions_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')  # Add trailing newline


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert React components to Jinja templates",
        epilog="""
Examples:
  # Basic conversion
  %(prog)s button

  # Convert with custom output name
  %(prog)s form-fieldset --name fieldset

  # Convert with custom name and aliases
  %(prog)s form-fieldset --name fieldset --alias fs --alias field
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "component_name",
        help="Name of the component to convert from RVO (e.g., 'button', 'form-fieldset')"
    )
    parser.add_argument(
        "--name", "-n",
        dest="output_name",
        help="Custom name for the output component (defaults to component_name). "
             "Use this when the RVO component name differs from your desired name."
    )
    parser.add_argument(
        "--alias", "-a",
        dest="aliases",
        action="append",
        help="Register an alias for this component (can be used multiple times). "
             "Example: --alias fs --alias field"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    try:
        converter = ComponentConverter(
            args.component_name,
            output_name=args.output_name,
            aliases=args.aliases
        )
        converter.convert()
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
