# PureBrain.ai: WordPress to Vercel Migration Plan

**Prepared by**: Aether | **Date**: March 7, 2026
**Status**: PROPOSAL (no action until Jared approves)

---

## Why We're Doing This

WordPress + GoDaddy + Elementor is a triple friction layer that costs us time every single day:

| Problem | Impact | Frequency |
|---------|--------|-----------|
| GoDaddy WAF blocks plugin uploads (error 1010) | Can't deploy fixes via REST API | Every deployment |
| GoDaddy CAPTCHA blocks admin actions | Can't update security plugin | Ongoing since Feb |
| Elementor `_elementor_data` corruption | Full page wipeout from one bad JSON edit | 3 times so far |
| `is_front_page()` returning false | Video/JS features silently fail | Discovered today |
| 23 active plugins for CSS/JS fixes | Any plugin change can cascade-break others | Weekly |
| Elementor cache stale after updates | Changes don't appear until manual cache clear | Every update |
| No SSH access on GoDaddy | Can't directly edit files, debug, or deploy | Permanent |
| No staging environment | Every change is live immediately | Permanent |

**The pattern**: 10 steps forward, 7 steps back. Every day.

**On Vercel**: Edit a file. Push. Live in 8 seconds. Broke something? `git revert`. Done in 10 seconds.

---

## What We're Moving

### Full Site Inventory

**82 published pages** (categorized by priority):

#### Tier 1 — Core Revenue Pages (migrate first)
| Page | ID | What It Does |
|------|----|-------------|
| Homepage | 11 | Hero, video background, living-background animation, demo player, pricing tiers, chatbox CTA |
| Pay-test-2 | 689 | Full onboarding chatbox + PayPal payment flow (PRODUCTION) |
| Pay-test-sandbox-3 | 1232 | Same as pay-test-2 (staging/testing) |
| Blog listing | 319 | Blog grid with category filtering |
| 22 blog posts | various | Self-contained HTML articles |
| Pricing/Compare hub | 752 | Central comparison page |

#### Tier 2 — Marketing & Conversion Pages
| Page | ID | What It Does |
|------|----|-------------|
| 8 comparison pages | 753-760, 1044, 1190, 1256-1258 | PureBrain vs ChatGPT/Claude/Copilot/etc. |
| AI Tool Stack Calculator | 777 | Interactive calculator tool |
| Why PureBrain | 794 | Value proposition page |
| Invitation | 987 | 3D neural network + invite form |
| Mission/Vision/Values | 929 | Company page |
| Refer & Earn | 1298 | Referral program page |
| Training | 1251 | Content-gated training portal |
| Cost Comparison | 970 | Pricing comparison tool |

#### Tier 3 — Sales & Client Pages
| Page | ID | What It Does |
|------|----|-------------|
| Graham Martin minisites | 1150-1156 | 5 client-specific pages |
| Investor Intelligence | 1205 | Investor-facing page |
| Hunden Partners pages | 1206, 1294, 1329, 1394 | Client proposals/blueprints |
| Sales Playbook | 1278 | Internal sales tool |
| Portfolio | 1006 | Case studies |
| Developers | 1324 | Developer-facing page |
| Various client pages | 1196, 1200, 1225, 1231, etc. | Client-specific landing pages |

#### Tier 4 — Utility Pages
| Page | ID | What It Does |
|------|----|-------------|
| Privacy Policy | 3 | Legal |
| Terms of Service | 541 | Legal |
| Thank You | 309 | Post-form confirmation |
| About Aether | 731 | AI identity page |
| Various test/backup pages | 95, 174, 338, 383, 439, 468, 688, 1128 | Can be archived or removed |

### Blog Posts (22 published)
All self-contained HTML with `<article class="pb-blog-post">` wrapper. Each has:
- Featured image (banner)
- Category assignment
- Yoast SEO metadata (title, description, OG image)
- FAQ sections (some posts)

### Media Files (~86 files)
- Blog banners/featured images
- PT logo variants
- Background video (brain GIF/MP4)
- OG images
- Orb/avatar images

