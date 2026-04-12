# Memory: purebrain.ai Homepage Canvas Animation Performance Fixes

**Date**: 2026-02-24
**Type**: teaching
**Agent**: full-stack-developer

## Task

Fix 3 critical performance issues + Issue 9 (visibilitychange) in the canvas particle animation system on purebrain.ai homepage.

## Critical Discovery: Elementor Data vs WP Content

The purebrain.ai homepage (page ID 11) uses Elementor canvas template. The animation code lives INSIDE `_elementor_data` meta field, NOT in `content.raw`.

- `content.raw` is the fallback/raw HTML (314KB) - updating this has NO effect on live page
- `_elementor_data` (334KB JSON string) is what Elementor actually renders
- The HTML page content is stored as a JSON string inside Elementor's widget `settings.html` field
- Newlines in the JSON string are encoded as `\n` (backslash-n two chars, not actual newlines)
- Double quotes in HTML attributes are encoded as `\"`

### How to update the live page:
```python
# 1. Fetch with context=edit to get _elementor_data
r = requests.get('https://purebrain.ai/wp-json/wp/v2/pages/11?context=edit', auth=auth)
el_data_str = r.json()['meta']['_elementor_data']

# 2. String-replace in the JSON string (encode newlines as \\n before inserting)
new_code_encoded = new_code.replace('\\', '\\\\').replace('\n', '\\n')
new_el_data = el_data_str[:start] + new_code_encoded + el_data_str[end:]

# 3. Push via meta update
requests.post('https://purebrain.ai/wp-json/wp/v2/pages/11', auth=auth,
    json={'meta': {'_elementor_data': new_el_data}})

# 4. Clear Elementor cache
requests.delete('https://purebrain.ai/wp-json/elementor/v1/cache', auth=auth)
```

## What Was Changed

### Issue 1: Cached dimensions
- **Before**: `canvas.offsetWidth`, `canvas.offsetHeight`, `window.innerWidth` read inside every rAF callback (108 style recalculations per second)
- **After**: Added `cachedCanvasW`, `cachedCanvasH` variables, updated only in `resizeCanvasAndCache()` on `resize` event
- Also updates viewport-aware `activeFlow`, `activeNeural`, `activeEnergy` counts on resize

### Issue 2: Float32Array typed arrays (no GC)
- **Before**: `FlowParticle`, `NeuralNode`, `EnergyPulse` classes instantiated as heap objects, never reused
- **After**: Pre-allocated `Float32Array` / `Uint8Array` typed arrays for all particle properties
  - `fp_x`, `fp_y`, `fp_size`, `fp_speedX`, `fp_speedY`, `fp_opacity`, `fp_pulseSpeed`, `fp_pulseOff`, `fp_colorRatio`, `fp_curOpa` (MAX_FLOW=150)
  - `nn_x`, `nn_y`, `nn_size`, `nn_pulsePhase`, `nn_isOrange`, `nn_curSize` (MAX_NEURAL=40)
  - `ep_x`, `ep_y`, `ep_targetX`, `ep_speed`, `ep_width`, `ep_opacity`, `ep_isOrange` (MAX_ENERGY=5)
- Particles reset in-place via `initFlowParticle(i)` etc., never allocating new objects
- Animation loop uses `for` loops with index access, not forEach with closure allocation

### Issue 3: Viewport-aware particle counts
- **Before**: Always 150 flow + 40 neural + 5 energy regardless of device
- **After**: `getParticleConfig()` returns counts based on viewport width:
  - `<480px`: 20 flow, 8 neural, 0 energy, pixelRatio capped at 1
  - `<768px`: 40 flow, 15 neural, 2 energy, pixelRatio capped at 1
  - `>=768px`: 150 flow, 40 neural, 5 energy, full pixelRatio

### Issue 9: visibilitychange listener
- **Before**: rAF runs continuously even when tab is hidden
- **After**: `document.addEventListener('visibilitychange', ...)` pauses/resumes rAF when tab hides/shows
- `rafId` variable tracks the animation frame ID for cancellation

### Bonus: prefers-reduced-motion
- If user has `prefers-reduced-motion: reduce`, animation is stopped entirely
- Canvas shows static gradient instead

## Files Modified

- WordPress page ID 11 `_elementor_data` meta field (via REST API)
- No local files on disk

## Verification Pattern

```python
r = requests.get('https://purebrain.ai/', headers={'Cache-Control': 'no-cache'})
checks = ['getParticleConfig', 'Float32Array', 'visibilitychange', 'prefers-reduced-motion',
          'cachedCanvasW', 'activeFlow', 'rafId']
# All should be present
missing = ['class FlowParticle', 'new FlowParticle()']
# All should be absent
```

## Key Lessons

1. **Always update `_elementor_data` meta**, not `content.raw`, for Elementor pages
2. **Encode newlines** as `\n` (two chars) when string-replacing inside Elementor JSON
3. The `rendered` content in the REST API response uses Elementor's cached output - `CF-Cache-Status: MISS` confirms whether live page is fresh
4. Clearing Elementor cache (`DELETE /wp-json/elementor/v1/cache`) is required after meta update
5. No cache plugin installed on purebrain.ai - Cloudflare is the CDN layer
