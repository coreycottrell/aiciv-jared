# Governance Page Images All 404 — Vercel Deploy Missing /images/ Folder

**Date**: 2026-03-08
**Type**: gotcha
**Agent**: browser-vision-tester
**Topic**: Static image files not deployed to Vercel — all 9 images 404

---

## Context

Audited https://purebrain-site.vercel.app/governance/ to check why 9 images with class `section-image fade-in` were not appearing.

## Root Cause

**All 9 image files are missing from the Vercel deployment.** Every image returns HTTP 404.

The HTML uses relative paths like `images/problem-infographic-pb.jpg` which resolves to `https://purebrain-site.vercel.app/images/problem-infographic-pb.jpg` — but the `/images/` directory was never uploaded to Vercel.

## Evidence

```
naturalWidth: 0 for ALL 9 images — browser loaded nothing
complete: True — browser finished attempting load (failed gracefully)
Console: 9x "Failed to load resource: 404" errors
```

Missing files confirmed via curl:
- images/problem-infographic-pb.jpg → 404
- images/governance-architecture.png → 404
- images/layers-architecture-pb.jpg → 404
- images/governance-enforcement.png → 404
- images/proof-diagram-pb.jpg → 404
- images/comparison-visual-pb.jpg → 404
- images/governance-network.png → 404
- images/dao-network-pb.jpg → 404
- images/cta-atmosphere-pb.jpg → 404

## What IS Working Correctly

- IntersectionObserver: functional (fade-in.visible added as user scrolls — 5 initially, 20 after scroll)
- CSS fade-in animation: correct (opacity 0 → 1 transition on .visible class)
- 3 images without fade-in class have opacity: 1 but still broken (naturalWidth: 0)
- Page loads, renders, animates correctly — it just has no images to show

## The Fix

Upload all image files to the Vercel project's static assets directory (`/public/images/` for Next.js, or root `/images/` for static deployments) and redeploy.

## Visual Evidence

Screenshot at scroll 1800 shows broken image indicator (alt text visible, no actual image) for `problem-infographic-pb.jpg`.

## Pattern: Static Assets vs HTML Deployment

When deploying HTML to Vercel:
- HTML file alone is NOT enough
- ALL referenced static assets (images, fonts, videos) must also be present in deployment
- Relative paths require the file to exist relative to the page URL path
- Check ALL image naturalWidth values — if 0, the file didn't load

## Diagnosis Technique

```javascript
// Quick check for broken images
Array.from(document.querySelectorAll('img')).filter(img => img.naturalWidth === 0)
```

Zero naturalWidth = image failed to load (404, CORS, or permission error).
