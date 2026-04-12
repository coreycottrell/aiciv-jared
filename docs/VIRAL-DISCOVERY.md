# Viral Content Discovery System

**Purpose**: Find viral/trending content related to Jared's ICPs and niches to enable:
- Reposting relevant content
- Piggybacking on trends
- Riding viral waves
- Engaging with hot content early

**Created**: 2026-02-04
**Location**: `tools/viral_discovery/`

---

## Quick Start

```bash
# Run full discovery across all platforms
python -m tools.viral_discovery.viral_discovery discover --all

# Generate daily digest (runs discovery + creates report)
python -m tools.viral_discovery.viral_digest

# Generate digest and sync to Google Drive
python -m tools.viral_discovery.viral_digest --sync-gdrive
```

---

## Architecture

```
tools/viral_discovery/
  __init__.py              # Package exports
  viral_discovery.py       # Main discovery engine
  viral_digest.py          # Digest/report generator
  niche_config.yaml        # Target keywords, hashtags, thresholds
```

---

## Platforms Monitored

| Platform | Apify Actor | Cost | What It Finds |
|----------|-------------|------|---------------|
| LinkedIn | `harvestapi~linkedin-post-search` | ~$2/1k posts | Viral thought leadership posts |
| Twitter/X | `apidojo/tweet-scraper` | ~$5/1k tweets | Trending marketing conversations |
| Reddit | `trudax/reddit-scraper` | ~$5/1k posts | Hot discussions in r/marketing, etc. |
| TikTok | `clockworks/tiktok-scraper` | Pay-per-event | Viral brand content videos |
| Instagram | `apify/instagram-hashtag-scraper` | ~$2.60/1k | Brand activations, experiential content |
| Google Trends | `apify/google-trends-scraper` | ~$0.80/1k keywords | Rising search topics |

**Estimated Daily Cost**: ~$1-3 for comprehensive discovery

---

## Configuration

Edit `tools/viral_discovery/niche_config.yaml` to customize:

```yaml
# Target keywords
keywords:
  primary:
    - experiential marketing
    - brand activation
    - CPG marketing
    # ...

# Platform-specific hashtags
hashtags:
  linkedin:
    - marketing
    - brandmarketing
  tiktok:
    - marketingtips
    - brandactivation
  # ...

# Engagement thresholds (what counts as "viral")
engagement_thresholds:
  linkedin:
    reactions: 100      # 100+ = notable
    viral_reactions: 500  # 500+ = viral
  twitter:
    retweets: 50
    viral_retweets: 200
  # ...

# Negative keywords to filter out
exclude_keywords:
  - hiring
  - job posting
  - MLM
```

---

## Python API

```python
from tools.viral_discovery import ViralContentDiscovery, generate_daily_digest

# Initialize
discovery = ViralContentDiscovery()

# Discover all platforms
results = discovery.discover_all()

# Platform-specific discovery
linkedin = discovery.discover_linkedin_viral(min_engagement=100)
twitter = discovery.discover_twitter_trending(min_retweets=50)
reddit = discovery.discover_reddit_discussions(min_upvotes=100)
tiktok = discovery.discover_tiktok_trends(min_views=10000)
instagram = discovery.discover_instagram_activations(min_likes=500)
trends = discovery.get_trending_topics()

# Get top opportunities across all platforms
top_content = discovery.get_top_content(limit=10)

# Export results
discovery.export_results("viral_content.json")
discovery.export_results("viral_content.csv", format="csv")

# Generate digest
filepath = generate_daily_digest(
    discovery=discovery,
    sync_gdrive=True,
    gdrive_path="AI Productivity Reports/Viral Content"
)
```

---

## CLI Commands

```bash
# Full discovery (all platforms)
python -m tools.viral_discovery.viral_discovery discover --all

# Single platform
python -m tools.viral_discovery.viral_discovery linkedin
python -m tools.viral_discovery.viral_discovery twitter
python -m tools.viral_discovery.viral_discovery reddit
python -m tools.viral_discovery.viral_discovery tiktok
python -m tools.viral_discovery.viral_discovery instagram
python -m tools.viral_discovery.viral_discovery trends

# Skip cache (force fresh scrape)
python -m tools.viral_discovery.viral_discovery discover --all --no-cache

# Export results
python -m tools.viral_discovery.viral_discovery discover --all --export viral.json
python -m tools.viral_discovery.viral_discovery discover --all --export viral.csv

# Generate daily digest
python -m tools.viral_discovery.viral_digest

# Digest with Google Drive sync
python -m tools.viral_discovery.viral_digest --sync-gdrive

# Digest with custom output location
python -m tools.viral_discovery.viral_digest --output /path/to/output
```

---

## Digest Output Format

The daily digest is a markdown file saved to:
- **Local**: `docs/viral-digest/Daily-Digest-YYYY-MM-DD.md`
- **Google Drive**: `CTO/AI Productivity Reports/Viral Content/Daily-Digest-YYYY-MM-DD.md`

### Sample Digest Structure

