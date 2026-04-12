# Hunden Enterprise Proposal Page — Build + Deploy

**Date**: 2026-03-06
**Type**: operational + teaching
**Topic**: Premium password-protected enterprise proposal page for Hunden Partners — WordPress Page ID 1329

---

## What Was Built

Full self-contained dark-theme HTML proposal page for Hunden Partners (hospitality consulting firm). Premium enterprise consulting aesthetic.

**File**: `/home/jared/projects/AI-CIV/aether/exports/client-proposals/hunden-proposal-page.html`
**Source content**: `/home/jared/projects/AI-CIV/aether/exports/client-proposals/hunden-ai-deployment-proposal.md`

**WordPress**:
- Page ID: 1329
- URL: https://purebrain.ai/hunden-proposal/
- Password: hunden2026
- Template: elementor_canvas
- Status: publish (password protected)

---

## Design Patterns Used

### Color palette
- Background: `#080a12` (deep dark)
- Surface: `#0e1120` / `#131627`
- Blue brand: `#2a93c1`
- Orange brand: `#f1420b`
- Gold accent: `#c8a84e` (used for enterprise/premium emphasis)
- Body text: `#e8ecf4`, secondary: `#b0b8c8`, muted: `#7a8494`

### Layout sections built
1. Fixed top nav bar with section anchors + "Confidential" pill
2. Scroll nav dots (right side, hidden until scroll, reveals active section)
3. Hero: badge + H1 + stat cards + key distinction block
4. Needs analysis: 6 domain cards in responsive grid
5. Architecture: 6 civilization cards (each with color-coded top accent bar, agent list, brain stream count)
6. Hunden OS infrastructure block (4-component grid)
7. Phase timeline: vertical line with 3 phases, pilots listed in Phase 1 cards
8. Pricing: standard tier reference (faded) → enterprise table → total card → phased cards → add-ons table
9. ROI: 2-column cards with big numbers + detail + "leverage" statement block
10. Why PureBrain: 2-column comparison (CCW vs PureBrain) + alignment block
11. Next Steps: 4 step cards + contact card
12. Appendix: brain stream summary table + pilot mapping table

### Key CSS pattern: card hover effect
```css
.hp-civ-card:hover {
  border-color: rgba(42, 147, 193, 0.35);
  box-shadow: 0 12px 40px rgba(0,0,0,0.4);
  transform: translateY(-3px);
}
```
Top accent bar on civ cards via positioned 3px `div` with gradient — clean way to color-code sections.

### Scroll nav dots pattern
- Position fixed, right 24px, opacity 0 by default
- JS adds `.visible` class after 200px scroll
- Active dot detection: loops sections, checks `getBoundingClientRect().top <= 120`
- Tooltip via CSS `::after` with `data-label` attribute (no JS needed)

---

## WordPress Deployment Pattern (Password-Protected)

```python
import json, base64, urllib.request

with open('page.html', 'r') as f:
    content = f.read()

# CRITICAL: build the wp:html wrapper WITHOUT string interpolation
# to avoid any escaping of the <!-- --> markers
opening = '<!-- wp:html -->'
closing = '<!-- /wp:html -->'
wrapped = opening + '\n' + content + '\n' + closing

payload_dict = {
    "title": "Page Title",
    "content": wrapped,
    "status": "publish",
    "password": "your-password-here",  # WP handles pw protection
    "template": "elementor_canvas",
    "slug": "page-slug"
}
payload = json.dumps(payload_dict).encode('utf-8')  # json.dumps handles escaping correctly

req = urllib.request.Request("https://purebrain.ai/wp-json/wp/v2/pages", data=payload, method='POST')
req.add_header('Content-Type', 'application/json; charset=utf-8')
req.add_header('Authorization', f'Basic {base64.b64encode(b"Aether:APP_PASS").decode()}')
req.add_header('User-Agent', 'Mozilla/5.0 ...')
resp = urllib.request.urlopen(req, timeout=30)
data = json.loads(resp.read())
# data['id'], data['link'], data['status']
```

**Password protection**: just pass `"password": "value"` in payload. WordPress handles the pw gate natively — no frontend logic needed. Response will have `"password": ""` in the output (WP strips it from response for security) but the page IS password protected. Verified by `data.get('password')` check being falsy — don't use that to confirm; check the actual live page instead.

---

## Dark Background Override (Required for elementor_canvas)

Must include in every self-contained page's `<style>`:
```css
body {
  background: #080a12 !important;
  background-color: #080a12 !important;
  color: #e8ecf4 !important;
  border-color: transparent !important;
}
body.tt-magic-cursor,
body.page-template-elementor_canvas {
  background: #080a12 !important;
  background-color: #080a12 !important;
  color: #e8ecf4 !important;
  border-color: transparent !important;
  fill: currentColor !important;
}
```
This beats the `[class*="magic"]` WordPress Additional CSS orange override.

---

## What Worked Well

- Color-coded civ cards with gradient accent bars → visual differentiation without complexity
- Stat cards in hero give instant TL;DR for executives
- Phase timeline with vertical line looks premium, far better than a plain table
- ROI section with large numbers ($187K, $1.2M) carries impact
- Phased pricing cards let client see the entry point clearly vs full commitment
- Gold (#c8a84e) used specifically for enterprise/premium elements (total pricing, gold accents) — good hierarchy signal
