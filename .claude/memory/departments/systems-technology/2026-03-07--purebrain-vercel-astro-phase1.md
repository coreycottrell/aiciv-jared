# PureBrain.ai Vercel Migration — Phase 1 Complete

**Date**: 2026-03-07
**Agent**: dept-systems-technology
**Status**: Phase 1 COMPLETE — Build passes, 24 pages generated

---

## What Was Built

Astro v5.18.0 project at `/home/jared/projects/AI-CIV/aether/purebrain-site/`

### Project Structure
```
purebrain-site/
├── src/
│   ├── layouts/BaseLayout.astro       # Shared layout: head, nav, footer, GTM
│   ├── pages/
│   │   ├── index.astro                # Homepage (hero, memory card, demo video, pricing, blog preview)
│   │   └── blog/
│   │       ├── index.astro            # Blog listing page
│   │       └── [...slug].astro       # Dynamic blog post pages
│   ├── components/
│   │   ├── Header.astro
│   │   ├── Footer.astro
│   │   ├── BlogCard.astro
│   │   └── TransparencySection.astro
│   ├── styles/global.css              # Brand CSS (dark theme, colors, typography)
│   └── content/blog/                  # 22 WP posts as markdown
├── astro.config.mjs                   # site, trailingSlash, output:static
├── vercel.json                        # Security headers (HSTS, X-Frame-Options, etc.)
└── src/content.config.ts             # Content collection schema
```

### Build Results
- 24 pages built successfully, 0 errors
- Homepage, blog listing, 22 blog post pages
- GTM-WTDXL4VJ integrated
- `pb-blog-post` class preserved on all blog pages

---

## Key Technical Decisions

### 1. Blog URL Structure
- WP blog posts are at `/[slug]/` (not `/blog/[slug]/`)
- Astro blog posts built at `/blog/[slug]/` — Phase 2 needs redirect rule in vercel.json
- Current WP site stays live, so no URL conflict yet

### 2. Dark Background Enforcement
- `#080a12` hardcoded in global.css with `!important` on body/html
- CSS variable `--pb-dark` used throughout
- Applied at BaseLayout level (every page inherits)

### 3. Content Collection
- All 22 WP posts fetched via REST API and converted to markdown with frontmatter
- Frontmatter: title, description, date, slug, category, featuredImage, ogImage, wpId, draft
- Files named: `YYYY-MM-DD--[slug].md`

### 4. PUREBRAIN Color Rule
- Implemented via `.pb-logo .blue` and `.pb-logo .orange` CSS classes
- BaseLayout nav, Footer, Homepage hero all follow: PUREBR=blue, AI=orange, N=blue

### 5. Video Background
- Hero background video from WP CDN (not re-hosted yet)
- `opacity: 0.4` — no overlay issues
- MP4 source: `purebrain.ai/wp-content/uploads/2026/02/Pure-Brain-Demo-Video-real-compression-and-sizing.mp4`

---

## Phase 2 Next Steps (Priority Order)

1. **URL redirects** — add `/[slug]/` → `/blog/[slug]/` redirects in vercel.json (or keep WP URLs as canonical)
2. **Vercel deploy** — `npx vercel --prod --yes` from purebrain-site/
3. **Compare page** — `/compare/` migration
4. **Why PureBrain page** — `/why-purebrain/` migration
5. **Mission Vision Values** — `/mission-vision-values/` migration
6. **Asset hosting** — migrate featured images to Vercel/R2 (currently served from WP)
7. **Chatbox integration** — re-integrate PureBrain chat widget
8. **Blog post cleanup** — HTML-to-markdown conversion needs QA on complex posts

---

## Patterns Learned

- Astro v5 uses `content.config.ts` (not `config.ts` in content dir) for collection schemas
- Astro v5 uses `glob` loader from `astro/loaders` — new API vs v4
- WP REST API: use `_fields` param to reduce payload size
- WP homepage is Elementor canvas — no standard `<header>` tag, nav extracted from page content
- GTM ID: `GTM-WTDXL4VJ`
- WP Credentials: `PUREBRAIN_WP_USER` + `PUREBRAIN_WP_APP_PASSWORD` in .env

---

## Files

- Project root: `/home/jared/projects/AI-CIV/aether/purebrain-site/`
- Build output: `/home/jared/projects/AI-CIV/aether/purebrain-site/dist/`
- Raw WP posts: `/tmp/wp_posts_raw.json`
