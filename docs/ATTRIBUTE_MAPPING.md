I was also curious about what attributes were set by each component. Only looking at categories 1 and 2 to keep it easy:

## Category 1: Direct 1:1 Mappings

### **c-button** → `<button>`

**Attributes constructed:**
- **class**: Multiple CSS classes based on kind, size, active, busy, hover, focus, full_width, icon
- **type**: button type (default: 'button')
- **disabled**: boolean (when disabled or busy)
- **aria-label**: "Loading..." when busy
- **data-utrecht-button-appearance**: appearance value
- **data-roos-component**: "button"
- **data-roos-kind**: kind value
- **data-roos-size**: size value
- **Event handlers**: via `_event_mixin.j2` (onclick, onchange, etc.)
- **Custom data-*/aria-* attributes**: via event mixin

### **c-link** → `<a>`

**Attributes constructed:**
- **href**: URL (default: '#')
- **target**: link target
- **class**: CSS classes based on no_underline, icon, color, weight, full_container
- **data-roos-component**: "link"
- **data-roos-icon**: icon name (if icon set)
- **data-roos-icon-placement**: icon placement (if icon set)

### **c-heading** → `<h1>` through `<h6>`

**Attributes constructed:**
- **class**: CSS classes based on type, no_margins
- **data-roos-component**: "heading"
- **data-roos-type**: heading type
- **data-roos-no-margins**: boolean value

### **c-paragraph** → `<p>`

**Attributes constructed:**
- **class**: CSS classes based on color, size, no_spacing
- **data-roos-component**: "paragraph"
- **data-roos-size**: size value
- **data-roos-color**: color value
- **data-roos-no-spacing**: boolean value

### **c-input** → `<input>`

**Attributes constructed:**
- **id**: input id
- **name**: input name
- **class**: CSS classes based on disabled, focus, invalid, readonly, required, size
- **type**: input type (default: 'text')
- **placeholder**: placeholder text
- **value**: input value (or defaultValue)
- **disabled**: boolean
- **required**: boolean
- **readonly**: boolean
- **aria-invalid**: "true" when invalid
- **maxlength**: max length
- **inputmode**: "numeric" for currency validation
- **pattern**: "[0-9.,]*" for currency validation
- **oninput/onchange**: Event handlers (supports HTMX)
- **data-roos-component**: "input" (when no prefix/suffix)

### **c-ul** → `<ul>`

**Attributes constructed:**
- **class**: CSS classes based on no_margin, no_padding, bullet_type, bullet_icon
- **data-roos-component**: "ul"

### **c-ol** → `<ol>`

**Attributes constructed:**
- **class**: CSS classes based on no_margin, no_padding
- **data-roos-component**: "ol"

### **c-li** → `<li>`

**Attributes constructed:**
- **class**: Additional class if provided
- **data-roos-component**: "li"

### **c-icon** → `<span>`

**Attributes constructed:**
- **class**: CSS classes based on icon name, size, color
- **role**: "img"
- **aria-label**: icon label (auto-generated or provided)
- **data-roos-component**: "icon"
- **data-roos-icon**: icon name
- **data-roos-size**: size value
- **data-roos-color**: color value
- **style**: background-color for named/hex colors

## Category 2: Minimal Wrapper

### **c-select** → wrapper div + `<select>`

**Wrapper div attributes:**
- **class**: "rvo-select-wrapper"
- **data-roos-component**: "select"

**Select element attributes:**
- **id**: select id
- **name**: select name
- **class**: CSS classes based on disabled, focus, invalid, required
- **disabled**: boolean
- **required**: boolean
- **aria-invalid**: "true" when invalid
- **data-default-value**: default value
- **data-value**: current value
- **onchange**: Event handler (supports HTMX)

### **c-textarea** → wrapper div + `<textarea>`

**Wrapper div attributes:**
- **class**: "rvo-textarea-wrapper"
- **data-roos-component**: "textarea"

**Textarea element attributes:**
- **id**: textarea id
- **name**: textarea name
- **class**: CSS classes based on disabled, focus, invalid, readonly, required
- **rows**: number of rows (default: 4)
- **cols**: number of columns
- **placeholder**: placeholder text
- **disabled**: boolean
- **required**: boolean
- **readonly**: boolean
- **aria-invalid**: "true" when invalid
- **maxlength**: max length
- **oninput/onchange**: Event handlers (supports HTMX)

