/**
 * PureBrain reskin for the AiCIV Skills Hub Swagger UI (/docs).
 *
 * Drop-in for skills-hub-proxy/worker.js. worker.js currently defines an inline
 * PASSTHROUGH stub `function reskinDocsHtml(html)` (see its bottom comment). To
 * integrate, devops deletes that stub and adds at the top of worker.js:
 *     import { reskinDocsHtml } from "./reskin.js";
 * This module therefore exports a NAMED `reskinDocsHtml` to match that call site
 * exactly (worker.js is an ES module: `export default { async fetch... }`).
 *
 * LOOK-ONLY cosmetic reskin. Given the full /docs HTML string, returns a rewritten
 * HTML string branded to the PureBrain dark theme. It:
 *   - splices Google Fonts (Oswald 600/700 + Inter 400/500/600) + a dark <style>
 *     override block before the first </head>;
 *   - statically relabels "AiCIV HUB" -> "PureBrain Skills Hub" (and "AiCIV" ->
 *     "PureBrain") in the shipped HTML (catches <title>);
 *   - splices a client <script> before the first </body> that (a) injects the real
 *     PureBrain hexagon logo (<img> from purebrain.ai) + an Oswald wordmark lockup
 *     into the topbar, and (b) re-runs the relabel after Swagger's CLIENT-SIDE render
 *     via a MutationObserver + a bounded setInterval polling fallback.
 *
 * Defensive: if `html` is not a string, or lacks </head> / </body> markers, the
 * original input is returned unchanged. Never throws.
 *
 * Author: ptt-full-stack-developer. Design notes:
 *   .claude/memory/agent-learnings/ptt-full-stack-developer/
 *   2026-07-03--swagger-ui-purebrain-reskin-worker-inject.md
 * Brand tokens: .claude/memory/brand/purebrain-visual-identity.md
 */

