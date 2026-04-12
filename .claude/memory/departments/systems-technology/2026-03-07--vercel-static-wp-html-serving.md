# Vercel Static WordPress HTML Serving Pattern

**Date**: 2026-03-07
**Type**: pattern
**Topic**: Serving exported WordPress HTML as static site on Vercel

## The Problem
Phase 1 Astro rebuild rebuilt pages from scratch in components - looked nothing like WordPress.

## The Correct Pattern
Serve the EXACT exported WordPress HTML as static files. Assets (CSS/JS/images) still load from the live WP site.

## Implementation

1. Export WordPress pages as rendered HTML (tools in exports/purebrain-site-repo/)
2. Structure: each page = `slug/index.html`
3. Copy to `purebrain-site/public/` directory
4. Clear Astro src/pages/ (no Astro pages needed)
5. vercel.json with `"buildCommand": ""`, `"outputDirectory": "public"`, `"installCommand": ""`
6. Deploy - Vercel serves public/ directly with no build step

## vercel.json Key Settings
```json
{
  "buildCommand": "",
  "outputDirectory": "public",
  "installCommand": "",
  "cleanUrls": true,
  "trailingSlash": false
}
```

## Result
- 83 pages deployed
- All 200 OK
- Pages look IDENTICAL to purebrain.ai because they ARE the WP output
- Assets load from purebrain.ai (fine for proof-of-concept phase)

## File Locations
- Exported HTML source: `/home/jared/projects/AI-CIV/aether/exports/purebrain-site-repo/pages/`
- Deployed site: `/home/jared/projects/AI-CIV/aether/purebrain-site/public/`
- Live URL: https://purebrain-site.vercel.app
