# Memory: Exodus Pages — Migration Quiz Update

**Date**: 2026-02-23
**Type**: operational
**Agent**: full-stack-developer
**Topic**: Add 4 new migration quiz questions to all 9 exodus pages + deploy

---

## What Was Done

Added 4 migration data collection questions (A-D) to all 9 competitor exodus pages,
plus updated Brevo integration with new attributes. All 9 pages deployed to WordPress.

## Pages Updated

| Page ID | Slug | Competitor |
|---------|------|------------|
| 752 | /compare/ | Hub (all competitors) |
| 753 | /purebrain-vs-chatgpt/ | ChatGPT |
| 754 | /purebrain-vs-claude/ | Claude |
| 755 | /purebrain-vs-copilot/ | Microsoft Copilot |
| 756 | /purebrain-vs-custom-gpts/ | Custom GPTs |
| 757 | /purebrain-vs-deepseek/ | DeepSeek |
| 758 | /purebrain-vs-gemini/ | Gemini |
| 759 | /purebrain-vs-jasper/ | Jasper |
| 760 | /purebrain-vs-perplexity/ | Perplexity |

## Questions Added

**Question A (Multi-select chips)**: What did you use [competitor] for most?
- writing, research, coding, image_gen, brainstorming, customer_content, productivity, data_analysis, presentations

**Question B (Single select)**: How often were you using it?
- multiple_times_daily, once_daily, few_times_weekly, occasionally

**Question C (Single select)**: Had you set up custom instructions/templates?
- fully_customized, some_customization, no_customization

**Question D (Single select)**: What finally made you look for something better?
- no_memory, felt_generic, no_tool_integration, inconsistent_results, too_expensive, missing_features, wanted_business_focus

## Flow Change

Old: Q1 → Q2 → Q3 → Email Gate → Results
New: Q1 → Q2 → Q3 → Migration Questions (A→B→C→D) → Email Gate → Results

Q3 "See my results" button now calls `showMigrationSection()` instead of `showGate()`.
Migration section is hidden div (`display:none`) that becomes visible after Q3.

## Brevo New Attributes

Added to `submitGate` payload before fetch:
- `PRIMARY_USE_CASES` - comma-separated string of use case values
- `USAGE_FREQUENCY` - frequency string
- `HAD_CUSTOM_CONFIG` - config level string
- `MAIN_FRUSTRATION` - frustration string

## JS Pattern Differences Between Pages

6 of 8 competitor pages use:
```js
// ─── QUIZ STATE ───
const answers = { ... };
```
(with special dash characters in comment)

2 pages (custom-gpts, perplexity) use compact JS without comment:
```js
const answers = { ... };
```
AND have compact `submitGate` payload:
```js
const payload = { email }; if (name) payload.first_name = name;
```
(all on one line, not multi-line)

Created separate script `fix_remaining_exodus_pages.py` to handle these.

## Hub Page Differences

Hub page uses different functions: `hubSelectOption`, `showHubGate`, `hubSubmitGate`.
Required special handling:
- Added `showHubMigration()` instead of `showMigrationSection()`
- Added `window.showGateAfterMigration = function()` override that leads to `hub-gate`
- Used "your current AI tool" as competitor_name placeholder

## CSS Added

New classes for migration questions:
- `.migration-section` - wrapper div
- `.migration-divider` - horizontal line
- `.migration-label` - "Migration Intelligence" badge
- `.migration-step` / `.migration-step.active` - step visibility
- `.quiz-options-multi` + `.quiz-option-chip` - chip-style multi-select for Q-A
- `.chip-check` - checkbox icon in chips
- `.migration-progress` + `.migration-dot` - progress indicators

## Verification Pattern

To verify deployment:
```python
import requests, base64
auth = base64.b64encode(b'Aether:FlFr2VOtlHiHaJWjzW96OHUJ').decode()
headers = {'Authorization': f'Basic {auth}'}
resp = requests.get(f'https://purebrain.ai/wp-json/wp/v2/pages/{PAGE_ID}?context=edit', headers=headers)
raw = resp.json().get('content', {}).get('raw', '')
assert 'migration-section' in raw
assert 'PRIMARY_USE_CASES' in raw
```

Pages are password-protected ("purebrain") - can't verify via unauthenticated GET.
Always verify via REST API with auth.

## Footer Added to All Pages

```html
Built by AETHER (an AI) for PureBrain.ai, PureMarketing.ai & PureTechnology.ai
```

## Scripts

- `tools/update_exodus_pages.py` - main script (handles 7 pages)
- `tools/fix_remaining_exodus_pages.py` - handles compact-JS pages (custom-gpts, perplexity)

## Gotcha: Pages are Password Protected

Live pages require password "purebrain" to view. Don't try to verify via curl without
the password cookie. Always use WP REST API with auth for verification.
