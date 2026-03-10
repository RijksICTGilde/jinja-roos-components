const API_BASE = "http://localhost:8100";

export async function renderComponent(component, attrs = {}, content = "") {
  let res;
  try {
    res = await fetch(`${API_BASE}/api/render`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ component, attrs, content }),
    });
  } catch (err) {
    return {
      html: `<div style="padding:1rem;border:2px solid red;border-radius:4px;font-family:sans-serif">
        <strong>Render API niet bereikbaar</strong>
        <p>Start de API met: <code>uvicorn storybook.render_api:app --port 8100</code></p>
        <p style="color:#666;font-size:0.85em">Fout: ${err.message}</p>
      </div>`,
      source: "",
    };
  }

  if (!res.ok) {
    const text = await res.text();
    return {
      html: `<pre style="color:red">Render error (${res.status}): ${text}</pre>`,
      source: "",
    };
  }

  const data = await res.json();
  return { html: data.html, source: data.source || "" };
}
