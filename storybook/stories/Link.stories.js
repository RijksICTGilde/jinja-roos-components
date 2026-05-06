import { formatHtml } from "../helpers/formatHtml";
import { renderComponent } from "../helpers/renderComponent";
import { buildSource } from "../helpers/buildSource";

const meta = {
  title: "Componenten/Link",
  argTypes: {
    label: { control: { type: "text" }, description: "Link tekst" },
    href: { control: { type: "text" }, description: "URL", table: { defaultValue: { summary: "#" } } },
    icon: { control: { type: "text" }, description: "Icoon naam (bijv. delta-naar-rechts, externe-link)" },
    iconPlacement: { options: ["before", "after"], control: { type: "inline-radio" }, description: "Icoon positie", table: { defaultValue: { summary: "before" } } },
    iconSize: { options: ["xs", "sm", "md", "lg"], control: { type: "inline-radio" }, description: "Icoon grootte", table: { defaultValue: { summary: "sm" } } },
    noUnderline: { control: { type: "boolean" }, description: "Geen underline", table: { defaultValue: { summary: "false" } } },
    color: { options: ["", "lintblauw", "hemelblauw", "donkerblauw", "grijs-700", "zwart"], control: { type: "select" }, description: "Link kleur" },
    weight: { options: ["", "normal", "bold"], control: { type: "select" }, description: "Font weight" },
    target: { options: ["", "_blank"], control: { type: "select" }, description: "Target" },
  },
  parameters: {
    docs: {
      source: {
        language: "html",
        transform: (_code, ctx) => buildSource("link", ctx.args),
      },
    },
  },
  loaders: [
    async ({ args }) => {
      const { label, ...attrs } = args;
      return await renderComponent("link", attrs, label || "");
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

export default meta;

export const Default = {
  name: "Link",
  args: {
    label: "Voorbeeld link",
    href: "#",
    icon: "",
    iconPlacement: "before",
    iconSize: "sm",
    noUnderline: false,
    color: "",
    weight: "",
    target: "",
  },
};

export const WithIcon = {
  name: "Met icoon",
  args: {
    label: "Privacy",
    href: "#",
    icon: "delta-naar-rechts",
    iconPlacement: "before",
    iconSize: "xs",
    noUnderline: false,
    color: "zwart",
    weight: "normal",
    target: "",
  },
};

export const External = {
  name: "Externe link",
  args: {
    label: "GitHub",
    href: "https://github.com",
    icon: "externe-link",
    iconPlacement: "after",
    iconSize: "xs",
    noUnderline: false,
    color: "",
    weight: "",
    target: "_blank",
  },
};
