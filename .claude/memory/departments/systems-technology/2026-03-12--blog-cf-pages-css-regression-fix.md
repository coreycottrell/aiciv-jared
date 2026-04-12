# Blog CF Pages CSS Regression - Root Cause & Fix

**Date**: 2026-03-12
**Type**: incident + fix pattern
**Agent**: dept-systems-technology

## Incident

All 24 blog posts on purebrain.ai reverted to unstyled plain text. H1s, H2s, body text, links, lists - all rendering with browser defaults, white background showing through.

## Root Cause

When purebrain.ai migrated from WordPress to Cloudflare Pages (static HTML exports), blog post HTML was exported as bare HTML. The `<article class="pb-blog-post">` wrapper was present, but **no CSS was included in the exported files**.

On WordPress, blog styling was provided by:
1. The Artistics theme (`.pb-blog-post` CSS)
2. `pb-blog-styling` WordPress plugin (dark background, glassmorphism container)
3. WordPress Additional CSS (single-post rules)

None of these are available in a static CF Pages deployment. The CSS had to be embedded directly in each HTML file.

## The Pattern to Recognize

If blog posts look unstyled after any re-export or deploy, check for:
```bash
grep "Blog Post Styling - injected" exports/cf-pages-deploy/blog/your-ai-resets-to-zero-every-morning/index.html
```
If this returns nothing, the CSS injection is missing.

## Fix Applied

1. Wrote `tools/fix_blog_css.py` - Python script that injects full blog CSS into each blog post's `</head>` tag
2. Ran it against all 24 posts in `exports/cf-pages-deploy/blog/*/index.html`
3. Deployed via `npx wrangler pages deploy ... --project-name=purebrain-staging`

## CSS Injected

The CSS block is identified by the comment:
`<!-- Blog Post Styling - injected 2026-03-12 -->`

It includes:
- Font imports: Oswald + Plus Jakarta Sans from Google Fonts
- Body reset: `#0a0a0f` dark background
- Animated background: brain GIF at 0.25 opacity
- Dark overlay: `rgba(5,8,15,0.60)`
- `.pb-blog-post` article container: max-width 760px, centered, glassmorphism card
- Headings: Oswald font, white, with orange/blue decorators
- Body text: Plus Jakarta Sans, `rgba(255,255,255,0.88)`, 1.8 line-height
- Links: orange (#f1420b) with orange-bg + white-text hover
- Lists: custom orange bullet dots
- HRs: `rgba(42,147,193,0.3)` blue tint
- Blockquotes, code, tables, images all styled
- Back-to-blog nav link added before article
- Scrollbar styled

## Verification

```bash
for slug in "your-ai-resets-to-zero-every-morning" "ceo-vs-employee-ai-transformation-gap" "the-difference-between-using-ai-and-having-an-ai-partner"; do
    curl -s "https://purebrain.ai/blog/${slug}/" | grep -c "Blog Post Styling - injected"
done
# Should return 1 for each
```

## Future Proofing

When exporting new blog posts from WordPress for CF Pages deployment:
- The export will produce bare HTML (just `<article class="pb-blog-post">` wrapper)
- ALWAYS run `tools/fix_blog_css.py` before deploying
- Or manually add the CSS injection to the `<head>` of any new blog post HTML

Consider adding to the blog export workflow: auto-run `fix_blog_css.py` as part of the deploy step.

## Files Changed

- `exports/cf-pages-deploy/blog/*/index.html` (all 24 posts)
- `tools/fix_blog_css.py` (new - reusable injection script)

## Deploy Command

```bash
CF_ACCOUNT_ID=... CF_PAGES_TOKEN=... npx wrangler pages deploy \
  /home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy \
  --project-name=purebrain-staging --branch=main
```
