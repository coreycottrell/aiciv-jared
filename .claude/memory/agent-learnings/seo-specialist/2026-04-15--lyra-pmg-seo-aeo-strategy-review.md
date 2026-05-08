# Memory — 2026-04-15 — Lyra/PMG SEO/AEO strategy review

**Type:** teaching + operational
**Agent:** seo-specialist
**Triggered by:** Aether EXECUTE request — review PureBrain SEO/AEO strategy from Lyra (Pure Marketing Group), CC Nathan

## What happened

Lyra sent a 90-day SEO/AEO strategy doc (1,064 lines) synthesizing frameworks from 11 experts (Neil Patel, Rand Fishkin, Eli Schwartz, Cyrus Shepard, Aleyda Solis, Kevin Indig, Jeff Coyle, Wil Reynolds, Lily Ray + HubSpot/Drift). Strategy is strong strategically but had factual staleness, unrealistic content velocity, and measurement gaps.

Verdict delivered: YELLOW — ship with changes.

## Key patterns to remember

### 1. ALWAYS verify current-state claims with live curl before grading an SEO audit

Lyra's doc claimed "sitemap returns 403" and "zero schema markup." Live check showed sitemap 200 with 106 URLs, and homepage has a full Yoast schema graph. If I had graded on the doc's framing alone, I would have rubber-stamped fixes for non-existent problems.

**Procedure:**
```bash
curl -sI https://purebrain.ai/sitemap.xml | head -3          # status code
curl -s https://purebrain.ai/sitemap.xml | grep -c '<loc>'    # URL count
curl -s https://purebrain.ai/robots.txt | grep -E "^(User-agent|Disallow|Allow)"
curl -s https://purebrain.ai/ | grep -c 'application/ld+json' # schema blocks
curl -s https://purebrain.ai/ | grep -oE '<meta property="og:image"[^>]*'
```

### 2. The real P0 for AEO at PureBrain (2026-04-15)

robots.txt currently **Disallows** GPTBot, ClaudeBot, CCBot, PerplexityBot, Google-Extended, Amazonbot, Applebot-Extended, Bytespider, meta-externalagent. This is the single biggest AEO blocker. Any AEO strategy that doesn't treat this as Day 1 Hour 1 is misordered.

### 3. og:image gotcha — animated GIFs don't render on LinkedIn/Twitter

Current homepage og:image is `Pure-Brain-Vid-3.gif` (480x270 animated). Needs to be 1200x630 static JPG/PNG. Week 1 fix.

### 4. Platform matrix for purebrain.ai (IMPORTANT — correct my default assumption)

- Homepage + `/blog/` index → **WordPress + Yoast SEO + Elementor**
- `/blog/[slug]/` posts → **CF Pages** (March 20 locked blog pipeline)
- `/refer/`, portal, tools → **CF Pages Workers/D1**

Mixed architecture. Agent default "site is CF Pages" is only true for blog posts and app surfaces. Yoast handles schema on WP pages; CF Pages blog posts need hand-authored JSON-LD.

### 5. Content velocity rule of thumb — cut external-agency proposals by ~40%

Lyra proposed 50 pieces in 90 days. Realistic for 1 human + AI partners is 25–30. Every time: pillars 3→2, comparisons 7→4, industry pages 6→3, guest posts 8→4.

### 6. Measurement stack — always ask "does it use what's already live?"

PureBrain has GA4 via GTM-WTDXL4VJ + Microsoft Clarity viy9bnc56x. Lyra's doc didn't mention either and prescribed $227–$327/mo paid tools first. Pattern: free-first for Q1 (GSC, Bing Webmaster, GA4, Clarity, Screaming Frog free), revisit paid at Day 90 with actual data.

### 7. AEO structured data — three assets often missed

- `@type: DefinedTerm` on glossary entries → LLMs use this for "what is X" answers
- `@type: Dataset` on original research → makes data machine-citable, citation magnet
- `/llms.txt` manifest → emerging convention (Anthropic, Mintlify adopting), 1hr build

### 8. Category-creation terms for PureBrain (keep, add, defer)

- Keep: "AI Partnership", "Context Tax"
- Add: "Named AI Partner" (literally what we sell, nobody uses the phrase)
- Harder/slower: "Memory Moat" (more abstract, slower to catch on)

### 9. Title tag current state

Homepage `<title>`: "PURE BRAIN - Your Brain. Your AI. Actual Intelligence! - Agentic AI" (67 chars, uses "PURE BRAIN" not "PureBrain"). Recommended: "PureBrain — The AI Partner That Remembers You" (47 chars).

## Files

- Review delivered: `/home/jared/exports/portal-files/seo-aeo-strategy-review-2026-04-15.md`
- Strategy source: `https://docs.google.com/document/d/1YVKbgxcqVS2MnQ7Tee6-OcxrCGlEJkkwnn4PPPwES6c`
- Research source: `https://docs.google.com/document/d/1U-9ktm4xeNkzNI_Of7qvy9rDBVsEis-wc4GUPqJxagM`
- Draft reply included in the review file, ready for Aether to forward.
