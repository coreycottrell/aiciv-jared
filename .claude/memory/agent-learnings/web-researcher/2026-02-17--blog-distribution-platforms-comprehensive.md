# Blog Distribution Platforms Research

**Date**: 2026-02-17
**Agent**: web-researcher
**Type**: synthesis
**Topic**: Free blog distribution platforms with RSS automation for purebrain.ai

---

## Context

Researched free platforms for automatically publishing blog content from purebrain.ai/blog. Focus on RSS import capabilities and automation options.

---

## Key Findings

### Platforms with NATIVE RSS Import (Best Options)

1. **Dev.to** - Settings > Extensions > "Publishing to DEV from RSS"
   - Posts appear as drafts, one-click publish
   - Automatic canonical URL
   - Tech-focused audience perfect for AI content

2. **Hashnode** - Blog Dashboard > Import > RSS Importer
   - Fully automatic with canonical
   - Developer audience
   - Custom domain support

3. **Flipboard** - flipboard.com/publishers > Add RSS
   - Creates magazine from RSS feed
   - Requires: full feed (not excerpts), 400px images, 30+ items

### Platforms WITHOUT RSS (Manual Required)

- **Medium** - Use Import Tool ONLY (preserves canonical). Never copy-paste.
- **HackerNoon** - Editorial review required
- **Vocal.media** - 24-72h review, 600 word minimum
- **NewsBreak** - US-only, approval required

### Automation Tools (Free Tiers)

| Tool | Free Tier | Best For |
|------|-----------|----------|
| **n8n** | Unlimited (self-hosted) | Multi-platform RSS to social |
| Make.com | 1,000 ops/month | Complex workflows |
| IFTTT | 5 applets | Simple triggers |
| Zapier | 100 tasks/month | 8000+ integrations |
| Buffer | 3 channels, 10 posts each | Social scheduling |

### Google News RSS DEPRECATED

As of 2026, Google News no longer accepts RSS feed submissions. Content is auto-discovered.

---

## Critical Gotchas

1. **Medium copy-paste loses SEO** - Google trusts Medium over your site
2. **dlvr.it is overpriced** - $199/mo for what n8n does free
3. **LinkedIn one-way only** - WordPress->LinkedIn works; reverse doesn't
4. **Substack has no API** - Cannot automate, only one-time import

---

## Recommended Priority

**Week 1 (5 minutes each)**:
- Enable Dev.to RSS import
- Enable Hashnode RSS import
- Create Flipboard magazine

**Month 1 (2-4 hours)**:
- Set up n8n self-hosted for additional social platforms
- Install WP LinkedIn Auto Publish plugin

---

## When to Apply

- Planning content distribution strategy
- Setting up automated cross-posting
- Evaluating new publishing platforms
- Prioritizing distribution channel investments

---

**Full Report**: `/home/jared/projects/AI-CIV/aether/exports/blog-distribution-platforms.md`

---

**Tags**: content-distribution, RSS, automation, cross-posting, publishing-platforms, purebrain
