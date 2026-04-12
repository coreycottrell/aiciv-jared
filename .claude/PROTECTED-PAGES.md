# PROTECTED PAGES — DO NOT MODIFY WITHOUT EXPLICIT JARED APPROVAL

**Last Updated**: 2026-03-19
**Reason**: These pages have been approved by Jared and were broken by overnight autonomous deploys.
**Rule**: NO agent may modify these files without a direct ST# or explicit written instruction from Jared.

---

## Protected Files

| File | URL | Notes |
|------|-----|-------|
| `exports/cf-pages-deploy/index.html` | https://purebrain.ai | Homepage. Hero gap fix applied 10+ times. Footer logo sizing stabilized. |
| `exports/cf-pages-deploy/live/index.html` | https://purebrain.ai/live/ | Live page — do not touch |
| `exports/cf-pages-deploy/insiders/index.html` | https://purebrain.ai/insiders/ | Insiders page |
| `exports/cf-pages-deploy/awakened/index.html` | https://purebrain.ai/awakened/ | Awakened tier page |
| `exports/cf-pages-deploy/partnered/index.html` | https://purebrain.ai/partnered/ | Partnered tier page |
| `exports/cf-pages-deploy/unified/index.html` | https://purebrain.ai/unified/ | Unified tier page |
| `exports/cf-pages-deploy/pay-test-sandbox-3/index.html` | https://purebrain.ai/pay-test-sandbox-3/ | Payment test page — section z-index fixed |

---

## What Broke These Pages (Root Cause — 2026-03-19)

The referral system update (90-day cookie, first-touch attribution) modified these files and injected `<script src="/referral-tracker.js" defer></script>` before `</body>`. That specific change is fine.

**What was NOT fine**: The overnight referral update also touched the homepage CSS in a way that re-introduced two recurring bugs.

1. **Sandbox-3 z-index**: `.timeline-section` and `.testimonials-section` needed `position: relative; z-index: 1;` to render above the fixed `video-background` (z-index: 0). When missing, the section content is invisible.

2. **Homepage footer logo**: A `width: 240px` rule was present earlier in the style block conflicting with the correct `width: auto; max-width: 200px` rule. Fixed by making both rules consistent.

3. **Homepage hero gap** (recurring — 10+ fixes): The `admin-bar` body class or CSS cascade rules periodically re-introduce `margin-top` on `html`. A permanent nuclear override block now runs as the LAST CSS rule in the hero style block.

---

## Rules for Agents

- **NEVER** add `margin-top` or `padding-top` to `html`, `body`, `body.home`, or `#hero` on the homepage.
- **NEVER** set `width: Npx` on `.footer__logo` — always use `width: auto`.
- **NEVER** change `z-index` on `.video-background`, `.timeline-section`, or `.testimonials-section` without understanding the full stacking context.
- **NIGHTLY JOBS** must NOT modify HTML structure, CSS, or content in any file listed above.
- Referral tracker script injection (appending `<script src="/referral-tracker.js">`) is the ONLY autonomous modification permitted on these pages.

---

## If You Must Make A Change

1. Get explicit approval from Jared (ST# message with specific change described)
2. Document what you're changing and why in git commit message
3. Always test locally before deploying
4. After deploy, verify at the live URLs listed above
