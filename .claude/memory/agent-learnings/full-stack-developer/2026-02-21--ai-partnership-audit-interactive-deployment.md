# AI Partnership Audit: Interactive Form Build + WordPress Fix

**Date**: 2026-02-21
**Type**: teaching
**Topic**: Built interactive scoring form, fixed WordPress styling with CSS scoping, deployed to both sites

---

## What Was Built

### Task 1: Fix (superseded by Task 2)
The static page was unstyled on WordPress because theme CSS overrode our custom styles.
Root cause: CSS variables in `:root` and unscoped selectors don't survive WordPress theme injection.

**Fix approach used**: Scope ALL CSS under `#pb-audit-page` wrapper + `html, body { ... !important }` for background/color.
This means every CSS rule is: `#pb-audit-page .some-class { ... }` instead of `.some-class { ... }`.
This gives sufficient specificity to win over theme styles without needing `!important` on every rule.

### Task 2: Interactive Form Version
Built `exports/ai-partnership-audit-interactive.html` — fully self-contained HTML with:
- Same dark theme visual design as static version
- Clickable 1-5 radio buttons (styled as circular score bubbles, not native radio inputs)
- Live score calculation + progress bar (sticky banner, updates on every click)
- Score tier label updates live as user answers
- Lead capture form (name, email, company optional)
- On submit: POST to Brevo API → List 9, attributes ASSESSMENT_SCORE, ASSESSMENT_TIER, LEAD_SCORE+30, FIRSTNAME
- Results section appears after submit with personalized tier analysis
- Graceful degradation: shows results even if Brevo call fails

---

## Key Patterns

### CSS Scoping for WordPress
```css
/* Global overrides need !important */
html, body { background-color: #080a12 !important; color: #e0e6f0 !important; }

/* Everything else scoped under wrapper - no !important needed */
#pb-audit-page { --blue: #2a93c1; ... }
#pb-audit-page .page { background: var(--bg-card); ... }
```
This pattern works because `#pb-audit-page .page` has higher specificity than `.page` alone.

### Hide WP Theme Header/Footer
```css
.site-header, .site-footer, .entry-header, .entry-footer,
.wp-block-post-title, h1.entry-title { display: none !important; }
```

### Radio Button Styling (custom score bubbles)
```css
input[type="radio"] { display: none; }
input[type="radio"]:checked + label { background: ...; transform: scale(1.12); }
label:hover { transform: scale(1.1); }
```

### Dynamic Question Generation (JS)
Questions defined as data array, rendered via JavaScript to avoid massive HTML duplication.
Keeps file manageable and easier to update.

### Brevo API (client-side, CORS works)
```js
var payload = {
  email: em,
  attributes: { FIRSTNAME: fn, ASSESSMENT_SCORE: score, ASSESSMENT_TIER: '...', LEAD_SCORE: 30 },
  listIds: [9],
  updateEnabled: true
};
xhr.setRequestHeader('api-key', BREVO_API_KEY);
// POST to https://api.brevo.com/v3/contacts
```
List 9 = Assessment Completions (created this session).

---

## Deployment Details

- purebrain.ai: Page ID 620, template = elementor_canvas, URL = https://purebrain.ai/ai-partnership-audit/
- jareddsanborn.com: Page ID 1116, template = page-template-blank.php, URL = https://jareddsanborn.com/ai-partnership-audit/
- Elementor cache cleared after purebrain.ai deploy
- Both verified HTTP 200 with all key features present

### REST API requires User-Agent
```python
headers = {
    'Authorization': f'Basic {auth}',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}
```
Without User-Agent, Cloudflare WAF returns 403 error code 1010.

---

## Tier Score Ranges (updated from static version)
- 10-24: AI Beginner
- 25-37: AI User
- 38-46: AI Explorer
- 47-50: AI Partner

---

## Files
- `/home/jared/projects/AI-CIV/aether/exports/ai-partnership-audit-interactive.html` - source
