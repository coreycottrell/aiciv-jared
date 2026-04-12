# Homepage Visual Bug Fix: Transparent Sections + Demo Video Player

**Date**: 2026-03-04
**Type**: fix + pattern + deployment
**Pages**: 11 (Homepage)
**Urgency**: URGENT - reported by Jared

---

## Bugs Fixed

### Bug 1: Background Video Bleeding Through Sections
**Root Cause**: `.video-background` is `position: fixed; z-index: -1` (brain video plays as fixed full-screen background). Multiple content sections had `background: transparent` CSS, causing the fixed video to show through them.

**Affected sections**: `.section`, `.chat-section`, `.value-section`

**Fix**: Changed `background: transparent` to dark gradient in all three:
```css
background: linear-gradient(180deg, rgba(8,10,18,0.85) 0%, rgba(8,10,18,0.98) 15%, rgba(8,10,18,0.98) 85%, rgba(8,10,18,0.85) 100%);
```
This matches the sandbox-3 pattern that was already working correctly.

### Bug 2: Footer Background Showing Brain Video
**Root Cause**: `.footer` CSS had `background: transparent`.

**Status**: This was ALREADY FIXED by a previous deploy (FOOTER BACKGROUND FIX - 2026-03-04 comment in the code). The fix uses `rgba(5, 8, 15, 0.97) !important`. Footer was confirmed working at `rgba(5, 8, 15, 0.97)` via getComputedStyle.

### Bug 3: Demo Video Player Dark/Not Loading
**Root Cause**: The `pbDemoPlayer` uses `preload="none"` so it's intentionally dark before click. But there was no poster image set, making it look broken.

**Fix**: Added `poster="https://purebrain.ai/wp-content/uploads/2026/02/MA1.BI-1.2.4-002-211107-Icon-PT.png"` to the `#pbDemoVideo` element.

**Verification**: `overlay display=flex, visible=true, hasPlayingClass=false` (play button visible and working)

---

## Key Technical Pattern: getComputedStyle for Gradients

When using `background: linear-gradient(...)` CSS, `getComputedStyle(el).backgroundColor` returns `rgba(0,0,0,0)` (transparent) because the color is in `backgroundImage`, NOT in `backgroundColor`. This is expected browser behavior.

To verify gradient fix:
```javascript
// WRONG check:
window.getComputedStyle(el).backgroundColor // always rgba(0,0,0,0) for gradients

// RIGHT check:
window.getComputedStyle(el).backgroundImage // returns the gradient string
```

---

## Deployment Method

```python
# Use requests library with dotenv for auth (NOT curl - env vars don't load)
from dotenv import load_dotenv
import requests

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
wp_user = os.getenv('PUREBRAIN_WP_USER', '')
wp_pass = os.getenv('PUREBRAIN_WP_APP_PASSWORD', '')

# PUT the fixed _elementor_data
resp = requests.put(
    'https://purebrain.ai/wp-json/wp/v2/pages/11',
    auth=(wp_user, wp_pass),
    json={"meta": {"_elementor_data": fixed_ed}},
    timeout=120
)

# MANDATORY: Clear Elementor cache after update
requests.delete(
    'https://purebrain.ai/wp-json/elementor/v1/cache',
    auth=(wp_user, wp_pass)
)
```

**CRITICAL**: `source .env` in bash does NOT work for PUREBRAIN_WP credentials. Use `python-dotenv` in Python instead.

---

## Reference: Comparison with sandbox-3

The sandbox-3 page (ID: 1232) was the reference for "how it should look":
- `section { background: linear-gradient(180deg, rgba(8,10,18,0) 0%, rgba(8,10,18,1) 8%, rgba(8,10,18,1) 92%, rgba(8,10,18,0) 100%) }` (solid center, transparent edges for nice fade)
- `.footer { background: rgba(5, 8, 15, 0.95) !important }` (nearly opaque dark)

Homepage was different - had `background: transparent` for all sections.

---

## Files

- Backup: `/home/jared/projects/AI-CIV/aether/exports/backup_page_11_elementor_data_2026-03-04-visual-bug-fix.json`
- Fixed elementor data was deployed directly via API (no local file saved - too large for standard deployment)

---

## QA Results

| Check | Result |
|-------|--------|
| About section background | Dark gradient applied (bgImage contains rgba(8,10,18,0.85)) |
| Chat/awakening section | Dark gradient applied |
| Value section | Dark gradient applied |
| Footer | rgba(5, 8, 15, 0.97) - already working |
| Demo video poster | PT logo showing before play |
| Demo play overlay | Visible and ready (display: flex) |
| Background video (bgVideo) | Playing (paused: false, readyState: 2) |
| Elementor cache | Cleared after deployment |

---

## Tags

homepage, page-11, background-video, transparent-sections, video-bleed, demo-player, footer-background, css-fix, z-index, elementor, deployment
