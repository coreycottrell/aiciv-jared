# Memory: Comparison Page Pricing Audit

**Date**: 2026-03-02
**Type**: operational
**Topic**: Audited and fixed PureBrain pricing on all comparison pages

---

## Current PureBrain Pricing (Source of Truth)

From main page (page ID: 11, slug: pure-brain-agentic-ai-partner):
- **Awakened**: $79/mo (DO NOT show on comparison pages)
- **Bonded**: $149/mo
- **Partnered**: $499/mo
- **Unified**: $999/mo

## Rules

- Never show $79 Awakened tier on comparison pages
- Never change competitor pricing
- Only change PureBrain pricing columns

## Pages Audited (13 total)

| Page ID | Slug | Pricing Found | Action |
|---------|------|---------------|--------|
| 1044 | purebrain-vs-sitegpt | PureBrain prices (old) | FIXED |
| 1190 | purebrain-vs-glbgpt | PureBrain prices (old) | FIXED |
| 970 | cost-comparison | Cost comparison (no tier pricing) | Skip |
| 794 | why-purebrain | No pricing | Skip |
| 760 | purebrain-vs-perplexity | No pricing | Skip |
| 759 | purebrain-vs-jasper | No pricing | Skip |
| 758 | purebrain-vs-gemini | No pricing | Skip |
| 757 | purebrain-vs-deepseek | No pricing | Skip |
| 756 | purebrain-vs-custom-gpts | No pricing | Skip |
| 755 | purebrain-vs-copilot | $30 = Copilot only | Skip |
| 754 | purebrain-vs-claude | No pricing | Skip |
| 753 | purebrain-vs-chatgpt | No pricing | Skip |
| 752 | compare (hub) | $5 = competitor only | Skip |

## Changes Made to Page 1044 (purebrain-vs-sitegpt)

Old pricing used: "Awakened $179/mo, range $179–$1,999/mo" (old product tier structure)
New pricing: "Bonded $149/mo, range $149–$999/mo"

1. Schema description: `$179/mo` → `$149/mo`
2. Hero card range: `$179 – $1,999/mo` → `$149 – $999/mo`
3. "PureBrain starts at $179/mo" → `$149/mo`
4. "more expensive at $179/mo minimum" → `$149/mo`
5. Table column header: `PureBrain Awakened` → `PureBrain Bonded`
6. Table Monthly Price (PureBrain col): `$179/mo` → `$149/mo`
7. Verdict text: `Awakened tier/$179/mo/$15 per function` → `Bonded tier/$149/mo/~$12 per function`
8. Table cost-per-function cell: `~$15` → `~$12`

## Changes Made to Page 1190 (purebrain-vs-glbgpt)

Old pricing: Awakened=$97, Bonded=$297, Partnered=$997 (completely wrong old structure)
New pricing: Bonded=$149, Partnered=$499, Unified=$999

1. Hero card: `From $97<span>/month</span>` → `From $149<span>/month</span>`
2. Compare strip: `From $97/mo` → `From $149/mo`
3. Feature table entry price: `$97/mo Awakened` → `$149/mo Bonded`
4. Tier renames (in order to avoid naming conflicts): Partnered→Unified($999), Bonded→Partnered($499), Awakened→Bonded($149)

## API Pattern for Verification

```python
r = requests.get(f'https://purebrain.ai/wp-json/wp/v2/pages/{page_id}?context=edit', auth=auth)
content = r.json()['content']['raw']
prices = re.findall(r'\$[\d,]+(?:/mo(?:nth)?)?', content)
```

## Cache Clear

```python
requests.delete('https://purebrain.ai/wp-json/elementor/v1/cache', auth=auth)
```

## Important Gotcha

When renaming tiers on a page that has Awakened→Bonded→Partnered chain:
- Rename from bottom up (Partnered→Unified first, then Bonded→Partnered, then Awakened→Bonded)
- Prevents naming collisions from sequential string replacement