const FONTS_AND_STYLE = `
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style id="pb-skills-hub-theme">
  :root {
    --pb-bg: #080a12;
    --pb-panel: #0d1020;
    --pb-panel-2: #0f1424;
    --pb-line: #1c2333;
    --pb-text: #e6ecff;
    --pb-text-dim: #cdd6f4;
    --pb-cyan: #00BFFF;
    --pb-blue: #0080FF;
    --pb-orange: #FF8C00;
    --pb-orange-2: #FFA500;
  }

  html, body, .swagger-ui, .swagger-ui .wrapper {
    background: var(--pb-bg) !important;
    color: var(--pb-text) !important;
  }
  body { font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, sans-serif !important; }
  .swagger-ui, .swagger-ui .info, .swagger-ui p, .swagger-ui li, .swagger-ui table,
  .swagger-ui label, .swagger-ui .parameter__name, .swagger-ui .response-col_description,
  .swagger-ui .markdown, .swagger-ui .renderedMarkdown {
    color: var(--pb-text-dim) !important;
    font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, sans-serif !important;
  }

  /* ---- Headings / brand type ---- */
  .swagger-ui .info .title,
  .swagger-ui h1, .swagger-ui h2, .swagger-ui h3, .swagger-ui h4, .swagger-ui h5,
  .swagger-ui .opblock-tag {
    font-family: 'Oswald', 'Inter', sans-serif !important;
    font-weight: 700 !important;
    color: var(--pb-text) !important;
    letter-spacing: 0.3px;
  }
  .swagger-ui .info .title small { background: var(--pb-blue) !important; color: #fff !important; }
  .swagger-ui .info a, .swagger-ui a.nostyle, .swagger-ui a { color: var(--pb-cyan) !important; }

  /* ---- Topbar ---- */
  .swagger-ui .topbar {
    background: #05070d !important;
    border-bottom: 1px solid var(--pb-line) !important;
    box-shadow: 0 1px 0 rgba(0,191,255,0.15);
  }
  .swagger-ui .topbar .topbar-wrapper { align-items: center; }
  .swagger-ui .topbar-wrapper .link > svg,
  .swagger-ui .topbar-wrapper .link > img { display: none !important; }
  .swagger-ui .topbar-wrapper .link {
    display: inline-flex !important;
    align-items: center;
    gap: 12px;
    font-family: 'Oswald', sans-serif !important;
    font-weight: 700 !important;
    font-size: 20px !important;
    color: var(--pb-text) !important;
    text-decoration: none !important;
  }
  #pb-logo { display: inline-flex; align-items: center; gap: 10px; }
  #pb-logo img { display: block; height: 40px; width: 40px; }
  #pb-logo .pb-wordmark {
    font-family: 'Oswald', sans-serif !important;
    font-weight: 700 !important;
    font-size: 22px !important;
    letter-spacing: 0.5px;
    color: var(--pb-text) !important;
    line-height: 1;
  }
  .swagger-ui .topbar .download-url-wrapper .select-label span { color: var(--pb-text-dim) !important; }
  .swagger-ui .topbar .download-url-wrapper input[type=text] {
    background: var(--pb-panel) !important;
    color: var(--pb-text) !important;
    border: 1px solid var(--pb-line) !important;
  }
  .swagger-ui .topbar .download-url-wrapper .download-url-button {
    background: var(--pb-blue) !important;
    color: #fff !important;
    border: none !important;
  }

  /* ---- Scheme / servers / filter bar ---- */
  .swagger-ui .scheme-container {
    background: var(--pb-panel) !important;
    border: 1px solid var(--pb-line) !important;
    box-shadow: none !important;
  }
  .swagger-ui .servers > label select,
  .swagger-ui select {
    background: var(--pb-panel-2) !important;
    color: var(--pb-text) !important;
    border: 1px solid var(--pb-line) !important;
  }
  .swagger-ui .filter .operation-filter-input {
    background: var(--pb-panel-2) !important;
    color: var(--pb-text) !important;
    border: 1px solid var(--pb-line) !important;
  }

  /* ---- Operation blocks ---- */
  .swagger-ui .opblock {
    background: var(--pb-panel) !important;
    border: 1px solid var(--pb-line) !important;
    box-shadow: none !important;
  }
  .swagger-ui .opblock .opblock-summary {
    border-color: var(--pb-line) !important;
  }
  .swagger-ui .opblock .opblock-summary-path,
  .swagger-ui .opblock .opblock-summary-path__deprecated,
  .swagger-ui .opblock .opblock-summary-description {
    color: var(--pb-text) !important;
  }
  .swagger-ui .opblock-body,
  .swagger-ui .opblock-section-header {
    background: var(--pb-panel-2) !important;
  }
  .swagger-ui .opblock-section-header h4,
  .swagger-ui .opblock-section-header > label,
  .swagger-ui .opblock-section-header > label > span,
  .swagger-ui .opblock-description-wrapper p,
  .swagger-ui .opblock-title_normal p,
  .swagger-ui .tab li { color: var(--pb-text-dim) !important; }
  .swagger-ui .opblock-tag { border-bottom: 1px solid var(--pb-line) !important; }
  .swagger-ui .opblock-tag small { color: var(--pb-text-dim) !important; }

  /* keep method accent colors, just calm the fills */
  .swagger-ui .opblock.opblock-get .opblock-summary { background: rgba(0,128,255,0.06) !important; }
  .swagger-ui .opblock.opblock-post .opblock-summary { background: rgba(0,191,255,0.06) !important; }
  .swagger-ui .opblock.opblock-put .opblock-summary { background: rgba(255,140,0,0.06) !important; }
  .swagger-ui .opblock.opblock-delete .opblock-summary { background: rgba(255,80,80,0.06) !important; }

  /* ---- Tables / params / responses ---- */
  .swagger-ui table thead tr th,
  .swagger-ui table thead tr td {
    color: var(--pb-text) !important;
    border-bottom: 1px solid var(--pb-line) !important;
  }
  .swagger-ui table tbody tr td { border-color: var(--pb-line) !important; color: var(--pb-text-dim) !important; }
  .swagger-ui .parameter__name { color: var(--pb-text) !important; }
  .swagger-ui .parameter__type,
  .swagger-ui .parameter__in,
  .swagger-ui .prop-type { color: var(--pb-cyan) !important; }
  .swagger-ui .response-col_status { color: var(--pb-text) !important; }

  /* ---- Inputs (Try it out must stay legible) ---- */
  .swagger-ui input[type=text],
  .swagger-ui input[type=password],
  .swagger-ui input[type=search],
  .swagger-ui input[type=email],
  .swagger-ui input[type=number],
  .swagger-ui textarea,
  .swagger-ui .body-param__text {
    background: var(--pb-panel-2) !important;
    color: var(--pb-text) !important;
    border: 1px solid var(--pb-line) !important;
  }
  .swagger-ui input::placeholder, .swagger-ui textarea::placeholder { color: #7b8bb0 !important; }

  /* ---- Buttons ---- */
  .swagger-ui .btn { color: var(--pb-text) !important; border-color: var(--pb-line) !important; }
  .swagger-ui .btn.execute {
    background: var(--pb-blue) !important;
    border-color: var(--pb-blue) !important;
    color: #fff !important;
  }
  .swagger-ui .btn.try-out__btn,
  .swagger-ui .btn.authorize {
    background: transparent !important;
    border: 1px solid var(--pb-cyan) !important;
    color: var(--pb-cyan) !important;
  }
  .swagger-ui .btn.authorize svg { fill: var(--pb-cyan) !important; }
  .swagger-ui .btn.cancel { border-color: var(--pb-orange) !important; color: var(--pb-orange) !important; }

  /* ---- Code / highlight ---- */
  .swagger-ui .microlight,
  .swagger-ui .highlight-code,
  .swagger-ui .highlight-code > .microlight {
    background: #05070d !important;
    color: var(--pb-cyan) !important;
  }
  .swagger-ui .response-col_description__inner div.microlight { color: var(--pb-cyan) !important; }

  /* ---- Models ---- */
  .swagger-ui section.models {
    background: var(--pb-panel) !important;
    border: 1px solid var(--pb-line) !important;
  }
  .swagger-ui section.models h4,
  .swagger-ui section.models .model-container { color: var(--pb-text-dim) !important; }
  .swagger-ui .model-title,
  .swagger-ui .model .property-row .property { color: var(--pb-text) !important; }
  .swagger-ui .model .prop-name { color: var(--pb-text) !important; }
  .swagger-ui .model-toggle:after { filter: invert(1) brightness(1.6); }

  /* ---- Auth / Try-it modal (easy to miss) ---- */
  .swagger-ui .dialog-ux .modal-ux {
    background: var(--pb-panel) !important;
    border: 1px solid var(--pb-line) !important;
    color: var(--pb-text) !important;
  }
  .swagger-ui .dialog-ux .modal-ux-header h3,
  .swagger-ui .dialog-ux .modal-ux-content h4,
  .swagger-ui .dialog-ux .modal-ux-content p { color: var(--pb-text) !important; }
  .swagger-ui .dialog-ux .backdrop-ux { background: rgba(0,0,0,0.7) !important; }

  /* ---- Misc ---- */
  .swagger-ui .loading-container .loading:after { color: var(--pb-cyan) !important; }
  .swagger-ui svg.arrow { fill: var(--pb-text-dim) !important; }
  .swagger-ui .errors-wrapper { background: rgba(255,140,0,0.08) !important; border-color: var(--pb-orange) !important; }
</style>
`;

