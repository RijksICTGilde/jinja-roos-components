# Boolean Attributes - Usage Guide

## Overview

Boolean attributes (like `outline`, `disabled`, `fullCardLink`, etc.) now automatically convert string values to proper booleans.

## Supported String Values

### Falsy Values (convert to `False`)
- `"false"`
- `"0"`
- `""` (empty string)
- `"no"`
- `"off"`

### Truthy Values (convert to `True`)
- `"true"`
- `"1"`
- `"yes"`
- `"on"`

**Case-insensitive:** `"FALSE"`, `"False"`, `"false"` all work the same.

## Usage Examples

### Card Component

```jinja
{# All of these work correctly #}

<!-- String "false" - NO outline -->
<c-card outline="false" title="Card 1">
  Content
</c-card>

<!-- String "true" - HAS outline -->
<c-card outline="true" title="Card 2">
  Content
</c-card>

<!-- Numeric strings also work -->
<c-card outline="0" title="Card 3">  <!-- NO outline -->
  Content
</c-card>

<c-card outline="1" title="Card 4">  <!-- HAS outline -->
  Content
</c-card>

<!-- Omitting attribute uses default (usually false) -->
<c-card title="Card 5">  <!-- NO outline (default) -->
  Content
</c-card>

<!-- Binding syntax still works for dynamic values -->
<c-card :outline="some_variable" title="Card 6">
  Content
</c-card>
```

### Button Component

```jinja
<!-- Disabled button -->
<c-button disabled="true">Click me</c-button>
<c-button disabled="1">Click me</c-button>

<!-- NOT disabled -->
<c-button disabled="false">Click me</c-button>
<c-button disabled="0">Click me</c-button>
<c-button>Click me</c-button>  <!-- default is false -->
```

### Full Card Link

```jinja
<!-- Only title is link -->
<c-card title="Title" link="/url" fullCardLink="false">
  Only the title is clickable
</c-card>

<!-- Entire card is link -->
<c-card title="Title" link="/url" fullCardLink="true">
  The entire card is clickable
</c-card>
```

## Why This Works

The component system checks the attribute type in the component registry. For attributes defined as `BOOLEAN` type, it automatically converts common string representations to actual boolean values.

This makes the syntax more intuitive - you don't need to remember special syntax like `:outline="false"` for booleans.

## When to Use Binding Syntax (`:`)

**Use regular syntax for static values:**
```jinja
<c-card outline="false">  <!-- Static false -->
```

**Use binding syntax for dynamic/variable values:**
```jinja
<c-card :outline="show_outline">  <!-- Variable -->
<c-card :outline="user.is_admin">  <!-- Expression -->
```

## Migration from Old Syntax

If you were using binding syntax for static booleans, both still work:

```jinja
<!-- Old way (still works) -->
<c-card :outline="false" :disabled="true">

<!-- New way (simpler) -->
<c-card outline="false" disabled="true">
```

## Technical Details

The conversion happens in `html_parser.py` in the `convert_parsed_component` function. It checks if an attribute is defined as `AttributeType.BOOLEAN` and automatically converts recognized string values.

## Testing

See `examples/test_boolean_fix.html` for comprehensive test cases demonstrating all supported boolean value formats.