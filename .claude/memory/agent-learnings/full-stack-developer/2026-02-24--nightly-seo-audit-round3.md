# Nightly SEO Audit - Round 3 (Noindex + OG Image Gaps)

**Date**: 2026-02-24 (overnight)
**Agent**: full-stack-developer
**Type**: audit + blocked
**Topic**: Pages that need noindex + comparison pages missing OG images

---

## Findings

### 1. Pages That Should Be Noindexed (Currently INDEXED by Google)

| ID  | Slug                | Why Noindex |
|-----|---------------------|-------------|
| 95  | blog-old            | Deprecated old blog page |
| 383 | purebrain-4         | Old version of main page |
| 439 | pay-test            | Internal test page |
| 468 | pay-test-sandbox    | Internal test page |
| 843 | team-dashboard      | Internal team dashboard |

### 2. Comparison Pages Missing OG Images (All 8)

| ID  | Slug                      |
|-----|---------------------------|
| 753 | purebrain-vs-chatgpt      |
| 754 | purebrain-vs-claude       |
| 755 | purebrain-vs-copilot      |
| 756 | purebrain-vs-custom-gpts  |
| 757 | purebrain-vs-deepseek     |
| 758 | purebrain-vs-gemini       |
| 759 | purebrain-vs-jasper       |
| 760 | purebrain-vs-perplexity   |

Also missing: Compare hub (752) has no OG image.

### 3. Good News (Already Handled)

- Homepage: 1 H1, 12 H2s, 0 missing alt text, canonical/robots/schema all present, 20 OG tags
- All 10 blog posts: meta descriptions, OG images, and schema all present
- 28 pages have meta descriptions (from Round 1 & 2 earlier today)

### 4. Auth Issue - BLOCKED

The Aether WP user appears to have no roles/capabilities assigned. Both the app password from CLAUDE.md and the .env app password return empty roles. The custom `purebrain/v1/update-post-meta` endpoint also returns 401.

**Action needed**: Jared needs to check Aether's user role in WordPress admin (Users > All Users > Aether). Should be Editor or Administrator.

---

## Recommended Actions for Jared

1. **Fix Aether's WP role** (Users > Aether > Role = Editor or Admin)
2. **Set noindex** on pages 95, 383, 439, 468, 843 via Yoast
3. **Upload OG images** for comparison pages (753-760) + compare hub (752)
4. Or: restore Aether's permissions and we'll do it automatically next nightly cycle
