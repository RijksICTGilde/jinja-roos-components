# Converting Multi-Variant Components: Split Component Pattern

This guide explains how to convert React components that represent multiple HTML elements into separate Jinja components.

## The Problem

Some React components are designed to represent multiple HTML elements based on a prop. For example:

**`ordered-unordered-list`** from RVO:
- When `type="unordered"` → renders `<ul>` element
- When `type="ordered"` → renders `<ol>` element

In Jinja templates, it's cleaner to have separate components `<c-ul>` and `<c-ol>` rather than a single component with a type prop.

## The Solution: Output-Name-Based Customizations

The conversion script now supports **output-name-based customizations**, allowing you to:
1. Convert the same source component multiple times with different names
2. Apply different customizations to each variant
3. Fix specific prop values per variant

### How It Works

When you specify `--name`, the conversion script checks for customizations in this order:

1. **Output name** (`ul.json`, `ol.json`) ← **First priority**
2. **Source component name** (`ordered-unordered-list.json`) ← Fallback

This allows you to create variant-specific customizations.

## Example: Converting `ordered-unordered-list` to `<c-ul>` and `<c-ol>`

### Step 1: Create Customization for Unordered List

**File**: `conversion/customizations/ul.json`

```json
{
  "component": "ordered-unordered-list",
  "description": "Unordered list variant of ordered-unordered-list",
  "default_overrides": {
    "type": "unordered"
  },
  "attribute_overrides": {
    "type": {
      "values": ["unordered"],
      "description": "Fixed to unordered type"
    }
  },
  "notes": "Unordered list (<ul>) variant with type fixed to 'unordered'"
}
```

**What this does:**
- Sets default `type` to `"unordered"`
- Restricts the `type` attribute to only accept `["unordered"]`
- Documents that this is the UL variant

### Step 2: Create Customization for Ordered List

**File**: `conversion/customizations/ol.json`

```json
{
  "component": "ordered-unordered-list",
  "description": "Ordered list variant of ordered-unordered-list",
  "default_overrides": {
    "type": "ordered"
  },
  "attribute_overrides": {
    "type": {
      "values": ["ordered"],
      "description": "Fixed to ordered type"
    }
  },
  "notes": "Ordered list (<ol>) variant with type fixed to 'ordered'"
}
```

**What this does:**
- Sets default `type` to `"ordered"`
- Restricts the `type` attribute to only accept `["ordered"]`
- Documents that this is the OL variant

### Step 3: Run Conversions

```bash
# Convert as unordered list
poetry run python conversion/convert_component.py ordered-unordered-list --name ul

# Convert as ordered list
poetry run python conversion/convert_component.py ordered-unordered-list --name ol
```

### Step 4: Verify Output

The conversion creates separate files for each variant:

**Generated files for `<c-ul>`:**
- `src/jinja_roos_components/templates/components/ul.html.j2`
- `conversion/definitions/ul.json`
- `conversion/review/ul_review.md`

**Generated files for `<c-ol>`:**
- `src/jinja_roos_components/templates/components/ol.html.j2`
- `conversion/definitions/ol.json`
- `conversion/review/ol_review.md`

### Key Differences in Generated Templates

**`ul.html.j2`:**
```jinja
{% set type = _component_context.type | default('unordered') %}
...
<ListTag
    class="{{ css_classes | join(' ') }}"
    data-roos-component="ul"
    type="{{ type }}"
    ...>
```

**`ol.html.j2`:**
```jinja
{% set type = _component_context.type | default('ordered') %}
...
<ListTag
    class="{{ css_classes | join(' ') }}"
    data-roos-component="ol"
    type="{{ type }}"
    ...>
```

## Usage in Templates

After conversion, you can use the components like standard HTML elements:

```jinja
<!-- Unordered list -->
<c-ul>
  <li>First item</li>
  <li>Second item</li>
  <li>Third item</li>
</c-ul>

<!-- Ordered list -->
<c-ol>
  <li>Step one</li>
  <li>Step two</li>
  <li>Step three</li>
</c-ol>

<!-- With items prop -->
<c-ul items="{{ ['Item 1', 'Item 2', 'Item 3'] }}"></c-ul>

<!-- With custom styling -->
<c-ol
  bulletType="decimal"
  text-style="bold"
  margin="md">
  <li>Bold numbered item</li>
</c-ol>
```

## Other Use Cases for Split Components

This pattern works for any React component that represents multiple variants:

