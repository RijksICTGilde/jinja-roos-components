# Utility Classes Documentation

This document describes the utility class system for Jinja Roos Components, including the attribute mixin and utility wrapper components.

## Overview

The utility class system allows you to apply common styling utilities (text styling, margins, and padding) to components without needing custom CSS. This is achieved through:

1. **Attribute Mixin** - A reusable Jinja2 macro that processes utility attributes
2. **Semantic Wrapper Components** - Pre-styled components like `<c-strong>`, `<c-small>`, etc.
3. **Utility Wrapper Components** - Generic components like `<c-span>` and `<c-div>` for applying utilities

## Utility Attributes

All utility wrapper components and semantic wrappers support three utility attributes:

### `text-style`

Applies text styling utilities from the RVO design system.

**Available values:**
- `subtle` - Subtle text color
- `sm` - Small text size (12px)
- `md` - Medium text size (16px)
- `lg` - Large text size (18px)
- `xl` - Extra large text size (24px)
- `error` - Error text color
- `bold` - Bold font weight
- `italic` - Italic font style
- `no-margins` - Removes margins

**Examples:**
```html
<c-span text-style="bold">Bold text</c-span>
<c-span text-style="italic">Italic text</c-span>
<c-span text-style="bold, italic">Bold and italic</c-span>
<c-div text-style="sm, subtle">Small subtle text</c-div>
```

### `margin`

Applies margin utilities from the RVO design system.

**Simple values:**
- `none` - No margin
- `3xs`, `2xs`, `xs`, `sm`, `md`, `lg`, `xl`, `2xl`, `3xl`, `4xl`, `5xl` - Predefined margin sizes

**Directional patterns:**
Use the pattern `{direction}-{size}` where:
- Direction: `inline-start`, `inline-end`, `block-start`, `block-end`
- Size: Same as simple values

**Examples:**
```html
<c-div margin="md">Medium margin on all sides</c-div>
<c-span margin="inline-end-sm">Small margin at inline end</c-span>
<c-div margin="block-start-lg">Large margin at block start</c-div>
<c-div margin="md, inline-end-xl">Combined margins</c-div>
```

### `padding`

Applies padding utilities from the RVO design system.

**Simple values:**
- `none` - No padding
- `3xs`, `2xs`, `xs`, `sm`, `md`, `lg`, `xl`, `2xl`, `3xl`, `4xl`, `5xl` - Predefined padding sizes

**Directional patterns:**
Use the pattern `{direction}-{size}` where:
- Direction: `inline-start`, `inline-end`, `block-start`, `block-end`
- Size: Same as simple values

**Examples:**
```html
<c-div padding="md">Medium padding on all sides</c-div>
<c-span padding="inline-start-sm">Small padding at inline start</c-span>
<c-div padding="block-end-lg">Large padding at block end</c-div>
<c-div padding="sm, inline-end-md">Combined padding</c-div>
```

## Multi-Value Syntax

All utility attributes support multiple values separated by spaces or commas (with optional spaces):

```html
<!-- Space-separated -->
<c-span text-style="bold italic">Bold and italic</c-span>

<!-- Comma-separated -->
<c-span text-style="bold, italic">Bold and italic</c-span>

<!-- Comma with spaces -->
<c-div margin="md, lg" padding="sm, xl">Multiple utilities</c-div>
```

When multiple values are specified, the system generates multiple CSS classes. For example:
- `text-style="bold, italic"` → `rvo-text--bold rvo-text--italic`
- `margin="md inline-end-sm"` → `rvo-margin--md rvo-margin-inline-end--sm`

## Semantic Wrapper Components

These components provide semantic styling with sensible defaults. They all render as `<span>` elements to avoid CSS reset issues.

### `<c-strong>` and `<c-b>`

Renders bold text using `rvo-text--bold`.

```html
<c-strong>This is bold text</c-strong>
<c-b>This is also bold text</c-b>

<!-- With additional utilities -->
<c-strong text-style="italic" margin="inline-end-sm">Bold and italic with margin</c-strong>
```

### `<c-small>`

Renders small text using `rvo-text--sm`.

```html
<c-small>This is small text</c-small>

<!-- With additional utilities -->
<c-small text-style="bold">Small bold text</c-small>
```

### `<c-i>` and `<c-em>`

Renders italic text using `rvo-text--italic`.

```html
<c-i>This is italic text</c-i>
<c-em>This is emphasized (italic) text</c-em>

<!-- With additional utilities -->
<c-em text-style="bold" margin="md">Bold emphasized with margin</c-em>
```

## Utility Wrapper Components

These components have **no default styling** and only apply the utility classes you specify.

### `<c-span>`

Generic inline wrapper for applying utility classes.

