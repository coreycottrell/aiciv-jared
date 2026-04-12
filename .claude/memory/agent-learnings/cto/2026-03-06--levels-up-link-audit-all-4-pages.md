# CTO Memory: Levels-Up Link Audit — All 4 Pricing Pages

**Date**: 2026-03-06
**Type**: operational
**Topic**: "How This Levels You Up" link missing from all 4 pricing pages; deployment script created

---

## Task
Audit 4 pricing pages for "How This Levels You Up →" link below CTA buttons.
Add link where missing.

## Findings

| Page | Status | Notes |
|------|--------|-------|
| /partnered/ | MISSING | CTA: "Get Partnered Now →" / "Activate Your Partnered AI →" |
| /unified/ | MISSING | CTA: "Activate Unified" (.pb-activate-btn) |
| /pay-test-2/ (ID 689) | MISSING | Password-protected; multi-tier |
| /pay-test-sandbox-3/ (ID 1232) | MISSING | Confirmed by browser-vision-tester 2026-03-04 |

## Link Destination Mapping
- Partnered CTA → /partnered-how-this-levels-you-up/
- Unified CTA → /unified-how-this-levels-you-up/

## Known Page IDs
- pay-test-sandbox-3 = ID 1232
- pay-test-2 = ID 689 (from exports/package-test-2/ folder name)
- partnered-how-this-levels-you-up = ID 1262
- unified-how-this-levels-you-up = ID 1263

## Known Button IDs on sandbox-3
- proCta = Awakened
- partnerCta = Partnered (inject partnered link after this)
- unifiedCta = Unified (inject unified link after this)

## Deployment Script
`/home/jared/projects/AI-CIV/aether/tools/deploy_levels_up_links.py`

Needs Bash-capable agent to execute (dept-systems-technology).

## Link HTML
```html
<div class="pb-levels-up-link" style="text-align:center;margin-top:14px;margin-bottom:4px;">
  <a href="https://purebrain.ai/[tier]-how-this-levels-you-up/"
     style="color:#00bcd4;font-size:0.875rem;font-weight:500;text-decoration:none;...">
    How This Levels You Up →
  </a>
</div>
```
Color: #00bcd4 (teal/cyan)

## Deployment Pattern
Same as pricing-deployment-688-pattern.md:
- Use Python urllib for large payloads
- Update content.raw (wp:html block)
- Inject after button element by ID or text match
- Clear Elementor cache after
