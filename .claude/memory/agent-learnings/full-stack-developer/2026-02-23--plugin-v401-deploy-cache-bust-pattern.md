# Plugin v4.0.1 Deploy + Cache Bust Pattern

**Date**: 2026-02-23
**Agent**: full-stack-developer
**Type**: operational + gotcha

## What Was Done
Deployed purebrain-security-plugin.php v4.0.1 to purebrain.ai.
Changed "every week" → "every day" in 3 plugin locations (lines 90, 2281, 2973).

## Key Pattern: Plugin Deploy + Page Cache

**Problem**: After a successful plugin deploy (CodeMirror set + file saved), the live page still shows OLD plugin-injected HTML ("every week" instead of "every day").

**Root Cause**: GoDaddy/WordPress page cache serves the previously rendered HTML. The plugin PHP changed but the cached page output is stale.

**Solution**: After deploy + Elementor cache clear, also **touch the post** via WP REST API:
```python
import json, urllib.request
payload = json.dumps({'status': 'publish'}).encode()
req = urllib.request.Request(
    'https://purebrain.ai/wp-json/wp/v2/posts/696',
    data=payload,
    method='POST',
    headers={'Authorization': f'Basic {auth}', 'Content-Type': 'application/json'}
)
# HTTP 200 = post touched, page cache busted
```

This triggers WordPress to regenerate the page cache. The next fetch picks up fresh PHP-rendered output.

## Standard Deploy Sequence (Updated)
1. Validate plugin content locally
2. Playwright: login → plugin editor → set CodeMirror → save
3. Clear Elementor cache: DELETE /wp-json/elementor/v1/cache (HTTP 200 with app password)
4. **Touch relevant posts**: POST /wp-json/wp/v2/posts/{id} with `{"status": "publish"}`
5. Verify live page (no-cache headers) - should show updated content

## Verification Gotchas
- **Transparency API is POST-only** (no GET route). HTTP 404 on GET is expected/normal.
- **v2.9.0 / v3.8.0 references** in the origin story post are INTENTIONAL (version history in transparency section). Don't flag as errors.
- **"every week" appeared 2x on live page** even though plugin PHP had "every day" - always bust page cache after plugin deploy.

## File References
- Plugin: `tools/security/purebrain-security/purebrain-security-plugin.php`
- Deploy script: `tools/security/deploy_plugin_v401_purebrain.py`
- Origin story post ID: 696
- Screenshots: `exports/screenshots/plugin_v401_purebrain_deploy.png`
