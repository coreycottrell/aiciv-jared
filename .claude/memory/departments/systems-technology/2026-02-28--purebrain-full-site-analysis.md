# Memory: PureBrain.ai Full Site Analysis — Feb 28 2026
**Date**: 2026-02-28
**Type**: synthesis + operational
**Topic**: Full website analysis — ST# overnight task (updated from Feb 27)

---

## Key Findings (Delta from Feb 27)

### NEW CRITICAL: Post 1084 Missing Meta Description
- Published today: /ai-doesnt-make-your-team-smarter-it-makes-the-gap-bigger/
- Has OG image, Article schema, H1, H2x7 — but no _yoast_wpseo_metadesc
- Suggested: "AI doesn't raise the floor — it raises the ceiling. Learn why implementing AI without a strategy widens the competence gap across your team, and what the top 10% do differently."
- Also: Post 950 still missing (unchanged from yesterday)

### NEW HIGH: /video-test/ and /training/ Are Indexed
- Both appear in page-sitemap.xml with index: follow
- /training/ has a password gate — should be noindex regardless
- /video-test/ is a staging/test page — definitely noindex
- Fix: Set Yoast noindex on both pages (IDs 1118 and 1115)

### UNCHANGED CRITICAL: Security Plugin Still Inactive
- PureBrain Security v4.7.2.1 = INACTIVE (day 2 unfixed)
- User enumeration now confirmed: /wp-json/wp/v2/users returns 3 users unauthenticated
  - 835655pwpadmin (admin username exposed)
  - Jared Sanborn
  - Aether (AI)
- xmlrpc.php returns 403 (good — blocked by Cloudflare or server config)
- wp-login.php returns 200 (accessible — needs WAF rule)

### UNCHANGED CRITICAL: Wrong Background Video
- Still: PureResearch.ai-1.mp4
- Location: <source> tag on WP page ID 11 (_elementor_data)

## Performance Status (Feb 28)
- All pages under 0.32s full download when cached (excellent)
- Homepage: 446KB (large but cached well)
- All comparison pages: 200 OK with good TTFB
- Newest blog post: 135KB (well-optimized)

## Chatbox Funnel Reality Check
- 745 total events in logs, 367 unique sessions
- BUT: 548 events from 127.0.0.x (local/internal test traffic)
- Real external traffic: ~90 sessions (3 external IP prefixes)
- Email capture in chat content: 231 sessions have email in messages (63% of all sessions)
- 13 unique email addresses — mostly internal test accounts

## Site Architecture (Current)
- 14 blog posts (all published, all in sitemap, good meta desc on 12 of 14)
- 51 WP pages (34 in sitemap, ~17 noindex/test)
- 8 plugins: 7 active, 1 inactive (PureBrain Security)
- Duplicate schema on homepage (Yoast + Elementor conflict)
- No security headers in HTTP response headers

## Report Location
/home/jared/projects/AI-CIV/aether/exports/overnight-reports/purebrain-site-analysis.md
~380 lines, ~14KB

## API Patterns Confirmed
- WP REST API with `curl -u "Aether:FlFr2VOtlHiHaJWjzW96OHUJ"` works for all authenticated endpoints
- Independent Analytics plugin has no REST API endpoint (returns 404 on all routes)
- Yoast head_json field in posts/pages returns full SEO data including schema, og tags, robots
- Check `yoast_head_json.robots.index` for indexability status per page/post

## Quick Fix Commands
```bash
WP_USER="Aether"
WP_PASS="FlFr2VOtlHiHaJWjzW96OHUJ"

# Fix post 1084 meta description
curl -s -u "$WP_USER:$WP_PASS" -X POST \
  "https://purebrain.ai/wp-json/wp/v2/posts/1084" \
  -H "Content-Type: application/json" \
  -d '{"meta":{"_yoast_wpseo_metadesc":"AI does not raise the floor — it raises the ceiling. Learn why implementing AI without a strategy widens the competence gap across your team, and what the top 10% do differently."}}'

# Fix post 950 meta description
curl -s -u "$WP_USER:$WP_PASS" -X POST \
  "https://purebrain.ai/wp-json/wp/v2/posts/950" \
  -H "Content-Type: application/json" \
  -d '{"meta":{"_yoast_wpseo_metadesc":"Most AI forgets everything the moment a conversation ends. PureBrain does not. Here is why persistent AI memory is the feature that changes how you work forever."}}'

# Noindex video-test (ID 1118) — requires Yoast meta update via plugin or admin
# Noindex training (ID 1115) — same
```
