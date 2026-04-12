# Analytics Infrastructure Audit — PureBrain.ai
**Date**: 2026-02-28
**Agent**: dept-systems-technology
**Type**: systems audit

## What Is Installed

- GTM: GTM-WTDXL4VJ (confirmed active, fires on all pages)
- GA4: G-86325WBT3P (found inside GTM container — collecting data)
- Independent Analytics (IAWP) plugin: Active in WordPress
- Yoast SEO v27.0: Active, schema markup, canonical URLs configured
- Brevo: Connected, 30 contacts, 5 campaigns sent

## What Is NOT Installed

- Microsoft Clarity: NOT found in page source. High priority to install.
- Hotjar: Not installed
- Facebook Pixel: Not installed

## API Access Reality

- GA4 Data API: Requires OAuth2 service account. API key does NOT work. Need Jared to create service account in Google Cloud Console.
- GSC API: Same — requires OAuth2. Same service account setup works for both.
- Brevo: Full API access via BREVO_API_KEY in .env. Works.
- WordPress: Full access via PUREBRAIN_WP_APP_PASSWORD + PUREBRAIN_WP_USER in .env.

## Key Data Points Found

- Chatbox sessions: 745 total (Feb 10-28)
- External unique visitors (non-Jared, non-internal): 4 IPs, 91 sessions
- Most engaged external visitor: 59.103.113.75 — 51 sessions, 59% onboarding rate, max 13 turns
- Avg user turns per chatbox session: 4.8 (industry avg: 2-3) — strong signal
- Brevo contacts: 30 total (~3 real, rest test/internal)
- Transactional email: 59% unique open rate (industry avg: 35-40%)
- Payment events: 17 test, 1 potentially real ($197, Feb 23, unverified)

## Conversion Funnel Gaps

No GA4 conversion events configured. No way to measure visitor-to-chatbox, chatbox-to-onboarding, onboarding-to-payment rates from GA4 yet.

## Top Priority Actions

1. Jared creates Microsoft Clarity account — we install in 10 min via GTM
2. Jared creates GA4 service account — unlocks programmatic reporting
3. Investigate $197 Feb 23 payment in PayPal dashboard
4. Fix Brevo list assignments for 30 contacts
5. Configure GA4 conversion events via GTM
