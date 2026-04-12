# SEO noindex + Meta Tags Report — purebrain.ai

**Date**: 2026-02-27
**Agent**: full-stack-developer
**Site**: purebrain.ai
**Auth**: Aether via WP REST API + custom plugin endpoint

---

## Summary

All tasks complete. 16 pages processed.

| Category | Count | Status |
|----------|-------|--------|
| Pages already noindexed (verified) | 14 | CONFIRMED |
| Pages newly noindexed | 2 | APPLIED |
| Legal pages restored to indexed | 2 | CONFIRMED INDEXED |
| Pages with new SEO meta (OG title, desc, image) | 3 | APPLIED |

---

## Section 1: Pages Already Noindexed — CONFIRMED

All 14 pages had `_yoast_wpseo_meta-robots-noindex = "1"` confirmed via REST API.

| ID | Slug | Status |
|----|------|--------|
| 95 | /blog-old/ | CONFIRMED noindex |
| 174 | /purebrain-2-0/ | CONFIRMED noindex |
| 338 | /purebrain-3/ | CONFIRMED noindex |
| 383 | /purebrain-4/ | CONFIRMED noindex |
| 439 | /pay-test/ | CONFIRMED noindex |
| 468 | /pay-test-sandbox/ | CONFIRMED noindex |
| 688 | /pay-test-sandbox-2/ | CONFIRMED noindex |
| 689 | /pay-test-2/ | CONFIRMED noindex |
| 811 | /ai-partnership-calculator/ | CONFIRMED noindex |
| 843 | /team-dashboard/ | CONFIRMED noindex |
| 854 | /duckdive-report/ | CONFIRMED noindex |
| 859 | /client-report-duckdive/ | CONFIRMED noindex |
| 309 | /thank-you/ | CONFIRMED noindex |
| 855 | /website-execution/ | CONFIRMED noindex |

---

## Section 2: Newly Noindexed Pages — APPLIED

| ID | Slug | Before | After | Verification |
|----|------|--------|-------|--------------|
| 963 | /demo-no-bs/ | index (no meta) | noindex | CONFIRMED via REST |
| 532 | /living-avatar/ | index (no meta) | noindex | CONFIRMED via REST |

---

## Section 3: Legal Pages — Restored to Indexed

These pages incorrectly had noindex set. Now restored to allow indexing.

| ID | Slug | Before | After | Yoast Robots |
|----|------|--------|-------|--------------|
| 3 | /privacy-policy/ | noindex | **indexed** | `index, follow` |
| 541 | /terms-of-service/ | noindex | **indexed** | `index, follow` |

**Verification method**: Yoast `get_head` API confirms `{'index': 'index', 'follow': 'follow'}` for both pages.

---

## Section 4: AI Readiness Assessment (ID 403) — SEO Meta Applied

Page: https://purebrain.ai/ai-readiness-assessment/

| Field | Value | Status |
|-------|-------|--------|
| OG Title | "AI Readiness Self-Assessment | PureBrain.ai" | APPLIED |
| OG Description | "Assess your readiness for AI partnership. Free self-assessment to determine which PureBrain tier fits your business." | APPLIED |
| Meta Description | "Free AI readiness self-assessment to determine your business's readiness for AI partnership with PureBrain." | APPLIED |
| Excerpt | "Free AI readiness self-assessment to determine your business's readiness for AI partnership with PureBrain." | APPLIED |
| OG Image | https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg (media 694) | APPLIED |
| noindex | Not set (remains indexed) | NO CHANGE |

**Live verification**:
- `og_title` confirmed in `yoast_head_json`: "AI Readiness Self-Assessment | PureBrain.ai"
- `og_image` confirmed: 1200x627 JPEG from media 694
- `og_description` confirmed active

---

## Section 5: Privacy Policy (ID 3) — SEO Meta Applied

Page: https://purebrain.ai/privacy-policy/

| Field | Value | Status |
|-------|-------|--------|
| SEO Title | "Privacy Policy | PureBrain.ai — Pure Technology" | APPLIED |
| OG Title | "Privacy Policy — PureBrain.ai" | APPLIED |
| Excerpt | "PureBrain.ai privacy policy by Pure Technology. How we collect, use, and protect your data." | APPLIED |
| noindex | Removed — now `index, follow` | RESTORED |

**Live verification**: `yoast_head_json.title` = "Privacy Policy | PureBrain.ai — Pure Technology" ✓

---

## Section 6: Terms of Service (ID 541) — SEO Meta Applied

Page: https://purebrain.ai/terms-of-service/

| Field | Value | Status |
|-------|-------|--------|
| SEO Title | "Terms of Service | PureBrain.ai — Pure Technology" | APPLIED |
| OG Title | "Terms of Service — PureBrain.ai" | APPLIED |
| Excerpt | "PureBrain.ai terms of service by Pure Technology. Terms governing use of PureBrain AI partnership services." | APPLIED |
| noindex | Removed — now `index, follow` | RESTORED |

**Live verification**: `yoast_head_json.title` = "Terms of Service | PureBrain.ai — Pure Technology" ✓

---

## Technical Notes

### Methods Used

1. **Standard REST API** (`/wp-json/wp/v2/pages/{id}`) for:
   - Setting `_yoast_wpseo_meta-robots-noindex` (registered with `show_in_rest => true`)
   - Setting page excerpt

2. **Custom Plugin Endpoint** (`/wp-json/purebrain/v1/update-post-meta`) for:
   - `_yoast_wpseo_title` (SEO title)
   - `_yoast_wpseo_opengraph-title`
   - `_yoast_wpseo_opengraph-description`
   - `_yoast_wpseo_opengraph-image`
   - `_yoast_wpseo_opengraph-image-id`
   - `_yoast_wpseo_metadesc`

### noindex Value Semantics

In Yoast's schema:
- `"1"` = noindex (blocked from search engines)
- `""` (empty string) = default behavior = `index` (allowed)
- `"0"` = explicitly set to index (same effect as empty string)

Setting noindex to `"0"` results in the meta returning `""` - this is correct behavior. Yoast normalizes this to the default "index" state.

### No Content Modified

Zero page content was modified. All changes were limited to Yoast SEO meta fields and page excerpt fields only.

---

## Script

Script used: `/home/jared/projects/AI-CIV/aether/tools/seo_noindex_apply.py`
