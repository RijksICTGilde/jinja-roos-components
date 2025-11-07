# Attribute Passthrough in ROOS Components

The ROOS component library supports attribute passthrough, allowing you to add custom data attributes, ARIA attributes, event handlers, and HTMX attributes to any component.

## Supported Attribute Types

### 1. Data Attributes (`data-*`)

Custom data attributes for storing extra information on elements.

```html
<c-button
    data-user-id="123"
    data-action="delete"
    data-confirm="true">
    Delete User
</c-button>
```

**Renders as:**
```html
<button class="rvo-button" data-user-id="123" data-action="delete" data-confirm="true">
    Delete User
</button>
```

### 2. ARIA Attributes (`aria-*`)

Accessibility attributes for assistive technologies.

```html
<c-button
    aria-label="Close dialog"
    aria-expanded="false"
    aria-controls="menu-panel">
    Menu
</c-button>
```

**Renders as:**
```html
<button class="rvo-button" aria-label="Close dialog" aria-expanded="false" aria-controls="menu-panel">
    Menu
</button>
```

### 3. Event Handlers (`@event`)

JavaScript event handlers using the `@` prefix notation (similar to Vue.js).

```html
<c-button @click="handleClick()" @mouseover="showTooltip()">
    Click Me
</c-button>
```

**Renders as:**
```html
<button class="rvo-button" onclick="handleClick()" onmouseover="showTooltip()">
    Click Me
</button>
```

#### Supported Events

**Mouse Events:**
- `@click`, `@dblclick`, `@mousedown`, `@mouseup`, `@mouseover`, `@mouseout`, `@mouseenter`, `@mouseleave`, `@mousemove`, `@contextmenu`

**Keyboard Events:**
- `@keydown`, `@keyup`, `@keypress`

**Focus Events:**
- `@focus`, `@blur`, `@focusin`, `@focusout`

**Form Events:**
- `@submit`, `@change`, `@input`, `@invalid`, `@reset`, `@search`, `@select`

**Touch Events:**
- `@touchstart`, `@touchend`, `@touchmove`, `@touchcancel`

**Drag & Drop:**
- `@drag`, `@dragstart`, `@dragend`, `@dragenter`, `@dragleave`, `@dragover`, `@drop`

**Clipboard:**
- `@copy`, `@cut`, `@paste`

**Media:**
- `@play`, `@pause`, `@ended`

**Window:**
- `@scroll`, `@resize`, `@load`, `@unload`, `@beforeunload`

**Other:**
- `@error`, `@abort`, `@toggle`

### 4. HTMX Attributes (`hx-*`)

HTMX attributes for dynamic server interactions (when HTMX is enabled).

```html
<c-button
    hx-post="/api/users"
    hx-target="#user-list"
    hx-swap="innerHTML">
    Load Users
</c-button>
```

**Note:** HTMX attributes can also use the `@` prefix: `@hx-post="/api/users"`

### 5. Generic HTML Attributes

Common HTML attributes that don't fit other categories:

- `id` - Element identifier
- `title` - Tooltip text
- `style` - Inline CSS styles
- `role` - ARIA role
- `tabindex` - Tab order

```html
<c-div
    id="main-container"
    title="Main content area"
    style="background-color: #f0f0f0;"
    role="main"
    tabindex="0">
    Content
</c-div>
```

## Where Attributes Land

The placement of passthrough attributes depends on the component structure:

### Simple Components (1-to-1 HTML mapping)

Attributes go on the main semantic element.

**Example - Button:**
```html
<c-button @click="save()" data-action="save">Save</c-button>
```
**Renders:**
```html
<button class="rvo-button" onclick="save()" data-action="save">Save</button>
```

### Container Components

Attributes go on the outermost wrapper element.

**Example - Card:**
```html
<c-card @click="openDetails()" data-card-id="123">...</c-card>
```
**Renders:**
```html
<div class="rvo-card" onclick="openDetails()" data-card-id="123">
    <!-- card content -->
</div>
```

### Form Elements

Attributes go on the semantic form control (input/select/textarea), not the wrapper.

**Example - Input:**
```html
<c-input
    @input="validateEmail()"
    data-validation="email"
    aria-describedby="email-help">
</c-input>
```
**Renders:**
```html
<input
    type="text"
    class="utrecht-textbox"
    oninput="validateEmail()"
    data-validation="email"
    aria-describedby="email-help">
```

