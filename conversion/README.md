# Component Conversion System

Automatically convert React components from the RVO design system to Jinja2 templates.

## Quick Start

### Convert a Component

```bash
# Convert the button component
poetry run python conversion/convert_component.py button

# Convert the card component
poetry run python conversion/convert_component.py card

# Any RVO component works
poetry run python conversion/convert_component.py alert
```

### Custom Component Naming

When the RVO component name differs from your desired name:

```bash
# Convert form-fieldset but name it "fieldset"
poetry run python conversion/convert_component.py form-fieldset --name fieldset

# This creates:
# - src/jinja_roos_components/templates/components/fieldset.html.j2
# - conversion/definitions/fieldset.json
# - conversion/review/fieldset_review.md
```

### Component Aliases

Create short aliases for components:

```bash
# Convert and add aliases
poetry run python conversion/convert_component.py form-fieldset --name fieldset --alias fs --alias field

# Use in templates:
# <c-fieldset>...</c-fieldset>
# <c-fs>...</c-fs>          (alias)
# <c-field>...</c-field>    (alias)
```

Aliases are registered in `src/jinja_roos_components/definitions.json` and work immediately in templates.

## CLI Options

```bash
poetry run python conversion/convert_component.py <component_name> [OPTIONS]
```

**Arguments:**
- `component_name` - Name of the RVO component to convert (e.g., `button`, `form-fieldset`)

**Options:**
- `--name`, `-n` - Custom name for the output component (defaults to component_name)
- `--alias`, `-a` - Register an alias for this component (can be used multiple times)
- `--verbose`, `-v` - Enable verbose output for debugging
- `--help`, `-h` - Show help message

**Examples:**
```bash
# Basic conversion
poetry run python conversion/convert_component.py button

# Custom naming
poetry run python conversion/convert_component.py form-fieldset --name fieldset

# With aliases
poetry run python conversion/convert_component.py form-fieldset -n fieldset -a fs -a field

# Verbose output for debugging
poetry run python conversion/convert_component.py card --verbose
```

### What Gets Generated

Running the conversion creates 3 files:

1. **Template**: `src/jinja_roos_components/templates/components/button.html.j2`
   - Jinja2 template with all CSS classes, attributes, and content rendering

2. **Definition**: `conversion/definitions/button.json`
   - Component metadata (attributes, types, defaults, enum values)

3. **Review**: `conversion/review/button_review.md`
   - Manual review items (usually false positives for content-only props)

### Conversion Output Example

```
🔄 Converting component: button
============================================================

📁 Locating source files...
   ✓ TSX: .../rvo/components/button/src/template.tsx
   ✓ Defaults: .../rvo/components/button/src/defaultArgs.ts

📖 Parsing React component...
   ✓ Found 18 attributes
   ✓ Found 13 default values
   ✓ Found 6 imports

🎨 Applying customizations...
   ✓ Customizations applied
   ℹ Added 'color' attribute to allow custom color overrides

🔍 Extracting CSS class logic from clsx()...
   ✓ Found 13 initial clsx mappings
   ✓ Expanded to 14 total clsx mappings

...rest of conversion...

✅ Conversion complete!
   Automation: 80%
   Manual review items: 3
```

## Customizations

Extend or override component attributes during conversion.

### Create a Customization

**File**: `conversion/customizations/card.json`

```json
{
  "component": "card",
  "description": "Allow all RVO colors for backgroundColor",
  "attribute_overrides": {
    "backgroundColor": {
      "type": "enum",
      "values": "all_rvo_colors"
    }
  },
  "notes": "Extended from 4 colors to full RVO palette"
}
```

### Run Conversion with Customization

```bash
poetry run python conversion/convert_component.py card
```

Output shows customization was applied:
```
🎨 Applying customizations...
   ✓ Customizations applied
   ℹ Extended from 4 colors to full RVO palette
```

### Available Token References

Use these in `"values"` for automatic design token extraction:

- **`all_rvo_colors`** - All RVO color names (hemelblauw, groen, rood, etc.)
- **`all_rvo_icons`** - All RVO icon names (home, arrow, info, etc.)
- **`primary_colors`** - Just primary brand colors

Defined in: `customizations/_tokens.json`

### Examples

**Allow all icons:**
```json
{
  "component": "alert",
  "attribute_overrides": {
    "icon": {
      "type": "enum",
      "values": "all_rvo_icons"
    }
  }
}
```

**Add new attribute:**
```json
{
  "component": "button",
  "attribute_additions": {
    "customColor": {
      "type": "enum",
      "values": "all_rvo_colors",
      "required": false,
      "description": "Custom color override"
    }
  }
}
```

