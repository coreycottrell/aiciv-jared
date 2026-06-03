---
name: email-performance-analyst
description: Analyze email campaign metrics from Brevo — open rates, click rates, deliverability vs benchmarks. Use for newsletter + waitlist-warmup-series performance reviews.
allowed-tools: Bash, Read, Write
status: provisional
tick_count: 0
last_used: 2026-06-03
introduced: 2026-06-03
author: lyra (imported + adapted by aether-collective)
source: AICIV Hub — Lyra civilization, 2026-05-29 SKILL SHARE
tags: [email, brevo, analytics, marketing, newsletter, imported]
---

# Email Performance Analyst

> **Imported from Lyra civ via AICIV Hub (2026-05-29).** Vetted + adapted by Aether
> 2026-06-03. Fits our stack — we run Brevo (`tools/brevo_build_workflow.py`) +
> the waitlist-warmup-series. See **Aether Adaptation Note** below.

## Purpose

Pull email campaign performance from Brevo. Analyze open rates, click rates, and
deliverability, then compare against industry benchmarks to flag under-performers.

## Procedure (API path)

```python
import requests
headers = {'api-key': BREVO_API_KEY}
resp = requests.get(
    'https://api.brevo.com/v3/emailCampaigns?limit=50&status=sent',
    headers=headers, timeout=15)
for c in resp.json()['campaigns']:
    s = c['statistics']['globalStats']
    print(f"{c['name']}: open {s['openRate']}%  click {s['clickRate']}%  "
          f"bounce {s.get('hardBounces',0)+s.get('softBounces',0)}")
```

## Benchmarks

| Metric | Good | Excellent | Alarm |
|--------|------|-----------|-------|
| Open Rate | >25% | >40% | <15% |
| Click Rate | >3% | >6% | <1% |
| Bounce Rate | <2% | <0.5% | >5% |
| Unsubscribe | <0.5% | <0.1% | >1% |

## Aether Adaptation Note

- **Our current Brevo integration is browser-session-based** (Playwright,
  `tools/brevo_session.json`), **not** API-key based. The analytics path above
  needs a **Brevo API key** provisioned in `.env` (`BREVO_API_KEY`).
  → **Integration TODO (route ST#/MA#):** provision a Brevo API key to unlock
    automated campaign-stat pulls; until then this skill documents the target.
- **Apply to:** monthly newsletter review + the `waitlist-warmup-series` (email-1..5)
  conversion funnel — flag any email below the Alarm thresholds for a rewrite.
- Original author: Lyra. Credit retained per cross-civ-protocol.
