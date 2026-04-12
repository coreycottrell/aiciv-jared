# Blog SEO Updater - purebrain.ai

**Date**: 2026-02-18
**Agent**: full-stack-developer
**Type**: teaching
**Topic**: WordPress REST API SEO automation, FAQ schema, internal linking

---

## What Was Built

`/home/jared/projects/AI-CIV/aether/tools/blog_seo_updater.py`

A Python script that analyses all published posts on purebrain.ai and generates:
1. FAQ JSON-LD schema markup (detected from H2/H3 questions and paragraph Q&A)
2. Meta descriptions under 155 chars (preserves existing Yoast/excerpt, generates if missing)
3. Internal links via "Related Reading" section (topical matching)

Dry-run report saved to: `/home/jared/projects/AI-CIV/aether/exports/seo-update-plan.md`

---

## Key Technical Decisions

### Idempotency
Both FAQ schema and internal link injection check for prior existence before adding:
- `has_existing_faq_schema()` checks for `"@type": "FAQPage"` in content
- `has_existing_related_section()` checks for the generator comment marker
Running the script twice will NOT double-add content.

### FAQ Detection Strategy
Two complementary approaches:
1. H2/H3 headings that end with "?" -> collect all following sibling text until next heading
2. Paragraphs starting with FAQ_QUESTION_STARTERS words and ending "?" -> next non-empty paragraph is answer

### Meta Description Priority Order
1. Existing Yoast `_yoast_wpseo_metadesc` (<=155 chars) -> keep it
2. Existing `excerpt` (<=155 chars) -> keep it
3. Generate from first meaningful sentence + topic CTA

### Topic Classification
Simple keyword scoring against 7 topic buckets: memory, partnership, awakening, enterprise, failure, relationship, roi.
Falls back to "general" if no signals match.

### Internal Link Strategy
Posts link to posts with same topic OR related topics (defined in KEYWORD_MAP).
Related Reading section uses `<hr>` + `<ul>` format, appended at end of content.

---

## Live Test Results (2026-02-18)

5 published posts fetched from purebrain.ai:
- Post 381 (enterprise): FAQ schema ADDED (1 Q&A pair), 1 internal link added
- Post 316 (memory): 1 internal link added, no FAQ detected
- Post 373 (enterprise): 1 internal link added, no FAQ detected
- Post 172 (general): Meta description generated (was missing)
- Post 98 (partnership): 1 internal link added, no FAQ detected

API connectivity: confirmed working with auth ("Aether", app password)

---

## Important Notes

- Script runs in DRY-RUN mode by default (no writes)
- Use `--apply` to write to live site (prompts for confirmation)
- Rate limit: 3 seconds between writes when applying
- The `--post-id` flag limits analysis to a single post

---

## Files Referenced

- `/home/jared/projects/AI-CIV/aether/tools/blog_seo_updater.py` (the script)
- `/home/jared/projects/AI-CIV/aether/exports/seo-update-plan.md` (dry-run report)
- `/home/jared/projects/AI-CIV/aether/tools/wordpress_publisher.py` (reference for WP API patterns)
