# marketing-strategist Learning: Competitor Exodus Expansion Strategy

**Date**: 2026-02-23
**Type**: synthesis
**Agent**: marketing-strategist
**Confidence**: high

---

## Task Summary

Built comprehensive expansion strategy for PureBrain's Competitor Exodus Program. Jared has 3 existing pages (ChatGPT, Copilot, Jasper). Asked to recommend which competitors to target next and whether to build a hub page, individual pages, or both.

---

## Key Decisions Made

### 1. Build Both Hub + Individual Pages

Hub page = multi-competitor switching portal, captures "frustrated but undecided" visitors, ranks for category-level SEO. Individual pages = deep-dive, rank for specific "[competitor] alternative" queries. They interlock: hub links to individual pages, individual pages link back to hub.

### 2. Top 5 New Individual Pages (Ranked)

1. Gemini — 3B+ Google users bundled in by default, frustrated by Google having all their data but Gemini barely using it. "So close yet so far" frustration.
2. DeepSeek — Time-sensitive privacy crisis. Banned in 7+ countries. User data going to China. Peak search volume now.
3. Claude — Sensitive: PureBrain uses Claude as backbone. Framing: "same engine, different relationship." Needs Jared approval before build.
4. Perplexity — Sophisticated ICP (knowledge workers who care about info quality). Frustration: research tool that answers questions but doesn't know you.
5. Custom GPTs — Power users who tried to solve the personalization problem themselves and hit the ceiling. "You built a tool. We built a partner."

### 3. Core Message Across All Pages

Every competitor is a TOOL. PureBrain is a PARTNER. Tools forget you when you close the tab. Partner remembers who you are. The frustration is not capability — it is the feeling of starting over every single time.

---

## Patterns Worth Noting

### Competitor Exodus Page Template Works — Don't Reinvent

The existing 3-page architecture (gradient strip → pain section → quiz → email gate → persona result → CTA → comparison table) is proven. New pages should use the same HTML template with these unique elements: competitor brand color, headline, pain cards, quiz questions, 4 personas, comparison table rows.

### DeepSeek = Most Time-Sensitive

Search volume for "deepseek alternative" is at peak now (Feb 2026). Multiple government bans, security researcher findings, Congressional warnings. Build this page before any other new page.

### Claude Page Requires Human Approval

PureBrain is built on Claude. The page must be factually fair (Claude is excellent; Anthropic chose not to build a relationship layer in the consumer product). Jared must approve the framing before development begins to avoid any impression of biting the hand that feeds.

### Hub Page UX Pattern

16-20 competitor tiles in a grid. On click: content panel slides open with (1) what competitor does well, (2) where it leaves you, (3) what PureBrain does differently, (4) CTA. Vanilla JS state management, CSS transitions, no framework needed. Short quiz below the grid captures email to Brevo List 3.

---

## SEO Opportunity Summary

DeepSeek: 8,000-20,000 monthly searches (trending up now)
Hub page: 5,000-15,000 monthly searches (category-level)
Gemini: 3,000-8,000 monthly searches
Claude: 2,000-5,000 monthly searches
Perplexity: 1,500-4,000 monthly searches
Custom GPTs: 1,000-3,000 monthly searches

Estimated total organic traffic at 90 days post-launch: +800-2,000 monthly clicks, +50-150 email captures/month via quiz.

---

## File Reference

Full strategy: `/home/jared/projects/AI-CIV/aether/exports/competitor-exodus-expansion-strategy.md`

Existing exodus pages (template to clone):
- `/home/jared/projects/AI-CIV/aether/exports/competitor-exodus-chatgpt.html`
- `/home/jared/projects/AI-CIV/aether/exports/competitor-exodus-copilot.html`
- `/home/jared/projects/AI-CIV/aether/exports/competitor-exodus-jasper.html`

Full-stack-developer memory on page architecture:
- `.claude/memory/agent-learnings/full-stack-developer/2026-02-23--competitor-exodus-program-3-pages.md`

---

**END MEMORY**
