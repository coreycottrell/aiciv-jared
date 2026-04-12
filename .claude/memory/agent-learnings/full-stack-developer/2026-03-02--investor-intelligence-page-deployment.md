# Investor Intelligence Page Deployment
**Date**: 2026-03-02
**Type**: operational
**Topic**: WordPress deployment of self-contained 74KB interactive investor page

## What Was Deployed
- Source: `/home/jared/projects/AI-CIV/aether/exports/purebrain-investor-intelligence.html`
- WordPress page ID: 1205
- Live URL: https://purebrain.ai/investor-intelligence/
- Template: elementor_canvas (full-width, no theme header/footer)
- Status: publish

## Deployment Method
Used Python `requests` library instead of curl to avoid shell JSON escaping issues with 73KB content.
Script: `/home/jared/projects/AI-CIV/aether/tools/deploy_investor_intelligence.py`

## Key Decisions
- `elementor_canvas` template used (not default) — page is fully self-contained with its own nav/footer
- Wrapped entire HTML in `<!-- wp:html -->` block per WP HTML DEPLOYMENT RULE
- WP REST API slug check returned 0 existing pages → created new (POST /wp/v2/pages)
- 201 response = success

## Verification
- `curl` HTTP check: 200 OK, 192KB response
- Telegram notification delivered (message_id: 15881)

## Pattern for Large HTML Deployments
When HTML > 10KB: use Python requests library, not curl. Avoids:
- Shell quoting issues with single/double quotes inside HTML
- Command line length limits
- JSON string escaping complexity with inline JS/CSS
