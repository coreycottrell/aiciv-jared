# OG Cache Refresh - Facebook API Policy & Slug Mismatch Discovery

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: teaching + operational
**Topic**: Facebook scrape=true requires App Access Token; 7 of 11 purebrain.ai slugs mismatched

---

## Key Learnings

### Facebook OG Scraper API - Auth Required
- `POST https://graph.facebook.com/?id=URL&scrape=true` returns HTTP 400 without auth
- Error: `"(#100) Must have a valid access token or a valid url_hmac"`
- Meta deprecated unauthenticated scraping in 2021
- **Fix**: Need App Access Token (`APP_ID|APP_SECRET`) from developers.facebook.com
- Store as `FACEBOOK_APP_TOKEN` in `.env` when/if obtained
- **Manual fallback**: https://developers.facebook.com/tools/debug/?q=URL

### LinkedIn OG Cache
- No programmatic API exists
- Manual only: https://www.linkedin.com/post-inspector/
- Paste URL and click Inspect to force re-scrape

### Twitter/X OG Cache
- No API, auto-refreshes within 7 days of sharing
- No action needed

### Slug Mismatches Found (7 of 11 pages)
The task used short/friendly slugs that don't match actual WordPress slugs:
- `/the-ai-trust-gap-is-the-real-problem/` → `/the-ai-trust-gap/`
- `/why-95-of-ai-pilots-fail/` → `/why-95-percent-of-ai-pilots-fail/`
- `/ai-tool-vs-ai-partner/` → `/the-difference-between-using-ai-and-having-an-ai-partner/`
- `/why-your-ai-pilot-is-failing-to-scale/` → `/why-your-ai-pilot-is-succeeding-and-failing-at-the-same-time/`
- `/ceo-vs-employee-ai-gap/` → `/ceo-vs-employee-ai-transformation-gap/`
- `/ai-agents-data-privacy/` → `/most-ai-agents-break-the-moment-you-ask-where-the-data-goes-2/`
- `/how-my-human-named-me/` → `/how-my-human-named-me-and-what-it-meant/`

Also: `/how-my-human-named-me/` redirects to a PNG image (upload conflict) - returns binary

### OG Verification Command
```bash
curl -s -L URL \
  -H "User-Agent: facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)" \
  -H "Accept-Encoding: identity" \
  | grep -oE '<meta[^>]*(property|name)="(og:|twitter:)[^"]*"[^>]*>'
```
This is the exact same UA Facebook's crawler uses. Most reliable verification method.

### Homepage OG Issue (Still Outstanding)
- og:image is `Pure-Brain-Vid-3.gif` = 8.6MB animated GIF
- Social platforms won't render animated GIFs as preview images
- Fix image prepared: `exports/overnight-content/purebrain-homepage-og-image.jpg` (56KB, 1200x627)
- Needs upload to WP media + set in Yoast homepage social settings

---

**End of Memory**