```markdown
# VIRAL CONTENT DIGEST - 2026-02-04

## LinkedIn Hot Posts (engage/comment today)
1. [Post] - 2.4K reactions
   Author: @marketingleader
   Relevance: 85/100
   ACTION: Comment with our POV on measurement

## Twitter Trending (quote tweet opportunities)
1. "Hot take about CPG marketing..." - 340 RTs
   ACTION: Quote with our counter-perspective

## Reddit Discussions (add value)
1. r/marketing: "Best experiential campaigns of 2025"
   ACTION: Share case study / insights

## TikTok Trends (content ideas)
1. #brandactivation has 2.3M views this week
   CONTENT IDEA: Create similar format for our niche

## Instagram Activations (brand inspiration)
1. @brandname - popup event post
   12K likes

## TOP OPPORTUNITIES (All Platforms)
1. [L] Marketing Leader - "Experiential ROI..."
   Relevance: 92/100

## QUICK ACTIONS CHECKLIST
- [ ] LinkedIn: Engage with 5 high-relevance posts
- [ ] Twitter: Quote tweet 2 trending discussions
- [ ] Create content about: Product Launch (8 trending posts)
```

---

## Relevance Scoring

Content is scored 0-100 for relevance to Jared's ICPs:

| Factor | Weight | Description |
|--------|--------|-------------|
| Primary keyword match | +15 per match | "experiential marketing", "brand activation" |
| Secondary keyword match | +7 per match | "marketing ROI", "brand building" |
| Platform hashtag match | +5 per match | #marketing, #brandactivation |
| Brand mention | +10 | Mentions target CPG brands |

**Score Interpretation**:
- 70+ = High relevance - engage/comment
- 40-69 = Moderate relevance - like/share
- <40 = Low relevance - monitor only

---

## Caching

Results are cached for 12 hours to avoid redundant API calls:
- Cache location: `.cache/viral_discovery/`
- Use `--no-cache` to force fresh scrape
- Cache is keyed by platform + query parameters

---

## Cost Optimization

1. **Run once daily** (morning recommended)
2. **Use caching** - default 12-hour cache prevents duplicate scrapes
3. **Limit keywords** - top 5 per platform by default
4. **Limit results** - max 100 posts per keyword

**Monthly estimate**: ~$30-50 for daily comprehensive discovery

---

## Integration with Workflow

### Recommended Daily Routine

1. **Morning (6 AM)**: Auto-run discovery via cron/scheduler
2. **Morning (7 AM)**: Review digest, prioritize engagement
3. **Throughout day**: Engage with top opportunities
4. **Weekly**: Review trends for content calendar

### Cron Setup (optional)

```bash
# Run discovery at 6 AM daily
0 6 * * * cd /path/to/aether && python -m tools.viral_discovery.viral_digest --sync-gdrive
```

---

## Troubleshooting

### "APIFY_API_KEY not set"
Add to `.env`:
```
APIFY_API_KEY=apify_api_xxxxxxxxxxxxx
```

### Actor fails / returns empty
- Check Apify dashboard for run status
- Actor may be rate-limited - wait and retry
- Try alternative actor (see `ALT_ACTORS` in code)

### Google Drive sync fails
- Ensure service account credentials at `.credentials/google-drive-service-account.json`
- Ensure "CTO" folder is shared with service account

---

## Extending

### Add New Platform

1. Find suitable Apify actor
2. Add to `ACTORS` dict in `viral_discovery.py`
3. Create `discover_{platform}_*` method
4. Add section generator in `viral_digest.py`
5. Add config section in `niche_config.yaml`

### Add New Keywords/Niches

Edit `niche_config.yaml`:
```yaml
keywords:
  primary:
    - your new keyword
  secondary:
    - another keyword
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `tools/viral_discovery/__init__.py` | Package exports |
| `tools/viral_discovery/viral_discovery.py` | Main discovery engine |
| `tools/viral_discovery/viral_digest.py` | Digest generation |
| `tools/viral_discovery/niche_config.yaml` | Keywords, thresholds, hashtags |
| `docs/VIRAL-DISCOVERY.md` | This documentation |
| `.cache/viral_discovery/` | Cached results (auto-created) |
| `docs/viral-digest/` | Generated digest files |

---

## Sources & Research

Apify actors selected based on 2026 research:

- **Reddit**: [trudax/reddit-scraper](https://apify.com/trudax/reddit-scraper) - Community-supported
- **TikTok**: [clockworks/tiktok-scraper](https://apify.com/clockworks/tiktok-scraper) - Most popular, full-featured
- **Instagram**: [apify/instagram-hashtag-scraper](https://apify.com/apify/instagram-hashtag-scraper) - Official Apify
- **Google Trends**: [apify/google-trends-scraper](https://apify.com/apify/google-trends-scraper) - Official Apify
- **LinkedIn**: [harvestapi~linkedin-post-search](https://apify.com/harvestapi/linkedin-post-search) - No cookies required
- **Twitter**: [apidojo/tweet-scraper](https://apify.com/apidojo/tiktok-scraper) - Reliable, cost-effective

---

*Created by web-researcher agent for Pure Technology*
