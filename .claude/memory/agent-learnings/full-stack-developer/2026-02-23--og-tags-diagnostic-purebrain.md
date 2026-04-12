# OG Tags Diagnostic - purebrain.ai

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: teaching + operational
**Topic**: OG tags are present via Yoast SEO, but homepage has 9MB GIF as OG image; blog listing has junk description

---

## Key Findings

### Yoast SEO Status
- Yoast SEO v27.0 is installed, active, and generating correct OG + Twitter Card tags
- All blog posts PASS - og:title, og:description, og:image all present and correct
- Blog posts use featured image as og:image automatically (correct behavior)
- Twitter Cards: summary_large_image on all pages

### Problem 1: Homepage OG Image is a 9MB GIF
- `og:image = Pure-Brain-Vid-3.gif`
- 9MB file, 480x270px, animated GIF
- Social platforms cannot render animated GIFs, may timeout on 9MB
- NEEDS: Static JPG/PNG at 1200x627px, under 1MB

### Problem 2: Blog Listing Page (/blog/) Has Junk OG Description
- Yoast falls back to page content when no description is set
- Page 319 has no Yoast meta description → scrapes nav menu text
- og:description = "Home Subscribe AI Assessment Start Your AI Partnership PUREBRAIN.ai The Neural Feed..."
- NEEDS: Custom Yoast description for the blog listing page

### Problem 3: Blog Author Shows as "Aether PureBrain.ai"
- Twitter cards expose author name via twitter:data1
- Brand decision needed: keep Aether or change to Jared/PureBrain Team

## Key Lesson

When analytics tools flag "missing OG tags", verify with raw curl before fixing.
WebFetch can miss tags due to JS rendering - curl shows what social crawlers actually see.

```bash
curl -s "https://DOMAIN/PATH/" | grep -i "og:\|twitter:"
```

## Fix Commands (when Jared approves)

```python
# Set Yoast OG description for blog listing page (ID 319)
# Via WP REST API - _yoast_wpseo_metadesc meta field
import requests
r = requests.post(
    "https://purebrain.ai/wp-json/wp/v2/pages/319",
    auth=("Aether", APP_PASSWORD),
    json={"meta": {"_yoast_wpseo_metadesc": "The Neural Feed: Weekly insights on AI adoption, human-AI partnership, and the future of work."}}
)
```

For homepage OG image: Upload 1200x627 JPG to WP media, then set via Yoast REST API or admin panel.

---

**End of Memory**
