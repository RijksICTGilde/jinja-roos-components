const meta = {
  title: "Brand/Typografie",
  parameters: {
    controls: { disable: true },
    actions: { disable: true },
  },
  render: () => {
    const container = document.createElement("div");
    container.style.cssText = "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 960px;";

    const intro = document.createElement("p");
    intro.style.cssText = "color: #666; margin: 0 0 32px;";
    intro.textContent = "Overzicht van de typografie design tokens. De huisstijl gebruikt lettertypen die beschikbaar zijn binnen de Rijkshuisstijl.";
    container.appendChild(intro);

    // --- Family ---
    container.appendChild(sectionHeading("Family"));

    const families = [
      { name: "'RijksoverheidSansWebText'", variable: "--rvo-font-sans-serif-font-family", fallback: { label: "'Verdana'", variable: "--rvo-font-sans-serif-fallback-font-family" } },
      { name: "'RijksoverheidSerifWeb'", variable: "--rvo-font-serif-font-family", fallback: { label: "'Times New Roman'", variable: "--rvo-font-serif-fallback-font-family" } },
    ];

    const familyTable = document.createElement("table");
    familyTable.style.cssText = "width:100%;border-collapse:collapse;margin-bottom:40px;";
    families.forEach(f => {
      familyTable.appendChild(fontRow(f.name, `var(${f.variable})`, f.name.replace(/'/g, "")));
      const fbRow = document.createElement("tr");
      fbRow.innerHTML = `<td style="padding:8px 0;color:#666;font-size:14px;">Fallback:<br>${f.fallback.label}</td><td style="padding:8px 0;font-family:monospace;font-size:13px;color:#555;text-align:right;">var(${f.fallback.variable})</td>`;
      familyTable.appendChild(fbRow);
    });
    container.appendChild(familyTable);

    // --- Weight ---
    container.appendChild(sectionHeading("Weight"));

    const weights = [
      { value: "400", variable: "--rvo-font-weight-normal" },
      { value: "550", variable: "--rvo-font-weight-semibold" },
      { value: "700", variable: "--rvo-font-weight-bold" },
      { value: "800", variable: "--rvo-font-weight-extrabold" },
    ];

    const weightTable = document.createElement("table");
    weightTable.style.cssText = "width:100%;border-collapse:collapse;margin-bottom:40px;";
    weights.forEach(w => {
      const tr = document.createElement("tr");
      tr.style.borderBottom = "1px solid #eee";
      tr.innerHTML = `<td style="padding:12px 0;font-weight:${w.value};font-size:16px;width:80px;">${w.value}</td><td style="padding:12px 0;font-family:monospace;font-size:13px;color:#555;">var(${w.variable})</td>`;
      weightTable.appendChild(tr);
    });
    container.appendChild(weightTable);

    // --- Line-height ---
    container.appendChild(sectionHeading("Line-height"));

    const lineHeights = [
      { value: "125%", variable: "--rvo-line-height-sm" },
      { value: "150%", variable: "--rvo-line-height-md" },
      { value: "175%", variable: "--rvo-line-height-lg" },
    ];

    const lhTable = document.createElement("table");
    lhTable.style.cssText = "width:100%;border-collapse:collapse;margin-bottom:40px;";
    lineHeights.forEach(lh => {
      const tr = document.createElement("tr");
      tr.style.borderBottom = "1px solid #eee";
      tr.innerHTML = `<td style="padding:12px 0;"><strong style="font-size:14px;">${lh.value}</strong><div style="line-height:${lh.value};font-size:14px;color:#555;margin-top:4px;max-width:500px;">De Nederlandse overheid zet zich in voor een goed leven in Nederland. Samen werken we aan een land waar iedereen kan meedoen.</div></td><td style="padding:12px 0;font-family:monospace;font-size:13px;color:#555;vertical-align:top;white-space:nowrap;">var(${lh.variable})</td>`;
      lhTable.appendChild(tr);
    });
    container.appendChild(lhTable);

    // --- Size ---
    container.appendChild(sectionHeading("Size"));

    const sizes = [
      { label: "2xs", px: "10px / 0.625rem", variable: "--rvo-font-size-2xs" },
      { label: "xs", px: "12px / 0.75rem", variable: "--rvo-font-size-xs" },
      { label: "sm", px: "14px / 0.875rem", variable: "--rvo-font-size-sm" },
      { label: "md", px: "16px / 1rem", variable: "--rvo-font-size-md" },
      { label: "lg", px: "18px / 1.125rem", variable: "--rvo-font-size-lg" },
      { label: "xl", px: "20px / 1.25rem", variable: "--rvo-font-size-xl" },
      { label: "2xl", px: "24px / 1.5rem", variable: "--rvo-font-size-2xl" },
      { label: "3xl", px: "32px / 2rem", variable: "--rvo-font-size-3xl" },
      { label: "4xl", px: "48px / 3rem", variable: "--rvo-font-size-4xl" },
    ];

    const sizeTable = document.createElement("table");
    sizeTable.style.cssText = "width:100%;border-collapse:collapse;margin-bottom:40px;";
    sizes.forEach(s => {
      const tr = document.createElement("tr");
      tr.style.borderBottom = "1px solid #eee";
      tr.innerHTML = `<td style="padding:12px 0;width:60px;"><strong>${s.label}</strong><br><span style="font-size:12px;color:#888;">${s.px}</span></td><td style="padding:12px 0;font-size:var(${s.variable});color:#333;">De Nederlandse overheid</td><td style="padding:12px 0;font-family:monospace;font-size:13px;color:#555;text-align:right;white-space:nowrap;">var(${s.variable})</td>`;
      sizeTable.appendChild(tr);
    });
    container.appendChild(sizeTable);

    // --- Headings preview ---
    container.appendChild(sectionHeading("Headings"));

    for (let i = 1; i <= 6; i++) {
      const row = document.createElement("div");
      row.style.cssText = "display:flex;align-items:baseline;gap:16px;padding:8px 0;border-bottom:1px solid #eee;";

      const heading = document.createElement("h" + i);
      heading.className = "utrecht-heading-" + i;
      heading.textContent = "Heading " + i;
      heading.style.margin = "0";
      heading.style.flex = "1";

      const varLabel = document.createElement("span");
      varLabel.style.cssText = "font-family:monospace;font-size:13px;color:#555;white-space:nowrap;";
      varLabel.textContent = "utrecht-heading-" + i;

      row.appendChild(heading);
      row.appendChild(varLabel);
      container.appendChild(row);
    }

    const spacer = document.createElement("div");
    spacer.style.marginBottom = "40px";
    container.appendChild(spacer);

    // --- Paragraph preview ---
    container.appendChild(sectionHeading("Paragraph"));

    const paragraphSizes = [
      { label: "Lead", size: "var(--rvo-font-size-lg)", desc: "rvo-paragraph-lg" },
      { label: "Default", size: "var(--rvo-font-size-md)", desc: "rvo-paragraph-md" },
      { label: "Small", size: "var(--rvo-font-size-sm)", desc: "rvo-paragraph-sm" },
    ];

    paragraphSizes.forEach(ps => {
      const row = document.createElement("div");
      row.style.cssText = "display:flex;align-items:baseline;gap:16px;padding:12px 0;border-bottom:1px solid #eee;";

      const left = document.createElement("div");
      left.style.cssText = "flex:1;";

      const labelEl = document.createElement("strong");
      labelEl.textContent = ps.label;
      labelEl.style.cssText = "font-size:14px;display:block;margin-bottom:4px;";
      left.appendChild(labelEl);

      const p = document.createElement("p");
      p.textContent = "De Nederlandse overheid zet zich in voor een goed leven in Nederland.";
      p.style.cssText = "margin:0;font-size:" + ps.size + ";";
      left.appendChild(p);

      const varLabel = document.createElement("span");
      varLabel.style.cssText = "font-family:monospace;font-size:13px;color:#555;white-space:nowrap;";
      varLabel.textContent = ps.desc;

      row.appendChild(left);
      row.appendChild(varLabel);
      container.appendChild(row);
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

function fontRow(name, varText, fontFamily) {
  const tr = document.createElement("tr");
  tr.style.borderBottom = "1px solid #eee";
  tr.innerHTML = `<td style="padding:12px 0;font-family:${fontFamily}, sans-serif;font-size:18px;">${name}</td><td style="padding:12px 0;font-family:monospace;font-size:13px;color:#555;text-align:right;">var(${varText.replace("var(", "").replace(")", "")})</td>`;
  return tr;
}

export default meta;

export const Default = {
  name: "Typografie",
};
