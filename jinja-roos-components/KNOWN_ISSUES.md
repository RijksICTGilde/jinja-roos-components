# Known Issues - ROOS Components

This document tracks known issues and workarounds for the ROOS Components library.

## Footer Component

### Issue: Footer Column Titles Display in Black Instead of White

**Problem Description:**
The footer column titles (h3 elements with classes `rvo-footer__column-title utrecht-heading-3`) are displaying in black text instead of the expected white text in the footer component.

**Root Cause:**
The `utrecht-heading-3` class from the Utrecht Design System sets its own color using the CSS variable `--utrecht-heading-3-color`. When this variable is not defined in the theme, it defaults to black, which overrides the footer's intended white text color.

**Affected Elements:**
- Footer menu column headers (e.g., "RVO Platform", "Ondersteuning")
- Any h3 elements using `utrecht-heading-3` class within the footer

**Current Structure:**
```html
<h3 class="rvo-footer__column-title utrecht-heading-3">Column Title</h3>
```

**Technical Details:**
- The `rvo-footer__column-title` class correctly sets `color: var(--rvo-footer-column-label-color)`
- However, `utrecht-heading-3` class overrides this with `color: var(--utrecht-heading-3-color)`
- The `--utrecht-heading-3-color` CSS variable is not defined in the current theme

**Potential Solutions:**
1. Define `--utrecht-heading-3-color` in your theme CSS variables
2. Use a different heading class that doesn't override the color
3. Set the CSS variable specifically in the footer context
4. Consider removing the `utrecht-heading-3` class if the semantic HTML (h3) is sufficient

**Temporary Workaround:**
Add the following CSS variable definition in your theme:
```css
:root {
  --utrecht-heading-3-color: inherit;
}
```
Or specifically for the footer:
```css
.rvo-footer {
  --utrecht-heading-3-color: var(--rvo-footer-column-label-color, white);
}
```

**Status:** Open
**Reported:** 2024
**Component:** Footer
**Severity:** Visual/Styling

---

## Layout-Flow Component

### Enhancement: Size Attribute Added

**Description:**
The `c-layout-flow` component has been enhanced with a new `size` attribute that controls the max-width layout classes.

**New Feature Details:**
- **Attribute:** `size`
- **Values:** `sm`, `md`, `lg`, `uncentered`
- **Default:** `lg`
- **CSS Classes Generated:** `rvo-max-width-layout rvo-max-width-layout--{size}`

**Usage:**
```html
<c-layout-flow gap="xl" size="lg">Content</c-layout-flow>
```

**Note:** The `gap` and `size` attributes are independent and do not interfere with each other.

---

## Menubar Component

### Enhancement: Selected State Support

**Description:**
The menubar component now supports a `selected` attribute for persistent active/selected state visualization.

**Feature Details:**
- **Attribute:** `selected`
- **Purpose:** Shows menu item as permanently selected (useful for current page indication)
- **Difference from `active`:** 
  - `selected`: Persistent state (always shows as selected)
  - `active`: Temporary state (for click/interaction feedback)

**Usage:**
```html
<c-menubar :items="[
  {'label': 'Home', 'link': '/', 'selected': true},
  {'label': 'About', 'link': '/about'}
]" />
```

---

## Contributing

If you encounter additional issues, please add them to this document with:
- Clear problem description
- Steps to reproduce (if applicable)
- Root cause analysis (if known)
- Potential solutions or workarounds
- Current status

For urgent issues, please also create a GitHub issue in the project repository.