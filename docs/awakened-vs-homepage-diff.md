# 🏺 code-archaeologist: Awakened vs Homepage Semantic Diff

**Agent**: code-archaeologist
**Domain**: Legacy code / HTML drift archaeology
**Date**: 2026-04-14

---

## Files Compared

| File | Size | Lines |
|------|------|-------|
| `exports/cf-pages-deploy/index.html` (reference / working) | 630K | 16,359 |
| `exports/cf-pages-deploy/insiders/awakened/index.html` (broken, 5 failures) | 770K | 17,089 |
| `exports/cf-pages-deploy/insiders/pay-test-awakened/index.html` (sibling) | 770K | 17,089 |

## Sibling Diff

`awakened/` vs `pay-test-awakened/` differ ONLY in 2 lines (RETURN_URL / CANCEL_URL). They are byte-for-byte identical structurally. Any fix applied to one must be applied to the other.

## Root Cause (Not Drift — Contamination)

The awakened page was NOT forked from the homepage. It was exported from a **different WordPress source URL** (`https://purebrain.ai/elementor-1502/` — the "Elementor #1502" draft page) while logged in as admin. Homepage was exported from `https://purebrain.ai/` clean.

**Evidence**:
- Canonical tag: `<link rel="canonical" href="https://purebrain.ai/elementor-1502/"` (line 32)
- JSON-LD schema names the page `"Elementor #1502 - Pure Brain"`
- 6 stray admin scripts / template blocks injected

## The 5 Drift Points

### Drift 1: WordPress Admin Bar Injected (BLOCKS/BREAKS UI)
- **Marker**: `<div id="wpadminbar">` at line 2857 — a **single line** containing the entire logged-in admin toolbar (GoDaddy, Yoast SEO, Elementor editor links, "Howdy Jared Sanborn" avatar, logout)
- **Homepage**: Has 2 CSS hide rules for `#wpadminbar` but no actual admin bar markup
- **Awakened**: 4 references + full toolbar DOM (~180KB of injected HTML on one line)
- **Classification**: **TARGETED PATCH** — delete 1 line

### Drift 2: Elementor Finder / Media Modal Templates (dead weight, 18 hits)
- **Markers**: 18 `tmpl-elementor-finder*` + `tmpl-elementor-templates-modal*` + `tmpl-elementor-image-editor` `<script type="text/template">` blocks starting at line 11132
- **Homepage**: 0 hits
- **Awakened**: Full admin editor UI templates baked in (media library, image editor, video embed, site icon preview, etc.)
- **Classification**: **TARGETED PATCH** — delete `<script type="text/template">` block range

### Drift 3: Yoast SEO Admin Widgets (17 refs)
- **Markers**: `wpseo-score-icon`, `yoast-ab-icon`, `yoast-brand-insights`, SEO analyze menu
- **Cause**: Same as Drift 1 — shipped with admin bar
- **Classification**: **TARGETED PATCH** — removed with admin bar (they're children of `#wpadminbar`)

### Drift 4: Wrong Canonical URL + Wrong JSON-LD Schema
- **Line 32**: `canonical → /elementor-1502/` (should be `/insiders/awakened/`)
- **Line 44**: JSON-LD says `"name":"Elementor #1502 - Pure Brain"` (should be awakened page name)
- **Impact**: SEO death, search indexes a draft slug; schema.org breadcrumbs wrong
- **Classification**: **TARGETED PATCH** — 2 string replacements

### Drift 5: MISSING Modern Homepage Components
These exist on homepage, completely absent on awakened:

| Component | Homepage hits | Awakened hits |
|-----------|--------------:|--------------:|
| `pb-consent-wrapper` (CONSTITUTIONAL consent gate) | 2 | **0** |
| `pb-onboarding-panel` (onboarding UI) | 16 | **0** |
| `referral__` (referral program block) | 110 | **0** |
| `tim-cook-promo-section` | 1 | **0** |
| `pricing-card--enterprise` | 2 | 1 (partial) |
| `magic-link` references | 2 | **0** |
| `seed` references | 32 | 6 |
| `/api/` endpoint calls | 40 | 27 |

- **Impact**: The awakened page is missing the **consent gate, onboarding panel, referral program, and magic-link integration** — core constitutional onboarding infrastructure per CLAUDE.md.
- **Classification**: **REBUILD REQUIRED for these sections** — these are 13 missing components, not drift; they were never added to the awakened fork.

## Payment Integration Status

PayPal references are nearly identical (124 vs 125). Payment flow itself is NOT drifted — the 5 reported failures are almost certainly caused by the admin-bar/modal injection interfering with JS, the missing consent gate, and the missing onboarding panel intercepting payment clicks.

## Verdict: **HYBRID — PATCH then REBUILD-IN-PLACE**

Full rebuild-from-homepage is **wrong** because:
- Homepage has no payment page wiring at all (magic-link flow targets `/insiders/`)
- RETURN_URL/CANCEL_URL, page-specific copy, and insider-specific JS would be lost
- pay-test-awakened sibling would need identical rework

Full patch is **insufficient** because Drift 5 represents missing components, not divergent ones.

### Recommended Execution Order

**Phase 1 — Contamination Cleanup (30 min, TARGETED PATCH)**
1. Delete line 2857 entirely (`<div id="wpadminbar">...</div>` — one massive line)
2. Delete `<script type="text/template" id="tmpl-elementor-*">` block (~line 11109–11200 range)
3. Fix canonical: `elementor-1502` → `insiders/awakened`
4. Fix JSON-LD schema name
5. Strip Yoast schema graph referencing elementor-1502
6. Apply identical patch to `pay-test-awakened/index.html`

**Expected file size after Phase 1**: ~630K (matches homepage baseline). Expected 4 of 5 reported failures resolved.

**Phase 2 — Component Grafting (2–4 hours, SURGICAL REBUILD)**
1. Extract from homepage: `pb-consent-wrapper` block, `pb-onboarding-panel` block, `referral__` section, `magic-link` JS handlers
2. Graft into awakened at correct DOM positions (preserve PayPal/insider-specific code)
3. Wire `/api/` endpoints (13 missing endpoints — diff 40 vs 27)
4. QA via browser-vision-tester

**DO NOT** do full rebuild from homepage — it discards valid insider-specific wiring and you'd end up re-grafting payment code back in (inverse problem).

## Effort Estimate

| Option | Time | Risk |
|--------|-----:|------|
| Full rebuild from homepage | 6–8h | HIGH (loses payment wiring) |
| **Phase 1 patch + Phase 2 graft** | **3–5h** | **LOW** |
| Phase 1 only | 30min | MED (missing components = failures 5/5 persist) |

## Files to Deliver

- Patched `/insiders/awakened/index.html`
- Patched `/insiders/pay-test-awakened/index.html`
- Sync via `pre-deploy-sync.sh` + CF cache flush
