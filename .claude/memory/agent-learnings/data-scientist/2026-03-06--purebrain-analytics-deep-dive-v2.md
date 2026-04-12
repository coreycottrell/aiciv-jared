# Memory: purebrain.ai Analytics Deep Dive v2 — Mar 6, 2026

**Agent**: data-scientist
**Date**: 2026-03-06
**Type**: operational + teaching

---

## What Changed Since Feb 21

- Posts published: 7 → 21 (1/day cadence)
- Published pages: 9 → 50
- Confirmed real customers: 0 → 6 (Jared's manual count from spots_state.json)
- Real email subscribers: 0 → ~5 genuine (lrosanio@vsblty.net, emmanoleye@gmail.com, johnalanparis@gmail.com, johnparis51@gmail.com, sergiomanchia.urbancore@gmail.com)
- 3 new subscribers joined on Mar 6 (first meaningful subscriber day)
- Intent engine now running daily on 102 LinkedIn profiles, generating ~146 signals/day

## Key Data Sources and What They Contain

| Source | File/Endpoint | What's In It |
|--------|--------------|-------------|
| Chat sessions | logs/purebrain_web_conversations.jsonl | Session IDs, messages array, server_timestamp, client_ip |
| Payments | logs/purebrain_payments.jsonl | type, orderId, tier, amount, payerEmail, payerName, verified |
| Pay test funnel | logs/purebrain_pay_test.jsonl | Full onboarding fields: name, email, company, role, primaryGoal, aiName, flowCompleted |
| Spot tracking | logs/spots_state.json | Manual customer tracking, confirmed order IDs, real count |
| Email subscribers | Brevo API /v3/contacts | 66 total but 42 have no email; ~5 real external |
| Birth completions | logs/birth_completions.jsonl | Magic link delivery to customer |
| Intent engine | logs/intent_engine_YYYY-MM-DD.log | LinkedIn profile signals, daily run on 102 profiles |

## Analytics Access Status

- **GTM-WTDXL4VJ**: Deployed on homepage (found in full HTML). GA4 + Clarity are likely inside GTM but NOT accessible without credentials.
- **GA4**: No GOOGLE_ANALYTICS_PROPERTY_ID or credentials JSON in .env. Dashboard collecting data but unreadable programmatically.
- **GSC**: No OAuth tokens. Unreadable programmatically.
- **Clarity**: Not confirmed active (may load via GTM post-initial-HTML). No API token in .env.

**Fix**: Create GCP service account, grant GA4 Data API + GSC Webmasters access, download JSON, add `GOOGLE_ANALYTICS_CREDENTIALS_PATH` and `GA4_PROPERTY_ID` to .env.

## Known Bots/Dev IPs to Filter

- 127.0.0.1: localhost (dev testing)
- 108.35.12.204: Jared's primary dev machine
- 59.103.113.75: Pakistan bot (jailbreak spam)
- 89.167.19.20: The one confirmed real external visitor (Feb 2026)

## Brevo List IDs Reference

- [3] The Neural Feed - Blog Subscribers
- [8] PureBrain Customers
- [4] Enterprise Leads
- [10] High Intent
- [9] Assessment Completions
- [20] Investor Brief Requests
- [11] PureBrain Migration Leads
- [12-18] PureBrain Migration by AI tool (ChatGPT, Claude, Gemini, etc.)

## Top Recommendations for Future Analysis

1. Set up GA4 API first — unlocks everything
2. Debug Brevo list assignment — contacts exist but 0 in any list
3. Add email capture to homepage + chatbot exit
4. Noindex test/internal pages (/pay-test-*, /homepage-backup, /video-test, /team-dashboard, /client report pages)
5. Fix duplicate pages (two /refer variants, two DuckDive report URLs)

## Report Location

`/home/jared/projects/AI-CIV/aether/exports/analytics-deep-dive-2026-03-06.md`
