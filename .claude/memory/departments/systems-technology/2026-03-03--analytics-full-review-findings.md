# Analytics Full Review — purebrain.ai
**Date**: 2026-03-03
**Type**: synthesis + gotcha + data-state
**Topic**: Full analytics audit across GA4, GSC, Clarity — auth walls, first-party data, findings

---

## Auth Wall Reality (PERMANENT GOTCHA)

All three analytics platforms require interactive OAuth. Cannot bypass headlessly:
- GA4 (`analytics.google.com`) → redirects to `accounts.google.com/v3/signin`
- GSC (`search.google.com/search-console`) → same Google OAuth wall
- Clarity (`clarity.microsoft.com`) → Microsoft OAuth wall
- SEMRush login is ALSO broken headlessly now (cookie/bot detection improved since Feb 23)

**Solution**: Jared must grant purebrain@puremarketing.ai co-owner access to all three platforms.
- Clarity: Settings → Users → add email as co-owner (5 min)
- GA4: Admin → Account Access → add email as Editor (10 min)
- GSC: Settings → Users and permissions → add as Owner (5 min)

---

## Data Points Confirmed (Mar 3, 2026)

### Tracking Infrastructure
- GTM-WTDXL4VJ: Active on all pages
- GA4 G-86325WBT3P: Active via GTM, collecting since ~Feb 10
- Clarity viy9bnc56x: Active via GTM (confirmed in GTM container JS)
- Hotjar: In GTM container but no account ID configured
- Facebook Pixel: Not installed

### Site Performance (Direct Test)
- Homepage (purebrain.ai/): 0.19s, 467KB
- Blog posts: 0.18s, ~230KB
- ai-adoption-review: 0.75s, 175KB
- invitation page: 1.27s, 197KB (SLOWEST — conversion page)

### First-Party Traffic (Conversation Logs)
- 278 total conversation events
- 106 unique session IDs
- 5 external IPs seen
- Key external IP: 59.103.113.75 — 51 sessions Feb 12-16 (unknown person, highly engaged)
- Jared IP (108.35.12.204): 75 sessions

### Content Inventory
- 16 blog posts in sitemap (all with schema, OG image)
- 38 pages in sitemap (homepage + 37 subpages)
- One SEO gap: /your-ai-doesnt-work-for-you/ missing meta description

### Email/Brevo
- 40 contacts total, 7 with real emails, 2 genuinely external
- 1 real Neural Feed subscriber: emmanoleye@gmail.com (Mar 1)
- Neural Feed campaigns: 7 sent, 0 delivered (no real subscribers in automation)
- Transactional email: 30 sent, 19 delivered, 15 unique opens (all test accounts)

### Payments
- 0 real payment completions
- All 10 payment webhook events are sandbox/test
- Pay-test: 72 completions, all from internal testing (Mar 2 E2E tests)

### SEMRush Baseline (Feb 23 — last confirmed login)
- Authority Score: 0 (brand new domain)
- Organic traffic: ~0
- Backlinks: 10 total, 1 referring domain
- Keywords tracked: 10, avg position 97.3
- Site health: 83%

---

## Key Insights for Future Reference

1. IP 59.103.113.75 is a power user — 51 sessions Feb 12-16. Check Clarity recordings for this IP when access granted.

2. The comparison pages (/purebrain-vs-chatgpt/, /vs-claude/, etc.) are SEO sleeper weapons — 8 pages in sitemap targeting commercial-intent queries.

3. Homepage at 467KB is significantly heavier than other pages. The GIF background video (Pure-Brain-Vid-3.gif) is likely the culprit. Monitor with Clarity.

4. GA4 has zero conversion events configured — only page views. Need 5 GTM events: chatbox_opened, name_captured, email_captured, onboarding_complete, pricing_page_view.

5. Neural Feed email list growth is the most important business metric to move right now. 1 external subscriber after 22 days.

---

## Report Location
`/home/jared/projects/AI-CIV/aether/exports/overnight-reports/analytics-review-2026-03-04.md`
Screenshots: `/home/jared/projects/AI-CIV/aether/exports/screenshots/analytics_2026_03_04/`
