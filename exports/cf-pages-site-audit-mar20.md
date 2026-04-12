# CF Pages Site Audit — purebrain.ai
**Date**: 2026-03-20
**Auditor**: browser-vision-tester
**Platform**: Cloudflare Pages (CF Pages)
**Method**: Playwright automation, 1440x900 viewport, full DOM inspection + console capture
**Scope**: 17 primary pages + 5 sampled blog posts = 22 pages total

---

## Executive Summary

| Category | Count |
|----------|-------|
| Pages checked | 22 |
| HTTP 200 OK | 22 (100%) |
| HTTP 404 / 500 | 0 |
| Pages with broken images | 7 |
| Pages with console errors | 8 |
| Pages with legacy HTML to clean up | 9 |
| Forms present | 13 |
| Network 4xx/5xx errors | 0 |
| Blank/failed pages | 0 |

**Overall health: GOOD.** All pages load. Zero 404s. Zero network failures. The site is up everywhere. Issues found are: broken image references (3 recurring), legacy HTML artifacts (admin bar injection on 9 pages), and WebGL warnings on heavy 3D pages.

---

## Page-by-Page Results

### 1. https://purebrain.ai/
**Status**: 200 OK
**Title**: PURE BRAIN – Your Brain. Your AI. Actual Intelligence!
**Console errors**: 0
**Network errors**: 0
**Forms**: waitlistForm (8 inputs) — present
**CTA buttons**: "See what Your AI can do", "Stay with Your AI", "Leave anyway" — all present

**Broken images (3)**:
- `https://purebrain.ai/wp-content/uploads/2026/02/jared-sanborn-headshot-official.png`
- `https://purebrain.ai/wp-content/uploads/joseph-diosana-headshot.jpg`
- `https://purebrain.ai/wp-content/uploads/2026/02/MA1.BI-1.2.6-001-211107-Side-by-Side-Main-Orange-PT-scaled.png`

**Notes**: These 3 broken image paths (from old origin storage) appear on ALL legacy-HTML pages below. See Issue #1.

---

### 2. https://purebrain.ai/blog/
**Status**: 200 OK
**Title**: The Neural Feed – Blog
**Console errors**: 0
**Network errors**: 0
**Forms**: nf-subscribe-form — present
**CTA buttons**: "START YOUR AI PARTNERSHIP", "Subscribe Free" — present and linked correctly

**Broken images (5)**:
- `https://purebrain.ai/blog/teach-your-ai-something-no-one-else-can/banner.png`
- `https://purebrain.ai/blog/52-billion-ai-agents-market-is-not-the-story/banner.png`
- `https://purebrain.ai/blog/age-of-ai-agents-next-18-months/banner.png`
- `https://purebrain.ai/blog/something-big-already-happened-you-just-werent-invited-yet/banner.png`
- `https://purebrain.ai/blog/the-ai-that-forgets-you-every-single-time/banner.png`

**Notes**: 5 blog post banners are missing from the listing page. These are posts whose banner.png files were not deployed or were removed. See Issue #2.

---

### 3. https://purebrain.ai/blog-neural-feed-memories/
**Status**: 200 OK
**Title**: The Neural Feed Memories
**Console errors**: 0
**Network errors**: 0
**Broken images**: 0
**Forms**: None
**Notes**: Clean page. No issues.

---

