# Why PureBrain Comparison Page Link Deployment

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: operational + teaching
**Topic**: Adding "Why PureBrain Is Different" link to multiple pages on purebrain.ai

---

## Task

Add a link to https://purebrain.ai/why-purebrain/ (the comparison/differentiation page, Page ID 794)
on multiple pages of purebrain.ai.

Target pages:
- Homepage (Page ID: 11, Elementor-based)
- pay-test (Page ID: 439)
- pay-test-2 (Page ID: 689)
- pay-test-sandbox (Page ID: 468)
- pay-test-sandbox-2 (Page ID: 688)

---

## What Was Done

### 1. Pay-Test Pages (439, 689, 468, 688) — SUCCESS via REST API

**Method**: Direct WP REST API content update (`POST /wp-json/wp/v2/pages/{id}`)

Pay-test pages store complete standalone HTML documents (including `<html>`, `<head>`, `<body>` tags).
They have a `<!-- END PAY-TEST SCRIPTS -->` marker before `</body></html>`.

Injection point: Before `<!-- END PAY-TEST SCRIPTS -->`

Injected HTML:
```html
<!-- WHY PUREBRAIN LINK (v4.6.0) -->
<style id="pb-why-purebrain-paytest-v460">
#pb-why-purebrain-paytest-link {
    text-align: center;
    padding: 16px 0 8px 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 13px;
}
#pb-why-purebrain-paytest-link a {
    color: #2a93c1;
    text-decoration: none;
    font-weight: 600;
    letter-spacing: 0.02em;
    transition: color 0.15s ease;
}
#pb-why-purebrain-paytest-link a:hover {
    color: #f1420b;
}
</style>
<div id="pb-why-purebrain-paytest-link">
    <a href="https://purebrain.ai/why-purebrain/" rel="noopener">See Why PureBrain Is Different &rarr;</a>
</div>
```

All 4 pages confirmed updated in WordPress database (verified via REST API `context=edit`).

**CDN note**: Cloudflare CDN serves cached HTML (CF-Cache-Status: HIT, max-age=31 days).
Live pages appear unchanged until CDN cache expires naturally or Jared purges in Cloudflare dashboard.
The WordPress database has the updated content — cache bust is the only remaining step.

### 2. Homepage (Page ID: 11) — SUCCESS via Elementor REST API

**Method**: Update `_elementor_data` meta via `POST /wp-json/wp/v2/pages/11`

The homepage uses Elementor. The safest approach is to add a new Elementor section, NOT
modify the existing Elementor HTML (risky and complex).

**What was added**: A new Elementor section containing a text-editor widget with the link,
inserted just before the `aether_footer_11` section (the last section).

```json
{
  "id": "why_purebrain_hp",
  "elType": "section",
  "settings": {
    "padding": {"unit":"px","top":"16","right":"0","bottom":"16","left":"0","isLinked":false},
    "background_background": "classic",
    "background_color": "#0d1117"
  },
  "elements": [{
    "id": "why_purebrain_hp_col",
    "elType": "column",
    "settings": {"_column_size": 100, "_inline_size": null},
    "elements": [{
      "id": "why_purebrain_hp_txt",
      "elType": "widget",
      "widgetType": "text-editor",
      "settings": {
        "editor": "<p style=\"text-align:center;font-size:13px;margin:0;padding:0;\"><a href=\"https://purebrain.ai/why-purebrain/\" style=\"color:#2a93c1;text-decoration:none;font-weight:600;letter-spacing:0.03em;\">See Why PureBrain Is Different &rarr;</a></p>"
      }
    }]
  }]
}
```

Elementor cache cleared after update (DELETE /wp-json/elementor/v1/cache).
Homepage cache busted (POST /wp-json/wp/v2/pages/11 with status:publish).

**VERIFIED LIVE**: `curl https://purebrain.ai/?nocache=1` shows `href="https://purebrain.ai/why-purebrain/"` — CONFIRMED working.

---

## Plugin v4.6.0 (Prepared but NOT Deployed)

The plugin v4.6.0 adds:
1. "Why Choose PureBrain?" link in the Aether footer credit bar (ALL pages site-wide)
2. Homepage "See Why PureBrain Is Different →" bar above footer (homepage only, priority 99)

Plugin file updated at: `tools/security/purebrain-security/purebrain-security-plugin.php`
Export copy: `exports/purebrain-security-plugin-v460.php`

**WHY NOT DEPLOYED**: The WordPress admin password (`PUREBRAIN_WP_PASSWORD` in .env) has changed.
Playwright login fails with "Invalid credentials." The REST API app password still works.

**To deploy plugin v4.6.0**:
1. Jared needs to update `PUREBRAIN_WP_PASSWORD` in `.env` with the current WP admin password
2. Then run: `python3 tools/security/deploy_plugin_v460_purebrain.py`

**Alternative manual deploy**:
- Download `exports/purebrain-security-plugin-v460.php`
- In WP Admin > Plugins > Editor > PureBrain Security Plugin
- Copy/paste the file content and save

---

## Key Patterns Learned

### Pay-Test Pages Are Full HTML Documents
Unlike normal WordPress pages, the pay-test pages store complete `<!DOCTYPE html>` documents
in their `content.raw`. The `<!-- END PAY-TEST SCRIPTS -->` marker is the safe injection point
for new content before `</body></html>`.

### Elementor Data Update (Safe Homepage Approach)
Per the CRITICAL task instruction: "Do NOT modify any og:image, twitter:image, or meta tags.
Do NOT touch any GIF references. Only add a text link near the footer."
Adding an Elementor section via REST API meta update is the safest approach:
- No Elementor JSON parsing/modification complexity
- No risk of breaking existing sections
- Uses a simple text-editor widget (minimal widget type)
- Idempotency check: look for `why_purebrain_hp` in serialized elements before inserting

### CDN Cache Reality
Cloudflare CDN caches pages with 31-day max-age. After REST API updates:
- Content IS stored in WordPress database (verified via `context=edit`)
- CDN serves stale HTML until cache expires naturally or is manually purged
- Cloudflare dashboard: Caching → Purge Everything (requires manual login)
- We do NOT have Cloudflare API credentials in .env

---

## Verification Status

| Page | DB Updated | Live (CDN bypassed) | Status |
|------|-----------|---------------------|--------|
| Homepage (11) | YES | YES (verified) | LIVE |
| pay-test (439) | YES | Waiting CDN expire | DB OK |
| pay-test-2 (689) | YES | Waiting CDN expire | DB OK |
| pay-test-sandbox (468) | YES | Waiting CDN expire | DB OK |
| pay-test-sandbox-2 (688) | YES | Waiting CDN expire | DB OK |

---

## Files

- Deploy script: `tools/security/deploy_plugin_v460_purebrain.py`
- Plugin v4.6.0: `tools/security/purebrain-security/purebrain-security-plugin.php`
- Plugin export: `exports/purebrain-security-plugin-v460.php`
