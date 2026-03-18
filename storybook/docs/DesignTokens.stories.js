function navigateTo(storyPath) {
  const url = `/story/${storyPath}--default`;
  if (window.top !== window) {
    window.top.location.href = `/?path=${url}`;
  } else {
    window.location.href = `/?path=${url}`;
  }
}

const meta = {
  title: "Brand/Design Tokens",
  parameters: {
    controls: { disable: true },
    actions: { disable: true },
  },
  render: () => {
    const container = document.createElement("div");
    container.style.cssText = "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 960px;";

    const intro = document.createElement("p");
    intro.style.cssText = "color: #666; margin: 0 0 32px;";
    intro.textContent = "Overzicht van design tokens die niet onder Kleuren of Typografie vallen. Wanneer ROOS afwijkt van de standaard RVO-waarde wordt dit gemarkeerd.";
    container.appendChild(intro);

    // --- ROOS Afwijkingen ---
    container.appendChild(sectionHeading("ROOS Afwijkingen"));

    const overridesIntro = document.createElement("p");
    overridesIntro.style.cssText = "color: #666; font-size: 14px; margin: -8px 0 16px;";
    overridesIntro.textContent = "Bewuste afwijkingen van de standaard RVO-stijlen. Deze overrides worden door ROOS toegepast.";
    container.appendChild(overridesIntro);

    const overrides = [
      {
        component: "Globaal",
        property: "outline (focus-visible)",
        rvoValue: "browser default",
        roosValue: "2px solid var(--rvo-color-focus)",
        reason: "Consistente focus-stijl met 2px offset",
      },
      {
        component: "Globaal",
        property: "transition",
        rvoValue: "geen",
        roosValue: "all 0.2s ease",
        reason: "Subtiele animaties op ROOS-componenten",
      },
      {
        component: "Button",
        property: "text-decoration (hover)",
        rvoValue: "underline",
        roosValue: "none",
        reason: "Geen underline op hover voor betere visuele rust",
      },
      {
        component: "Card",
        property: "transform (hover)",
        rvoValue: "geen",
        roosValue: "translateY(-1px)",
        reason: "Subtiel lift-effect bij hover op klikbare cards",
      },
      {
        component: "Card",
        property: "transform (active)",
        rvoValue: "geen",
        roosValue: "scale(0.98)",
        reason: "Klik-feedback op interactieve cards",
      },
      {
        component: "Card",
        property: "border-color (hover)",
        rvoValue: "geen wijziging",
        roosValue: "var(--rvo-color-donkerblauw)",
        reason: "Visuele hover-indicatie op klikbare cards",
      },
    ];

    const overridesTable = tokenTable();
    const oHeader = document.createElement("tr");
    oHeader.style.borderBottom = "2px solid #ddd";
    oHeader.innerHTML =
      ["Component", "Property", "RVO standaard", "ROOS override", "Reden"].map(c =>
        `<th style="padding:8px 0;text-align:left;font-size:12px;font-weight:600;color:#888;text-transform:uppercase;letter-spacing:0.5px;">${c}</th>`
      ).join("");
    overridesTable.appendChild(oHeader);

    overrides.forEach(o => {
      const tr = document.createElement("tr");
      tr.style.borderBottom = "1px solid #eee";
      tr.innerHTML =
        `<td style="padding:12px 0;font-weight:600;font-size:14px;">${o.component}</td>` +
        `<td style="padding:12px 0;font-family:monospace;font-size:13px;color:#555;">${o.property}</td>` +
        `<td style="padding:12px 0;font-family:monospace;font-size:13px;color:#999;text-decoration:line-through;">${o.rvoValue}</td>` +
        `<td style="padding:12px 0;font-family:monospace;font-size:13px;color:#39870C;font-weight:600;">${o.roosValue}</td>` +
        `<td style="padding:12px 0;font-size:13px;color:#666;">${o.reason}</td>`;
      overridesTable.appendChild(tr);
    });
    container.appendChild(overridesTable);

    // --- Nieuwe componenten ---
    const newHeading = document.createElement("h3");
    newHeading.textContent = "Nieuwe componenten (niet in RVO)";
    newHeading.style.cssText = "font-size:16px;font-weight:600;margin:0 0 12px;";
    container.appendChild(newHeading);

    const newComponents = [
      { name: "Dialog", description: "Modal en drawer met sticky header/footer, maat-varianten (sm/md/lg/xl) en mobiele fullscreen", path: "componenten-dialog" },
      { name: "Search field", description: "Zoekveld met icoon en wisknop", path: "componenten-searchfield" },
      { name: "Card (avatar-variant)", description: "Card-uitbreiding met avatar, metadata en subheading", path: "componenten-card" },
    ];

    const newList = document.createElement("div");
    newList.style.cssText = "display:flex;flex-direction:column;gap:8px;margin-bottom:40px;";
    newComponents.forEach(c => {
      const link = document.createElement("a");
      link.href = "#";
      link.onclick = (e) => { e.preventDefault(); navigateTo(c.path); };
      link.style.cssText = "display:flex;align-items:baseline;gap:12px;padding:10px 12px;background:#F0F7EE;border-left:3px solid #39870C;border-radius:0 4px 4px 0;text-decoration:none;color:inherit;transition:background 0.15s ease;cursor:pointer;";
      link.onmouseover = () => link.style.background = "#E3F0DF";
      link.onmouseout = () => link.style.background = "#F0F7EE";
      link.innerHTML =
        `<strong style="font-size:14px;white-space:nowrap;">${c.name}</strong>` +
        `<span style="font-size:13px;color:#555;">${c.description}</span>` +
        `<span style="margin-left:auto;color:#39870C;font-size:13px;">&#8594;</span>`;
      newList.appendChild(link);
    });
    container.appendChild(newList);

    // --- Spacing ---
    container.appendChild(sectionHeading("Spacing"));

    const spacingTokens = [
      { name: "--rvo-space-3xs", value: "2px / 0.125rem" },
      { name: "--rvo-space-2xs", value: "4px / 0.25rem" },
      { name: "--rvo-space-xs", value: "8px / 0.5rem" },
      { name: "--rvo-space-sm", value: "12px / 0.75rem" },
      { name: "--rvo-space-md", value: "16px / 1rem" },
      { name: "--rvo-space-lg", value: "24px / 1.5rem" },
      { name: "--rvo-space-xl", value: "32px / 2rem" },
      { name: "--rvo-space-2xl", value: "40px / 2.5rem" },
      { name: "--rvo-space-3xl", value: "48px / 3rem" },
      { name: "--rvo-space-4xl", value: "64px / 4rem" },
    ];

    const spacingTable = tokenTable();
    spacingTable.appendChild(headerRow(["Token", "Waarde", "Preview"]));
    spacingTokens.forEach(t => {
      const pxVal = t.value.split(" / ")[0];
      const tr = document.createElement("tr");
      tr.style.borderBottom = "1px solid #eee";
      tr.innerHTML =
        `<td style="padding:12px 0;font-family:monospace;font-size:13px;color:#555;">${t.name}</td>` +
        `<td style="padding:12px 0;font-size:14px;">${t.value}</td>` +
        `<td style="padding:12px 0;"><div style="width:${pxVal};height:16px;background:#007BC7;border-radius:2px;"></div></td>`;
      spacingTable.appendChild(tr);
    });
    container.appendChild(spacingTable);

    // --- Sizes ---
    container.appendChild(sectionHeading("Sizes"));

    const sizeTokens = [
      { name: "--rvo-size-3xs", value: "16px / 1rem" },
      { name: "--rvo-size-2xs", value: "20px / 1.25rem" },
      { name: "--rvo-size-xs", value: "24px / 1.5rem" },
      { name: "--rvo-size-sm", value: "32px / 2rem" },
      { name: "--rvo-size-md", value: "40px / 2.5rem" },
      { name: "--rvo-size-lg", value: "48px / 3rem" },
      { name: "--rvo-size-xl", value: "56px / 3.5rem" },
      { name: "--rvo-size-2xl", value: "64px / 4rem" },
      { name: "--rvo-size-3xl", value: "80px / 5rem" },
      { name: "--rvo-size-4xl", value: "96px / 6rem" },
    ];

    const sizeTable = tokenTable();
    sizeTable.appendChild(headerRow(["Token", "Waarde", "Preview"]));
    sizeTokens.forEach(t => {
      const pxVal = t.value.split(" / ")[0];
      const tr = document.createElement("tr");
      tr.style.borderBottom = "1px solid #eee";
      tr.innerHTML =
        `<td style="padding:12px 0;font-family:monospace;font-size:13px;color:#555;">${t.name}</td>` +
        `<td style="padding:12px 0;font-size:14px;">${t.value}</td>` +
        `<td style="padding:12px 0;"><div style="width:${pxVal};height:16px;background:#154273;border-radius:2px;"></div></td>`;
      sizeTable.appendChild(tr);
    });
    container.appendChild(sizeTable);

    // --- Border radius ---
    container.appendChild(sectionHeading("Border radius"));

    const radiusTokens = [
      { name: "--rvo-border-radius-sm", value: "4px / 0.25rem" },
      { name: "--rvo-border-radius-md", value: "8px / 0.5rem" },
      { name: "--rvo-border-radius-lg", value: "16px / 1rem" },
      { name: "--rvo-border-radius-round", value: "50%" },
    ];

    const radiusTable = tokenTable();
    radiusTable.appendChild(headerRow(["Token", "Waarde", "Preview"]));
    radiusTokens.forEach(t => {
      const cssVal = t.value.includes("%") ? t.value : t.value.split(" / ")[0];
      const tr = document.createElement("tr");
      tr.style.borderBottom = "1px solid #eee";
      tr.innerHTML =
        `<td style="padding:12px 0;font-family:monospace;font-size:13px;color:#555;">${t.name}</td>` +
        `<td style="padding:12px 0;font-size:14px;">${t.value}</td>` +
        `<td style="padding:12px 0;"><div style="width:48px;height:48px;background:#E2E8F0;border:2px solid #94A3B8;border-radius:${cssVal};"></div></td>`;
      radiusTable.appendChild(tr);
    });
    container.appendChild(radiusTable);

    // --- Layout ---
    container.appendChild(sectionHeading("Layout"));

    const layoutTokens = [
      { name: "--rvo-layout-max-width", value: "1440px" },
      { name: "--rvo-layout-content-max-width", value: "960px" },
      { name: "--rvo-layout-sidebar-width", value: "300px" },
      { name: "--rvo-layout-sidebar-narrow-width", value: "240px" },
    ];

    const layoutTable = tokenTable();
    layoutTable.appendChild(headerRow(["Token", "Waarde"]));
    layoutTokens.forEach(t => {
      const tr = document.createElement("tr");
      tr.style.borderBottom = "1px solid #eee";
      tr.innerHTML =
        `<td style="padding:12px 0;font-family:monospace;font-size:13px;color:#555;">${t.name}</td>` +
        `<td style="padding:12px 0;font-size:14px;">${t.value}</td>`;
      layoutTable.appendChild(tr);
    });
    container.appendChild(layoutTable);

    // --- Component tokens ---
    container.appendChild(sectionHeading("Component tokens"));

    const componentNote = document.createElement("p");
    componentNote.style.cssText = "color: #666; font-size: 14px; margin: 0 0 16px;";
    componentNote.textContent = "Overzicht van de belangrijkste component-specifieke tokens. Zie de individuele component-pagina's voor het volledige overzicht.";
    container.appendChild(componentNote);

    const componentGroups = [
      {
        label: "Button",
        path: "componenten-button",
        tokens: [
          { name: "--rvo-button-primary-background-color", value: "var(--rvo-color-hemelblauw)" },
          { name: "--rvo-button-primary-color", value: "var(--rvo-color-wit)" },
          { name: "--rvo-button-padding-block", value: "var(--rvo-space-sm)" },
          { name: "--rvo-button-padding-inline", value: "var(--rvo-space-md)" },
          { name: "--rvo-button-border-radius", value: "var(--rvo-border-radius-sm)" },
        ],
      },
      {
        label: "Card",
        path: "componenten-card",
        tokens: [
          { name: "--rvo-card-background-color", value: "var(--rvo-color-wit)" },
          { name: "--rvo-card-border-color", value: "var(--rvo-color-grijs-200)" },
          { name: "--rvo-card-border-radius", value: "var(--rvo-border-radius-md)" },
          { name: "--rvo-card-padding", value: "var(--rvo-space-lg)" },
        ],
      },
      {
        label: "Alert",
        path: "componenten-alert",
        tokens: [
          { name: "--rvo-alert-padding", value: "var(--rvo-space-md)" },
          { name: "--rvo-alert-border-radius", value: "var(--rvo-border-radius-sm)" },
          { name: "--rvo-alert-info-border-color", value: "var(--rvo-color-hemelblauw)" },
          { name: "--rvo-alert-warning-border-color", value: "var(--rvo-color-donkergeel)" },
          { name: "--rvo-alert-error-border-color", value: "var(--rvo-color-rood)" },
          { name: "--rvo-alert-success-border-color", value: "var(--rvo-color-groen)" },
        ],
      },
      {
        label: "Input",
        path: "componenten-input",
        tokens: [
          { name: "--rvo-input-border-color", value: "var(--rvo-color-grijs-400)" },
          { name: "--rvo-input-border-radius", value: "var(--rvo-border-radius-sm)" },
          { name: "--rvo-input-padding-block", value: "var(--rvo-space-xs)" },
          { name: "--rvo-input-padding-inline", value: "var(--rvo-space-sm)" },
        ],
      },
    ];

    componentGroups.forEach(group => {
      const groupHeading = document.createElement("a");
      groupHeading.href = "#";
      groupHeading.onclick = (e) => { e.preventDefault(); navigateTo(group.path); };
      groupHeading.textContent = group.label + " →";
      groupHeading.style.cssText = "display:block;font-size:16px;font-weight:600;margin:24px 0 8px;color:#154273;text-decoration:none;cursor:pointer;";
      groupHeading.onmouseover = () => groupHeading.style.textDecoration = "underline";
      groupHeading.onmouseout = () => groupHeading.style.textDecoration = "none";
      container.appendChild(groupHeading);

      const table = tokenTable();
      table.appendChild(headerRow(["Token", "Standaard waarde"]));
      group.tokens.forEach(t => {
        const tr = document.createElement("tr");
        tr.style.borderBottom = "1px solid #eee";
        tr.innerHTML =
          `<td style="padding:10px 0;font-family:monospace;font-size:13px;color:#555;">${t.name}</td>` +
          `<td style="padding:10px 0;font-family:monospace;font-size:13px;color:#333;">${t.value}</td>`;
        table.appendChild(tr);
      });
      container.appendChild(table);
    });

    return container;
  },
};

function sectionHeading(text) {
  const h = document.createElement("h2");
  h.textContent = text;
  h.style.cssText = "font-size:20px;font-weight:600;margin:0 0 16px;padding-bottom:8px;border-bottom:1px solid #ddd;";
  return h;
}

function tokenTable() {
  const table = document.createElement("table");
  table.style.cssText = "width:100%;border-collapse:collapse;margin-bottom:40px;";
  return table;
}

function headerRow(cols) {
  const tr = document.createElement("tr");
  tr.style.borderBottom = "2px solid #ddd";
  tr.innerHTML = cols.map(c =>
    `<th style="padding:8px 0;text-align:left;font-size:12px;font-weight:600;color:#888;text-transform:uppercase;letter-spacing:0.5px;">${c}</th>`
  ).join("");
  return tr;
}

export default meta;

export const Default = {
  name: "Design Tokens",
};
