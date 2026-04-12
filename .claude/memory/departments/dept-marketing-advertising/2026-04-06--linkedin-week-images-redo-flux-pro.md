# LinkedIn Week 2026-04-07 Images: Full SOP Redo with FLUX 2 Pro

**Date**: 2026-04-06
**Campaign**: Weekly LinkedIn standalone post images (7 posts)
**Status**: COMPLETE (images generated + filed to Drive, BaaS update pending)

## What Happened

Jared caught that previous LinkedIn images were Playwright HTML renders, not FLUX Pro quality per content-creation-sop. Full redo executed with proper toolchain.

## Pipeline Used

1. FLUX 2 Pro via Replicate API (model: black-forest-labs/flux-2-pro)
2. PIL composite with Oswald Bold font
3. Brand elements per purebrain-social-design skill
4. Google Drive filing per content-creation-sop

## Images Generated (All 7/7 PASS)

| Day | Post | Image Size | FLUX Cost |
|-----|------|-----------|-----------|
| Mon | 88% AI Security Stat | 1776KB | ~$0.05 |
| Tue | Agentic Era Is Here | 2053KB | ~$0.05 |
| Wed | Tool vs Partner | 1392KB | ~$0.05 |
| Thu | 83% Personalization Gap | 1656KB | ~$0.05 |
| Fri | 86% AI Budgets Wasted | 2079KB | ~$0.05 |
| Sat | Transparency 7 Pillars | 2089KB | ~$0.05 |
| Sun | Sunday Reset Myth | 1692KB | ~$0.05 |

Total FLUX cost: ~$0.35

## Quality Gates (All Passed)

- [x] All images created by FLUX 2 Pro + PIL (not HTML render)
- [x] Font: Oswald Bold (verified via getname())
- [x] Dimensions: 1080x1350 (all 7)
- [x] Wordmark per-letter colors correct
- [x] Hexagon logo present
- [x] 80px safe zones
- [x] Dark navy background
- [x] Post-specific CTAs
- [x] FLUX prompts saved

## Google Drive Locations

All in Pending Approval (1Cr6EhkNi0ToBqQs27q0TQzKtCNDGeFwz):
- Mon: 1hsFK4GOar5cC_NpKKTOR9PQG2RhVw3Nz
- Tue: 1W-CdrtCDswliU4KMB4Ko0MStynLIsf78
- Wed: 16q6lEAA_YxdNm609wqxMvpxPIaf6UrBd
- Thu: 14ra3GBUjll8pDfKJXwSGYt4gT0ucnXCu
- Fri: 17lUtwKo4CDSOk-UVmSncGIUhTe967OpG
- Sat: 1C_sxpHoG_zZb86wR2CHnzKSPlVxwZlVl
- Sun: 1SthnD5W14k1yUV6Y9N3eqgTS1e2-3GGj

## Local Paths

All at: /home/jared/exports/portal-files/linkedin-week-2026-04-07/

## Learnings

1. FLUX 2 Pro works reliably for all 7 calls (no fallback needed)
2. Gleb Kuznetsov transition language ("mid-transformation between...") produces dynamic glass imagery
3. Physics terminology (Fresnel edge glow, subsurface scattering) anchors quality
4. PIL composite template from Night 12/13 is production-stable
5. BaaS social dashboard API needs investigation (endpoints return 404)
6. Reference images from Drive were downloaded and studied but all 7 got fresh FLUX generations (themes were unique enough)

## Pending

- BaaS dashboard update (API endpoints not found, needs ST# investigation)
- Reference image move to Live folders (after posts go live)
