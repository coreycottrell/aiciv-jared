# Memory: Add #awakening Fragment to CTA Links
**Date**: 2026-02-19
**Type**: operational
**Topic**: Adding #awakening hash fragment to all "Start Your AI Partnership" CTA links across both WordPress sites

## Task
Jared updated purebrain.ai to add an `#awakening` section anchor. All blog CTA buttons need to
deep-link to that anchor. Task: append `#awakening` at the end of ALL existing CTA URLs (after UTM params).

## Result
- purebrain.ai: 6/6 posts updated and verified (IDs: 480, 381, 316, 373, 172, 98)
- jareddsanborn.com: 2/7 posts updated and verified (IDs: 1069, 1060)
- 0 errors, all 8 changes individually verified by re-fetching post content
- Newsletter/blog links correctly left untouched

## Script Location
`/home/jared/projects/AI-CIV/aether/tools/add_awakening_fragment.py`

## Report Location
`/home/jared/projects/AI-CIV/aether/exports/cta-awakening-fix-report.json`

## URL Transform Pattern
```
BEFORE: https://purebrain.ai/?utm_source=blog&utm_medium=cta&utm_campaign=ai_partnership&utm_content={slug}
AFTER:  https://purebrain.ai/?utm_source=blog&utm_medium=cta&utm_campaign=ai_partnership&utm_content={slug}#awakening
```

## Key Technical Decisions

### CTA Link Detection (surgical, not regex-only)
- Check href is to purebrain.ai root (not a subpage path)
- Use SUBPAGE_PATTERN to exclude /blog/, /purebrain-4/, etc.
- Check 300-char context window around href for CTA text signals:
  - "Start Your AI Partnership", "blog-cta-block", "blog-cta-button"
- Exclude safe patterns: /blog, subscribe, /newsletter, social media domains

### Fragment Placement Rule (critical)
- `#awakening` goes at the VERY END, after all query params
- `https://purebrain.ai/?utm_source=blog&...&utm_content=slug#awakening`
- NOT: `https://purebrain.ai/#awakening?utm_source=blog...` (broken)

### Idempotency
- Skip links that already contain `#awakening`
- Safe to re-run without double-adding

### Bonus Discovery
- jareddsanborn.com post 1060 had a CTA with different UTM campaign (`enterprise-ready` instead of `ai_partnership`) — it was correctly caught and updated because CTA detection uses context text signals, not URL pattern matching alone.

## Auth Pattern (confirmed working)
```python
auth = ("Aether", os.getenv("PUREBRAIN_WP_APP_PASSWORD").strip("'"))  # purebrain.ai
auth = ("jared", os.getenv("WORDPRESS_APP_PASSWORD").strip("'"))       # jareddsanborn.com
```

## Prior Related Work
- 2026-02-18: Initial CTA standardization to "Start Your AI Partnership"
- 2026-02-19 (earlier today): Fixed /purebrain-4/ test-page links to use homepage URL
- This is the 3rd CTA link update — pattern is now mature and script-driven
