# AI Partnership Guide Content Gate - v4.1.0

**Date**: 2026-02-23
**Type**: operational
**Agent**: full-stack-developer

## What Was Built

Partial content gate on `/ai-partnership-guide/` page at purebrain.ai.

**Gate Strategy**:
- Sections 1-3 (Why AI Fails, Memory Problem, What Partnership Looks Like) = FREE
- Sections 4-7 (Business Case, Readiness, Getting Started, FAQ) = GATED

Cutoff at section 4 is strategic: sections 1-3 establish the PROBLEM, sections 4-7 deliver the SOLUTION. Readers are invested after 3 sections and want the payoff.

## Technical Implementation

### Plugin File
`/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security/purebrain-security-plugin.php`
Version bumped from 4.0.1 → **4.1.0**

### New REST Endpoint
`POST /wp-json/purebrain/v1/guide-unlock`
- Server-side Brevo proxy (no API key exposed client-side)
- Accepts: `{ "email": "...", "first_name": "..." }` (first_name optional)
- Adds to Brevo list 3 (The Neural Feed) with FIRSTNAME attribute
- Rate limited: 5 req/IP/min
- Function: `purebrain_guide_unlock()` in plugin

### DOM Gating Strategy
JS finds all `h2` headings in `.entry-content` (or fallback selectors).
4th h2 = gate start. All elements from that point wrapped in `#pb-guide-gated-content`.
Gate area (fade overlay + email form) appended after the gated content wrapper.

### CSS Classes
- `#pb-guide-gated-content` - wrapper for sections 4-7 (blurred by default)
- `#pb-guide-gated-content.pb-guide-unlocked` - revealed state
- `#pb-guide-fade-overlay` - dark gradient over blurred preview
- `#pb-guide-gate-form-wrapper` - email form container
- `.pb-gate-submit` - orange (#f1420b) → blue (#2a93c1) hover

### LocalStorage Persist
Key: `pb_guide_unlocked = '1'`
Return visit: JS checks localStorage on init, auto-reveals without needing email re-entry.

### WordPress Page Detection
`is_page('ai-partnership-guide')` - uses page slug, not ID. Robust to ID changes.

## Deployment
Script: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v410_purebrain.py`

## Verification Results
- All 20 pre-flight validation checks passed
- Deployed via Playwright to GoDaddy Plugin Editor
- Page HTTP 200, 192336 bytes
- All 10 gate element checks passed on live page
- REST endpoint: HTTP 200 `{"success":true,"message":"unlocked"}`

## Patterns Learned

1. **`is_page()` with slug** is more robust than ID for page-specific hooks - slug won't change if page is cloned/migrated
2. **Content gating via DOM manipulation** (not PHP): WordPress page content is complex - better to let it render fully then use JS to restructure it. Avoids wpautop/Elementor conflicts.
3. **Gradient + blur combo**: `filter: blur(6px)` on content + dark gradient overlay above it creates a compelling "there's more here" visual without requiring complex PHP filtering
4. **`max-height: 320px + overflow: hidden`** constrains the blurred preview to a tasteful slice rather than showing the full blurred content
5. **Existing `purebrain_brevo_subscribe` function** was the template for `purebrain_guide_unlock` - nearly identical pattern with addition of FIRSTNAME attribute support
