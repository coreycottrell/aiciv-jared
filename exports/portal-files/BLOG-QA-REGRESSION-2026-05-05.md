# 🚨 Blog QA Regression Report — 2026-05-05

**Source**: BOOP [nightly-blog-qa] (browser-vision-tester)
**Target**: https://purebrain.ai/blog/
**Reference baseline**: March 20 2026 locked-in standard
**Reference post**: `/blog/the-ai-that-gets-smarter-when-you-push-back/` (Mar 18, full standard ✅)

---

## TL;DR

**The March 20 locked-in template was silently abandoned on April 20.** Every post published April 20 → April 30 (7 posts) is missing the FAQ section. Most are also missing the Daily Recap section AND the audio.mp3 file. The current top post (April 30 — "Compound Intelligence Effect") is missing FAQ + Daily Recap + audio.mp3 → broken `<audio>` player on the page.

This is a **template regression**, not a one-off glitch. Posts shipped April 14–17 (when team was still on March 20 template) all pass; posts shipped April 20+ all fail.

---

## 10-Point Index Check

| # | Check | Status | Notes |
|---|---|---|---|
| 1 | Sequential dates newest→oldest | ✅ | Apr 30 → Apr 14 |
| 2 | Latest post at top | ✅ | Compound Intelligence (Apr 30) |
| 3 | Oswald font on headings | ✅ | `font-family: 'Oswald', sans-serif` confirmed |
| 4 | Dark theme #080a12 | ⚠️ | Uses `#0a0c14 / #0d1120 / #080c18` gradient (close but not exact) |
| 5 | Max 10 posts on index | ❌ | **11 posts** rendered (one over limit) |
| 6 | All posts have audio.mp3 | ❌ | **5 of 11 return 404** (see matrix below) |
| 7 | All posts match prompting-is-dead template | ❌ | **7 of 11 missing FAQ + Daily Recap** (see matrix) |
| 8 | Banner images load | ✅ | All 11 banners 200 OK |
| 9 | Footer CTA → /#awakening | ✅ | `https://purebrain.ai/#awakening` |
| 10 | No broken links/404s | ❌ | 5 audio.mp3 files = 404 |

---

## Template Compliance Matrix (all 11 index posts)

`FAQ` = `pb-faq-section` present · `Recap` = "daily recap" mentions · `Video` = `<video>` tag · `Audio` = HTTP status of `audio.mp3`

| Date | Post | FAQ | Recap | Video | Audio |
|------|------|-----|-------|-------|-------|
| Apr 30 | the-compound-intelligence-effect | ❌ | ❌ | ✅ | **404** |
| Apr 26 | the-3-am-test | ❌ | ❌ | ✅ | 200 |
| Apr 23 | your-ai-has-a-memory-problem | ❌ | ❌ | ✅ | 200 |
| Apr 21 | why-your-next-hire-should-be-an-ai | ❌ | ✅ | ✅ | **404** |
| Apr 20 | the-40-percent-problem | ❌ | ❌ | ✅ | **404** |
| Apr 20 | first-ai-to-ai-transaction | ❌ | ❌ | ✅ | **404** |
| Apr 20 | when-your-ai-agent-goes-rogue | ❌ | ❌ | ✅ | **404** |
| Apr 17 | when-the-playbook-runs-out | ✅ | ✅ | ✅ | 200 |
| Apr 15 | your-customers-will-tell-you-everything | ✅ | ✅ | ✅ | 200 |
| Apr 15 | your-ai-wrote-10000-lines | ✅ | ✅ | ✅ | 200 |
| Apr 14 | why-your-ai-investment-isnt-paying-off | ✅ | ✅ | ✅ | 200 |

**Cutover line**: April 17 → April 20. Something changed in the publishing pipeline that dropped two locked sections AND stopped uploading audio for ~70% of posts.

---

## Reference Post Spot-Check (March 20 standard)

`/blog/the-ai-that-gets-smarter-when-you-push-back/` — Published 2026-03-18

- ✅ FAQ section: `pb-faq-section`, `pb-faq-trigger`, `pb-faq-chevron`, `pb-faq-answer` (collapsible)
- ✅ Background video: `<video autoplay muted loop playsinline preload="none">`
- ✅ Daily Recap section (2 mentions in body)
- ✅ Opacity overlays: `rgba(10,12,22,0.55)`, `rgba(15,23,42,0.7)`, `rgba(10,12,22,0.9)` (close to "60% opacity" spec — uses 55/70/90 layering)
- ✅ audio.mp3 = 200

This is what the template should look like. Apr 20+ posts have lost half of it.

---

## Recommended Routing

1. **ST# / PTT#** — investigate publishing pipeline change between Apr 17 and Apr 20. Did template skeleton get swapped? Did the FAQ injector / Daily Recap generator break?
2. **MA#** — backfill: regenerate FAQ + Daily Recap sections + audio.mp3 for the 7 affected posts. Priority on the LATEST post (Compound Intelligence, Apr 30) which is currently the front-page representation of the brand.
3. **MA# / Aether** — confirm whether 11-post index is intentional cadence change, or revert to max 10.
4. **PR / blog-thread automation** — verify next published post is fully compliant before deploy. Add automated FAQ/Recap/audio existence check to the pre-deploy gate.

---

## Cross-BOOP Convergence Note

Per `feedback_cross_boop_convergence_signal.md`: this is the FIRST convergence signal on the post-template regression in this BOOP. If a second BOOP / agent independently flags the same Apr 20 cutover, escalate to immediate fix without waiting for a third confirmation.

---

**Filed by**: browser-vision-tester (BOOP nightly-blog-qa)
**Timestamp**: 2026-05-05
**Evidence**: `curl -s -o /dev/null -w "%{http_code}"` on all 12 posts (incl. reference); HTML inspected for `pb-faq-section`, `daily recap`, `<video`
