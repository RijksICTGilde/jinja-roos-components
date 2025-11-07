#!/usr/bin/env python3
"""Regenerate components based on existing definition files.

This script reads all component definition files and re-runs the conversion
for each component that has been previously converted.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from conversion.convert_component import ComponentConverter


# Skip problematic components and their dependents
# feedback -> causes hanging
# field, form-field -> depend on feedback
# form-field-select, form-fieldset -> depend on field which depends on feedback
skip_components = {'feedback', 'field', 'form-field', 'form-field-select', 'form-fieldset'}


def find_definition_files(definitions_dir: Path) -> List[Path]:
    """Find all JSON definition files.

    Args:
        definitions_dir: Path to definitions directory

    Returns:
        List of definition file paths
    """
    return list(definitions_dir.glob("*.json"))


def load_definition(definition_file: Path) -> Dict:
    """Load a component definition from JSON file.

    Args:
        definition_file: Path to definition file

    Returns:
        Definition dictionary
    """
    with open(definition_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_component_name_from_source(source_file: str) -> str:
    """Extract component name from source file path.

    Args:
        source_file: Relative source file path (e.g., "rvo/components/button/src/template.tsx")

    Returns:
        Component name (e.g., "button")
    """
    # Source file format: rvo/components/{component-name}/src/template.tsx
    parts = source_file.split('/')
    try:
        # Find 'components' in path and get the next part
        components_idx = parts.index('components')
        return parts[components_idx + 1]
    except (ValueError, IndexError):
        # Fallback: try to get the parent directory of 'src'
        try:
            src_idx = parts.index('src')
            return parts[src_idx - 1]
        except (ValueError, IndexError):
            return None


def regenerate_component(
    definition_file: Path,
    verbose: bool = False
) -> bool:
    """Regenerate a single component.

    Args:
        definition_file: Path to definition file
        verbose: Enable verbose output

    Returns:
        True if successful, False otherwise
    """
    definition = load_definition(definition_file)

    definition_name = definition.get("name")
    source_file = definition.get("source_file")

    if not definition_name or not source_file:
        print(f"⚠️  Skipping {definition_file.name}: missing name or source_file")
        return False

    # Extract component name from source file
    component_name = extract_component_name_from_source(source_file)

    if not component_name:
        print(f"⚠️  Skipping {definition_name}: could not extract component name from {source_file}")
        return False

    print(f"🔄 Regenerating: {definition_name} (from {component_name})...")

    # Determine output_name and aliases
    output_name = definition_name if definition_name != component_name else None
    aliases = None  # Aliases are stored in overall_definitions.json, not in individual definitions

    if verbose:
        if output_name:
            print(f"   Converting: {component_name} -> {output_name}")
        else:
            print(f"   Converting: {component_name}")

    # Execute conversion using ComponentConverter directly
    try:
        converter = ComponentConverter(
            component_name,
            output_name=output_name,
            aliases=aliases
        )
        converter.convert()
        print(f"✅ Successfully regenerated: {definition_name}")
        return True

    except Exception as e:
        print(f"❌ Failed to regenerate: {definition_name}")
        print(f"   Error: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Regenerate components based on existing definition files",
        epilog="""
Examples:
  # Regenerate all components
  %(prog)s

  # Regenerate with verbose output
  %(prog)s --verbose

  # Regenerate specific components only
  %(prog)s --only button paragraph
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--only",
        nargs="+",
        metavar="COMPONENT",
        help="Only regenerate specific components (by definition name)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Locate definitions directory
    project_root = Path(__file__).parent.parent
    definitions_dir = project_root / "src" / "jinja_roos_components" / "definitions"

    if not definitions_dir.exists():
        print(f"❌ Error: Definitions directory not found: {definitions_dir}", file=sys.stderr)
        sys.exit(1)

    # Find all definition files
    definition_files = find_definition_files(definitions_dir)

    if not definition_files:
        print(f"⚠️  No definition files found in {definitions_dir}")
        sys.exit(0)

    definition_files = [f for f in definition_files if f.stem not in skip_components]

    # Filter by --only if specified
    if args.only:
        only_set = set(args.only)
        # Check if user is trying to regenerate a skipped component
        requesting_skipped = only_set & skip_components
        if requesting_skipped:
            print(f"⚠️  Cannot regenerate skipped component(s): {', '.join(requesting_skipped)}")
            only_set = only_set - skip_components

        definition_files = [
            f for f in definition_files
            if f.stem in only_set
        ]
        print(f"📋 Regenerating {len(definition_files)} component(s): {', '.join(args.only)}")
    else:
        print(f"📋 Found {len(definition_files)} component(s) to regenerate")
        if skip_components:
            print(f"⏭️  Skipping: {', '.join(skip_components)} (known to cause issues)")

    print("=" * 60)
    print()

    # Track results
    successful = []
    failed = []

    # Regenerate each component
    for definition_file in sorted(definition_files):

        if regenerate_component(
            definition_file,
            verbose=args.verbose
        ):
            successful.append(definition_file.stem)
        else:
            failed.append(definition_file.stem)

        # Add spacing between components only in verbose mode
        if args.verbose:
            print()

    # Summary
    print("=" * 60)
    print(f"✅ Successfully regenerated: {len(successful)}/{len(definition_files)}")
    if failed:
        print(f"❌ Failed: {len(failed)}")
        print(f"   Components: {', '.join(failed)}")
    print()
    print(f'skipped: {len(skip_components)}')
    for skip in skip_components:
        print(f'- {skip}')


if __name__ == "__main__":
    main()
