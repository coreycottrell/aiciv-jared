# Financial Analyst Memory: Price-Flip Unit Economics Exercise
**Date**: 2026-05-03
**Type**: teaching
**Topic**: Gross margin per container as the price-flip decision metric

## What Was Asked
Identify the single metric to measure on every active customer to determine whether PureBrain has margin headroom before flipping from launch pricing ($149/$499/$999) to scale pricing ($197/$579/$1,089).

## Key Finding
Gross Margin Per Active Container is the right metric. It is the only number that tells you whether the price increase is capturing demand surplus or covering a margin problem.

## Data Sources Confirmed Live
- `logs/purebrain_payments.jsonl` — 62 entries, real paying customers confirmed on Awakened ($74.50-$149) and Partnered ($499) as of May 2026. Most entries are sandbox/test.
- `logs/payer_emails_by_uuid.json` — maps UUID to customer email, needed to cross-reference with Hetzner containers.
- PayPal auto-split lives in `tools/paypal_auto_split.py` — $35 ops fee fires per order.
- TTS/GPU usage needs to be pulled from `37.27.237.109:8950` request logs directly.

## Critical Unresolved Input
Whether the $35 ops fee fires only at initial signup or on every monthly subscription renewal. This single variable changes the effective per-month variable cost materially.

## The Trap to Remember
Margin optimization via cost-cutting on container/TTS specs can degrade product quality and trigger churn. Always pair GM measurement with cohort retention at 30/60/90 days. Never present GM in isolation without the retention signal alongside it.

## Output File
`/home/jared/exports/portal-files/agent-training/growth/2026-05-03-financial-analyst-price-flip-metric.md`
