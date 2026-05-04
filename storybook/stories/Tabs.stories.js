import { formatHtml } from "../helpers/formatHtml";
import { renderComponent } from "../helpers/renderComponent";
import { buildSource } from "../helpers/buildSource";

const meta = {
  title: "Componenten/Tabs",
  argTypes: {
    tabLabels: { control: { type: "text" }, description: "Tab labels (komma-gescheiden)", table: { defaultValue: { summary: "Gegevens, Updates" } } },
    activeTab: { control: { type: "number" }, description: "Actieve tab (0-based)", table: { defaultValue: { summary: "0" } } },
    size: { options: ["sm", "md", "lg"], control: { type: "inline-radio" }, description: "Formaat", table: { defaultValue: { summary: "md" } } },
    variant: { options: ["default", "borderless"], control: { type: "inline-radio" }, description: "Stijlvariant", table: { defaultValue: { summary: "default" } } },
    ariaLabel: { control: { type: "text" }, description: "Aria label voor de tablist", table: { defaultValue: { summary: "Tabs" } } },
  },
  parameters: {
    docs: {
      source: {
        language: "html",
        transform: (_code, ctx) => {
          const { tabLabels, ...rest } = ctx.args;
          return buildSource("tabs", { ...rest, tabs: parseTabs(tabLabels) });
        },
      },
    },
  },
  loaders: [
    async ({ args }) => {
      const { tabLabels, ...attrs } = args;
      const tabs = parseTabs(tabLabels);
      const panelContent = `<div class="rvo-tabs__panel" role="tabpanel" tabindex="0"><p>Inhoud van tab ${(attrs.activeTab || 0) + 1}.</p></div>`;
      return await renderComponent("tabs", { ...attrs, tabs: JSON.stringify(tabs) }, panelContent);
    },
  ],
  render: (_args, { loaded: { html, source } }) => {
    const container = document.createElement("div");
    const preview = document.createElement("div");
    preview.innerHTML = html;
    container.appendChild(preview);
    if (source) {
      const codeBlock = document.createElement("pre");
      codeBlock.className = "variant-code";
      const codeEl = document.createElement("code");
      codeEl.textContent = formatHtml(source);
      codeBlock.appendChild(codeEl);
      codeBlock.style.marginTop = "16px";
      codeBlock.style.borderRadius = "6px";
      container.appendChild(codeBlock);
    }
    return container;
  },
};

function parseTabs(labels) {
  return (labels || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)
    .map((label) => ({ label }));
}

export default meta;

export const Playground = {
  name: "Tabs",
  args: {
    tabLabels: "Gegevens, Updates, Notities",
    activeTab: 0,
    size: "md",
    variant: "default",
  },
};
