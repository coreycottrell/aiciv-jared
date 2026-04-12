# 🔍 web-researcher: Blog Distribution Platforms Research

**Agent**: web-researcher
**Domain**: Content syndication, RSS automation, free publishing platforms
**Date**: 2026-02-17

---

## Executive Summary

Comprehensive research on free blog/newsletter distribution platforms for purebrain.ai/blog. Found **23+ viable platforms** across 4 categories: Publishing Platforms (8), Aggregators/Syndication (6), Automation Tools (6), and Community Platforms (5). Key finding: **Dev.to and Hashnode offer native RSS import** for automatic cross-posting, while **n8n provides free self-hosted RSS-to-social automation**.

---

## Prior Knowledge Applied

Searched memory and found relevant prior research:
- `2026-02-16--content-distribution-platforms-research.md` - Platform priority recommendations
- `2026-02-13--blog-distribution-pipeline-built.md` - Existing Bluesky/Telegram automation

**Existing infrastructure**: `tools/blog_distribution_pipeline.py` already handles WordPress -> Bluesky threads and LinkedIn copy-paste via Telegram.

---

## PART 1: FREE PUBLISHING PLATFORMS

### 1. Medium.com

| Attribute | Details |
|-----------|---------|
| **Cost** | Free to publish |
| **Automation** | Import Tool (recommended), Zapier, Blog2Social plugin |
| **RSS Import** | No native RSS import - must use Import Tool or third-party |
| **API** | Yes - via Medium Integration Tokens |
| **Setup Steps** | 1. Create Medium account 2. Use "Import Story" (hamburger menu) 3. Paste URL -> Auto-imports with canonical |
| **Reach/Benefit** | High domain authority, SEO boost, built-in audience |
| **CRITICAL** | ALWAYS use Import Tool - it auto-adds canonical URL. Copy-paste loses SEO to Medium. |

