# CRO v3 Analysis: purebrain.ai Homepage (delta from v2)

**Date**: 2026-05-08
**Type**: operational + teaching
**Agent**: conversion-rate-optimizer (overnight task 3)

## Key Findings (delta from v2 Apr 16)

### Persistent unresolved issues (3 weeks later)
- Consent checkbox STILL pre-checked at line 8627 (GDPR risk + still no helper text on locked CTAs)
- "Activate Keen Now" pricing CTAs unchanged (lines 8679, 8735, 8797) — internal product name still leaking
- Waitlist form STILL 7 fields with required textarea (lines 7757–7813)

### New observations not captured in v2
- **Testimonials = 22 cards** (not 21 — counted via `grep -c "testimonial-card__quote"`)
- **Microsoft Clarity ID: `viy9bnc56x`** — installed and live; this is the data goldmine
- **GTM also installed** — full analytics stack present, just under-leveraged
- WP backend probes (`/wp-json`, `/wp-admin`, `/wp-login.php`) all return 404 → **CF Pages serves static, no live WP at this domain**. Backend analytics access only via Clarity dashboard or WP admin login (not public-probable).
- Page structure: 13 sections, **testimonials are section 12 of 13** (after pricing) — biggest structural CRO miss on the page
- Hero buries the real value prop (identity-discovery AI) as 4th line of body copy

### Top 3 A/B Tests for v3
1. T1 trust strip in hero (existing testimonial headshots)
2. T3 testimonials moved above pricing (DOM reorder)
3. T4 pricing CTA copy ("Start with Awakened" instead of "Activate Keen Now")

### Quick wins shippable in <1 hr each
- "Activate Keen Now" → "Start with [Tier]" (3 button text replacements)
- Hero CTA micro-copy "No credit card · ~5 minutes"
- Uncheck the GDPR consent checkbox default

## Dead Ends
- WP REST API still 404 from public — never going to be probable; must use Clarity / GTM dashboards directly
- WebFetch on purebrain.ai still 403 (CF bot protection); curl with default UA works fine for this site

## Files Referenced
- `/home/jared/projects/AI-CIV/aether/exports/portal-files/overnight-task3-purebrain-page-analysis-2026-05-08.md` (deliverable)
- `/tmp/purebrain-home.html` (16,341 lines fetched 2026-05-08)
- Prior: `.claude/memory/agent-learnings/conversion-rate-optimizer/2026-04-16--homepage-cro-v2-pricing-mobile-competitor.md`

## Teachings
1. v2 → v3 delta tracking surfaces "persistent unresolved" issues; these have HIGHER priority than new theories because they've already failed to ship.
2. Testimonial misplacement (after pricing) is the single biggest structural opportunity on the page — 22 cards of unactivated proof.
3. Always probe WP endpoints early so you can tell ${HUMAN_NAME} where real analytics live (Clarity ID `viy9bnc56x`).
4. Hero atmospheric effects (vortex, particles, pulse) cost mobile battery AND don't improve clarity. Test removing on mobile before adding more.
5. When in doubt about what to test next, route ${HUMAN_NAME} to Clarity heatmaps for 1 hour — better than another static analysis.
