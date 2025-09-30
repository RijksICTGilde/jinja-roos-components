# Event Handling in ROOS Components

The ROOS component library supports comprehensive JavaScript event handling through the `@` prefix notation, similar to modern frameworks like Vue.js.

## Features

### Supported Event Types

The event mixin (`components/_event_mixin.j2`) supports all standard HTML events:

#### Mouse Events
- `@click` - Mouse click
- `@dblclick` - Double click  
- `@mousedown`, `@mouseup` - Mouse button press/release
- `@mouseover`, `@mouseout` - Mouse enters/leaves (includes children)
- `@mouseenter`, `@mouseleave` - Mouse enters/leaves (element only)
- `@mousemove` - Mouse movement
- `@contextmenu` - Right-click context menu

#### Keyboard Events
- `@keydown`, `@keyup`, `@keypress` - Keyboard interactions

#### Focus Events
- `@focus`, `@blur` - Element gains/loses focus
- `@focusin`, `@focusout` - Focus events that bubble

#### Form Events
- `@submit` - Form submission
- `@change` - Value change (after blur)
- `@input` - Value change (immediate)
- `@invalid`, `@reset`, `@search`, `@select` - Other form events

#### Touch Events
- `@touchstart`, `@touchend`, `@touchmove`, `@touchcancel` - Touch screen interactions

#### Drag & Drop Events
- `@drag`, `@dragstart`, `@dragend` - Dragging source
- `@dragenter`, `@dragleave`, `@dragover`, `@drop` - Drop target

#### Clipboard Events
- `@copy`, `@cut`, `@paste` - Clipboard operations

#### Media Events
- `@play`, `@pause`, `@ended` - Media playback

#### Window Events
- `@scroll`, `@resize`, `@load`, `@unload`, `@beforeunload` - Window/document events

#### Other Events
- `@error`, `@abort`, `@toggle` - Miscellaneous events

### Data and ARIA Attributes

The system also supports:
- `data-*` attributes for custom data
- `aria-*` attributes for accessibility

### HTMX Support

When HTMX is enabled (`roos_htmx=true`), the following attributes are also supported:
- `@hx-get`, `@hx-post`, `@hx-put`, `@hx-patch`, `@hx-delete` - HTTP methods
- `@hx-trigger`, `@hx-target`, `@hx-swap` - HTMX configuration
- `@hx-boost`, `@hx-push-url`, `@hx-select` - Navigation
- And many more HTMX attributes

## Usage Examples

### Basic Click Handler
```html
<c-button @click="handleClick()">
    Click Me
</c-button>
```

### Multiple Events
```html
<c-button 
    @click="handleClick()"
    @mouseover="showTooltip()"
    @mouseleave="hideTooltip()">
    Hover for tooltip
</c-button>
```

### Form Input Events
```html
<c-text-input-field
    id="username"
    name="username"
    label="Username"
    @input="validateUsername(event)"
    @focus="clearError()"
    @blur="checkAvailability()">
</c-text-input-field>
```

### Complex Event with Data Attributes
```html
<c-button
    @click="submitForm()"
    @keydown="handleKeyShortcut(event)"
    data-form-id="user-form"
    data-action="save"
    aria-label="Save user information">
    Save
</c-button>
```

### HTMX Integration (when enabled)
```html
<c-button
    @hx-post="/api/users"
    @hx-target="#user-list"
    @hx-swap="innerHTML">
    Add User
</c-button>
```

## Implementation Details

### Component Extension
The ComponentExtension (`extension.py`) recognizes attributes with the `@` prefix and passes them to the component context.

### Event Mixin
The `_event_mixin.j2` template provides macros that:
1. `render_events()` - Renders all JavaScript event handlers
2. `render_data_attributes()` - Renders data-* attributes
3. `render_aria_attributes()` - Renders aria-* attributes
4. `render_extra_attributes()` - Combines all above

### Using in Components
Components import and use the event mixin:

```jinja2
{% import 'components/_event_mixin.j2' as events %}

<button 
    class="{{ button_classes }}"
    {{ events.render_extra_attributes(_component_context) }}>
    {{ label }}
</button>
```

## Components with Event Support

The following components have full event support:
- `button.html.j2`
- `text-input-field.html.j2`
- `select-field.html.j2`
- `textarea-field.html.j2`

Other components can easily be updated by:
1. Importing the event mixin
2. Adding `{{ events.render_extra_attributes(_component_context) }}` to the main element

## Security Note

All event handler values are automatically HTML-escaped by Jinja2's autoescape feature. Single quotes in JavaScript strings will be rendered as `&#39;` which is the correct and secure behavior for HTML attributes.