**Example - Select:**
```html
<c-select @change="updateRegion()" data-region-id="nl">...</c-select>
```
**Renders:**
```html
<div class="rvo-select-wrapper">
    <select
        class="utrecht-select"
        onchange="updateRegion()"
        data-region-id="nl">
        <!-- options -->
    </select>
</div>
```

### Field Components (Label + Input)

Field wrapper components (like `c-text-input-field`, `c-select-field`) pass attributes to the **field wrapper** (the outer container with `role="group"`), not the inner form elements.

**Example:**
```html
<c-checkbox-field
    id="terms"
    label="Terms and Conditions"
    @click="trackInteraction()"
    data-field-group="legal">
</c-checkbox-field>
```
**Renders:**
```html
<div
    role="group"
    aria-labelledby="terms-label"
    class="utrecht-form-field"
    data-roos-component="checkbox-field"
    onclick="trackInteraction()"
    data-field-group="legal">
    <label id="terms-label">Terms and Conditions</label>
    <!-- checkbox inputs -->
</div>
```

**Note:** For multi-input field components like `c-checkbox-field` and `c-radio-button-field`, attributes apply to the entire group wrapper, not individual inputs. This is because applying the same attributes to multiple inputs in a loop doesn't make semantic sense.

## Components with Passthrough Support

**58 components** currently support attribute passthrough:

### Layout Components
- `c-action-group`, `c-card`, `c-div`, `c-footer`, `c-grid`, `c-header`, `c-hero`, `c-layout-column`, `c-layout-grid`, `c-layout-row`, `c-layout-flow`, `c-max-width-layout`, `c-page`

### Text Components
- `c-b`, `c-em`, `c-heading`, `c-i`, `c-label`, `c-paragraph`, `c-small`, `c-span`, `c-strong`

### List Components
- `c-data-list`, `c-li`, `c-list`, `c-list-item`, `c-ol`, `c-ordered-unordered-list`, `c-ul`

### Interactive Components
- `c-alert`, `c-button`, `c-link`, `c-menubar`, `c-progress-tracker`, `c-progress-tracker-step`, `c-status-icon`, `c-tabs`, `c-tag`

### Form Components
- `c-checkbox`, `c-checkbox-field`, `c-date-input-field`, `c-fieldset`, `c-file-input-field`, `c-form-field`, `c-form-field-select`, `c-form-fieldset`, `c-form-select`, `c-horizontal-rule`, `c-input`, `c-radio`, `c-radio-button-field`, `c-select`, `c-select-field`, `c-text-input-field`, `c-textarea`, `c-textarea-field`

### Other Components
- `c-icon`

## Practical Examples

### Complete Form Example

```html
<c-text-input-field
    id="username"
    name="username"
    label="Username"
    @input="checkAvailability()"
    @blur="validateField()"
    @focus="clearErrors()"
    data-field-type="username"
    data-required="true"
    aria-required="true"
    aria-describedby="username-help">
</c-text-input-field>

<c-select-field
    id="country"
    name="country"
    label="Country"
    @change="updateRegions()"
    data-category="location"
    aria-label="Select your country">
    <option value="nl">Netherlands</option>
    <option value="be">Belgium</option>
</c-select-field>
```

### Navigation with HTMX

```html
<c-button
    hx-get="/api/dashboard"
    hx-target="#content"
    hx-swap="innerHTML"
    hx-indicator="#spinner"
    @htmx:afterSwap="initCharts()"
    data-page="dashboard"
    aria-label="Load dashboard">
    Dashboard
</c-button>
```

### Accessible Card with Events

```html
<c-card
    @click="openModal()"
    @keydown="handleKeyPress(event)"
    data-modal-id="product-123"
    data-product-category="electronics"
    aria-label="Product details for Laptop Pro"
    role="button"
    tabindex="0"
    title="Click to view product details">

    <c-heading type="h3">Laptop Pro</c-heading>
    <c-paragraph>€999.00</c-paragraph>
</c-card>
```

### Dynamic List Item

```html
<c-li
    @click="selectItem()"
    @dblclick="editItem()"
    @contextmenu="showContextMenu(event)"
    data-item-id="456"
    data-item-type="task"
    data-priority="high"
    aria-selected="false"
    aria-label="Task: Review documentation"
    role="option"
    tabindex="0">
    Review documentation
</c-li>
```
