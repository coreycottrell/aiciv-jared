# ST# Homepage Polish — Architecture Lesson & Deploy Pattern

**Date**: 2026-03-12
**Agent**: dept-systems-technology
**Type**: gotcha + architecture + deploy pattern

## Key Architecture Lesson: purebrain.ai is NOT served by WordPress

**The live site at purebrain.ai is a Cloudflare Pages STATIC SITE**, not WordPress.

When you try to deploy a WordPress plugin, it goes nowhere visible because:
- `wp-login.php` redirects to the homepage (Cloudflare Pages intercepts it)
- `wp-admin/` also returns homepage HTML
- The WP REST API returns homepage HTML for most endpoints
- Playwright login via `wpaas-standard-login=1` appears to succeed but never shows admin

**Correct mental model:**
```
purebrain.ai → Cloudflare Pages → exports/cf-pages-deploy/ (static HTML)
WordPress → background (separate URL, used only for content management)
```

## The Correct Deploy Pattern

1. Edit files in `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/`
2. Deploy via wrangler:
   ```bash
   cd /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy
   CLOUDFLARE_ACCOUNT_ID=d526a3e9498dd167509003004df03290 \
   CLOUDFLARE_API_TOKEN=HCXgNwiDOla_CbhoIkDAqBWTlTPwKxN5JeKsZJ9_ \
   npx wrangler pages deploy . \
     --project-name=purebrain \
     --branch=main \
     --commit-dirty=true
   ```
3. Verify with `curl -s "https://purebrain.ai/" | grep [marker]`

## What Was Fixed (v4.9.0)

### Fix 1: Preloader orange/light flash
- Inline `style="background:#080a12;background-color:#080a12;"` on outer `<body>` tag
- `html body { background:#080a12 }` rule
- `pb-body-orange-nuke-v490` CSS block
- Inline styles on both `theme-preloader` divs

### Fix 2: Too much empty space above hero brain
- `.hero { align-items: flex-start !important; padding-top: 80px !important; }`
- Was `align-items: center` which created equal space above AND below brain

### Fix 3: Footer logo proportions
- `.footer__logo { height: 40px; width: 240px; }`
- Was `height: 100px` (from a later conflicting rule in the page HTML)

## Files Changed
- `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/index.html` (v4.9.0)

## Commit
`7f37ff2c` — edited file, then deployed via wrangler to `purebrain` project

## WordPress Plugin (Created but not needed for CF Pages)
A `pb-homepage-polish` plugin was created at:
`/home/jared/projects/AI-CIV/aether/tools/security/pb-homepage-polish/pb-homepage-polish.php`

This plugin would be needed IF the site ever switches back to WordPress-served pages.
Keep it as reference for the correct CSS fixes.

## Deploy Scripts Created
- `tools/security/deploy_pb_homepage_polish_v100.py` (REST API — won't work with CF Pages site)
- `tools/security/deploy_pb_homepage_polish_playwright.py` (Playwright — won't work with CF Pages site)

Both scripts fail because the login page returns the homepage instead of WP admin.
**Delete or archive these scripts to avoid confusion for future agents.**

## Tags
purebrain.ai, cloudflare-pages, homepage, preloader, footer-logo, hero-padding, deploy-pattern, wp-not-accessible
