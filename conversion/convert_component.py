#!/usr/bin/env python3
"""Main script to convert React components to Jinja templates."""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from conversion.parsers.tsx_parser import TsxParser
from conversion.parsers.base_component_resolver import BaseComponentResolver
from conversion.parsers.clsx_parser import ClsxParser
from conversion.parsers.switch_parser import SwitchParser
from conversion.parsers.jsx_attr_parser import JsxAttrParser
from conversion.parsers.content_parser import ContentParser
from conversion.parsers.jsx_structure_parser import JsxStructureParser
from conversion.parsers.nested_component_detector import NestedComponentDetector
from conversion.parsers.array_shape_analyzer import ArrayShapeAnalyzer
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

    def __init__(self, component_name: str, output_name: str = None, aliases: List[str] = None, source_file: str = None):
        """Initialize converter.

        Args:
            component_name: Name of component to convert from RVO (or full path to tsx file)
            output_name: Custom name for the output component (defaults to component_name)
            aliases: List of alias names to register for this component
            source_file: Optional full path to the source tsx file (for nested components)
        """
        # Handle full path or just component name
        component_path = Path(component_name)
        if component_path.is_absolute() and component_path.suffix in ('.tsx', '.ts'):
            # Full path to tsx file provided
            self.source_file_override = str(component_path)
            # Extract component name from the parent directory
            # e.g., /path/to/progress-tracker-step/template.tsx -> progress-tracker-step
            self.component_name = component_path.parent.name
        elif source_file:
            # Explicit source file provided
            self.source_file_override = source_file
            self.component_name = component_name
        else:
            # Just a component name
            self.source_file_override = None
            self.component_name = component_name

        self.output_name = output_name or self.component_name
        self.aliases = aliases or []
        self.tsx_parser = TsxParser()
        self.base_resolver = BaseComponentResolver()
        self.clsx_parser = ClsxParser()
        self.switch_parser = SwitchParser()
        self.jsx_attr_parser = JsxAttrParser()
        self.content_parser = ContentParser()
        self.jsx_structure_parser = JsxStructureParser()
        self.nested_component_detector = NestedComponentDetector()
        self.array_shape_analyzer = ArrayShapeAnalyzer()
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
        print(f"   ✓ Actual defaults: {len(component_info.actual_defaults)} (used in component)")
        if component_info.example_values:
            print(f"   ℹ Example values: {len(component_info.example_values)} (only for stories)")
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

        # Step 3a: Detect nested/child components
        print("\n🔍 Detecting nested components...")
        nested_components = self._detect_nested_components(component_info, tsx_file)
        if nested_components:
            for nc in nested_components:
                print(f"   ✓ {nc['component_class']} → {nc['tag_name']}")
        else:
            print("   ℹ No nested components detected")

        # Step 3a.1: Ensure nested components are converted
        if nested_components:
            print("\n🔄 Ensuring nested components are converted...")
            self._ensure_nested_components_converted(nested_components)

        # Step 3b: Analyze array shapes and map to components
        print("\n📊 Analyzing array attributes...")
        array_mappings = self._analyze_array_shapes(component_info, nested_components, defaultargs_file)
        if array_mappings:
            for arr_name, mapping in array_mappings.items():
                if mapping.get('maps_to_component'):
                    print(f"   ✓ {arr_name}[] → {mapping['maps_to_component']} (score: {mapping['match_score']:.2f})")
                else:
                    print(f"   ℹ {arr_name}[] (type: {mapping['item_type']})")
        else:
            print("   ℹ No array attributes found")

        # Step 4: Extract clsx mappings
        print("\n🔍 Extracting CSS class logic from clsx()...")
        class_mappings = self._extract_clsx_mappings(component_info)
        clsx_base_classes = self.clsx_parser.base_classes
        print(f"   ✓ Found {len(class_mappings)} initial clsx mappings")
        if clsx_base_classes:
            print(f"   ✓ Found {len(clsx_base_classes)} base classes from clsx")

        # Step 4a: Expand template literals in clsx mappings
        class_mappings = self.clsx_parser.expand_template_literals(
            class_mappings,
            component_info.props_interface or []
        )
        print(f"   ✓ Expanded to {len(class_mappings)} total clsx mappings")

        # Step 4b: Extract props passed to base component from JSX
        base_component_props = {}
        if base_components:
            base_component_props = self._extract_base_component_props(component_info, base_components[0])
            if base_component_props:
                props_summary = ', '.join(f"{k}={v[:20]}..." if len(str(v)) > 20 else f"{k}={v}"
                                          for k, v in base_component_props.items())
                print(f"\n   ✓ Props on base component: {props_summary}")

        # Step 5: Resolve base component structure (generic tree walking)
        print("\n🏗  Resolving base component structure...")
        component_structure = self._resolve_component_structure(
            component_info, base_components, class_mappings, base_component_props
        )
        print(f"   ✓ Resolved structure with {len(component_structure.get('elements', []))} nested elements")

        # Extract base structure info for compatibility
        html_tag = component_structure.get('primary_tag', 'div')
        base_classes = component_structure.get('primary_classes', [])

        # Merge clsx base classes with component structure base classes
        if clsx_base_classes:
            # Add clsx base classes to the beginning
            base_classes = clsx_base_classes + [c for c in base_classes if c not in clsx_base_classes]

        # Step 4b: Extract switch statement mappings (after getting base classes to filter)
        print("\n🔀 Extracting switch statement logic...")
        switch_raw_mappings = self._extract_raw_switch_mappings(component_info)
        switch_mappings = self._extract_switch_mappings(component_info, base_components, base_classes)
        class_mappings.extend(switch_mappings)
        print(f"   ✓ Found {len(switch_mappings)} switch mappings")
        if switch_raw_mappings:
            print(f"   ✓ Found {len(switch_raw_mappings)} switch variables (for templates)")

        # Step 4c: Extract JSX attribute expressions (like hint={...})
        print("\n📋 Extracting JSX attribute logic...")
        jsx_attr_mappings = self._extract_jsx_attr_mappings(component_info, base_components, base_classes)
        class_mappings.extend(jsx_attr_mappings)
        print(f"   ✓ Found {len(jsx_attr_mappings)} JSX attr mappings (total: {len(class_mappings)})")

        # Step 6: Build class logic
        print("\n🎨 Building CSS class logic...")
        self._build_class_logic(component_info, base_classes, class_mappings, switch_raw_mappings)
        print(f"   ✓ Class builder configured")

        # Step 6a: Extract content rendering logic
        print("\n📝 Extracting content rendering logic...")
        content_elements = self._extract_content(component_info, tsx_file)
        print(f"   ✓ Found {len(content_elements)} content elements")

        # Step 7: Generate Jinja template
        print("\n📝 Generating Jinja template...")
        jinja_content = self._generate_jinja_template(
            component_info, component_structure, content_elements, nested_components, array_mappings
        )
        output_file = get_output_template_dir() / f"{self.output_name}.html.j2"
        write_file(output_file, jinja_content)
        print(f"   ✓ Written to: {output_file}")

        # Step 8: Generate definition
        print("\n📋 Generating component definition...")
        definition = self._generate_definition(
            component_info, base_components, nested_components, array_mappings, tsx_file
        )
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
        # If a source file was explicitly provided, use it
        if self.source_file_override:
            tsx_file = Path(self.source_file_override)
            if not tsx_file.exists():
                raise FileNotFoundError(f"Template file not found: {tsx_file}")

            # Look for defaultArgs in the same directory
            defaultargs_file = tsx_file.parent / "defaultArgs.ts"
            if not defaultargs_file.exists():
                defaultargs_file = None

            return str(tsx_file), str(defaultargs_file) if defaultargs_file else None

        # Standard path for top-level components
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

    def _detect_nested_components(self, component_info, tsx_file: str) -> List[Dict[str, Any]]:
        """Detect nested/child components from imports and JSX.

        Args:
            component_info: Parsed component information
            tsx_file: Path to TSX file

        Returns:
            List of nested component metadata
        """
        return self.nested_component_detector.detect_nested_components(
            component_info.imports,
            component_info.jsx_content,
            tsx_file
        )

    def _ensure_nested_components_converted(self, nested_components: List[Dict[str, Any]]) -> None:
        """Ensure all nested components are converted to Jinja templates.

        Args:
            nested_components: List of nested component metadata
        """
        for nested_comp in nested_components:
            # Check if template already exists
            output_file = get_output_template_dir() / f"{nested_comp['name']}.html.j2"

            if not output_file.exists():
                print(f"   🔄 Auto-converting: {nested_comp['component_class']}")

                # Use the resolved path if available, otherwise fall back to extracting from source_path
                resolved_path = nested_comp.get('resolved_path')

                if resolved_path and file_exists(resolved_path):
                    # Use full path directly
                    try:
                        print(f"      → Starting conversion using: {resolved_path}")
                        nested_converter = ComponentConverter(
                            component_name=nested_comp['name'],
                            source_file=resolved_path
                        )
                        nested_converter.convert()
                        print(f"      ✓ Completed conversion of {nested_comp['name']}")
                    except Exception as e:
                        print(f"      ⚠ Failed to convert {nested_comp['name']}: {str(e)[:100]}")
                else:
                    # Fallback: extract component name from source path
                    # ./progress-tracker-step/template → progress-tracker-step
                    source_path = nested_comp.get('source_path', '')
                    if source_path.startswith('./'):
                        component_name = source_path[2:].split('/')[0]

                        # Try to convert as top-level component (may fail for nested ones)
                        try:
                            print(f"      → Starting conversion of {component_name}...")
                            nested_converter = ComponentConverter(component_name)
                            nested_converter.convert()
                            print(f"      ✓ Completed conversion of {component_name}")
                        except Exception as e:
                            print(f"      ⚠ Failed to convert {component_name}: {str(e)[:100]}")
            else:
                print(f"   ✓ Already converted: {nested_comp['name']}")

    def _analyze_array_shapes(self, component_info, nested_components: List[Dict[str, Any]], defaultargs_file: Optional[str] = None) -> Dict[str, Dict]:
        """Analyze array attributes to map them to nested components.

        Args:
            component_info: Parsed component information
            nested_components: List of nested component metadata
            defaultargs_file: Optional path to defaultArgs file for resolving references

        Returns:
            Dict mapping array attribute names to component mapping info
        """
        # Merge default_args and example_values to find all arrays
        all_defaults = {**component_info.default_args, **component_info.example_values}

        # If we have string references like "defaultSteps", try to resolve them
        if defaultargs_file and file_exists(defaultargs_file):
            defaults_content = read_file(defaultargs_file)
            for key, value in list(all_defaults.items()):
                if isinstance(value, str) and value.startswith('default'):
                    # Try to extract the actual array from the file
                    # Pattern: export const defaultSteps = [...]
                    import re
                    pattern = rf'export\s+const\s+{value}\s*=\s*(\[[\s\S]*?\]);'
                    match = re.search(pattern, defaults_content)
                    if match:
                        try:
                            import json
                            array_str = match.group(1)
                            # Replace TypeScript syntax
                            array_str = re.sub(r'\s+as\s+const', '', array_str)
                            # Remove trailing commas (not allowed in JSON)
                            array_str = re.sub(r',\s*([}\]])', r'\1', array_str)
                            # Quote object keys for JSON compatibility
                            # Pattern: word followed by colon (but not inside strings)
                            array_str = re.sub(r'(\w+):', r'"\1":', array_str)
                            # Replace single quotes with double quotes
                            array_str = array_str.replace("'", '"')
                            # Try to parse as JSON
                            try:
                                parsed = json.loads(array_str)
                                all_defaults[key] = parsed
                                print(f"   📖 Resolved {value} → array with {len(parsed)} items")
                            except Exception as e:
                                # If JSON parsing fails, keep the reference
                                print(f"   ⚠ Failed to parse {value}: {str(e)[:50]}")
                                pass
                        except Exception as e:
                            print(f"   ⚠ Error resolving {value}: {str(e)[:50]}")
                            pass

        return self.array_shape_analyzer.analyze_arrays(
            all_defaults,
            nested_components
        )

    def _extract_base_component_props(self, component_info, base_component: Dict[str, str]) -> Dict[str, str]:
        """Extract props/attributes passed to the base component in JSX.

        Args:
            component_info: Parsed component information
            base_component: Base component info dict

        Returns:
            Dictionary of prop names to values
        """
        import re

        jsx_name = base_component['jsx_name']
        jsx_content = component_info.jsx_content

        # Find the base component tag in JSX: <JsxName ...props>
        pattern = rf'<{jsx_name}\s+([^>]*?)(?:>|/>)'
        match = re.search(pattern, jsx_content, re.DOTALL)

        if not match:
            return {}

        props_str = match.group(1).strip()
        if not props_str:
            return {}

        # Parse props using a simple attribute parser
        props = {}
        # Pattern for prop="value" or prop={value}
        prop_pattern = r'(\w+)=(?:"([^"]*)"|{([^}]*)})'

        for match in re.finditer(prop_pattern, props_str):
            prop_name = match.group(1)
            # Get either quoted value or braced value
            prop_value = match.group(2) if match.group(2) is not None else match.group(3)
            props[prop_name] = prop_value

        return props

    def _resolve_component_structure(
        self,
        component_info,
        base_components,
        class_mappings=None,
        rvo_props: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Resolve the full component structure by walking the component tree.

        Args:
            component_info: Parsed component information
            base_components: List of base component info
            class_mappings: Optional clsx mappings
            rvo_props: Props passed from RVO to the base component

        Returns:
            Dictionary containing the full nested structure with elements array
        """
        if not base_components:
            # No base component - parse JSX structure directly
            jsx_structure = self.jsx_structure_parser.parse_root_element(component_info.jsx_content)

            # Track review items
            for review_item in jsx_structure.get('needs_review', []):
                self.manual_review_items.append({
                    'issue': review_item,
                    'severity': 'low',
                    'source_line': 0
                })

            return {
                'primary_tag': jsx_structure['html_tag'],
                'primary_classes': jsx_structure['css_classes'],
                'elements': [{
                    'tag': jsx_structure['html_tag'],
                    'classes': jsx_structure['css_classes'],
                    'attributes': jsx_structure.get('attributes', {}),
                    'is_primary': True
                }]
            }

        first_base = base_components[0]

        # Get the base component structure from js_parser (for library components)
        # or from manual mappings
        resolution = self.base_resolver.resolve(
            first_base['library'],
            first_base['component'],
            component_info.default_args
        )

        # Track review items
        if resolution.get('needs_review'):
            mapped_props = set()
            if class_mappings:
                for mapping in class_mappings:
                    mapped_props.add(mapping.prop_name)

            for issue in resolution['needs_review']:
                if issue.startswith('Unmapped prop:'):
                    prop_name = issue.split(':')[1].strip()
                    if prop_name in mapped_props:
                        continue
                self.manual_review_items.append({
                    'issue': issue,
                    'severity': 'medium',
                    'source_line': 0
                })

        # Merge RVO props (like className) into the structure
        if rvo_props and 'className' in rvo_props:
            # Add RVO classes to the outermost element
            rvo_classes = rvo_props['className'].strip('"').split()
            if resolution.get('wrapper'):
                # Add to wrapper
                resolution['wrapper']['classes'].extend(rvo_classes)
            else:
                # Add to primary element classes
                resolution['css_classes'].extend(rvo_classes)

        # Build element structure for template generation
        elements = []

        if resolution.get('wrapper'):
            # Wrapper element
            elements.append({
                'tag': resolution['wrapper']['tag'],
                'classes': resolution['wrapper']['classes'],
                'is_wrapper': True
            })

        # Primary element
        elements.append({
            'tag': resolution['html_tag'],
            'classes': resolution['css_classes'],
            'attributes': resolution.get('attributes', {}),
            'is_primary': True
        })

        return {
            'primary_tag': resolution['html_tag'],
            'primary_classes': resolution['css_classes'],
            'elements': elements,
            'wrapper': resolution.get('wrapper')
        }

    def _resolve_base_component(self, component_info, base_components, class_mappings=None, rvo_props=None) -> tuple[str, List[str], Optional[Dict]]:
        """Resolve base component to HTML tag, classes, and wrapper info.

        Args:
            component_info: Parsed component information
            base_components: List of base component info
            class_mappings: Optional clsx mappings to check

        Returns:
            Tuple of (html_tag, base_classes, wrapper_info)
        """
        if not base_components:
            return 'div', [], None

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

        return resolution['html_tag'], resolution['css_classes'], resolution.get('wrapper')

    def _extract_clsx_mappings(self, component_info):
        """Extract class mappings from clsx() calls.

        Args:
            component_info: Parsed component information

        Returns:
            List of ClassMapping objects
        """
        return self.clsx_parser.extract_from_jsx(component_info.jsx_content)

    def _extract_raw_switch_mappings(self, component_info):
        """Extract raw switch mappings (for use in template literals).

        Args:
            component_info: Parsed component information

        Returns:
            List of SwitchMapping objects
        """
        source_content = read_file(component_info.file_path)
        return self.switch_parser.extract_from_source(source_content)

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

    def _build_class_logic(self, component_info, base_classes: List[str], class_mappings: List, switch_mappings: List = None) -> None:
        """Build CSS class logic for component.

        Args:
            component_info: Parsed component information
            base_classes: Base CSS classes
            class_mappings: Extracted class mappings from clsx
            switch_mappings: Optional raw switch mappings for computed variables
        """
        # Add base classes to Jinja generator
        self.jinja_generator.class_builder.add_base_classes(base_classes)

        # Add switch mappings as computed variables
        if switch_mappings:
            for switch_mapping in switch_mappings:
                # Generate Jinja if/elif chain for switch
                jinja_expr = self._switch_to_jinja_expr(switch_mapping)
                self.jinja_generator.class_builder.add_computed_var(
                    switch_mapping.result_var,
                    jinja_expr
                )

        # Add conditional classes from clsx mappings
        for mapping in class_mappings:
            # Handle special template markers
            if mapping.value == '__TEMPLATE__':
                # Template literal class
                condition = mapping.condition if mapping.condition != '__ALWAYS__' else None
                self.jinja_generator.class_builder.add_template_class(
                    mapping.css_class,
                    condition
                )
            elif mapping.prop_name == '__TERNARY__':
                # Ternary expression in template - needs special handling
                # For now, add as template class
                self.jinja_generator.class_builder.add_template_class(
                    mapping.css_class,
                    None  # Always include, but has ternary inside
                )
            elif mapping.value == 'true':
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

    def _switch_to_jinja_expr(self, switch_mapping) -> str:
        """Convert a switch mapping to a Jinja inline if/else expression.

        Args:
            switch_mapping: SwitchMapping object

        Returns:
            Jinja expression like "'start-end' if state == 'start' or state == 'end' else ..."
        """
        # Build nested ternary expression from switch cases
        if not switch_mapping.cases:
            return "''"

        # Separate default case from regular cases
        regular_cases = []
        default_case = None

        for case in switch_mapping.cases:
            if case.values == ['__DEFAULT__']:
                default_case = case
            else:
                regular_cases.append(case)

        # Start from the default case or empty string
        if default_case:
            # If result is a variable (not quoted), use it directly
            if default_case.result.isidentifier():
                expr = default_case.result
            else:
                expr = f"'{default_case.result}'"
        else:
            expr = "''"

        # Work backwards through regular cases
        for case in reversed(regular_cases):
            # Build condition for this case
            conditions = [f"{switch_mapping.switch_var} == '{val}'" for val in case.values]
            condition = ' or '.join(conditions)

            # Nest in ternary
            expr = f"'{case.result}' if {condition} else {expr}"

        return expr

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
                    ref_info = component_refs[element.content]

                    # Check if this is a conditional component reference
                    if ref_info.get('type') == 'conditional':
                        # Convert to a conditional content element with component info
                        element.type = 'conditional_component'
                        element.condition = ref_info['condition']
                        element.component_name = ref_info['component']
                        element.component_props = ref_info['props']
                        # Store the default value (fallback when condition is false)
                        element.fallback_value = ref_info['default']
                    else:
                        # Simple component reference
                        element.component_name = ref_info['component']
                        element.component_props = ref_info['props']

        return content_elements

    def _generate_jinja_template(
        self,
        component_info,
        component_structure: Dict[str, Any],
        content_elements: List = None,
        nested_components: List[Dict] = None,
        array_mappings: Dict[str, Dict] = None
    ) -> str:
        """Generate Jinja template content.

        Args:
            component_info: Parsed component information
            component_structure: Complete component structure with nested elements
            content_elements: List of ContentElement objects
            nested_components: List of nested component metadata
            array_mappings: Dict mapping array attributes to component info

        Returns:
            Jinja template as string
        """
        return self.jinja_generator.generate_template(
            component_info.props_interface or [],
            component_info.default_args,
            component_structure['primary_tag'],
            component_structure['primary_classes'],
            content_elements=content_elements or [],
            wrapper_info=component_structure.get('wrapper'),
            component_structure=component_structure,
            nested_components=nested_components or [],
            array_mappings=array_mappings or {}
        )

    def _generate_definition(
        self,
        component_info,
        base_components,
        nested_components: List[Dict],
        array_mappings: Dict[str, Dict],
        source_file: str
    ) -> Dict:
        """Generate component definition.

        Args:
            component_info: Parsed component information
            base_components: List of base components
            nested_components: List of nested component metadata
            array_mappings: Dict mapping array attributes to component info
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
            nested_components,
            self.manual_review_items,
            actual_defaults=component_info.actual_defaults,
            example_values=component_info.example_values,
            array_mappings=array_mappings
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
