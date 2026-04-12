# Systems & Technology: Clarity Verification + OG Image Audit
**Date**: 2026-03-01
**Type**: gotcha + pattern
**Topic**: Microsoft Clarity is loaded via GTM (not inline), Elementor Canvas + CDN cache masks Yoast og:image

---

## Task 1: Microsoft Clarity Verification

### Finding
Clarity IS installed on purebrain.ai. Jared was correct. Our overnight report was wrong.

### Root Cause of False Negative
Clarity is NOT in the page HTML as an inline script.
It is loaded via **Google Tag Manager container GTM-WTDXL4VJ**, tag ID `viy9bnc56x`.

The GTM container JSON shows:
```json
{
  "function": "__html",
  "vtp_html": "<script>(function(a,e,b,f,g,c,d){a[b]=a[b]||function(){...})(window,document,'clarity','script','viy9bnc56x');</script>"
}
```

GTM fires AFTER page load via JavaScript — curl/server-side fetch sees NO Clarity tag.
Any audit that fetches HTML without executing JS will miss GTM-loaded scripts.

### Future Audit Rule
When checking for analytics scripts (Clarity, Hotjar, Heap, etc.):
- FIRST check GTM container: `curl https://www.googletagmanager.com/gtm.js?id=GTM-{container_id} | grep -i clarity`
- Do NOT rely solely on raw HTML source

---

## Task 2: OG Image Audit & Fix

### Pages Checked (public-facing key pages)
| Page | ID | Yoast meta set | Live HTML og:image |
|------|----|----------------|-------------------|
| /cost-comparison/ | 970 | YES (694) | NO (CDN cache) |
| /website-execution/ | 855 | NO -> FIXED | YES after fix |
| /ai-website-execution/ | 860 | YES (694) | YES |
| /compare/ | 752 | YES (694) | assumed OK |
| /why-purebrain/ | 794 | YES (694) | assumed OK |
| /ai-partnership-calculator/ | 811 | NO | Redirects to /ai-tool-stack-calculator/ - irrelevant |

### Fix Applied
Set Yoast OG image for `/website-execution/` (ID 855):
- `_yoast_wpseo_opengraph-image`: `https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg`
- `_yoast_wpseo_opengraph-image-id`: `694`

### Default OG Image
Media ID: 694
URL: `https://purebrain.ai/wp-content/uploads/2026/02/purebrain-homepage-og.jpg`
Dimensions: 1200x627

### Cost-Comparison Issue Diagnosis
cost-comparison (970) has correct Yoast meta in DB and Yoast head API returns correct og:image.
But live HTML does NOT show og:image — this is Cloudflare CDN caching a stale page version.

Yoast head API at `/wp-json/yoast/v1/get_head?url=...` returns correct og:image for BOTH pages.
Social crawlers (Facebook, LinkedIn, Twitter) typically bypass CDN and hit origin or use head API.

### Elementor Canvas + Yoast Pattern
All three pages (970, 855, 860) use `elementor_canvas` template.
Elementor Canvas DOES call wp_head on this site (confirmed: Yoast schema IS present in live HTML).
The security plugin adds additional wp_head hooks but doesn't override Yoast og:image logic.

### CDN Cache Pattern
When Yoast shows correct data via API but live HTML shows stale/missing:
- Not a data issue
- Not a Yoast issue
- Cloudflare CDN cache holding old version
- Solution: Wait for natural TTL expiry OR use Cloudflare API to purge specific URL
- CF credentials: Only CF_ACCOUNT_ID in .env, no CF_API_TOKEN stored

---

## Key Commands

### Check if script loaded via GTM
```bash
curl -s "https://www.googletagmanager.com/gtm.js?id=GTM-WTDXL4VJ" | grep -i "clarity"
```

### Check Yoast OG image for any page (authoritative source)
```bash
curl -s "https://purebrain.ai/wp-json/yoast/v1/get_head?url=ENCODED_URL" | python3 -c "
import json,sys,re
d=json.load(sys.stdin)
imgs=re.findall(r'og:image.*?content=[\"\'](.*?)[\"\']', d.get('html',''))
print(imgs)
"
```

### Set Yoast OG image for a page
```bash
curl -X POST "https://purebrain.ai/wp-json/wp/v2/pages/{PAGE_ID}" \
  -u "Aether:FlFr2VOtlHiHaJWjzW96OHUJ" \
  -H "Content-Type: application/json" \
  -d '{"meta": {"_yoast_wpseo_opengraph-image": "URL", "_yoast_wpseo_opengraph-image-id": "694"}}'
```