**Sources**: [Content Powered Guide](https://www.contentpowered.com/blog/auto-publish-wordpress-medium/), [Medium WordPress Plugin](https://github.com/Medium/medium-wordpress-plugin), [illuminea Ultimate Guide](https://illuminea.com/ultimate-guide-to-wp-medium/)

---

### 2. Dev.to

| Attribute | Details |
|-----------|---------|
| **Cost** | Free |
| **Automation** | **Native RSS Import** (best option!) |
| **RSS Import** | YES - Settings > Extensions > "Publishing to DEV from RSS" |
| **API** | Yes - full API available |
| **Setup Steps** | 1. Create account 2. Settings > Extensions 3. Add RSS URL 4. Posts appear as drafts |
| **Reach/Benefit** | Tech-focused audience, great for AI/dev content, SEO value |
| **Note** | Content imported as drafts - one-click to publish |

**Sources**: [Felix Runquist Guide](https://felixrunquist.com/posts/automatically-cross-publishing-posts-to-dev-to-with-rss)

---

### 3. Hashnode

| Attribute | Details |
|-----------|---------|
| **Cost** | Free |
| **Automation** | **Native RSS Importer** |
| **RSS Import** | YES - Blog Dashboard > Import > RSS Importer |
| **API** | GraphQL API available |
| **Setup Steps** | 1. Create blog 2. Dashboard > Import 3. Enter RSS URL 4. Auto-imports with canonical |
| **Reach/Benefit** | Developer-focused, custom domain support, excellent SEO |
| **Note** | Automatically sets canonical URL to original post |

**Sources**: [smartrs.blog Guide](https://smartrs.blog/publish-your-hashnode-blog-on-wordpress-and-other-sites-using-rss-feed), [Hashnode Townhall](https://townhall.hashnode.com/increase-your-custom-blog-traffic-by-republishing-on-hashnode)

---

### 4. Substack

| Attribute | Details |
|-----------|---------|
| **Cost** | Free |
| **Automation** | Limited - RSS importer for one-time import |
| **RSS Import** | Partial - import tool accepts RSS for bulk migration |
| **API** | No public API |
| **Setup Steps** | 1. Create publication 2. substack.com/signup/import 3. Enter RSS URL |
| **Reach/Benefit** | Newsletter-first platform, cross-promotion network, email subscribers |
| **Note** | Better for primary newsletter, not automated cross-posting |

**Sources**: [Substack Import Help](https://support.substack.com/hc/en-us/articles/360037830351), [Substack Import Page](https://substack.com/signup/import)

---

### 5. HackerNoon

| Attribute | Details |
|-----------|---------|
| **Cost** | Free |
| **Automation** | Manual submission only |
| **RSS Import** | No |
| **API** | No public API |
| **Setup Steps** | 1. Create account at hackernoon.com 2. Submit articles for editorial review |
| **Reach/Benefit** | 15,000+ AI articles published, human editorial support, 12-language translation, audio versions |
| **Note** | Editorial review required - not instant publish. Quality focus. |

**Sources**: [HackerNoon AI Publishing](https://hackernoon.ai/publishing), [Publish on HackerNoon](https://www.publish.hackernoon.com/)

---

### 6. Vocal.media

| Attribute | Details |
|-----------|---------|
| **Cost** | Free (Vocal+: $9.99/month for higher payouts) |
| **Automation** | Manual submission only |
| **RSS Import** | No |
| **API** | No |
| **Setup Steps** | 1. Create account 2. Submit stories 3. 24-72h review period |
| **Reach/Benefit** | Pay per read ($3.80/1000), contests with prizes, tips from readers |
| **Note** | 600 word minimum. AI content faces additional review. |

**Sources**: [Vocal.media](https://vocal.media/), [Vocal Review](https://selfmademillennials.com/vocal-media-review/)

---

### 7. NewsBreak

| Attribute | Details |
|-----------|---------|
| **Cost** | Free |
| **Automation** | Manual submission |
| **RSS Import** | No |
| **API** | No public API |
| **Setup Steps** | 1. Apply at creators.newsbreak.com 2. Get approved 3. Submit articles |
| **Reach/Benefit** | 45M+ monthly active users, potential $1000/month for top creators |
| **Note** | US-based writers only. 10 articles required before monetization. |

**Sources**: [NewsBreak Creators](https://creators.newsbreak.com/), [NewsBreak Review](https://bloggingguide.com/guides/newsbreak/)

---

### 8. Beehiiv

| Attribute | Details |
|-----------|---------|
| **Cost** | Free tier available |
| **Automation** | RSS-to-Send (Max plan only) |
| **RSS Import** | Yes - for content import; RSS-to-Send on paid plans |
| **API** | Yes |
| **Setup Steps** | 1. Create account 2. Import from WordPress 3. Grow subscriber list |
| **Reach/Benefit** | Newsletter growth focus, referral program, sponsorship marketplace |
| **Note** | RSS-to-Send (auto publish from RSS) requires Max plan ($99/mo) |

**Sources**: [Beehiiv RSS Features](https://www.beehiiv.com/support/article/9363537272215), [Beehiiv Review](https://selfmademillennials.com/beehiiv-review/)

---

## PART 2: AGGREGATORS & SYNDICATION

### 1. Flipboard

| Attribute | Details |
|-----------|---------|
| **Cost** | Free |
| **Automation** | **Native RSS Magazine Creation** |
| **RSS Import** | YES - Create magazine from RSS feed |
| **Setup Steps** | 1. flipboard.com/publishers 2. Create magazine 3. Add RSS source |
| **Requirements** | Full RSS feed (not excerpts), images 400px+, 30+ items in feed |
| **Reach/Benefit** | Content discovery, topic-based distribution |

**Sources**: [Flipboard RSS Guide](https://about.flipboard.com/inside-flipboard/rss-feed-on-flipboard/), [Flipboard Publishers](https://about.flipboard.com/inside-flipboard/new-feed-your-rss-feed-into-a-flipboard-magazine/)

---

### 2. Google News (UPDATE: RSS Deprecated)

| Attribute | Details |
|-----------|---------|
| **Cost** | Free |
| **Automation** | **CHANGED IN 2026** - No longer accepts RSS submissions |
| **RSS Import** | NO - Google News now uses automatic crawling |
| **Setup Steps** | Submit at Publisher Center for branding/logos only |
| **Reach/Benefit** | Massive reach IF indexed |
| **Note** | Manual RSS submission deprecated. Google now auto-discovers content. |

**Sources**: [Google Publisher Center Update](https://support.google.com/news/publisher-center/answer/15898024)

---

### 3. Mix.com (formerly StumbleUpon)

| Attribute | Details |
|-----------|---------|
| **Cost** | Free |
| **Automation** | Manual + Browser extension |
| **RSS Import** | No |
| **Setup Steps** | 1. Create account 2. Create collections 3. Add content manually or via extension |
| **Reach/Benefit** | Algorithm recommends to interested users, niche targeting |

**Sources**: [Brafton Content Syndication](https://www.brafton.com/blog/distribution/14-content-syndication-networks-and-platforms-you-should-already-know/)

---

### 4. Pocket

| Attribute | Details |
|-----------|---------|
| **Cost** | Free |
| **Automation** | API available for submissions |
| **RSS Import** | No |
| **Setup Steps** | Users save content; focus on making content save-worthy |
| **Reach/Benefit** | Content recommendation to Pocket users |
| **Note** | Pocket recommends popular saved content to other users |

---

### 5. Quora Spaces

| Attribute | Details |
|-----------|---------|
| **Cost** | Free |
| **Automation** | Manual only |
| **RSS Import** | No |
| **Setup Steps** | 1. Create Space or join relevant ones 2. Share content (space rules vary) |
| **Reach/Benefit** | 300M+ monthly users, SEO value from answers |
| **Note** | External links in answers discouraged. Better: answer questions, link in bio. |

**Sources**: [Quora Spaces Policies](https://help.quora.com/hc/en-us/articles/360043961972-Spaces-Policies)

---

### 6. LinkedIn Articles/Newsletter

| Attribute | Details |
|-----------|---------|
| **Cost** | Free |
| **Automation** | WordPress plugins available (WP LinkedIn Auto Publish) |
| **RSS Import** | No |
| **Setup Steps** | Use WP LinkedIn Auto Publish plugin or manual copy-paste |
| **Reach/Benefit** | Professional audience, newsletter subscribers |
| **Note** | **One-directional only** (WordPress -> LinkedIn, not reverse) |

**Sources**: [WP LinkedIn Auto Publish](https://wordpress.org/plugins/wp-linkedin-auto-publish/), [WPBeginner Guide](https://www.wpbeginner.com/wp-tutorials/how-to-auto-publish-wordpress-posts-to-linkedin/)

---

## PART 3: AUTOMATION TOOLS

### 1. n8n (RECOMMENDED - Free Self-Hosted)

| Attribute | Details |
|-----------|---------|
| **Cost** | **FREE when self-hosted** |
| **Capability** | RSS to multi-platform social media |
| **Platforms** | Bluesky, X, LinkedIn, Instagram, TikTok, Telegram, YouTube, Threads |
| **Setup** | Self-host or n8n cloud (free tier: 5 workflows) |
| **Key Features** | AI summaries, image generation, approval workflows |

**Pre-built Templates**:
- [RSS to PostPulse Multi-Platform](https://n8n.io/workflows/8800-automate-rss-news-to-multi-platform-social-media-publishing-via-postpulse/)
- [RSS to Social with AI Summaries](https://n8n.io/workflows/9208-automate-rss-to-social-media-with-ai-summaries-and-image-generation/)
- [RSS with Telegram Approval](https://n8n.io/workflows/5397-auto-generate-and-approve-social-media-posts-from-rss-feeds-with-openai-and-telegram/)
- [AI Content Factory](https://n8n.io/workflows/11298-ai-powered-content-factory-rss-to-blog-instagram-and-tiktok-with-slack-approval/)

**Sources**: [n8n RSS Integrations](https://n8n.io/integrations/rss-read/)

---

### 2. Make.com (formerly Integromat)

| Attribute | Details |
|-----------|---------|
| **Cost** | Free tier: 1,000 operations/month |
| **Capability** | RSS to any connected platform |
| **Setup** | Visual workflow builder |
| **Note** | HTTP module can fetch RSS directly for free |

**Sources**: [Substack RSS Tutorial](https://aimaker.substack.com/p/how-to-automate-rss-feed-digest-ai-substack-makecom-tutorial)

---

### 3. IFTTT

| Attribute | Details |
|-----------|---------|
| **Cost** | Free tier: 5 applets |
| **Capability** | RSS to social media, notifications |
| **2026 Features** | AI Content Creator, AI Social Creator |
| **Setup** | Simple if-this-then-that recipes |

**Sources**: [IFTTT RSS Integrations](https://ifttt.com/feed)

---

### 4. Zapier

| Attribute | Details |
|-----------|---------|
| **Cost** | Free tier: 100 tasks/month |
| **Capability** | RSS to 8,000+ app integrations |
| **Setup** | Multi-step workflows |
| **Note** | More powerful than IFTTT but limited free tier |

---

### 5. dlvr.it

| Attribute | Details |
|-----------|---------|
| **Cost** | Free tier (very limited), Paid: $199/month |
| **Capability** | RSS to 21 social networks |
| **Note** | **NOT RECOMMENDED** - Free tier too limited, paid too expensive |

**Sources**: [dlvr.it](https://dlvrit.com/), [Nuelink Alternative Comparison](https://blog.nuelink.com/dlvr-it-alternative/)

---

### 6. Missinglettr

| Attribute | Details |
|-----------|---------|
| **Cost** | Free tier: 1 profile, 50 posts/month; Solo: $15/mo |
| **Capability** | Auto-generates year of social posts from each blog |
| **Setup** | Connect blog, AI creates drip campaigns |
| **Note** | Free tier not practical for real use |

**Sources**: [Missinglettr Pricing](https://missinglettr.com/pricing/)

---

## PART 4: SOCIAL MEDIA AUTO-POSTING

### Buffer

| Attribute | Details |
|-----------|---------|
| **Cost** | **Free: 3 channels, 10 posts/channel** |
| **RSS** | Can track RSS feeds for content ideas |
| **Paid** | $5/month per channel |

**Sources**: [Buffer Review](https://efficient.app/apps/buffer)

---

### Hootsuite RSS Autopublisher

| Attribute | Details |
|-----------|---------|
| **Cost** | Paid only ($199/mo minimum) |
| **RSS** | Direct RSS to LinkedIn, X, Facebook |
| **Note** | Too expensive for small operations |

**Sources**: [Hootsuite RSS Autopublisher](https://apps.hootsuite.com/apps/rssautopublisher)

---

## PRIORITY RECOMMENDATIONS

### Tier 1: Implement This Week (Free, High Impact)

| Platform | Method | Time to Setup |
|----------|--------|---------------|
| **Dev.to** | Native RSS import | 5 minutes |
| **Hashnode** | Native RSS import | 5 minutes |
| **Flipboard** | RSS Magazine | 10 minutes |
| **Medium** | Import Tool (manual per post) | 2 min/post |

### Tier 2: Implement This Month (Requires More Setup)

| Platform | Method | Time to Setup |
|----------|--------|---------------|
| **n8n self-hosted** | RSS to multi-social automation | 2-4 hours |
| **WP LinkedIn Auto Publish** | WordPress plugin | 30 minutes |
| **HackerNoon** | Manual submission | 10 min/post |

### Tier 3: Nice to Have (Lower Priority)

| Platform | Method | Notes |
|----------|--------|-------|
| Vocal.media | Manual | Good for monetization testing |
| NewsBreak | Manual | US audience, approval required |
| Quora Spaces | Manual | Better for answer-linking strategy |
| Substack | One-time import | Only if starting newsletter there |

---

## RECOMMENDED WORKFLOW

```
purebrain.ai/blog (WordPress)
         |
         v
    [RSS Feed: purebrain.ai/feed/]
         |
    +---------+---------+---------+
    |         |         |         |
    v         v         v         v
  Dev.to   Hashnode  Flipboard  n8n
  (auto)   (auto)    (auto)     (auto)
                                  |
                            +-----+-----+
                            |     |     |
                            v     v     v
                         Bluesky  X   Threads
                         (thread) (post) (post)
         |
         v
    [Manual per post]
         |
    +----+----+
    |         |
    v         v
  Medium   HackerNoon
  (Import)  (Submit)
```

---

## EXISTING INFRASTRUCTURE

Your current `tools/blog_distribution_pipeline.py` handles:
- WordPress publish detection
- Bluesky 4-part thread auto-post
- LinkedIn copy-paste to Telegram
- Twitter ready (awaiting API keys)

**Recommended additions**:
1. Dev.to RSS import (one-time setup)
2. Hashnode RSS import (one-time setup)
3. Flipboard magazine creation (one-time setup)
4. n8n workflow for additional social platforms

---

## GOTCHAS & WARNINGS

1. **Medium copy-paste = SEO loss** - ALWAYS use Import Tool
2. **Google News RSS deprecated** - Don't waste time submitting feeds
3. **dlvr.it pricing** - $199/mo is not justified vs free alternatives
4. **Substack no API** - Cannot automate posting, only import
5. **NewsBreak US-only** - International content won't be accepted
6. **Quora external links** - Space admins control; answers better than links
7. **LinkedIn one-way only** - WordPress->LinkedIn works; reverse doesn't

---

## Sources

### Publishing Platforms
- [Content Powered - Medium Auto-Publish](https://www.contentpowered.com/blog/auto-publish-wordpress-medium/)
- [Felix Runquist - Dev.to RSS](https://felixrunquist.com/posts/automatically-cross-publishing-posts-to-dev-to-with-rss)
- [smartrs.blog - Hashnode RSS](https://smartrs.blog/publish-your-hashnode-blog-on-wordpress-and-other-sites-using-rss-feed)
- [HackerNoon Publishing](https://hackernoon.ai/publishing)
- [Vocal.media](https://vocal.media/)
- [NewsBreak Creators](https://creators.newsbreak.com/)

### Aggregators
- [Flipboard RSS Guide](https://about.flipboard.com/inside-flipboard/rss-feed-on-flipboard/)
- [Google Publisher Center Update](https://support.google.com/news/publisher-center/answer/15898024)
- [Quora Spaces Policies](https://help.quora.com/hc/en-us/articles/360043961972-Spaces-Policies)

### Automation Tools
- [n8n RSS Workflows](https://n8n.io/integrations/rss-read/)
- [IFTTT Feed Integrations](https://ifttt.com/feed)
- [Make.com RSS Tutorial](https://aimaker.substack.com/p/how-to-automate-rss-feed-digest-ai-substack-makecom-tutorial)
- [Missinglettr Pricing](https://missinglettr.com/pricing/)

### Social Media Tools
- [WP LinkedIn Auto Publish](https://wordpress.org/plugins/wp-linkedin-auto-publish/)
- [Buffer Review](https://efficient.app/apps/buffer)
- [Hootsuite RSS Autopublisher](https://apps.hootsuite.com/apps/rssautopublisher)

---

**Memory Written**:
Path: /home/jared/projects/AI-CIV/aether/.claude/memory/agent-learnings/web-researcher/2026-02-17--blog-distribution-platforms-comprehensive.md
Type: synthesis
Topic: Free blog distribution platforms with RSS automation capabilities

---

*Research completed 2026-02-17 by web-researcher agent*
