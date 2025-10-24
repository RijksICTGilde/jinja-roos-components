# Customizations Quick Start

## Example: Extend Card Component Colors

**Problem:** RVO Card component only allows 4 background colors, but you want all RVO colors.

### 1. Create customization file

**File:** `conversion/customizations/card.json`

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

### 2. Run conversion

```bash
poetry run python conversion/convert_component.py card
```

### 3. Output

```
🔄 Converting component: card
============================================================

📁 Locating source files...
   ✓ TSX: .../rvo/components/card/src/template.tsx
   ✓ Defaults: .../rvo/components/card/src/defaultArgs.ts

📖 Parsing React component...
   ✓ Found 5 attributes
   ✓ Found 4 default values
   ✓ Found 3 imports

🎨 Applying customizations...
   ✓ Customizations applied
   ℹ Extended from 4 colors to full RVO palette

...rest of conversion...
```

### 4. Result

**Before customization:**
```python
# backgroundColor only accepts: 'wit', 'grijs-200', 'hemelblauw', 'donkerblauw'
```

**After customization:**
```python
# backgroundColor now accepts all RVO colors:
# hemelblauw, logoblauw, lichtblauw, donkerblauw, groen, oranje,
# donkergeel, rood, wit, grijs, zwart, grijs-200, grijs-300, etc.
```

## Available Token References

Defined in `_tokens.json`:

- **`all_rvo_colors`** - All RVO color names
- **`all_rvo_icons`** - All RVO icon names
- **`primary_colors`** - Just primary brand colors

## Where Values Come From

**Icons:**
Extracted from `node_modules/@nl-rvo/assets/icons/types.ts`

**Colors:**
Extracted from `node_modules/@nl-rvo/design-tokens/src/brand/rvo/color.tokens.json`

Both map **name → value**:
- Colors: `"hemelblauw" → "#0B69B2"`
- Icons: `"home" → category: "interface"`

## Updating Extracted Values

When RVO packages update:

```bash
# Re-extract design tokens
poetry run python scripts/extract_design_tokens.py

# Re-run conversion (automatically picks up new values)
poetry run python conversion/convert_component.py card
```

## Common Customizations

### Allow all icons instead of specific ones

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

### Add a new attribute not in React component

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

### Use static list instead of token reference

```json
{
  "component": "badge",
  "attribute_overrides": {
    "color": {
      "type": "enum",
      "values": ["hemelblauw", "groen", "rood", "oranje"]
    }
  }
}
```

## Testing

After creating a customization:

1. Run conversion
2. Check generated template attributes
3. Test in a real Jinja template:

```jinja
{# Test extended colors #}
<c-card backgroundColor="oranje">
  This should work with the customization!
</c-card>
```

## See Also

- [Full README](README.md) - Complete documentation
- [_tokens.json](_tokens.json) - Available token references
- [card.json](card.json) - Example customization
