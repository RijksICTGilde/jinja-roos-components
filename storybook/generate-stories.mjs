/**
 * Generate Storybook stories from ROOS component definitions.
 * Based on the official RVO Storybook structure.
 *
 * Usage: node storybook/generate-stories.mjs
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const SRC = path.join(ROOT, "src", "jinja_roos_components");
const STORIES_DIR = path.join(__dirname, "stories");

// Components to skip (page-level or layout wrappers)
const SKIP_COMPONENTS = new Set([
  "page",
  "footer",
  "menubar",
  "layout-column",
  "layout-row",
  "layout-flow",
  // Simple HTML wrappers — too trivial for own stories
  "b",
  "em",
  "i",
  "small",
  "span",
  "li",
  "div",
  // Sub-components / duplicates of other components
  "checkbox-field",
  "radio-button-field",
  "form-field-select",
  "form-select",
  "field",
  "feedback",
  "label",
  "progress-tracker-step",
  // Table sub-components (shown as part of table story)
  "table-head",
  "table-body",
  "table-row",
  "table-header",
  "table-cell",
]);

function pascalCase(str) {
  return str
    .split("-")
    .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
    .join("");
}

function quoteKey(name) {
  return /^[a-zA-Z_$][a-zA-Z0-9_$]*$/.test(name)
    ? name
    : JSON.stringify(name);
}

function loadOverallDefinitions() {
  return JSON.parse(
    fs.readFileSync(path.join(SRC, "overall_definitions.json"), "utf-8"),
  );
}

function loadIndividualDefinitions() {
  const defsDir = path.join(SRC, "definitions");
  const defs = {};
  if (!fs.existsSync(defsDir)) return defs;
  for (const file of fs.readdirSync(defsDir)) {
    if (!file.endsWith(".json")) continue;
    const data = JSON.parse(
      fs.readFileSync(path.join(defsDir, file), "utf-8"),
    );
    if (data.name) defs[data.name] = data;
  }
  return defs;
}

// ─── Preview wrapper styles for specific components ───
const PREVIEW_STYLE = {
  dialog:
    "background:rgba(0,0,0,0.35);padding:3rem;min-height:300px;display:flex;align-items:center;justify-content:center",
};

// ─── Default args matching official RVO Storybook ───

const DEFAULT_ARGS = {
  button: {
    kind: "primary",
    size: "md",
    label: "Button",
    disabled: false,
    icon: "",
    iconAriaLabel: "",
    fullWidth: false,
  },
  alert: {
    kind: "info",
    heading: "",
    content:
      'Dit is een voorbeeld van een melding, met een <a href="#" class="rvo-link">link</a> erin.',
    closable: false,
    padding: "md",
  },
  card: {
    title: "",
    content: "Content",
    outline: true,
    padding: "sm",
    fullCardLink: false,
    showLinkIndicator: true,
    backgroundColor: "none",
    layout: "column",
    image: "",
    imageAlt: "",
    invertedColors: false,
  },
  link: {
    content: "Dit is een link",
    href: "#",
    icon: "",
    iconPlacement: "before",
    noUnderline: false,
  },
  icon: {
    icon: "home",
    size: "md",
    color: "hemelblauw",
    ariaLabel: "",
  },
  tag: {
    content: "Tag naam",
  },
  heading: {
    type: "h1",
    content: "Heading",
  },
  tabs: {
    activeTab: "0",
    tabs: '[{"label": "Tab 1", "href": "#"}, {"label": "Tab 2", "href": "#"}, {"label": "Tab 3", "href": "#"}]',
    content: "<p>Inhoud van het geselecteerde tabblad.</p>",
  },
  checkbox: {
    id: "field",
    name: "group",
    label: "Label",
    checked: false,
    disabled: false,
    invalid: false,
    required: false,
  },
  "checkbox-field": {
    id: "field",
    name: "group",
    label: "Label",
    checked: false,
    disabled: false,
    invalid: false,
  },
  hero: {
    title: "Hero titel",
    subtitle: "Ondertitel van de hero",
    size: "md",
  },
  "action-group": {},
  "data-list": {},
  grid: { columns: "2", gap: "md" },
  header: { type: "h1", content: "Heading" },
  input: { id: "field", type: "text", placeholder: "Voer tekst in" },
  select: { id: "field" },
  "select-field": { label: "Label", id: "field" },
  textarea: { id: "field", placeholder: "Voer tekst in" },
  "textarea-field": { label: "Label", id: "field" },
  "text-input-field": { label: "Label", id: "field" },
  "date-input-field": { label: "Datum", id: "field" },
  "file-input-field": { label: "Bestand kiezen", id: "field" },
  "radio-button-field": { label: "Label", id: "field", name: "group" },
  radio: { id: "field", name: "group", label: "Optie" },
  fieldset: { legend: "Fieldset legend" },
  "status-icon": { type: "bevestiging", size: "md" },
  paragraph: { content: "Dit is een paragraaf met tekst." },
  label: { content: "Label", htmlFor: "field" },
  "max-width-layout": { size: "md", content: "Content binnen de layout." },
  "progress-tracker": {},
  "progress-tracker-step": {
    state: "incomplete",
    line: "none",
    size: "md",
    label: "Stap label",
  },
  feedback: { text: "Dit is feedback tekst.", type: "warning" },
  field: { label: "Label", fieldId: "field" },
  "form-field": { label: "Label", fieldId: "field" },
  "form-select": { id: "field" },
  "form-field-select": {},
  "form-fieldset": { legend: "Fieldset legend" },
  "horizontal-rule": {},
  dialog: {
    id: "demo-dialog",
    modalTitle: "Gebruiker bewerken",
    size: "md",
    open: true,
    content: "<p>Dialog content</p>",
    footer: '<c-button kind="secondary" type="button">Annuleren</c-button><c-button kind="primary" type="submit">Opslaan</c-button>',
  },
  "search-field": {
    id: "search",
    placeholder: "Zoek medewerker...",
    label: "Zoeken",
  },
  table: {
    responsive: true,
    content: `<c-table-head><c-table-row><c-table-header size="md">Naam</c-table-header><c-table-header size="lg">Functie</c-table-header><c-table-header size="sm" numeric="true">Uren</c-table-header></c-table-row></c-table-head><c-table-body><c-table-row><c-table-cell>Jan Jansen</c-table-cell><c-table-cell>Ontwikkelaar</c-table-cell><c-table-cell numeric="true">40</c-table-cell></c-table-row><c-table-row><c-table-cell>Piet Pietersen</c-table-cell><c-table-cell>Designer</c-table-cell><c-table-cell numeric="true">32</c-table-cell></c-table-row></c-table-body>`,
  },
  ol: { items: '["Item 1", "Item 2", "Item 3"]' },
  ul: { items: '["Item 1", "Item 2", "Item 3"]' },
  "ordered-unordered-list": { items: '["Item 1", "Item 2", "Item 3"]' },
  list: { variant: "unordered" },
  "list-item": {},
  div: {},
  span: {},
  strong: {},
  em: {},
  b: {},
  i: {},
  small: {},
  li: {},
};

// ─── Content for components that need children ───

const DEFAULT_CONTENT = {
  card: "Dit is de content van de card.",
  div: "Content",
  span: "Inline tekst",
  li: "List item",
  "list-item": "List item",
  link: "Dit is een link",
  heading: "Heading",
  header: "Heading",
  strong: "Belangrijke tekst",
  em: "Benadrukte tekst",
  b: "Vetgedrukte tekst",
  i: "Schuine tekst",
  small: "Kleine tekst",
};

// ─── Variant stories per component (matching RVO Storybook) ───

const COMPONENT_VARIANTS = {
  button: {
    "Kinds": {
      Primary: { kind: "primary" },
      Secondary: { kind: "secondary" },
      Tertiary: { kind: "tertiary" },
      Quaternary: { kind: "quaternary" },
      WarningSubtle: { kind: "warning-subtle" },
      Warning: { kind: "warning" },
    },
    "Sizes": {
      ExtraSmall: { size: "xs" },
      Small: { size: "sm" },
      Medium: { size: "md" },
    },
    "States": {
      Hover: { hover: "true" },
      Active: { active: "true" },
      Focus: { focus: "true" },
      FocusVisible: { focus: "true", focusVisible: "true" },
      Disabled: { disabled: "true" },
      Busy: { busy: "true" },
    },
    "Icons": {
      WithIconBefore: { icon: "home", iconPlacement: "before" },
      WithIconAfter: { icon: "home", iconPlacement: "after" },
    },
  },
  alert: {
    "Kinds": {
      Info: {
        kind: "info",
        content: "Dit is een voorbeeld van een info melding.",
      },
      Warning: {
        kind: "warning",
        content: "Dit is een voorbeeld van een waarschuwing.",
      },
      Error: {
        kind: "error",
        content: "Dit is een voorbeeld van een foutmelding.",
      },
      Success: {
        kind: "success",
        content: "Dit is een voorbeeld van een succesmelding.",
      },
    },
  },
  dialog: {
    "Sizes": {
      Small: { size: "sm", modalTitle: "Small dialog", open: true, content: "<p>Dialog content</p>" },
      Medium: { size: "md", modalTitle: "Medium dialog", open: true, content: "<p>Dialog content</p>" },
      Large: { size: "lg", modalTitle: "Large dialog", open: true, content: "<p>Dialog content</p>" },
      ExtraLarge: { size: "xl", modalTitle: "Extra large dialog", open: true, content: "<p>Dialog content</p>" },
    },
    "Types": {
      Centered: { type: "centered", modalTitle: "Centered dialog", open: true, content: "<p>Gecentreerde dialog (standaard)</p>" },
      DrawerRight: { type: "inset-inline-end", modalTitle: "Drawer rechts", open: true, content: "<p>Drawer aan de rechterkant</p>" },
      DrawerLeft: { type: "inset-inline-start", modalTitle: "Drawer links", open: true, content: "<p>Drawer aan de linkerkant</p>" },
    },
  },
  icon: {
    "Sizes": {
      ExtraSmall: { size: "xs" },
      Small: { size: "sm" },
      Medium: { size: "md" },
      Large: { size: "lg" },
      ExtraLarge: { size: "xl" },
      XXL: { size: "2xl" },
      XXXL: { size: "3xl" },
      XXXXL: { size: "4xl" },
    },
  },
  heading: {
    "Levels": {
      H1: { type: "h1", content: "Heading niveau 1" },
      H2: { type: "h2", content: "Heading niveau 2" },
      H3: { type: "h3", content: "Heading niveau 3" },
      H4: { type: "h4", content: "Heading niveau 4" },
      H5: { type: "h5", content: "Heading niveau 5" },
      H6: { type: "h6", content: "Heading niveau 6" },
    },
  },
  paragraph: {
    "Sizes": {
      Small: { size: "sm" },
      Medium: { size: "md" },
      Large: { size: "lg" },
    },
  },
  "status-icon": {
    "Types": {
      Info: { type: "info" },
      Bevestiging: { type: "bevestiging" },
      Waarschuwing: { type: "waarschuwing" },
      Foutmelding: { type: "foutmelding" },
    },
  },
};

// ─── Component categories (like RVO Storybook sidebar) ───

const COMPONENT_CATEGORIES = {
  "Brand/Typografie": new Set([
    "heading", "paragraph", "link", "list", "list-item",
    "ordered-unordered-list", "ol", "ul", "li",
    "strong", "em", "b", "i", "small", "span",
  ]),
  "Layout": new Set([
    "grid", "max-width-layout", "div", "horizontal-rule",
  ]),
};

function getStoryTitle(componentName) {
  const pascal = pascalCase(componentName);
  for (const [category, components] of Object.entries(COMPONENT_CATEGORIES)) {
    if (components.has(componentName)) return `${category}/${pascal}`;
  }
  return `Componenten/${pascal}`;
}

// ─── Source code generation ───

function buildJinjaSource(componentName, args, hasChildrenContent) {
  let attrsStr = "";
  const content = hasChildrenContent ? args.content || "" : args.content || "";

  for (const [key, value] of Object.entries(args)) {
    if (key === "content") continue;
    if (value === false || value === "" || value === null || value === undefined)
      continue;
    if (value === true) {
      attrsStr += ` ${key}="true"`;
    } else {
      attrsStr += ` ${key}="${value}"`;
    }
  }

  if (content) {
    return `<c-${componentName}${attrsStr}>${content}</c-${componentName}>`;
  }
  return `<c-${componentName}${attrsStr} />`;
}

// ─── Story generation ───

function buildArgTypesBlock(attributes) {
  const lines = [];
  for (const attr of attributes) {
    if (attr.name === "className" || attr.name === "children") continue;

    const key = quoteKey(attr.name);

    // Color enums with too many options → text input
    if (attr.type === "enum" && attr.enum_values?.length > 20) {
      lines.push(
        `    ${key}: { control: { type: "text" }, description: ${JSON.stringify(attr.description || "")} },`,
      );
      continue;
    }

    let control;
    switch (attr.type) {
      case "enum":
        control = `{ type: "select", options: ${JSON.stringify(attr.enum_values || [])} }`;
        break;
      case "boolean":
        control = '{ type: "boolean" }';
        break;
      case "number":
        control = '{ type: "number" }';
        break;
      default:
        control = '{ type: "text" }';
    }

    let line = `    ${key}: { control: ${control}, description: ${JSON.stringify(attr.description || "")}`;
    if (attr.default !== undefined && attr.default !== null) {
      line += `, table: { defaultValue: { summary: ${JSON.stringify(String(attr.default))} } }`;
    }
    line += " },";
    lines.push(line);
  }
  return lines.join("\n");
}

function generateDefaultStory(componentName, attributes) {
  const pascal = pascalCase(componentName);
  const storyTitle = getStoryTitle(componentName);
  const argTypesBlock = buildArgTypesBlock(attributes);
  const defaultArgs = DEFAULT_ARGS[componentName] || {};
  const defaultContent = DEFAULT_CONTENT[componentName] || "";

  // Components with content attribute don't need separate content arg
  const hasContentAttr = attributes.some((a) => a.name === "content");
  const needsChildrenContent = !hasContentAttr && defaultContent;

  let contentArgType = "";
  if (needsChildrenContent) {
    contentArgType = `\n    content: { control: { type: "text" }, description: "Inner content / children" },`;
  }

  const allArgs = needsChildrenContent
    ? { ...defaultArgs, content: defaultContent }
    : { ...defaultArgs };

  const sourceCode = buildJinjaSource(componentName, allArgs, needsChildrenContent);
  const previewStyle = PREVIEW_STYLE[componentName] || "";

  return `import { renderComponent } from "../helpers/renderComponent";
import { buildSource } from "../helpers/buildSource";

const meta = {
  title: "${storyTitle}",
  argTypes: {
${argTypesBlock}${contentArgType}
  },
  parameters: {
    docs: {
      source: {
        language: "html",
        transform: (_code, ctx) => buildSource("${componentName}", ctx.args),
      },
    },
  },
  loaders: [
    async ({ args }) => {
      const { content, ...attrs } = args;
      return await renderComponent("${componentName}", attrs, content || "");
    },
  ],
  render: (_args, { loaded: { html, source } }) => {
    const container = document.createElement("div");
    const preview = document.createElement("div");${previewStyle ? `\n    preview.style.cssText = ${JSON.stringify(previewStyle)};` : ""}
    preview.innerHTML = html;
    container.appendChild(preview);
    if (source) {
      const codeWrap = document.createElement("div");
      codeWrap.style.cssText = "display:flex;justify-content:flex-end;margin-top:12px";
      const btn = document.createElement("button");
      btn.textContent = "Show code";
      btn.style.cssText = "background:#fff;border:1px solid #d9d9d9;border-radius:4px;padding:4px 12px;font-size:12px;color:#333;cursor:pointer;font-family:inherit";
      const codeBlock = document.createElement("pre");
      codeBlock.textContent = source;
      codeBlock.style.cssText = "display:none;width:100%;margin-top:8px;padding:12px 16px;background:#f6f9fc;border:1px solid #e0e0e0;border-radius:4px;font-size:13px;line-height:1.5;font-family:'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace;overflow-x:auto;white-space:pre-wrap";
      btn.onclick = () => {
        const open = codeBlock.style.display !== "none";
        codeBlock.style.display = open ? "none" : "block";
        btn.textContent = open ? "Show code" : "Hide code";
      };
      codeWrap.appendChild(btn);
      container.appendChild(codeWrap);
      container.appendChild(codeBlock);
    }
    return container;
  },
};

export default meta;

export const Default = {
  name: "${pascal}",
  args: ${JSON.stringify(allArgs, null, 4).replace(/\n/g, "\n  ")},
};
`;
}

function generateVariantStory(
  componentName,
  groupName,
  variants,
  attributes,
) {
  const pascal = pascalCase(componentName);
  const storyTitle = getStoryTitle(componentName);
  const argTypesBlock = buildArgTypesBlock(attributes);
  const defaultArgs = DEFAULT_ARGS[componentName] || {};
  const defaultContent = DEFAULT_CONTENT[componentName] || "";

  const hasContentAttr = attributes.some((a) => a.name === "content");
  const needsChildrenContent = !hasContentAttr && defaultContent;

  let contentArgType = "";
  if (needsChildrenContent) {
    contentArgType = `\n    content: { control: { type: "text" }, description: "Inner content / children" },`;
  }

  const baseArgs = needsChildrenContent
    ? { ...defaultArgs, content: defaultContent }
    : { ...defaultArgs };
  const previewStyle = PREVIEW_STYLE[componentName] || "";

  let variantExports = "";
  for (const [storyName, overrides] of Object.entries(variants)) {
    const storyArgs = { ...baseArgs, ...overrides };
    // Handle content override for variants that have it
    const contentOverride = overrides.content;
    if (contentOverride && !hasContentAttr) {
      storyArgs.content = contentOverride;
      delete overrides.content;
    }

    const humanName = storyName.replace(/([A-Z])/g, " $1").trim();
    variantExports += `
export const ${storyName} = {
  name: "${humanName}",
  args: ${JSON.stringify(storyArgs, null, 4).replace(/\n/g, "\n  ")},
};
`;
  }

  return `import { renderComponent } from "../helpers/renderComponent";
import { buildSource } from "../helpers/buildSource";

const meta = {
  title: "${storyTitle}/${groupName}",
  argTypes: {
${argTypesBlock}${contentArgType}
  },
  parameters: {
    docs: {
      source: {
        language: "html",
        transform: (_code, ctx) => buildSource("${componentName}", ctx.args),
      },
    },
  },
  loaders: [
    async ({ args }) => {
      const { content, ...attrs } = args;
      return await renderComponent("${componentName}", attrs, content || "");
    },
  ],
  render: (_args, { loaded: { html, source } }) => {
    const container = document.createElement("div");
    const preview = document.createElement("div");${previewStyle ? `\n    preview.style.cssText = ${JSON.stringify(previewStyle)};` : ""}
    preview.innerHTML = html;
    container.appendChild(preview);
    if (source) {
      const codeWrap = document.createElement("div");
      codeWrap.style.cssText = "display:flex;justify-content:flex-end;margin-top:12px";
      const btn = document.createElement("button");
      btn.textContent = "Show code";
      btn.style.cssText = "background:#fff;border:1px solid #d9d9d9;border-radius:4px;padding:4px 12px;font-size:12px;color:#333;cursor:pointer;font-family:inherit";
      const codeBlock = document.createElement("pre");
      codeBlock.textContent = source;
      codeBlock.style.cssText = "display:none;width:100%;margin-top:8px;padding:12px 16px;background:#f6f9fc;border:1px solid #e0e0e0;border-radius:4px;font-size:13px;line-height:1.5;font-family:'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace;overflow-x:auto;white-space:pre-wrap";
      btn.onclick = () => {
        const open = codeBlock.style.display !== "none";
        codeBlock.style.display = open ? "none" : "block";
        btn.textContent = open ? "Show code" : "Hide code";
      };
      codeWrap.appendChild(btn);
      container.appendChild(codeWrap);
      container.appendChild(codeBlock);
    }
    return container;
  },
};

export default meta;
${variantExports}`;
}

function main() {
  fs.mkdirSync(STORIES_DIR, { recursive: true });

  // Clear existing generated stories
  for (const file of fs.readdirSync(STORIES_DIR)) {
    if (file.endsWith(".stories.js")) {
      fs.unlinkSync(path.join(STORIES_DIR, file));
    }
  }

  const overall = loadOverallDefinitions();
  const individual = loadIndividualDefinitions();

  // Merge all component definitions
  const allComponents = {};
  for (const comp of overall.components || []) {
    allComponents[comp.name] = comp.attributes || [];
  }
  for (const [name, def] of Object.entries(individual)) {
    if (!allComponents[name]) {
      allComponents[name] = def.attributes || [];
    }
  }

  let count = 0;

  for (const [name, attributes] of Object.entries(allComponents)) {
    if (SKIP_COMPONENTS.has(name)) continue;

    const pascal = pascalCase(name);

    // Generate default story
    const defaultStory = generateDefaultStory(name, attributes);
    fs.writeFileSync(
      path.join(STORIES_DIR, `${pascal}.stories.js`),
      defaultStory,
    );
    count++;

    // Generate variant stories
    const variants = COMPONENT_VARIANTS[name];
    if (variants) {
      for (const [groupName, groupVariants] of Object.entries(variants)) {
        const variantStory = generateVariantStory(
          name,
          groupName,
          groupVariants,
          attributes,
        );
        fs.writeFileSync(
          path.join(STORIES_DIR, `${pascal}${groupName}.stories.js`),
          variantStory,
        );
        count++;
      }
    }
  }

  console.log(`Generated ${count} story files in ${STORIES_DIR}`);
}

main();
