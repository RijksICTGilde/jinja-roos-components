# Web-Types for IntelliJ IDE Support

This document explains how to create and maintain web-types definitions for the jinja-roos-components library, enabling IntelliJ IDEA (and other JetBrains IDEs) to provide autocompletion, validation, and documentation for our custom Jinja2 components.

## Overview

Web-types is a JSON format that describes custom HTML elements and their attributes, allowing IDEs to understand and provide intelligent assistance for custom components. For our Jinja2 components library, this means:

- **Autocompletion** of component names and attributes
- **Validation** of attribute values and required fields
- **Inline documentation** when hovering over components
- **Type checking** for boolean, enum, and other typed attributes

## Structure

```
jinja-roos-components/
├── jinja_roos_components/
│   └── templates/
│       └── components/
│           ├── button.html.j2                    # Component template
│           ├── button.web-types.json             # Component web-types definition
│           ├── text-input-field.html.j2
│           ├── text-input-field.web-types.json
│           └── ...
├── generate_web_types.py                         # Aggregation script
└── web-types.json                               # Generated main web-types file
```

## How It Works

1. Each component has its own `.web-types.json` file alongside its template
2. The `generate_web_types.py` script scans for all `*.web-types.json` files
3. It aggregates them into a single `web-types.json` file
4. IntelliJ reads this file to understand the components

## Creating Web-Types for a New Component

### Step 1: Analyze Your Component Template

First, examine your component's Jinja2 template to identify all parameters it accepts:

```jinja2
{# Example: checkbox.html.j2 #}
{% set id = _component_context.id | default('') %}
{% set name = _component_context.name | default('') %}
{% set value = _component_context.value | default('') %}
{% set checked = _component_context.checked | default(false) %}
{% set disabled = _component_context.disabled | default(false) %}
{% set label = _component_context.label | default('') %}
```

### Step 2: Create the Web-Types Definition

Create a file named `[component-name].web-types.json` next to the template:

```json
{
  "name": "c-checkbox",
  "description": "RVO Checkbox component for boolean input",
  "doc-url": "https://rvo.nl/design-system/components/checkbox",
  "attributes": [
    {
      "name": "id",
      "description": "Unique identifier for the checkbox",
      "value": {
        "type": "string",
        "required": true
      }
    },
    {
      "name": "name",
      "description": "Name attribute for form submission",
      "value": {
        "type": "string",
        "required": true
      }
    },
    {
      "name": "value",
      "description": "Value submitted when checkbox is checked",
      "value": {
        "type": "string",
        "required": false
      }
    },
    {
      "name": "checked",
      "description": "Whether the checkbox is initially checked",
      "value": {
        "type": "boolean",
        "required": false,
        "default": "false"
      }
    },
    {
      "name": "disabled",
      "description": "Whether the checkbox is disabled",
      "value": {
        "type": "boolean",
        "required": false,
        "default": "false"
      }
    },
    {
      "name": "label",
      "description": "Label text for the checkbox",
      "value": {
        "type": "string",
        "required": false
      }
    }
  ]
}
```

### Step 3: Attribute Value Types

The following value types are supported:

#### String
```json
{
  "name": "placeholder",
  "description": "Placeholder text",
  "value": {
    "type": "string",
    "required": false
  }
}
```

#### Boolean
```json
{
  "name": "disabled",
  "description": "Whether the element is disabled",
  "value": {
    "type": "boolean",
    "required": false,
    "default": "false"
  }
}
```

#### Number
```json
{
  "name": "maxlength",
  "description": "Maximum character length",
  "value": {
    "type": "number",
    "required": false
  }
}
```

#### Enum (Predefined Options)
```json
{
  "name": "size",
  "description": "Size of the component",
  "value": {
    "type": "enum",
    "required": false,
    "default": "md",
    "enum": ["xs", "sm", "md", "lg", "xl"]
  }
}
```

#### Array/Object (for complex attributes using Jinja2 syntax)
```json
{
  "name": ":items",
  "description": "Array of menu items (Jinja2 expression)",
  "value": {
    "type": "string",
    "required": false
  }
}
```

### Step 4: Special Attributes

#### Event Handlers
Prefix with `@` for event attributes:
```json
{
  "name": "@click",
  "description": "Click event handler",
  "value": {
    "type": "string",
    "required": false
  }
}
```

#### Jinja2 Expressions
Prefix with `:` for attributes that expect Jinja2 expressions:
```json
{
  "name": ":options",
  "description": "Array of options (Jinja2 expression)",
  "value": {
    "type": "string",
    "required": false
  }
}
```

