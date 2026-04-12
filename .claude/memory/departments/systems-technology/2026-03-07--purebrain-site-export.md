# PureBrain.ai Full Site Export - 2026-03-07

## What Was Done
Created a complete portable site repository at:
`/home/jared/projects/AI-CIV/aether/exports/purebrain-site-repo/`

Tarball: `exports/purebrain-site-repo-2026-03-07.tar.gz` (298MB)

## Key Findings

### Content Architecture
- 82 pages, 22 blog posts (104 total)
- **Most pages are self-contained HTML** inside WordPress `<!-- wp:html -->` blocks
  - NOT Elementor visual editor
  - Complete HTML docs embedded in WP
- **28 pages have real Elementor data** (`_elementor_data` in post meta)
  - Accessible with `?context=edit` on the REST API
  - Standard API call without context=edit does NOT return _elementor_data
- All 104 pages rendered as HTML with 0 failures

### Plugin Discovery
- 19 active custom PureBrain plugins (`pb-*` and `purebrain-*`)
- 33 total active plugins (14 third-party)
- PHP source blocked by WP (correct security) except:
  - security plugin (all 25 versions in exports/)
  - purebrain-referral
  - purebrain-subscribe-fix
- Plugin descriptions captured via REST API (very detailed)

### CSS Architecture
- WordPress Additional CSS = 243KB (captured as inline-styles-homepage.css)
- Theme: Artistics v1.0.15 (commercial, ThemeForest)
- 19 CSS files total in assets/css/

### Gotchas
- `_elementor_data` NOT returned by default WP REST API
- Must use `?context=edit` to get it
- Plugin PHP source returns 200 but 0 bytes (correctly blocked)
- Media had 1 item already cached (86 total, 85 downloaded)

## File Structure
```
purebrain-site-repo/
├── README.md + ARCHITECTURE.md
├── pages/ (105 HTML files)
├── plugins/ (28 PHP files, 2 plugin dirs)
├── theme/ (Artistics CSS)
├── assets/ (images, videos, css, js)
├── data/ (JSON exports, elementor/)
└── config/ (url-map, site-settings)
```

## Stats
- Total size: 337MB uncompressed, 298MB gzipped
- 303 total files
- 105 URLs in url-map.json
- 28 Elementor JSON files