### Integrations to Preserve
| Integration | How It Works Now | How It Works on Vercel |
|------------|-----------------|----------------------|
| **Brevo (email)** | Sendinblue WP plugin + API calls | Direct API calls from frontend/serverless. Zero change on Brevo side. |
| **PayPal** | JS SDK loaded in chatbox pages | Same JS SDK, same code. No change. |
| **Google Tag Manager** | WP plugin injects `<script>` | Same `<script>` tag in layout. No change. |
| **Google Analytics** | Via GTM | No change. |
| **Yoast SEO** | WP plugin generates meta tags | Meta tags in page `<head>` directly. Same data. |
| **Referral system** | Custom WP plugin (PHP) | Vercel serverless function (JS/Python). Same logic. |
| **Portal (portal.purebrain.ai)** | Separate server, not on WordPress | Zero change. Already independent. |
| **Cloudflare tunnel** | Routes subdomains to services | DNS change only. Tunnels stay. |
| **IndexNow** | WP plugin pings search engines | Simple API call on deploy. |

### Active Plugins — What Happens to Each

| Plugin | Verdict | Reason |
|--------|---------|--------|
| purebrain-security-plugin | **DISSOLVE** | Security headers go in Vercel config (`vercel.json`). CSP, HSTS, etc. = 10 lines of config. |
| purebrain-referral-system | **REBUILD** as serverless function | Same logic, proper API. ~200 lines of code. |
| purebrain-blog-styles | **DISSOLVE** | CSS goes directly in blog template. |
| pb-blog-styling | **DISSOLVE** | Same — CSS in templates. |
| pb-button-styling | **DISSOLVE** | CSS in components. |
| pb-awaken-cta | **DISSOLVE** | HTML/CSS in page component. |
| pb-blog-faq | **DISSOLVE** | FAQ component in blog template. |
| pb-breadcrumb-fix | **DISSOLVE** | Breadcrumbs in layout component. |
| pb-cache-control | **DISSOLVE** | Vercel handles caching natively. |
| pb-calculator-cta | **DISSOLVE** | HTML in page. |
| pb-content-gate | **REBUILD** as middleware | Simple auth check. 20 lines. |
| pb-footer-branding | **DISSOLVE** | Footer is a shared component. |
| pb-lead-capture | **DISSOLVE** | Brevo API call from form. |
| pb-page-metadata | **DISSOLVE** | Meta tags in page `<head>`. |
| pb-social-sharing | **DISSOLVE** | Share buttons in blog template. |
| pb-video-modal | **DISSOLVE** | JS in page. |
| pb-301-redirects | **DISSOLVE** | `vercel.json` redirects config. |
| elementor | **GONE** | We write HTML directly. |
| akismet | **GONE** | No WordPress = no comment spam. |
| mailin/sendinblue | **DISSOLVE** | Direct Brevo API. |
| wordpress-seo | **DISSOLVE** | Meta tags in templates. Auto-sitemap via build. |
| wp-file-manager | **GONE** | We have git. |
| google-tag-manager | **DISSOLVE** | Script tag in layout. |

**23 plugins become 0 plugins.** Referral + content gate become 2 tiny serverless functions.

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Framework** | Astro | Outputs pure static HTML. Zero JS shipped by default. Fastest possible page loads. Supports React/Vue components when needed. |
| **Hosting** | Vercel | Free tier handles our traffic. Instant deploys. Preview URLs for every branch. Edge CDN worldwide. |
| **Media/Assets** | Cloudflare R2 or Vercel Blob | Same URLs, fast CDN delivery. Cheap storage. |
| **Serverless Functions** | Vercel Functions | For referral system, content gate, form handlers. Python or Node.js. |
| **Blog** | Astro Content Collections | Markdown files with frontmatter. Auto-generates listing, categories, RSS. |
| **Styling** | Tailwind CSS (or plain CSS) | Whatever is fastest. The existing pages already have inline CSS that works. |
| **Version Control** | GitHub | Every change tracked. Instant rollback. Branch previews. |
| **DNS** | Cloudflare (keep existing) | Just change the A/CNAME record to point to Vercel. |
| **SSL** | Vercel (automatic) | Free, auto-renewing. Zero config. |
| **Forms** | Direct Brevo API calls | No middleware needed. |

