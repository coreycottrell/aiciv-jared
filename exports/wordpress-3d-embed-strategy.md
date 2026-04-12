# WordPress 3D Embed Strategy

**Day 4 Deliverable**
**Date**: 2026-02-21
**Context**: Getting the `gleb-r3f-scene` Vite/R3F project into purebrain.ai WordPress pages

---

## Decision: iframe Embed (Recommended)

After evaluating all three options, **iframe embed is the correct strategy for purebrain.ai**.

### Why Not JS Bundle?

Direct JS bundle injection (via WordPress enqueue or Elementor HTML widget) fails because:

1. **Elementor CSS conflicts**: Elementor's global `img { border-radius: 0 }` overrides, CSS resets, and z-index stacking contexts all interfere with Three.js canvas styling.
2. **React version conflicts**: Elementor-dependent plugins sometimes ship their own React builds. Two React instances on one page = white screen.
3. **CSP headers**: purebrain.ai has Cloudflare WAF + custom security plugin. Inline scripts via Elementor HTML widget can be blocked by `script-src 'self'` CSP policy.
4. **Global namespace pollution**: `window.THREE` or `window.__R3F_FIBER__` globals from the 3D scene can conflict with other plugins.
5. **JavaScript load order**: WordPress concatenates/defers scripts in ways that break R3F's initialization sequence.

### Why Not WordPress Plugin Enqueue?

Plugin-enqueued scripts solve the load order problem but still face:

1. **CSS isolation failure**: Canvas element inherits WordPress/Elementor global styles
2. **Difficult updates**: Every scene change requires a new plugin version + deployment
3. **No sandboxing**: A JS error in the 3D scene crashes the whole page

### Why iframe Works

```
┌─────────────────────────────────────────────────────┐
│  purebrain.ai WordPress page (Elementor)            │
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │  <iframe                                      │  │
│  │    src="https://3d.purebrain.ai/scene/"       │  │
│  │    width="100%" height="600px"                │  │
│  │    frameborder="0"                            │  │
│  │    allow="accelerometer; autoplay"            │  │
│  │  ></iframe>                                   │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
│  Zero CSS conflicts. Zero JS conflicts. Isolated.   │
└─────────────────────────────────────────────────────┘
```

**iframe advantages**:
- Complete DOM isolation (no CSS bleeds in or out)
- Separate JavaScript context (no plugin conflicts)
- Independent caching (Three.js cached at 3d.purebrain.ai separately)
- WebGL errors don't crash the main page
- Easy updates: deploy new scene version at subdomain, iframe picks it up instantly
- Works with Elementor HTML widget, Custom HTML Gutenberg block, or shortcode

---

## Implementation Plan

### Step 1: Deploy Scene to Subdomain

Host the Vite build at a subdomain:
```
https://3d.purebrain.ai/
```

OR use the existing WordPress uploads directory:
```
https://purebrain.ai/wp-content/3d/scene/
```

The subdomain approach is cleaner. GoDaddy supports adding subdomains for domains on the same hosting account.

**Build the scene**:
```bash
cd /home/jared/projects/AI-CIV/aether/exports/gleb-r3f-scene
npm run build
# Output: dist/
# Upload dist/ to 3d.purebrain.ai via FTP or SSH
```

### Step 2: WordPress iframe Embed

**Option A: Elementor HTML Widget** (easiest, no code needed)

```html
<iframe
  src="https://3d.purebrain.ai/"
  width="100%"
  height="600"
  frameborder="0"
  style="border: none; background: #060606; display: block;"
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
  loading="lazy"
></iframe>
```

Place this in an Elementor HTML widget anywhere on the page.

**Option B: WordPress Shortcode** (for reuse across multiple pages)