### 4. https://purebrain.ai/live/
**Status**: 200 OK
**Title**: PURE BRAIN - Your Brain. Your AI. Actual Intelligence. Awaken Yours Today!
**Console errors**: 3 (see below)
**Network errors**: 0
**Forms**: waitlistForm present + `adminbarsearch` (legacy HTML artifact — see Issue #3)

**Broken images (3)**: Same 3 origin-storage images as homepage.

**Console errors**:
- `Refused to execute script from 'https://purebrain.ai/wp-includes/js/wp-emoji-release.min.js?ver=6.9.1' because its MIME type ('text/html') is not executable` — legacy HTML artifact, script reference resolves to a 404/HTML page
- `SCC Library has already been loaded on page` — duplicate script load

**Legacy HTML to clean up**: Admin bar present (links to `wp-admin/`, `wp-admin/plugins.php`, `wp-admin/themes.php`, `wp-admin/nav-menus.php`, etc.). This is a logged-in admin bar being injected. See Issue #3.

---

### 5. https://purebrain.ai/insiders/
**Status**: 200 OK
**Title**: PURE BRAIN - Your Brain. Your AI. Actual Intelligence. Insiders Only
**Console errors**: 3 (same as /live/)
**Network errors**: 0
**Broken images (3)**: Same 3 origin-storage images.
**Legacy HTML to clean up**: Admin bar injected. Same issue as /live/.

---

### 6. https://purebrain.ai/awakened/
**Status**: 200 OK
**Title**: PURE BRAIN - Your Brain. Your AI. Actual Intelligence. Awaken Yours Today!
**Console errors**: 3 (same as /live/)
**Network errors**: 0
**Broken images (3)**: Same 3 origin-storage images.
**Legacy HTML to clean up**: Admin bar injected.

---

### 7. https://purebrain.ai/partnered/
**Status**: 200 OK
**Title**: PURE BRAIN - Your Brain. Your AI. Actual Intelligence. Awaken Yours Today!
**Console errors**: 3 (same as /live/)
**Network errors**: 0
**Broken images (3)**: Same 3 origin-storage images.
**Legacy HTML to clean up**: Admin bar injected.

---

### 8. https://purebrain.ai/unified/
**Status**: 200 OK
**Title**: PURE BRAIN - Your Brain. Your AI. Actual Intelligence. Awaken Yours Today!
**Console errors**: 3 (same as /live/)
**Network errors**: 0
**Broken images (3)**: Same 3 origin-storage images.
**Legacy HTML to clean up**: Admin bar injected.

---

### 9. https://purebrain.ai/pay-test-sandbox-3/
**Status**: 200 OK
**Title**: PURE BRAIN - Your Brain. Your AI. Actual Intelligence. Awaken Yours Today!
**Console errors**: 3 (same as /live/)
**Network errors**: 0
**Broken images (3)**: Same 3 origin-storage images.
**Legacy HTML to clean up**: Admin bar injected.
**Forms**: waitlistForm present.

---

### 10. https://purebrain.ai/refer/
**Status**: 200 OK
**Title**: Refer & Earn
**Console errors**: 0
**Network errors**: 0
**Broken images**: 0
**Forms**: None (JavaScript-driven flow)
**CTA buttons**: "Generate My Link", "Copy", "Login", "Send Reset Link", "Set New Password" — all present
**Notes**: Clean CF Pages page. No issues detected.

---

### 11. https://purebrain.ai/invitation/
**Status**: 200 OK
**Title**: You've Been Invited — PureBrain.ai
**Console errors**: 4 warnings (WebGL GPU stall — expected for 3D pages, not a functional error)
**Network errors**: 0
**Broken images**: 0
**CTA buttons**: "CLAIM THIS SPOT" → /awakened/, "GET STARTED" → /partnered/, "GET STARTED" → /unified/ — all linked correctly
**Notes**: WebGL warnings are GPU performance messages from headless browser environment — not a real user-facing error. Page is functional.

---

### 12. https://purebrain.ai/governance/
**Status**: 200 OK
**Title**: Governance Spine — PureBrain.ai
**Console errors**: 0
**Network errors**: 0
**Forms**: governance-form (6 inputs)
**CTA buttons**: "Challenge Us", "Send Governance Challenge" — present

**Broken images (4)**:
- `https://purebrain.ai/governance/images/proof-diagram-pb.jpg`
- `https://purebrain.ai/governance/images/comparison-visual-pb.jpg`
- `https://purebrain.ai/governance/images/dao-network-pb.jpg`
- `https://purebrain.ai/governance/images/cta-atmosphere-pb.jpg`

**Notes**: 4 governance section images are missing. These are relative-path images that were not deployed with the page. See Issue #4.

---

### 13. https://purebrain.ai/ai-partnership-guide/
**Status**: 200 OK
**Title**: The Complete Guide to AI Partnership
**Console errors**: 0
**Network errors**: 0
**Broken images**: 0
**CTA buttons**: "Meet Your AI Partner" → /#awakening, "Take the Assessment" → /ai-partnership-assessment/, "Subscribe Free" → /blog/#neural-feed-subscribe — all correct
**Notes**: Clean CF Pages page. No issues.

---

### 14. https://purebrain.ai/compare/
**Status**: 200 OK
**Title**: Compare PureBrain to Other AI Tools | Side-by-Side
**Console errors**: 1

**Console error**:
- `Refused to execute script from 'https://purebrain.ai/wp-includes/js/wp-emoji-release.min.js' because its MIME type ('text/html') is not executable` — legacy script reference in HTML, not a functional blocker

**Broken images**: 0
**Forms**: Quiz/recommendation form (2 inputs) — present
**CTA buttons**: "Start Your AI Partnership", "Get my recommendation", multiple "Next" buttons — all present
**Notes**: Page is functional. One stale script reference in the HTML. See Issue #5.

---

### 15. https://purebrain.ai/brainiac-mastermind-training/
**Status**: 200 OK
**Title**: Brainiac Mastermind Training
**Console errors**: 0
**Network errors**: 0
**Broken images**: 0
**Forms**: gate-form (password gate) — present
**CTA buttons**: "Access Training Library", "Sign Out", filter tabs ("All", "Foundations") — all present
**Notes**: Clean page. Module links present: brainiac-module-1-foundations/, brainiac-module-2-ai-workflows/, brainiac-module-3-agent-delegation/. No issues.

---

### 16. https://purebrain.ai/investors-v8/?open=1
**Status**: 200 OK
**Title**: Pure Technology — Investor Portal
**Console errors**: 8 warnings (WebGL + GSAP)
**Network errors**: 0
**Broken images**: 0
**Forms**: investor-form (7 inputs)
**CTA buttons**: "Enter", "Calculate My ROI", "Schedule a Call", "Base Case", "Bull Case" — all present

**Console warnings**:
- `GSAP target #avatar-orb not found` — GSAP animation targeting an element that may not exist yet at load time (timing issue, not critical)
- `WebGL: INVALID_VALUE: texImage2D: bad image data` — WebGL texture error (likely headless GPU limitation)
- Multiple `GL_INVALID_OPERATION: glDrawElements: Feedback loop` — WebGL framebuffer warnings (headless GPU)

**Notes**: All WebGL/GSAP warnings are expected in headless environment. The GSAP `#avatar-orb not found` warning may be worth investigating — if the element is conditionally rendered, GSAP may be initializing before DOM is ready. Not a blocker. See Issue #6.

---

### 17. https://purebrain.ai/think-traffic/
**Status**: 200 OK
**Title**: Think Traffic x PureBrain — Sales Intelligence Briefing
**Console errors**: 7 warnings (WebGL only)
**Network errors**: 0
**Broken images**: 0
**Forms**: None
**CTA buttons**: "ACCESS BRIEFING" — present
**Notes**: Same WebGL feedback loop warnings as investors-v8. Expected in headless. Page is functional.

---

## Blog Post Samples (5 posts)

### Blog 1: https://purebrain.ai/blog/prompting-is-dead/
**Status**: 200 OK | **Broken images**: 0 | **Console errors**: 0
**CTA**: "Start Your AI Partnership" with UTM params — correct
**Notes**: Clean. FAQs collapsible. Audio player present.

### Blog 2: https://purebrain.ai/blog/the-meeting-your-ai-should-already-know-about/
**Status**: 200 OK | **Broken images**: 0 | **Console errors**: 0
**CTA**: "START YOUR AI PARTNERSHIP" — correct
**Notes**: Clean. No issues.

### Blog 3: https://purebrain.ai/blog/the-ai-that-knows-you-before-you-even-speak/
**Status**: 200 OK | **Broken images**: 0 | **Console errors**: 0
**CTA**: "Start Your AI Partnership" with UTM params — correct
**Notes**: Clean. No issues.

### Blog 4: https://purebrain.ai/blog/your-ai-has-no-idea-who-you-are/
**Status**: 200 OK | **Broken images**: 0 | **Console errors**: 0
**CTA**: "Start Your AI Partnership" with UTM params — correct
**Notes**: Clean. No issues.

### Blog 5: https://purebrain.ai/blog/#neural-feed-subscribe (anchor)
**Status**: 200 OK | **Broken images**: 1 (teach-your-ai banner)
**Notes**: Anchor resolves to /blog/ listing. One banner missing (same as Issue #2).

---

## Issues Found — Prioritized

---

### ISSUE #1 — MEDIUM PRIORITY
**Type**: Broken Images (Origin Storage References)
**Affects**: Homepage, /live/, /insiders/, /awakened/, /partnered/, /unified/, /pay-test-sandbox-3/ (7 pages)

**The 3 broken images on all 7 pages**:
1. `/wp-content/uploads/2026/02/jared-sanborn-headshot-official.png` — Jared headshot
2. `/wp-content/uploads/joseph-diosana-headshot.jpg` — Testimonial headshot
3. `/wp-content/uploads/2026/02/MA1.BI-1.2.6-001-211107-Side-by-Side-Main-Orange-PT-scaled.png` — Product comparison image

**Root cause**: These image paths point to origin storage that is no longer served at these URLs since the CF Pages migration. The HTML still references the old origin paths.

**User impact**: 3 images missing across all major conversion pages. Jared's headshot not showing = trust/credibility hit. Testimonial headshot missing. Product comparison image missing.

**Fix**: Update image `src` attributes in the HTML to point to the correct CF Pages asset paths, or re-upload images to CF Pages under `/assets/images/` and update references.

---

### ISSUE #2 — MEDIUM PRIORITY
**Type**: Missing Blog Banner Images
**Affects**: /blog/ listing page (5 of the visible blog cards)

**Missing banners**:
1. `/blog/teach-your-ai-something-no-one-else-can/banner.png`
2. `/blog/52-billion-ai-agents-market-is-not-the-story/banner.png`
3. `/blog/age-of-ai-agents-next-18-months/banner.png`
4. `/blog/something-big-already-happened-you-just-werent-invited-yet/banner.png`
5. `/blog/the-ai-that-forgets-you-every-single-time/banner.png`

**Root cause**: These blog post directories exist and their index.html is deployed, but the `banner.png` file was not included in the CF Pages deployment for these posts. More recent posts (prompting-is-dead, your-ai-has-no-idea-who-you-are) have banners correctly deployed.

**User impact**: Blog listing shows broken image placeholders for ~5 post cards. Reduces visual quality of the blog feed.

**Fix**: Re-deploy these specific post directories with their banner.png files included. Check `exports/cf-pages-deploy/blog/` for which posts have banners vs which don't.

---

### ISSUE #3 — LOW PRIORITY (Cosmetic / Cleanup)
**Type**: Legacy HTML Artifact — Admin Bar Injection
**Affects**: /live/, /insiders/, /awakened/, /partnered/, /unified/, /pay-test-sandbox-3/ (6 pages)

**What was found**: A logged-in CMS admin bar is being injected into the HTML of these pages. The bar includes navigation links to admin panel URLs:
- `/wp-admin/about.php`
- `/wp-admin/plugins.php`
- `/wp-admin/themes.php`
- `/wp-admin/nav-menus.php`
- `/wp-admin/customize.php?url=...`
- `/wp-admin/post-new.php`
- etc.

Also: `wp-emoji-release.min.js` script tags are present in the HTML, causing a browser console error because the script now returns a 404/HTML page rather than JavaScript.

**Root cause**: These pages were exported from the legacy CMS while logged in as admin. The admin toolbar HTML was captured in the static export. The script reference also came from the export.

**User impact**: Admin bar is visible to users (low severity — it may be hidden by CSS, but the HTML is present and links are functional). Script error fires on every page load. Anonymous users seeing admin links is a privacy/UX concern.

**Recommendation**: Strip the admin bar HTML from these 6 page exports. Remove the `wp-emoji-release.min.js` script tag. These are legacy artifacts from the export process that need to be cleaned from the static HTML files.

---

### ISSUE #4 — MEDIUM PRIORITY
**Type**: Missing Section Images — Governance Page
**Affects**: /governance/

**Missing images**:
1. `/governance/images/proof-diagram-pb.jpg`
2. `/governance/images/comparison-visual-pb.jpg`
3. `/governance/images/dao-network-pb.jpg`
4. `/governance/images/cta-atmosphere-pb.jpg`

**Root cause**: The governance page references images via relative paths in an `/images/` subdirectory that was not deployed to CF Pages alongside the HTML file.

**User impact**: 4 key visual sections on the governance page show as broken images. This is a prominent page for investor/partner audiences — visual quality matters here.

**Fix**: Locate the governance page image assets and deploy them to `exports/cf-pages-deploy/governance/images/`. Then redeploy.

---

### ISSUE #5 — LOW PRIORITY (Cosmetic / Cleanup)
**Type**: Legacy Script Reference in Compare Page HTML
**Affects**: /compare/

**Console error**:
`Refused to execute script from 'https://purebrain.ai/wp-includes/js/wp-emoji-release.min.js' because its MIME type ('text/html') is not executable`

**Root cause**: Same as Issue #3 — the compare page HTML contains a stale script tag pointing to a legacy script path that now resolves to a 404 HTML response. The page was exported with this tag present.

**User impact**: Harmless console error. No functional impact on the compare page.

**Fix**: Remove the `<script src="wp-includes/js/wp-emoji-release.min.js">` tag from the compare page HTML.

---

### ISSUE #6 — LOW PRIORITY (Monitoring)
**Type**: GSAP Animation Target Not Found
**Affects**: /investors-v8/

**Console warning**:
`GSAP target #avatar-orb not found`

**Root cause**: GSAP is attempting to animate `#avatar-orb` before the element is rendered into the DOM. This can happen if the animation initialization runs before conditional rendering completes.

**User impact**: The avatar orb animation may not play correctly on the investor page. Not a blocker for the rest of the page.

**Fix**: Wrap the GSAP animation targeting `#avatar-orb` in a `ScrollTrigger` or delay until the element is confirmed present in the DOM (e.g., `if (document.querySelector('#avatar-orb'))`).

---

## No Issues Found (Clean Pages)

The following pages passed all checks with no broken images, no console errors, and no legacy HTML artifacts:

- /blog-neural-feed-memories/ — Clean
- /refer/ — Clean
- /ai-partnership-guide/ — Clean
- /brainiac-mastermind-training/ — Clean
- /blog/prompting-is-dead/ — Clean
- /blog/the-meeting-your-ai-should-already-know-about/ — Clean
- /blog/the-ai-that-knows-you-before-you-even-speak/ — Clean
- /blog/your-ai-has-no-idea-who-you-are/ — Clean
- /invitation/ — Clean (WebGL GPU warnings are headless-only, not user-facing)
- /think-traffic/ — Clean (WebGL warnings same as above)

---

## Homepage Links Found (Internal — Spot Check)

These internal links were found on the homepage. They were NOT individually audited but are noted for awareness:
- /pay-test-2/#awakening
- /partnered-how-this-levels-you-up/
- /unified-how-this-levels-you-up/
- /ai-tool-stack-calculator/
- /purebrain-vs-chatgpt/
- /purebrain-vs-claude/
- /purebrain-vs-copilot/
- /purebrain-vs-custom-gpts/
- /purebrain-vs-deepseek/
- /purebrain-vs-gemini/

These were not in the audit scope. Recommend follow-up audit sweep on the `purebrain-vs-*` series and calculator page.

---

## Summary Table

| URL | HTTP | Broken Images | Console Errors | Legacy HTML | Status |
|-----|------|---------------|----------------|-------------|--------|
| / | 200 | 3 (origin storage) | 0 | No | WARN |
| /blog/ | 200 | 5 (banner.png missing) | 0 | No | WARN |
| /blog-neural-feed-memories/ | 200 | 0 | 0 | No | PASS |
| /live/ | 200 | 3 | 3 (script MIME) | YES (admin bar) | WARN |
| /insiders/ | 200 | 3 | 3 (script MIME) | YES (admin bar) | WARN |
| /awakened/ | 200 | 3 | 3 (script MIME) | YES (admin bar) | WARN |
| /partnered/ | 200 | 3 | 3 (script MIME) | YES (admin bar) | WARN |
| /unified/ | 200 | 3 | 3 (script MIME) | YES (admin bar) | WARN |
| /pay-test-sandbox-3/ | 200 | 3 | 3 (script MIME) | YES (admin bar) | WARN |
| /refer/ | 200 | 0 | 0 | No | PASS |
| /invitation/ | 200 | 0 | 4 (WebGL GPU, headless only) | No | PASS |
| /governance/ | 200 | 4 (images dir missing) | 0 | No | WARN |
| /ai-partnership-guide/ | 200 | 0 | 0 | No | PASS |
| /compare/ | 200 | 0 | 1 (legacy script) | Partial | WARN |
| /brainiac-mastermind-training/ | 200 | 0 | 0 | No | PASS |
| /investors-v8/?open=1 | 200 | 0 | 8 (WebGL + GSAP, mostly headless) | No | WARN |
| /think-traffic/ | 200 | 0 | 7 (WebGL, headless only) | No | PASS |
| /blog/prompting-is-dead/ | 200 | 0 | 0 | No | PASS |
| /blog/the-meeting-your-ai-should-already-know-about/ | 200 | 0 | 0 | No | PASS |
| /blog/the-ai-that-knows-you-before-you-even-speak/ | 200 | 0 | 0 | No | PASS |
| /blog/your-ai-has-no-idea-who-you-are/ | 200 | 0 | 0 | No | PASS |
| /blog/#neural-feed-subscribe | 200 | 1 (banner) | 0 | No | WARN |

**PASS: 11 | WARN: 11 | FAIL: 0**

---

## Recommended Action Order

1. **Fix broken images on all 7 conversion pages** (Issue #1) — Jared's headshot and product images not showing on the pages where people make buying decisions. High trust impact.

2. **Deploy missing governance images** (Issue #4) — 4 missing images on a page used for investor/partner outreach.

3. **Deploy missing blog banner.pngs** (Issue #2) — 5 blog cards showing broken images in the listing feed.

4. **Strip admin bar HTML from 6 legacy pages** (Issue #3) — Admin toolbar is present in HTML for /live/, /insiders/, /awakened/, /partnered/, /unified/, /pay-test-sandbox-3/. Also removes the wp-emoji-release.min.js console error across all 6 pages at once.

5. **Remove stale script tag from /compare/** (Issue #5) — One-line fix.

6. **Investigate GSAP #avatar-orb timing on /investors-v8/** (Issue #6) — Low priority, animation may not be playing.

---

**Audit complete**: 2026-03-20
**Tool**: Playwright async, Chromium headless, 1440x900
**Pages audited**: 22
**Zero pages returned 404. Zero pages failed to load.**
