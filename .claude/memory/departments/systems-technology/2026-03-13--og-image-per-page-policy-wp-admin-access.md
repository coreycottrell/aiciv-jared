# ST# OG Image Per-Page Policy + WP Admin Access Investigation

**Date**: 2026-03-13
**Agent**: dept-systems-technology
**Type**: policy + gotcha + architecture

## Task 1: Per-Page OG Image Fix

### The Problem
fix_og_tags.py was applying the animated GIF to ALL 35+ pages. Jared wanted:
- Homepage + pay-test pages = animated GIF
- Invitation page = different OG image
- All other pages = what Yoast had originally

### Yoast OG Data (discovered by examining HTML files)
Since the CF Pages REST API is blocked by Cloudflare WAF (returns homepage HTML), we extracted Yoast OG data directly from the HTML files by stripping the injected block and looking for remaining og:image tags.

Results:
- Most pages: PT icon (`cropped-cropped-MA1.BI-1.2.4-002-211107-Icon-PT.png`) = Yoast site default
- `compare`: `purebrain-homepage-og.jpg` (page-specific Yoast OG)
- `ai-tool-stack-calculator`: `ai-tool-stack-calculator-og.png` (page-specific)
- `your-ai-tim-cook`: `og-tim-cook.jpg` (page-specific)
- `invitation`: standalone page, NO Yoast OG at all
- `index.html`: PT icon (Yoast default - NOT the GIF before our script)

### OG Image Policy Implemented (2026-03-13)
| Page group | OG Image |
|-----------|---------|
| Homepage + all pay-test/sandbox pages | `Pure-Brain-Vid-3.gif` |
| invitation | `purebrain-homepage-og.jpg` (best branded fallback for standalone page) |
| compare | `purebrain-homepage-og.jpg` (original Yoast) |
| ai-tool-stack-calculator | `ai-tool-stack-calculator-og.png` (original Yoast) |
| your-ai-tim-cook | `og-tim-cook.jpg` (original Yoast) |
| Blog posts | `blog/{slug}/banner.png` (per-post) |
| All other pages | `cropped-cropped-MA1.BI-1.2.4-002-211107-Icon-PT.png` (Yoast default) |

### Script Updated
`/home/jared/projects/AI-CIV/aether/tools/fix_og_tags.py`
- Added OG_IMAGE_GIF, OG_IMAGE_DEFAULT, OG_IMAGE_INVITE constants
- og:image:type now dynamic (gif/png/jpeg based on URL)
- 46 files injected successfully

### Deploy
- CF Pages project: `purebrain-staging`
- 46 files uploaded
- CF cache purged for all affected URLs

## Task 2: WordPress Admin Access

### Root Cause
`purebrain.ai` DNS: `CNAME purebrain.ai => purebrain-staging.pages.dev (proxied)`

This means ALL traffic to purebrain.ai hits Cloudflare Pages, not WordPress.
- `wp-admin/` returns homepage HTML (CF Pages catch-all)
- `wp-login.php` returns homepage HTML
- WP REST API (`/wp-json/`) returns homepage HTML
- No WAF rules pass admin paths through to origin

### WordPress Hosting
GoDaddy Managed WordPress (`wpaas_v2` platform) - NOT accessible via purebrain.ai domain.

### How to Access WordPress Admin
Option A (immediate): Use GoDaddy hosting panel directly
- Log into GoDaddy account
- Navigate to Managed WordPress hosting
- Use "Log in to WordPress" button in hosting panel (bypasses domain DNS)

Option B (permanent fix): Add CF tunnel or subdomain pointing to WP origin
- Create DNS record: `wp.purebrain.ai CNAME [godaddy-wp-direct-url]`
- But this exposes the WP backend publicly - security risk
- Better: Use GoDaddy panel only for admin tasks

Option C (current workaround): WordPress app password via Playwright
- Using PUREBRAIN_WP_APP_PASSWORD with the WP REST API when not blocked
- This works for plugin updates via the standard REST API flow
- See existing agent learnings for deployment patterns

### Current Capability
Aether CAN still:
- Update WordPress via REST API (for Elementor data, pages, posts)
- Deploy plugins via the plugin editor nonce approach
- All WordPress updates happen "in the background" via API

What Jared CANNOT do manually:
- Access wp-admin dashboard via purebrain.ai URL
- Must use GoDaddy hosting panel for admin access

## Tags
og-image, yoast, cloudflare-pages, wp-admin, wordpress-access, fix-og-tags, deploy-pattern
