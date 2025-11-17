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

Field components behave differently depending on whether they wrap a single input or multiple inputs:

#### Single-Input Field Components

For components wrapping a single form control (`c-text-input-field`, `c-select-field`, `c-textarea-field`, `c-date-input-field`, `c-file-input-field`), passthrough attributes go to the **form control element** (input, select, or textarea), not the wrapper.

**Why:** The form control is the interactive element. Testing selectors, event handlers, validation attributes, and ARIA attributes must be on the actual input for proper functionality with testing frameworks, analytics tools, validation libraries, and screen readers.

**Example - Text Input Field:**
```html
<c-text-input-field
    id="email"
    label="Email Address"
    @input="validateEmail()"
    @blur="checkAvailability()"
    data-testid="email-input"
    data-validate="email">
</c-text-input-field>
```

**Renders:**
```html
<div role="group" aria-labelledby="email-label" class="utrecht-form-field">
    <label id="email-label">Email Address</label>
    <input
        id="email"
        type="text"
        class="utrecht-textbox"
        oninput="validateEmail()"
        onblur="checkAvailability()"
        data-testid="email-input"
        data-validate="email" />
</div>
```

**Example - Select Field:**
```html
<c-select-field
    id="country"
    label="Country"
    @change="updateRegions()"
    data-region-selector="true"
    hx-post="/api/regions"
    hx-target="#region-field">
    <option value="nl">Netherlands</option>
    <option value="be">Belgium</option>
</c-select-field>
```

**Renders:**
```html
<div class="utrecht-form-field">
    <label id="country-label">Country</label>
    <div class="rvo-select-wrapper">
        <select
            id="country"
            class="utrecht-select"
            onchange="updateRegions()"
            data-region-selector="true"
            hx-post="/api/regions"
            hx-target="#region-field">
            <option value="nl">Netherlands</option>
            <option value="be">Belgium</option>
        </select>
    </div>
</div>
```

#### Multi-Input Field Components

For components containing multiple form controls (`c-checkbox-field`, `c-radio-button-field`), passthrough attributes go to the **wrapper group** (the outer container with `role="group"`).

**Why:** A single attribute can't logically apply to multiple inputs. The semantic field container is the appropriate target for group-level attributes and events.

**Example - Checkbox Field:**
```html
<c-checkbox-field
    id="preferences"
    label="Preferences"
    @change="updatePreferences()"
    data-field-group="user-settings">
    <!-- multiple checkbox options -->
</c-checkbox-field>
```

**Renders:**
```html
<div
    role="group"
    aria-labelledby="preferences-label"
    class="utrecht-form-field"
    data-roos-component="checkbox-field"
    onchange="updatePreferences()"
    data-field-group="user-settings">
    <label id="preferences-label">Preferences</label>
    <input type="checkbox" id="pref1" />
    <input type="checkbox" id="pref2" />
    <!-- more checkboxes -->
</div>
```

#### Common Use Cases for Field Component Passthrough

**Testing Selectors:**
```html
<c-text-input-field
    id="username"
    label="Username"
    data-testid="signup-username"
    data-cy="username-field">
</c-text-input-field>
```
The `data-testid` and `data-cy` attributes go directly on the `<input>`, making it easy to select in Playwright, Cypress, or other testing frameworks.

**Form Validation:**
```html
<c-text-input-field
    id="email"
    label="Email"
    data-validate="email"
    data-validate-message="Please enter a valid email"
    @input="validateOnChange()">
</c-text-input-field>
```
Validation libraries typically hook into the actual form element, so attributes must be on the `<input>`.

**Analytics Tracking:**
```html
<c-select-field
    id="product"
    label="Product"
    data-analytics-event="product-selection"
    data-analytics-category="signup-flow"
    @change="trackSelection()">
</c-select-field>
```
Event tracking attributes land on the `<select>` element where the change event actually fires.

**HTMX Integration:**
```html
<c-text-input-field
    id="search"
    label="Search"
    hx-post="/api/search"
    hx-trigger="keyup changed delay:500ms"
    hx-target="#results"
    @htmx:afterRequest="updateCount()">
</c-text-input-field>
```
HTMX attributes must be on the `<input>` to properly trigger on user input events.

#### When Passthrough Attributes Are NOT Needed

Field components already handle these automatically via their props. Only use passthrough if you need to **override** the automatic behavior:

- `aria-invalid` (auto-generated from `hasError` or `invalid` props)
- `aria-describedby` (auto-linked to `helperText`/`errorText`)
- `aria-labelledby` (auto-linked to `label`)
- `aria-required` (auto-generated from `required` prop)
- `required`, `disabled`, `readonly` (use the explicit props instead)

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

### Complete Form Example with Testing and Validation

```html
<!-- Text input with validation and testing selectors -->
<c-text-input-field
    id="username"
    name="username"
    label="Username"
    @input="checkAvailability()"
    @blur="validateField()"
    @focus="clearErrors()"
    data-testid="signup-username"
    data-validate="alphanumeric"
    data-min-length="3">
</c-text-input-field>

<!-- Select field with HTMX dynamic loading -->
<c-select-field
    id="country"
    name="country"
    label="Country"
    @change="updateRegions()"
    hx-post="/api/regions"
    hx-target="#region-container"
    data-testid="country-selector"
    data-analytics="country-selection">
    <option value="nl">Netherlands</option>
    <option value="be">Belgium</option>
</c-select-field>

<!-- Multi-input checkbox group -->
<c-checkbox-field
    id="preferences"
    label="Email Preferences"
    @change="savePreferences()"
    data-field-group="notifications"
    data-testid="email-prefs-group">
    <!-- checkbox options -->
</c-checkbox-field>
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
