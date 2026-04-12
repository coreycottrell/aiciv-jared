# Comparison Pages Password Protection Removal

**Date**: 2026-02-23
**Type**: operational
**Topic**: Removing password protection from 9 exodus/comparison pages on purebrain.ai

## What Happened
9 comparison pages (IDs 752-760) were deployed password-protected by mistake.
Jared flagged as urgent - needed to be made public immediately.

## Fix Applied
Used WordPress REST API to set status=publish and password="" for each page:
```bash
curl -s -X POST \
  -u "Aether:FlFr2VOtlHiHaJWjzW96OHUJ" \
  -H "Content-Type: application/json" \
  -d '{"status":"publish","password":""}' \
  "https://purebrain.ai/wp-json/wp/v2/pages/${PAGE_ID}"
```

## Pages Fixed
- 752: /compare/ (hub page)
- 753: /purebrain-vs-chatgpt/
- 754: /purebrain-vs-claude/
- 755: /purebrain-vs-copilot/
- 756: /purebrain-vs-custom-gpts/
- 757: /purebrain-vs-deepseek/
- 758: /purebrain-vs-gemini/
- 759: /purebrain-vs-jasper/
- 760: /purebrain-vs-perplexity/

## Verification
- HTTP 200 on /purebrain-vs-chatgpt/ and /compare/
- No "post-password-form" in page content
- Elementor cache cleared

## Key Pattern
To remove WP password: POST to pages endpoint with `{"status":"publish","password":""}` - 
empty string clears the password, status:publish ensures it's live.
