import { renderComponent } from "./renderComponent";
import { buildSource } from "./buildSource";

/**
 * Render multiple component variants in a grid with labels and code blocks.
 *
 * @param {string} componentName - The component tag name (e.g. "button")
 * @param {Array<{label: string, args: object}>} variants - Array of variant definitions
 * @param {object} [options] - Optional settings
 * @param {string} [options.previewStyle] - CSS for each preview wrapper
 * @returns {HTMLElement} A grid container with all variants rendered
 */
export async function renderVariants(componentName, variants, options = {}) {
  const results = await Promise.all(
    variants.map(async ({ label, args }) => {
      const { content, ...attrs } = args;
      const rendered = await renderComponent(
        componentName,
        attrs,
        content || "",
      );
      const source = buildSource(componentName, args);
      return { label, html: rendered.html, source };
    }),
  );

  const grid = document.createElement("div");
  grid.className = "variant-grid";

  for (const { label, html, source } of results) {
    const card = document.createElement("div");
    card.className = "variant-card";

    const labelEl = document.createElement("h3");
    labelEl.className = "variant-label";
    labelEl.textContent = label;
    card.appendChild(labelEl);

    const preview = document.createElement("div");
    preview.className = "variant-preview";
    if (options.previewStyle) {
      preview.style.cssText = options.previewStyle;
    }
    preview.innerHTML = html;
    // Contain dialog elements within their preview box
    preview.querySelectorAll("dialog").forEach(d => {
      d.style.position = "relative";
      d.style.inset = "unset";
      d.style.maxHeight = "none";
      d.style.maxWidth = "100%";
      d.style.width = "100%";
    });
    card.appendChild(preview);

    const codeBlock = document.createElement("pre");
    codeBlock.className = "variant-code";
    const codeEl = document.createElement("code");
    codeEl.textContent = source;
    codeBlock.appendChild(codeEl);
    card.appendChild(codeBlock);

    grid.appendChild(card);
  }

  return grid;
}
