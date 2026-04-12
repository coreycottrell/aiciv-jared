# Client Page Password-Gated Deployment Pattern

**Date**: 2026-03-02
**Type**: pattern
**Topic**: Deploying client-facing HTML pages to purebrain.ai as password-gated WordPress pages

---

## Deployment Summary

Deployed Jim Estill AI Blueprint as a password-gated page for Danby Appliances.

- Page ID: 1200
- URL: https://purebrain.ai/purebrain-for-danby-appliances/
- Password: DanbyAI2026
- File source: `exports/client-marketing/jim-estill/jim-estill-ai-blueprint.html`

---

## Pattern: Client HTML to WP Password-Gated Page

### Steps

1. Read HTML from `exports/client-marketing/[client]/`
2. Prepend CSS to suppress WP title/breadcrumb/dead space
3. Wrap entire content in `<!-- wp:html --> ... <!-- /wp:html -->`
4. POST to `https://purebrain.ai/wp-json/wp/v2/pages` with:
   - `status: publish`
   - `password: [client-password]`
   - `template: ""` (default, NOT elementor_canvas)
5. Verify: HTTP 201, page ID returned, password gate confirmed on public URL

### CSS Suppression Block (Always Prepend)

```html
<style>
.entry-title, h1.entry-title, .page-title { display: none !important; }
.rank-math-breadcrumb, .breadcrumb, .breadcrumbs, nav.breadcrumb, .breadcrumb-wrapper, #breadcrumbs { display: none !important; }
.entry-header, .page-header, .post-header { display: none !important; margin: 0 !important; padding: 0 !important; }
.entry-content { margin-top: 0 !important; padding-top: 0 !important; }
</style>
```

### Key Notes

- WP REST API returns `password: ""` even after setting it — that is normal behavior
- Password protection confirmed by checking public page for `post_password` form field or "Enter password" text
- Auth: Basic auth with `Aether` user + `PUREBRAIN_WP_APP_PASSWORD` from `.env`
- Template MUST be empty string — never elementor_canvas (strips theme styling)
- Content size ~76KB is fine for WP REST API
