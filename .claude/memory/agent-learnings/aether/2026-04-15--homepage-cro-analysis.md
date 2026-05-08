# Homepage CRO Analysis — purebrain.ai (2026-04-15)

**Type:** operational + teaching
**Topic:** On-page CRO audit of purebrain.ai homepage

## Key findings
- Page is fast at edge (TTFB ~127ms, 0 render-blocking external scripts) but HTML is 643 KB (238 KB inline CSS + 249 KB inline JS).
- Hero H1 is brand-speak, not outcome-led. Primary CTA "Awaken Your PURE BRAIN" is abstract.
- Waitlist form has 5 fields incl. required 1-5 rating AND pre-checked GDPR consent (legal risk).
- 35 images, 34 lazy-loaded (good), 0 with width/height (CLS risk).
- OG image is a GIF — broken previews on LinkedIn/Slack/iMessage.
- WP REST API not accessible from public domain — CF Pages edge returns homepage HTML for ALL paths including `/wp-json/`, `/wp-admin/`. Analytics must come from Clarity (tag viy9bnc56x) / GA4 / the live WP origin.

## A/B tests proposed (falsifiable)
T1 hero H1 copy, T2 primary CTA label, T3 waitlist field reduction, T4 above-fold trust strip, T5 tier-specific pricing CTA.

## Quick wins
1. Add width/height to img tags (CLS fix)
2. Uncheck consent checkbox (GDPR)
3. Replace OG GIF with static JPG

## Strategic
Re-sequence page, cut form to 2 fields, rewrite H1+CTA for outcome.

## Gotcha
CF Pages deploy catches ALL paths — can't hit WP REST directly from purebrain.ai even with valid basic-auth credentials. Need origin hostname or internal access.

## Deliverable
/home/jared/exports/portal-files/overnight-homepage-cro-analysis-2026-04-15.md
