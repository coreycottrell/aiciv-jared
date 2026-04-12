# Tim Cook Article Card — 4-Page Deployment

**Date**: 2026-03-03
**Type**: deployment pattern
**Pages**: Homepage (11), pay-test-2 (689), pay-test-sandbox-2 (688), pay-test-sandbox-3 (1232)

## What Was Done

Added a clickable Tim Cook article card to 4 purebrain.ai pages, positioned after the `#about` section on each page.

## Card Details

- **Link**: https://purebrain.ai/your-ai-tim-cook/
- **CSS class**: `.pb-tim-cook-card` / `.pb-tim-cook-card-wrapper`
- **Position**: After `</section>` closing tag of `#about` section
- **Design**: PT Blue (#2a93c1) border, PT Orange (#f1420b) label, dark bg, hover effects
- **Comment marker**: `<!-- TIM COOK ARTICLE CARD - Added by Aether 2026-03-03 -->`

## Page Structure (All 4 Pages)

All 4 pages use `elementor_canvas` template with a single HTML widget in Container 0, Element 0:
- `elem[0]['elements'][0]['settings']['html']` = full self-contained HTML page
- Sections: `#hero`, `#about`, `#pb-demo-section`, `#value-pyramid`, `#capabilities`, `#awakening`, `#value`, `#pricing`, `#compare`, timeline, testimonials

## Technical Pattern

1. Fetch page via `GET /wp-json/wp/v2/pages/{id}?context=edit` (curl with User-Agent required)
2. Parse `meta._elementor_data` as JSON
3. Extract `elem[0]['elements'][0]['settings']['html']`
4. Find `#about` section closing `</section>` (track depth for nested sections)
5. Inject card HTML after it
6. POST updated `_elementor_data` via `POST /wp-json/wp/v2/pages/{id}` with JSON body
7. Clear Elementor cache: `DELETE /wp-json/elementor/v1/cache`

## Critical: Python urllib vs curl

- Python urllib gets 403 Forbidden from Cloudflare WAF on purebrain.ai
- curl with `-H "User-Agent: Mozilla/5.0..."` works correctly
- Use `subprocess.run(['curl', ...])` for all purebrain.ai WP API calls

## Verification

- Source confirmed via WP REST API: all 4 pages have `pb-tim-cook-card` in `_elementor_data`
- Homepage visible at https://purebrain.ai/ (public)
- Pay-test pages require bypass code to view publicly (expected)
- Elementor cache cleared post-deployment

## Card HTML Insertion Logic

```python
def inject_card(html, card_html):
    # Find <section ... id="about" ...>
    # Track depth to find matching </section>
    # Insert card after closing </section>
    # Fallback 1: before #pricing section
    # Fallback 2: before </body>
```
