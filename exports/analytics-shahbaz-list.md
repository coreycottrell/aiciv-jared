# Analytics Deep Dive: Verified Status + Shahbaz Task List
## Date: 2026-02-23

---

## What's Been FIXED Since Report (No Longer Accurate)

| Item | Report Said | Current Reality |
|------|-------------|----------------|
| Blog OG tags | Missing | NOW PRESENT on posts (og:title, og:description, og:image) |
| Meta descriptions | Missing | NOW PRESENT on blog posts via Yoast |
| Author page | No bio | about-aether/ page NOW LIVE with full bio |
| Blog count | 9 posts | Now 10 posts (we-both-wrote-this-post added) |
| Pages count | 10 pages | Now 12 pages (about-aether + blog-neural-feed-memories added) |

---

## What Aether CAN Fix (Doing Now)

| Item | Fix | Status |
|------|-----|--------|
| Thank You page noindex | Add noindex via Yoast/plugin | Launching now |
| Privacy/Terms noindex | Same approach | Launching now |
| FAQ schema on blog posts | Add FAQPage JSON-LD markup | Can do via plugin update |
| Article schema description consistency | Fill missing description fields | Can do via Yoast |
| Homepage OG tags | Add og:title, og:description, og:image | Can do via plugin |

---

## What SHAHBAZ Needs to Do (Requires Manual/Admin Access)

### P0 - This Week (Highest Impact)

1. **Google Search Console Verification**
   - Go to search.google.com/search-console
   - Add property as Domain: purebrain.ai
   - Copy TXT record → add to Cloudflare DNS
   - After verification: submit sitemap_index.xml
   - ~30 min, one-time setup
   - THIS IS THE #1 BLOCKER - zero Google indexing until this is done

2. **GA4 Property Creation**
   - Go to analytics.google.com
   - Create account "PureBrain.ai" → property "PureBrain Production"
   - Create Web data stream for purebrain.ai
   - Send Measurement ID (G-XXXXXXXXXX) to Aether
   - Set data retention to 14 months (Admin → Data Settings)
   - ~45 min, one-time setup

3. **Microsoft Clarity Setup**
   - Go to clarity.microsoft.com
   - Create project "PureBrain.ai"
   - Install WordPress plugin OR add tracking code
   - ~10 min, one-time setup

### P1 - This Month

4. **Homepage H1 Tag**
   - Open Elementor on homepage
   - Find the main heading widget
   - Change HTML tag from whatever it is (div/span) to H1
   - ~5 min in Elementor editor
   - Aether cannot do this via REST API (Elementor visual builder needed)

5. **Backlink Outreach** (Jared, not Shahbaz)
   - Contact Thrive Global, Jerusalem Post, CEOWORLD
   - Ask them to add/update backlinks pointing to purebrain.ai
   - Jared has existing relationships with these publications

6. **Link GA4 to Search Console** (after both are set up)
   - In GA4 Admin → Property Settings → Search Console links
   - ~5 min after both platforms verified

7. **Cloudflare Cache Purge** (whenever CSS/content changes aren't showing)
   - Cloudflare dashboard → Caching → Purge Everything
   - Or set up a Page Rule for more targeted purging

---

## Still Accurate (No Changes Needed to Report)

- Google indexing: still zero results (expected for new domain)
- robots.txt: correct, no issues
- FAQ sections exist visually but no schema markup
- H1 missing from homepage
- Thank you page still indexable (being fixed)
- Internal link density still low (Read Next blocks being deployed)
- Twitter Card tags not present (being addressed via og:image split strategy)
- No Bluesky sameAs link in author schema

---

## Summary for Jared

**Big picture**: The report was accurate when written. Since then, several items have been fixed (OG tags, meta descriptions, author page). The single highest-ROI action remains **GSC verification** - until that's done, Google doesn't know the site exists. Shahbaz can knock that out in 30 minutes.

Everything Aether can fix without admin access is being fixed now. The Shahbaz list above covers the 7 items that need human hands.
