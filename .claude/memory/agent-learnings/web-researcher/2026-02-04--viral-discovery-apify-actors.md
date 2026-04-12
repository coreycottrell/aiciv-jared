# Viral Discovery System - Apify Actors Research

**Date**: 2026-02-04
**Type**: synthesis
**Agent**: web-researcher
**Confidence**: high

## Context

Researched and implemented a viral content discovery system for Pure Technology to find trending content across social platforms related to Jared's ICPs (experiential marketing, CPG, brand activations).

## Key Findings

### Best Apify Actors by Platform (2026)

| Platform | Recommended Actor | Cost | Notes |
|----------|-------------------|------|-------|
| LinkedIn Posts | `harvestapi~linkedin-post-search` | ~$2/1k posts | No cookies/login required |
| Twitter/X | `apidojo/tweet-scraper` | ~$5/1k tweets | Reliable, cost-effective |
| Reddit | `trudax/reddit-scraper` | ~$5/1k posts | Good community support |
| TikTok | `clockworks/tiktok-scraper` | Pay-per-event | Most popular, full-featured |
| Instagram | `apify/instagram-hashtag-scraper` | ~$2.60/1k | Official Apify actor |
| Google Trends | `apify/google-trends-scraper` | ~$0.80/1k | Official, well-maintained |

### Alternative Actors (Fallbacks)

- LinkedIn: `curious_coder/linkedin-post-search-scraper`
- Twitter: `quacker/twitter-scraper`
- Reddit: `crawlerbros/reddit-scraper`
- TikTok: `apidojo/tiktok-scraper`
- Instagram: `instaprism/instagram-hashtag-scraper`

### Cost Optimization Patterns

1. **Caching**: 12-hour cache prevents duplicate scrapes
2. **Limit keywords**: Top 5 per platform reduces API calls
3. **Limit results**: Max 100 posts per keyword
4. **Daily run**: Once per day is sufficient for trends

**Monthly estimate**: ~$30-50 for comprehensive daily discovery

## Implementation

Created `tools/viral_discovery/` package:
- `viral_discovery.py` - Main discovery engine with `ViralContentDiscovery` class
- `viral_digest.py` - Generates actionable markdown digest
- `niche_config.yaml` - Keywords, hashtags, engagement thresholds
- `__init__.py` - Package exports

### Key Design Decisions

1. **Relevance scoring (0-100)**: Weights primary keywords (+15), secondary (+7), hashtags (+5), brand mentions (+10)
2. **Engagement thresholds**: Configurable per platform (e.g., LinkedIn 100+ reactions = notable)
3. **Negative keyword filtering**: Excludes job postings, MLM, crypto content
4. **Google Drive integration**: Optional sync to `CTO/AI Productivity Reports/Viral Content/`

## When to Apply

- Daily morning discovery routine
- Finding content to engage with/repost
- Identifying trending topics for content calendar
- Monitoring competitor activity in experiential marketing space

## Sources

- [trudax/reddit-scraper](https://apify.com/trudax/reddit-scraper)
- [clockworks/tiktok-scraper](https://apify.com/clockworks/tiktok-scraper)
- [apify/instagram-hashtag-scraper](https://apify.com/apify/instagram-hashtag-scraper)
- [apify/google-trends-scraper](https://apify.com/apify/google-trends-scraper)
- [harvestapi~linkedin-post-search](https://apify.com/harvestapi/linkedin-post-search)
- [Apify Review 2026](https://hackceleration.com/apify-review/)