### Button Variants by Type

If you have a `Button` component with `type="submit|button|reset"`:

```bash
# Create submit-button, regular-button, reset-button
poetry run python conversion/convert_component.py button --name submit-button
poetry run python conversion/convert_component.py button --name button
poetry run python conversion/convert_component.py button --name reset-button
```

With customizations:
```json
// submit-button.json
{
  "component": "button",
  "default_overrides": {
    "type": "submit"
  }
}
```

### Heading Levels

If you have a `Heading` component with `level="1|2|3|4|5|6"`:

```bash
# Create h1, h2, h3, h4, h5, h6
poetry run python conversion/convert_component.py heading --name h1
poetry run python conversion/convert_component.py heading --name h2
# ... etc
```

With customizations:
```json
// h1.json
{
  "component": "heading",
  "default_overrides": {
    "level": "1"
  },
  "attribute_overrides": {
    "level": {
      "values": ["1"]
    }
  }
}
```

## Best Practices

### 1. Use Semantic Names

Choose output names that match the HTML element or semantic purpose:
- ✅ `--name ul` (matches `<ul>`)
- ✅ `--name ol` (matches `<ol>`)
- ❌ `--name list-unordered` (less intuitive)

### 2. Document the Split in Customizations

Always include clear notes explaining the variant:

```json
{
  "notes": "Unordered list (<ul>) variant with type fixed to 'unordered'"
}
```

### 3. Restrict Variant-Specific Props

Use `attribute_overrides` to limit prop values to the specific variant:

```json
{
  "attribute_overrides": {
    "type": {
      "values": ["unordered"],
      "description": "Fixed to unordered type"
    }
  }
}
```

This prevents mistakes like using `<c-ul type="ordered">`.

### 4. Keep Common Props Shared

Only override props that differ between variants. Common props like `items`, `noMargin`, etc. should use the same defaults from the source component.

### 5. Test Both Variants

After conversion, test both components to ensure:
- Correct HTML element is rendered
- Default values are applied correctly
- Customizations work as expected

## Troubleshooting

### Customization Not Applied

**Problem:** Conversion runs but customization isn't used.

**Solution:** Check the customization filename matches the **output name** (not source name):
```bash
poetry run python conversion/convert_component.py ordered-unordered-list --name ul
# Looks for: conversion/customizations/ul.json ✓
# Not: conversion/customizations/ordered-unordered-list.json
```

### Both Variants Look Identical

**Problem:** Both templates are the same despite different customizations.

**Solution:** Check that `default_overrides` and `attribute_overrides` are correctly specified in both customization files.

### Type Validation Errors

**Problem:** Users can still pass wrong type values.

**Solution:** Ensure `attribute_overrides` limits the values:
```json
{
  "attribute_overrides": {
    "type": {
      "values": ["unordered"]
    }
  }
}
```

## Technical Details

### How Output-Name Priority Works

The conversion script (`convert_component.py` line 109) checks for customizations in this order:

```python
customization_name = (
    self.output_name
    if self.customization_loader.has_customization(self.output_name)
    else self.component_name
)
```

This allows you to:
1. Create a generic customization for the source component
2. Override with specific customizations per variant

### Customization File Format

```json
{
  "component": "<source-component-name>",
  "description": "What this variant represents",

  "default_overrides": {
    "<prop>": "<value>"
  },

  "attribute_overrides": {
    "<prop>": {
      "values": ["<restricted-values>"],
      "description": "Why this is restricted"
    }
  },

  "notes": "Additional context for reviewers"
}
```

## Related Documentation

- **[Main Conversion Guide](README.md)** - Full conversion documentation
- **[Customization Guide](customizations/README.md)** - Complete customization reference
- **[Customization Quick Start](customizations/QUICKSTART.md)** - Common patterns

## Real-World Example

The `<c-ul>` and `<c-ol>` components were converted using this exact approach:

```bash
# Commands used
poetry run python conversion/convert_component.py ordered-unordered-list --name ul
poetry run python conversion/convert_component.py ordered-unordered-list --name ol

# Files created
conversion/customizations/ul.json
conversion/customizations/ol.json
src/jinja_roos_components/templates/components/ul.html.j2
src/jinja_roos_components/templates/components/ol.html.j2
conversion/definitions/ul.json
conversion/definitions/ol.json
```

**Result:** Two clean, semantic components that map directly to their HTML counterparts, providing better developer experience than a single component with a type prop.
