const colors = {
  "Hemelblauw": {
    "hemelblauw": "#007BC7",
    "hemelblauw-150": "#D9EBF7",
    "hemelblauw-300": "#B3D7EE",
    "hemelblauw-450": "#8CC4E6",
    "hemelblauw-600": "#66B0DD",
    "hemelblauw-750": "#409CD5",
  },
  "Logoblauw": {
    "logoblauw": "#154273",
    "logoblauw-150": "#DCE3EA",
    "logoblauw-300": "#B9C7D5",
    "logoblauw-450": "#95AAC0",
    "logoblauw-600": "#738EAB",
    "logoblauw-750": "#507196",
  },
  "Lichtblauw": {
    "lichtblauw": "#8FCAE7",
    "lichtblauw-150": "#EEF7FC",
    "lichtblauw-300": "#DEF0F8",
    "lichtblauw-450": "#CCE7F4",
    "lichtblauw-600": "#BCDFF1",
    "lichtblauw-750": "#ABD7ED",
  },
  "Donkerblauw": {
    "donkerblauw": "#01689B",
    "donkerblauw-150": "#D9E9F0",
    "donkerblauw-300": "#B3D2E1",
    "donkerblauw-450": "#8CBBD2",
    "donkerblauw-600": "#67A4C3",
    "donkerblauw-750": "#418EB4",
  },
  "Groen": {
    "groen": "#39870C",
    "groen-150": "#E2EDDB",
    "groen-300": "#C4DBB7",
    "groen-450": "#A6C991",
    "groen-600": "#88B76D",
    "groen-750": "#6BA549",
  },
  "Oranje": {
    "oranje": "#E17000",
    "oranje-150": "#FBEAD9",
    "oranje-300": "#F6D4B3",
    "oranje-450": "#F1BF8C",
    "oranje-600": "#EDA966",
    "oranje-750": "#E89440",
  },
  "Donkergeel": {
    "donkergeel": "#FFB612",
    "donkergeel-150": "#FFF4DB",
    "donkergeel-300": "#FFE9B8",
    "donkergeel-450": "#FFDE94",
    "donkergeel-600": "#FFD371",
    "donkergeel-750": "#FFC84D",
  },
  "Rood": {
    "rood": "#D51B1E",
    "rood-150": "#F9DFDD",
    "rood-300": "#F3C0BC",
    "rood-450": "#EC9F99",
    "rood-600": "#E68078",
    "rood-750": "#E06056",
  },
  "Grijs": {
    "grijs-050": "#F8FAFC",
    "grijs-100": "#F1F5F9",
    "grijs-200": "#E2E8F0",
    "grijs-300": "#CBD5E1",
    "grijs-400": "#94A3B8",
    "grijs-500": "#64748B",
    "grijs-600": "#475569",
    "grijs-700": "#334155",
    "grijs-800": "#1E293B",
    "grijs-900": "#0F172A",
  },
  "Zwart & Wit": {
    "zwart": "#000000",
    "wit": "#FFFFFF",
  },
};

function isLight(hex) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return (r * 299 + g * 587 + b * 114) / 1000 > 150;
}

const meta = {
  title: "Brand/Kleuren",
  parameters: {
    controls: { disable: true },
    actions: { disable: true },
  },
  render: () => {
    const container = document.createElement("div");
    container.style.cssText = "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 960px;";

    for (const [groupName, groupColors] of Object.entries(colors)) {
      const section = document.createElement("div");
      section.style.cssText = "margin-bottom: 32px;";

      const title = document.createElement("h3");
      title.textContent = groupName;
      title.style.cssText = "margin: 0 0 12px 0; font-size: 16px; font-weight: 600;";
      section.appendChild(title);

      const grid = document.createElement("div");
      grid.style.cssText = "display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px;";

      for (const [name, hex] of Object.entries(groupColors)) {
        const card = document.createElement("div");
        card.style.cssText = "border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;";

        const swatch = document.createElement("div");
        swatch.style.cssText = `background: ${hex}; height: 72px; display: flex; align-items: center; justify-content: center;`;

        const hexLabel = document.createElement("span");
        hexLabel.textContent = hex;
        hexLabel.style.cssText = `font-size: 12px; font-weight: 500; color: ${isLight(hex) ? "#333" : "#fff"};`;
        swatch.appendChild(hexLabel);

        const info = document.createElement("div");
        info.style.cssText = "padding: 8px 10px;";

        const nameEl = document.createElement("div");
        nameEl.textContent = name;
        nameEl.style.cssText = "font-size: 13px; font-weight: 500; color: #333;";

        const varEl = document.createElement("div");
        varEl.textContent = `--rvo-color-${name}`;
        varEl.style.cssText = "font-size: 11px; color: #888; margin-top: 2px; font-family: monospace;";

        info.appendChild(nameEl);
        info.appendChild(varEl);
        card.appendChild(swatch);
        card.appendChild(info);
        grid.appendChild(card);
      }

      section.appendChild(grid);
      container.appendChild(section);
    }

    return container;
  },
};

export default meta;

export const Default = {
  name: "Kleuren",
};
