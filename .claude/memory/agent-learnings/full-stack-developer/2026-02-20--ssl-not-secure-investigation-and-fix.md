# Memory: SSL Not Secure Investigation and Fix

**Date**: 2026-02-20
**Type**: operational + teaching
**Agent**: full-stack-developer

## Task
Investigated "Not Secure" warning on purebrain.ai/pay-test/ and /pay-test-sandbox/ pages after Cloudflare Tunnel was set up (api.purebrain.ai -> localhost:8443).

## Root Cause Analysis

### What Was True
- The `_elementor_data` for pages 439 and 468 WAS correctly updated to use `api.purebrain.ai`
- The Cloudflare Tunnel was working: `api.purebrain.ai` had valid `*.purebrain.ai` wildcard cert from Google Trust Services
- The live HTML (static markup) had ZERO raw IP references or insecure resources
- All script/link/image resources were HTTPS

### What Was Wrong
1. **Page 174 (PureBrain 2.0) `_elementor_data`**: Still had `89.167.19.20:8443` in `LOGGING_ENDPOINT`
2. **Pages 439 and 468 `content.raw`**: Had 8 raw IP occurrences each (though content.raw is NOT rendered by Elementor - only `_elementor_data` is used)

### Key Architectural Detail (CRITICAL)
Elementor pages use `_elementor_data` for rendering, NOT `content.raw`. When `_elementor_edit_mode: builder`, WordPress serves the Elementor-rendered version. `content.raw` is essentially dead code on Elementor pages but still worth cleaning for hygiene.

The JS code in the Elementor HTML widget is NOT present in the static HTML response - Elementor frontend JS injects it dynamically. This means `curl`ing the page shows the widget content is NOT in the initial HTML (Elementor renders it client-side via AJAX or inline data).

## Why "Not Secure" Was Happening

The previous session's investigation (ssl-not-secure-investigation.md) correctly identified that Chrome was blocking fetch() calls to the self-signed cert at `89.167.19.20:8443`. The Cloudflare Tunnel fix was correct but:
- Page 174 was MISSED (its `_elementor_data` still had the raw IP)
- The previous session only fixed pages 439 and 468

## Fixes Applied

1. **Page 174 `_elementor_data`**: Replaced `89.167.19.20` with `api.purebrain.ai` (1 occurrence in LOGGING_ENDPOINT)
2. **Page 439 `content.raw`**: Replaced all 8 occurrences of `89.167.19.20` with `api.purebrain.ai`
3. **Page 468 `content.raw`**: Replaced all 8 occurrences of `89.167.19.20` with `api.purebrain.ai`
4. **Page 174 `content.raw`**: Replaced 1 occurrence

## Verification Results

All 6 pages (11, 174, 338, 383, 439, 468): ALL CLEAN
- `_elementor_data`: 0 IP occurrences
- `content.raw`: 0 IP occurrences
- Live HTML: 0 IP occurrences, 0 http:// references (except w3.org SVG namespaces)
- CDN cache refreshed (age: 0, new last-modified timestamps)

## Pattern: Large Payload WP API Updates

When pushing large _elementor_data (200KB+) via WP REST API, `curl -d` fails with `OSError: Argument list too long`. Use `--data-binary @tmpfile` pattern:

```python
import tempfile, os, json, subprocess

payload = json.dumps({"meta": {"_elementor_data": fixed_elem}})
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    f.write(payload)
    tmp_file = f.name

subprocess.run(['curl', '-s', '-X', 'POST', '-u', f'Aether:{WP_PASS}',
    f'https://purebrain.ai/wp-json/wp/v2/pages/{page_id}',
    '-H', 'Content-Type: application/json',
    '--data-binary', f'@{tmp_file}'], capture_output=True, text=True)

os.unlink(tmp_file)
```

## CDN Cache Behavior

Cloudflare (cf-cache-status: HIT) serves the cached version. After WP REST API updates:
- The CDN cache refreshes when WordPress updates the page modification time
- The `last-modified` header updates to the new modification time
- Cache `age` resets to 0 for new requests

## SSL Certificate for api.purebrain.ai

Valid `*.purebrain.ai` wildcard cert issued by Google Trust Services (WE1):
- Subject: CN=purebrain.ai
- SAN: *.purebrain.ai matches api.purebrain.ai
- Expires: May 12 2026
- TLS: TLSv1.3

## Files Affected

- WordPress pages 11, 174, 338, 383, 439, 468 (all via WP REST API)
- No local files modified
