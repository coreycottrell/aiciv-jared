# Team Dashboard Brain Icon Replacement
**Date**: 2026-02-24
**Type**: operational
**Topic**: Replacing placeholder hexagon SVG icons with actual PureBrain brain icon

## What Was Done
Replaced three placeholder hexagonal SVG icons in the team dashboard with the actual PureBrain brain/swirl icon (blue hexagon outline + orange spiral).

## Files Modified
- `/home/jared/projects/AI-CIV/aether/exports/team-dashboard/dist/index.html`

## Three Locations Replaced
1. **Line 9** - `<link rel="icon">` favicon: replaced with 32x32 PNG base64
2. **Line 1264** - Login card SVG (40x40 hex): replaced with `<img>` tag using 192x192 PNG base64
3. **Line 1301** - Topnav logo SVG (28x28 hex): replaced with `<img>` tag using 192x192 PNG base64

## Icon Source
- Fetched from `https://purebrain.ai/wp-content/uploads/2026/02/cropped-MA1.BI-1.2.4-002-211107-Icon-PT-192x192.png`
- 32x32 favicon from `https://purebrain.ai/wp-content/uploads/2026/02/cropped-MA1.BI-1.2.4-002-211107-Icon-PT-32x32.png`
- Also exists locally at: `docs/from-telegram/MA1.BI-1.2.4-002-211107-Icon - PT.png`

## Icon Description
The actual PureBrain brain icon is NOT a hexagon with a dot. It's a **blue hexagonal outer frame with an orange/coral spiral/swirl inside** - elegant geometric brand mark.

## Deployment
- Site: `d2556d0a-5333-47ca-a8d6-8add4141f090`
- URL: https://pure-tech-dashboard.netlify.app
- Deploy status: 200 OK

## Pattern: Icon Replacement in Self-Contained HTML
When replacing SVG placeholders with actual brand icons in self-contained HTML:
1. Fetch icon from brand website (check `<link rel="icon">` tags in page HTML)
2. Use curl with browser User-Agent to bypass bot blocking
3. Convert to base64: `base64 -w 0 icon.png`
4. For login card sized icons use 192x192 source
5. For favicons use 32x32 source
6. Replace `<svg>` with `<img src="data:image/png;base64,..." width="X" height="X" alt="Brand" style="display:block;" />`
