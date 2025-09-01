"""
Component registry for managing component metadata and validation.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class AttributeType(Enum):
    """Types of component attributes."""
    STRING = "string"
    BOOLEAN = "boolean" 
    NUMBER = "number"
    ENUM = "enum"
    OBJECT = "object"


@dataclass
class AttributeDefinition:
    """Definition of a component attribute."""
    name: str
    type: AttributeType
    required: bool = False
    default: Any = None
    description: str = ""
    enum_values: Optional[List[str]] = None
    
    def __post_init__(self) -> None:
        if self.type == AttributeType.ENUM and not self.enum_values:
            raise ValueError("Enum attributes must specify enum_values")


@dataclass 
class ComponentDefinition:
    """Definition of a component."""
    name: str
    description: str
    attributes: List[AttributeDefinition] = field(default_factory=list)
    slots: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    
    def get_attribute(self, name: str) -> Optional[AttributeDefinition]:
        """Get attribute definition by name."""
        for attr in self.attributes:
            if attr.name == name:
                return attr
        return None
    
    def has_attribute(self, name: str) -> bool:
        """Check if component has an attribute."""
        return self.get_attribute(name) is not None


class ComponentRegistry:
    """Registry for managing component definitions."""
    
    def __init__(self) -> None:
        self._components: Dict[str, ComponentDefinition] = {}
        self._register_default_components()
    
    def register_component(self, component: ComponentDefinition) -> None:
        """Register a new component."""
        self._components[component.name] = component
    
    def has_component(self, name: str) -> bool:
        """Check if a component is registered."""
        return name in self._components
    
    def get_component(self, name: str) -> Optional[ComponentDefinition]:
        """Get component definition by name."""
        return self._components.get(name)
    
    def list_components(self) -> List[str]:
        """List all registered component names."""
        return list(self._components.keys())
    
    def get_all_component_names(self) -> List[str]:
        """Get all registered component names (alias for list_components)."""
        return self.list_components()
    
    def get_component_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get component metadata as dictionary."""
        component = self.get_component(name)
        if not component:
            return None
            
        return {
            'name': component.name,
            'description': component.description,
            'attributes': [
                {
                    'name': attr.name,
                    'type': attr.type.value,
                    'required': attr.required,
                    'default': attr.default,
                    'description': attr.description,
                    'enum_values': attr.enum_values,
                }
                for attr in component.attributes
            ],
            'slots': component.slots,
            'examples': component.examples,
        }
    
    def _register_default_components(self) -> None:
        """Register the default RVO-based components."""
        
        # Button component (enhanced to match RVO API)
        button = ComponentDefinition(
            name="button",
            description="RVO button component with Utrecht styling and comprehensive variants",
            attributes=[
                AttributeDefinition(
                    name="kind",
                    type=AttributeType.ENUM,
                    enum_values=["primary", "secondary", "tertiary", "quaternary", "subtle", "warning-subtle", "warning"],
                    default="primary",
                    description="Visual style variant of the button"
                ),
                AttributeDefinition(
                    name="size", 
                    type=AttributeType.ENUM,
                    enum_values=["xs", "sm", "md"],
                    default="md",
                    description="Size of the button"
                ),
                AttributeDefinition(
                    name="label",
                    type=AttributeType.STRING,
                    description="Button text label"
                ),
                AttributeDefinition(
                    name="disabled",
                    type=AttributeType.BOOLEAN,
                    default=False,
                    description="Whether the button is disabled"
                ),
                AttributeDefinition(
                    name="busy",
                    type=AttributeType.BOOLEAN,
                    default=False,
                    description="Whether the button shows a loading/busy state"
                ),
                AttributeDefinition(
                    name="showIcon",
                    type=AttributeType.ENUM,
                    enum_values=["no", "before", "after"],
                    default="no",
                    description="Icon placement in button"
                ),
                AttributeDefinition(
                    name="icon",
                    type=AttributeType.STRING,
                    description="Icon name from RVO icon set"
                ),
                AttributeDefinition(
                    name="fullWidth",
                    type=AttributeType.BOOLEAN,
                    default=False,
                    description="Whether button takes full width"
                ),
                AttributeDefinition(
                    name="type",
                    type=AttributeType.ENUM,
                    enum_values=["button", "submit", "reset"],
                    default="button",
                    description="HTML button type"
                ),
                AttributeDefinition(
                    name="class",
                    type=AttributeType.STRING,
                    description="Additional CSS classes"
                ),
                
                # Event attributes (commonly used with buttons)
                AttributeDefinition(
                    name="click",
                    type=AttributeType.STRING,
                    description="JavaScript function to call on click event"
                ),
                AttributeDefinition(
                    name="mousedown",
                    type=AttributeType.STRING,
                    description="JavaScript function to call on mousedown event"
                ),
                AttributeDefinition(
                    name="mouseup",
                    type=AttributeType.STRING,
                    description="JavaScript function to call on mouseup event"
                ),
                AttributeDefinition(
                    name="focus",
                    type=AttributeType.STRING,
                    description="JavaScript function to call on focus event"
                ),
                AttributeDefinition(
                    name="blur",
                    type=AttributeType.STRING,
                    description="JavaScript function to call on blur event"
                ),
                AttributeDefinition(
                    name="keydown",
                    type=AttributeType.STRING,
                    description="JavaScript function to call on keydown event"
                ),
                AttributeDefinition(
                    name="keyup",
                    type=AttributeType.STRING,
                    description="JavaScript function to call on keyup event"
                ),
            ],
            slots=["content"],
            examples=[
                '<c-button kind="primary" label="Save" />',
                '<c-button kind="secondary" size="sm" label="Cancel" />',
                '<c-button kind="tertiary" showIcon="before" icon="home" label="Home" />',
                '<c-button kind="primary" label="Save" @click="handleSave()" />',
                '<c-button kind="quaternary" label="Delete" @click="confirmDelete(this)" />',
            ]
        )
        
        # Card component (enhanced to match RVO API)
        card = ComponentDefinition(
            name="card",
            description="RVO card component with comprehensive styling and layout options",
            attributes=[
                AttributeDefinition(name="title", type=AttributeType.STRING, description="Card title (displayed in header)"),
                AttributeDefinition(name="content", type=AttributeType.STRING, description="Card content text"),
                AttributeDefinition(name="link", type=AttributeType.STRING, description="Card link URL"),
                AttributeDefinition(name="fullCardLink", type=AttributeType.BOOLEAN, default=False, description="Make entire card clickable"),
                AttributeDefinition(name="showLinkIndicator", type=AttributeType.BOOLEAN, default=False, description="Show arrow indicator for links"),
                AttributeDefinition(name="outline", type=AttributeType.BOOLEAN, default=False, description="Add card outline/border"),
                AttributeDefinition(name="padding", type=AttributeType.ENUM, enum_values=["none", "sm", "md", "lg", "xl"], default="md", description="Card padding size"),
                AttributeDefinition(name="background", type=AttributeType.ENUM, enum_values=["none", "color", "image"], default="none", description="Card background type"),
                AttributeDefinition(name="backgroundColor", type=AttributeType.STRING, default="none", description="Background color from RVO color system"),
                AttributeDefinition(name="backgroundImage", type=AttributeType.STRING, description="Background image URL"),
                AttributeDefinition(name="layout", type=AttributeType.ENUM, enum_values=["column", "row"], default="column", description="Card layout direction"),
                AttributeDefinition(name="image", type=AttributeType.STRING, description="Card image URL"),
                AttributeDefinition(name="imageAlt", type=AttributeType.STRING, description="Image alt text"),
                AttributeDefinition(name="imageSize", type=AttributeType.ENUM, enum_values=["sm", "md"], default="md", description="Image size"),
                AttributeDefinition(name="inlineImage", type=AttributeType.BOOLEAN, default=False, description="Render image inline with content"),
                AttributeDefinition(name="invertedColors", type=AttributeType.BOOLEAN, default=False, description="Use inverted color scheme"),
                AttributeDefinition(name="class", type=AttributeType.STRING, description="Additional CSS classes"),
            ],
            slots=["content"],
            examples=[
                '<c-card title="Settings">Card content here</c-card>',
                '<c-card title="Learn More" link="/learn" :showLinkIndicator="true" outline="true" />',
                '<c-card title="Featured" background="color" backgroundColor="grijs-100" padding="lg" />',
            ]
        )
        
        # Form components
        checkbox = ComponentDefinition(
            name="checkbox",
            description="RVO checkbox input with validation support",
            attributes=[
                AttributeDefinition(
                    name="id", type=AttributeType.STRING, description="HTML id attribute"
                ),
                AttributeDefinition(
                    name="name", type=AttributeType.STRING, description="HTML name attribute"
                ),
                AttributeDefinition(
                    name="label", type=AttributeType.STRING, required=False, description="Checkbox label text"
                ),
                AttributeDefinition(
                    name="checked", type=AttributeType.BOOLEAN, default=False, description="Whether checkbox is checked"
                ),
                AttributeDefinition(
                    name="disabled", type=AttributeType.BOOLEAN, default=False, description="Whether checkbox is disabled"
                ),
                AttributeDefinition(
                    name="required", type=AttributeType.BOOLEAN, default=False, description="Whether checkbox is required"
                ),
                AttributeDefinition(
                    name="invalid", type=AttributeType.BOOLEAN, default=False, description="Whether checkbox has validation error"
                ),
                AttributeDefinition(
                    name="value", type=AttributeType.STRING, description="Checkbox value"
                ),
            ],
            examples=[
                '<c-checkbox label="Accept terms" name="terms" />',
                '<c-checkbox label="Subscribe" :checked="true" />',
            ]
        )
        
        select = ComponentDefinition(
            name="select",
            description="RVO select dropdown with option support",
            attributes=[
                AttributeDefinition(name="id", type=AttributeType.STRING, description="HTML id attribute"),
                AttributeDefinition(name="name", type=AttributeType.STRING, description="HTML name attribute"),
                AttributeDefinition(name="options", type=AttributeType.OBJECT, description="Array of options"),
                AttributeDefinition(name="placeholder", type=AttributeType.STRING, description="Placeholder text"),
                AttributeDefinition(name="disabled", type=AttributeType.BOOLEAN, default=False, description="Whether select is disabled"),
                AttributeDefinition(name="required", type=AttributeType.BOOLEAN, default=False, description="Whether select is required"),
                AttributeDefinition(name="invalid", type=AttributeType.BOOLEAN, default=False, description="Whether select has validation error"),
            ],
            examples=[
                '<c-select name="country" :options="[\'Netherlands\', \'Germany\']" />',
            ]
        )
        
        radio = ComponentDefinition(
            name="radio",
            description="RVO radio button input",
            attributes=[
                AttributeDefinition(name="id", type=AttributeType.STRING, description="HTML id attribute"),
                AttributeDefinition(name="name", type=AttributeType.STRING, description="HTML name attribute"),
                AttributeDefinition(name="label", type=AttributeType.STRING, required=True, description="Radio button label"),
                AttributeDefinition(name="checked", type=AttributeType.BOOLEAN, default=False, description="Whether radio is selected"),
                AttributeDefinition(name="disabled", type=AttributeType.BOOLEAN, default=False, description="Whether radio is disabled"),
                AttributeDefinition(name="value", type=AttributeType.STRING, description="Radio button value"),
            ],
            examples=['<c-radio label="Option 1" name="choice" value="1" />']
        )
        
        textarea = ComponentDefinition(
            name="textarea",
            description="RVO multiline text input",
            attributes=[
                AttributeDefinition(name="id", type=AttributeType.STRING, description="HTML id attribute"),
                AttributeDefinition(name="name", type=AttributeType.STRING, description="HTML name attribute"),
                AttributeDefinition(name="placeholder", type=AttributeType.STRING, description="Placeholder text"),
                AttributeDefinition(name="rows", type=AttributeType.NUMBER, default=4, description="Number of visible text lines"),
                AttributeDefinition(name="disabled", type=AttributeType.BOOLEAN, default=False, description="Whether textarea is disabled"),
                AttributeDefinition(name="required", type=AttributeType.BOOLEAN, default=False, description="Whether textarea is required"),
            ],
            examples=['<c-textarea name="message" placeholder="Enter your message" />']
        )
        
        input_field = ComponentDefinition(
            name="input",
            description="RVO text input with various types and validation",
            attributes=[
                AttributeDefinition(name="id", type=AttributeType.STRING, description="HTML id attribute"),
                AttributeDefinition(name="name", type=AttributeType.STRING, description="HTML name attribute"),
                AttributeDefinition(name="type", type=AttributeType.ENUM, 
                                  enum_values=["text", "email", "password", "tel", "url", "search", "number"], 
                                  default="text", description="Input type"),
                AttributeDefinition(name="placeholder", type=AttributeType.STRING, description="Placeholder text"),
                AttributeDefinition(name="disabled", type=AttributeType.BOOLEAN, default=False, description="Whether input is disabled"),
                AttributeDefinition(name="required", type=AttributeType.BOOLEAN, default=False, description="Whether input is required"),
                AttributeDefinition(name="size", type=AttributeType.ENUM, 
                                  enum_values=["xs", "sm", "md", "lg", "max"], default="md", description="Input size"),
            ],
            examples=['<c-input name="email" type="email" placeholder="Enter email" />']
        )
        
        # Layout components
        layout_flow = ComponentDefinition(
            name="layout-flow",
            description="RVO flexible layout container for organizing content",
            attributes=[
                AttributeDefinition(
                    name="gap", type=AttributeType.ENUM,
                    enum_values=["0", "3xs", "2xs", "xs", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl"],
                    default="md", description="Space between elements"
                ),
                AttributeDefinition(
                    name="size", type=AttributeType.ENUM,
                    enum_values=["sm", "md", "lg", "uncentered"],
                    default="lg", description="Maximum width layout size"
                ),
                AttributeDefinition(name="row", type=AttributeType.BOOLEAN, default=False, description="Use row layout instead of column"),
                AttributeDefinition(name="wrap", type=AttributeType.BOOLEAN, default=False, description="Allow items to wrap"),
                AttributeDefinition(name="alignItems", type=AttributeType.ENUM, enum_values=["", "start", "center", "end"], description="Cross-axis alignment"),
                AttributeDefinition(name="justifyContent", type=AttributeType.ENUM, enum_values=["", "start", "center", "end", "space-between"], description="Main-axis alignment"),
            ],
            slots=["content"],
            examples=[
                '<c-layout-flow gap="lg" size="lg">Content here</c-layout-flow>',
                '<c-layout-flow gap="xl" size="md" :row="true">Row layout</c-layout-flow>'
            ]
        )
        
        grid = ComponentDefinition(
            name="grid",
            description="RVO CSS Grid layout container with comprehensive column support",
            attributes=[
                AttributeDefinition(name="gap", type=AttributeType.ENUM, 
                                  enum_values=["3xs", "2xs", "xs", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl"], 
                                  default="md", description="Grid gap"),
                AttributeDefinition(name="columns", type=AttributeType.ENUM, 
                                  enum_values=["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"], 
                                  description="Number of columns"),
                AttributeDefinition(name="division", type=AttributeType.STRING, description="Custom grid template columns (e.g., '2fr 1fr')"),
                AttributeDefinition(name="class", type=AttributeType.STRING, description="Additional CSS classes"),
            ],
            slots=["content"],
            examples=[
                '<c-grid columns="three" gap="lg">Grid items here</c-grid>',
                '<c-grid division="2fr 1fr" gap="md">Custom layout</c-grid>',
            ]
        )
        
        tag = ComponentDefinition(
            name="tag",
            description="RVO visual tag/badge component",
            attributes=[
                AttributeDefinition(name="content", type=AttributeType.STRING, required=True, description="Tag content text"),
                AttributeDefinition(name="type", type=AttributeType.ENUM, enum_values=["info", "success", "error", "warning"], description="Tag type for semantic coloring"),
                AttributeDefinition(name="isPill", type=AttributeType.BOOLEAN, default=False, description="Use pill (rounded) styling"),
                AttributeDefinition(name="url", type=AttributeType.STRING, description="Make tag clickable with URL"),
            ],
            examples=[
                '<c-tag content="New" type="info" />',
                '<c-tag content="Link tag" url="/page" />',
            ]
        )
        
        # Page component - provides complete HTML structure
        page = ComponentDefinition(
            name="page",
            description="Complete HTML page with RVO styling and ROOS components support",
            attributes=[
                AttributeDefinition(name="title", type=AttributeType.STRING, default="ROOS Page", description="Page title for <title> tag"),
                AttributeDefinition(name="lang", type=AttributeType.STRING, default="nl", description="HTML language attribute"),
                AttributeDefinition(name="charset", type=AttributeType.STRING, default="utf-8", description="Character encoding"),
                AttributeDefinition(name="viewport", type=AttributeType.STRING, default="width=device-width, initial-scale=1.0", description="Viewport meta tag content"),
                AttributeDefinition(name="description", type=AttributeType.STRING, description="Page description for meta tag"),
                AttributeDefinition(name="additionalCss", type=AttributeType.STRING, description="Additional CSS files or inline styles"),
                AttributeDefinition(name="additionalJs", type=AttributeType.STRING, description="Additional JavaScript files or inline scripts"),
                AttributeDefinition(name="bodyClass", type=AttributeType.STRING, description="CSS classes for body element"),
                AttributeDefinition(name="htmx", type=AttributeType.BOOLEAN, default=True, description="Include HTMX library"),
                AttributeDefinition(name="noIndex", type=AttributeType.BOOLEAN, default=False, description="Add noindex meta tag"),
                AttributeDefinition(name="favicon", type=AttributeType.STRING, description="Favicon URL"),
            ],
            slots=["content"],
            examples=[
                '<c-page title="My App"><c-button label="Click me" /></c-page>',
                '<c-page title="Dashboard" bodyClass="dashboard" htmx="false">Page content</c-page>',
            ]
        )
        
        # New hyphenated form components (adding the missing ones)
        text_input_field = ComponentDefinition(
            name="text-input-field",
            description="Complete text input field with label, validation, and help text",
            attributes=[
                AttributeDefinition(name="id", type=AttributeType.STRING, description="HTML id attribute"),
                AttributeDefinition(name="name", type=AttributeType.STRING, description="HTML name attribute"),
                AttributeDefinition(name="label", type=AttributeType.STRING, description="Field label"),
                AttributeDefinition(name="type", type=AttributeType.ENUM, 
                                  enum_values=["text", "email", "password", "tel", "url", "search", "number"], 
                                  default="text", description="Input type"),
                AttributeDefinition(name="value", type=AttributeType.STRING, description="Field value"),
                AttributeDefinition(name="placeholder", type=AttributeType.STRING, description="Placeholder text"),
                AttributeDefinition(name="pattern", type=AttributeType.STRING, description="Regular expression pattern for input validation"),
                AttributeDefinition(name="required", type=AttributeType.BOOLEAN, default=False, description="Required field"),
                AttributeDefinition(name="disabled", type=AttributeType.BOOLEAN, default=False, description="Disabled state"),
                AttributeDefinition(name="readonly", type=AttributeType.BOOLEAN, default=False, description="Read-only state"),
                AttributeDefinition(name="size", type=AttributeType.ENUM, 
                                  enum_values=["xs", "sm", "md", "lg"], default="lg", description="Field width"),
                AttributeDefinition(name="helperText", type=AttributeType.STRING, description="Help text below field"),
                AttributeDefinition(name="expandableHelperText", type=AttributeType.BOOLEAN, default=False, description="Make helper text expandable"),
                AttributeDefinition(name="expandableHelperTextTitle", type=AttributeType.STRING, default="More info", description="Title for expandable helper text"),
                AttributeDefinition(name="errorText", type=AttributeType.STRING, description="Error text with icon"),
                AttributeDefinition(name="warningText", type=AttributeType.STRING, description="Warning text with icon"),
                AttributeDefinition(name="invalid", type=AttributeType.BOOLEAN, default=False, description="Invalid state"),
                AttributeDefinition(name="errorMessage", type=AttributeType.STRING, description="Error message (legacy)"),
                AttributeDefinition(name="hasError", type=AttributeType.BOOLEAN, default=False, description="Error state (legacy)"),
            ],
            examples=[
                '<c-text-input-field id="name" name="name" label="Name" required="true" />',
                '<c-text-input-field id="email" name="email" label="Email" type="email" pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}" />',
                '<c-text-input-field id="phone" name="phone" label="Phone" type="tel" pattern="[0-9]{3}-[0-9]{3}-[0-9]{4}" placeholder="123-456-7890" />'
            ]
        )
        
        select_field = ComponentDefinition(
            name="select-field",
            description="Complete select field with label, validation, and help text",
            attributes=[
                AttributeDefinition(name="id", type=AttributeType.STRING, description="HTML id attribute"),
                AttributeDefinition(name="name", type=AttributeType.STRING, description="HTML name attribute"),
                AttributeDefinition(name="label", type=AttributeType.STRING, description="Field label"),
                AttributeDefinition(name="options", type=AttributeType.OBJECT, description="Array of options"),
                AttributeDefinition(name="value", type=AttributeType.STRING, description="Selected value"),
                AttributeDefinition(name="required", type=AttributeType.BOOLEAN, default=False, description="Required field"),
                AttributeDefinition(name="disabled", type=AttributeType.BOOLEAN, default=False, description="Disabled state"),
                AttributeDefinition(name="size", type=AttributeType.ENUM, 
                                  enum_values=["xs", "sm", "md", "lg"], default="lg", description="Field width"),
                AttributeDefinition(name="helperText", type=AttributeType.STRING, description="Help text below field"),
                AttributeDefinition(name="expandableHelperText", type=AttributeType.BOOLEAN, default=False, description="Whether helper text is expandable"),
                AttributeDefinition(name="expandableHelperTextTitle", type=AttributeType.STRING, description="Title for expandable helper text section"),
                AttributeDefinition(name="errorMessage", type=AttributeType.STRING, description="Error message"),
                AttributeDefinition(name="hasError", type=AttributeType.BOOLEAN, default=False, description="Error state"),
                AttributeDefinition(name="placeholder", type=AttributeType.STRING, description="Placeholder option text"),
            ],
            examples=[
                '<c-select-field id="country" name="country" label="Country" :options="countries" />',
                '<c-select-field id="cpu" name="cpu_limit" label="CPU Limit" :options="cpuOptions" :expandableHelperText="true" expandableHelperTextTitle="More info about CPU limits" />'
            ]
        )
        
        date_input_field = ComponentDefinition(
            name="date-input-field", 
            description="Complete date input field with label, validation, and help text",
            attributes=[
                AttributeDefinition(name="id", type=AttributeType.STRING, description="HTML id attribute"),
                AttributeDefinition(name="name", type=AttributeType.STRING, description="HTML name attribute"),
                AttributeDefinition(name="label", type=AttributeType.STRING, description="Field label"),
                AttributeDefinition(name="value", type=AttributeType.STRING, description="Date value"),
                AttributeDefinition(name="required", type=AttributeType.BOOLEAN, default=False, description="Required field"),
                AttributeDefinition(name="disabled", type=AttributeType.BOOLEAN, default=False, description="Disabled state"),
                AttributeDefinition(name="readonly", type=AttributeType.BOOLEAN, default=False, description="Read-only state"),
                AttributeDefinition(name="size", type=AttributeType.ENUM, 
                                  enum_values=["xs", "sm", "md", "lg"], default="lg", description="Field width"),
                AttributeDefinition(name="helperText", type=AttributeType.STRING, description="Help text below field"),
                AttributeDefinition(name="errorMessage", type=AttributeType.STRING, description="Error message"),
                AttributeDefinition(name="hasError", type=AttributeType.BOOLEAN, default=False, description="Error state"),
                AttributeDefinition(name="minDate", type=AttributeType.STRING, description="Minimum date"),
                AttributeDefinition(name="maxDate", type=AttributeType.STRING, description="Maximum date"),
            ],
            examples=['<c-date-input-field id="birthdate" name="birthdate" label="Birth Date" required="true" />']
        )
        
        fieldset = ComponentDefinition(
            name="fieldset",
            description="Form fieldset grouping with legend",
            attributes=[
                AttributeDefinition(name="legend", type=AttributeType.STRING, description="Fieldset legend text"),
            ],
            slots=["content"],
            examples=['<c-fieldset legend="Personal Information">Form fields here</c-fieldset>']
        )
        
        action_group = ComponentDefinition(
            name="action-group",
            description="Button layout and organization component",
            attributes=[
                AttributeDefinition(name="actions", type=AttributeType.OBJECT, description="Array of action objects"),
                AttributeDefinition(name="alignment", type=AttributeType.ENUM, 
                                  enum_values=["start", "end", "center", "space-between"], 
                                  default="start", description="Action alignment"),
                AttributeDefinition(name="gap", type=AttributeType.ENUM,
                                  enum_values=["xs", "sm", "md", "lg", "xl"],
                                  default="md", description="Gap between actions"),
                AttributeDefinition(name="direction", type=AttributeType.ENUM,
                                  enum_values=["horizontal", "vertical"],
                                  default="horizontal", description="Layout direction"),
            ],
            slots=["content"],
            examples=['<c-action-group :actions="actionButtons" alignment="end" />']
        )
        
        data_list = ComponentDefinition(
            name="data-list",
            description="Read-only information display using definition lists",
            attributes=[
                AttributeDefinition(name="items", type=AttributeType.OBJECT, description="Array of term/value objects"),
            ],
            slots=["content"],
            examples=['<c-data-list :items="businessInfo" />']
        )
        
        # Navigation and layout components
        header = ComponentDefinition(
            name="header",
            description="Site header with logo and navigation content",
            attributes=[
                AttributeDefinition(name="link", type=AttributeType.STRING, default="#", description="Logo link URL"),
                AttributeDefinition(name="text", type=AttributeType.STRING, default="Rijksorganisatie voor Ontwikkeling, Digitalisering en Innovatie", description="Site title text displayed in header"),
                AttributeDefinition(name="subtitle", type=AttributeType.STRING, default="Ministerie van Binnenlandse Zaken en Koninkrijksrelaties", description="Site subtitle text displayed below title"),
                AttributeDefinition(name="class", type=AttributeType.STRING, description="Additional CSS classes"),
            ],
            slots=["content"],
            examples=['<c-header text="Site Title" subtitle="Department" link="/home" />', '<c-header text="Custom Site" class="custom-header" />']
        )
        
        footer = ComponentDefinition(
            name="footer",
            description="Site footer with menu columns",
            attributes=[
                AttributeDefinition(name="primaryMenu", type=AttributeType.OBJECT, description="Primary menu columns"),
                AttributeDefinition(name="secondaryMenu", type=AttributeType.OBJECT, description="Secondary menu items"),
                AttributeDefinition(name="maxWidth", type=AttributeType.ENUM, 
                                  enum_values=["sm", "md", "lg"], description="Maximum width"),
                AttributeDefinition(name="payOff", type=AttributeType.STRING, description="Footer payoff text"),
            ],
            examples=['<c-footer :primaryMenu="footerMenus" maxWidth="lg" />']
        )
        
        menubar = ComponentDefinition(
            name="menubar",
            description="Navigation menu bar component",
            attributes=[
                AttributeDefinition(name="size", type=AttributeType.ENUM, 
                                  enum_values=["sm", "md", "lg"], default="md", description="Menu size"),
                AttributeDefinition(name="direction", type=AttributeType.ENUM,
                                  enum_values=["horizontal", "vertical"], default="horizontal", description="Layout direction"),
                AttributeDefinition(name="items", type=AttributeType.OBJECT, description="Menu items array"),
                AttributeDefinition(name="useIcons", type=AttributeType.BOOLEAN, default=False, description="Enable icons"),
                AttributeDefinition(name="iconPlacement", type=AttributeType.ENUM,
                                  enum_values=["before", "after"], default="before", description="Icon placement"),
                AttributeDefinition(name="maxWidth", type=AttributeType.ENUM,
                                  enum_values=["none", "sm", "md", "lg"], default="none", description="Maximum width"),
                AttributeDefinition(name="horizontalRule", type=AttributeType.BOOLEAN, default=True, description="Show bottom border"),
                AttributeDefinition(name="linkColor", type=AttributeType.ENUM,
                                  enum_values=["donkerblauw", "hemelblauw", "logoblauw", "grijs-700", "zwart"], 
                                  default="logoblauw", description="Link color"),
            ],
            examples=['<c-menubar :items="navItems" size="lg" useIcons="true" />']
        )
        
        icon = ComponentDefinition(
            name="icon", 
            description="Icon component with sizing and coloring",
            attributes=[
                AttributeDefinition(name="icon", type=AttributeType.STRING, required=True, description="Icon name"),
                AttributeDefinition(name="size", type=AttributeType.ENUM,
                                  enum_values=["xs", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl"],
                                  default="md", description="Icon size"),
                AttributeDefinition(name="color", type=AttributeType.STRING, description="Icon color from RVO color system"),
                AttributeDefinition(name="ariaLabel", type=AttributeType.STRING, description="Aria label for accessibility"),
            ],
            examples=['<c-icon icon="home" size="lg" color="hemelblauw" />']
        )
        
        alert = ComponentDefinition(
            name="alert",
            description="Alert/notification component",
            attributes=[
                AttributeDefinition(name="kind", type=AttributeType.ENUM,
                                  enum_values=["info", "warning", "error", "success"], default="info", description="Alert type"),
                AttributeDefinition(name="heading", type=AttributeType.STRING, description="Alert heading"),
                AttributeDefinition(name="content", type=AttributeType.STRING, description="Alert content"),
                AttributeDefinition(name="closable", type=AttributeType.BOOLEAN, default=False, description="Closable alert"),
                AttributeDefinition(name="padding", type=AttributeType.ENUM,
                                  enum_values=["xs", "sm", "md", "lg", "xl", "2xl"], default="md", description="Padding size"),
                AttributeDefinition(name="maxWidth", type=AttributeType.ENUM,
                                  enum_values=["sm", "md", "lg"], description="Maximum width"),
            ],
            examples=['<c-alert kind="warning" heading="Warning" content="Please check your input" />']
        )
        
        hero = ComponentDefinition(
            name="hero",
            description="Hero banner section",
            attributes=[
                AttributeDefinition(name="size", type=AttributeType.ENUM,
                                  enum_values=["sm", "md", "lg"], default="md", description="Hero size"),
                AttributeDefinition(name="image", type=AttributeType.OBJECT, description="Hero image object"),
                AttributeDefinition(name="title", type=AttributeType.STRING, description="Hero title"),
                AttributeDefinition(name="subtitle", type=AttributeType.STRING, description="Hero subtitle"),
                AttributeDefinition(name="overlay", type=AttributeType.BOOLEAN, default=False, description="Text overlay on image"),
            ],
            slots=["content"],
            examples=['<c-hero title="Welcome" subtitle="Hero subtitle" size="lg" />']
        )
        
        tabs = ComponentDefinition(
            name="tabs",
            description="Tab navigation component",
            attributes=[
                AttributeDefinition(name="tabs", type=AttributeType.OBJECT, description="Array of tab objects"),
                AttributeDefinition(name="activeTab", type=AttributeType.NUMBER, default=0, description="Active tab index"),
            ],
            slots=["content"],
            examples=['<c-tabs :tabs="tabItems" :activeTab="0" />']
        )
        
        link = ComponentDefinition(
            name="link",
            description="Enhanced link component with icons",
            attributes=[
                AttributeDefinition(name="href", type=AttributeType.STRING, default="#", description="Link URL"),
                AttributeDefinition(name="content", type=AttributeType.STRING, description="Link text content"),
                AttributeDefinition(name="target", type=AttributeType.STRING, description="Link target"),
                AttributeDefinition(name="icon", type=AttributeType.STRING, description="Icon name"),
                AttributeDefinition(name="showIcon", type=AttributeType.ENUM,
                                  enum_values=["no", "before", "after"], default="no", description="Icon placement"),
                AttributeDefinition(name="iconSize", type=AttributeType.ENUM,
                                  enum_values=["xs", "sm", "md", "lg"], default="sm", description="Icon size"),
                AttributeDefinition(name="iconColor", type=AttributeType.STRING, description="Icon color"),
                AttributeDefinition(name="noUnderline", type=AttributeType.BOOLEAN, default=False, description="Remove underline"),
                AttributeDefinition(name="color", type=AttributeType.STRING, description="Link color"),
                AttributeDefinition(name="weight", type=AttributeType.STRING, description="Font weight"),
                AttributeDefinition(name="fullContainer", type=AttributeType.BOOLEAN, default=False, description="Full container link"),
            ],
            examples=['<c-link href="/page" content="Link Text" showIcon="after" icon="arrow-right" />']
        )
        
        heading = ComponentDefinition(
            name="heading",
            description="Typography heading component",
            attributes=[
                AttributeDefinition(name="type", type=AttributeType.ENUM,
                                  enum_values=["h1", "h2", "h3", "h4", "h5", "h6"], default="h1", description="Heading level"),
                AttributeDefinition(name="textContent", type=AttributeType.STRING, description="Heading text"),
                AttributeDefinition(name="noMargins", type=AttributeType.BOOLEAN, default=False, description="Remove margins"),
            ],
            slots=["content"],
            examples=['<c-heading type="h2" textContent="Section Title" />']
        )
        
        # New advanced form field components
        radio_button_field = ComponentDefinition(
            name="radio-button-field",
            description="Complete radio button field with label, validation, and help text",
            attributes=[
                AttributeDefinition(name="id", type=AttributeType.STRING, description="HTML id attribute"),
                AttributeDefinition(name="name", type=AttributeType.STRING, description="HTML name attribute"),
                AttributeDefinition(name="label", type=AttributeType.STRING, description="Field label"),
                AttributeDefinition(name="options", type=AttributeType.OBJECT, description="Array of radio options"),
                AttributeDefinition(name="helperText", type=AttributeType.STRING, description="Help text below field"),
                AttributeDefinition(name="expandableHelperText", type=AttributeType.BOOLEAN, default=False, description="Make helper text expandable"),
                AttributeDefinition(name="expandableHelperTextTitle", type=AttributeType.STRING, default="More info", description="Title for expandable helper text"),
                AttributeDefinition(name="errorText", type=AttributeType.STRING, description="Error message"),
                AttributeDefinition(name="warningText", type=AttributeType.STRING, description="Warning message"),
                AttributeDefinition(name="invalid", type=AttributeType.BOOLEAN, default=False, description="Invalid state"),
                AttributeDefinition(name="required", type=AttributeType.BOOLEAN, default=False, description="Required field"),
                AttributeDefinition(name="disabled", type=AttributeType.BOOLEAN, default=False, description="Disabled state"),
            ],
            examples=['<c-radio-button-field name="choice" label="Choose option" :options="radioOptions" />']
        )
        
        checkbox_field = ComponentDefinition(
            name="checkbox-field",
            description="Complete checkbox field with label, validation, and help text",
            attributes=[
                AttributeDefinition(name="id", type=AttributeType.STRING, description="HTML id attribute"),
                AttributeDefinition(name="name", type=AttributeType.STRING, description="HTML name attribute"),
                AttributeDefinition(name="label", type=AttributeType.STRING, description="Field label"),
                AttributeDefinition(name="options", type=AttributeType.OBJECT, description="Array of checkbox options"),
                AttributeDefinition(name="helperText", type=AttributeType.STRING, description="Help text below field"),
                AttributeDefinition(name="errorText", type=AttributeType.STRING, description="Error message"),
                AttributeDefinition(name="warningText", type=AttributeType.STRING, description="Warning message"),
                AttributeDefinition(name="invalid", type=AttributeType.BOOLEAN, default=False, description="Invalid state"),
                AttributeDefinition(name="required", type=AttributeType.BOOLEAN, default=False, description="Required field"),
                AttributeDefinition(name="disabled", type=AttributeType.BOOLEAN, default=False, description="Disabled state"),
            ],
            examples=['<c-checkbox-field name="preferences" label="Select preferences" :options="checkboxOptions" />']
        )
        
        textarea_field = ComponentDefinition(
            name="textarea-field",
            description="Complete textarea field with label, validation, and help text",
            attributes=[
                AttributeDefinition(name="id", type=AttributeType.STRING, description="HTML id attribute"),
                AttributeDefinition(name="name", type=AttributeType.STRING, description="HTML name attribute"),
                AttributeDefinition(name="label", type=AttributeType.STRING, description="Field label"),
                AttributeDefinition(name="value", type=AttributeType.STRING, description="Field value"),
                AttributeDefinition(name="placeholder", type=AttributeType.STRING, description="Placeholder text"),
                AttributeDefinition(name="rows", type=AttributeType.NUMBER, default=4, description="Number of rows"),
                AttributeDefinition(name="helperText", type=AttributeType.STRING, description="Help text below field"),
                AttributeDefinition(name="expandableHelperText", type=AttributeType.BOOLEAN, default=False, description="Make helper text expandable"),
                AttributeDefinition(name="expandableHelperTextTitle", type=AttributeType.STRING, default="More info", description="Title for expandable helper text"),
                AttributeDefinition(name="errorText", type=AttributeType.STRING, description="Error message"),
                AttributeDefinition(name="warningText", type=AttributeType.STRING, description="Warning message"),
                AttributeDefinition(name="hasError", type=AttributeType.BOOLEAN, default=False, description="Error state"),
                AttributeDefinition(name="invalid", type=AttributeType.BOOLEAN, default=False, description="Invalid state"),
                AttributeDefinition(name="required", type=AttributeType.BOOLEAN, default=False, description="Required field"),
                AttributeDefinition(name="disabled", type=AttributeType.BOOLEAN, default=False, description="Disabled state"),
                AttributeDefinition(name="readonly", type=AttributeType.BOOLEAN, default=False, description="Read-only state"),
            ],
            examples=['<c-textarea-field name="message" label="Message" rows="6" />']
        )
        
        file_input_field = ComponentDefinition(
            name="file-input-field",
            description="Complete file input field with label, validation, and help text",
            attributes=[
                AttributeDefinition(name="id", type=AttributeType.STRING, description="HTML id attribute"),
                AttributeDefinition(name="name", type=AttributeType.STRING, description="HTML name attribute"),
                AttributeDefinition(name="label", type=AttributeType.STRING, description="Field label"),
                AttributeDefinition(name="accept", type=AttributeType.STRING, description="Accepted file types"),
                AttributeDefinition(name="multiple", type=AttributeType.BOOLEAN, default=False, description="Allow multiple files"),
                AttributeDefinition(name="helperText", type=AttributeType.STRING, description="Help text below field"),
                AttributeDefinition(name="errorText", type=AttributeType.STRING, description="Error message"),
                AttributeDefinition(name="warningText", type=AttributeType.STRING, description="Warning message"),
                AttributeDefinition(name="hasError", type=AttributeType.BOOLEAN, default=False, description="Error state"),
                AttributeDefinition(name="invalid", type=AttributeType.BOOLEAN, default=False, description="Invalid state"),
                AttributeDefinition(name="required", type=AttributeType.BOOLEAN, default=False, description="Required field"),
                AttributeDefinition(name="disabled", type=AttributeType.BOOLEAN, default=False, description="Disabled state"),
            ],
            examples=['<c-file-input-field name="upload" label="Upload file" accept=".pdf,.doc" />']
        )

        # Add layout-row component
        layout_row = ComponentDefinition(
            name="layout-row",
            description="RVO layout row component for grid layouts",
            attributes=[
                AttributeDefinition(
                    name="gap", type=AttributeType.ENUM,
                    enum_values=["xs", "sm", "md", "lg", "xl", "2xl", "3xl"],
                    default="md", description="Gap between columns"
                ),
                AttributeDefinition(
                    name="verticalSpacing", type=AttributeType.ENUM,
                    enum_values=["xs", "sm", "md", "lg", "xl", "2xl", "3xl", "center"],
                    default="lg", description="Vertical spacing/margin around the row or alignment"
                ),
                AttributeDefinition(name="class", type=AttributeType.STRING, description="Additional CSS classes"),
            ],
            slots=["content"],
            examples=['<c-layout-row gap="md" verticalSpacing="lg"><c-layout-column size="md-6">Content</c-layout-column></c-layout-row>']
        )
        
        # Add layout-column component  
        layout_column = ComponentDefinition(
            name="layout-column",
            description="RVO layout column component for grid layouts",
            attributes=[
                AttributeDefinition(
                    name="size", type=AttributeType.STRING,
                    description="Column size (e.g. 'md-6', 'lg-4', 'sm-12')"
                ),
                AttributeDefinition(name="class", type=AttributeType.STRING, description="Additional CSS classes"),
            ],
            slots=["content"],
            examples=['<c-layout-column size="md-6">Column content</c-layout-column>']
        )

        # List component (based on RVO ordered-unordered-list)
        list_component = ComponentDefinition(
            name="list",
            description="RVO list component supporting both ordered and unordered lists with styling options",
            attributes=[
                AttributeDefinition(
                    name="type",
                    type=AttributeType.ENUM,
                    enum_values=["unordered", "ordered"],
                    default="unordered",
                    description="List type - unordered (ul) or ordered (ol)"
                ),
                AttributeDefinition(
                    name="items",
                    type=AttributeType.OBJECT,
                    description="Array of list items (strings) - used when not using nested c-list-item components"
                ),
                AttributeDefinition(
                    name="bulletType",
                    type=AttributeType.ENUM,
                    enum_values=["disc", "none", "icon"],
                    default="disc",
                    description="Bullet type for unordered lists"
                ),
                AttributeDefinition(
                    name="bulletIcon",
                    type=AttributeType.ENUM,
                    enum_values=["option-1", "option-2", "option-3"],
                    default="option-1",
                    description="Icon type when bulletType is 'icon'"
                ),
                AttributeDefinition(
                    name="noMargin",
                    type=AttributeType.BOOLEAN,
                    default=False,
                    description="Remove default margins"
                ),
                AttributeDefinition(
                    name="noPadding",
                    type=AttributeType.BOOLEAN,
                    default=False,
                    description="Remove default padding"
                ),
                AttributeDefinition(
                    name="class",
                    type=AttributeType.STRING,
                    description="Additional CSS classes"
                ),
            ],
            slots=["content"],
            examples=[
                '<c-list type="unordered" :items="[\'Item 1\', \'Item 2\', \'Item 3\']" />',
                '<c-list type="ordered" :items="[\'First\', \'Second\', \'Third\']" />',
                '<c-list type="unordered" bulletType="icon" bulletIcon="option-2" :items="items" />',
                '<c-list type="unordered" bulletType="none" :noMargin="true" :noPadding="true" :items="simpleList" />',
                '<c-list type="unordered"><c-list-item>Custom content</c-list-item><c-list-item>Another item</c-list-item></c-list>'
            ]
        )

        # List item component
        list_item = ComponentDefinition(
            name="list-item",
            description="Individual list item component for use within c-list",
            attributes=[
                AttributeDefinition(
                    name="content",
                    type=AttributeType.STRING,
                    description="List item content"
                ),
                AttributeDefinition(
                    name="class",
                    type=AttributeType.STRING,
                    description="Additional CSS classes"
                ),
            ],
            slots=["content"],
            examples=[
                '<c-list-item>Simple text item</c-list-item>',
                '<c-list-item><strong>Bold</strong> content with HTML</c-list-item>',
                '<c-list-item class="custom-item">Item with custom class</c-list-item>'
            ]
        )

        # Register all components
        for component in [
            # Original components
            button, card, checkbox, select, radio, textarea, input_field, layout_flow, grid, tag, page,
            # New form field components
            text_input_field, select_field, date_input_field, fieldset, action_group, data_list,
            # Advanced form field components
            radio_button_field, checkbox_field, textarea_field, file_input_field,
            # Navigation and layout components
            header, footer, menubar, icon, alert, hero, tabs, link, heading,
            # Grid layout components
            layout_row, layout_column,
            # List components
            list_component, list_item
        ]:
            self.register_component(component)