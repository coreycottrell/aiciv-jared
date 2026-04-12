# PureBrain A/B Test Implementation Files

**Created**: 2026-02-17
**Based on**: PUREBRAIN-FULL-UX-AUDIT-2026-02-17.md
**Agent**: full-stack-developer

---

## Files in This Directory

| File | Test | What it is |
|---|---|---|
| `test1-simple-form.html` | Form Simplification | Drop-in 2-field form (Name + Email) with analytics, AJAX submit, success state |
| `test2-cta-variants.md` | CTA Copy Test | All copy options, implementation instructions, analytics plan |
| `test3-overlay-css.css` | Background Overlay Opacity | CSS for 35% (control) vs 18% (variant) with JS assignment snippet |
| `test4-trust-signals.html` | Trust Signals Position | Self-contained trust bar HTML, paste below hero section |
| `test5-headline-variants.md` | Headline Rewrite | All headline variants, supporting copy matrix, JS split script |
| `test6-exit-intent-timing.js` | Exit Intent Timing | Full vanilla JS exit intent handler with variant assignment and analytics |
| `README.md` | — | This file |

---

## Concurrency Guide

Not all tests can run at the same time. Tests affecting the same page element interfere with each other's signal.

| Test | Can run with |
|---|---|
| Test 1 (Form) | Tests 3, 4 |
| Test 2 (CTA Copy) | Tests 3, 4 — NOT with Test 5 |
| Test 3 (Overlay) | Tests 1, 2, 4, 6 |
| Test 4 (Trust Signals) | Tests 1, 2, 3, 5, 6 |
| Test 5 (Headline) | Tests 3, 4, 6 — NOT with Test 2 |
| Test 6 (Exit Intent) | Tests 3, 4, 5 |

**Recommended launch sequence**:
- Week 1-3: Tests 1 + 3 + 4 (form, overlay, trust bar — independent elements)
- Week 4-6: Tests 5 + 4 + 6 (headline, trust bar continued, exit intent)
- Week 7-9: Test 2 (CTA copy — after headline winner is locked in)

---

## Minimum Run Times

| Test | Minimum run | Minimum sample |
|---|---|---|
| Test 1 | 2 weeks | 200 form views per variant |
| Test 2 | 3 weeks | 300 CTA clicks per variant |
| Test 3 | 3 weeks | 400 sessions per variant |
| Test 4 | 3 weeks | 500 visitors per variant |
| Test 5 | 3 weeks | 400 unique visitors per variant |
| Test 6 | 3 weeks | 500 exit intent triggers per variant |

---

## Analytics Setup (GA4)

All tests fire events in this format:

```
Event: ab_variant_assigned
Properties: { test_name: "[test-name]", variant: "control"|"b"|"c" }
```

Primary conversion event to track for all tests:
```
Event: form_submit
Properties: { test_name: "[test-name]", variant: "[variant]" }
```

Build a single GA4 exploration report segmented by `ab_variant` dimension to compare all tests.

---

## Predicted Impact Summary

| Test | Predicted lift | Confidence |
|---|---|---|
| Test 1 (Form Simplification) | +40-60% form completion | High — industry benchmark |
| Test 2 (CTA Copy) | +15-30% CTR | Medium |
| Test 3 (Overlay Opacity) | +8-15% scroll depth | Medium |
| Test 4 (Trust Signals) | +15-25% CTR | Medium-High |
| Test 5 (Headline) | -10-20% bounce rate | High — addresses #1 issue |
| Test 6 (Exit Intent) | +20-35% modal conversion rate | Medium |

Combined full-funnel lift estimate (all tests winning): 4-6X increase in overall conversion rate (aligned with UX audit projection of 2.1% → 12.6%).
