# Analytics Task Scope Boundary (SEO vs Marketing)

**Date**: 2026-04-14
**Type**: teaching
**Agent**: seo-specialist

## Context
Received an overnight task to deep-dive GA4 + Google Search Console + Microsoft Clarity across 30-90 day windows and produce a 1500-2000 word insights report at `/home/jared/exports/portal-files/overnight-analytics-insights-2026-04-15.md`.

## Decision
Declined full-scope execution. Routed back for MA# dispatch.

## Reasoning
- My domain: on-page SEO, sitemaps, JSON-LD schema, og:image verification, robots.txt, internal linking, meta/title audits, and interpreting Search Console specifically for SEO actions.
- Out of my domain: GA4 traffic/conversion analysis, Clarity UX heatmaps/rage clicks, cross-platform analytics synthesis. That is analytics-specialist / MA# territory.
- Constitutional rule (CLAUDE.md): dept-first routing, never skip dept manager. Analytics deep-dive → MA# → analytics-specialist.

## What I Can Own
The Search Console slice only, when dispatched by MA#:
- Top queries + CTR (90 days)
- Low-CTR-high-impression opportunities (meta rewrite candidates)
- Average position by page
- Mobile vs desktop
- Indexing coverage issues
- SEO actions (meta, schema, internal linking)

## Access Blockers Documented (for whoever runs it)
1. GA4 — need service account as Viewer on property, GOOGLE_APPLICATION_CREDENTIALS + GA4_PROPERTY_ID in .env
2. Search Console — service account added as user on `sc-domain:purebrain.ai` or https property
3. Clarity — Data Export API requires Bearer token generated in Clarity project settings (Jared action)
4. Existing `.credentials/oauth-token.json` (Drive scope) insufficient — needs `analytics.readonly` + `webmasters.readonly` scopes added via re-consent

## Anti-Pattern Avoided
Did NOT fabricate analytics data. Without API access or cached exports, any numbers would be invented. Flagged blockers instead.

## Next Time
If Jared or MA# sends SEO-only analytics (Search Console), accept it. If it spans GA4/Clarity, bounce to MA# immediately with this memory as justification.
