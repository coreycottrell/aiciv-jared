# Calculator Nuclear Color Defense - Page 777

**Date**: 2026-02-24
**Type**: technique
**Agent**: full-stack-developer

## What Was Done

Replaced the ineffective magic cursor override rule on the AI Tool Stack Calculator (WP page 777) with a full nuclear defense CSS block.

## The Problem

The WordPress `tt-magic-cursor` theme effect was cascading `color: inherit` down to all elements, overriding custom colors set via CSS variables. The old fix used a single `:not()` exclusion rule but it had too many gaps - logo blue spans, category header names, tool names, and other elements were being poisoned orange.

## The Solution

Two-part nuclear defense:

**1. 100+ hardcoded `body.page-id-777 .class { color: #hex !important; }` rules**
- Covers every meaningful text element in the calculator
- Uses literal hex values (not CSS variables) so nothing can cascade over them
- Specificity: `body.page-id-777` + class = very high, plus `!important` = unbeatable

**2. Kept the old `:not()` rule as a fallback** but expanded its exclusion list to include all the previously-missed elements.

## Elements Covered

- Logo: `.calc-logo span.blue` (#2a93c1), `.orange` (#f1420b), `.white` (#ffffff)
- Hero h1, p, stats, eyebrows
- Search input, placeholder, icons
- Preset buttons
- Category headers: title, count, selected, subtotal, chevron, ctrl-btn
- Tool cards: name, desc, price (including `--on` and `--free` states)
- Sidebar panel: header, labels, amounts
- Savings bar, tier recommendation, savings summary
- Share button, sticky bar, tool count bar
- Selected items list, grand total table, tier cards
- Bottom bar, personal chatbox, share modal
- Zero/empty states, Claude note

## Key Pattern

When WordPress theme CSS is poisoning colors on a self-contained HTML widget:
1. Don't fight theme specificity - go nuclear with page-specific overrides
2. Use `body.page-id-{N}` prefix + `!important` on every color declaration
3. Use hardcoded hex values, not CSS variables (variables can be overridden too)
4. Cover ALL text elements - even ones that seem stable today

## File Modified

`/home/jared/projects/AI-CIV/aether/exports/ai-tool-stack-calculator-v3.html`

Lines 1654-1830 (approximate) - CSS section replaced.

## Deployment

WP page 777 via REST API `POST /wp-json/wp/v2/pages/777`
Content wrapped in `<!-- wp:html -->` block per WP HTML deployment rule.
Deployed: 2026-02-24T00:02:47
Live at: https://purebrain.ai/ai-tool-stack-calculator/

## Verification

- HTTP 200 from WP REST API
- `curl` live page confirmed: "NUCLEAR DEFENSE" comment present
- 100 `body.page-id-777` rules confirmed live
