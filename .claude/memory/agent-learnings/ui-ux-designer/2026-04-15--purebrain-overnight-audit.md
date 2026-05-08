# PureBrain Overnight UX Audit — 30-Day Delta

**Date**: 2026-04-15
**Agent**: ui-ux-designer
**Type**: teaching + operational
**Topic**: Full-page audit, delta vs Feb 16–20 audits, overall score 7.3/10

---

## Delta Since Feb 2026

| Dimension | Feb 16 | Apr 15 | Change |
|---|---|---|---|
| Overall score | ~5.5 | 7.3 | +1.8 (major) |
| Testimonials | Empty placeholders | 22 real named + LinkedIn | FIXED |
| Timeline ("What Happens Next") | Empty | 4 populated items | FIXED |
| Schema.org markup | Basic | Organization+WebSite+WebPage+SoftwareApplication+speakable | UPGRADED |
| LLM discoverability | None | `/llms.txt` + `/llms-full.txt` | NEW, ahead of industry |
| Hidden nav | Yes | Still yes | OPEN |
| Animation overload | 6 concurrent | 6 concurrent | OPEN |
| Accessibility (reduced-motion, skip link, focus ring) | Missing | Still missing | OPEN — now legal risk |
| Two-CTA hero (decision paralysis) | Yes | Yes | OPEN — identified as "blinding weakness" |

## Key Insight (New)
**The work shifted from "fix fundamentals" to "interaction restraint."**
When a site's proof and narrative land, the next ceiling is decision-clarity. Two CTAs competing with a persistent chat widget + waitlist modal = user paralysis even when each element is individually well-designed.

## Reusable Pattern: The "One CTA Per Scroll Screen" Test
For any hero section: if a first-time visitor can articulate "the one thing the page wants me to do right now" in under 3 seconds, the CTA is clear. If they list 2+ options, collapse them.

## Competitive Benchmarks Used
Linear, Vercel, Notion AI, Cursor, Perplexity — each represents a specific discipline PureBrain should borrow:
- Linear: single-CTA obsession
- Vercel: translucent scroll-aware nav
- Notion AI: role-based content segmentation
- Cursor: autoplay hero demo
- Perplexity: framed conversational entry

## Top 3 Recommendations (Impact × Ease)
1. Collapse hero to ONE gated CTA (email → chat) — 2hr, +35–50% lead capture
2. `prefers-reduced-motion` + skip link + focus ring — 3hr, WCAG AA + legal shield
3. Minimal sticky top nav appearing on scroll-up — 3hr, +8–12% multi-section engagement

## Gotchas
- WebFetch 403s on direct purebrain.ai — use staging mirror `purebrain-staging.pages.dev` OR inspect local `exports/cf-pages-deploy/index.html`
- File is 10k+ tokens — MUST read in offset/limit chunks, never whole
- Testimonial count: 22 (I counted in grep). Don't underestimate — this is a wall, not a curation

## Files Referenced
- Source: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/index.html`
- Report: `/home/jared/exports/portal-files/overnight-ux-improvement-report-2026-04-15.md`
- Prior audits: `.claude/memory/agent-learnings/ui-ux-designer/2026-02-{15,16,17,20}-*.md`

## Integration Points
- full-stack-developer: implements Quick Wins 1–6 (~9.5hr)
- conversion-rate-optimizer: runs A/B tests A, B, C in parallel (complements, not duplicates)
- content-specialist: writes objection-handling FAQ section (improvement #9)
- browser-vision-tester: device-matrix screenshots (375/390/412/768px)

---

**END MEMORY**
