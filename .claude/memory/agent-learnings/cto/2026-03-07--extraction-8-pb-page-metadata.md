# Extraction #8: pb-page-metadata plugin

**Date**: 2026-03-07
**Type**: operational
**Agent**: cto

## What Was Done

Extracted the Twitter/X Card meta tag injection block from the security plugin into a standalone plugin.

## Source

- File: `tools/security/purebrain-security/purebrain-security-plugin.php`
- Lines: 1048–1127
- Section label: `g2b) TWITTER/X CARD META TAGS (v6.1.0)`
- First line of block: `// g2b) TWITTER/X CARD META TAGS (v6.1.0)`
- Last line of block: `}, 20 ); // Priority 20 — after Yoast...`

## Output

- File: `tools/security/pb-page-metadata/pb-page-metadata.php`
- Plugin Name: PureBrain Page Metadata
- Task: 8 of 14 in security plugin extraction series

## Replacement Comment (for security plugin)

```
// PAGE METADATA (OG/Twitter) — extracted to pb-page-metadata plugin (2026-03-07)
```

## Key Details

- Hook: `wp_head` at priority 20 (after Yoast at priority 10)
- Covers: twitter:card, twitter:site, twitter:title, twitter:description, twitter:image
- Fallback chain: Yoast twitter meta > Yoast OG meta > post title/featured image > site defaults
- No OG tags touched — Yoast handles og:* natively; this plugin only fills the twitter:* gap
