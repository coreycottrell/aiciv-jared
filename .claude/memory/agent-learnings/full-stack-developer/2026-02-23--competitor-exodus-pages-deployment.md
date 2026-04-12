# Memory: Competitor Exodus Pages Deployment

**Date**: 2026-02-23
**Type**: operational
**Agent**: full-stack-developer
**Topic**: Deploy 9 self-contained HTML competitor comparison pages + footer injection

---

## What Was Done

Deployed 9 competitor exodus comparison pages to purebrain.ai using WordPress REST API.
Then injected comparison footer strip into 5 Elementor pages.

## Page IDs Created

| Slug | ID | Title |
|------|-----|-------|
| /compare/ | 752 | Compare AI Tools to PureBrain (hub) |
| /purebrain-vs-chatgpt/ | 753 | PureBrain vs ChatGPT |
| /purebrain-vs-claude/ | 754 | PureBrain vs Claude |
| /purebrain-vs-copilot/ | 755 | PureBrain vs Microsoft Copilot |
| /purebrain-vs-custom-gpts/ | 756 | PureBrain vs Custom GPTs |
| /purebrain-vs-deepseek/ | 757 | PureBrain vs DeepSeek |
| /purebrain-vs-gemini/ | 758 | PureBrain vs Gemini |
| /purebrain-vs-jasper/ | 759 | PureBrain vs Jasper |
| /purebrain-vs-perplexity/ | 760 | PureBrain vs Perplexity |

All pages: `template=elementor_canvas`, `status=publish`, `password=purebrain`

## Deployment Pattern for Self-Contained HTML

1. Read HTML file from exports/
2. Fix any cross-links/placeholders
3. Inject back-links (See All Comparisons) before `</body>`
4. Wrap entire content in `<!-- wp:html -->..<!-- /wp:html -->` block
5. POST to `/wp-json/wp/v2/pages` with elementor_canvas template
6. Clear Elementor cache after batch

## Cross-Link Fixes in Hub Page

Hub had old JS data with `/switching-from-*` URLs. Replaced:
- `/switching-from-chatgpt` → `/purebrain-vs-chatgpt/`
- `/switching-from-copilot` → `/purebrain-vs-copilot/`
- `/switching-from-gemini` → `/purebrain-vs-gemini/`
- `/switching-from-claude` → `/purebrain-vs-claude/`
- `/switching-from-deepseek` → `/purebrain-vs-deepseek/`
- `/switching-from-perplexity` → `/purebrain-vs-perplexity/`
- `/switching-from-jasper` → `/purebrain-vs-jasper/`
- `/switching-from-custom-gpts` → `/purebrain-vs-custom-gpts/`

## Elementor Footer Injection Pattern

For Elementor pages, inject by:
1. GET page with `context=edit` to get `_elementor_data` JSON
2. Parse the JSON array
3. Append a new section object with html widget containing the footer HTML
4. POST back with `meta._elementor_data` = re-serialized JSON
5. Clear Elementor cache

DO NOT use `content` field for Elementor pages - changes won't render.

## Gotcha: Password-Protected Pages Hide Content

When checking deployed pages via HTTP GET (no auth), password-protected pages
show only the WordPress password form. The content IS there - verify by:
- Fetching via REST API with auth: `GET /wp-json/wp/v2/pages/{id}?context=edit`
- Check `content.raw` for the actual content

## Script Location

`/home/jared/projects/AI-CIV/aether/tools/deploy_competitor_pages.py`
Reusable for future competitor page deployments.