---

## The Plan — 4 Phases

### Phase 1: Foundation + Core Pages (Days 1-3)
**Build the skeleton. Get the homepage and blog working.**

- [ ] Create Astro project in new repo (`purebrain-site`)
- [ ] Set up Vercel project (deploys on every push)
- [ ] Create shared layout: header, footer, navigation, meta tags
- [ ] Port brand CSS: colors, fonts, animations, responsive breakpoints
- [ ] **Migrate Homepage (page 11)**: hero section, video background, living-background canvas, demo player, pricing section, all CTAs
- [ ] **Migrate Blog system**: convert all 22 posts to markdown, build listing page with category filtering, individual post template with FAQ support
- [ ] Set up media pipeline: download all WordPress uploads, host on R2/Vercel Blob
- [ ] Verify: Homepage looks identical on desktop + mobile. Blog posts match. All images load.

**Milestone**: Homepage + blog live on preview URL (e.g., `purebrain-preview.vercel.app`)

### Phase 2: Revenue Pages + Integrations (Days 4-6)
**Get the money-making pages working.**

- [ ] **Migrate Pay-test-2 (page 689)**: Full chatbox, payment flow, all JS logic
- [ ] **Migrate Pay-test-sandbox-3 (page 1232)**: Testing version
- [ ] Rebuild referral system as Vercel serverless function
- [ ] Set up Brevo integration: subscribe forms, API calls, automation triggers
- [ ] Set up Google Tag Manager in layout
- [ ] **Migrate Compare hub + all 11 comparison pages**
- [ ] **Migrate Calculator page (777)**
- [ ] **Migrate Why PureBrain (794)**, Invitation (987), Mission/Values (929)
- [ ] Set up security headers in `vercel.json` (CSP, HSTS, X-Frame-Options)
- [ ] Content gate middleware for training pages
- [ ] End-to-end payment test on preview URL

**Milestone**: Full payment flow working on preview URL. Brevo capturing leads. All comparison pages live.

### Phase 3: Everything Else (Days 7-9)
**Port remaining pages. QA everything.**

- [ ] Migrate all Tier 3 pages (client pages, sales tools, investor pages)
- [ ] Migrate all Tier 4 pages (legal, utility)
- [ ] Set up 301 redirects in `vercel.json` for any URL changes
- [ ] Build auto-sitemap generation
- [ ] Structured data (JSON-LD) for all pages
- [ ] Full SEO audit: compare every page's meta tags, OG images, canonical URLs
- [ ] Mobile QA: every page on iPhone + Android viewport
- [ ] Desktop QA: every page on Chrome, Firefox, Safari
- [ ] Performance audit: Lighthouse scores for all core pages
- [ ] Accessibility check
- [ ] Archive/skip test pages and backups that aren't needed

**Milestone**: Complete 1:1 replica on preview URL. Every page verified.

### Phase 4: The Flip (Day 10 — 30 minutes)
**Point the domain. Go live.**

- [ ] Final side-by-side review with Jared on preview URL
- [ ] **DNS change**: Update `purebrain.ai` CNAME/A record to Vercel
- [ ] SSL auto-provisions (usually under 5 minutes)
- [ ] Verify live site loads correctly
- [ ] Test payment flow on production domain
- [ ] Test Brevo form submission on production domain
- [ ] Test referral system on production domain
- [ ] Monitor for 24 hours
- [ ] **Keep WordPress running on GoDaddy as backup** for 30 days
- [ ] After 30 days with zero issues: cancel GoDaddy hosting

**Milestone**: purebrain.ai running on Vercel. WordPress backup available if needed.

---

## URL Preservation (SEO Protection)

Every URL stays the same:

