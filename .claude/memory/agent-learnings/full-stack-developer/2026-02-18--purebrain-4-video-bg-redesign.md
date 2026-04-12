# PureBrain 4.0 Landing Page Video Background Implementation

**Date**: 2026-02-18
**Type**: operational + teaching
**Agent**: full-stack-developer

## Task
Redesign PureBrain 4.0 landing page (page ID 383) to match homepage visual quality with video background.

## Key Discovery: Elementor HTML Widget vs WordPress Post Content

**Critical pattern**: When a page uses Elementor HTML widget, content is stored in TWO places:
1. **WordPress post content** (`content.raw` in REST API) - rendered fallback
2. **Elementor data** (`_elementor_data` in post meta) - what Elementor actually renders

You MUST update `_elementor_data` meta to change what Elementor shows. Updating just the post content does nothing visually.

### Access Pattern
```python
# Get Elementor data
r = requests.get(
    'https://purebrain.ai/wp-json/wp/v2/pages/383?context=edit',
    auth=auth
)
data = r.json()
elementor_data_str = data['meta']['_elementor_data']
elementor_data = json.loads(elementor_data_str)

# Navigate to HTML widget
widget = elementor_data[0]['elements'][0]  # structure depends on page
widget['settings']['html'] = new_html_content

# Update via REST API
requests.put(
    'https://purebrain.ai/wp-json/wp/v2/pages/383',
    auth=auth,
    json={'meta': {'_elementor_data': json.dumps(elementor_data)}}
)
```

## Cache Architecture at purebrain.ai

**Three-layer cache stack**:
1. WordPress object cache (cleared by updating pages)
2. GoDaddy/WPaaS platform cache
3. Cloudflare CDN (most persistent)

**Cache clearing**:
- `GET /wp-json/wpaas/v1/flush-cache/status` - check status (accessible)
- `POST /wp-json/wpaas/v1/flush-cache` - requires admin role (403 for Aether user)
- Cloudflare CDN eventually self-clears on MISS (query string `?v=timestamp` forces MISS)

**Practical workaround**: 
- Fetch with `?v={timestamp}` to force Cloudflare MISS
- After a few MISS fetches, canonical URL starts serving fresh

## Video Background Implementation Pattern

For a page-contained video background (doesn't use Elementor's built-in video bg):

```css
.pb4-video-bg {
    position: fixed;    /* Fixed covers entire viewport */
    inset: 0;
    z-index: -2;        /* Behind everything */
    overflow: hidden;
}

.pb4-video-bg__video {
    position: absolute;
    top: 50%; left: 50%;
    min-width: 100%; min-height: 100%;
    transform: translate(-50%, -50%);
    object-fit: cover;
    opacity: 0.65;      /* Lower = more legible text over it */
}

.pb4-video-bg__overlay {
    position: absolute;
    inset: 0;
    background: rgba(5, 5, 18, 0.55);  /* Dark tint for readability */
}
```

**Content sections must be semi-transparent** to show video through:
```css
.section { background: rgba(10, 10, 26, 0.75) !important; }
```

## Cloudflare Page Rules Context

The site has `max-age=2678400` (31 days!) on pages. Don't rely on CDN cache auto-expiring.

## Video Sources Used
- Background: `https://res.cloudinary.com/dq06qxzhz/video/upload/v1769961538/PureResearch.ai_1_nzlral.mp4`
- Demo modal: `https://res.cloudinary.com/dq06qxzhz/video/upload/v1770156001/Pure_Brain_Demo_Video_nyjoon.mp4`

## File Modified
- WordPress page ID 383 (`_elementor_data` meta)
- No file system changes needed
