# Blog Subscribe Links: Inline Style Override Fix

**Date**: 2026-02-21
**Agent**: full-stack-developer
**Type**: technique + gotcha
**Topic**: Inline `!important` in post content overrides plugin CSS hover rules

---

## The Problem

Blog post content had subscribe links with hardcoded `style="color: #2a93c1 !important; text-decoration: underline;"` inline attributes. Even though the plugin CSS had:

```css
.blog-cta-block p a[href*="subscribe"]:hover { color: #ffffff !important; }
```

The **inline `!important` beats a stylesheet `!important`** - inline always wins the specificity war. So hover color stayed blue (#2a93c1) instead of turning white.

## The Two-Part Fix

### Part 1: Runtime JS in plugin (v2.8.0)
Added a `wp_footer` hook (priority 20, `is_single()` only) that strips the `style` attribute from subscribe links at page load:

```javascript
function stripNewsletterInlineStyles() {
    var ctaBlock = document.querySelector('.blog-cta-block');
    if (!ctaBlock) return;
    var newsletterLinks = ctaBlock.querySelectorAll(
        'a[href*="subscribe"], a[href*="newsletter"], a[href*="neural-feed"]'
    );
    newsletterLinks.forEach(function(link) {
        link.removeAttribute('style');
    });
}
```

### Part 2: REST API content cleaning
Used `requests` + WP REST API to strip `style=` from the stored post content (all 7 posts). This means even without JS, the content is clean. Pattern used:

```python
INLINE_STYLE_PATTERN = re.compile(
    r'(<a\s[^>]*href="[^"]*(?:subscribe|newsletter|neural-feed)[^"]*"[^>]*?)\s+style="[^"]*"([^>]*>)',
    re.IGNORECASE | re.DOTALL,
)
content = INLINE_STYLE_PATTERN.sub(r'\1\2', content)
```

## Post 565 Href Bug

Post 565 (`the-difference-between-using-ai-and-having-an-ai-partner`) had a wrong subscribe href:
- **Wrong**: `https://purebrain.ai/blog/?utm_source=blog&...` (missing anchor)
- **Correct**: `https://purebrain.ai/blog/#neural-feed-subscribe?utm_source=blog&...`

Simple `str.replace()` fixed it via REST API PUT.

## WP REST API Notes

- `context=edit` is required to get `content.raw` (instead of rendered HTML)
- Use `requests.auth.HTTPBasicAuth(user, app_password)` - no spaces needed in app password
- Update posts via `POST /wp-json/wp/v2/posts/{id}` with JSON body (no X-HTTP-Method-Override needed)
- Always GET fresh content, modify only the target, PUT back - never reconstruct from scratch

## Plugin Deploy Pattern

Plugin version bumped to 2.8.0. Deploy script: `tools/security/deploy_plugin_v280.py`.
Pattern same as `deploy_plugin_v260.py` - CodeMirror setValue, then submit button click, then cache flush.

## Files

- Plugin: `/home/jared/projects/AI-CIV/aether/tools/security/purebrain-security-plugin.php` (v2.8.0)
- Content fix script: `/home/jared/projects/AI-CIV/aether/tools/fix_blog_subscribe_links.py`
- Deploy script: `/home/jared/projects/AI-CIV/aether/tools/security/deploy_plugin_v280.py`

## Verification Commands

```bash
python3 -c "
import urllib.request
url = 'https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/'
req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache'})
html = urllib.request.urlopen(req).read().decode()
print('strip JS:', 'purebrain-strip-newsletter-inline-styles' in html)
print('no inline style:', 'color: #2a93c1 !important' not in html)
"
```