**Use static list:**
```json
{
  "component": "badge",
  "attribute_overrides": {
    "variant": {
      "type": "enum",
      "values": ["success", "warning", "error", "info"]
    }
  }
}
```

## What Gets Converted Automatically

### ✅ Fully Automated

- **CSS Classes**: All `clsx()` calls, switch statements, JSX attributes
- **Template Literals**: `` `class-${variable}` `` expanded to enum values
- **Content Rendering**: Icon components inlined, conditional content
- **Attributes**: TypeScript interfaces, default values, enum types
- **Fallbacks**: `children || label` converted to Jinja fallback chains

### ⚠️ Manual Review May Be Needed

- Content-only props (label, icon, iconAriaLabel) - flagged but usually working
- Complex nested components beyond Icon
- Custom JavaScript logic not translatable to Jinja

## Project Structure

```
conversion/
├── README.md                      # This file
├── convert_component.py           # Main conversion script
├── customizations/                # Component customizations
│   ├── README.md                  # Customization docs
│   ├── QUICKSTART.md              # Quick examples
│   ├── _tokens.json               # Design token references
│   ├── button.json                # Button customization
│   └── card.json                  # Card customization
├── definitions/                   # Generated component definitions
│   ├── button.json
│   └── card.json
├── review/                        # Manual review documents
│   ├── button_review.md
│   └── card_review.md
├── parsers/                       # React source parsers
│   ├── tsx_parser.py              # TypeScript/TSX parser
│   ├── clsx_parser.py             # CSS class logic
│   ├── switch_parser.py           # Switch statement logic
│   ├── jsx_attr_parser.py         # JSX attribute ternaries
│   ├── content_parser.py          # Content rendering
│   └── ...
└── generators/                    # Jinja template generators
    ├── jinja_generator.py
    ├── class_builder.py
    └── definition_generator.py
```

## How It Works

1. **Parse React Source**
   - Extract TypeScript interface (attributes, types)
   - Parse defaultArgs for default values
   - Extract JSX content and logic

2. **Apply Customizations** (if exist)
   - Load `customizations/{component}.json`
   - Expand token references (all_rvo_colors → actual color list)
   - Override/add attributes

3. **Extract Logic**
   - Parse `clsx()` calls for CSS classes
   - Extract `switch` statements for value mappings
   - Parse JSX attribute ternaries (`hint={...}`)
   - Extract content rendering (`{condition && element}`)
   - Expand template literals (`` `class-${var}` ``)

4. **Generate Jinja Template**
   - Variable declarations with defaults
   - CSS class building logic
   - HTML element with attributes
   - Content rendering (including inlined Icon components)

5. **Generate Metadata**
   - Component definition JSON
   - Review document with manual items

## Updating Design Tokens

When RVO packages update with new colors/icons:

```bash
# Re-extract design tokens
poetry run python scripts/extract_design_tokens.py

# Re-convert components (automatically picks up new tokens)
poetry run python conversion/convert_component.py card
```

## Further Reading

- **[Customizations Quick Start](customizations/QUICKSTART.md)** - Examples and common patterns
- **[Customizations Full Guide](customizations/README.md)** - Complete documentation
- **[Boolean Attributes](../docs/BOOLEAN_ATTRIBUTES.md)** - How boolean attributes work

## Examples

### Convert Multiple Components

```bash
# Convert all form components
for component in button text-input checkbox radio-button; do
  poetry run python conversion/convert_component.py $component
done
```

### Test Generated Template

After conversion, test in a template:

```jinja
<!-- Generated button template with customizations -->
<c-button
  kind="primary"
  color="hemelblauw"
  showIcon="before"
  icon="home">
  Click me
</c-button>

<!-- Works with all RVO colors now! -->
<c-button color="groen">Success</c-button>
<c-button color="rood">Danger</c-button>
```

## Troubleshooting

**Component not found:**
```bash
❌ Error: Component directory not found: .../rvo/components/foo
```
→ Make sure the component exists in the RVO repository at `../rvo/components/`

**No customizations applied:**
- Customization file must match component name exactly
- Check `conversion/customizations/{component}.json` exists

**Design tokens empty:**
```bash
❌ No colors found in design tokens
```
→ Run `npm install` to ensure `@nl-rvo` packages are installed
→ Run `poetry run python scripts/extract_design_tokens.py`

## Contributing

When adding new parsers or generators:

1. Extract logic from React source (don't invent it)
2. Add tests demonstrating the extraction
3. Document what patterns are supported
4. Update this README with new capabilities