```html
<c-span text-style="bold">Bold text</c-span>
<c-span text-style="bold, italic" margin="md">Bold italic with margin</c-span>
<c-span padding="inline-start-sm" text-style="sm">Small text with padding</c-span>
```

### `<c-div>`

Generic block wrapper for applying utility classes.

```html
<c-div text-style="bold">Bold block content</c-div>
<c-div margin="md lg" padding="sm">Block with margin and padding</c-div>
<c-div text-style="sm, italic">Small italic block</c-div>
```

## Component Attribute Conflicts

When a component already has native `margin` or `padding` attributes (unlikely for `text-style`), the utility attribute mixin should be avoided or will be ignored to prevent conflicts. Currently, the attribute mixin applies to the component regardless, so users should be aware of potential conflicts and choose either:

1. Use the component's native attributes, OR
2. Use the utility attribute mixin

**Example of potential conflict:**
```html
<!-- If a component has a native 'margin' prop -->
<c-custom-component margin="20px" /> <!-- Native prop -->

<!-- Don't mix with utility attribute mixin -->
<c-custom-component margin="md" /> <!-- Utility mixin -->
```

For most wrapper components (span, div, strong, etc.), there are no native margin/padding props, so conflicts are not a concern.

## Generated CSS Classes

The attribute mixin generates CSS classes following these patterns:

### Text Style
Pattern: `rvo-text--{value}`

Examples:
- `text-style="bold"` → `class="rvo-text--bold"`
- `text-style="italic"` → `class="rvo-text--italic"`
- `text-style="sm"` → `class="rvo-text--sm"`

### Margin
**Simple:** `rvo-margin--{size}`
**Directional:** `rvo-margin-{direction}--{size}`

Examples:
- `margin="md"` → `class="rvo-margin--md"`
- `margin="inline-end-sm"` → `class="rvo-margin-inline-end--sm"`
- `margin="block-start-lg"` → `class="rvo-margin-block-start--lg"`

### Padding
**Simple:** `rvo-padding--{size}`
**Directional:** `rvo-padding-{direction}--{size}`

Examples:
- `padding="md"` → `class="rvo-padding--md"`
- `padding="inline-start-sm"` → `class="rvo-padding-inline-start--sm"`
- `padding="block-end-lg"` → `class="rvo-padding-block-end--lg"`

## Implementation Details

### Attribute Mixin (`_attribute_mixin.j2`)

The attribute mixin is implemented as a Jinja2 macro that:

1. Accepts the component context
2. Extracts `text-style`, `margin`, and `padding` attributes
3. Normalizes comma-separated values to space-separated
4. Splits values and generates corresponding CSS classes
5. Returns a space-separated string of CSS classes

**Usage in component templates:**

```jinja
{% import 'components/_attribute_mixin.j2' as attributes %}

{% set utility_classes = attributes.render_utility_classes(_component_context) %}
{% if utility_classes %}
    {% set css_classes = css_classes + utility_classes.split() %}
{% endif %}

<span class="{{ css_classes | join(' ') }}">{{ content | safe }}</span>
```

### Directional Margin/Padding Parsing

The mixin detects directional patterns by:

1. Checking if the value contains hyphens: `'-' in value`
2. Counting hyphens: `value.count('-') >= 2`
3. Splitting into parts and validating length is 3
4. Constructing: `rvo-{utility}-{part1}-{part2}--{part3}`

Example:
- Input: `inline-end-sm`
- Parts: `['inline', 'end', 'sm']`
- Output: `rvo-margin-inline-end--sm`

## Best Practices

1. **Use semantic wrappers** when you need consistent styling (e.g., always bold)
2. **Use utility wrappers** when you need flexible, ad-hoc styling
3. **Combine multiple utilities** for complex styling needs
4. **Prefer semantic HTML** where it makes sense, but use spans to avoid reset issues
5. **Document component-specific** attribute conflicts in your component docs
6. **Use directional patterns** for precise layout control

## Examples

### Complex Text Styling
```html
<p>
  This is normal text, but
  <c-strong text-style="italic" margin="inline-end-sm">this part is bold and italic</c-strong>
  and this continues normally.
</p>
```

### Layout with Utilities
```html
<c-div margin="md" padding="lg">
  <c-span text-style="bold, xl">Large Bold Title</c-span>
  <c-div margin="block-start-sm">
    <c-span text-style="subtle, sm">Small subtle description</c-span>
  </c-div>
</c-div>
```

### Inline Formatting
```html
<p>
  The price is
  <c-span text-style="bold" margin="inline-start-xs inline-end-xs">$99.99</c-span>
  per month.
</p>
```

### Mixed Semantic and Utility Wrappers
```html
<c-div padding="md" margin="block-end-lg">
  <c-strong>Important Notice:</c-strong>
  <c-span text-style="error, bold" margin="inline-start-sm">Action Required</c-span>
</c-div>
```