const RELABEL_SCRIPT = `
<script id="pb-skills-hub-relabel">
(function () {
  var OLD_FULL = "AiCIV HUB";
  var NEW_FULL = "PureBrain Skills Hub";
  var OLD_SHORT = "AiCIV";
  var NEW_SHORT = "PureBrain";

  // Real PureBrain hexagon logo (<img> on our own HTTPS domain) + Oswald wordmark lockup.
  var LOGO_SVG =
    '<span id="pb-logo">' +
    '<img src="https://purebrain.ai/purebrain-hexagon-logo.png" alt="PureBrain" ' +
    'width="40" height="40" ' +
    'style="display:block;height:40px;width:40px;" />' +
    '<span class="pb-wordmark" ' +
    'style="font-family:Oswald,sans-serif;font-weight:700;font-size:22px;' +
    'letter-spacing:0.5px;color:#e6ecff;line-height:1;">PureBrain</span>' +
    '</span>';

  function fix(str) {
    if (typeof str !== "string") return str;
    return str.split(OLD_FULL).join(NEW_FULL).split(OLD_SHORT).join(NEW_SHORT);
  }

  // Relabel visible TEXT NODES only, scoped to the title + topbar link. Skips inputs.
  function relabelIn(root) {
    if (!root) return;
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var n, batch = [];
    while ((n = walker.nextNode())) batch.push(n);
    for (var i = 0; i < batch.length; i++) {
      var node = batch[i];
      var p = node.parentNode;
      if (p) {
        var tag = p.nodeName;
        if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SCRIPT" || tag === "STYLE") continue;
        // never touch the version pill
        if (p.classList && p.classList.contains("version")) continue;
      }
      var v = node.nodeValue;
      var fixed = fix(v);
      if (fixed !== v) node.nodeValue = fixed;
    }
  }

  function injectLogo() {
    var wrap = document.querySelector(".swagger-ui .topbar-wrapper .link");
    if (wrap && !wrap.querySelector("#pb-logo")) {
      wrap.insertAdjacentHTML("afterbegin", LOGO_SVG);
    } else if (!wrap) {
      // Fallback banner if the topbar link never renders.
      var sw = document.querySelector(".swagger-ui");
      if (sw && !document.getElementById("pb-header")) {
        var hdr = document.createElement("div");
        hdr.id = "pb-header";
        hdr.style.cssText =
          "display:flex;align-items:center;gap:12px;padding:14px 18px;" +
          "background:#05070d;border-bottom:1px solid #1c2333;" +
          "font-family:Oswald,sans-serif;font-weight:700;font-size:20px;color:#e6ecff;";
        hdr.innerHTML = LOGO_SVG + "<span>" + NEW_FULL + "</span>";
        sw.insertBefore(hdr, sw.firstChild);
      }
    }
  }

  function relabel() {
    try {
      var title = document.querySelector(".swagger-ui .info .title");
      if (title) relabelIn(title);
      var link = document.querySelector(".swagger-ui .topbar-wrapper .link");
      if (link) relabelIn(link);
      if (typeof document.title === "string") {
        var dt = fix(document.title);
        if (dt !== document.title) document.title = dt;
      }
      injectLogo();
    } catch (e) { /* never break the page */ }
  }

  // Swagger renders .info .title client-side from openapi.json AFTER load, so a static
  // replace on the shipped HTML is not enough. Observe + poll.
  function start() {
    relabel();
    try {
      var obs = new MutationObserver(function () { relabel(); });
      obs.observe(document.documentElement, { childList: true, subtree: true, characterData: true });
    } catch (e) { /* observer unsupported -> polling still covers it */ }

    var ticks = 0;
    var timer = setInterval(function () {
      relabel();
      if (++ticks >= 40) clearInterval(timer); // ~10s bounded fallback
    }, 250);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
</script>
`;

/**
 * @param {string} html full /docs HTML from the FastAPI Swagger UI origin.
 * @returns {string} rewritten HTML (or the original, unchanged, if unsafe to rewrite).
 */
export function reskinDocsHtml(html) {
  // Defensive contract: only rewrite a real HTML document with both markers present.
  if (typeof html !== "string") return html;
  if (html.indexOf("</head>") === -1 || html.indexOf("</body>") === -1) return html;

  let out;
  try {
    // (a) Static relabel of the shipped HTML (catches <title>). Longest-match first.
    out = html.split("AiCIV HUB").join("PureBrain Skills Hub");
    out = out.split("AiCIV").join("PureBrain");

    // Splice fonts + theme <style> before the FIRST </head>.
    out = out.replace("</head>", FONTS_AND_STYLE + "</head>");

    // Splice the relabel/logo client script before the FIRST </body>.
    out = out.replace("</body>", RELABEL_SCRIPT + "</body>");
  } catch (_e) {
    return html; // never throw
  }

  return out;
}

export default reskinDocsHtml;
