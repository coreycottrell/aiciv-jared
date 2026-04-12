# Memory: Blog Link Hover v3.9.2 Verification & Status

**Date**: 2026-02-22
**Type**: teaching
**Topic**: v392 CSS verification — all fixes already deployed, Cloudflare cache issue for 2 JDS posts

---

## Final Status (Post-v392 Deployment)

### PureBrain.ai (9 posts)
ALL 9 posts: v392 deployed, `.post-content` selector present, CTA has white text, no proper names.
Live page delivery: CONFIRMED for all 9.

### JDS (10 posts)
ALL 10 posts in DB: v392 deployed, selectors correct, no proper names.
Live delivery: 8/10 confirmed. 2 posts (1045, 998) serving from Cloudflare cache (31-day max-age).
CF-Cache-Status: HIT for those 2. DB is correct.

**Resolution for cached pages**: Jared must purge Cloudflare cache (Dashboard → Caching → Purge Everything)
or wait for natural expiry.

---

## Theme Content Class Discovery

| Site | Content Wrapper Class |
|------|-----------------------|
| purebrain.ai (Astra/Elementor) | `.post-content` |
| jareddsanborn.com (Divi) | `.entry-content` |

**v392 targets BOTH**: `.post-content`, `.entry-content`, AND `.elementor-widget-theme-post-content`

---

## CSS Specificity Rule: CSS !important beats inline style without !important

Post 1060 (JDS) has old-style CTA: `style="color: #f1420b;"` (no !important).
The v392 CSS rule `body.single-post a[href*="awakening"] { color: #ffffff !important; }` WINS
because CSS `!important` overrides non-`!important` inline styles.

---

## Transparency Section Status

No proper names (Gleb Kuznetsov, 3D Design Specialist) in:
- Post content (all 19 posts)
- Transparency section rendered HTML (confirmed live)
- Transparency config: `config/transparency-week-2026-02-17-v2.json` (clean)

The transparency-data endpoint (`POST /purebrain/v1/transparency-data`) was used to update
the option. The v2 config file has no proper names.

---

## Audit Tool Pattern (WORKING)

To audit posts for CSS deployment status:
```python
# Use RENDERED content (not raw - raw is often empty for older posts)
post = requests.get(f'{base}/posts/{id}', auth=auth).json()
rendered = post['content'].get('rendered', '')  # Always use rendered
# NOT: post['content'].get('raw', '')  # Often empty on JDS
```

---

## Files Involved

- Posts updated: all 9 PB + all 10 JDS
- Style block ID: `pb-link-hover-v392`
- Previous style block ID removed: `pb-link-hover-v391`
- Plugin file: `tools/security/purebrain-security/purebrain-security-plugin.php`
