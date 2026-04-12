# Three Page Fixes + PROTECTED-PAGES System

**Date**: 2026-03-19
**Type**: operational + teaching
**Topic**: CF Pages autonomous deploys breaking approved pages

## Root Cause

Overnight referral system update (90-day cookie, first-touch attribution) touched homepage and sandbox-3. The `<script src="/referral-tracker.js">` injection was correct. Surrounding CSS edits introduced conflicts.

## Fix 1: Sandbox-3 z-index (WHAT HAPPENS NEXT / WHAT OTHERS HAVE BUILT invisible)

**Cause**: `.timeline-section` and `.testimonials-section` had no `position` or `z-index`. The `video-background` div uses `position: fixed; z-index: 0`. Static-position elements cannot establish stacking context relative to fixed elements — content rendered behind the video.

**Fix**: Add `position: relative; z-index: 1;` to both sections.

**Pattern**: Any content section on pages with `position: fixed; z-index: 0` background MUST have `position: relative; z-index: 1` or higher, or it won't show through.

## Fix 2: Footer logo wrong proportions

**Cause**: Two conflicting `.footer__logo` CSS rules in the same style block:
- Earlier rule: `{ height: 40px; width: 240px; }` — forces fixed width, distorts aspect ratio
- Later rule: `{ height: 40px; width: auto; max-width: 240px; }` — correct

The later rule wins but the earlier one created confusion and potential for future regressions. Both now read `width: auto; max-width: 200px`.

**Pattern**: Never use `width: Npx` on logos with natural aspect ratios. Always `width: auto`.

## Fix 3: Hero gap (recurring — 10+ times fixed)

**Cause**: WordPress `admin-bar` class or other CSS cascade issues periodically re-introduce `margin-top` on `html`. The fix keeps getting undone by overnight agents.

**Permanent fix**: Injected a named CSS block `/* PERMANENT HERO GAP FIX v1.0 */` as the LAST rule in the hero style block. Covers `html`, `html body.home`, `body.home`, `html.admin-bar`, `body.admin-bar`, `body.home.admin-bar` — all `margin-top: 0 !important; padding-top: 0 !important`.

**Key insight**: Place this LAST in the style block so it wins the cascade. Name it clearly so future agents don't remove it.

## PROTECTED-PAGES.md

Created: `.claude/PROTECTED-PAGES.md`

Lists 7 pages that autonomous agents must NOT modify without explicit Jared approval:
- index.html (homepage)
- live/index.html
- insiders/index.html
- awakened/index.html
- partnered/index.html
- unified/index.html
- pay-test-sandbox-3/index.html

Includes rules for agents, root cause documentation, and escalation path.

## Git Diff Analysis

The ONLY change in the overnight commit that should have been made:
```
+<script src="/referral-tracker.js" defer></script>
```

And referral tracking JS changes (cookie expiry 30→90 days, first-touch attribution, uppercase normalization). These were valid. The CSS conflicts were introduced alongside.

## Files Changed

- `exports/cf-pages-deploy/pay-test-sandbox-3/index.html` — z-index fix
- `exports/cf-pages-deploy/index.html` — footer logo + hero gap
- `.claude/PROTECTED-PAGES.md` — new protection policy document
