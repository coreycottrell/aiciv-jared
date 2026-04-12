# CTO Memory: 4-Task Sprint Delegation — 2026-03-12

**Date**: 2026-03-12
**Type**: operational, teaching
**Topic**: Multi-task sprint — blog CTA, homepage polish, CF LB, R2 videos

## Task Breakdown

### Task 1: Blog CTA Hover (URGENT)

**Root cause of Jared's "not done" report**:
Earlier fix deployed `.pb-recap-live-cta` (Awaken button) correctly.
But TWO OTHER elements still had wrong hover behavior:
- Newsletter link: goes orange (#f1420b) on hover — should be WHITE text only
- "Start Your AI Partnership" button: inline-styled, should go blue

**Two-layer fix required**:
1. `pb-blog-styling.php` plugin — the WordPress layer (newsletter hover = orange)
2. CF Pages static HTML files — the CDN layer (24 blog posts, same orange rule)

**Key insight**: When we deploy blog changes, they exist in TWO places simultaneously:
- WordPress posts (served by WP when CF Pages is bypassed/not deployed)
- CF Pages static files (the CDN-served version via purebrain-staging project)
BOTH must be updated for the fix to be complete.

**Newsletter link CSS location in pb-blog-styling.php**:
Lines 251-268 in `/home/jared/projects/AI-CIV/aether/tools/security/pb-blog-styling/pb-blog-styling.php`

**cf-pages-deploy location**: `/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/*/index.html` (24 files)

### Task 3: Homepage Polish

**Orange flash root cause analysis**:
- v4.8.5 fix targeted `html body.home.tt-magic-cursor { background: transparent }` for video to show through
- BUT the `.theme-preloader` div itself inherits no background when body is transparent
- The Awaiken theme gives the preloader an orange/light bg from theme default CSS
- FIX: Target `.theme-preloader { background: #080a12 !important }` explicitly
- This does NOT require security plugin — use a new dedicated `pb-homepage-polish` plugin

**Footer logo issue**: Use `.footer__logo img { width: auto; height: auto; max-width: 160px; object-fit: contain }`

**Hero space issue**: Remove top padding from first Elementor section on homepage

### Task 2: CF Load Balancer

**Critical first step**: SSH to 89.167.19.20 and check what tunnel serves app.purebrain.ai.
The known tunnel is for api.purebrain.ai. app.purebrain.ai may be a different tunnel.

**If CF LB not on plan**: Use Cloudflare Worker to serve fallback HTML on 502.
Worker approach is free and achieves the same resilience goal.

### Task 4: R2 Videos

**Zoom API**: Server-to-Server OAuth needs account_id from Zoom Developer Portal.
Standard credentials: ZOOM_CLIENT_ID + ZOOM_CLIENT_SECRET in .env.

**Video pipeline is proven**: transcode.sh + upload_r2.py works. Just need the source MP4.

## Delegation Pattern Used

CTO → Pre-analyzed all 4 tasks → Wrote detailed briefs → Dispatched:
- full-stack-developer: Tasks 1 + 3 (blog CSS + homepage plugin)
- devops-engineer: Tasks 2 + 4 (CF LB + R2 video pipeline)
- qa-engineer: Post-deploy verification

## Key Principles Demonstrated

1. **Security plugin is untouchable** — created new `pb-homepage-polish` plugin instead of adding CSS to security plugin
2. **Two-layer blog deployment** — any blog CSS change must update BOTH WordPress plugin AND CF Pages HTML files
3. **CF Load Balancing fallback** — if paid LB not available, free Worker is a valid alternative
4. **Zoom API** — Server-to-Server OAuth requires account_id (not just client_id/secret)

## Files Created

- `/home/jared/projects/AI-CIV/aether/exports/departments/systems-technology/reports/2026-03-12--task1-AND-task3-full-stack-brief.md`
- `/home/jared/projects/AI-CIV/aether/exports/departments/systems-technology/reports/2026-03-12--task2-cf-load-balancer-devops-brief.md`
- `/home/jared/projects/AI-CIV/aether/exports/departments/systems-technology/reports/2026-03-12--task4-r2-videos-devops-brief.md`
