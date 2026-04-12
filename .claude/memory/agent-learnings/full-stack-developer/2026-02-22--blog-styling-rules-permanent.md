# Memory: Permanent Blog Styling Rules — 2026-02-22

**Date**: 2026-02-22
**Type**: teaching
**Topic**: Permanent blog styling rules established + deployment patterns for GoDaddy sites

---

## Permanent Rules (Established 2026-02-22)

### Rule 1: NO Proper Names in Blog Content

**Rule**: NO proper names (personal, corporate, product) in ANY blog content or transparency sections. EVER.

**Enforcement points**:
- Transparency section summary text
- Transparency section "Biggest Win" field
- Transparency work breakdown table rows
- Blog post body content
- FAQ sections

**Violations fixed**:
- "Gleb Kuznetsov-level glass aesthetics" → "studio-quality glass aesthetics"
- "7-day Gleb Kuznetsov mastery sprint" → "7-day 3D mastery sprint"

**How to update transparency data**:
```bash
python3 tools/update_transparency_data.py --file config/transparency-week-YYYY-MM-DD.json
```

### Rule 2: CTA Button Styling

**Default**: Orange (#f1420b) background, WHITE (#ffffff) text
**Hover**: Blue (#2a93c1) background, WHITE (#ffffff) text

**Implementation**:
1. Inline style on the `<a>` tag: `color: #ffffff !important`
2. Plugin CSS backup: `body.single-post .blog-cta-block a[href*="awakening"] { color: #ffffff !important }`
3. Template: `.claude/skills/wordpress-publishing/blog-footer-template.html`

**Selectors that target the CTA button**:
- `body.single-post .blog-cta-block p a[href*="awakening"]`
- `.blog-cta-block a[href*="awakening"]`

### Rule 3: Tag Pill Styling

**Default**: Blue (#2a93c1) background, WHITE (#ffffff) text, border-radius: 20px (pill shape)
**Hover**: Orange (#f1420b) background, WHITE (#ffffff) text

**Implementation**: CSS deployed via plugin AND as inline `<style>` block in each post content.

**CSS selectors**:
```css
body.single-post .post-tags .tag-links a[rel="tag"] { background: #2a93c1; color: #fff; border-radius: 20px; }
body.single-post .post-tags .tag-links a[rel="tag"]:hover { background: #f1420b; color: #fff; }
```

**Post content CSS block ID**: `pb-tag-pills-v390` (injected at top of each post content)

### Rule 4: Subscribe Forms Must Connect to Brevo List 3

**Requirement**: ALL subscribe/neural-feed forms must connect to Brevo List 3 (The Neural Feed).

**Implementation**:
- Plugin endpoint: `POST /wp-json/purebrain/v1/subscribe` (v3.5.0+)
- Endpoint adds email to Brevo List 3 via server-side API call
- BREVO_API_KEY must be defined in wp-config.php

**Verification**: Look for `pb-security/v1/subscribe` or `purebrain/v1/subscribe` in page source.

---

## Deployment Patterns Learned

### Transparency Data Update (WORKS via REST API)
```bash
python3 tools/update_transparency_data.py --file config/transparency-week-YYYY-MM-DD.json
```
- Uses application password (Basic Auth)
- Updates `purebrain_transparency_data` wp_option on both sites
- Data update is immediate in DB; CDN cache may delay visible update

### Plugin File Deployment (BLOCKED by GoDaddy when rate-limited)

GoDaddy blocks automated logins after multiple attempts (429 Too Many Requests).
The block shows a reCAPTCHA page that cannot be solved programmatically.

**When rate limited (shows "Please verify you are human" reCAPTCHA)**:
- Wait 30-60+ minutes for IP-based rate limit to reset
- Try Playwright deployment via `python3 tools/security/deploy_plugin_v390.py`

**Alternative when plugin deployment is blocked**:
- Inject CSS as `<style>` block directly in each post's content via REST API
- Use app password (Basic Auth) to PATCH posts: `POST /wp-json/wp/v2/posts/{id}`
- This works even when form login is blocked
- Tag: `<style id="pb-tag-pills-v390">` for identification/removal later

### JDS Form Login (REQUIRES actual admin password, NOT app password)
- App password `u3GO 3dvG rUqG...` = ONLY for REST API (Basic Auth)
- Form login (wp-login.php) requires the account's actual admin password
- JDS admin password changed since v3.6.0 - need Jared to provide current password
- Without form login password: use REST API CSS injection approach

### CDN Cache Behavior
- Cloudflare caches page HTML for 31 days (`cache-control: max-age=2678400`)
- Transparency data updates go to DB immediately but page HTML stays cached
- To see updates: user must hard-refresh (Cmd+Shift+R) or use incognito
- Elementor cache cleared via: `DELETE /wp-json/elementor/v1/cache` (HTTP 200 on PB, 404 on JDS)
- Cloudflare purge: only via Cloudflare dashboard (no API key stored in .env)

---

## Current Plugin Versions (as of 2026-02-22)

| Site | Plugin Version | Tag Pills | Transparency | Lead Capture |
|------|---------------|-----------|--------------|--------------|
| purebrain.ai | 3.7.0 | via post CSS | YES | YES |
| jareddsanborn.com | 3.6.0 | via post CSS | YES | YES |

**Target version**: 3.9.0 (has tag pills + CTA CSS natively in plugin)
**Deploy blocker**: GoDaddy IP rate limiting + JDS admin password unknown

---

## Files Modified (2026-02-22)

1. `config/transparency-week-2026-02-17-v2.json` — Updated transparency data (Gleb removed)
2. All 9 PB blog posts — CSS block prepended to content
3. All 10 JDS blog posts — CSS block prepended to content

## Blog Footer Template

Location: `.claude/skills/wordpress-publishing/blog-footer-template.html`

The template already has correct CTA button styling:
- `color: #ffffff !important` on the awakening link
- Orange background gradient
- Blue hover via plugin CSS
