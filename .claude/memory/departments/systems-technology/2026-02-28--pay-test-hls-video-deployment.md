# HLS Video Player Deployment - pay-test Page 439

**Date**: 2026-02-28
**Agent**: dept-systems-technology
**Type**: deployment | pattern | gotcha

---

## What Was Done

Deployed HLS video player (`portal-enhanced-v1`) to purebrain.ai/pay-test (page ID 439).

Video source: Cloudflare R2
- `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/demo/portal-enhanced-v1/master.m3u8`
- `https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev/videos/demo/portal-enhanced-v1/poster.jpg`

## Page Architecture

Page 439 is a single giant Elementor HTML widget (`elementor_canvas` template). The widget contains:
- A full self-contained HTML page (DOCTYPE through </html>)
- Widget ID: `292c72a`
- Parent Elementor container: `c4d524c`

## Insertion Point

Video section was inserted BEFORE the "WHAT IS PUREBRAIN" section comment:

```
ANCHOR = '\n    <!-- ============================================\n         WHAT IS <span class=\"text-blue\">PURE</span>'
```

This puts the video between the hero marquee (scrolling capabilities text) and the About section.

## Section IDs in Page (in order)
1. `#hero` (data-atmosphere="awakening") - hero section with portal vortex
2. Marquee scrolling capabilities bar
3. **`#demo-video`** - OUR NEW VIDEO SECTION (inserted here)
4. `#about` - "What is PureBrain"
5. `#value-pyramid` - value proposition pyramid
6. `#capabilities` - capabilities grid
7. `#awakening` (chat-section) - chatbox / awakening flow

## Verification Results

- `_elementor_data` length: 444173 -> 447322 (diff: +3149 chars - correct)
- `pb-demo-video-section` class: CONFIRMED present
- `master.m3u8` HLS source: CONFIRMED present
- `r2.dev` CDN references: CONFIRMED present
- Chatbox override (`pb-chatbox-override`): INTACT
- PayPal integration: INTACT
- Pricing section: INTACT
- Page modified timestamp: 2026-02-28T19:34:33

## Cache Behavior (GOTCHA)

The rendered HTML (fetched via browser/curl) does NOT immediately show the update because:
1. Elementor stores rendered HTML in server-side file cache
2. Cloudflare CDN caches the rendered output
3. Password-protected pages add another layer

**What works for cache clearing:**
- `DELETE /wp-json/elementor/v1/cache` - returns 200 (works)
- POST to autosave endpoint - triggers cache invalidation hooks

**What does NOT work:**
- `objectcache/v1/flush` - 403 Forbidden (blocked by nginx)
- Cloudflare API purge (no CF credentials in .env)
- `wp-json/cloudflare/v1/purge` - 404

**Resolution:** Elementor cache auto-clears on next page admin save OR after TTL expires. The _elementor_data DB update IS confirmed - Elementor will serve the new HTML once cache expires.

## Pattern for Future Elementor Page Updates

```python
import requests, json

WP_USER = 'Aether'
WP_PASS = 'FlFr2VOtlHiHaJWjzW96OHUJ'
BASE = 'https://purebrain.ai/wp-json/wp/v2'

# 1. Fetch
data = requests.get(f'{BASE}/pages/{PAGE_ID}', params={'context': 'edit'}, auth=(WP_USER, WP_PASS)).json()
elem_data = data['meta']['_elementor_data']

# 2. Modify (string replacement in the JSON-encoded elementor_data string)
VIDEO_HTML = json.dumps(VIDEO_SECTION_HTML)[1:-1]  # JSON-escape without surrounding quotes
new_elem_data = elem_data.replace(ANCHOR, VIDEO_HTML + ANCHOR, 1)

# 3. Push
requests.post(f'{BASE}/pages/{PAGE_ID}', auth=(WP_USER, WP_PASS), json={'meta': {'_elementor_data': new_elem_data}})

# 4. Clear cache
requests.delete('https://purebrain.ai/wp-json/elementor/v1/cache', auth=(WP_USER, WP_PASS))
```

## HLS Player Pattern

The player uses hls.js as a dynamic loader with graceful fallback for Safari (native HLS):

```javascript
(function(){
  var V = document.getElementById('pb-video-portal-enhanced-v1');
  if(!V){return;}  // Always guard with null check
  var URL = '...master.m3u8';
  var HLS = 'https://cdn.jsdelivr.net/npm/hls.js@1.5.7/dist/hls.min.js';
  function init(Hls){
    if(Hls.isSupported()){ /* Chrome/FF path */ }
    else if(V.canPlayType('application/vnd.apple.mpegurl')){ /* Safari path */ }
  }
  if(typeof Hls !== 'undefined'){init(Hls);return;}
  // Dynamic load
  var s = document.createElement('script');
  s.src = HLS; s.async = true;
  s.onload = function(){if(typeof Hls !== 'undefined')init(Hls);};
  document.head.appendChild(s);
})();
```

## Files Modified

- `/home/jared/projects/AI-CIV/aether/.claude/memory/departments/systems-technology/2026-02-28--pay-test-hls-video-deployment.md` (this file)

## Existing Functionality Preserved

All confirmed INTACT:
- `pb-chatbox-override` script (timer override 15min->30min)
- PayPal integration
- Pricing section
- Hero/portal vortex animation
- Social proof counter
- Guarantee badge
- Exit popup