```
purebrain.ai/                              -> homepage
purebrain.ai/blog/                         -> blog listing
purebrain.ai/blog/teach-your-ai.../        -> blog post
purebrain.ai/compare/                      -> compare hub
purebrain.ai/purebrain-vs-chatgpt/         -> comparison page
purebrain.ai/ai-tool-stack-calculator/     -> calculator
purebrain.ai/privacy-policy/               -> legal
purebrain.ai/terms-of-service/             -> legal
... (all 82 pages keep their exact URLs)
```

Any URLs that need to change get 301 redirects in `vercel.json`:
```json
{
  "redirects": [
    { "source": "/old-path/", "destination": "/new-path/", "permanent": true }
  ]
}
```

---

## What Changes for Jared (Day-to-Day)

| Before (WordPress) | After (Vercel) |
|--------------------|--------------------|
| Can't see what Aether changed without logging into WP admin | Every change is a git commit with a description |
| Changes go live immediately (no staging) | Preview URL for every change — review before it goes live |
| Page breaks = scramble to restore from backup | Page breaks = `git revert` (10 seconds) |
| Plugin updates can cascade-break things | No plugins. Code is code. |
| GoDaddy hosting fees | Vercel free tier (upgrade to Pro at $20/mo if needed) |
| Slow page loads (WordPress PHP rendering) | Static HTML served from edge CDN (fastest possible) |

**What stays exactly the same:**
- Portal (portal.purebrain.ai) — completely separate, no change
- Brevo email automations — no change on Brevo side
- PayPal payment flows — same JS code
- Google Analytics / GTM — same tracking
- All URLs — no SEO impact
- DNS managed in Cloudflare — just one record change

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Something breaks on go-live | WordPress stays running for 30 days. DNS flip-back takes 60 seconds. |
| SEO ranking drop | All URLs preserved. 301 redirects for any changes. Sitemap submitted to Google. |
| Email deliverability | Brevo is separate from hosting. SPF/DKIM records don't change. |
| Payment flow breaks | Full E2E test on preview URL before DNS flip. Sandbox testing. |
| Missing page/content | Full inventory above. Side-by-side QA before flip. |
| Vercel goes down | Vercel has 99.99% uptime SLA. But we keep WordPress backup for 30 days. |

---

## Cost Comparison

| Item | GoDaddy (current) | Vercel (new) |
|------|-------------------|-------------|
| Hosting | ~$25-35/mo | $0 (free tier) or $20/mo (Pro) |
| SSL | Included | Free (automatic) |
| CDN | Cloudflare (free) | Vercel Edge + Cloudflare (free) |
| Plugins | Free (but cost us TIME) | N/A |
| Media storage | Included in GoDaddy | Cloudflare R2: ~$0.50/mo for our volume |
| **Total** | **~$30/mo + massive time cost** | **~$0-20/mo + near-zero friction** |

The real savings isn't dollars — it's the hours we spend fighting WordPress every week.

---

## Timeline Summary

| Phase | Days | What's Done |
|-------|------|-------------|
| Phase 1: Foundation | Days 1-3 | Homepage + blog + media on preview URL |
| Phase 2: Revenue | Days 4-6 | Payment flows + integrations working on preview |
| Phase 3: Everything Else | Days 7-9 | All 82 pages ported + full QA |
| Phase 4: The Flip | Day 10 | DNS change. Live on Vercel. |
| Monitoring | Days 10-40 | WordPress backup running. Monitor everything. |
| Decommission | Day 40 | Cancel GoDaddy if all clear. |

**Total: ~10 working days to full migration, with WordPress as safety net for 30 days after.**

This can happen alongside normal daily work — I build the Vercel site during focused sessions while the WordPress site stays live and untouched until we flip.

---

## Decision Points for Jared

1. **Green light to start Phase 1?** (I can begin building the Astro/Vercel project immediately)
2. **Keep current domain setup?** (purebrain.ai DNS stays in Cloudflare, just change one record)
3. **Any pages to skip/archive?** (Some test/backup pages might not need migrating)
4. **Priority order?** (I've suggested core revenue pages first — agree?)

---

*This plan builds on the side. WordPress stays untouched until we flip. Zero risk to current operations.*
