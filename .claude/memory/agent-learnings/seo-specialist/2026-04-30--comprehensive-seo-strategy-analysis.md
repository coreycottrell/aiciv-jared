# 2026-04-30 -- Comprehensive SEO Strategy Analysis

**Type**: operational
**Agent**: seo-specialist

## Key Findings

### Indexation Crisis Persists
- Only ~9 pages showing in Google site: query (out of 111 sitemap URLs)
- robots.txt has critical contradiction: Cloudflare Managed section DISALLOWs AI crawlers BEFORE custom section ALLOWs them. First match wins.
- 42 pages STILL have wp-content og:image (unchanged since Apr 18 audit)
- Homepage still 632KB with 4 duplicate head sections

### Competitive Landscape
- PureBrain ranks for ZERO non-branded keywords
- "AI partner platform" dominated by IBM, Microsoft, Google Cloud
- "AI assistant for business" dominated by Moveworks, Amazon Quick, Sintra, Wing
- "best AI tools for small business" dominated by Salesforce, Missive, Mailmodo
- One external review exists (firstsales.io) -- positive signal but isolated

### Quick-Win Keywords Identified
- "AI that remembers context" -- low competition, 3+ blog posts exist
- "persistent AI memory" -- unique differentiator, low competition
- "agentic AI partner" -- niche, strong existing content
- All require technical fixes FIRST (robots.txt, og:image, blog index)

### robots.txt Architecture Issue
- Cloudflare Managed Content block (top of file) explicitly disallows ClaudeBot, GPTBot, Google-Extended, Amazonbot, Bytespider, etc.
- Custom Allow rules at bottom attempt to override but per robots.txt spec, first matching rule wins
- This means AI search engines (Perplexity, ChatGPT Search, Google AI Overviews) are likely blocked from crawling

## Files
- Report: `/home/jared/projects/AI-CIV/aether/exports/portal-files/overnight-seo-analysis-2026-05-01.md`
- Prior audits: `2026-04-25--followup-site-audit-purebrain.md`, `2026-04-18--full-site-seo-audit-purebrain.md`
