# Mobile Footer Overlap Root Cause: Mission Section — Plugin v5.9.0

**Date**: 2026-02-24
**Agent**: full-stack-developer
**Type**: teaching + gotcha
**Plugin Version**: 5.9.0

---

## Bug Fixed

### Root Cause: "Our Purpose" Mission Section (pb-mission-section)

**Symptom**: After removing the "Why Different" bar (v5.7.0), Jared still reported mobile
footer overlap — something "between the Pure Technology footer and the Aether bar."

**Root cause discovered**: The `pb-mission-section` (Our Purpose) section was still present.
It was:
- Injected via wp_footer priority 5 (CSS + HTML, display:none)
- Moved into the DOM by JS (priority 6) using `insertBefore()` BEFORE the theme footer
- Selector used: `footer:not(#pb-aether-footer)` → matches `<footer class="footer">` (Pure Technology theme footer)
- Final DOM order on mobile: [page content] → [**pb-mission-section**] → [Pure Technology footer] → [Legal/Privacy bar] → [Aether fixed bar]

The mission section had `padding: 40px 20px 44px` on mobile — it's a full content block with
eyebrow text ("Our Purpose"), h2 heading, paragraph, and a CTA button. This is what Jared
was seeing as the "leftover remnant."

**Fix**: Remove the entire mission section (both wp_footer hooks at priority 5 and 6).
The Aether footer credit bar already links to `/mission-vision-values/` — no content lost.

---

## Pattern: "We Fixed It" But It's Still Broken

v5.7.0 removed the "Why Different" fixed bar. But the "Our Purpose" section was a SEPARATE
element added in v5.2.0–v5.4.0. Both were conceptually "footer additions" but one was
`position: fixed` and one was `position: relative` in the normal flow.

**Lesson**: When fixing mobile footer overlap:
1. Check ALL injected elements near the footer — both fixed AND in-flow
2. `position: fixed` elements overlap content FROM ABOVE
3. In-flow elements (like pb-mission-section) appear AS VISIBLE CONTENT between
   the theme footer and the fixed Aether bar on mobile

---

## Investigation Method

1. `curl https://purebrain.ai/?cb=TIMESTAMP | grep "id=\"pb-"` → lists all injected elements
2. Check DOM order of pb- elements: pb-mission-section appeared BEFORE theme footer
3. Check `display:none` in HTML → section starts hidden, JS makes it visible

Key signals:
- `id="pb-mission-section"` in HTML with `style="display:none;"` = section exists but deferred
- If JS runs, `section.style.display = ''` makes it visible
- The section inserts before `footer:not(#pb-aether-footer)` = Pure Technology footer

---

## Files Changed

- Plugin: `tools/security/purebrain-security/purebrain-security-plugin.php` (v5.8.0 → v5.9.0)
  - Removed: `add_action('wp_footer', ..., 5)` — the CSS + HTML block
  - Removed: `add_action('wp_footer', ..., 6)` — the JS DOM insertion companion
  - Added: removal comment block where code used to be
- Deploy script: `tools/security/deploy_plugin_v590_purebrain.py`

---

## Deployment

- All 15 validation checks: OK
- All 5 pages verified live (with cache-bust query string):
  - homepage: PASS
  - pay-test: PASS
  - pay-test-2: PASS
  - pay-test-sandbox: PASS
  - pay-test-sandbox-2: PASS

---

## Validation Check Pattern

When removing a block that's referenced in changelog comments, the check string
must target the ACTUAL CODE ARTIFACT (style tag, script tag, HTML element) not
just the ID name — because the ID appears in changelog text too.

WRONG: `"pb-mission-section-v540" not in content`  (still in changelog text)
RIGHT: `'<style id="pb-mission-section-v540">' not in content`  (the actual rendered code)
