# Analytics Deep Dive - PureBrain.ai
**Date**: 2026-04-07
**Type**: operational
**Agent**: dept-systems-technology

## Key Findings

### Credentials Status
- CF API Token ([REDACTED-2026-05-09-LEAK-CFUT]...) is ACTIVE but lacks `analytics.read` permission
- No GA4 API credentials in .env
- No Clarity API credentials in .env
- No Search Console API credentials in .env
- GA4 Measurement ID: G-86325WBT3P (found in GTM container GTM-WTDXL4VJ)
- Clarity Project ID: viy9bnc56x (confirmed in page source)

### Infrastructure Facts
- purebrain.ai hosted on CF Pages (purebrain-staging.pages.dev)
- CF Zone ID: 49400cad1527af716705f6cb8c22bb65
- 28 DNS records, CF Free plan
- Google site verification active (2 TXT records)
- Argo tunnel handles app/portal/services: 244196cb-a1ab-45ae-9732-788179e2a55f

### Issues Found
- 3 subdomains returning 530: 777, cal, social
- api.purebrain.ai returns 404
- Homepage has 3 duplicate viewport meta tags
- sitemap.xml returns 403
- OG image is a GIF (poor social sharing)
- No font-display: swap, no font preloading

### Blog Stats
- 10 published posts, avg 2,495 words, strong SEO metadata
- All have proper H1/H2 structure, canonical URLs, meta descriptions

## File Paths
- Report: /home/jared/exports/portal-files/analytics-deep-dive-2026-04-07.md
