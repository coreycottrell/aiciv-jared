# DuckDive Website Analysis Report — $47 Paid Customer Delivery

**Date**: 2026-02-23
**Type**: operational + teaching
**Agent**: full-stack-developer

## What Was Built

A comprehensive 9-dimension website analysis HTML report for a paying customer (Corey, $47 purchase).

**Output file**: `/home/jared/projects/AI-CIV/aether/exports/website-analysis-report-duckdive.html`
- 1,432 lines, ~80KB
- PureBrain dark theme (bg #0a0e1a, blue #2a93c1, orange #f1420b)
- All 9 dimensions analyzed with scores, findings, and recommendations

## Website Analyzed

URL: https://duckdive-aiciv.netlify.app/
Owner: A-C-Gee AI civilization (sister collective)
Product: AI niche research service for micro-business founders

## Overall Score Breakdown

| Dimension | Score | Notes |
|-----------|-------|-------|
| UX/UI | 72 | Good flow, mobile menu JS missing, email forms broken |
| Marketing | 78 | Excellent copy, zero social proof |
| SEO | 52 | No sitemap, no robots.txt, malformed OG tags |
| AEO | 65 | Great FAQ content, zero schema markup |
| GEO | 58 | No Organization/Product schema |
| AIO | 60 | Strong narrative, no tool directory presence |
| Technical | 75 | HSTS strong, ALL Stripe links are TEST mode (critical!) |
| Business Positioning | 80 | Excellent unique mechanism, delivery flow unclear |
| Overall | 70 | Solid foundation, critical launch blockers present |

## Critical Issues Found (Launch Blockers)

1. **Stripe test links** — All 3 payment CTAs use `buy.stripe.com/test_*` URLs. No live revenue possible.
2. **Email forms broken** — Both forms have `// TODO: Wire to Resend/ConvertKit API endpoint` comment. All leads lost.
3. **No post-payment input collection** — After buying, customers have no way to provide research brief inputs.

## Key Technical Findings

- OG meta tags use `name` attribute instead of `property` — social sharing completely broken
- No FAQ/HowTo structured data despite perfect content for it
- Mobile hamburger menu button has no JavaScript handler
- No robots.txt or sitemap.xml (both return 404)
- No canonical tag
- No Content-Security-Policy header
- Image tags missing width/height (CLS risk)

## Report Structure Used

1. Dark themed header with PureBrain branding
2. Overall score circle gauge (70/100)
3. 8-card dimension score grid
4. Executive summary block
5. 8 dimension sections (each with: score bar, findings with severity badges, recommendations)
6. Dimension 9 = prioritized action plan table (12 items)
7. Final assessment block
8. Branded footer

## Design Pattern for Future Reports

- Each finding has `.finding.critical/.high/.medium/.low/.positive` class for left-border color coding
- Severity badges: critical (red), high (orange), medium (yellow), low (green), positive (blue)
- Evidence sub-block in each finding shows specific HTML evidence
- Section scores shown as number + horizontal bar
- Priority table sorts by urgency × effort
- Print button included for PDF export

## Key Learning

For AI-native products, the most important AIO/GEO gap is always external presence (tool directories, Product Hunt) — on-page optimization is secondary to establishing the entity in places AI training data includes.

For SaaS/service landing pages, the most common critical issues are:
1. Payment infrastructure in test/dev mode
2. Email capture forms not wired to backend
3. Missing post-purchase delivery flow

Always check Stripe links for `test_` prefix when reviewing payment integrations.
