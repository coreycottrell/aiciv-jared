# Password-Gated WordPress Page Deployment Pattern

**Date**: 2026-03-02
**Type**: deployment pattern
**Agent**: dept-systems-technology

---

## What Was Done

Deployed a self-contained HTML file as a password-gated WordPress page on purebrain.ai.

**Page**: PureBrain for Staycation Breaks
**URL**: https://purebrain.ai/purebrain-for-staycation-breaks/
**Page ID**: 1196
**Password**: StaycationAI2026 (shared with client)

---

## Deployment Pattern

### 1. Read HTML + Credentials
- HTML from: `exports/client-marketing/staycation-breaks/graham-martin-ai-blueprint.html`
- Credentials: `.env` -> `PUREBRAIN_WP_USER=Aether`, `PUREBRAIN_WP_APP_PASSWORD`
- Load with: `from dotenv import load_dotenv; load_dotenv('.env')`

### 2. Wrap in wp:html block
```python
wrapped_content = f"<!-- wp:html -->\n{raw_html}\n<!-- /wp:html -->"
```
Critical: wpautop filter destroys CSS/JS without this wrapper.

### 3. REST API Payload for Password-Gated Page
```python
payload = {
    "title": "Page Title",
    "slug": "page-slug",
    "content": wrapped_content,
    "status": "publish",
    "password": "ThePassword",  # THIS enables password protection
    "template": "",             # MUST be "" (default), NOT "elementor_canvas"
}
response = requests.post(
    "https://purebrain.ai/wp-json/wp/v2/pages",
    json=payload,
    auth=("Aether", WP_APP_PASSWORD),
    headers={"Content-Type": "application/json"},
    timeout=60
)
```

### 4. Verification
- HTTP 201 = created, HTTP 200 = updated
- Confirm with: `curl -s URL | grep -E "post-password-required|protected"`
- Yoast og:description will show: "There is no excerpt because this is a protected post."

---

## Key Learnings

- `"password": "value"` in the REST API payload is the correct way to set WordPress password protection
- `"template": ""` is critical — elementor_canvas strips all theme styling
- For client deliverables, file deployment result JSON to: `exports/client-marketing/[client]/deployment-result.json`
- Self-contained HTML (61KB) deploys cleanly via REST API with no external dependency issues
- Password-protected pages return HTTP 200 to unauthenticated visitors (they see the password form, not 403/401)

---

## Files
- HTML source: `/home/jared/projects/AI-CIV/aether/exports/client-marketing/staycation-breaks/graham-martin-ai-blueprint.html`
- Deploy script: `/home/jared/projects/AI-CIV/aether/tools/deploy_staycation_page.py`
- Result: `/home/jared/projects/AI-CIV/aether/exports/client-marketing/staycation-breaks/deployment-result.json`
