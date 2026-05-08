# SEO Analysis Report — purebrain.ai
**Date**: 2026-05-02
**Analyst**: SEO Specialist (Aether)

---

## 1. Indexation Status

### Google Index (site:purebrain.ai results)
- **Homepage**: Indexed
- **Terms of Service**: Indexed
- **AI Website Execution**: Indexed
- **AI Website Analysis**: Indexed
- **Brainiac Training Workshop**: Indexed
- **Cost Comparison**: Indexed
- **Partnered How This Levels You Up**: Indexed
- **AI Adoption Review**: Indexed
- **Privacy Policy**: Indexed

**Verdict**: Core pages are indexing. Google is returning 9+ results for site:purebrain.ai, which shows the robots.txt fix (Allow: / for all user-agents) is working. Previously blocked AI crawlers are now explicitly allowed.

### NOT YET INDEXED
- `/brainscore/` — NOT in Google index (confirmed: site:purebrain.ai/brainscore returns zero)
- `/blog/compound-intelligence/` — NOT in Google index AND not found in local deploy files (page may not exist yet or uses a different slug)

### Sitemap Gap (CRITICAL)
The sitemap.xml has NOT been updated since April 10. It is missing:
- `/brainscore/` (not listed)
- Any blog posts published after April 10

**Action Required**: Rebuild sitemap.xml to include `/brainscore/` and any new blog posts.

---

## 2. robots.txt Status

**Status: FIXED (AI crawlers now ALLOWED)**

The robots.txt correctly:
- Allows all user-agents with `Allow: /`
- Explicitly allows GPTBot, Google-Extended, anthropic-ai, ClaudeBot, cohere-ai, PerplexityBot, Amazonbot, FacebookBot, Applebot, CCBot, Bytespider, YouBot
- Blocks only legacy WP paths and internal/test pages
- Points to sitemap at `https://purebrain.ai/sitemap.xml`

No blocking issues for AI crawlers. This is correctly configured for GEO/AIO visibility.

---

## 3. BrainScore Page SEO Audit (/brainscore/)

### What is correct:
| Element | Value | Status |
|---------|-------|--------|
| Title | "BrainScore by PureBrain -- Would AI Recommend Your Brand?" | GOOD (58 chars) |
| Meta Description | "Free BrainScore. Find out if AI recommends your business to customers." | GOOD but short (71 chars, aim for 120-155) |
| og:title | Matches title | GOOD |
| og:description | "Free instant AI brand readiness score. 5 dimensions, 0-100..." | GOOD (rich, descriptive) |
| og:image | `https://purebrain.ai/brainscore/og-image.jpg` | GOOD (absolute URL, correct path) |
| og:type | website | GOOD |
| og:url | `https://purebrain.ai/brainscore/` | GOOD |
| twitter:card | summary_large_image | GOOD |
| twitter:image | Matches og:image | GOOD |
| robots meta | index,follow | GOOD |
| H1 | "Would AI Recommend Your Brand?" | GOOD |

### What is missing (FIX THESE):
| Element | Issue | Priority |
|---------|-------|----------|
| Canonical link | MISSING — add `<link rel="canonical" href="https://purebrain.ai/brainscore/">` | HIGH |
| JSON-LD structured data | MISSING — no WebApplication or SoftwareApplication schema | HIGH |
| Sitemap entry | NOT in sitemap.xml | HIGH |
| Meta description length | Only 71 chars — expand to 130+ chars | MEDIUM |
| FAQ schema | Page has no FAQ section but could benefit from one | LOW |

### Recommended JSON-LD for BrainScore:
```json
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "BrainScore",
  "description": "Free AI brand readiness score tool. Measures how well AI understands, finds, and recommends your business across 5 dimensions.",
  "url": "https://purebrain.ai/brainscore/",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "creator": {
    "@type": "Organization",
    "name": "Pure Technology",
    "url": "https://purebrain.ai"
  }
}
```

---

## 4. BrainScore Keyword Targets (5 Primary)

| Keyword | Monthly Volume (est.) | Competition | Intent | Strategy |
|---------|----------------------|-------------|--------|----------|
| **AI brand score** | Low-Med | LOW | Informational/Tool | Own this term. No dominant player. |
| **GEO score tool** | Low | LOW | Tool | Generative Engine Optimization scoring — emerging category |
| **AI readiness score** | Medium | MEDIUM | Tool/Assessment | upGrowth, Trustworthy Digital competing. Differentiate on "brand" angle |
| **AI brand visibility checker** | Low-Med | LOW | Tool | LLMClicks and Rankscale are competitors, but "BrainScore" branding is stronger |
| **would AI recommend my brand** | Low (long-tail) | VERY LOW | Question/Tool | Perfect for featured snippet. Match H1 exactly. |

### Secondary targets (content/blog support):
- "AI search readiness assessment"
- "brand visibility in ChatGPT"
- "how to get recommended by AI"
- "GEO optimization tool free"
- "AI brand authority score"

---

## 5. Competitive Landscape

Key competitors in this space:
- **HubSpot AEO Grader** — Free, 5 dimensions, massive domain authority
- **Trustworthy Digital AI Readiness Tool** — Website positioning focus
- **upGrowth AI Readiness Score** — 5 dimensions, 0-100 (nearly identical format)
- **LLMClicks.ai** — Visibility checker across multiple AI assistants
- **BrandRank.AI** — Brand authority in AI context
- **VerityAI AI Search Readiness** — Free grader tool
- **Rankscale** — Track visibility in AI search engines
- **QuestionDB Brand Authority Score** — Free brand authority check

**Our differentiation**: BrainScore is the only tool branded as a "score" with memorable naming + direct CTA into a paid AI partnership service. Competitors are standalone tools or lead-gen for agencies.

---

## 6. Quick Wins This Week

### Priority 1 (Do Today):
1. **Add `/brainscore/` to sitemap.xml** with priority 0.8 and today's date
2. **Add canonical link** to brainscore/index.html
3. **Add JSON-LD WebApplication schema** (code above)
4. **Submit URL to Google Search Console** for immediate crawl request

### Priority 2 (This Week):
5. **Expand meta description** to: "Free BrainScore by PureBrain. Instantly measure how well AI recommends your brand across 5 dimensions: structure, authority, citations, sentiment, and discoverability. Score 0-100."
6. **Add `/blog/compound-intelligence/` to sitemap** (if page exists — confirm slug)
7. **Write a blog post** targeting "would AI recommend my brand" — link to BrainScore tool
8. **Add internal links** from existing pages to /brainscore/ (homepage, ai-website-analysis, compare page)

### Priority 3 (Next Week):
9. **Add FAQ section** with FAQPage schema to BrainScore page (What is BrainScore? How is it calculated? What do the 5 dimensions mean?)
10. **Create a blog post** about GEO/AIO optimization that naturally links to BrainScore as the measurement tool

---

## 7. Summary

| Area | Status |
|------|--------|
| robots.txt | GOOD — AI crawlers fully allowed |
| Homepage indexation | GOOD — indexed with correct title |
| BrainScore indexation | NOT YET — missing from sitemap, no canonical |
| BrainScore OG/social | GOOD — absolute URLs, proper images |
| BrainScore structured data | MISSING — needs JSON-LD |
| Compound Intelligence blog | NOT FOUND in deploy (confirm slug/existence) |
| Sitemap freshness | STALE — last updated April 10, needs rebuild |

**Bottom line**: The robots.txt fix is working (pages are indexing). BrainScore has solid base SEO (title, OG, description) but needs sitemap inclusion, canonical tag, and structured data to start appearing in search. The page will not index until it is in the sitemap and Google is prompted to crawl it.
