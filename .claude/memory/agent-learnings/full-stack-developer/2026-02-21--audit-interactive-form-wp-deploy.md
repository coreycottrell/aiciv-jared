# AI Partnership Audit — Interactive Form WordPress Deployment
**Date**: 2026-02-21
**Type**: teaching
**Topic**: Building WP-survivable interactive form with Brevo lead capture from scoped CSS

## What Was Built
- Full interactive 10-question scoring form replacing the static lead magnet HTML
- Self-contained single HTML file: `exports/ai-partnership-audit-interactive.html`
- Deployed to both WordPress sites (same page IDs as static version)

## WordPress CSS Survival Strategy (KEY PATTERNS)

### 1. Scope everything under a unique ID wrapper
```css
/* ALL styles under #pb-audit-page — zero global leakage */
#pb-audit-page .pb-card { ... }
#pb-audit-page .pb-header { ... }
```

### 2. CSS variables on the wrapper, NOT :root
```css
/* WRONG - WordPress may override :root */
:root { --pb-blue: #2a93c1; }

/* RIGHT - scoped to our wrapper */
#pb-audit-page {
  --pb-blue: #2a93c1;
}
```

### 3. !important on ALL properties inside the wrapper
Every CSS declaration inside `#pb-audit-page` uses `!important`. This defeats:
- WordPress Twenty-Twenty+ base styles
- Elementor base styles
- Theme-specific overrides

### 4. Kill WordPress body/page background at top of `<style>`
```css
body, body.page, body.single, body.home, html {
  background-color: #0a0a14 !important;
}
#page, .site, .site-content, #content, .entry-content { background: transparent !important; }
.entry-header, header.entry-header { display: none !important; }
```
This goes OUTSIDE the #pb-audit-page scope so it targets WP structure elements.

### 5. Radio button technique for score bubbles
Radio inputs are hidden (opacity:0, position:absolute), labels are styled as bubbles.
The `:checked + label` selector drives the selected-state glow effect:
```css
#pb-audit-page input[type="radio"].pb-radio:checked + .pb-bubble-label {
  background: linear-gradient(...) !important;
  box-shadow: 0 0 12px var(--pb-blue-glow) !important;
}
```
This works in all browsers without JS needing to manage selected state.

## Interactive Features Built
- Real-time score tracking as user clicks bubbles
- Progress bar (questions answered / 10)
- Live score counter (X/50)
- Answered rows get subtle blue tint + filled number circle
- Auto-show results after all 10 answered (smooth scroll)
- Animated score bar that fills on reveal
- 4 scoring tiers with unique colors, descriptions, recommendations
- Lead capture form (name, email, company optional)
- Brevo API v3 integration — adds to List 9, List 10 if score >= 38
- Duplicate contact handling (PUT /contacts/{email} on 400 duplicate)
- Success state with CTA button → https://purebrain.ai/#awakening

## Brevo Integration Pattern
```javascript
// Create contact
fetch('https://api.brevo.com/v3/contacts', {
  method: 'POST',
  headers: { 'api-key': BREVO_API_KEY },
  body: JSON.stringify({
    email: email,
    attributes: {
      FIRSTNAME, LASTNAME, COMPANY,
      ASSESSMENT_SCORE: totalScore,
      ASSESSMENT_TIER: tierLabel,
      LEAD_SCORE: totalScore
    },
    listIds: [9, 10],  // 10 only if score >= 38
    updateEnabled: true
  })
})
```

## Deployment Pattern (same as lead magnet)
1. Read full HTML file
2. Extract `<style>` block + `<body>` content
3. Combine: `<style>{css}</style>\n{body}`
4. Prepend body-override `<style>` block for WP structural kills
5. PUT to `/wp-json/wp/v2/pages/{id}` with content + template
6. DELETE `/wp-json/elementor/v1/cache` on purebrain.ai

## Pages
- purebrain.ai: ID 620, template=elementor_canvas → https://purebrain.ai/ai-partnership-audit/
- jareddsanborn.com: ID 1116, template=page-template-blank.php → https://jareddsanborn.com/ai-partnership-audit/

## Tier Score Ranges
- AI Beginner: 10-24 (red)
- AI User: 25-37 (yellow)
- AI Explorer: 38-46 (blue)
- AI Partner: 47-50 (green)

## Key Rules Applied
- CTA button: https://purebrain.ai/#awakening (CTA LINK RULE - never test pages)
- Brand: PUREBR (blue #2a93c1) + AI (orange #f1420b) + N (blue) + .ai (white)
- CSS classes all prefixed `pb-` to avoid WP collisions
- Brevo API key embedded directly in JS (client-side, same as existing patterns on site)
