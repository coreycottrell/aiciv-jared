# 2026-04-15 — GSC Sitemap DELETE + Title Rewrite Patterns

**Type**: teaching (operational + technique)

## GSC Sitemap DELETE via service account
- `analytics_api.py` defaults to `webmasters.readonly` — not enough for DELETE.
- Solution: re-init creds in a one-off script with full `https://www.googleapis.com/auth/webmasters` scope using same SA file (`.credentials/google-drive-service-account.json`).
- SA must be a verified owner of the GSC property for DELETE to succeed.
- Endpoint: `DELETE https://www.googleapis.com/webmasters/v3/sites/{site}/sitemaps/{url}` — both `site` and sitemap `url` must be URL-encoded. Success = HTTP 204.
- Verify by re-listing after delete.

## Ghost WP sitemaps on CF-Pages sites
- WordPress leaves behind `/sitemap_index.xml`, `/page-sitemap.xml`, `/post-sitemap.xml`, `/category-sitemap.xml` submissions. These keep erroring for years after migration.
- Always audit GSC sitemap list after any CMS migration.

## Title/meta rewrite heuristic (for position 5-7 pages with low CTR)
1. Keep title ≤60 chars so it doesn't truncate.
2. Front-load primary keyword.
3. Add freshness signal (year) when topic is time-sensitive — proven CTR lever.
4. Meta must end with a specific, scannable promise (number + "now" CTA).
5. All 4 title slots (title/og/twitter × 2) should match for quality signal.

## Files
- Draft: `/home/jared/exports/portal-files/seo-rewrite-age-of-ai-agents-2026-04-15.md`
- Source HTML: `exports/cf-pages-deploy/blog/age-of-ai-agents-next-18-months/index.html`
