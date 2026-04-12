# PureBrain.ai Repo Updates — For Corey & Witness

Tracked changes to purebrain.ai infrastructure. Send to Witness team for coordination.

---

## 2026-03-07

### 1. Homepage Content Swap
- **What**: Swapped homepage-clone-test content onto main homepage (page ID 11)
- **How**: Copied `_elementor_data` (498K chars) from page 1434 → page 11 via REST API, cleared Elementor cache
- **Cleanup**: Deleted homepage-clone-test page (ID 1434)
- **Preserved**: Front page setting (page_on_front = 11), `elementor_canvas` template

### 2. Duplicate Plugin Deactivation — Blog Transparency Section Fix
- **Problem**: Every blog post had the Aether Transparency Report section rendered TWICE (visually duplicated at bottom of posts)
- **Root cause**: Two standalone plugins (`PureBrain Blog Styles` v1.0.0 and `PureBrain Blog Styling` v1.0.1) were active alongside the `PureBrain Security` plugin (v6.2.7), all three outputting identical blog features (CSS, transparency section, lead capture, nav menus, FAQ accordions)
- **Fix**: Deactivated both duplicate plugins:
  - `purebrain-blog-styles/purebrain-blog-styles` → inactive
  - `pb-blog-styling/pb-blog-styling` → inactive
- **Why safe**: The `PureBrain Security` plugin (v6.2.7) already contains all blog styling, transparency section rendering, lead capture, social sharing, FAQ accordion, and nav menu code. The standalone plugins were redundant copies.
- **Remaining known duplicates**: `pb-blog-faq`, `pb-lead-capture`, `pb-social-sharing` also duplicate features in the security plugin but don't cause visible issues (different element injection strategies). These could be cleaned up later.
- **Verification**: All blog posts now show exactly 1 transparency section. Homepage, other pages unaffected.

### Active Plugin List (post-change)
Key active plugins:
- PureBrain Security v6.2.7 (main feature plugin — blog styles, transparency, lead capture, social share, nav, FAQ, etc.)
- PureBrain Blog FAQ v1.0.0 (active, partially duplicates security plugin FAQ)
- PureBrain Lead Capture (active, partially duplicates security plugin lead capture)
- PureBrain Social Sharing (active, partially duplicates security plugin social share)
- PureBrain Awaken CTA, Button Styling, Footer Branding, Breadcrumb Fix, etc. (unique features)

### 3. Full Site Export Package (for Corey/Witness)
- **What**: Complete portable export of purebrain.ai for replication on external hosting
- **Location**: `exports/purebrain-site-repo/` + tarball `exports/purebrain-site-repo-2026-03-07.tar.gz` (298MB)
- **Contents**:
  - 105 pages as rendered HTML (82 pages + 22 blog posts + blog listing, 0 failures)
  - 85 media files (images, videos)
  - 28 Elementor JSON data exports (`_elementor_data` from context=edit API)
  - All custom plugin PHP source code (25 plugin versions documented)
  - 19 CSS files + 13 JS files extracted from live site
  - Full WordPress data as JSON (pages, posts, categories, menus, active plugins, site settings)
  - README + ARCHITECTURE docs explaining how everything connects
- **Key finding**: Most pages are self-contained HTML in `<!-- wp:html -->` blocks — highly portable, no WordPress dependency needed for static serving
- **Note for external team**: `_elementor_data` only returns via REST API with `?context=edit` parameter

### 4. Vercel Migration Phase 1 — Astro Project Built & Deployed
- **What**: New Astro-based static site replicating purebrain.ai, deployed to Vercel
- **Preview URL**: https://purebrain-site.vercel.app
- **Project location**: `purebrain-site/`
- **Built**: 24 pages (homepage + 22 blog posts + blog listing), 0 errors
- **Stack**: Astro (static output) + Vercel hosting + security headers
- **Blog posts**: All 22 converted from WP HTML → markdown with frontmatter
- **Brand CSS**: Dark bg (#080a12), blue/orange brand colors, pb-blog-post class preserved
- **Security**: vercel.json with HSTS, X-Frame-Options, nosniff, Referrer-Policy
- **Phase 2 needed**: Revenue pages, payment flows, compare hub, remaining content pages, media migration

---

*Updated by Aether — will append new entries as changes are made.*
