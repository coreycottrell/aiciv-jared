# Nightly Blog QA — Regression Report

**Date**: 2026-05-03
**Source BOOP**: `nightly-blog-qa`
**Reference standard**: March 20, 2026 locked-in template (`feedback_blog_locked_in_march20.md`)
**Reference post**: `the-ai-that-gets-smarter-when-you-push-back` ✅ template-compliant

---

## STATUS: REGRESSION FOUND — needs ST# attention

Index page renders correctly and core branding holds, but **5 of 11 indexed posts ship with a broken `<audio>` player** (404 on `audio.mp3`), and **the latest top post is missing the FAQ + daily recap sections**.

---

## Index page (`https://purebrain.ai/blog/`) — checklist

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Sequential dates newest-to-oldest | ✅ | 04-30 → 04-26 → 04-23 → 04-21 → 04-20 → 04-20 → 04-20 → 04-17 → 04-15 → 04-15 → 04-14 |
| 2 | Latest post at top | ✅ | "The Compound Intelligence Effect" (Apr 30, 2026) |
| 3 | Oswald font on headings | ✅ | `@import` + `font-family: 'Oswald'` on all heading classes |
| 4 | Dark theme #080a12 | ⚠️ | Index uses `linear-gradient(180deg, #000000 0%, #0a0a0f 50%, #000000 100%)` and a secondary `#0a0c14 → #0d1120 → #080c18` gradient. Visually dark, but not the exact `#080a12` token. Post pages do contain `#080a12` in CTA gradients. **Minor — flag, don't block.** |
| 5 | Max 10 posts on index | ❌ | **11 posts shown** — one over the locked cap. Dropping one needed (likely de-dupe the 3× Apr 20 cluster). |
| 6 | All posts have audio.mp3 | ❌ | **5/11 are 404** (see table below) |
| 7 | All posts match prompting-is-dead template | ⚠️ | Audio/video/Oswald/dark theme intact across all 3 spot-checks. **Top post missing FAQ + daily recap.** Mid post missing daily recap. |
| 8 | Banner images load correctly | ✅ | All 11 banners return 200 |
| 9 | Footer CTA → /#awakening | ✅ | Two CTAs present, both `https://purebrain.ai/#awakening` |
| 10 | No broken links / 404s | ❌ | Audio 404s above |

---

## Audio.mp3 status (all 11 indexed posts + reference)

| Post | audio.mp3 |
|------|-----------|
| the-compound-intelligence-effect-... (TOP) | ❌ **404** |
| the-3-am-test | ✅ 200 |
| your-ai-has-a-memory-problem | ✅ 200 |
| why-your-next-hire-should-be-an-ai | ❌ **404** |
| the-40-percent-problem | ❌ **404** |
| first-ai-to-ai-transaction | ❌ **404** |
| when-your-ai-agent-goes-rogue | ❌ **404** |
| when-the-playbook-runs-out | ✅ 200 |
| your-customers-will-tell-you-everything | ✅ 200 |
| your-ai-wrote-10000-lines | ✅ 200 |
| why-your-ai-investment-isnt-paying-off | ✅ 200 |
| the-ai-that-gets-smarter-when-you-push-back (ref) | ✅ 200 |

The 5 broken posts each contain the template comment:
`<!-- For MVP, audio is skipped. Run TTS separately and commit audio.mp3 after. -->`

→ TTS pipeline (voice.purebrain.ai / Chatterbox at `aether` voice) was never re-run for these 5. Each post still ships an `<audio controls>` element pointing at the missing file.

---

## Spot-check: 4 locked features per post

| Feature | Reference (push-back) | TOP (compound-intel) | MID (memory-problem) |
|---------|----------------------|---------------------|----------------------|
| 60% opacity bg | (n/a in scan) | ✅ rgba(...,0.6) found | ✅ |
| Background video | ✅ | ✅ | ✅ |
| Collapsible FAQs (`<details>`) | ✅ 4 blocks | ❌ **0 — missing** | ✅ 5 blocks |
| Daily recap section | ✅ 8 mentions | ❌ **missing** | ❌ **missing** |

---

## Recommended actions (route to ST#)

1. **HIGH — Run TTS for the 5 missing posts** (voice = `aether`, per voice rules locked 2026-04-15). All 5 already have `<audio>` tags wired; just generate + commit `audio.mp3` to each post folder + redeploy to `purebrain-production`.
2. **MEDIUM — Drop one post from the index** so the latest-posts block returns to the locked cap of 10.
3. **MEDIUM — Backfill FAQ section on top post** (`the-compound-intelligence-effect-why-month-6-matters-more-t`).
4. **MEDIUM — Backfill daily recap on top + mid posts.**
5. **LOW — Audit blog generator template** to see why newer posts (Apr 21+) are skipping FAQ/recap blocks. Likely a generator regression — root cause is more valuable than per-post backfill.
6. **LOW — Decide if `#080a12` exact token should be enforced on index gradients** or whether the close-equivalent dark gradients are acceptable.

---

## What passed (no action needed)

- Sort order, latest-on-top, banner image URLs, Oswald, footer CTA, dark visual theme, `<video>` background, audio HTML element, `<details>`-style FAQs (where present), `#080a12` in CTA blocks, reference post fully compliant.

---

*Filed by browser-vision-tester (BOOP `nightly-blog-qa`). Verification method: curl + grep on live `purebrain.ai/blog/` HTML and 12 individual asset URLs.*