## Regenerating the Main Web-Types File

After adding or modifying component web-types:

```bash
cd /path/to/jinja-roos-components
python generate_web_types.py
```

This will:
1. Scan for all `*.web-types.json` files
2. Aggregate them into `web-types.json`
3. Update `package.json` with the web-types reference (if needed)

## Configuring IntelliJ IDEA

### Automatic Detection
IntelliJ should automatically detect the `web-types.json` file if:
- It's referenced in `package.json` (the script does this automatically)
- The project is opened as a Node.js/Web project

### Manual Configuration
If automatic detection doesn't work:

1. **Go to Settings** → Languages & Frameworks → JavaScript → Libraries
2. **Click Add** → Choose "Node.js Core Modules"
3. **Point to** your `jinja-roos-components` directory
4. **Apply** the changes

### Jinja2 Support
For proper Jinja2 template support:

1. **Install** the Jinja2 plugin (if not already installed)
2. **Go to Settings** → Editor → File Types
3. **Ensure** `.j2` files are associated with Jinja2

## Testing Your Web-Types

Once configured, test that IntelliJ recognizes your components:

1. **Open** any `.html.j2` template file
2. **Type** `<c-` and you should see autocompletion suggestions
3. **Hover** over a component name to see its description
4. **Add** attributes and verify autocompletion works
5. **Check** that required attributes show warnings when missing

## Complete Example: Card Component

### Template Analysis (`card.html.j2`)
```jinja2
{% set title = _component_context.title | default('') %}
{% set padding = _component_context.padding | default('md') %}
{% set background = _component_context.background | default('color') %}
{% set backgroundColor = _component_context.backgroundColor | default('wit') %}
{% set outline = _component_context.outline | default(false) %}
```

### Web-Types Definition (`card.web-types.json`)
```json
{
  "name": "c-card",
  "description": "RVO Card component for grouping related content",
  "doc-url": "https://rvo.nl/design-system/components/card",
  "attributes": [
    {
      "name": "title",
      "description": "Optional title for the card",
      "value": {
        "type": "string",
        "required": false
      }
    },
    {
      "name": "padding",
      "description": "Padding size for card content",
      "value": {
        "type": "enum",
        "required": false,
        "default": "md",
        "enum": ["none", "xs", "sm", "md", "lg", "xl"]
      }
    },
    {
      "name": "background",
      "description": "Background type",
      "value": {
        "type": "enum",
        "required": false,
        "default": "color",
        "enum": ["none", "color", "image"]
      }
    },
    {
      "name": "backgroundColor",
      "description": "Background color when background='color'",
      "value": {
        "type": "enum",
        "required": false,
        "default": "wit",
        "enum": ["wit", "grijs-50", "grijs-100", "hemelblauw-50"]
      }
    },
    {
      "name": "outline",
      "description": "Whether to show a border outline",
      "value": {
        "type": "boolean",
        "required": false,
        "default": "false"
      }
    }
  ]
}
```

## Tips and Best Practices

1. **Keep descriptions concise** but informative
2. **Always specify defaults** when the component has them
3. **Use enums** for attributes with predefined options
4. **Mark attributes as required** only if the component breaks without them
5. **Include doc-url** if documentation exists
6. **Test your definitions** in IntelliJ after generation
7. **Use consistent naming** (kebab-case for attributes)
8. **Document complex attributes** thoroughly

## Troubleshooting

### IntelliJ doesn't show autocompletion
- Check that `web-types.json` exists in the project root
- Verify it's referenced in `package.json`
- Restart IntelliJ after adding web-types
- Check File → Project Structure → Libraries

### Attributes not recognized
- Ensure the component name matches exactly (including `c-` prefix)
- Verify the JSON syntax is valid
- Run `generate_web_types.py` after changes
- Check the generated `web-types.json` includes your component

### Validation not working
- Make sure required fields are marked correctly
- Check that enum values match exactly
- Verify boolean attributes use "true"/"false" as strings in defaults

## Contributing

When adding new components to the library:

1. Create the component template (`.html.j2`)
2. Create the web-types definition (`.web-types.json`)
3. Run `python generate_web_types.py`
4. Test in IntelliJ
5. Commit both the individual and generated files

## Resources

- [Web-Types Specification](https://github.com/JetBrains/web-types)
- [JetBrains Web-Types Documentation](https://plugins.jetbrains.com/docs/intellij/websymbols-web-types.html)
- [JSON Schema for Web-Types](https://raw.githubusercontent.com/JetBrains/web-types/master/schema/web-types.json)