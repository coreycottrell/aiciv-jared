# Trust Gap Content Sync: PureBrain → JDS

**Date**: 2026-02-22
**Agent**: full-stack-developer
**Type**: operational
**Topic**: Syncing stub JDS post with full PureBrain article content

---

## Task

JDS post ID 1122 (The AI Trust Gap) was published as a stub - had CSS blocks and a test paragraph but was missing ~14,570 chars of article content including social share icons and CTA block. Full content from purebrain.ai post ID 631 needed to be synced.

## Root Cause

The original dual-publish created the JDS post but something truncated the content to only the initial CSS blocks (chars 0-14032). The article body, FAQ section, social share block, and blog-cta block were all missing.

## Fix Applied

1. Fetched full content from purebrain.ai via REST API with `context=edit` param (gives raw content)
2. Adapted 2 links for JDS:
   - 95% pilots interlink: `purebrain.ai/why-95-percent-of-ai-pilots-fail/` → `jareddsanborn.com/2026/02/21/why-95-percent-of-ai-pilots-fail/`
   - Newsletter link: `purebrain.ai/blog/?utm_source=...` → `jareddsanborn.com/blog/?utm_source=...`
3. Kept as-is: Awakening CTA (`purebrain.ai/#awakening`), AI Partnership Audit link, social share (uses `window.location.href` dynamically)
4. PATCH via POST to `/wp-json/wp/v2/posts/1122` with `{"content": adapted_content}`

## Result

- Content: 14,032 chars → 28,623 chars (fully synced)
- All 12 verification checks passed
- Public URL returns HTTP 200

## Link Adaptation Rules (Reference)

| Link Type | Treatment |
|-----------|-----------|
| Internal blog post links | Replace `purebrain.ai/[slug]` with JDS equivalent URL |
| Newsletter subscribe link | Replace with JDS blog URL |
| Product CTA links (#awakening) | Keep as purebrain.ai - this is the product |
| External tool links (Audit) | Keep as purebrain.ai - product page |
| Social share block | No change - uses `window.location.href` dynamically |

## Credential Notes

- PureBrain: user=`Aether`, env=`PUREBRAIN_WP_APP_PASSWORD`
- JDS: user=`AetherPureBrain.ai`, env=`WORDPRESS_APP_PASSWORD` (has spaces - must `.strip().strip('"')`)
- Both use Basic auth: `base64.b64encode(f"{user}:{pass}".encode()).decode()`
- Use `POST /wp-json/wp/v2/posts/{id}` (not PATCH) with JSON payload to update

---

**End of Memory**
