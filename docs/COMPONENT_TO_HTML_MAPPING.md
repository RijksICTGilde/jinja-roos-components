# Component-to-HTML Mapping

This document provides an overview of how components in this library map to their HTML equivalents.

## Category 1: Direct 1:1 Mappings

These components render as just the HTML element with no wrapper.

- **`c-button`** → `<button>`
- **`c-link`** → `<a>` (with `<span role="img"...>` icon iside if defined)
- **`c-heading`** → `<h1>` through `<h6>` (type parameter determines which)
- **`c-h1`-`c-h6`** -> `<h1>` through `<h6>`
- **`c-paragraph`** → `<p>`
- **`c-input`** → `<input>` (when no prefix/suffix)
- **`c-ul`** → `<ul>`
- **`c-ol`** → `<ol>`
- **`c-li`** → `<li>`
- **`c-icon`** → `<span role="img" ... >`

```html
<!-- c-button maps directly to <button> -->
<button class="utrecht-button utrecht-button--primary-action" type="button">
    Click me
</button>
```

## Category 2: Minimal Wrapper

These components include the HTML element plus a simple wrapper div or label for styling/layout purposes.

- **`c-select`** → `<select>` in `<div class="rvo-select-wrapper">`
- **`c-textarea`** → `<textarea>` in `<div class="rvo-textarea-wrapper">`
- **`c-checkbox`** → `<input type="checkbox">` in `<label>`
- **`c-radio`** → `<input type="radio">` in `<label>`
- **`c-input`** → `<input>` in `<div class="rvo-layout-row">` (when prefix/suffix present)

```html
<!-- c-select wraps <select> in a div -->
<div class="rvo-select-wrapper" data-roos-component="select">
    <select class="utrecht-select utrecht-select--html-select">
        <option>Option 1</option>
    </select>
</div>
```

## Category 3: Field Components

These components wrap the base element with complete form field structure including `<label>`, helper text divs, error message divs, and aria attributes.

- **`c-text-input-field`** → `<input>` inside `<div role="group">` with label, helper text, error messages
- **`c-select-field`** → `<select>` in `<div class="rvo-select-wrapper">` with label, helper text, error messages
- **`c-checkbox-field`** → Multiple `<input type="checkbox">` inside `<div role="group">` with label, helper text, error messages
- **`c-radio-button-field`** → Multiple `<input type="radio">` in `<div role="group">` with label, helper text, error messages
- **`c-textarea-field`** → `<textarea>` inside `<div role="group">` with label, helper text, error messages
- **`c-date-input-field`** → `<input type="date">` inside `<div>` with label, helper text, error messages
- **`c-file-input-field`** → `<input type="file">` inside `<div role="group">` with label
- **`c-fieldset`** → `<fieldset>` inside `<div>` wrapper with `<legend>`

```html
<!-- c-text-input-field includes full form field structure -->
<div role="group" class="utrecht-form-field rvo-form-field">
    <div class="rvo-form-field__label">
        <label class="rvo-label" for="name">Name</label>
        <div class="utrecht-form-field-description">Helper text here</div>
    </div>
    <input id="name" type="text" class="utrecht-textbox" />
</div>
```

## Category 4: Layout Components

These are generic `<div>` containers with CSS classes for layout. They have no direct HTML equivalent beyond a plain div.

- **`c-layout-grid`** → `<div>` with CSS Grid classes
- **`c-layout-row`** → `<div>` with flexbox row classes
- **`c-layout-column`** → `<div>` with flexbox column classes
- **`c-layout-flow`** → `<div>` with flow layout classes
- **`c-grid`** → `<div>` with grid layout

## Category 5: Composite/Complex Components

These components contain multiple HTML elements combined into a cohesive UI pattern.

- **`c-alert`** → `<div role="alert">` containing icon `<span>`, heading `<strong>`, content `<div>`, optional close `<button>`
- **`c-card`** → `<div>` containing optional image, title (`<h3>`), content, and link with various layout options
- **`c-action-group`** → Container for grouping buttons/actions
- **`c-tabs`** → Tab interface with tab list and panels
- **`c-menubar`** → Navigation menu structure with items
- **`c-menubar-debug`** → Debug version of menubar
- **`c-header`** → Page header structure
- **`c-footer`** → Page footer structure
- **`c-hero`** → Hero/banner section
- **`c-page`** → Full page wrapper/template
- **`c-data-list`** → `<dl>` (definition list) structure for key-value pairs
- **`c-list`** → Generic list component
- **`c-list-item`** → Generic list item component
- **`c-tag`** → Badge/tag element