Add to `purebrain-security-plugin.php` (Jared's custom plugin):

```php
// Register 3D scene shortcode
add_shortcode('purebrain_3d', function($atts) {
    $a = shortcode_atts([
        'src'    => 'https://3d.purebrain.ai/',
        'height' => '600',
        'mode'   => 'idle',
    ], $atts);

    $src = esc_url($a['src']);
    $height = intval($a['height']);
    $mode = esc_attr($a['mode']);

    // Pass mode via URL parameter (read by App.jsx on load)
    if ($mode !== 'idle') {
        $src = add_query_arg('mode', $mode, $src);
    }

    return sprintf(
        '<div class="purebrain-3d-wrapper" style="width:100%%;height:%dpx;background:#060606;">
            <iframe
                src="%s"
                width="100%%"
                height="100%%"
                frameborder="0"
                style="border:none;display:block;"
                allow="accelerometer; autoplay"
                loading="lazy"
            ></iframe>
        </div>',
        $height,
        $src
    );
});
```

Usage in any WordPress page or post:
```
[purebrain_3d height="500" mode="blue"]
[purebrain_3d height="700" mode="orange"]
```

### Step 3: CSS Variable Injection for Theming

To pass PureBrain brand colors from WordPress into the iframe WITHOUT breaking isolation:

**Method: URL parameters**

The iframe src can include query params that App.jsx reads on load:
```
https://3d.purebrain.ai/?mode=orange&theme=dark
```

App.jsx reads these on startup:
```javascript
// In App.jsx
const params = new URLSearchParams(window.location.search)
const initialMode = params.get('mode') || 'idle'
const [mode, setMode] = useState(initialMode)
```

**Method: PostMessage API** (for real-time communication)

The parent page can send messages to the iframe to change modes dynamically:

```javascript
// On parent WordPress page (e.g., when user scrolls to hero section)
const iframe = document.querySelector('iframe[src*="3d.purebrain.ai"]')

// Trigger orange mode when user reaches a certain section
iframe.contentWindow.postMessage({ type: 'SET_MODE', mode: 'orange' }, 'https://3d.purebrain.ai')

// Trigger speaking mode when chatbot is active
iframe.contentWindow.postMessage({ type: 'SET_MODE', mode: 'speaking' }, 'https://3d.purebrain.ai')
```

In the 3D scene (App.jsx):
```javascript
// Listen for messages from parent
useEffect(() => {
    const handler = (event) => {
        if (event.origin !== 'https://purebrain.ai') return  // security check
        if (event.data?.type === 'SET_MODE') {
            setMode(event.data.mode)
        }
    }
    window.addEventListener('message', handler)
    return () => window.removeEventListener('message', handler)
}, [])
```

This is how the Aether chatbot can control the 3D sphere mode: speaking when Aether is talking, thinking when processing, idle when waiting.

---

## Performance Considerations

### Lazy Loading

The `loading="lazy"` attribute on the iframe means the browser will only load the 3D scene when the user scrolls near it. This is critical for page load time.

```html
<iframe src="..." loading="lazy"></iframe>
```

Without `loading="lazy"`: Three.js loads at page start (adds ~400ms to First Contentful Paint).
With `loading="lazy"`: Three.js loads only when user approaches the 3D section.

### Intersection Observer (Advanced)

For more control, use Intersection Observer to load the scene only when it enters the viewport:

```html
<div id="3d-placeholder" style="width:100%;height:600px;background:#060606;">
    <!-- Placeholder shows dark background while loading -->
</div>

<script>
const placeholder = document.getElementById('3d-placeholder')
const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
        // Replace placeholder with iframe only when visible
        const iframe = document.createElement('iframe')
        iframe.src = 'https://3d.purebrain.ai/'
        iframe.width = '100%'
        iframe.height = '600'
        iframe.frameBorder = '0'
        iframe.style.cssText = 'border:none;display:block;'
        placeholder.replaceWith(iframe)
        observer.disconnect()
    }
}, { threshold: 0.1 })  // load when 10% visible
observer.observe(placeholder)
</script>
```

### Mobile Fallback

Detect WebGL support and show a fallback image on unsupported devices:

```html
<div id="3d-container">
    <noscript>
        <img src="https://purebrain.ai/wp-content/uploads/3d-fallback.jpg"
             alt="PureBrain 3D Sphere"
             style="width:100%;height:auto;" />
    </noscript>
</div>

<script>
const canvas = document.createElement('canvas')
const supportsWebGL = !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))

const container = document.getElementById('3d-container')
if (supportsWebGL) {
    container.innerHTML = '<iframe src="https://3d.purebrain.ai/" ...></iframe>'
} else {
    container.innerHTML = '<img src="fallback.jpg" style="width:100%" />'
}
</script>
```

---

## Cloudflare / CSP Considerations

### X-Frame-Options

For the subdomain `3d.purebrain.ai` to be embeddable in `purebrain.ai`, the iframe host must allow it:

```
# Cloudflare / server headers for 3d.purebrain.ai
X-Frame-Options: SAMEORIGIN
# OR more specific:
Content-Security-Policy: frame-ancestors https://purebrain.ai https://www.purebrain.ai
```

If using WordPress uploads directory instead of a subdomain, this is automatically allowed (same origin).

### Current PureBrain Security Plugin

The existing security plugin (v2.8+) sets CSP headers. Before deploying the iframe, verify the current CSP `frame-ancestors` directive allows the 3D subdomain.

```bash
# Check current CSP headers on purebrain.ai
curl -sI https://purebrain.ai | grep -i "content-security-policy"
```

---

## Recommended Deployment Sequence

1. **Build scene**: `npm run build` in `exports/gleb-r3f-scene/`
2. **Upload `dist/` to WordPress**: `/wp-content/3d/scene/` directory via FTP
   - OR create a subdomain `3d.purebrain.ai` and upload there
3. **Verify direct access**: Open `https://purebrain.ai/wp-content/3d/scene/` in browser
   - Should show the 3D scene running
4. **Add Elementor HTML widget**: Paste the iframe code in the desired section
5. **Test mobile**: Verify on phone (WebGL works on iOS/Android modern browsers)
6. **Add PostMessage listener**: If chatbot-to-3D integration is desired

---

## File Size Reference

After Day 4 code splitting:
```
dist/assets/three-DrdX3_7U.js     187.65 kB gzip  (cached aggressively)
dist/assets/r3f-GDf76nXz.js       155.67 kB gzip  (cached aggressively)
dist/assets/pp-D4hu7zPD.js         20.89 kB gzip  (postprocessing)
dist/assets/motion-BheSypY2.js     11.57 kB gzip  (framer-motion)
dist/assets/index-CKE59NLu.js       3.96 kB gzip  (app code)
dist/assets/index-DM7G8zms.css      1.48 kB gzip  (styles)
```

Total: ~382 kB gzip on first load.
Subsequent loads: ~3.96 kB (only app code changes; Three.js served from cache).

Comparison to CDN-delivered Three.js (no code splitting): 345 kB gzip in one chunk.
Code splitting: 382 kB total but parallel loading + better caching = faster perceived load.

---

## Summary Table

| Option | Isolation | Elementor Compatible | Update Speed | Chatbot Integration |
|--------|-----------|---------------------|-------------|---------------------|
| **iframe (recommended)** | Full | Yes | Instant (re-deploy scene) | PostMessage API |
| JS bundle via enqueue | None | Risky | Plugin update needed | Direct JS |
| Elementor HTML widget | Partial | Yes but conflicts | Plugin update needed | Direct JS |

**Use iframe for production. Use Elementor HTML widget for rapid prototyping/testing.**
