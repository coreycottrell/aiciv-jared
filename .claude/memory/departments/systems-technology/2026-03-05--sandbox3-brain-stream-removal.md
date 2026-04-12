# Sandbox-3 Brain Stream CTA Removal

**Date**: 2026-03-05
**Type**: fix / elementor-surgery
**Page**: purebrain.ai/pay-test-sandbox-3/ (WP page ID 1232)

## What Was Removed

A 5,746-character block from the Elementor HTML widget (`_elementor_data`) containing:
- JS IIFE: `window.showBrainStreamButton()` function
- CSS styles for `#pb-brain-stream-wrapper`
- HTML: `div#pb-brain-stream-wrapper` with heading "Your AI is ready", button "Click to Connect to Your AI's Brain Stream", subtitle "Your personalized AI portal is ready. One tap to enter."

## Why

Jared said: "not sure what this is. delete it as it not even the button they click after payment at the end of the chatbox"

The section was designed to be hidden by default (opacity: 0.35, pointer-events: none) and only activated by `window.showBrainStreamButton(url, aiName)` when the Witness system called it. But it was showing in a dimmed state and Jared didn't want it on this page at all.

## Key Technical Points

1. **The content was in `_elementor_data` meta**, NOT in `post_content` — standard REST API `content.raw` field only showed the small "How This Levels You Up" link injection script.
2. **Elementor HTML widget** stores the entire chatbox (484KB of HTML/CSS/JS) as a single widget inside `_elementor_data`.
3. **Removal boundaries**: The JS block started with `\n\n// ====\n// BRAIN STREAM CONNECT BUTTON` and the HTML ended with `<!-- END BRAIN STREAM CONNECT BUTTON -->`.
4. **curl required for large payloads** — Python's urllib was blocked by Cloudflare (403 error code 1010), but curl with Basic Auth worked fine.

## Procedure

```bash
# 1. Get page data
curl -u "Aether:${WP_APP_PASS}" "https://purebrain.ai/wp-json/wp/v2/pages/1232?context=edit" > page.json

# 2. Extract _elementor_data from meta
# 3. Find and remove the BRAIN STREAM block (python string slice)
# 4. Write payload JSON: {"meta": {"_elementor_data": cleaned_data}}
# 5. POST via curl (not urllib - Cloudflare blocks Python UA)
curl -X POST -u "Aether:${WP_APP_PASS}" -H "Content-Type: application/json" \
  "https://purebrain.ai/wp-json/wp/v2/pages/1232" --data @payload.json

# 6. Clear Elementor cache
curl -X DELETE -u "Aether:${WP_APP_PASS}" "https://purebrain.ai/wp-json/elementor/v1/cache"
```

## Verification

- HTTP 200 on update
- Response `_elementor_data` length reduced from 484354 to 478608 (5746 chars removed)
- Live page curl: 0 matches for "brain-stream", "BRAIN STREAM", "One tap to enter"
- Chatbox JS still present (5 references)
- Page HTTP 200

## Files Referenced

- `/tmp/sandbox3_page.json` — original page data snapshot
- `/tmp/sandbox3_elementor_cleaned.json` — cleaned elementor data
- `/tmp/sandbox3_update_payload.json` — POST payload used
