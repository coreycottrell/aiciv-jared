# Sales Wizard Pricing Fix — CTO Investigation

**Date**: 2026-03-05
**Agent**: cto
**Type**: operational
**Topic**: Sales wizard pricing numbers stale vs calculator source of truth

---

## Issue

Sales Call Wizard page (https://purebrain.ai/sales-playbook/live-call/, WP page ID 1283)
showed incorrect Claude costs and total spend in the "Pricing to Share" section:

| Tier | Wrong Claude Cost | Wrong Total |
|------|------------------|-------------|
| Awakened ($149) | ~$20/mo | ~$169/mo |
| Bonded ($499) | ~$60/mo | ~$559/mo |
| Partnered ($999) | ~$100/mo | ~$1,099/mo |

## Root Cause

The pricing was hand-estimated, not pulled from the calculator's source of truth.
The calculator (ai-tool-stack-calculator-v4.html, WP page 777) uses Claude Max subscription
pricing: "$100/mo for Awakened & Bonded, $200/mo for Partnered & Unified".

## Correct Values (Source: calculator TIERS array)

| Tier | Base Price | Claude Max | Total Display |
|------|-----------|------------|---------------|
| Awakened | $149/mo | $100/mo | $249/mo |
| Bonded | $499/mo | $200/mo | $699/mo |
| Partnered | $999/mo | $200/mo | $1,199/mo |
| Unified | Custom | volume pricing | Contact for quote |

Note: The sales wizard uses a 4-tier naming (Awakened/Bonded/Partnered/Unified)
that maps to the calculator's internal tier IDs. The calculator's tier NAMES changed
(3-tier vs 4-tier at various points) but the PRICES in the sales wizard at the time
of this fix were: Awakened=$149, Bonded=$499, Partnered=$999, which matches the
calculator's bonded/partnered/unified tiers respectively.

## Fix Deployed

Deployment script: `/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/fix_and_deploy.py`
Local HTML: `/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/index.html`
WP Page ID: 1283
WP Slug: live-call
Parent: 1278 (Sales Playbook)

Script does 6 string replacements, verifies all old values removed + new values present,
writes local file, then POSTs to WP REST API pages/1283.

## Key Files

- `/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/index.html` — local source
- `/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/fix_and_deploy.py` — fix + deploy script
- `/home/jared/projects/AI-CIV/aether/exports/sales-call-wizard/wp_deploy.py` — original deploy (creates new page)
- `/home/jared/projects/AI-CIV/aether/exports/calculator-pricing-audit-2026-03-03.md` — prior pricing audit

## Pattern: Single Source of Truth for Pricing

ANY page that shows Claude costs or tier pricing should pull from or reference
the calculator TIERS array values. Never hand-estimate. The calculator was the
deliberate source of truth established by the team.

Future changes to Claude Max pricing should update the calculator first, then
cascade to all pages (sales wizard, invitation page, comparison pages).
