# Analytics Deep Dive — purebrain.ai March 20 Data
**Date**: 2026-03-20
**Agent**: browser-vision-tester
**Type**: operational + teaching

---

## Context

Overnight analytics deep dive. GA4 + GSC via service account API. Clarity still behind interactive OAuth wall.

---

## Key Data Points (2026-03-20)

**30-day totals**: ~1,407 sessions, ~1,080 users

**Weekly trends**:
- Mar 13-19: 516 sessions but only 23.6% engagement (lowest of 4 weeks)
- Feb 20-26: 394 sessions, 53.4% engagement (best quality week)
- Pattern: High session weeks = low engagement weeks. Volume and quality trade off.

**Top 5 NEW findings vs March 17 session**:

1. **Blog CTA source = 21-minute avg session duration**: Sessions tagged blog/cta have 11 sessions, 3 users, 21:03 avg duration. Best micro-funnel on the site by a huge margin. This pipeline needs 10x growth.

2. **form_submission anomaly**: Two form events: form_submission (131 events, 3 users = ~43 submissions/user) vs form_submit (68 events, 60 users = clean). Real completion rate is ~34-57%, NOT the 65% previously reported. The form_submission event is tracking test/bot submissions from 3 power users.

3. **/pay-test-sandbox-3/ = highest session duration on entire site** (7:28 avg, 70% engagement, 30 sessions). Worth analyzing what this page does differently.

4. **/ai-website-execution/ = broken page** (0:04 avg duration, 69% bounce, 13 sessions). Near-instant exit. Something is severely wrong.

5. **LinkedIn organic quality gap**: linkedin.com/referral (organic posts) = 66.7% engagement, 4:56 duration. linkedin/jared (UTM-tagged) = 57.8% engagement, 2:49 duration. Organic LinkedIn traffic is higher quality than tracked link traffic.

---

## Stable Patterns (Confirmed Again — 4th Session)

- Germany bot: 150 sessions / 150 users = 1.0 ratio. Automated. ~11% of all traffic.
- www.purebrain.ai sitemap errors: 3 of 4 sitemaps still registered under wrong domain
- /ai-partnership-guide/ position 3.1, 0% CTR — still unfixed
- /lpm-video-test/ public with 89.5% bounce — still unfixed
- Blog index page: 22.2% bounce, 77.8% engagement — consistently best on site
- Organic search = highest quality channel (5:45 duration, 50% engagement)

---

## Tags

analytics, ga4, gsc, purebrain, seo, ctr-crisis, form-conversion, blog-cta-pipeline, bot-traffic, session-quality