### **c-checkbox** → `<label>` + `<input type="checkbox">`

**Label attributes:**
- **class**: CSS classes based on active, hover, checked, disabled, focus, invalid, indeterminate, required
- **for**: links to input id
- **data-roos-component**: "checkbox"

**Input element attributes:**
- **id**: checkbox id
- **name**: checkbox name
- **value**: checkbox value
- **class**: "rvo-checkbox__input"
- **type**: "checkbox"
- **checked**: boolean
- **disabled**: boolean
- **required**: boolean
- **data-indeterminate**: "true" when indeterminate
- **aria-describedby**: helper text id
- **aria-invalid**: "true" when invalid
- **data-roos-checkbox-input**: marker attribute
- **onchange**: Event handler (supports HTMX)

### **c-radio** → `<label>` + `<input type="radio">`

**Label attributes:**
- **class**: CSS classes based on active, hover, checked, disabled, focus, invalid, required
- **for**: links to input id
- **data-roos-component**: "radio"

**Input element attributes:**
- **id**: radio id
- **name**: radio name
- **value**: radio value
- **class**: "rvo-radio-button__input"
- **type**: "radio"
- **checked**: boolean
- **disabled**: boolean
- **required**: boolean
- **aria-invalid**: "true" when invalid
- **data-roos-radio-input**: marker attribute
- **onchange**: Event handler (supports HTMX)

## Summary of Attribute Types

Beyond classes, the components construct:

1. **Standard HTML attributes**: id, name, type, href, target, value, placeholder, disabled, required, readonly, checked, rows, cols, maxlength
2. **ARIA attributes**: aria-label, aria-invalid, aria-describedby (plus any custom aria-* passed through via event mixin)
3. **data-roos-* attributes**: Component tracking and metadata (data-roos-component, data-roos-kind, data-roos-size, data-roos-color, etc.)
4. **data-utrecht-* attributes**: Framework-specific attributes (data-utrecht-button-appearance)
5. **Custom data attributes**: Any data-* attributes passed through via event mixin
6. **Event handlers**: onclick, onchange, oninput, onblur, onfocus, etc. (with HTMX support via hx-* attributes)
7. **Input validation attributes**: inputmode, pattern for specific validation types
8. **Style attribute**: For icon color customization (named colors or hex values)

## Event Mixin Support

The `_event_mixin.j2` template provides comprehensive event handling support for components that use it (primarily `c-button`). It supports:

- **Mouse events**: click, dblclick, mousedown, mouseup, mouseover, mouseout, mouseenter, mouseleave, mousemove, contextmenu
- **Keyboard events**: keydown, keyup, keypress
- **Focus events**: focus, blur, focusin, focusout
- **Form events**: submit, change, input, invalid, reset, search, select
- **Touch events**: touchstart, touchend, touchmove, touchcancel
- **Drag events**: drag, dragstart, dragend, dragenter, dragleave, dragover, drop
- **Clipboard events**: copy, cut, paste
- **Media events**: play, pause, ended
- **Window events**: scroll, resize, load, unload, beforeunload
- **Other events**: error, abort, toggle
- **HTMX attributes**: hx-get, hx-post, hx-put, hx-patch, hx-delete, hx-trigger, hx-target, hx-swap, hx-boost, hx-push-url, hx-select, hx-select-oob, hx-indicator, hx-params, hx-vals, hx-confirm, hx-disable, hx-headers

## Purpose of data-roos-* Attributes

The `data-roos-*` attributes serve multiple purposes:

1. **Component identification**: `data-roos-component` identifies the component type for JavaScript selectors and debugging
2. **State tracking**: Attributes like `data-roos-size`, `data-roos-kind`, `data-roos-color` track component configuration
3. **JavaScript integration**: These attributes can be used by JavaScript to query and manipulate components
4. **Testing and debugging**: Makes it easier to identify and test specific components in automated tests
5. **CSS targeting**: Can be used as alternative selectors for styling without relying on class names
