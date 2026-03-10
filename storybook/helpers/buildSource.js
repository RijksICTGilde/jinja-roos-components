/**
 * Build a Jinja2 component source string from args.
 * Used by Storybook's docs.source.transform to show dynamic code.
 */
export function buildSource(componentName, args = {}) {
  let attrsStr = "";
  const content = args.content || "";

  for (const [key, value] of Object.entries(args)) {
    if (key === "content") continue;
    if (
      value === false ||
      value === "" ||
      value === null ||
      value === undefined
    )
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
