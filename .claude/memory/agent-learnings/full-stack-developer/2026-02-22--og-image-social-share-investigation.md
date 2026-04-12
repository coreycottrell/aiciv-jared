# WordPress OG Image Social Share Investigation

**Date**: 2026-02-22
**Agent**: full-stack-developer
**Type**: teaching + operational
**Topic**: Diagnosing "wrong social share preview image" when WP is actually correct

---

## Task

Jared reported social share preview for https://purebrain.ai/the-ai-trust-gap/ showed wrong image.

## Diagnosis Findings

Everything at the WordPress level was ALREADY CORRECT:

### purebrain.ai (Post 631)
- Featured Media ID: 639 (Jared's banner - correct)
- og:image: `https://purebrain.ai/wp-content/uploads/2026/02/trust-gap-blog-banner-jared.jpg`
- og:image dimensions: 1280x720 (matches actual image)
- Image HTTP 200, no redirects
- Twitterbot sees same correct og:image

### jareddsanborn.com (Post 1122)
- Featured Media ID: 1124 (correct)
- og:image: `https://jareddsanborn.com/wp-content/uploads/2026/02/trust-gap-blog-banner-jared.jpg`
- og:image dimensions: 1280x720 (matches actual image)
- Image HTTP 200, no redirects
- Twitterbot sees same correct og:image

## Root Cause

**Social platform cache.** LinkedIn, Twitter/X, Facebook all cache OG scraped data
aggressively (24-72 hours). When the post was first published, the OG data was
scraped and cached. If the featured image was wrong or missing at that moment,
or if the post was initially a draft, the wrong data gets cached.

The infrastructure was already correct when I checked. No WordPress fixes were needed.

## Fix for Social Platform Cache

### LinkedIn
- Go to: https://www.linkedin.com/post-inspector/
- Enter the URL, click "Inspect"
- Shows what LinkedIn sees + has "Scrape Again" button

### Facebook
- Go to: https://developers.facebook.com/tools/debug/
- Enter URL, click "Debug"
- Click "Scrape Again" to force refresh

### Twitter/X
- Go to: https://cards-dev.twitter.com/validator (may require login)
- Or: https://socialsharepreview.com/ to check current state

### General
- Social platforms cache OG data for 24-72 hours
- Even after scraping again, CDN/edge nodes may still serve old cache for 30 min
- This is NOT a WordPress problem - it's a social platform caching problem

## Key Lesson

When "social share image looks wrong" is reported:
1. FIRST check the live og:image tag on the page (curl | grep og:image)
2. THEN verify the image URL is actually accessible (HTTP 200, correct content-type)
3. THEN check featured_media via WP REST API
4. If all three are correct → tell Jared to use the social platform's scraper tool to refresh cache
5. If any of the above are wrong → fix at the appropriate layer

## Verification Commands Used

```bash
# Check live OG tags
curl -s "https://purebrain.ai/the-ai-trust-gap/" | grep -i "og:image"

# Check with Twitterbot UA
python3 -c "import requests; r = requests.get('URL', headers={'User-Agent': 'Twitterbot/1.0'}); print([m for m in __import__('re').findall('og:image.*?content=\"([^\"]+)\"', r.text)])"

# Check WP REST API
GET /wp-json/wp/v2/posts/631 → check featured_media field
GET /wp-json/wp/v2/media/639 → check source_url
```

---

**End of Memory**
