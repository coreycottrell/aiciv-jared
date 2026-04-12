# content-specialist Learning: Blog & Newsletter Analysis — Session 13

**Date**: 2026-03-18
**Type**: synthesis + live audit + new gap discovery
**Agent**: content-specialist (Session 13 of ongoing audit series)
**Confidence**: high — 28 posts confirmed in cf-pages-deploy, newest post (prompting-is-dead) read in full, Article schema gap verified, LinkedIn newsletter live data fetched

---

## Task Summary

Thirteenth session of ongoing PureBrain.ai blog and Neural Feed audit. Built on all twelve prior sessions (Feb 20 – March 17). New this session: 28th post confirmed (prompting-is-dead, March 17), Article/BlogPosting schema confirmed missing from ALL posts, SEO title tag optimization gap identified for keyword-targeted posts, byline class inconsistency re-confirmed, and new "AI Skills Ladder" pillar post opportunity mapped.

---

## Key New Findings This Session

### 1. Blog Now Has 28 Posts

New post since Session 12:
- `/prompting-is-dead/` — March 17, 2026

Content quality: strong. Operational opening, clean three-part argument (Memory / Agent Orchestration / Workflows), natural product integration.

### 2. Article Schema Gap — First Confirmed This Session

All individual posts have `FAQPage` schema only. No `BlogPosting` or `Article` schema. This means Google cannot identify author, publish date, or article structure from structured data. Affects all 28 posts. Fix is a template-level addition, then retroactive deploy.

### 3. SEO Title Tag Gap on Keyword-Targeted Posts

"Prompting Is Dead" has a 31-character title tag. Target keyword "prompt engineering" does not appear in H1, title tag, or any H2. For posts competing on specific search terms, the keyword must appear in at least one of title tag, H1, or first H2.

### 4. Byline CSS Class Re-Confirmed Inconsistent

`prompting-is-dead` uses `<p class="byline">` — not `.pb-byline`. Same bug as March 14 and March 15 posts (Session 12). Three posts confirmed with wrong class. Should be standardized across all posts.

### 5. "AI Skills Ladder" Pillar Opportunity

"Prompting Is Dead" introduces a three-level AI maturity framework (Level 1 prompt / Level 2 workflow / Level 3 autonomous) as a parenthetical. This framework warrants a dedicated 1,500-word pillar post ("The AI Skills Ladder: Five Levels of Working with AI") that could become the highest-traffic and most-linked post in the archive. It would also serve as a natural internal link hub for every other post.

### 6. Internal Linking — 13 Sessions Without Resolution

Zero internal links in post bodies. Now confirmed in 3 of the 3 most recent posts. This has been the #1 structural gap since Session 2. At 28 posts, the compounding SEO cost is significant.

### 7. Neural Feed Newsletter Subject Line Pattern Reinforced

Data across 13 sessions confirms: second-person direct titles ("Your AI Has No Idea Who You Are") consistently outperform concept/cost titles ("The Hidden Cost of AI Without Memory"). Two recent issues used "Briefing" framing within 48 hours — thematic compression within a 7-day window dilutes both.

---

## Implementation Tracker Status (Session 13)

- DONE: About Aether page
- NOT DONE (critical): Internal linking — 13 sessions
- NOT DONE (6 sessions): Brevo welcome sequence
- NOT DONE (4 sessions): Newsletter reply CTA
- NOT DONE (3 sessions): Byline CSS standardization
- NOT DONE (2 sessions): Pilot Purgatory markdown bug
- NOT DONE (2 sessions): Duplicate byline in March 14 post
- NEW: Article/BlogPosting schema (all posts)
- NEW: Title tag optimization for keyword-targeted posts

---

## Reusable Patterns Documented This Session

**Article schema gap pattern**: FAQPage schema without BlogPosting schema is a common export artifact from WordPress to static sites. The FAQPage schema is often injected by SEO plugins for FAQ blocks; the BlogPosting schema requires explicit templating. Any blog migrated from WordPress to a static export should be audited for this gap.

**SEO title tag keyword check**: For posts targeting a specific search query, run a three-point check: (1) does the keyword appear in the title tag? (2) does it appear in the H1? (3) does it appear in the first H2 or within the first 200 words? If none of these are true, the post will struggle to rank for that term regardless of content quality.

**Thematic compression rule**: At daily newsletter cadence, publishing two issues on the same primary concept within 7 days dilutes both. The second issue should either be separated by 10+ days OR come from a materially different angle (e.g., problem framing vs. proof vs. how-to vs. counterintuitive).

---

## File Location

Full report: `/home/jared/projects/AI-CIV/aether/exports/overnight-content/blog-newsletter-analysis-session13.md`

---

**END MEMORY**
