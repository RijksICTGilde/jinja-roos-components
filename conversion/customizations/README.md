# Component Customizations

This directory contains customizations that override or extend the base RVO component definitions during conversion.

## Purpose

The base RVO React components sometimes have restricted attribute values. For example:
- Card component only allows 4 background colors
- Some components have limited icon options

Customizations allow you to extend these restrictions while still auto-generating from the React source.

## Structure

### `_tokens.json`
Special file defining design token references that can be used in customizations.

Available token references:
- `all_rvo_colors` - All available RVO color names
- `all_rvo_icons` - All available RVO icon names
- `primary_colors` - Only primary brand colors

These are automatically extracted from `@nl-rvo/design-tokens` and `@nl-rvo/assets`.

### `{component-name}.json`
One file per component that needs customization.

## Example: Extending Card Colors

**File:** `card.json`

```json
{
  "component": "card",
  "description": "Allow all RVO colors instead of just 4",
  "attribute_overrides": {
    "backgroundColor": {
      "type": "enum",
      "values": "all_rvo_colors",
      "description": "Extended to support full RVO color palette"
    }
  },
  "notes": [
    "Original RVO card only supports 4 background colors",
    "Extended to support full palette for more flexibility"
  ]
}
```

## Customization Options

### `attribute_overrides`
Override existing attributes from the React component.

```json
"attribute_overrides": {
  "attributeName": {
    "type": "enum",
    "values": "all_rvo_colors",  // Token reference OR ["value1", "value2"]
    "required": false,
    "description": "Override description"
  }
}
```

### `attribute_additions`
Add new attributes not in the React component.

```json
"attribute_additions": {
  "customIcon": {
    "type": "enum",
    "values": "all_rvo_icons",
    "required": false,
    "description": "Custom icon support"
  }
}
```

### `notes`
Documentation about what was customized and why.

```json
"notes": [
  "Extended color palette for more design flexibility",
  "Added icon support for better visual hierarchy"
]
```

## Token References vs Static Values

**Token Reference** (automatically extracted):
```json
"values": "all_rvo_colors"  // Will extract current colors from @nl-rvo packages
```

**Static List**:
```json
"values": ["hemelblauw", "donkerblauw", "wit"]  // Fixed list
```

## How Customizations Are Applied

1. Conversion script reads React component definition
2. Checks if `customizations/{component}.json` exists
3. If yes, loads customization file
4. Resolves any token references (e.g., `all_rvo_colors`)
5. Applies overrides to attribute definitions
6. Adds new attributes if specified
7. Generates Jinja template with customized attributes
8. Adds notes to generated definition file

## Updating Design Tokens

When RVO packages are updated with new colors/icons:

```bash
poetry run python scripts/extract_design_tokens.py
```

This regenerates the token values. Customizations using token references will automatically pick up the new values on next conversion.

## Creating a New Customization

1. Create `customizations/{component-name}.json`
2. Define overrides or additions
3. Use token references from `_tokens.json` or static lists
4. Add documentation notes
5. Run conversion: `poetry run python conversion/convert_component.py {component-name}`
6. Check generated template and definition

## Example: Icon Component

```json
{
  "component": "icon",
  "description": "Allow all RVO icons",
  "attribute_overrides": {
    "icon": {
      "type": "enum",
      "values": "all_rvo_icons",
      "description": "Any RVO icon from the design system"
    }
  },
  "notes": "Extended to support all icons from @nl-rvo/assets"
}
```

## Best Practices

1. **Document why**: Always include notes explaining the customization
2. **Use token references**: Prefer `all_rvo_colors` over static lists for maintainability
3. **Keep it minimal**: Only override what's necessary
4. **Test thoroughly**: Verify the generated template works with edge cases
5. **Version control**: Commit customizations alongside conversion scripts
