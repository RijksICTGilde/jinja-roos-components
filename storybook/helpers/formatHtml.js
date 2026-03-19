const selfClosing = new Set(["c-icon", "c-status-icon"]);

export function formatHtml(source) {
  if (!source) return source;
  let formatted = "";
  let indent = 0;
  const tokens = source.replace(/>\s*</g, ">\n<").split("\n");
  for (const token of tokens) {
    const trimmed = token.trim();
    if (!trimmed) continue;
    if (/^<\//.test(trimmed)) indent--;
    formatted += "  ".repeat(Math.max(indent, 0)) + trimmed + "\n";
    if (/^<[^/]/.test(trimmed) && !/>.*<\//.test(trimmed) && !/\/>$/.test(trimmed)) {
      const tagMatch = trimmed.match(/^<([\w-]+)/);
      if (tagMatch && !selfClosing.has(tagMatch[1])) indent++;
    }
  }
  return formatted.trimEnd();
}
