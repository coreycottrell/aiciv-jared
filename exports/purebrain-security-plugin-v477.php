<?php
/**
 * Plugin Name: PureBrain Security
 * Plugin URI:  https://purebrain.ai
 * Description: Security hardening: blocks user enumeration, adds security headers, provides server-side proxies for conversation logging and payment verification. API keys are held server-side only. Also exposes Yoast SEO meta via REST API. Adds FAQ accordion on single blog posts. Adds "Home | Subscribe | Free AI Assessment" nav menu on single blog posts and category/archive pages (Subscribe links to /blog/#neural-feed-subscribe). Nav menu hover: orange (#f1420b) universally on ALL page types via html body prefix (max specificity). Fixes CTA button orange default + blue hover, newsletter link readability in CTA footer. Newsletter link gets orange button-style hover. Strips inline styles from newsletter links so plugin hover CSS can take effect. Subscribe link hover override: counters broad Additional CSS blue-glow rule with higher-specificity selectors. Footer logo brand fix: replaces "Pure Brain" plain text with color-coded PUREBRAIN.AI on all pages. Breadcrumb structured data fix: ensures every ListItem in Yoast BreadcrumbList has required 'item' (URL) property (fixes GSC error). REST endpoint: POST /purebrain/v1/update-post-meta to set _yoast_wpseo_metadesc (and other protected postmeta) via authenticated API calls. Lead capture: in-content subscribe box (50% scroll) + post-read CTA bar (85% scroll) + Brevo proxy endpoint. Both forms submit to Brevo list 3 (The Neural Feed) via server-side proxy. Aether Transparency Section: auto-injects a weekly AI partnership transparency report into every single blog post, after post content and before .blog-cta-block. Data stored as wp_option purebrain_transparency_data (JSON), updatable via authenticated REST endpoint POST /purebrain/v1/transparency-data. Gracefully absent when option is empty. In-text link hover fix (v3.9.1): body.single-post in-content links now show orange background + WHITE text on hover (was invisible orange-on-orange). Excludes CTA button and tag pills. Transparency CTA button white text fix (v3.9.2): .aether-transparency__cta-btn enforced white text with maximum-specificity selectors overriding any Additional CSS color inheritance. Twitter image override (v3.9.3): adds _yoast_wpseo_twitter-image and _yoast_wpseo_twitter-image-id to REST API whitelist and update-post-meta allowed keys, so homepage can have a separate static JPG for Twitter/X while keeping GIF for og:image. Blog listing Read More button (v4.0.0): JS on blog listing page (/blog/) ensures EVERY post card has a "READ MORE" orange button — uniform appearance rule enforced permanently. Posts_per_page filter (v4.0.0): pre_get_posts filter limits blog listing to 10 posts max. AI Partnership Guide content gate (v4.1.0): partial content gate on /ai-partnership-guide/ — sections 1-3 visible freely, sections 4-7 hidden behind gradient fade + email capture form. Server-side Brevo proxy endpoint POST /purebrain/v1/guide-unlock accepts email + first name, adds to Brevo list 3, stores unlock in localStorage. Auto-reveals on return visit. GEO Fix 3 (v4.2.0): Social sharing bar injection on all single blog posts. Injects LinkedIn, X (Twitter), Email, and Copy Link buttons before .blog-cta-block via JS DOM insertion (same pattern as transparency section). CSS injected via wp_head. Also un-hides theme-native .post-social-sharing buttons. Buttons styled in PureBrain brand colors: default Pure Tech Blue (#2a93c1), hover orange (#f1420b). IndexNow (v4.3.0): auto-pings api.indexnow.org on publish_post and save_post hooks. Key: 823869521fbf4f33b93e67c781571e20. Verification file required at site root: {key}.txt containing the key string. Notifies Bing, Yandex, and IndexNow-compatible engines instantly on content change. OG meta fields (v4.4.0): adds _yoast_wpseo_opengraph-title, _yoast_wpseo_opengraph-description, _yoast_wpseo_opengraph-image, _yoast_wpseo_opengraph-image-id, _yoast_wpseo_twitter-title, _yoast_wpseo_twitter-description to both the register_post_meta REST registration and the update-post-meta allowlist. Aether Footer Credit (v4.5.0): injects a fixed-position footer credit bar on ALL pages site-wide: "Built by AETHER (an AI) for PureBrain.ai, PureMarketing.ai & PureTechnology.ai". Background #080a12, text #6b7280, AETHER bold white, site names in brand colors (orange/blue), links open in _blank. 36px height. Body gets 36px padding-bottom to prevent content overlap. z-index 9999. Homepage Backup Rewrite (v4.7.7): adds rewrite rule mapping /2/ to page ID 1128 (password-protected homepage backup). WordPress does not allow numeric slugs via REST API; this rewrite rule serves the page at /2 path while preserving native WP password protection.
 * Version:     4.7.7
 * Author:      Aether (AI) for Pure Technology
 * Author URI:  https://purebrain.ai
 * License:     Private - All Rights Reserved
 *
 * Changelog:
 *   v4.7.5 - PRICING BULLET ALIGNMENT FIX: Nova/AI name text no longer splits into
 *            separate columns in the Awakened pricing tier bullet points.
 *            Root cause: .pricing-card__feature uses display:flex. The <span class="ai-name-dynamic">
 *            and the trailing text node become separate flex items, causing "Nova"
 *            to appear left-separated from the rest of the bullet text.
 *            Fix: CSS changes .pricing-card__feature to display:grid (2 cols: icon + text).
 *            In grid layout, span and text node fall into same track, flowing inline.
 *            Applies site-wide to all pages with pricing cards.
 *   v4.7.4 - CSP FIX: Cloudflare R2 video bucket added to connect-src + media-src.
 *            Root cause of video failures on homepage/pay-test-2/pay-test-sandbox-2:
 *            HLS.js uses XHR/fetch to download .m3u8 + .ts files from R2. Without
 *            pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev in connect-src, CSP blocked
 *            all these requests. Video readyState stayed at 0 (HAVE_NOTHING), never played.
 *            Fix: R2 bucket URL added to connect-src. media-src added for blob: MSE URLs.
 *   v4.7.3 - CHATBOX DISCOVER BUTTON UX FIX (all chatbox pages):
 *            1. Button text: "Click to discover what [AI NAME] can do"
 *            2. Input field DISABLED when discover button appears
 *            3. Placeholder: "Click the button above ↑" while disabled
 *            4. Input RE-ENABLED after button click
 *            5. 30-minute session timer (override 15min in cached Elementor HTML)
 *            Injected via wp_footer on pages 688, 689, 11, 439, 468.
 *            Uses MutationObserver to catch dynamically-added discover button.
 *   v4.7.2 - SANDBOX FIX: pay-test-sandbox-2 (page 688) now uses PayPal Sandbox
 *            environment. Replaces production SDK with sandbox SDK, swaps client ID
 *            to sandbox credentials, and uses createOrder (one-time capture) for
 *            testing instead of createSubscription (which needs sandbox plan IDs).
 *   v4.7.1 - URGENT FIX: PayPal button routing restored. Root cause: DOMContentLoaded
 *            callback in page JS overwrites window.openWaitlistModal (which PayPal SDK
 *            section had set to PayPal checkout) back to the Google Forms waitlist
 *            version. Fix: Plugin injects a late-running script that restores
 *            window.openWaitlistModal = window.openPayPalCheckout after all
 *            DOMContentLoaded handlers have fired. Uses setTimeout(0) for safety.
 *   v4.7.0 - URGENT FIX: PayPal payment gateway restoration + CSP worker-src.
 *            PayPal SDK creates Web Workers from blob: URLs. Without worker-src
 *            in the CSP, "script-src" was used as fallback, which blocks blob:.
 *            Result: PayPal Smart Buttons failed to render, payment was broken.
 *            Fix: Added "worker-src 'self' blob:" to CSP. Also added GTM and
 *            GoDaddy tracking scripts to script-src (were being blocked).
 *   v4.6.9 - Chatbox bypass v4.6.9 (capturing event listeners) + session timer fix.
 *   v4.6.7 - HOTFIX: Homepage/pay-test/invitation video background restoration.
 *            v4.6.6 made body opaque (#080a12) on ALL pages, but pages with video/3D
 *            backgrounds use z-index:-1 (behind body). Opaque body covered the video.
 *            Fix: html stays dark (#080a12), body made transparent on pages that have
 *            fixed-position video/3D backgrounds (homepage, pay-test pages 688/689,
 *            invitation page 987). All other pages keep opaque dark body.
 *   v4.6.6 - SITE-WIDE dark background enforcement (LOCKED IN per Jared 2026-02-27).
 *            Replaces page-777-only fix with GLOBAL rule for ALL pages on purebrain.ai.
 *            NO page should EVER show orange/light background again.
 *            3-layer approach: CSS priority 1 + CSS priority 999 + JS enforcement.
 *            Exceptions: blog posts (body.single-post) keep their own dark bg system
 *            with GIF overlay pseudo-elements from Additional CSS.
 *   v4.6.5 - Calculator page 777 dark background nuclear fix.
 *            Problem: page 777 showed orange background despite fix deployed in page content.
 *            Root cause: theme/plugin CSS cascade, potential JS color override post-paint.
 *            Fix (3-layer):
 *            Layer 1 - wp_head priority 1 (fires FIRST): body.page-id-777 { background:#080a12!important }
 *            Layer 2 - wp_head priority 999 (fires LAST): same rule after ALL other CSS
 *            Layer 3 - JS at DOMContentLoaded: force document.body.style.background = '#080a12'
 *            All three layers combined ensure the dark background persists regardless of
 *            what Elementor, theme JS, or plugins inject after page load.
 *   v4.6.4 - CSP connect-src: add 89.167.19.20:8443 for Witness birth webhook
 *            (sandbox direct access). Allows browser to reach the Aether log
 *            server directly from sandbox pay-test page (page 688) without
 *            triggering CSP block. No impact on production routing.
 *   v4.6.3 - CSP connect-src: add cdn.jsdelivr.net to fix Three.js neural network
 *            background on /invitation/ page. Root cause: the Three.js module script
 *            uses dynamic import() (await import('https://cdn.jsdelivr.net/...')).
 *            Dynamic imports use the fetch/connect mechanism, governed by connect-src.
 *            cdn.jsdelivr.net was already in script-src (for <script src> tags) but
 *            NOT in connect-src, causing dynamic import() calls to fail silently.
 *            Fix: add https://cdn.jsdelivr.net to connect-src directive.
 *            No security risk: only allows fetching JS from a trusted CDN that was
 *            already permitted for script loading.
 *   v4.6.0 - Why PureBrain link injection on homepage + pay-test pages.
 *            Adds a "Why Choose PureBrain?" link in the Aether footer credit bar
 *            on ALL pages (visible on homepage, blog, and all site pages).
 *            Footer bar updated: appended separator + "Why Choose PureBrain?" link
 *            in blue (#2a93c1) with orange (#f1420b) hover, linking to /why-purebrain/.
 *            Also injects a standalone "Why PureBrain Is Different" bar on the homepage
 *            (is_front_page()) above the footer credit bar via wp_footer priority 99.
 *            Bar style: dark bg #0d1117, border-top #2a93c1, centered link, subtle.
 *            Does NOT touch og:image, twitter:image, GIF references, or any Elementor data.
 *
 * Installation:
 *   1. Upload this file via WP Admin > Plugins > Add New > Upload Plugin
 *   2. Activate the plugin
 *   3. Add ACGEE_API_KEY to wp-config.php (see deployment instructions)
 *
 * Changelog:
 *   v4.5.0 - Aether Footer Credit bar: fixed-position bar on ALL pages site-wide.
 *            Text: "Built by AETHER (an AI) for PureBrain.ai, PureMarketing.ai & PureTechnology.ai"
 *            Style: background #080a12, muted gray text #6b7280, AETHER bold white,
 *            PureBrain.ai in orange (#f1420b), PureMarketing.ai + PureTechnology.ai in blue (#2a93c1).
 *            Links open in _blank. Height: 36px. z-index: 9999.
 *            Body gets padding-bottom: 36px to prevent content overlap.
 *            Injected via wp_footer at priority 100 (after everything else).
 *            Applies on all pages, posts, archives, and the homepage.
 *   v4.4.0 - OG meta fields added to REST API and update-post-meta allowlist.
 *   v4.3.0 - IndexNow integration: instant search engine notification on publish/update.
 *            Fires on publish_post (new publications) and save_post (edits to published
 *            posts and pages). Submits a POST to https://api.indexnow.org/IndexNow with
 *            the page URL. No plugin conflict risk — does not use Yoast filters.
 *            API key: 823869521fbf4f33b93e67c781571e20
 *            Verification file required at webroot: {key}.txt containing the key.
 *            Silent fail on network error (non-critical, best-effort ping).
 *            Covers Bing, Yandex, and all IndexNow-compatible search engines.
 *   v4.2.0 - GEO Fix 3: Social sharing bar injection on single blog posts.
 *            Custom pb-social-share bar injected via JS (wp_footer, priority 25)
 *            before .blog-cta-block (same insertion pattern as transparency section).
 *            Buttons: LinkedIn, X/Twitter, Email, Copy Link.
 *            Styled in PureBrain brand: Pure Tech Blue (#2a93c1) default,
 *            orange (#f1420b) hover. Inline SVG icons (no external dependency).
 *            Copy Link button: copies current URL to clipboard, confirms with
 *            "Copied!" feedback for 2 seconds.
 *            Also un-hides theme-native .post-social-sharing via wp_head CSS
 *            override (counters Additional CSS display:none hiding rule).
 *            Only fires on body.single-post pages.
 *   v4.1.1 - TEST 20: Blog nav copy update.
 *            "AI Assessment" → "Free AI Assessment" in nav menu label.
 *            Applies on single blog posts and category/archive pages.
 *            No functional changes — text label only.
 *   v4.1.0 - AI Partnership Guide content gate.
 *            Sections 1-3 visible freely (the "problem" content).
 *            Sections 4-7 hidden behind a gradient fade-out overlay + email form (the "solution").
 *            Gate activates only on /ai-partnership-guide/ URL.
 *            Email form collects email (required) + first name (optional).
 *            On submit: POST /wp-json/purebrain/v1/guide-unlock (server-side Brevo proxy).
 *            Adds contact to Brevo list 3 (The Neural Feed) with FIRSTNAME attribute.
 *            On success: content revealed, pb_guide_unlocked=1 stored in localStorage.
 *            Return visit: auto-reveal if localStorage shows previously unlocked.
 *            Visual: dark gradient overlay, CSS blur on hidden sections, clean centered form.
 *            No API key exposure client-side. BREVO_API_KEY read from wp-config.php.
 *            Rate limit: 5 requests per IP per minute (same as subscribe endpoint).
 *   v4.0.0 - Blog listing Read More button: uniform "READ MORE" orange button on ALL
 *            blog post cards on the main /blog/ listing page. Previously only posts
 *            using the <!--more--> tag showed the button; posts with plain excerpts
 *            did not. Fix: JS injected via wp_footer on the blog listing page detects
 *            every .wp-block-latest-posts__post-excerpt and appends an orange "READ MORE"
 *            anchor if one doesn't already exist. Button style: orange (#f1420b) bg, white
 *            text, rounded, uppercase. The post href is read from the nearest sibling anchor
 *            linking to the post. PERMANENT RULE: all blog post cards must have READ MORE.
 *            Also adds pre_get_posts filter limiting the blog listing page to max 10 posts.
 *   v3.9.2 - Transparency section CTA button white text fix.
 *            Problem: .aether-transparency__cta-btn showed invisible text (orange-on-orange).
 *            Root cause: broad Additional CSS `body.single-post a { color: #f1420b }` overrides
 *            the transparency CSS `color: #ffffff !important` via load order (Additional CSS loads
 *            after plugin wp_head hooks at priority 30 and wins the specificity tie).
 *            Fix: New wp_head hook (priority 99, after Additional CSS) injects
 *            <style id="purebrain-transparency-cta-v392"> with maximum-specificity selectors:
 *            body.single-post .aether-transparency .aether-transparency__cta-btn
 *            Covers: default color, text-decoration, hover state.
 *            Also deployed as <style id="pb-transparency-cta-v394"> in each post's content
 *            via REST API for immediate effect before plugin deployment.
 *   v3.9.1 - Blog in-text link hover fix: orange background + white text on hover.
 *            Problem: body.single-post in-content links are orange (#f1420b) by default.
 *            When hovered, the theme/Additional CSS added an orange background — causing
 *            orange text on orange background (invisible).
 *            Fix: on hover, keep orange background but swap text to white (#ffffff).
 *            Adds smooth 0.2s transition for both background-color and color.
 *            Adds subtle padding (1px 4px) + border-radius (3px) for pill effect.
 *            Exclusions: :not(.blog-cta-button):not([rel="tag"]) — does not override
 *            the CTA button (handled by v3.9.0) or tag pills (handled by v3.9.0).
 *            Selectors: .entry-content a + .elementor-widget-theme-post-content a
 *            (covers both standard WordPress and Elementor Pro theme post content).
 *            Also deployed as <style id="pb-link-hover-v391"> in each post's content
 *            via REST API for immediate effect before plugin deployment.
 *   v3.9.0 - Blog styling: tag pills + CTA button white text enforcement.
 *            Tag pills (body.single-post .post-tags .tag-links a[rel="tag"]):
 *            default blue (#2a93c1) bg + white text, hover orange (#f1420b) bg +
 *            white text. Pill shape (border-radius: 20px). Covers WordPress standard
 *            .post-tags > .tag-links > a[rel="tag"] HTML structure.
 *            CTA button: additional high-specificity white text rules added as
 *            belt-and-suspenders backup covering posts without inline style attr.
 *   v3.8.0 - Security hardening: three fixes from security review.
 *            MED-003: Brevo subscribe endpoint now explicitly fail-closed (HTTP 503 + clear
 *            error message) when BREVO_API_KEY constant is not defined in wp-config.php.
 *            LOW-001: Transparency section output — esc_html() applied at echo point
 *            (not at variable assignment). Raw values stored in variables, escaped only
 *            when written to HTML output. Follows WordPress VIP output-escaping best practice.
 *            LOW-002: purebrain_get_client_ip() now requires the optional
 *            PUREBRAIN_BEHIND_CLOUDFLARE constant to be defined before trusting
 *            HTTP_CF_CONNECTING_IP. Without it, falls back to REMOTE_ADDR. Prevents
 *            spoofed CF-Connecting-IP headers on installations not behind Cloudflare.
 *   v3.7.0 - Blog nav "Blog" link changed to "Subscribe" on single posts + category/archive pages.
 *            The pb-blog-nav (plugin-injected nav bar) previously showed "Blog" linking to /blog/.
 *            Updated to show "Subscribe" linking to /blog/#neural-feed-subscribe (the subscribe
 *            section at the bottom of the blog page). When you're already reading a post, linking
 *            to the blog index is redundant — Subscribe is more useful and drives email signups.
 *   v3.6.0 - Aether Transparency Section auto-injection on single blog posts.
 *            New REST endpoint: POST /wp-json/purebrain/v1/transparency-data
 *            Accepts: week_of, summary, stats (specialist_agents, work_domains,
 *            deliverables, human_hours), work_breakdown (array of domain/description/
 *            effort/value rows), biggest_win, cta_text (optional override).
 *            Data stored in wp_options as purebrain_transparency_data (JSON).
 *            CSS injected via wp_head (is_single() only, id=purebrain-transparency-css).
 *            HTML rendered via wp_footer (is_single() only), positioned after post
 *            content and before .blog-cta-block via JS DOM insertion.
 *            If purebrain_transparency_data option is empty/missing, nothing is injected.
 *            All dynamic output escaped with esc_html/esc_attr/esc_url.
 *            REST endpoint requires authenticated user with manage_options capability.
 *            Update data via tools/update_transparency_data.py helper script.
 *   v3.5.0 - Lead capture systems for blog posts.
 *            Three capture points added to body.single-post pages:
 *            (1) In-Content Subscribe Box: slides in after 50% scroll depth.
 *                Subtle inline dark card (#0d1117 bg, #2a93c1 border). Single email
 *                field. X-button dismisses for 7 days via localStorage.
 *                Text: "Enjoying this? Aether writes more like this every day in The Neural Feed."
 *            (2) Post-Read CTA Bar: floating bottom bar after 85% scroll depth.
 *                More prominent than the inline box. Only shows if 50% box was
 *                dismissed/not converted. Dismisses for 14 days via localStorage.
 *                Text: "You made it to the end. That means you take AI seriously."
 *            (3) Subscriber Detection: sets localStorage 'pb_subscribed'=true on
 *                successful submit. Neither form shows if already subscribed.
 *                Success message: "Welcome to The Neural Feed. Check your inbox."
 *            Both forms submit via server-side Brevo proxy:
 *                POST /wp-json/pb-security/v1/subscribe
 *                Body: { "email": "..." }
 *                Calls Brevo API to add contact to list 3 (The Neural Feed).
 *                Rate limit: 5 requests per IP per minute.
 *            CSS injected via wp_head, JS injected via wp_footer.
 *            Only fires on body.single-post (single blog post pages).
 *   v3.4.0 - REST endpoint for updating protected postmeta (Yoast SEO meta descriptions).
 *            Adds POST /wp-json/purebrain/v1/update-post-meta which authenticates via
 *            WordPress application passwords (same auth as REST API) and writes
 *            _yoast_wpseo_metadesc (and whitelisted meta keys) via update_post_meta().
 *            This bypasses the limitation of _yoast_wpseo_metadesc not being registered
 *            as writable in the standard wp/v2/posts meta endpoint. Requires 'edit_posts'
 *            capability. Allowed keys whitelist prevents abuse.
 *   v3.3.0 - Breadcrumb structured data fix: Google Search Console flagged missing 'item'
 *            (URL) property on last ListItem in Yoast SEO's BreadcrumbList. By default Yoast
 *            omits 'item' on the current page (last breadcrumb). Google now requires it.
 *            Fix: wpseo_schema_breadcrumb filter iterates all itemListElement entries; for
 *            any ListItem missing 'item', injects the canonical URL via get_permalink() (posts/
 *            pages), term_link() (category/tag archives), or get_pagenum_link() (paged archives).
 *            Covers single posts, pages, category archives, tag archives, and custom post types.
 *   v3.2.0 - Nav menu hover UNIVERSAL fix: replaced body-class-scoped selectors with
 *            `html body .pb-blog-nav a:hover` (specificity 0,0,2,1 = beats any single body-class
 *            rule). Works on ALL page types past, present, and future — single posts, category
 *            pages, archive pages, tag pages, custom post types, any new page type. No per-page
 *            selector maintenance needed. Orange (#f1420b) hover guaranteed universally.
 *   v3.1.0 - Nav menu hover color fix: .pb-blog-nav a:hover now correctly shows orange (#f1420b)
 *            on BOTH blog posts AND category/archive pages. Previously the plugin used blue (#2a93c1)
 *            for hover, which was accidentally overridden to orange on blog posts only by the broad
 *            Additional CSS rule `body.single-post a:hover { color: #f1420b }`. On category pages
 *            no such broad rule existed, so hover showed blue. Fix: use orange in the plugin's own
 *            rule and add body-class-scoped higher-specificity selectors to prevent overrides.
 *   v3.0.0 - Footer logo brand fix: replaces "Pure Brain" plain text in div.footer-logo h4 with
 *            color-coded PUREBRAIN.AI on ALL pages site-wide. PUREBR=#2a93c1 (blue),
 *            AI=#f1420b (orange), N=#2a93c1 (blue), .AI=#ffffff (white). Uses JS via wp_footer
 *            hook (priority 30, no page conditional) so it fires everywhere including homepage,
 *            blog index, single posts, archives, and static pages.
 *   v2.9.0 - Added high-specificity CSS override to counter Additional CSS blue-glow rule
 *            (body.single-post .blog-cta-block a:hover) that was matching subscribe links.
 *            Root cause: Additional CSS rule loads after plugin CSS in the HTML head, so at
 *            equal specificity it wins. Fix: plugin CSS now uses a higher-specificity compound
 *            selector (5 qualifiers vs Additional CSS's 4) plus an explicit data-attribute
 *            hook injected by JS (data-pb-subscribe) to make the match unambiguous.
 *            Also includes companion JS to set data-pb-subscribe on subscribe links.
 *            Note: companion narrowing of Additional CSS rule should also be deployed
 *            (see tools/security/deploy_additional_css_fix.py).
 *   v2.8.0 - JS in wp_footer strips inline style="" from subscribe/newsletter/neural-feed
 *            links inside .blog-cta-block on single posts. Inline `color: #2a93c1 !important`
 *            was overriding the plugin's hover CSS (color: #ffffff !important), keeping text
 *            blue on hover instead of turning white. Stripping the attribute lets plugin CSS
 *            take full control of default AND hover appearance.
 *   v2.7.0 - Newsletter subscribe link in .blog-cta-block now shows orange gradient background
 *            on hover (mini button effect: white text + #f1420b orange bg + border-radius).
 *            Default state gets invisible vertical padding so layout doesn't jump on hover.
 *   v2.6.0 - Security hardening: switch proxy endpoints from raw IP to Cloudflare Tunnel
 *            (api.purebrain.ai), enable sslverify=true for valid TLS cert, add transient-based
 *            rate limiting (30 req/min logging, 10 req/min payment), add 64KB body size cap,
 *            replace inline onmouseover/onmouseout handlers with CSS-only hover class.
 *   v2.5.0 - CTA button fix: orange default background restored, blue hover (was orange).
 *            Uses href-based selectors (a[href*="awakening"] vs a[href*="subscribe"]) to
 *            separate button from newsletter link. Removes overbroad p a rule from v2.4.0
 *            that was stripping the button's background color.
 *   v2.4.0 - Nav menu (Home | Blog | AI Assessment) on single posts + category/archive pages.
 *            Newsletter/CTA footer link readability fix.
 *            Removed old "← All Posts" link.
 *   v2.3.0 - FAQ flash-of-content fix, CTA hover white text fix.
 *   v2.2.0 - Blog nav link on category pages.
 *   v2.1.0 - CTA button hover effect.
 *   v2.0.0 - FAQ accordion.
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit; // Exit if accessed directly
}

// ============================================================
// INDEXNOW INTEGRATION (v4.3.0)
// Notifies Bing, Yandex, and other IndexNow-compatible search
// engines instantly when content is published or updated.
//
// API Key: 823869521fbf4f33b93e67c781571e20
// Verification file: https://purebrain.ai/823869521fbf4f33b93e67c781571e20.txt
//
// The key file must exist at the site root and contain the key.
// Create it via WP Admin > Plugins > PureBrain Security (see
// tools/security/indexnow-setup.php) or manually upload:
//   File path (on server): {WEBROOT}/823869521fbf4f33b93e67c781571e20.txt
//   File contents:         823869521fbf4f33b93e67c781571e20
//
// Fires on: publish_post (new posts), post_updated (edits to
// already-published posts), and save_post (catch-all for pages).
// Only fires for public, published posts/pages.
// ============================================================

define( 'PUREBRAIN_INDEXNOW_KEY', '823869521fbf4f33b93e67c781571e20' );

/**
 * Submit a single URL to the IndexNow API.
 *
 * @param string $url The fully-qualified URL to submit.
 * @return bool True on success (HTTP 200/202), false on failure.
 */
function purebrain_indexnow_submit( $url ) {
    $key     = PUREBRAIN_INDEXNOW_KEY;
    $host    = wp_parse_url( home_url(), PHP_URL_HOST );

    $body = wp_json_encode( array(
        'host'    => $host,
        'key'     => $key,
        'keyLocation' => home_url( '/' . $key . '.txt' ),
        'urlList' => array( esc_url_raw( $url ) ),
    ) );

    $response = wp_remote_post(
        'https://api.indexnow.org/IndexNow',
        array(
            'headers'   => array( 'Content-Type' => 'application/json; charset=utf-8' ),
            'body'      => $body,
            'timeout'   => 10,
            'sslverify' => true,
        )
    );

    if ( is_wp_error( $response ) ) {
        // Silent fail — IndexNow ping is best-effort, non-critical
        return false;
    }

    $status = wp_remote_retrieve_response_code( $response );
    // IndexNow returns 200 (OK) or 202 (Accepted) on success
    return in_array( (int) $status, array( 200, 202 ), true );
}

/**
 * Fire IndexNow ping when a new post is published.
 * Hook: publish_post fires once when status transitions TO 'publish'.
 *
 * @param int $post_id Post ID.
 */
add_action( 'publish_post', function ( $post_id ) {
    // Bail on autosaves and revisions
    if ( wp_is_post_revision( $post_id ) || wp_is_post_autosave( $post_id ) ) {
        return;
    }

    $post = get_post( $post_id );
    if ( ! $post || $post->post_status !== 'publish' ) {
        return;
    }

    purebrain_indexnow_submit( get_permalink( $post_id ) );
} );

/**
 * Fire IndexNow ping when an already-published post is saved/updated.
 * Hook: save_post fires on every save; we check old + new status to
 * target "published → published" (i.e. edits to live content) as well
 * as new publications for pages (post_type = 'page').
 *
 * @param int     $post_id Post ID.
 * @param WP_Post $post    Post object after save.
 * @param bool    $update  Whether this is an update (true) or new post (false).
 */
add_action( 'save_post', function ( $post_id, $post, $update ) {
    // Bail on autosaves, revisions, and bulk edits
    if (
        wp_is_post_revision( $post_id ) ||
        wp_is_post_autosave( $post_id ) ||
        ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE )
    ) {
        return;
    }

    // Only ping for published content
    if ( $post->post_status !== 'publish' ) {
        return;
    }

    // For 'post' type: publish_post hook above handles new publications.
    // Here we handle: (a) edits to published posts, (b) pages being published/updated.
    $allowed_types = array( 'post', 'page' );
    if ( ! in_array( $post->post_type, $allowed_types, true ) ) {
        return;
    }

    purebrain_indexnow_submit( get_permalink( $post_id ) );
}, 10, 3 );

// ============================================================
// BREADCRUMB STRUCTURED DATA FIX (GSC: missing 'item' field)
// Yoast SEO omits the 'item' (URL) property from the last
// ListItem in BreadcrumbList. Google Search Console flags this
// as an error. This filter injects the canonical URL for every
// ListItem that is missing the 'item' property.
// ============================================================

add_filter( 'wpseo_schema_breadcrumb', function ( $schema_data ) {
    if ( empty( $schema_data['itemListElement'] ) || ! is_array( $schema_data['itemListElement'] ) ) {
        return $schema_data;
    }

    foreach ( $schema_data['itemListElement'] as &$list_item ) {
        // Only fix items that are missing the 'item' property
        if ( isset( $list_item['item'] ) ) {
            continue;
        }

        // Determine the canonical URL for this breadcrumb position
        $url = '';

        if ( is_singular() ) {
            // Single post, page, or custom post type — use the canonical permalink
            $url = get_permalink();
        } elseif ( is_category() || is_tag() || is_tax() ) {
            // Category, tag, or custom taxonomy archive
            $term = get_queried_object();
            if ( $term && ! is_wp_error( $term ) ) {
                $url = get_term_link( $term );
                if ( is_wp_error( $url ) ) {
                    $url = '';
                }
            }
        } elseif ( is_archive() ) {
            // Date archive, author archive, post type archive, etc.
            $url = get_pagenum_link( get_query_var( 'paged' ) ? get_query_var( 'paged' ) : 1 );
        } elseif ( is_home() || is_front_page() ) {
            $url = home_url( '/' );
        }

        if ( ! empty( $url ) ) {
            $list_item['item'] = esc_url( $url );
        }
    }
    unset( $list_item ); // Unset reference to last element

    return $schema_data;
}, 10, 1 );

// ============================================================
// a) BLOCK USER ENUMERATION VIA REST API
// ============================================================

add_filter( 'rest_endpoints', function ( $endpoints ) {
    // Remove users list endpoint
    if ( isset( $endpoints['/wp/v2/users'] ) ) {
        unset( $endpoints['/wp/v2/users'] );
    }
    // Remove single user endpoint
    if ( isset( $endpoints['/wp/v2/users/(?P<id>[\d]+)'] ) ) {
        unset( $endpoints['/wp/v2/users/(?P<id>[\d]+)'] );
    }
    return $endpoints;
} );

// ============================================================
// b) BLOCK ?author= ENUMERATION
// ============================================================

add_action( 'template_redirect', function () {
    if ( isset( $_GET['author'] ) ) {
        wp_redirect( home_url(), 301 );
        exit;
    }
} );

// ============================================================
// b2) SLUG REDIRECTS (v4.6.1)
//     301 redirects for renamed/moved pages
// ============================================================

add_action( 'template_redirect', function () {
    $request_path = trim( parse_url( $_SERVER['REQUEST_URI'], PHP_URL_PATH ), '/' );
    $redirects = [
        'ai-partnership-calculator' => 'ai-tool-stack-calculator',
    ];
    if ( isset( $redirects[ $request_path ] ) ) {
        wp_redirect( home_url( '/' . $redirects[ $request_path ] . '/' ), 301 );
        exit;
    }
} );

// ============================================================
// b3) NUMERIC SLUG REWRITE (v4.7.7)
//     Maps /2/ to the homepage backup page (ID 1128)
//     WordPress reserves numeric slugs to avoid URL conflicts with post IDs,
//     so we use add_rewrite_rule to serve the page at the /2 path.
// ============================================================

add_action( 'init', function () {
    add_rewrite_rule( '^2/?$', 'index.php?page_id=1128', 'top' );
} );

add_action( 'after_switch_theme', 'flush_rewrite_rules' );

// Flush rewrite rules on plugin activation
register_activation_hook( __FILE__, function() {
    add_rewrite_rule( '^2/?$', 'index.php?page_id=1128', 'top' );
    flush_rewrite_rules();
} );

// ============================================================
// c) SECURITY HEADERS
// ============================================================

add_action( 'send_headers', function () {
    // Force HTTPS for 1 year, including subdomains
    header( 'Strict-Transport-Security: max-age=31536000; includeSubDomains; preload' );

    // Prevent MIME type sniffing
    header( 'X-Content-Type-Options: nosniff' );

    // Prevent clickjacking - allow same origin only
    header( 'X-Frame-Options: SAMEORIGIN' );

    // Control referrer information
    header( 'Referrer-Policy: strict-origin-when-cross-origin' );

    // Restrict browser API access (MED-003)
    header( 'Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(self)' );

    // Content Security Policy - ENFORCED as of v4.6.2
    // Was report-only from v1.3.0-v4.6.1. Now enforcing to resolve browser "unsecure" indicator.
    //
    // Changelog:
    //   v1.3.0 - Initial CSP (report-only)
    //   v1.4.0 - Added api.purebrain.ai (Cloudflare Tunnel), api.puremarketing.ai (chat AI),
    //            cdn.by.wonderpush.com + *.wonderpush.com (push notifications),
    //            www.sandbox.paypal.com (PayPal sandbox scripts)
    //   v4.6.2 - Promoted from report-only to enforced (all pages verified clean)
    //   v4.6.3 - Added cdn.jsdelivr.net to connect-src (Three.js dynamic import fix)
    $csp = "default-src 'self'; "
         // WordPress core, Elementor, theme JS, PayPal SDK, WonderPush, Brevo, CDN helpers
         . "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
         .     "https://www.paypal.com https://*.paypal.com https://www.sandbox.paypal.com "
         .     "https://cdn.jsdelivr.net "
         .     "https://js.brevo.com "
         .     "https://cdn.by.wonderpush.com "
         .     "https://pure-brain-dashboard-api.purebrain.workers.dev "
         .     "https://www.googletagmanager.com "
         .     "https://img1.wsimg.com "
         .     "blob:; "
         // Google Fonts stylesheets only (fonts loaded via font-src)
         . "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
         // Google Fonts actual font files
         . "font-src 'self' https://fonts.gstatic.com data:; "
         // Images: allow all HTTPS sources (WP uploads, Cloudinary, tracking pixels, etc.)
         . "img-src 'self' data: https: blob:; "
         // Fetch/XHR targets: chat APIs, PayPal, analytics, logging, push notifications
         // Note: cdn.jsdelivr.net added v4.6.3 — dynamic import() uses connect-src, not
         // script-src. Three.js postprocessing uses await import() which requires this.
         . "connect-src 'self' "
         .     "https://api.purebrain.ai "
         .     "https://api.puremarketing.ai "
         .     "https://pure-brain-dashboard-api.purebrain.workers.dev "
         .     "https://www.paypal.com https://*.paypal.com https://www.sandbox.paypal.com "
         .     "https://api.brevo.com "
         .     "https://purebrain.ai "
         .     "https://sageandweaver-network.netlify.app "
         .     "https://*.wonderpush.com "
         .     "https://cdn.jsdelivr.net "
         .     "https://89.167.19.20:8443 "
         // Cloudflare R2: HLS.js fetches .m3u8 manifest + .ts video segments via XHR/fetch
         // Without this, CSP blocks all HLS requests -> video never plays (readyState=0)
         .     "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev; "
         // Iframes: PayPal checkout, YouTube embeds
         . "frame-src 'self' https://www.paypal.com https://*.paypal.com https://www.sandbox.paypal.com https://www.youtube.com; "
         // Workers: PayPal SDK creates Web Workers from blob URLs
         . "worker-src 'self' blob:; "
         // Media: HLS.js MSE creates blob: URLs for video buffers; R2 serves the source media
         . "media-src 'self' blob: https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev; "
         // No plugins (Flash, Silverlight, etc.)
         . "object-src 'none'; "
         // Prevent base tag injection
         . "base-uri 'self';";
    header( 'Content-Security-Policy: ' . $csp );
} );

// ============================================================
// d) HIDE WORDPRESS + PLUGIN VERSION NUMBERS (MED-001)
// ============================================================

// Remove <meta name="generator"> tags
remove_action( 'wp_head', 'wp_generator' );

// Remove version from RSS feed
add_filter( 'the_generator', '__return_empty_string' );

// Remove ?ver= query strings from stylesheets and scripts
add_filter( 'style_loader_src', 'purebrain_remove_version_strings', 9999 );
add_filter( 'script_loader_src', 'purebrain_remove_version_strings', 9999 );

function purebrain_remove_version_strings( $src ) {
    if ( strpos( $src, 'ver=' ) ) {
        $src = remove_query_arg( 'ver', $src );
    }
    return $src;
}

// ============================================================
// e) SECURE COOKIE FLAGS (HIGH-003)
//    Forces Secure + HttpOnly on wp-postpass cookies
// ============================================================

add_action( 'init', function () {
    // Enforce secure cookies when HTTPS is available
    if ( is_ssl() ) {
        @ini_set( 'session.cookie_httponly', true );
        @ini_set( 'session.cookie_secure', true );
    }
}, 1 );

// Override the wp-postpass cookie to add Secure + HttpOnly flags
add_action( 'wp', function () {
    if ( isset( $_COOKIE ) ) {
        foreach ( $_COOKIE as $name => $value ) {
            if ( strpos( $name, 'wp-postpass_' ) === 0 ) {
                // Re-set with proper flags (24h expiry instead of 10 days)
                setcookie( $name, $value, [
                    'expires'  => time() + 86400, // 24 hours
                    'path'     => COOKIEPATH,
                    'secure'   => true,
                    'httponly'  => true,
                    'samesite' => 'Strict',
                ] );
            }
        }
    }
}, 1 );

// ============================================================
// f) SUPPRESS LOGIN ERROR MESSAGES (LOW-001)
//    Prevents username enumeration via wp-login.php error messages
// ============================================================

add_filter( 'login_errors', function () {
    return 'Invalid credentials. Please try again.';
} );

// ============================================================
// g) SITE-WIDE FOOTER: Privacy Policy + Terms of Service links
//    Injected into every page via wp_footer hook
//    Pages: /privacy-policy/ and /terms-of-service/
// ============================================================
// ============================================================
// SITE-WIDE DARK BACKGROUND ENFORCEMENT (v4.6.6)
//    LOCKED IN per Jared 2026-02-27: NO page on purebrain.ai
//    should EVER show an orange/light background.
//    Replaces the page-777-only fix from v4.6.5 with a GLOBAL rule.
//
//    The Artistics theme sets body { background-color: var(--e-global-color-black) }
//    which resolves to #000000. But nested HTML documents, Elementor widget
//    backgrounds, and theme JS can override this. This 3-layer nuclear fix
//    ensures dark background on ALL pages, ALL templates, ALL conditions.
//
//    Layer 1: wp_head priority 1 (fires BEFORE all plugin/theme CSS)
//    Layer 2: wp_head priority 999 (fires AFTER all plugin/theme CSS)
//    Layer 3: JS at DOMContentLoaded forces body.style.background inline
//
//    Exceptions: blog posts (body.single-post) already have their own
//    dark background (#0a0a0f) in Additional CSS with ::before GIF overlay.
// ============================================================

// LAYER 1: Fire at priority 1 — before ALL other CSS
add_action( 'wp_head', function () {
    ?>
<style id="pb-dark-bg-layer1">
/* SITE-WIDE DARK BG - Layer 1 (earliest possible, priority 1 in wp_head) */
/* LOCKED IN: Jared 2026-02-27 — no page should ever show orange background */
/* html is ALWAYS dark — deepest fallback, safe on all pages */
html {
    background: #080a12 !important;
    background-color: #080a12 !important;
}
/* body is dark by default — overridden below for video/3D pages */
body {
    background: #080a12 !important;
    background-color: #080a12 !important;
}
/* EXCEPTION: Pages with fixed-position video/3D backgrounds at z-index:-1
   need body to be transparent so the video shows through.
   html stays dark = no orange leaks anywhere. */
body.home,
body.page-id-11,
body.page-id-688,
body.page-id-689,
body.page-id-987 {
    background: transparent !important;
    background-color: transparent !important;
}
</style>
    <?php
}, 1 );

// LAYER 2: Fire at priority 999 — after ALL other CSS (Additional CSS, Elementor, everything)
add_action( 'wp_head', function () {
    ?>
<style id="pb-dark-bg-layer2">
/* SITE-WIDE DARK BG - Layer 2 (latest possible, priority 999 in wp_head) */
/* Multiple selectors for maximum specificity across ALL page types */
body,
body.elementor-default,
body.elementor-template-canvas,
body.wp-theme-artistics,
body.tt-magic-cursor,
html body,
body.page,
body.archive,
body.search,
body.error404 {
    background: #080a12 !important;
    background-color: #080a12 !important;
}
/* Blog posts keep their own dark bg (#0a0a0f) from Additional CSS — don't override */
/* body.single-post is handled by Additional CSS with GIF overlay pseudo-elements */
/* EXCEPTION: Video/3D background pages need transparent body (v4.6.7 hotfix) */
body.home,
body.page-id-11,
body.page-id-688,
body.page-id-689,
body.page-id-987 {
    background: transparent !important;
    background-color: transparent !important;
}
</style>
    <?php
}, 999 );


// PRICING BULLET ALIGNMENT FIX (v4.7.6)
// Root cause: .pricing-card__feature uses display:flex. The <span class="ai-name-dynamic">
// and the trailing text node are separate flex children, so "Nova" appears left-separated
// from the rest of the bullet text.
//
// v4.7.5 attempted CSS grid switch but CSS grid also blockifies direct children,
// so display:inline on .ai-name-dynamic inside a grid cell has no effect.
//
// v4.7.6 correct fix: JS DOM wrapping at DOMContentLoaded. For each .pricing-card__feature
// that contains an .ai-name-dynamic span, we wrap the span + its following text node
// into a single <span class="pb-bullet-text"> wrapper. This gives the grid one block
// element in column 2 containing both the named span and the trailing text as inline content.
add_action( 'wp_head', function () {
    ?>
<style id="pb-pricing-bullet-fix">
/* v4.7.6: Pricing card feature alignment fix — CSS + JS DOM wrapping */
/* Grid: SVG in col 1, text wrapper in col 2. */
.pricing-card__feature {
    display: grid !important;
    grid-template-columns: 24px 1fr !important;
    gap: 12px !important;
    align-items: start !important;
}
.pricing-card__feature svg {
    grid-column: 1 !important;
    grid-row: 1 !important;
    width: 20px !important;
    height: 20px !important;
    margin-top: 2px !important;
    flex-shrink: 0 !important;
}
/* The JS-injected wrapper fills column 2 */
.pricing-card__feature .pb-bullet-text {
    display: block !important;
    grid-column: 2 !important;
    grid-row: 1 !important;
}
/* The ai-name-dynamic span inside the wrapper must be inline */
.pricing-card__feature .pb-bullet-text .ai-name-dynamic {
    display: inline !important;
}
</style>
<script id="pb-pricing-bullet-fix-js">
/* v4.7.6: Wrap .ai-name-dynamic + text node into .pb-bullet-text in each pricing bullet */
(function() {
    function wrapPricingBullets() {
        var features = document.querySelectorAll('.pricing-card__feature');
        features.forEach(function(li) {
            var span = li.querySelector('.ai-name-dynamic');
            if (!span) return;
            /* Already wrapped — skip */
            if (span.parentElement.classList.contains('pb-bullet-text')) return;
            /* Collect the ai-name-dynamic span + all following text/inline nodes */
            var wrapper = document.createElement('span');
            wrapper.className = 'pb-bullet-text';
            /* Move all nodes after the SVG into the wrapper */
            var nodes = Array.from(li.childNodes);
            var afterSvg = false;
            nodes.forEach(function(node) {
                if (node.nodeName === 'svg' || (node.nodeName === 'SVG')) {
                    afterSvg = true;
                    return;
                }
                if (afterSvg) {
                    wrapper.appendChild(node);
                }
            });
            li.appendChild(wrapper);
        });
    }
    /* Run immediately if DOM ready, else wait */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', wrapPricingBullets);
    } else {
        wrapPricingBullets();
    }
    /* Also run after a short delay to catch dynamically-added pricing sections */
    setTimeout(wrapPricingBullets, 500);
    setTimeout(wrapPricingBullets, 1500);
})();
</script>
    <?php
}, 20 );

// LAYER 3: JS forces inline style at DOMContentLoaded (beats ALL CSS)
add_action( 'wp_head', function () {
    // Skip single posts — they have their own background system with GIF overlay
    if ( is_singular( 'post' ) ) {
        return;
    }
    // Skip pages with video/3D backgrounds — body must stay transparent (v4.6.7)
    if ( is_front_page() || is_page( array( 688, 689, 987 ) ) ) {
        return;
    }
    ?>
<script id="pb-dark-bg-js">
/* SITE-WIDE DARK BG - Layer 3 (JS enforcement for non-blog/non-video pages) */
(function() {
    function applyDarkBg() {
        var b = document.body;
        if (b) {
            b.style.setProperty('background', '#080a12', 'important');
            b.style.setProperty('background-color', '#080a12', 'important');
        }
    }
    applyDarkBg();
    document.addEventListener('DOMContentLoaded', applyDarkBg);
    window.addEventListener('load', function() {
        applyDarkBg();
        setTimeout(applyDarkBg, 500);
        setTimeout(applyDarkBg, 1500);
    });
})();
</script>
    <?php
}, 999 );



add_action( 'wp_head', function () {
    // Inject CSS for legal footer hover — replaces inline onmouseover/onmouseout handlers
    echo '<style id="purebrain-legal-footer-css">';
    echo '#purebrain-legal-footer .pb-legal-link { color:#999; text-decoration:none; margin:0 14px; transition:color 0.2s; }';
    echo '#purebrain-legal-footer .pb-legal-link:hover, #purebrain-legal-footer .pb-legal-link:focus { color:#2a93c1; }';
    echo '</style>';
} );

add_action( 'wp_footer', function () {
    // Don't inject on admin pages
    if ( is_admin() ) {
        return;
    }
    echo '<div id="purebrain-legal-footer" style="text-align:center; padding:20px 0 24px; background:#0a0a0a; border-top:1px solid rgba(255,255,255,0.08); font-size:13px; font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,sans-serif;">';
    echo '<a href="/privacy-policy/" class="pb-legal-link">Privacy Policy</a>';
    echo '<span style="color:#444;">|</span>';
    echo '<a href="/terms-of-service/" class="pb-legal-link">Terms of Service</a>';
    echo '<span style="color:#444; margin:0 14px;">&mdash;</span>';
    echo '<span style="color:#555;">&copy; ' . date( 'Y' ) . ' Pure Technology Inc.</span>';
    echo '</div>';
} );

// ============================================================
// g2) NOINDEX STAGING PAGES (MED-002)
//     Forces noindex on old/development pages via wp_head
// ============================================================

add_action( 'wp_head', function () {
    if ( is_page( array( 95, 338, 383, 532 ) ) ) {
        echo '<meta name="robots" content="noindex, nofollow" />' . "\n";
    }
}, 1 );

// Override Yoast robots output for staging pages
add_filter( 'wpseo_robots', function ( $robots ) {
    if ( is_page( array( 95, 338, 383, 532 ) ) ) {
        return 'noindex, nofollow';
    }
    return $robots;
} );

// ============================================================
// g3) REGISTER YOAST SEO META FIELDS IN REST API (MED-002)
//     Allows setting noindex via REST API for staging pages
// ============================================================

add_action( 'init', function () {
    $yoast_meta_fields = [
        '_yoast_wpseo_meta-robots-noindex',
        '_yoast_wpseo_meta-robots-nofollow',
        '_yoast_wpseo_meta-robots-adv',
        '_yoast_wpseo_title',
        '_yoast_wpseo_metadesc',
        '_yoast_wpseo_twitter-image',
        '_yoast_wpseo_twitter-image-id',
        '_yoast_wpseo_opengraph-title',
        '_yoast_wpseo_opengraph-description',
        '_yoast_wpseo_opengraph-image',
        '_yoast_wpseo_opengraph-image-id',
        '_yoast_wpseo_twitter-title',
        '_yoast_wpseo_twitter-description',
    ];

    foreach ( $yoast_meta_fields as $field ) {
        register_post_meta( 'page', $field, [
            'show_in_rest'  => true,
            'single'        => true,
            'type'          => 'string',
            'auth_callback' => function () {
                return current_user_can( 'edit_posts' );
            },
        ] );
    }
} );

// ============================================================
// h0) RATE LIMITER (v2.6.0)
//     Transient-based per-IP rate limiting for REST proxy endpoints.
//     Uses WordPress transients (no extra DB tables needed).
//
//     @param string $key           Endpoint identifier (used in transient key)
//     @param int    $max_requests  Max allowed requests within the window
//     @param int    $window_seconds Sliding window duration in seconds
//     @return bool  true = request allowed, false = rate limit exceeded
// ============================================================

function purebrain_get_client_ip() {
    // LOW-002 (v3.8.0): Only trust CF-Connecting-IP when the site operator has explicitly
    // declared it is behind Cloudflare. Without this constant, the header could be spoofed
    // by a direct-to-origin attacker, defeating the rate limiter.
    //
    // To enable Cloudflare IP trust, add this line to wp-config.php:
    //   define( 'PUREBRAIN_BEHIND_CLOUDFLARE', true );
    if ( defined( 'PUREBRAIN_BEHIND_CLOUDFLARE' ) && PUREBRAIN_BEHIND_CLOUDFLARE ) {
        if ( ! empty( $_SERVER['HTTP_CF_CONNECTING_IP'] ) ) {
            return sanitize_text_field( $_SERVER['HTTP_CF_CONNECTING_IP'] );
        }
    }
    // Default: use the direct TCP connection address (safe for all configurations)
    return isset( $_SERVER['REMOTE_ADDR'] ) ? $_SERVER['REMOTE_ADDR'] : 'unknown';
}

function purebrain_check_rate_limit( $key, $max_requests = 30, $window_seconds = 60 ) {
    $client_ip     = purebrain_get_client_ip();
    $transient_key = 'pb_rl_' . md5( $key . '_' . $client_ip );
    $count         = (int) get_transient( $transient_key );
    if ( $count >= $max_requests ) {
        return false;
    }
    set_transient( $transient_key, $count + 1, $window_seconds );
    return true;
}

// ============================================================
// h) SERVER-SIDE PROXY: A-C-Gee Conversation Logging Fallback
//    Holds ACGEE_API_KEY server-side - never exposed to client
//    Route: POST /wp-json/purebrain/v1/log-conversation-fallback
// ============================================================

add_action( 'rest_api_init', function () {

    register_rest_route( 'purebrain/v1', '/log-conversation-fallback', array(
        'methods'             => 'POST',
        'callback'            => 'purebrain_proxy_acgee_logging',
        'permission_callback' => '__return_true', // Public - no auth needed from browser
    ) );

    // ============================================================
    // e) SERVER-SIDE PROXY: Direct Log Server (avoids IP exposure)
    //    Route: POST /wp-json/purebrain/v1/log-conversation
    // ============================================================

    register_rest_route( 'purebrain/v1', '/log-conversation', array(
        'methods'             => 'POST',
        'callback'            => 'purebrain_proxy_log_server',
        'permission_callback' => '__return_true',
    ) );

    // ============================================================
    // f) SERVER-SIDE PROXY: Payment Verification
    //    Route: POST /wp-json/purebrain/v1/verify-payment
    // ============================================================

    register_rest_route( 'purebrain/v1', '/verify-payment', array(
        'methods'             => 'POST',
        'callback'            => 'purebrain_proxy_verify_payment',
        'permission_callback' => '__return_true',
    ) );

    // ============================================================
    // g) UPDATE PROTECTED POST META (e.g. Yoast SEO meta description)
    //    Requires authenticated user with edit_posts capability.
    //    Route: POST /wp-json/purebrain/v1/update-post-meta
    //    Body: { "post_id": 123, "meta_key": "_yoast_wpseo_metadesc", "meta_value": "..." }
    // ============================================================

    register_rest_route( 'purebrain/v1', '/update-post-meta', array(
        'methods'             => 'POST',
        'callback'            => 'purebrain_update_post_meta_handler',
        'permission_callback' => function() {
            return current_user_can( 'edit_posts' );
        },
        'args' => array(
            'post_id' => array(
                'required'          => true,
                'type'              => 'integer',
                'sanitize_callback' => 'absint',
            ),
            'meta_key' => array(
                'required'          => true,
                'type'              => 'string',
                'sanitize_callback' => 'sanitize_key',
            ),
            'meta_value' => array(
                'required'          => true,
                'type'              => 'string',
                'sanitize_callback' => 'sanitize_text_field',
            ),
        ),
    ) );

    // ============================================================
    // h) BREVO SUBSCRIBE PROXY (v3.5.0)
    //    Accepts email from lead capture forms, adds contact to
    //    Brevo list 3 (The Neural Feed) via server-side API call.
    //    BREVO_API_KEY read from wp-config.php constant.
    //    Rate limit: 5 requests per IP per minute.
    //    Route: POST /wp-json/pb-security/v1/subscribe
    //    Body:  { "email": "user@example.com" }
    // ============================================================

    register_rest_route( 'pb-security/v1', '/subscribe', array(
        'methods'             => 'POST',
        'callback'            => 'purebrain_brevo_subscribe',
        'permission_callback' => '__return_true', // Public - lead capture form
        'args' => array(
            'email' => array(
                'required'          => true,
                'type'              => 'string',
                'sanitize_callback' => 'sanitize_email',
                'validate_callback' => function( $value ) {
                    return is_email( $value );
                },
            ),
        ),
    ) );

    // ============================================================
    // h2) GUIDE UNLOCK PROXY (v4.1.0)
    //     Server-side Brevo proxy for the AI Partnership Guide content gate.
    //     Accepts email + optional first name, adds contact to Brevo list 3.
    //     BREVO_API_KEY read from wp-config.php constant (never exposed client-side).
    //     Rate limit: 5 requests per IP per minute.
    //     Route: POST /wp-json/purebrain/v1/guide-unlock
    //     Body:  { "email": "user@example.com", "first_name": "Jane" }
    // ============================================================

    register_rest_route( 'purebrain/v1', '/guide-unlock', array(
        'methods'             => 'POST',
        'callback'            => 'purebrain_guide_unlock',
        'permission_callback' => '__return_true', // Public - lead capture form
        'args' => array(
            'email' => array(
                'required'          => true,
                'type'              => 'string',
                'sanitize_callback' => 'sanitize_email',
                'validate_callback' => function( $value ) {
                    return is_email( $value );
                },
            ),
            'first_name' => array(
                'required'          => false,
                'type'              => 'string',
                'sanitize_callback' => 'sanitize_text_field',
            ),
        ),
    ) );

    // ============================================================
    // i) TRANSPARENCY DATA ENDPOINT (v3.6.0)
    //    Stores Aether's weekly transparency report as a wp_option.
    //    This data is auto-injected into every single blog post by
    //    the transparency section render hooks below.
    //    Route: POST /wp-json/purebrain/v1/transparency-data
    //    Auth:  Requires manage_options capability (admin only)
    //    Body:  {
    //             "week_of":        "February 17, 2026",
    //             "summary":        "2-3 sentence executive summary",
    //             "stats":          { "specialist_agents": N, "work_domains": N,
    //                                 "deliverables": "N+", "human_hours": "N-N" },
    //             "work_breakdown": [ { "domain": "...", "description": "...",
    //                                   "effort": "High", "value": "..." } ],
    //             "biggest_win":    "One sentence win",
    //             "cta_text":       "Optional CTA override"  (optional)
    //           }
    // ============================================================

    register_rest_route( 'purebrain/v1', '/transparency-data', array(
        'methods'             => 'POST',
        'callback'            => 'purebrain_update_transparency_data',
        'permission_callback' => function() {
            return current_user_can( 'manage_options' );
        },
        'args' => array(
            'week_of' => array(
                'required'          => true,
                'type'              => 'string',
                'sanitize_callback' => 'sanitize_text_field',
            ),
            'summary' => array(
                'required'          => true,
                'type'              => 'string',
                'sanitize_callback' => 'sanitize_textarea_field',
            ),
            'stats' => array(
                'required' => true,
                'type'     => 'object',
            ),
            'work_breakdown' => array(
                'required' => true,
                'type'     => 'array',
            ),
            'biggest_win' => array(
                'required'          => true,
                'type'              => 'string',
                'sanitize_callback' => 'sanitize_textarea_field',
            ),
            'cta_text' => array(
                'required' => false,
                'type'     => 'string',
                'sanitize_callback' => 'sanitize_text_field',
            ),
        ),
    ) );

} );


/**
 * Update protected post meta (e.g. _yoast_wpseo_metadesc).
 * Requires authenticated user with edit_posts capability.
 *
 * Allowed meta keys whitelist prevents arbitrary meta writes.
 *
 * @param WP_REST_Request $request
 * @return WP_REST_Response|WP_Error
 */
function purebrain_update_post_meta_handler( WP_REST_Request $request ) {
    // Whitelist of allowed meta keys (extend as needed)
    $allowed_keys = array(
        '_yoast_wpseo_metadesc',
        '_yoast_wpseo_title',
        '_yoast_wpseo_focuskw',
        '_yoast_wpseo_canonical',
        '_yoast_wpseo_twitter-image',
        '_yoast_wpseo_twitter-image-id',
        '_yoast_wpseo_twitter-title',
        '_yoast_wpseo_twitter-description',
        '_yoast_wpseo_opengraph-title',
        '_yoast_wpseo_opengraph-description',
        '_yoast_wpseo_opengraph-image',
        '_yoast_wpseo_opengraph-image-id',
    );

    $post_id    = (int) $request->get_param( 'post_id' );
    $meta_key   = sanitize_key( $request->get_param( 'meta_key' ) );
    $meta_value = sanitize_text_field( $request->get_param( 'meta_value' ) );

    // Validate post exists and user can edit it
    $post = get_post( $post_id );
    if ( ! $post ) {
        return new WP_Error(
            'post_not_found',
            'Post not found.',
            array( 'status' => 404 )
        );
    }

    if ( ! current_user_can( 'edit_post', $post_id ) ) {
        return new WP_Error(
            'forbidden',
            'You do not have permission to edit this post.',
            array( 'status' => 403 )
        );
    }

    // Enforce whitelist
    if ( ! in_array( $meta_key, $allowed_keys, true ) ) {
        return new WP_Error(
            'meta_key_not_allowed',
            sprintf( 'Meta key "%s" is not in the allowed list.', $meta_key ),
            array( 'status' => 400 )
        );
    }

    // Validate meta_value length (max 500 chars - accommodates image URLs)
    if ( strlen( $meta_value ) > 500 ) {
        return new WP_Error(
            'meta_value_too_long',
            'meta_value exceeds maximum length of 500 characters.',
            array( 'status' => 400 )
        );
    }

    // Write the meta
    $result = update_post_meta( $post_id, $meta_key, $meta_value );

    // update_post_meta returns false if value is unchanged (not an error)
    $current = get_post_meta( $post_id, $meta_key, true );

    return new WP_REST_Response( array(
        'success'    => true,
        'post_id'    => $post_id,
        'meta_key'   => $meta_key,
        'meta_value' => $current,
        'updated'    => ( $result !== false ),
    ), 200 );
}


/**
 * Brevo subscribe proxy for lead capture forms (v3.5.0).
 * Adds email to Brevo list 3 (The Neural Feed).
 * BREVO_API_KEY read from wp-config.php constant.
 * Rate limit: 5 requests per IP per minute (strict - form endpoint).
 *
 * @param WP_REST_Request $request
 * @return WP_REST_Response|WP_Error
 */
function purebrain_brevo_subscribe( WP_REST_Request $request ) {
    // Strict rate limit: 5 per minute per IP (form endpoint, not a bulk API)
    if ( ! purebrain_check_rate_limit( 'brevo_subscribe', 5, 60 ) ) {
        return new WP_Error( 'rate_limited', 'Too many requests. Please wait a moment.', array( 'status' => 429 ) );
    }

    $email = sanitize_email( $request->get_param( 'email' ) );

    if ( empty( $email ) || ! is_email( $email ) ) {
        return new WP_Error( 'invalid_email', 'Please enter a valid email address.', array( 'status' => 400 ) );
    }

    // Get Brevo API key from wp-config.php constant
    // Define BREVO_API_KEY in wp-config.php:
    //   define( 'BREVO_API_KEY', 'xkeysib-...' );
    $api_key = defined( 'BREVO_API_KEY' ) ? BREVO_API_KEY : '';

    // MED-003 (v3.8.0): Fail CLOSED — return 503 immediately when API key is absent.
    // Previous behavior returned a vague message; now uses the spec-mandated phrasing
    // so operators can distinguish a configuration error from an upstream failure.
    if ( empty( $api_key ) ) {
        error_log( '[PureBrain Security] BREVO_API_KEY not defined in wp-config.php — subscribe endpoint returning 503' );
        return new WP_Error(
            'configuration_error',
            'Service unavailable - API key not configured',
            array( 'status' => 503 )
        );
    }

    // Brevo API v3: create contact and add to list 3
    $brevo_url  = 'https://api.brevo.com/v3/contacts';
    $brevo_body = wp_json_encode( array(
        'email'         => $email,
        'listIds'       => array( 3 ),
        'updateEnabled' => true, // Update existing contact if email exists
    ) );

    $response = wp_remote_post( $brevo_url, array(
        'body'    => $brevo_body,
        'headers' => array(
            'Content-Type' => 'application/json',
            'api-key'      => $api_key,
            'Accept'       => 'application/json',
        ),
        'timeout'   => 15,
        'sslverify' => true,
    ) );

    if ( is_wp_error( $response ) ) {
        error_log( '[PureBrain Security] Brevo subscribe error: ' . $response->get_error_message() );
        return new WP_Error( 'upstream_failed', 'Subscription service unavailable. Please try again.', array( 'status' => 503 ) );
    }

    $http_code = wp_remote_retrieve_response_code( $response );
    $body      = wp_remote_retrieve_body( $response );
    $decoded   = json_decode( $body, true );

    // Brevo returns 201 (created) or 204 (updated existing) on success
    if ( $http_code === 201 || $http_code === 204 ) {
        return rest_ensure_response( array(
            'success' => true,
            'message' => 'subscribed',
        ) );
    }

    // 400 with "Contact already exist" is actually fine (updateEnabled should handle it,
    // but belt-and-suspenders check)
    if ( $http_code === 400 && ! empty( $decoded['message'] ) ) {
        $msg = strtolower( $decoded['message'] );
        if ( strpos( $msg, 'already exist' ) !== false || strpos( $msg, 'duplicate' ) !== false ) {
            return rest_ensure_response( array(
                'success' => true,
                'message' => 'already_subscribed',
            ) );
        }
    }

    error_log( '[PureBrain Security] Brevo API error: HTTP ' . $http_code . ' - ' . $body );
    return new WP_Error(
        'brevo_error',
        'Could not complete subscription. Please try again.',
        array( 'status' => 502 )
    );
}


/**
 * AI Partnership Guide unlock proxy (v4.1.0).
 * Adds email + optional first name to Brevo list 3 (The Neural Feed).
 * BREVO_API_KEY read from wp-config.php constant.
 * Rate limit: 5 requests per IP per minute.
 *
 * @param WP_REST_Request $request
 * @return WP_REST_Response|WP_Error
 */
function purebrain_guide_unlock( WP_REST_Request $request ) {
    // Rate limit: 5 per minute per IP
    if ( ! purebrain_check_rate_limit( 'guide_unlock', 5, 60 ) ) {
        return new WP_Error( 'rate_limited', 'Too many requests. Please wait a moment.', array( 'status' => 429 ) );
    }

    $email      = sanitize_email( $request->get_param( 'email' ) );
    $first_name = sanitize_text_field( (string) $request->get_param( 'first_name' ) );

    if ( empty( $email ) || ! is_email( $email ) ) {
        return new WP_Error( 'invalid_email', 'Please enter a valid email address.', array( 'status' => 400 ) );
    }

    // Get Brevo API key from wp-config.php constant
    $api_key = defined( 'BREVO_API_KEY' ) ? BREVO_API_KEY : '';

    if ( empty( $api_key ) ) {
        error_log( '[PureBrain Security] BREVO_API_KEY not defined — guide-unlock endpoint returning 503' );
        return new WP_Error(
            'configuration_error',
            'Service unavailable - API key not configured',
            array( 'status' => 503 )
        );
    }

    // Build Brevo contact payload
    $brevo_payload = array(
        'email'         => $email,
        'listIds'       => array( 3 ), // The Neural Feed
        'updateEnabled' => true,
    );

    // Include FIRSTNAME attribute if provided
    if ( ! empty( $first_name ) ) {
        $brevo_payload['attributes'] = array(
            'FIRSTNAME' => $first_name,
        );
    }

    $brevo_url  = 'https://api.brevo.com/v3/contacts';
    $brevo_body = wp_json_encode( $brevo_payload );

    $response = wp_remote_post( $brevo_url, array(
        'body'    => $brevo_body,
        'headers' => array(
            'Content-Type' => 'application/json',
            'api-key'      => $api_key,
            'Accept'       => 'application/json',
        ),
        'timeout'   => 15,
        'sslverify' => true,
    ) );

    if ( is_wp_error( $response ) ) {
        error_log( '[PureBrain Security] Guide unlock Brevo error: ' . $response->get_error_message() );
        return new WP_Error( 'upstream_failed', 'Subscription service unavailable. Please try again.', array( 'status' => 503 ) );
    }

    $http_code = wp_remote_retrieve_response_code( $response );
    $body      = wp_remote_retrieve_body( $response );
    $decoded   = json_decode( $body, true );

    // Brevo returns 201 (created) or 204 (updated) on success
    if ( $http_code === 201 || $http_code === 204 ) {
        return rest_ensure_response( array(
            'success' => true,
            'message' => 'unlocked',
        ) );
    }

    // Handle "already exists" gracefully
    if ( $http_code === 400 && ! empty( $decoded['message'] ) ) {
        $msg = strtolower( $decoded['message'] );
        if ( strpos( $msg, 'already exist' ) !== false || strpos( $msg, 'duplicate' ) !== false ) {
            return rest_ensure_response( array(
                'success' => true,
                'message' => 'already_subscribed',
            ) );
        }
    }

    error_log( '[PureBrain Security] Guide unlock Brevo API error: HTTP ' . $http_code . ' - ' . $body );
    return new WP_Error(
        'brevo_error',
        'Could not complete unlock. Please try again.',
        array( 'status' => 502 )
    );
}


/**
 * Update the Aether Transparency Section data (v3.6.0).
 * Stores the weekly report payload as a wp_option (JSON).
 * Requires manage_options capability (admin only).
 *
 * @param WP_REST_Request $request
 * @return WP_REST_Response|WP_Error
 */
function purebrain_update_transparency_data( WP_REST_Request $request ) {
    $week_of        = sanitize_text_field( $request->get_param( 'week_of' ) );
    $summary        = sanitize_textarea_field( $request->get_param( 'summary' ) );
    $stats_raw      = $request->get_param( 'stats' );
    $breakdown_raw  = $request->get_param( 'work_breakdown' );
    $biggest_win    = sanitize_textarea_field( $request->get_param( 'biggest_win' ) );
    $cta_text_raw   = $request->get_param( 'cta_text' );

    // Validate week_of is non-empty
    if ( empty( $week_of ) ) {
        return new WP_Error( 'missing_week_of', 'week_of is required and must not be empty.', array( 'status' => 400 ) );
    }

    // Validate stats is an array/object with expected keys
    if ( ! is_array( $stats_raw ) ) {
        return new WP_Error( 'invalid_stats', 'stats must be an object with specialist_agents, work_domains, deliverables, and human_hours.', array( 'status' => 400 ) );
    }

    $stats = array(
        'specialist_agents' => isset( $stats_raw['specialist_agents'] ) ? absint( $stats_raw['specialist_agents'] ) : 0,
        'work_domains'      => isset( $stats_raw['work_domains'] )      ? absint( $stats_raw['work_domains'] )      : 0,
        'deliverables'      => isset( $stats_raw['deliverables'] )      ? sanitize_text_field( $stats_raw['deliverables'] )  : '0',
        'human_hours'       => isset( $stats_raw['human_hours'] )       ? sanitize_text_field( $stats_raw['human_hours'] )   : '0',
    );

    // Validate work_breakdown is an array of rows
    if ( ! is_array( $breakdown_raw ) ) {
        return new WP_Error( 'invalid_work_breakdown', 'work_breakdown must be an array of objects.', array( 'status' => 400 ) );
    }

    $work_breakdown = array();
    foreach ( $breakdown_raw as $row ) {
        if ( ! is_array( $row ) ) {
            continue;
        }
        $work_breakdown[] = array(
            'domain'      => sanitize_text_field( isset( $row['domain'] )      ? $row['domain']      : '' ),
            'description' => sanitize_text_field( isset( $row['description'] ) ? $row['description'] : '' ),
            'effort'      => sanitize_text_field( isset( $row['effort'] )      ? $row['effort']      : '' ),
            'value'       => sanitize_text_field( isset( $row['value'] )       ? $row['value']       : '' ),
        );
    }

    // Optional CTA text override
    $cta_text = ( ! empty( $cta_text_raw ) )
        ? sanitize_text_field( $cta_text_raw )
        : '';

    // Build the canonical data structure
    $data = array(
        'week_of'        => $week_of,
        'summary'        => $summary,
        'stats'          => $stats,
        'work_breakdown' => $work_breakdown,
        'biggest_win'    => $biggest_win,
        'cta_text'       => $cta_text,
        'updated_at'     => gmdate( 'c' ), // ISO 8601 timestamp
    );

    // Persist to wp_options
    update_option( 'purebrain_transparency_data', wp_json_encode( $data ), false );

    return new WP_REST_Response( array(
        'success'    => true,
        'week_of'    => $week_of,
        'updated_at' => $data['updated_at'],
        'rows'       => count( $work_breakdown ),
    ), 200 );
}


/**
 * Proxy to A-C-Gee's capture endpoint.
 * API key is read from wp-config.php constant ACGEE_API_KEY.
 *
 * @param WP_REST_Request $request
 * @return WP_REST_Response|WP_Error
 */
function purebrain_proxy_acgee_logging( WP_REST_Request $request ) {
    // Rate limit: 30 requests per minute per IP
    if ( ! purebrain_check_rate_limit( 'acgee_logging', 30, 60 ) ) {
        return new WP_Error( 'rate_limited', 'Too many requests', array( 'status' => 429 ) );
    }
    // Body size cap: 64 KB
    if ( strlen( $request->get_body() ) > 65536 ) {
        return new WP_Error( 'payload_too_large', 'Request body too large', array( 'status' => 413 ) );
    }

    // Get API key from wp-config.php (never hardcoded here)
    $api_key = defined( 'ACGEE_API_KEY' ) ? ACGEE_API_KEY : '';

    if ( empty( $api_key ) ) {
        // Log silently - don't break the user experience, just skip logging
        error_log( '[PureBrain Security] ACGEE_API_KEY not defined in wp-config.php' );
        return rest_ensure_response( array( 'status' => 'skipped', 'reason' => 'no_api_key' ) );
    }

    $upstream_url = 'https://sageandweaver-network.netlify.app/api/capture-proxy';

    $response = wp_remote_post( $upstream_url, array(
        'body'    => $request->get_body(),
        'headers' => array(
            'Content-Type' => 'application/json',
            'X-API-Key'    => $api_key,
        ),
        'timeout' => 10,
    ) );

    if ( is_wp_error( $response ) ) {
        error_log( '[PureBrain Security] ACGEE proxy error: ' . $response->get_error_message() );
        return rest_ensure_response( array( 'status' => 'error', 'message' => 'upstream_failed' ) );
    }

    $body = wp_remote_retrieve_body( $response );
    $decoded = json_decode( $body, true );

    return rest_ensure_response( $decoded !== null ? $decoded : array( 'status' => 'ok' ) );
}


/**
 * Proxy to the internal log server via Cloudflare Tunnel (api.purebrain.ai).
 * Raw IP (89.167.19.20:8443) replaced in v2.6.0 — Cloudflare provides valid TLS.
 *
 * @param WP_REST_Request $request
 * @return WP_REST_Response|WP_Error
 */
function purebrain_proxy_log_server( WP_REST_Request $request ) {
    // Rate limit: 30 requests per minute per IP
    if ( ! purebrain_check_rate_limit( 'log_server', 30, 60 ) ) {
        return new WP_Error( 'rate_limited', 'Too many requests', array( 'status' => 429 ) );
    }
    // Body size cap: 64 KB
    if ( strlen( $request->get_body() ) > 65536 ) {
        return new WP_Error( 'payload_too_large', 'Request body too large', array( 'status' => 413 ) );
    }

    // Cloudflare Tunnel endpoint — valid TLS cert, no raw IP exposed to client
    $upstream_url = 'https://api.purebrain.ai/api/log-conversation';

    $response = wp_remote_post( $upstream_url, array(
        'body'      => $request->get_body(),
        'headers'   => array(
            'Content-Type' => 'application/json',
        ),
        'timeout'   => 10,
        'sslverify' => true, // Cloudflare Tunnel provides valid TLS certificate
    ) );

    if ( is_wp_error( $response ) ) {
        error_log( '[PureBrain Security] Log server proxy error: ' . $response->get_error_message() );
        return rest_ensure_response( array( 'status' => 'error', 'message' => 'upstream_failed' ) );
    }

    $body = wp_remote_retrieve_body( $response );
    $decoded = json_decode( $body, true );

    return rest_ensure_response( $decoded !== null ? $decoded : array( 'status' => 'ok' ) );
}


/**
 * Proxy for payment verification via Cloudflare Tunnel (api.purebrain.ai).
 * Raw IP (89.167.19.20:8443) replaced in v2.6.0 — Cloudflare provides valid TLS.
 *
 * @param WP_REST_Request $request
 * @return WP_REST_Response|WP_Error
 */
function purebrain_proxy_verify_payment( WP_REST_Request $request ) {
    // Rate limit: 10 requests per minute per IP (stricter — payment endpoint)
    if ( ! purebrain_check_rate_limit( 'verify_payment', 10, 60 ) ) {
        return new WP_Error( 'rate_limited', 'Too many requests', array( 'status' => 429 ) );
    }
    // Body size cap: 64 KB
    if ( strlen( $request->get_body() ) > 65536 ) {
        return new WP_Error( 'payload_too_large', 'Request body too large', array( 'status' => 413 ) );
    }

    // Cloudflare Tunnel endpoint — valid TLS cert, no raw IP exposed to client
    $upstream_url = 'https://api.purebrain.ai/api/verify-payment';

    $response = wp_remote_post( $upstream_url, array(
        'body'      => $request->get_body(),
        'headers'   => array(
            'Content-Type' => 'application/json',
        ),
        'timeout'   => 15, // Payment verification may take longer
        'sslverify' => true, // Cloudflare Tunnel provides valid TLS certificate
    ) );

    if ( is_wp_error( $response ) ) {
        error_log( '[PureBrain Security] Payment verification proxy error: ' . $response->get_error_message() );
        return new WP_Error(
            'upstream_failed',
            'Payment verification service unavailable',
            array( 'status' => 503 )
        );
    }

    $body = wp_remote_retrieve_body( $response );
    $decoded = json_decode( $body, true );

    return rest_ensure_response( $decoded !== null ? $decoded : array( 'status' => 'error' ) );
}

// ============================================================
// j) FAQ ACCORDION (Feb 20, 2026 - v2.0.0)
//    Converts .faq-section divs on single blog posts into an
//    accordion: all collapsed on load, click to expand,
//    one-at-a-time behavior, smooth CSS transition.
//    Targets: body.single-post .faq-section
//    Structure expected: <div class="faq-section">
//                          <h3>Question</h3>
//                          <p>Answer</p>
//                        </div>
//
//    v2.3.0 fix: Added pre-JS CSS to hide <p> directly (prevents flash of
//    expanded content before JS runs). Also added explicit body.single-post
//    scoping to JS selector for reliability.
// ============================================================

add_action( 'wp_head', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<style id="purebrain-faq-accordion">
/* ============================================================
   FAQ ACCORDION STYLES
   All .faq-section items start collapsed.
   Active item shows answer with smooth height animation.
   v2.3.0: Pre-JS hiding of <p> prevents flash of open content.
   ============================================================ */

/* FAQ heading above the items */
body.single-post .post-content h2 + .faq-section,
body.single-post .post-content .faq-section {
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 10px;
    margin-bottom: 10px !important;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.03);
    transition: background 0.2s ease;
}

body.single-post .post-content .faq-section:hover {
    background: rgba(255, 255, 255, 0.05);
}

/* PRE-JS: Hide the answer <p> immediately on page load so FAQs start collapsed.
   This prevents the flash of expanded content before DOMContentLoaded fires.
   The JS will wrap these in .faq-answer divs; once wrapped, the .faq-answer
   rules (below) take over for the smooth height animation. */
body.single-post .post-content .faq-section > p {
    overflow: hidden !important;
    max-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    transition: max-height 0.35s ease !important;
}

/* Question (h3) acts as the clickable trigger */
body.single-post .post-content .faq-section h3 {
    margin: 0 !important;
    padding: 16px 52px 16px 20px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    position: relative !important;
    user-select: none !important;
    color: #e8e8e8 !important;
    line-height: 1.5 !important;
    transition: color 0.2s ease !important;
    list-style: none !important;
}

body.single-post .post-content .faq-section h3:hover {
    color: #2a93c1 !important;
}

/* Chevron indicator */
body.single-post .post-content .faq-section h3::after {
    content: '' !important;
    position: absolute !important;
    right: 18px !important;
    top: 50% !important;
    transform: translateY(-50%) rotate(0deg) !important;
    width: 20px !important;
    height: 20px !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%232a93c1' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-size: contain !important;
    transition: transform 0.3s ease !important;
}

/* Chevron rotates when open */
body.single-post .post-content .faq-section.faq-open h3::after {
    transform: translateY(-50%) rotate(180deg) !important;
}

/* Answer (.faq-answer wrapper added by JS) - hidden by default */
body.single-post .post-content .faq-section .faq-answer {
    max-height: 0 !important;
    overflow: hidden !important;
    transition: max-height 0.35s ease, padding 0.25s ease !important;
    padding: 0 20px !important;
    color: #b0b8c4 !important;
    font-size: 15px !important;
    line-height: 1.7 !important;
}

/* .faq-answer > p: once wrapped by JS, restore normal paragraph display */
body.single-post .post-content .faq-section .faq-answer > p {
    max-height: none !important;
    overflow: visible !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Answer visible when open */
body.single-post .post-content .faq-section.faq-open .faq-answer {
    max-height: 800px !important;
    padding: 0 20px 18px 20px !important;
}

/* Active item: accent left border */
body.single-post .post-content .faq-section.faq-open {
    border-left: 3px solid #2a93c1 !important;
    background: rgba(42, 147, 193, 0.06) !important;
}
</style>
<script id="purebrain-faq-accordion-js">
(function() {
    'use strict';

    function initFaqAccordion() {
        // Target .faq-section inside body.single-post .post-content
        // querySelector('body.single-post') may not work from document level;
        // instead check body class directly and query from document.
        if (!document.body.classList.contains('single-post')) return;

        var items = document.querySelectorAll('.post-content .faq-section');
        if (!items.length) return;

        // Wrap each direct <p> child in a .faq-answer div for animation
        items.forEach(function(item) {
            // Collect all direct <p> children (may be multiple)
            var paragraphs = [];
            var children = item.childNodes;
            for (var i = 0; i < children.length; i++) {
                if (children[i].nodeName === 'P') {
                    paragraphs.push(children[i]);
                }
            }

            if (paragraphs.length > 0 && !item.querySelector('.faq-answer')) {
                var wrapper = document.createElement('div');
                wrapper.className = 'faq-answer';
                // Insert wrapper before the first paragraph
                item.insertBefore(wrapper, paragraphs[0]);
                // Move all paragraphs into the wrapper
                paragraphs.forEach(function(p) {
                    wrapper.appendChild(p);
                });
            }
        });

        // Attach click handlers to each h3
        items.forEach(function(item) {
            var trigger = item.querySelector('h3');
            if (!trigger) return;

            trigger.addEventListener('click', function() {
                var isOpen = item.classList.contains('faq-open');

                // Close all items (accordion: one open at a time)
                items.forEach(function(other) {
                    other.classList.remove('faq-open');
                });

                // If it wasn't open before, open it now
                if (!isOpen) {
                    item.classList.add('faq-open');
                }
            });
        });
    }

    // Run as soon as possible - either now or on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFaqAccordion);
    } else {
        initFaqAccordion();
    }
})();
</script>
    <?php
}, 15 );

// ============================================================
// i) BLOG POST IMAGE CONSTRAIN (Feb 20, 2026 - v5/1.9.0)
//    Constrains featured image + content on desktop AND tablet.
//    Scoped to body.single-post only. Does NOT touch mobile (<768px).
//
//    v5 change: Fixed bottom-clipping bug on desktop/tablet.
//    Root cause: Artistics theme forces aspect-ratio: 1/0.50 on BOTH
//    .post-single-image figure AND img - constraining container height to
//    50% of width, then object-fit: cover crops from center, cutting off
//    bottom text in banners (e.g. "THE DIFFERENCE" / CTA text).
//    Fix: Override aspect-ratio to auto on BOTH figure AND img so image
//    displays at its natural dimensions. object-fit changed to fill
//    (not cover) so nothing is cropped. Mobile (<768px) is completely
//    untouched - theme's mobile rules remain in effect there.
// ============================================================

add_action( 'wp_head', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<style id="purebrain-blog-desktop-padding">
/* ============================================================
   TABLET + DESKTOP: min-width 768px
   Applies to: tablet (768-1024px) and desktop (1025px+)
   Does NOT touch mobile (below 768px)
   ============================================================ */
@media (min-width: 768px) {
    /* Override Bootstrap row negative gutter */
    body.single-post .page-single-post .container > .row {
        margin-left: 0 !important;
        margin-right: 0 !important;
    }
    /* Override Bootstrap col gutter inside the row */
    body.single-post .page-single-post .container > .row > .col-md-12 {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    /* Featured image wrapper: constrain width, clear separation from background */
    body.single-post .post-single-image {
        max-width: 680px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        margin-bottom: 36px !important;
        margin-top: 8px !important;
        border-radius: 14px !important;
        overflow: visible !important;
        display: block !important;
        box-shadow: 0 6px 30px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.07) !important;
    }
    /* CRITICAL FIX v1.9.0: Theme sets aspect-ratio: 1/0.50 on figure which
       constrains container height and causes bottom-clipping via object-fit: cover.
       Override to auto so the figure grows to fit the image naturally. */
    body.single-post .post-single-image figure {
        margin: 0 !important;
        border-radius: 14px !important;
        overflow: hidden !important;
        aspect-ratio: auto !important;
        height: auto !important;
    }
    /* CRITICAL FIX v1.9.0: Override theme's aspect-ratio: 1/0.50 and object-fit: cover
       so image shows at its natural dimensions - no cropping of bottom content. */
    body.single-post .post-single-image img {
        border-radius: 14px !important;
        display: block !important;
        width: 100% !important;
        height: auto !important;
        aspect-ratio: auto !important;
        object-fit: fill !important;
    }
    /* Post content text: constrain to comfortable reading width */
    body.single-post .post-content {
        max-width: 680px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    /* Tablet: modest side padding so content doesn't go to absolute edge */
    body.single-post .page-single-post .container {
        padding-left: 30px !important;
        padding-right: 30px !important;
        box-sizing: border-box !important;
    }
    body.single-post .page-header .container {
        padding-left: 30px !important;
        padding-right: 30px !important;
        box-sizing: border-box !important;
    }
}

/* ============================================================
   DESKTOP ONLY: min-width 1025px
   Increases padding and max-width for larger screens
   ============================================================ */
@media (min-width: 1025px) {
    /* Add breathing room between page-header (title bar) and content */
    body.single-post .page-single-post {
        padding-top: 20px !important;
    }
    /* Container: cap at 1100px with generous horizontal breathing room */
    body.single-post .page-single-post .container {
        max-width: 1100px !important;
        padding-left: 60px !important;
        padding-right: 60px !important;
    }
    /* Featured image: larger max-width for desktop */
    body.single-post .post-single-image {
        max-width: 760px !important;
        margin-bottom: 48px !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.55), 0 0 0 1px rgba(255, 255, 255, 0.07) !important;
    }
    body.single-post .post-single-image figure {
        border-radius: 16px !important;
    }
    body.single-post .post-single-image img {
        border-radius: 16px !important;
    }
    /* Post content: wider max-width for desktop reading */
    body.single-post .post-content {
        max-width: 760px !important;
    }
    /* Page header title: cap width to match */
    body.single-post .page-header .container {
        max-width: 1100px !important;
        padding-left: 60px !important;
        padding-right: 60px !important;
    }
}

/* ============================================================
   WIDE SCREENS: min-width 1400px
   Extra horizontal breathing room for very wide displays
   ============================================================ */
@media (min-width: 1400px) {
    body.single-post .page-single-post .container {
        padding-left: 80px !important;
        padding-right: 80px !important;
    }
    body.single-post .page-header .container {
        padding-left: 80px !important;
        padding-right: 80px !important;
    }
}
</style>
    <?php
}, 20 );

// ============================================================
// j) BLOG CTA BUTTON STYLES (v2.1.0 → v2.9.0)
//    Controls the "Start Your AI Partnership" CTA button and the
//    newsletter link inside .blog-cta-block on blog posts.
//
//    v2.1.0: Initial hover effect (blue glow, lift).
//    v2.3.0: Preserve white text + orange bg on hover (overrides theme's
//            body.single-post a:hover { color: #f1420b }).
//    v2.4.0: Added `.blog-cta-block p a` blue base + white hover for
//            newsletter links. BUT this rule was overbroad — it also
//            matched the CTA button (which is also a p > a), stripping
//            its background: none !important broke the orange gradient.
//    v2.5.0 FIX: Split rules by href attribute selector:
//            - a[href*="awakening"] = CTA button → orange default, BLUE hover
//            - a[href*="subscribe|newsletter|neural-feed"] = newsletter link → blue text
//            This leaves each element with the correct appearance without
//            either rule stomping on the other.
//    v2.7.0: Newsletter link hover now shows orange gradient background
//            (mini button effect). Default state gets invisible vertical
//            padding (3px 0) so text doesn't jump on hover. Transition
//            includes background + padding for smooth animation.
//    v2.9.0: Added high-specificity override to beat Additional CSS blue-glow
//            rule (body.single-post .blog-cta-block a:hover). Root cause:
//            Additional CSS loads after plugin CSS in <head>, so at equal
//            specificity it wins even though both use !important. Fix uses:
//            (a) a[data-pb-subscribe] attribute selector added via JS to push
//                specificity above the conflicting Additional CSS rule; and
//            (b) explicit box-shadow: orange + transform: none on subscribe
//                hover to definitively cancel the blue glow + translateY.
// ============================================================

add_action( 'wp_head', function () {
    ?>
<style id="purebrain-blog-cta-hover">
/* ============================================================
   BLOG CTA BLOCK — v2.7.0
   Uses href-based attribute selectors to target CTA button vs
   newsletter link independently, preventing CSS collision.
   Newsletter link hover: orange gradient mini-button effect.
   ============================================================ */

/* ----------------------------------------------------------
   1. CTA BUTTON: links containing "awakening"
      Default: orange gradient | Hover: BLUE gradient + glow + lift
   ---------------------------------------------------------- */
body.single-post .blog-cta-block p a[href*="awakening"],
.blog-cta-block p a[href*="awakening"] {
    display: inline-block !important;
    padding: 14px 32px !important;
    background: linear-gradient(135deg, #f1420b 0%, #d13608 100%) !important;
    background-color: #f1420b !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    border-radius: 8px !important;
    text-decoration: none !important;
    letter-spacing: 0.5px !important;
    box-shadow: none !important;
    transition: background 0.25s ease, box-shadow 0.25s ease, transform 0.2s ease !important;
    position: relative !important;
}

body.single-post .blog-cta-block p a[href*="awakening"]:hover,
body.single-post .blog-cta-block p a[href*="awakening"]:focus,
.blog-cta-block p a[href*="awakening"]:hover,
.blog-cta-block p a[href*="awakening"]:focus {
    background: linear-gradient(135deg, #2a93c1 0%, #1e7da8 100%) !important;
    background-color: #2a93c1 !important;
    color: #ffffff !important;
    box-shadow:
        0 0 0 3px rgba(42, 147, 193, 0.5),
        0 0 18px rgba(42, 147, 193, 0.35),
        0 6px 20px rgba(0, 0, 0, 0.3) !important;
    transform: translateY(-2px) !important;
    text-decoration: none !important;
    outline: none !important;
}

/* ----------------------------------------------------------
   2. NEWSLETTER / SUBSCRIBE LINKS inside .blog-cta-block p
      Default: blue text with underline, invisible 3px vertical padding.
      Hover: white text + orange gradient mini-button effect.
      Invisible default padding prevents layout jump on hover.
      Targets href containing "subscribe", "newsletter", or "neural-feed".
   ---------------------------------------------------------- */
body.single-post .blog-cta-block p a[href*="subscribe"],
body.single-post .blog-cta-block p a[href*="newsletter"],
body.single-post .blog-cta-block p a[href*="neural-feed"],
.blog-cta-block p a[href*="subscribe"],
.blog-cta-block p a[href*="newsletter"],
.blog-cta-block p a[href*="neural-feed"] {
    color: #2a93c1 !important;
    text-decoration: underline !important;
    text-decoration-color: rgba(42, 147, 193, 0.4) !important;
    background: none !important;
    background-color: transparent !important;
    padding: 3px 0 !important;
    display: inline !important;
    border-radius: 5px !important;
    box-shadow: none !important;
    transform: none !important;
    font-weight: inherit !important;
    font-size: inherit !important;
    letter-spacing: inherit !important;
    transition: color 0.2s ease, text-decoration-color 0.2s ease, background 0.2s ease, padding 0.15s ease !important;
}

body.single-post .blog-cta-block p a[href*="subscribe"]:hover,
body.single-post .blog-cta-block p a[href*="subscribe"]:focus,
body.single-post .blog-cta-block p a[href*="newsletter"]:hover,
body.single-post .blog-cta-block p a[href*="newsletter"]:focus,
body.single-post .blog-cta-block p a[href*="neural-feed"]:hover,
body.single-post .blog-cta-block p a[href*="neural-feed"]:focus,
.blog-cta-block p a[href*="subscribe"]:hover,
.blog-cta-block p a[href*="newsletter"]:hover,
.blog-cta-block p a[href*="neural-feed"]:hover {
    color: #ffffff !important;
    text-decoration: none !important;
    background: linear-gradient(135deg, #f1420b 0%, #d13608 100%) !important;
    background-color: #f1420b !important;
    padding: 3px 10px !important;
    border-radius: 5px !important;
    box-shadow: 0 2px 8px rgba(241, 66, 11, 0.3) !important;
    transform: none !important;
}

/* ----------------------------------------------------------
   3. FALLBACK: Any other .blog-cta-block a NOT matched above
      (safety net for future link additions)
      Keeps white text + blue glow on hover.
   ---------------------------------------------------------- */
.blog-cta-block a,
body.single-post .blog-cta-block a {
    transition: box-shadow 0.25s ease, transform 0.2s ease, color 0.1s ease !important;
    position: relative !important;
}

/* ----------------------------------------------------------
   4. HIGH-SPECIFICITY OVERRIDE (v2.9.0)
      Problem: WordPress Additional CSS (wp-custom-css) loads AFTER
      this plugin's CSS in <head>. The Additional CSS block:
        body.single-post .blog-cta-block a:hover,
        body.single-post .blog-cta-block p a:hover { box-shadow: blue; transform: translateY(-2px); }
      matches subscribe links AND wins at equal specificity because
      it appears later in the document.
      Fix: JS below adds data-pb-subscribe="1" to subscribe links,
      giving these selectors an extra attribute qualifier that pushes
      specificity above the Additional CSS rule (5 qualifiers vs 4).
      Result: orange hover + no transform wins definitively.
   ---------------------------------------------------------- */
body.single-post .blog-cta-block p a[data-pb-subscribe]:hover,
body.single-post .blog-cta-block p a[data-pb-subscribe]:focus {
    box-shadow: 0 2px 8px rgba(241, 66, 11, 0.3) !important;
    transform: none !important;
    background: linear-gradient(135deg, #f1420b 0%, #d13608 100%) !important;
    background-color: #f1420b !important;
    color: #ffffff !important;
    text-decoration: none !important;
}
</style>
    <?php
} );

// ============================================================
// j2) BLOG TAG PILLS + CTA BUTTON WHITE TEXT (v3.9.0)
//     Fix 1: CTA button "Start Your AI Partnership" — enforce white text
//             with maximum-specificity override covering ALL href patterns
//             (not just #awakening). Belt-and-suspenders since the inline
//             style in blog-footer-template.html already sets white text,
//             but theme hover rules can override color back to orange-on-orange.
//     Fix 2: Post tag links (.post-tags .tag-links a[rel="tag"]) — pill style.
//             Default: blue (#2a93c1) background, white text.
//             Hover: orange (#f1420b) background, white text.
//             These are the tags displayed at the bottom of each blog post
//             before the social sharing row.
// ============================================================

add_action( 'wp_head', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<style id="purebrain-tag-pills-cta-fix">
/* ============================================================
   BLOG TAG PILLS + CTA BUTTON WHITE TEXT — v3.9.0
   Tag pills: blue bg + white text, hover orange bg + white text.
   CTA button: white text enforced at all specificity levels.
   ============================================================ */

/* ----------------------------------------------------------
   1. CTA BUTTON — white text enforced (backup/belt-and-suspenders)
      The inline style in blog-footer-template.html already sets
      color: #ffffff !important but this provides CSS-level fallback
      covering any future posts added without the inline style.
   ---------------------------------------------------------- */
body.single-post .blog-cta-block a,
body.single-post .blog-cta-block p a,
.blog-cta-block a[href*="awakening"],
body.single-post .blog-cta-block a[href*="awakening"] {
    color: #ffffff !important;
}

body.single-post .blog-cta-block a[href*="awakening"]:hover,
body.single-post .blog-cta-block p a[href*="awakening"]:hover,
.blog-cta-block a[href*="awakening"]:hover {
    color: #ffffff !important;
}

/* ----------------------------------------------------------
   2. POST TAG PILLS — blue background, white text, pill shape
      Selectors cover WordPress default tag output structure:
        .post-tags > .tag-links > a[rel="tag"]
      Also covers .tags-links a[rel="tag"] (some themes use this).
   ---------------------------------------------------------- */
body.single-post .post-tags .tag-links a,
body.single-post .post-tags .tag-links a[rel="tag"],
body.single-post .tags-links a[rel="tag"],
body.single-post a[rel="tag"] {
    display: inline-block !important;
    background-color: #2a93c1 !important;
    background: #2a93c1 !important;
    color: #ffffff !important;
    padding: 4px 12px !important;
    border-radius: 20px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-decoration: none !important;
    letter-spacing: 0.03em !important;
    margin: 2px 3px !important;
    transition: background-color 0.2s ease, color 0.2s ease !important;
    border: none !important;
    line-height: 1.5 !important;
}

body.single-post .post-tags .tag-links a:hover,
body.single-post .post-tags .tag-links a[rel="tag"]:hover,
body.single-post .tags-links a[rel="tag"]:hover,
body.single-post a[rel="tag"]:hover {
    background-color: #f1420b !important;
    background: #f1420b !important;
    color: #ffffff !important;
    text-decoration: none !important;
}

/* Ensure the "Tags:" label text is muted, not an odd color */
body.single-post .post-tags .tag-links,
body.single-post .tags-links {
    color: rgba(224, 230, 240, 0.5) !important;
    font-size: 13px !important;
}
</style>
    <?php
} );

// ============================================================
// j3) BLOG IN-TEXT LINK HOVER FIX (v3.9.1)
//     Problem: In-content links are orange (#f1420b) by default (from Additional CSS
//     rule `body.single-post a { color: #f1420b }`). When hovered, a broad Additional
//     CSS hover rule adds an orange background — creating invisible orange-on-orange text.
//     Fix: On hover, keep orange background (#f1420b) but swap text to WHITE (#ffffff).
//     Exclusions prevent overriding the CTA button and tag pills (styled by v3.9.0).
// ============================================================

add_action( 'wp_head', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<style id="purebrain-link-hover-fix">
/* ============================================================
   BLOG IN-TEXT LINK HOVER — v3.9.1
   On hover: orange background (#f1420b) + WHITE text (#ffffff).
   Transition: smooth 0.2s fade for bg + text.
   Exclusions: .blog-cta-button (CTA button) + [rel="tag"] (tag pills).
   Selectors cover both standard WP (.entry-content) and
   Elementor Pro (.elementor-widget-theme-post-content) output.
   ============================================================ */

/* Transition on default state (so the transition plays on both enter and leave) */
body.single-post .entry-content a:not(.blog-cta-button):not([rel="tag"]),
body.single-post .elementor-widget-theme-post-content a:not(.blog-cta-button):not([rel="tag"]) {
    transition: background-color 0.2s ease, color 0.2s ease !important;
}

/* Hover: orange background, WHITE text */
body.single-post .entry-content a:not(.blog-cta-button):not([rel="tag"]):hover,
body.single-post .elementor-widget-theme-post-content a:not(.blog-cta-button):not([rel="tag"]):hover {
    background-color: #f1420b !important;
    color: #ffffff !important;
    text-decoration: none !important;
    border-radius: 3px !important;
    padding: 1px 4px !important;
}

</style>
    <?php
} );

// ============================================================
// j4) TRANSPARENCY SECTION CTA BUTTON WHITE TEXT FIX (v3.9.2)
//     Problem: .aether-transparency__cta-btn text was invisible.
//              The broad Additional CSS rule `body.single-post a { color: #f1420b }`
//              wins the specificity tie against the transparency section's own CSS
//              block (both use !important, but Additional CSS loads AFTER plugin
//              wp_head hooks at priority 30 — last wins in a specificity tie).
//     Fix: Add a new wp_head hook at priority 99 (fires AFTER Additional CSS which
//          is output at priority ~100 via wp_enqueue_style or inline) with
//          maximum-specificity selectors that explicitly override color to white.
//     Selectors: body.single-post .aether-transparency .aether-transparency__cta-btn
//     Note: `purebrain-transparency-css` style block (priority 30) already has
//           `color: #ffffff !important` but Additional CSS at priority 8 (wp_head
//           default for enqueued styles) can override via load-order on tie.
//           Priority 99 ensures this block fires AFTER everything else.
// ============================================================

add_action( 'wp_head', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<style id="purebrain-transparency-cta-v392">
/* ============================================================
   TRANSPARENCY SECTION CTA BUTTON WHITE TEXT — v3.9.2
   Forces white text on the orange "Start Your AI Partnership"
   button inside the transparency section.
   Root cause: broad Additional CSS `body.single-post a { color: #f1420b }`
   was overriding color inside .aether-transparency__cta-btn.
   Fix: maximum-specificity selectors at wp_head priority 99 (loads last).
   ============================================================ */
body.single-post .aether-transparency .aether-transparency__cta-btn,
body.single-post .aether-transparency__cta .aether-transparency__cta-btn,
html body.single-post .aether-transparency__cta-btn {
    color: #ffffff !important;
    text-decoration: none !important;
}
body.single-post .aether-transparency .aether-transparency__cta-btn:hover,
body.single-post .aether-transparency__cta .aether-transparency__cta-btn:hover,
html body.single-post .aether-transparency__cta-btn:hover {
    color: #ffffff !important;
    text-decoration: none !important;
}
</style>
    <?php
}, 99 );

// ============================================================
// k) BLOG NAV MENU: Home | Subscribe | Free AI Assessment (v2.4.0 → v4.1.1)
//    Injects a "Home | Subscribe | Free AI Assessment" nav menu into
//    the top navbar on:
//      - ALL single blog posts (is_single())
//      - ALL category/archive/tag pages (is_category() || is_archive() || is_tag())
//
//    Replaces the old v2.2.0 "← All Posts" category-only link.
//
//    CSS is injected via wp_head (fires on is_single OR is_category/archive).
//    JS injection runs via wp_footer to ensure DOM is ready.
//    Links:
//      Home → https://purebrain.ai/
//      Subscribe → https://purebrain.ai/blog/#neural-feed-subscribe
//      Free AI Assessment → https://purebrain.ai/ai-adoption-review/
//
//    v3.7.0: "Blog" link changed to "Subscribe" linking to the subscribe section
//            at the bottom of the blog page (#neural-feed-subscribe). When reading
//            a post, linking back to the blog index is redundant — Subscribe drives
//            email signups instead.
//    v3.2.0: Universal fix — `html body .pb-blog-nav a:hover` with specificity
//            (0,0,2,1) beats ALL body-class rules. Works on any page type.
//            No per-page-type selectors needed. Future-proof.
//    v3.1.0 fix: Hover color changed from blue (#2a93c1) to orange (#f1420b).
//    Previously the plugin set blue hover, but on blog posts the Additional CSS
//    `body.single-post a:hover { color: #f1420b }` accidentally overrode it to
//    orange. Category pages lacked a matching broad rule so showed blue. Fix:
//    plugin now directly uses orange with body-class-scoped high-specificity
//    selectors so hover is consistently orange on all page types.
// ============================================================

add_action( 'wp_head', function () {
    if ( ! ( is_single() || is_category() || is_archive() || is_tag() ) ) {
        return;
    }
    ?>
<style id="purebrain-blog-nav-menu">
/* ============================================================
   BLOG NAV MENU: Home | Subscribe | Free AI Assessment
   Appears in the right side of the top navbar on:
     - Single blog posts (body.single-post)
     - Category/archive/tag pages (body.category, body.archive, body.tag)
     - ANY future page type (universal selector — no maintenance needed)
   v2.4.0: Replaces "← All Posts" with full nav menu.
   v3.1.0: Hover color changed to orange (#f1420b) on ALL page types.
   v3.2.0: Universal fix — `html body .pb-blog-nav a:hover` with specificity
           (0,0,2,1) beats ALL body-class rules. Works on any page type.
           No per-page-type selectors needed. Future-proof.
   v3.7.0: "Blog" changed to "Subscribe" — links to #neural-feed-subscribe.
   ============================================================ */

.pb-blog-nav {
    display: flex;
    align-items: center;
    margin-left: auto;
    gap: 0;
    flex-shrink: 0;
}

.pb-blog-nav a {
    color: rgba(224, 230, 240, 0.7) !important;
    text-decoration: none !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    line-height: 1 !important;
    padding: 4px 10px !important;
    transition: color 0.2s ease !important;
    white-space: nowrap !important;
    background: none !important;
    box-shadow: none !important;
    transform: none !important;
}

/* v3.2.0: UNIVERSAL orange hover — works on ALL page types past, present, future.
   `html body .pb-blog-nav a:hover` has specificity (0,0,2,1) which beats any single
   body-class rule like `body.category a:hover` (0,1,0,1) OR `.pb-blog-nav a:hover` (0,0,1,1).
   No per-page-type maintenance needed. Add any new WordPress page type — it just works. */
html body .pb-blog-nav a:hover,
html body .pb-blog-nav a:focus {
    color: #f1420b !important;
    text-decoration: none !important;
    background: none !important;
    box-shadow: none !important;
    transform: none !important;
}

.pb-blog-nav .pb-nav-sep {
    color: rgba(224, 230, 240, 0.3);
    font-size: 12px;
    line-height: 1;
    user-select: none;
    pointer-events: none;
}

/* Responsive: shrink font on smaller viewports, hide on very small mobile */
@media (max-width: 480px) {
    .pb-blog-nav {
        display: none !important;
    }
}

@media (min-width: 481px) and (max-width: 767px) {
    .pb-blog-nav a {
        font-size: 11px !important;
        padding: 4px 6px !important;
    }
}
</style>
    <?php
}, 10 );

// ============================================================
// l) STRIP INLINE STYLES + TAG NEWSLETTER LINKS (v2.8.0 → v2.9.0)
//    v2.8.0: Strip inline style="" from subscribe links so plugin hover
//            CSS takes full control (inline !important beats stylesheet).
//    v2.9.0: Also sets data-pb-subscribe="1" on each subscribe link.
//            This attribute is used by the high-specificity CSS override
//            (section 4 of purebrain-blog-cta-hover) to beat the broad
//            Additional CSS hover rule that also matches subscribe links
//            and applies blue box-shadow + translateY(-2px).
//    Only runs on single posts (is_single). Targets .blog-cta-block.
// ============================================================

add_action( 'wp_footer', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<script id="purebrain-strip-newsletter-inline-styles">
(function() {
    'use strict';
    function initSubscribeLinks() {
        var ctaBlock = document.querySelector('.blog-cta-block');
        if (!ctaBlock) return;
        var newsletterLinks = ctaBlock.querySelectorAll(
            'a[href*="subscribe"], a[href*="newsletter"], a[href*="neural-feed"]'
        );
        newsletterLinks.forEach(function(link) {
            // v2.8.0: strip inline styles that override CSS hover rules
            link.removeAttribute('style');
            // v2.9.0: add data attribute for high-specificity CSS override
            // This beats the broad Additional CSS rule that gives subscribe
            // links an unwanted blue glow + translateY on hover.
            link.setAttribute('data-pb-subscribe', '1');
        });
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSubscribeLinks);
    } else {
        initSubscribeLinks();
    }
})();
</script>
    <?php
}, 20 );

// ============================================================
// FOOTER LOGO BRAND FIX (v3.0.0)
//    Replaces plain "Pure Brain" text in div.footer-logo h4 with
//    color-coded PUREBRAIN.AI on ALL pages site-wide.
//    Brand colors: PUREBR=#2a93c1 (blue), AI=#f1420b (orange),
//                  N=#2a93c1 (blue), .AI=#ffffff (white).
//    Runs on every page (no conditional). Priority 30 to run after
//    other footer hooks.
// ============================================================

add_action( 'wp_footer', function () {
    ?>
<script id="purebrain-footer-logo-brand">
(function() {
    'use strict';
    function brandFooterLogo() {
        var logoEl = document.querySelector('.footer-logo h4, #site-footer .footer-logo h4, footer .footer-logo h4');
        if (!logoEl) return;
        // Already branded - don't run twice
        if (logoEl.querySelector('.pb-logo-brand')) return;
        // Replace text content with color-coded brand name
        logoEl.innerHTML =
            '<span class="pb-logo-brand" style="font-size:inherit;font-weight:inherit;letter-spacing:inherit;">' +
            '<span style="color:#2a93c1;">PUREBR</span>' +
            '<span style="color:#f1420b;">AI</span>' +
            '<span style="color:#2a93c1;">N</span>' +
            '<span style="color:#ffffff;">.AI</span>' +
            '</span>';
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', brandFooterLogo);
    } else {
        brandFooterLogo();
    }
})();
</script>
    <?php
}, 30 );

// ============================================================
// LEAD CAPTURE STYLES (v3.5.0)
//    Injects CSS for both lead capture elements on single posts.
//    1. In-content subscribe box (#pb-lead-inline)
//    2. Post-read floating CTA bar (#pb-lead-bar)
//    Only on body.single-post pages.
// ============================================================

add_action( 'wp_head', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<style id="purebrain-lead-capture-css">
/* ============================================================
   LEAD CAPTURE STYLES v3.5.0
   Two capture points: inline box (50% scroll) + CTA bar (85% scroll)
   Both only on body.single-post.
   ============================================================ */

/* ----------------------------------------------------------
   1. IN-CONTENT SUBSCRIBE BOX
   Appears inline within post content after 50% scroll.
   Slides in from slightly below, fades in.
   ---------------------------------------------------------- */
#pb-lead-inline {
    display: none;
    position: relative;
    margin: 36px auto 36px auto !important;
    max-width: 600px !important;
    background: #0d1117 !important;
    border: 1px solid #2a93c1 !important;
    border-radius: 12px !important;
    padding: 28px 32px 24px 32px !important;
    box-shadow: 0 4px 24px rgba(42, 147, 193, 0.15), 0 1px 4px rgba(0,0,0,0.5) !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    animation: pb-slide-in 0.45s ease forwards;
    box-sizing: border-box !important;
}

#pb-lead-inline.pb-visible {
    display: block !important;
}

@keyframes pb-slide-in {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

#pb-lead-inline .pb-lead-close {
    position: absolute !important;
    top: 12px !important;
    right: 14px !important;
    background: none !important;
    border: none !important;
    color: rgba(255,255,255,0.35) !important;
    font-size: 20px !important;
    line-height: 1 !important;
    cursor: pointer !important;
    padding: 4px 6px !important;
    transition: color 0.2s ease !important;
    border-radius: 4px !important;
}

#pb-lead-inline .pb-lead-close:hover {
    color: rgba(255,255,255,0.75) !important;
    background: rgba(255,255,255,0.07) !important;
}

#pb-lead-inline .pb-lead-eyebrow {
    display: block !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #2a93c1 !important;
    margin-bottom: 8px !important;
}

#pb-lead-inline .pb-lead-headline {
    font-size: 17px !important;
    font-weight: 600 !important;
    color: #e8edf2 !important;
    margin: 0 0 16px 0 !important;
    line-height: 1.45 !important;
}

#pb-lead-inline .pb-lead-form {
    display: flex !important;
    gap: 10px !important;
    align-items: stretch !important;
    flex-wrap: wrap !important;
}

#pb-lead-inline .pb-lead-email {
    flex: 1 1 200px !important;
    min-width: 0 !important;
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 7px !important;
    color: #e8edf2 !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    outline: none !important;
    transition: border-color 0.2s ease !important;
    box-sizing: border-box !important;
}

#pb-lead-inline .pb-lead-email:focus {
    border-color: #2a93c1 !important;
    background: rgba(42,147,193,0.06) !important;
}

#pb-lead-inline .pb-lead-email::placeholder {
    color: rgba(255,255,255,0.3) !important;
}

#pb-lead-inline .pb-lead-submit {
    flex: 0 0 auto !important;
    background: linear-gradient(135deg, #2a93c1 0%, #1e7da8 100%) !important;
    background-color: #2a93c1 !important;
    border: none !important;
    border-radius: 7px !important;
    color: #ffffff !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    cursor: pointer !important;
    transition: background 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease !important;
    white-space: nowrap !important;
}

#pb-lead-inline .pb-lead-submit:hover {
    background: linear-gradient(135deg, #1e7da8 0%, #1669908f 100%) !important;
    background-color: #1e7da8 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(42,147,193,0.35) !important;
}

#pb-lead-inline .pb-lead-submit:disabled {
    opacity: 0.6 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

#pb-lead-inline .pb-lead-success {
    display: none !important;
    color: #6fcf97 !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    padding: 6px 0 !important;
}

#pb-lead-inline .pb-lead-error {
    display: none !important;
    color: #f1420b !important;
    font-size: 13px !important;
    margin-top: 8px !important;
}

/* ----------------------------------------------------------
   2. POST-READ CTA BAR
   Fixed bottom bar, appears after 85% scroll depth.
   Slides up from bottom.
   ---------------------------------------------------------- */
#pb-lead-bar {
    display: none;
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 99990 !important;
    background: #0d1117 !important;
    border-top: 2px solid #2a93c1 !important;
    padding: 16px 24px !important;
    box-shadow: 0 -4px 24px rgba(0,0,0,0.5) !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    animation: pb-bar-slide 0.4s ease forwards;
    box-sizing: border-box !important;
}

#pb-lead-bar.pb-visible {
    display: block !important;
}

@keyframes pb-bar-slide {
    from {
        transform: translateY(100%);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

#pb-lead-bar .pb-bar-inner {
    max-width: 900px !important;
    margin: 0 auto !important;
    display: flex !important;
    align-items: center !important;
    gap: 20px !important;
    flex-wrap: wrap !important;
}

#pb-lead-bar .pb-bar-text {
    flex: 1 1 200px !important;
    min-width: 0 !important;
}

#pb-lead-bar .pb-bar-headline {
    font-size: 15px !important;
    font-weight: 700 !important;
    color: #e8edf2 !important;
    margin: 0 0 3px 0 !important;
    line-height: 1.3 !important;
}

#pb-lead-bar .pb-bar-subline {
    font-size: 13px !important;
    color: rgba(232,237,242,0.65) !important;
    margin: 0 !important;
    line-height: 1.4 !important;
}

#pb-lead-bar .pb-bar-form {
    display: flex !important;
    gap: 8px !important;
    align-items: center !important;
    flex-shrink: 0 !important;
    flex-wrap: wrap !important;
}

#pb-lead-bar .pb-bar-email {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 7px !important;
    color: #e8edf2 !important;
    font-size: 14px !important;
    padding: 9px 14px !important;
    outline: none !important;
    width: 220px !important;
    transition: border-color 0.2s ease !important;
    box-sizing: border-box !important;
}

#pb-lead-bar .pb-bar-email:focus {
    border-color: #2a93c1 !important;
    background: rgba(42,147,193,0.08) !important;
}

#pb-lead-bar .pb-bar-email::placeholder {
    color: rgba(255,255,255,0.3) !important;
}

#pb-lead-bar .pb-bar-submit {
    background: linear-gradient(135deg, #f1420b 0%, #d13608 100%) !important;
    background-color: #f1420b !important;
    border: none !important;
    border-radius: 7px !important;
    color: #ffffff !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    padding: 9px 20px !important;
    cursor: pointer !important;
    transition: background 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease !important;
    white-space: nowrap !important;
    flex-shrink: 0 !important;
}

#pb-lead-bar .pb-bar-submit:hover {
    background: linear-gradient(135deg, #d13608 0%, #b82d06 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(241,66,11,0.35) !important;
}

#pb-lead-bar .pb-bar-submit:disabled {
    opacity: 0.6 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

#pb-lead-bar .pb-bar-close {
    position: absolute !important;
    top: 10px !important;
    right: 14px !important;
    background: none !important;
    border: none !important;
    color: rgba(255,255,255,0.3) !important;
    font-size: 18px !important;
    cursor: pointer !important;
    padding: 4px 6px !important;
    transition: color 0.2s ease !important;
    border-radius: 4px !important;
    line-height: 1 !important;
}

#pb-lead-bar .pb-bar-close:hover {
    color: rgba(255,255,255,0.7) !important;
    background: rgba(255,255,255,0.06) !important;
}

#pb-lead-bar .pb-bar-success {
    display: none !important;
    color: #6fcf97 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    flex: 1 1 auto !important;
    text-align: center !important;
    padding: 4px 0 !important;
}

#pb-lead-bar .pb-bar-error {
    display: none !important;
    color: #f1420b !important;
    font-size: 12px !important;
    margin-top: 4px !important;
    width: 100% !important;
}

/* Mobile: stack bar vertically */
@media (max-width: 600px) {
    #pb-lead-bar {
        padding: 14px 16px !important;
    }

    #pb-lead-bar .pb-bar-inner {
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 12px !important;
    }

    #pb-lead-bar .pb-bar-email {
        width: 100% !important;
    }

    #pb-lead-bar .pb-bar-form {
        width: 100% !important;
    }

    #pb-lead-bar .pb-bar-submit {
        width: 100% !important;
        text-align: center !important;
    }

    #pb-lead-inline {
        padding: 20px 18px 18px 18px !important;
    }
}
</style>
    <?php
}, 25 );

// ============================================================
// LEAD CAPTURE MARKUP + JAVASCRIPT (v3.5.0)
//    Injects both lead capture elements and scroll-triggered
//    JavaScript on single blog posts only.
//    wp_footer priority 25 — after other footer hooks but before
//    the nav menu JS (priority default 10).
// ============================================================

add_action( 'wp_footer', function () {
    if ( ! is_single() ) {
        return;
    }
    $subscribe_url = esc_url( rest_url( 'pb-security/v1/subscribe' ) );
    ?>
<!-- Lead Capture: In-Content Subscribe Box -->
<div id="pb-lead-inline" role="complementary" aria-label="Subscribe to The Neural Feed" aria-live="polite">
    <button class="pb-lead-close" type="button" aria-label="Dismiss subscription offer">&times;</button>
    <span class="pb-lead-eyebrow">The Neural Feed</span>
    <p class="pb-lead-headline">Enjoying this? Aether writes more like this every day in The Neural Feed.</p>
    <div class="pb-lead-form">
        <input class="pb-lead-email" type="email" placeholder="your@email.com" autocomplete="email" aria-label="Email address" />
        <button class="pb-lead-submit" type="button">Subscribe</button>
    </div>
    <p class="pb-lead-success">Welcome to The Neural Feed. Check your inbox &#x2014; Aether is waiting.</p>
    <p class="pb-lead-error"></p>
</div>

<!-- Lead Capture: Post-Read CTA Bar -->
<div id="pb-lead-bar" role="complementary" aria-label="Subscribe to The Neural Feed" aria-live="polite">
    <button class="pb-bar-close" type="button" aria-label="Dismiss">&times;</button>
    <div class="pb-bar-inner">
        <div class="pb-bar-text">
            <p class="pb-bar-headline">You made it to the end. That means you take AI seriously. So does Aether.</p>
            <p class="pb-bar-subline">Get The Neural Feed &#x2014; AI partnership insights from inside the partnership. Free.</p>
        </div>
        <div class="pb-bar-form">
            <input class="pb-bar-email" type="email" placeholder="your@email.com" autocomplete="email" aria-label="Email address" />
            <button class="pb-bar-submit" type="button">Get The Neural Feed</button>
            <p class="pb-bar-error"></p>
        </div>
        <p class="pb-bar-success">Welcome to The Neural Feed. Check your inbox &#x2014; Aether is waiting.</p>
    </div>
</div>

<script id="purebrain-lead-capture-js">
(function() {
    'use strict';

    var SUBSCRIBE_URL = '<?php echo $subscribe_url; ?>';

    // ── localStorage keys ──────────────────────────────────────
    var LS_SUBSCRIBED       = 'pb_subscribed';        // Set when user subscribes
    var LS_INLINE_DISMISSED = 'pb_inline_dismissed';  // Timestamp of inline dismiss
    var LS_BAR_DISMISSED    = 'pb_bar_dismissed';     // Timestamp of bar dismiss
    var INLINE_DISMISS_TTL  = 7  * 24 * 60 * 60 * 1000; // 7 days in ms
    var BAR_DISMISS_TTL     = 14 * 24 * 60 * 60 * 1000; // 14 days in ms

    // ── State ──────────────────────────────────────────────────
    var inlineShown    = false;
    var barShown       = false;
    var inlineConverted = false; // Track whether user subscribed via inline form

    // ── Helper: check dismissal TTL ───────────────────────────
    function isDismissed(key, ttl) {
        try {
            var ts = localStorage.getItem(key);
            if (!ts) return false;
            return (Date.now() - parseInt(ts, 10)) < ttl;
        } catch(e) {
            return false;
        }
    }

    // ── Helper: read localStorage flag ────────────────────────
    function getFlag(key) {
        try { return localStorage.getItem(key); } catch(e) { return null; }
    }

    // ── Helper: set localStorage flag ────────────────────────
    function setFlag(key, value) {
        try { localStorage.setItem(key, value); } catch(e) {}
    }

    // ── Helper: calculate scroll depth % ──────────────────────
    function scrollDepth() {
        var scrollTop  = window.scrollY || document.documentElement.scrollTop || 0;
        var docHeight  = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        if (docHeight <= 0) return 100;
        return Math.min(100, Math.round((scrollTop / docHeight) * 100));
    }

    // ── Helper: inject inline box before CTA block ────────────
    // Finds the .blog-cta-block and inserts the inline box before it.
    // Falls back to appending after .post-content if no CTA block found.
    function injectInlineBox() {
        var box = document.getElementById('pb-lead-inline');
        if (!box) return;

        var ctaBlock = document.querySelector('.blog-cta-block');
        var postContent = document.querySelector('.post-content');

        if (ctaBlock && ctaBlock.parentNode) {
            ctaBlock.parentNode.insertBefore(box, ctaBlock);
        } else if (postContent) {
            postContent.appendChild(box);
        } else {
            // Last resort: put it before the legal footer
            var footer = document.getElementById('purebrain-legal-footer');
            if (footer && footer.parentNode) {
                footer.parentNode.insertBefore(box, footer);
            }
        }
    }

    // ── Show / hide inline box ─────────────────────────────────
    function showInline() {
        if (inlineShown) return;
        inlineShown = true;
        var box = document.getElementById('pb-lead-inline');
        if (box) {
            box.classList.add('pb-visible');
            box.querySelector('.pb-lead-email') && box.querySelector('.pb-lead-email').focus();
        }
    }

    function hideInline() {
        var box = document.getElementById('pb-lead-inline');
        if (box) {
            box.classList.remove('pb-visible');
            box.style.display = 'none';
        }
    }

    // ── Show / hide bar ────────────────────────────────────────
    function showBar() {
        if (barShown) return;
        // Don't show bar if user already subscribed via inline form
        if (inlineConverted) return;
        barShown = true;
        var bar = document.getElementById('pb-lead-bar');
        if (bar) {
            bar.classList.add('pb-visible');
        }
    }

    function hideBar() {
        var bar = document.getElementById('pb-lead-bar');
        if (bar) {
            bar.classList.remove('pb-visible');
            bar.style.display = 'none';
        }
    }

    // ── API: Subscribe ─────────────────────────────────────────
    function doSubscribe(email, onSuccess, onError) {
        var body = JSON.stringify({ email: email });
        var xhr  = new XMLHttpRequest();
        xhr.open('POST', SUBSCRIBE_URL, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.timeout = 15000;
        xhr.onreadystatechange = function() {
            if (xhr.readyState !== 4) return;
            if (xhr.status === 200 || xhr.status === 201) {
                try {
                    var resp = JSON.parse(xhr.responseText);
                    if (resp && resp.success) {
                        onSuccess();
                        return;
                    }
                } catch(e) {}
                onSuccess(); // Treat any 200/201 as success
            } else if (xhr.status === 429) {
                onError('Too many attempts. Please wait a moment.');
            } else {
                onError('Something went wrong. Please try again.');
            }
        };
        xhr.ontimeout = function() {
            onError('Request timed out. Please try again.');
        };
        xhr.onerror = function() {
            onError('Network error. Please try again.');
        };
        xhr.send(body);
    }

    // ── Wire up inline form ────────────────────────────────────
    function initInlineForm() {
        var box        = document.getElementById('pb-lead-inline');
        if (!box) return;

        var closeBtn   = box.querySelector('.pb-lead-close');
        var emailInput = box.querySelector('.pb-lead-email');
        var submitBtn  = box.querySelector('.pb-lead-submit');
        var successMsg = box.querySelector('.pb-lead-success');
        var errorMsg   = box.querySelector('.pb-lead-error');

        closeBtn && closeBtn.addEventListener('click', function() {
            setFlag(LS_INLINE_DISMISSED, String(Date.now()));
            hideInline();
        });

        function handleInlineSubmit() {
            var email = emailInput ? emailInput.value.trim() : '';
            if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                if (errorMsg) {
                    errorMsg.textContent = 'Please enter a valid email address.';
                    errorMsg.style.display = 'block';
                }
                return;
            }

            if (errorMsg) errorMsg.style.display = 'none';
            if (submitBtn) submitBtn.disabled = true;
            if (submitBtn) submitBtn.textContent = 'Subscribing\u2026';

            doSubscribe(email, function() {
                // Success
                setFlag(LS_SUBSCRIBED, 'true');
                inlineConverted = true;
                if (box.querySelector('.pb-lead-form')) {
                    box.querySelector('.pb-lead-form').style.display = 'none';
                }
                if (successMsg) successMsg.style.display = 'block';
                // Hide the bar since user just subscribed
                hideBar();
            }, function(errText) {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Subscribe';
                }
                if (errorMsg) {
                    errorMsg.textContent = errText;
                    errorMsg.style.display = 'block';
                }
            });
        }

        submitBtn && submitBtn.addEventListener('click', handleInlineSubmit);
        emailInput && emailInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') handleInlineSubmit();
        });
    }

    // ── Wire up bar form ───────────────────────────────────────
    function initBarForm() {
        var bar        = document.getElementById('pb-lead-bar');
        if (!bar) return;

        var closeBtn   = bar.querySelector('.pb-bar-close');
        var emailInput = bar.querySelector('.pb-bar-email');
        var submitBtn  = bar.querySelector('.pb-bar-submit');
        var successMsg = bar.querySelector('.pb-bar-success');
        var errorMsg   = bar.querySelector('.pb-bar-error');
        var formDiv    = bar.querySelector('.pb-bar-form');

        closeBtn && closeBtn.addEventListener('click', function() {
            setFlag(LS_BAR_DISMISSED, String(Date.now()));
            hideBar();
        });

        function handleBarSubmit() {
            var email = emailInput ? emailInput.value.trim() : '';
            if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                if (errorMsg) {
                    errorMsg.textContent = 'Please enter a valid email address.';
                    errorMsg.style.display = 'block';
                }
                return;
            }

            if (errorMsg) errorMsg.style.display = 'none';
            if (submitBtn) submitBtn.disabled = true;
            if (submitBtn) submitBtn.textContent = 'Joining\u2026';

            doSubscribe(email, function() {
                setFlag(LS_SUBSCRIBED, 'true');
                if (formDiv) formDiv.style.display = 'none';
                var textDiv = bar.querySelector('.pb-bar-text');
                if (textDiv) textDiv.style.display = 'none';
                if (successMsg) successMsg.style.display = 'block';
                // Auto-dismiss bar after 4 seconds on success
                setTimeout(function() { hideBar(); }, 4000);
            }, function(errText) {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Get The Neural Feed';
                }
                if (errorMsg) {
                    errorMsg.textContent = errText;
                    errorMsg.style.display = 'block';
                }
            });
        }

        submitBtn && submitBtn.addEventListener('click', handleBarSubmit);
        emailInput && emailInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') handleBarSubmit();
        });
    }

    // ── Main scroll handler ────────────────────────────────────
    function onScroll() {
        var depth = scrollDepth();

        // 50% threshold: show inline box
        if (depth >= 50 && !inlineShown) {
            // Only show if not already subscribed and not recently dismissed
            if (!getFlag(LS_SUBSCRIBED) && !isDismissed(LS_INLINE_DISMISSED, INLINE_DISMISS_TTL)) {
                showInline();
            }
        }

        // 85% threshold: show bar
        if (depth >= 85 && !barShown) {
            // Only show if not already subscribed and not recently dismissed
            if (!getFlag(LS_SUBSCRIBED) && !isDismissed(LS_BAR_DISMISSED, BAR_DISMISS_TTL)) {
                showBar();
            }
        }
    }

    // ── Init ──────────────────────────────────────────────────
    function init() {
        // Only run on single post pages (double-check body class)
        if (!document.body.classList.contains('single-post')) return;

        // Early exit: already subscribed, no need to set anything up
        if (getFlag(LS_SUBSCRIBED)) return;

        // Inject inline box into the DOM at correct position
        injectInlineBox();

        // Wire up form event handlers
        initInlineForm();
        initBarForm();

        // Attach scroll listener (passive for performance)
        window.addEventListener('scroll', onScroll, { passive: true });

        // Check on init in case page is already scrolled (e.g. anchor link)
        onScroll();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
</script>
    <?php
}, 25 );

// ============================================================
// AETHER TRANSPARENCY SECTION — CSS (v3.6.0)
//    Injects the self-contained CSS for the transparency section.
//    Only on single blog post pages (is_single()).
//    All styles namespaced under .aether-transparency.
// ============================================================

add_action( 'wp_head', function () {
    if ( ! is_single() ) {
        return;
    }
    // Only inject CSS if there is data to show
    $raw = get_option( 'purebrain_transparency_data', '' );
    if ( empty( $raw ) ) {
        return;
    }
    ?>
<style id="purebrain-transparency-css">
/* ===================================================
   AETHER TRANSPARENCY SECTION — Self-Contained CSS
   All styles namespaced to .aether-transparency
   No conflicts with existing blog CSS
   v3.6.0
   =================================================== */

.aether-transparency {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0d0f1a;
    border: 1px solid rgba(42, 147, 193, 0.25);
    border-left: 4px solid #2a93c1;
    border-radius: 10px;
    padding: 28px 32px;
    margin: 48px 0 32px 0;
    color: #e0e6f0;
    max-width: 100%;
    position: relative;
    overflow: hidden;
    box-sizing: border-box;
}

.aether-transparency::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 220px;
    height: 220px;
    background: radial-gradient(circle at top right, rgba(42, 147, 193, 0.06) 0%, transparent 70%);
    pointer-events: none;
}

.aether-transparency__header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(42, 147, 193, 0.15);
}

.aether-transparency__badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(42, 147, 193, 0.12);
    border: 1px solid rgba(42, 147, 193, 0.3);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #2a93c1;
    white-space: nowrap;
}

.aether-transparency__badge-dot {
    width: 6px;
    height: 6px;
    background: #2a93c1;
    border-radius: 50%;
    animation: pb-transparency-pulse 2.4s ease-in-out infinite;
    flex-shrink: 0;
}

@keyframes pb-transparency-pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

.aether-transparency__title {
    font-size: 13px;
    color: rgba(224, 230, 240, 0.5);
    font-weight: 400;
    letter-spacing: 0.02em;
}

.aether-transparency__summary {
    font-size: 15px;
    line-height: 1.65;
    color: #c8d4e8;
    margin-bottom: 24px;
    font-style: italic;
}

.aether-transparency__summary strong {
    color: #e0e6f0;
    font-style: normal;
}

.aether-transparency__stats {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 24px;
}

.aether-transparency__stat {
    flex: 1;
    min-width: 120px;
    background: rgba(8, 10, 18, 0.6);
    border: 1px solid rgba(42, 147, 193, 0.15);
    border-radius: 8px;
    padding: 12px 16px;
    text-align: center;
    box-sizing: border-box;
}

.aether-transparency__stat-number {
    display: block;
    font-size: 22px;
    font-weight: 700;
    color: #2a93c1;
    line-height: 1.1;
    margin-bottom: 4px;
}

.aether-transparency__stat-label {
    display: block;
    font-size: 11px;
    color: rgba(224, 230, 240, 0.5);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 500;
}

.aether-transparency__table-wrap {
    margin-bottom: 24px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

.aether-transparency__table-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(224, 230, 240, 0.4);
    margin-bottom: 10px;
}

.aether-transparency__table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13.5px;
}

.aether-transparency__table thead tr {
    border-bottom: 1px solid rgba(42, 147, 193, 0.2);
}

.aether-transparency__table th {
    text-align: left;
    padding: 8px 12px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: rgba(224, 230, 240, 0.45);
    white-space: nowrap;
}

.aether-transparency__table td {
    padding: 9px 12px;
    color: #c8d4e8;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    vertical-align: top;
}

.aether-transparency__table tbody tr:last-child td {
    border-bottom: none;
}

.aether-transparency__table tbody tr:hover td {
    background: rgba(42, 147, 193, 0.04);
}

.aether-transparency__table td:first-child {
    color: #e0e6f0;
    font-weight: 500;
}

.aether-transparency__table td.value-cell {
    color: #2a93c1;
    font-weight: 600;
    white-space: nowrap;
}

.aether-transparency__highlight {
    background: rgba(241, 66, 11, 0.07);
    border: 1px solid rgba(241, 66, 11, 0.2);
    border-left: 3px solid #f1420b;
    border-radius: 6px;
    padding: 14px 16px;
    margin-bottom: 24px;
    display: flex;
    gap: 12px;
    align-items: flex-start;
}

.aether-transparency__highlight-icon {
    font-size: 16px;
    line-height: 1;
    flex-shrink: 0;
    margin-top: 1px;
}

.aether-transparency__highlight-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #f1420b;
    display: block;
    margin-bottom: 4px;
}

.aether-transparency__highlight-text {
    font-size: 13.5px;
    line-height: 1.55;
    color: #c8d4e8;
    margin: 0;
}

.aether-transparency__cta {
    border-top: 1px solid rgba(42, 147, 193, 0.15);
    padding-top: 20px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
}

.aether-transparency__cta-text {
    font-size: 14px;
    color: rgba(224, 230, 240, 0.65);
    line-height: 1.5;
    flex: 1;
    min-width: 200px;
}

.aether-transparency__cta-text strong {
    color: #e0e6f0;
}

.aether-transparency__cta-btn {
    display: inline-block;
    background: #f1420b;
    color: #ffffff !important;
    text-decoration: none !important;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.04em;
    padding: 11px 22px;
    border-radius: 6px;
    white-space: nowrap;
    transition: background 0.2s ease, box-shadow 0.2s ease;
    flex-shrink: 0;
}

.aether-transparency__cta-btn:hover {
    background: #d93600 !important;
    box-shadow: 0 4px 16px rgba(241, 66, 11, 0.35);
    color: #ffffff !important;
}

.aether-transparency__sig {
    margin-top: 16px;
    font-size: 12px;
    color: rgba(224, 230, 240, 0.3);
    text-align: right;
    font-style: italic;
}

@media (max-width: 640px) {
    .aether-transparency {
        padding: 20px 18px;
    }
    .aether-transparency__stats {
        gap: 8px;
    }
    .aether-transparency__stat {
        min-width: 100px;
        padding: 10px 12px;
    }
    .aether-transparency__stat-number {
        font-size: 18px;
    }
    .aether-transparency__cta {
        flex-direction: column;
        align-items: flex-start;
    }
    .aether-transparency__cta-btn {
        width: 100%;
        text-align: center;
    }
}
</style>
    <?php
}, 30 );

// ============================================================
// AETHER TRANSPARENCY SECTION — HTML RENDER (v3.6.0)
//    Reads purebrain_transparency_data option (JSON).
//    If empty/missing: no output (graceful fallback).
//    Renders the transparency section HTML and injects it
//    into the DOM before .blog-cta-block via JS (wp_footer).
//    Runs only on single blog post pages (is_single()).
//    All dynamic data escaped with esc_html / esc_url.
//    Priority 28 — after lead capture CSS (25), before nav JS (default).
// ============================================================

add_action( 'wp_footer', function () {
    if ( ! is_single() ) {
        return;
    }

    $raw = get_option( 'purebrain_transparency_data', '' );
    if ( empty( $raw ) ) {
        return;
    }

    $data = json_decode( $raw, true );
    if ( ! is_array( $data ) ) {
        return;
    }

    // LOW-001 (v3.8.0): Store raw values in variables — escaping is applied at the
    // echo/output point below (WordPress VIP best practice). Do NOT escape here.
    $week_of     = isset( $data['week_of'] )     ? $data['week_of']     : '';
    $summary     = isset( $data['summary'] )     ? $data['summary']     : '';
    $biggest_win = isset( $data['biggest_win'] ) ? $data['biggest_win'] : '';
    $cta_url     = home_url( '/#awakening' ); // esc_url() applied at echo point

    // CTA text: use override if set, otherwise default
    $default_cta = 'This is what AI partnership looks like. Not a chatbot. Not a tool you prompt once and forget. A team that ships real work, every day, alongside you.';
    $cta_text    = ( ! empty( $data['cta_text'] ) ) ? $data['cta_text'] : $default_cta;

    // Stats — stored raw, escaped at echo point
    $stats             = isset( $data['stats'] ) && is_array( $data['stats'] ) ? $data['stats'] : array();
    $stat_agents       = isset( $stats['specialist_agents'] ) ? (string) $stats['specialist_agents'] : '0';
    $stat_domains      = isset( $stats['work_domains'] )      ? (string) $stats['work_domains']      : '0';
    $stat_deliverables = isset( $stats['deliverables'] )      ? $stats['deliverables']               : '0';
    $stat_hours        = isset( $stats['human_hours'] )       ? $stats['human_hours']                : '0';

    // Work breakdown rows
    $breakdown = isset( $data['work_breakdown'] ) && is_array( $data['work_breakdown'] ) ? $data['work_breakdown'] : array();

    // Only render if we have the minimum required fields
    if ( empty( $week_of ) || empty( $summary ) ) {
        return;
    }

    ?>
<div id="pb-transparency-section" style="display:none;">
<div class="aether-transparency" role="complementary" aria-label="Aether Weekly Transparency Report">

  <div class="aether-transparency__header">
    <span class="aether-transparency__badge">
      <span class="aether-transparency__badge-dot"></span>
      Aether Transparency Report
    </span>
    <span class="aether-transparency__title">Week of <?php echo esc_html( $week_of ); ?></span>
  </div>

  <p class="aether-transparency__summary"><?php echo esc_html( $summary ); ?></p>

  <div class="aether-transparency__stats">
    <div class="aether-transparency__stat">
      <span class="aether-transparency__stat-number"><?php echo esc_html( $stat_agents ); ?></span>
      <span class="aether-transparency__stat-label">Specialist Agents</span>
    </div>
    <div class="aether-transparency__stat">
      <span class="aether-transparency__stat-number"><?php echo esc_html( $stat_domains ); ?></span>
      <span class="aether-transparency__stat-label">Work Domains</span>
    </div>
    <div class="aether-transparency__stat">
      <span class="aether-transparency__stat-number"><?php echo esc_html( $stat_deliverables ); ?></span>
      <span class="aether-transparency__stat-label">Deliverables Shipped</span>
    </div>
    <div class="aether-transparency__stat">
      <span class="aether-transparency__stat-number"><?php echo esc_html( $stat_hours ); ?></span>
      <span class="aether-transparency__stat-label">Est. Human Hours</span>
    </div>
  </div>

  <?php if ( ! empty( $breakdown ) ) : ?>
  <div class="aether-transparency__table-wrap">
    <p class="aether-transparency__table-label">Work Breakdown</p>
    <table class="aether-transparency__table">
      <thead>
        <tr>
          <th>Domain</th>
          <th>What Got Done</th>
          <th>Effort Level</th>
          <th>Value Estimate</th>
        </tr>
      </thead>
      <tbody>
        <?php foreach ( $breakdown as $row ) : ?>
        <tr>
          <td><?php echo esc_html( isset( $row['domain'] )      ? $row['domain']      : '' ); ?></td>
          <td><?php echo esc_html( isset( $row['description'] ) ? $row['description'] : '' ); ?></td>
          <td><?php echo esc_html( isset( $row['effort'] )      ? $row['effort']      : '' ); ?></td>
          <td class="value-cell"><?php echo esc_html( isset( $row['value'] ) ? $row['value'] : '' ); ?></td>
        </tr>
        <?php endforeach; ?>
      </tbody>
    </table>
  </div>
  <?php endif; ?>

  <?php if ( ! empty( $biggest_win ) ) : ?>
  <div class="aether-transparency__highlight">
    <span class="aether-transparency__highlight-icon">&#9655;</span>
    <div>
      <span class="aether-transparency__highlight-label">Biggest Win</span>
      <p class="aether-transparency__highlight-text"><?php echo esc_html( $biggest_win ); ?></p>
    </div>
  </div>
  <?php endif; ?>

  <div class="aether-transparency__cta">
    <p class="aether-transparency__cta-text"><?php echo esc_html( $cta_text ); ?></p>
    <a href="<?php echo esc_url( $cta_url ); ?>" class="aether-transparency__cta-btn">Start Your AI Partnership</a>
  </div>

  <p class="aether-transparency__sig">&#x2014; Aether &nbsp;|&nbsp; The invisible essential</p>

</div>
</div>

<script id="purebrain-transparency-inject">
(function() {
    'use strict';
    function injectTransparencySection() {
        var wrapper = document.getElementById('pb-transparency-section');
        if (!wrapper) return;

        var inner = wrapper.firstElementChild;
        if (!inner) return;

        // Target: insert AFTER post content AND BEFORE .blog-cta-block
        var ctaBlock    = document.querySelector('.blog-cta-block');
        var postContent = document.querySelector('.post-content');

        if (ctaBlock && ctaBlock.parentNode) {
            // Insert the transparency div immediately before the CTA block
            ctaBlock.parentNode.insertBefore(inner, ctaBlock);
        } else if (postContent && postContent.parentNode) {
            // Fallback: append after post content
            postContent.parentNode.insertBefore(inner, postContent.nextSibling);
        } else {
            // Last resort: insert before legal footer
            var legalFooter = document.getElementById('purebrain-legal-footer');
            if (legalFooter && legalFooter.parentNode) {
                legalFooter.parentNode.insertBefore(inner, legalFooter);
            }
        }

        // Remove the now-empty wrapper
        if (wrapper.parentNode) {
            wrapper.parentNode.removeChild(wrapper);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectTransparencySection);
    } else {
        injectTransparencySection();
    }
})();
</script>
    <?php
}, 28 );

add_action( 'wp_footer', function () {
    if ( ! ( is_single() || is_category() || is_archive() || is_tag() ) ) {
        return;
    }
    $home_url       = esc_url( home_url( '/' ) );
    $subscribe_url  = esc_url( home_url( '/blog/#neural-feed-subscribe' ) );
    $assessment_url = esc_url( home_url( '/ai-adoption-review/' ) );
    ?>
<script id="purebrain-blog-nav-menu-js">
(function() {
    'use strict';

    function initBlogNav() {
        // Find the navbar container
        var container = document.querySelector('nav.navbar .container');
        if (!container) {
            // Fallback: try common navbar selectors
            container = document.querySelector('.navbar-inner') ||
                        document.querySelector('header nav') ||
                        document.querySelector('.site-header .container') ||
                        document.querySelector('header .container');
        }
        if (!container) return;

        // Don't inject twice
        if (document.querySelector('.pb-blog-nav')) return;

        // Build the nav links element
        var nav = document.createElement('div');
        nav.className = 'pb-blog-nav';
        nav.setAttribute('role', 'navigation');
        nav.setAttribute('aria-label', 'Quick navigation');
        nav.innerHTML =
            '<a href="<?php echo $home_url; ?>">Home</a>' +
            '<span class="pb-nav-sep" aria-hidden="true">|</span>' +
            '<a href="<?php echo $subscribe_url; ?>">Subscribe</a>' +
            '<span class="pb-nav-sep" aria-hidden="true">|</span>' +
            '<a href="<?php echo $assessment_url; ?>">Free AI Assessment</a>';

        container.appendChild(nav);
    }

    // Run on DOMContentLoaded (or immediately if already loaded)
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initBlogNav);
    } else {
        initBlogNav();
    }
})();
</script>
    <?php
} );

// ============================================================
// n) BLOG LISTING READ MORE BUTTON (v4.0.0)
//    On the main blog listing page (/blog/, page ID 319 on purebrain.ai),
//    the WordPress wp:latest-posts block only appends a "Read More" link
//    to posts that use the <!--more--> tag in their content. Posts with
//    plain excerpts render without any button.
//
//    PERMANENT RULE: Every post card on the blog listing page MUST show
//    a "READ MORE" orange button. This ensures a uniform, professional
//    appearance regardless of how each post was authored.
//
//    Implementation:
//    - CSS injected via wp_head: styles the button.
//    - JS injected via wp_footer (priority 5 — runs early so Elementor
//      doesn't re-render over it): scans every .wp-block-latest-posts__list-item
//      for a read-more link. If missing, creates one by reading the post href
//      from the item's first <a> tag and inserting a styled button after the
//      excerpt div.
//
//    Fires on: is_page(319) — the blog listing page.
//    Does NOT fire on single posts, categories, or archives.
//
//    Button style: matches the brand orange button (#f1420b bg, white text,
//    uppercase "READ MORE", border-radius 6px, bold font).
// ============================================================

add_action( 'wp_head', function () {
    // Only on the blog listing page
    if ( ! is_page( 319 ) && ! is_home() ) {
        return;
    }
    ?>
<style id="purebrain-read-more-btn">
/* ============================================================
   BLOG LISTING: Universal READ MORE button (v4.0.0)
   Applies to: wp:latest-posts block on blog listing page.
   Ensures uniform orange button on every post card.
   ============================================================ */

/* Style the WordPress-native read-more link (when it exists) */
.wp-block-latest-posts__list-item .wp-block-latest-posts__read-more,
.wp-block-latest-posts li .wp-block-latest-posts__read-more {
    display: inline-block !important;
    margin-top: 12px !important;
    padding: 8px 20px !important;
    background: #f1420b !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-radius: 6px !important;
    text-decoration: none !important;
    transition: background 0.2s ease, transform 0.15s ease !important;
    box-shadow: none !important;
}

.wp-block-latest-posts__list-item .wp-block-latest-posts__read-more:hover,
.wp-block-latest-posts li .wp-block-latest-posts__read-more:hover {
    background: #2a93c1 !important;
    color: #ffffff !important;
    text-decoration: none !important;
    transform: translateY(-1px) !important;
}

/* Style the JS-injected pb-read-more button (for posts missing the native link) */
.pb-read-more-btn {
    display: inline-block !important;
    margin-top: 14px !important;
    padding: 8px 20px !important;
    background: #f1420b !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-radius: 6px !important;
    text-decoration: none !important;
    transition: background 0.2s ease, transform 0.15s ease !important;
    box-shadow: none !important;
}

.pb-read-more-btn:hover {
    background: #2a93c1 !important;
    color: #ffffff !important;
    text-decoration: none !important;
    transform: translateY(-1px) !important;
}
</style>
    <?php
} );

add_action( 'wp_footer', function () {
    // Only on the blog listing page
    if ( ! is_page( 319 ) && ! is_home() ) {
        return;
    }
    ?>
<script id="purebrain-read-more-btn-js">
(function() {
    'use strict';

    // PERMANENT RULE: Every post card on the blog listing MUST have a READ MORE button.
    // This function ensures uniform appearance regardless of how posts were authored.
    function enforceReadMoreButtons() {
        // Target each post card in the wp:latest-posts block
        var postItems = document.querySelectorAll(
            '.wp-block-latest-posts__list-item, ' +
            '.wp-block-latest-posts li'
        );

        if (!postItems.length) return;

        postItems.forEach(function(item) {
            // Check if this item already has any read-more link
            var existingReadMore = item.querySelector(
                '.wp-block-latest-posts__read-more, ' +
                '.pb-read-more-btn, ' +
                'a[class*="read-more"]'
            );
            if (existingReadMore) return; // Already has button — skip

            // Find the post URL from the first anchor in this card
            // (usually the title link or featured image link)
            var postLink = item.querySelector('a');
            if (!postLink) return;

            var postUrl = postLink.getAttribute('href');
            if (!postUrl) return;

            // Find the excerpt div to insert button after it
            var excerptEl = item.querySelector(
                '.wp-block-latest-posts__post-excerpt, ' +
                '.wp-block-latest-posts__post-full-content'
            );

            // Create the Read More button
            var btn = document.createElement('a');
            btn.href = postUrl;
            btn.className = 'pb-read-more-btn';
            btn.textContent = 'READ MORE';
            btn.setAttribute('aria-label', 'Read the full post');

            if (excerptEl) {
                // Insert after the excerpt element
                excerptEl.parentNode.insertBefore(btn, excerptEl.nextSibling);
            } else {
                // Fallback: append to the list item
                item.appendChild(btn);
            }
        });
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', enforceReadMoreButtons);
    } else {
        enforceReadMoreButtons();
    }

    // Also run after a short delay in case Elementor re-renders the block
    setTimeout(enforceReadMoreButtons, 800);
})();
</script>
    <?php
}, 5 );

// ============================================================
// p) AI PARTNERSHIP GUIDE CONTENT GATE (v4.1.0)
//    Partial content gate on /ai-partnership-guide/ page.
//    Sections 1-3 visible freely (problem framing).
//    Sections 4-7 hidden behind gradient fade + blurred preview + email form.
//    Email form submits to POST /wp-json/purebrain/v1/guide-unlock (server-side proxy).
//    On success: content revealed, localStorage['pb_guide_unlocked'] = '1'.
//    Return visit: auto-reveals if localStorage key is present.
// ============================================================

add_action( 'wp_head', function () {
    // Only inject on the AI Partnership Guide page
    if ( ! is_page( 'ai-partnership-guide' ) ) {
        return;
    }
    ?>
<style id="pb-guide-gate-css">
/* ============================================================
   AI PARTNERSHIP GUIDE - CONTENT GATE (v4.1.0)
   ============================================================ */

/* Gate wrapper: wraps sections 4-7 */
#pb-guide-gate-wrapper {
    position: relative;
}

/* Blurred preview of gated content */
#pb-guide-gated-content {
    filter: blur(6px) !important;
    pointer-events: none !important;
    user-select: none !important;
    max-height: 320px !important;
    overflow: hidden !important;
    opacity: 0.5 !important;
    transition: filter 0.6s ease, opacity 0.6s ease, max-height 0.8s ease !important;
}

/* Unlocked state - full reveal */
#pb-guide-gated-content.pb-guide-unlocked {
    filter: none !important;
    pointer-events: auto !important;
    user-select: auto !important;
    max-height: none !important;
    overflow: visible !important;
    opacity: 1 !important;
}

/* Gradient fade overlay - sits above the blurred content */
#pb-guide-fade-overlay {
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    height: 280px;
    background: linear-gradient(
        to bottom,
        rgba(8, 10, 18, 0) 0%,
        rgba(8, 10, 18, 0.5) 40%,
        rgba(8, 10, 18, 0.88) 70%,
        rgba(8, 10, 18, 1) 100%
    ) !important;
    pointer-events: none;
    z-index: 2;
}

/* Gate form container */
#pb-guide-gate-form-wrapper {
    position: relative;
    z-index: 10;
    margin: 0 auto 48px auto;
    max-width: 540px;
    background: rgba(13, 17, 23, 0.95);
    border: 1px solid rgba(42, 147, 193, 0.35);
    border-radius: 16px;
    padding: 40px 36px;
    text-align: center;
    box-shadow:
        0 0 0 1px rgba(42, 147, 193, 0.12),
        0 12px 48px rgba(0, 0, 0, 0.6),
        0 0 80px rgba(42, 147, 193, 0.06);
}

@media (max-width: 600px) {
    #pb-guide-gate-form-wrapper {
        margin-left: 16px;
        margin-right: 16px;
        padding: 28px 20px;
    }
}

/* Lock icon above the headline */
#pb-guide-gate-form-wrapper .pb-gate-lock-icon {
    font-size: 32px;
    margin-bottom: 14px;
    display: block;
    filter: drop-shadow(0 0 12px rgba(42, 147, 193, 0.4));
}

#pb-guide-gate-form-wrapper h3 {
    color: #ffffff !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    margin: 0 0 10px 0 !important;
    line-height: 1.3 !important;
}

#pb-guide-gate-form-wrapper p {
    color: #8b9bb4 !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
    margin: 0 0 24px 0 !important;
}

/* Form inputs */
#pb-guide-gate-form-wrapper .pb-gate-input {
    display: block;
    width: 100%;
    box-sizing: border-box;
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    font-size: 15px !important;
    padding: 13px 16px !important;
    margin-bottom: 12px !important;
    outline: none !important;
    transition: border-color 0.2s ease !important;
    font-family: inherit !important;
}

#pb-guide-gate-form-wrapper .pb-gate-input:focus {
    border-color: rgba(42, 147, 193, 0.6) !important;
    background: rgba(255, 255, 255, 0.09) !important;
}

#pb-guide-gate-form-wrapper .pb-gate-input::placeholder {
    color: rgba(255, 255, 255, 0.35) !important;
}

/* Submit button - orange bg, white text, hover blue */
#pb-guide-gate-form-wrapper .pb-gate-submit {
    display: block !important;
    width: 100% !important;
    background: #f1420b !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    padding: 14px 24px !important;
    cursor: pointer !important;
    transition: background 0.2s ease, transform 0.15s ease !important;
    letter-spacing: 0.03em !important;
    text-transform: uppercase !important;
    font-family: inherit !important;
    margin-top: 4px !important;
}

#pb-guide-gate-form-wrapper .pb-gate-submit:hover {
    background: #2a93c1 !important;
    transform: translateY(-1px) !important;
}

#pb-guide-gate-form-wrapper .pb-gate-submit:active {
    transform: translateY(0) !important;
}

#pb-guide-gate-form-wrapper .pb-gate-submit:disabled {
    opacity: 0.6 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* Privacy note */
#pb-guide-gate-form-wrapper .pb-gate-privacy {
    color: rgba(255, 255, 255, 0.3) !important;
    font-size: 12px !important;
    margin: 14px 0 0 0 !important;
}

/* Status messages */
#pb-guide-gate-form-wrapper .pb-gate-msg {
    font-size: 14px !important;
    margin-top: 12px !important;
    padding: 10px 14px !important;
    border-radius: 6px !important;
    display: none;
}

#pb-guide-gate-form-wrapper .pb-gate-msg.pb-gate-error {
    background: rgba(241, 66, 11, 0.12) !important;
    border: 1px solid rgba(241, 66, 11, 0.3) !important;
    color: #f87a5c !important;
}

#pb-guide-gate-form-wrapper .pb-gate-msg.pb-gate-success {
    background: rgba(42, 147, 193, 0.12) !important;
    border: 1px solid rgba(42, 147, 193, 0.3) !important;
    color: #6ec8e8 !important;
}

/* Full-gate area (includes fade overlay + form) */
#pb-guide-gate-area {
    position: relative;
    margin-top: -60px;
    padding-top: 20px;
}
</style>
    <?php
}, 25 );

add_action( 'wp_footer', function () {
    // Only inject on the AI Partnership Guide page
    if ( ! is_page( 'ai-partnership-guide' ) ) {
        return;
    }
    ?>
<script id="pb-guide-gate-js">
(function() {
    'use strict';

    var LS_KEY = 'pb_guide_unlocked';
    var UNLOCK_ENDPOINT = '/wp-json/purebrain/v1/guide-unlock';

    function isAlreadyUnlocked() {
        try {
            return localStorage.getItem(LS_KEY) === '1';
        } catch(e) {
            return false;
        }
    }

    function markUnlocked() {
        try {
            localStorage.setItem(LS_KEY, '1');
        } catch(e) {}
    }

    function revealContent() {
        var gated = document.getElementById('pb-guide-gated-content');
        var gateArea = document.getElementById('pb-guide-gate-area');
        if (gated) {
            gated.classList.add('pb-guide-unlocked');
        }
        if (gateArea) {
            gateArea.style.display = 'none';
        }
    }

    /**
     * Find the cutoff point: after the 3rd h2/h3 heading that marks a section.
     * The guide has 7 sections identified by h2 headings.
     * We show sections 1-3, gate sections 4-7.
     *
     * Strategy: Find all top-level h2 elements in the post content.
     * Insert the gate after the 3rd h2's section ends (before 4th h2).
     */
    function buildGate() {
        // Find the post content container - try multiple selectors
        var contentEl = (
            document.querySelector('.entry-content') ||
            document.querySelector('.post-content') ||
            document.querySelector('.elementor-widget-theme-post-content') ||
            document.querySelector('.wp-block-post-content') ||
            document.querySelector('article .content') ||
            document.querySelector('main .content') ||
            document.body
        );

        if (!contentEl) return;

        // Collect all h2 elements inside the content
        var headings = Array.prototype.slice.call(contentEl.querySelectorAll('h2'));

        // We need at least 4 headings to gate (show 3, hide the rest)
        if (headings.length < 4) {
            return; // Not enough structure to gate
        }

        // The 4th heading (index 3) is where the gated content begins
        var gateStartEl = headings[3];

        // Collect all sibling elements from gateStartEl onwards
        var allChildren = Array.prototype.slice.call(contentEl.children);
        var gateStartIdx = allChildren.indexOf(gateStartEl);
        if (gateStartIdx === -1) {
            // heading might be nested inside a wrapper - find its container
            // Walk up from gateStartEl until we find a direct child of contentEl
            var walker = gateStartEl;
            while (walker && walker.parentElement !== contentEl) {
                walker = walker.parentElement;
            }
            if (walker && walker.parentElement === contentEl) {
                gateStartIdx = allChildren.indexOf(walker);
            }
        }

        if (gateStartIdx === -1 || gateStartIdx >= allChildren.length) {
            return; // Could not find cutoff
        }

        // Elements to be gated (sections 4-7)
        var toGate = allChildren.slice(gateStartIdx);
        if (toGate.length === 0) return;

        // Create the gated content wrapper
        var gatedWrapper = document.createElement('div');
        gatedWrapper.id = 'pb-guide-gated-content';

        // Move gated elements into the wrapper
        toGate.forEach(function(el) {
            gatedWrapper.appendChild(el);
        });

        // Build the gate area (fade overlay + email form)
        var gateArea = document.createElement('div');
        gateArea.id = 'pb-guide-gate-area';

        // Fade overlay
        var fadeOverlay = document.createElement('div');
        fadeOverlay.id = 'pb-guide-fade-overlay';
        gateArea.appendChild(fadeOverlay);

        // Form wrapper
        var formWrapper = document.createElement('div');
        formWrapper.id = 'pb-guide-gate-form-wrapper';
        formWrapper.innerHTML = [
            '<span class="pb-gate-lock-icon">&#128274;</span>',
            '<h3>You\'re halfway through the guide</h3>',
            '<p>The next 4 sections cover the business case, readiness assessment, how to get started, and FAQ. Enter your email to unlock the full guide instantly.</p>',
            '<form id="pb-guide-gate-form" novalidate>',
            '  <input type="text" class="pb-gate-input" id="pb-gate-firstname" placeholder="First name (optional)" autocomplete="given-name" />',
            '  <input type="email" class="pb-gate-input" id="pb-gate-email" placeholder="Your email address" required autocomplete="email" />',
            '  <button type="submit" class="pb-gate-submit">Unlock the Full Guide</button>',
            '  <p class="pb-gate-privacy">No spam. Unsubscribe anytime. Your data is never shared.</p>',
            '  <div class="pb-gate-msg" id="pb-gate-msg"></div>',
            '</form>'
        ].join('');
        gateArea.appendChild(formWrapper);

        // Build the outer wrapper
        var outerWrapper = document.createElement('div');
        outerWrapper.id = 'pb-guide-gate-wrapper';
        outerWrapper.appendChild(gatedWrapper);
        outerWrapper.appendChild(gateArea);

        // Insert the outer wrapper at the gateStartIdx position in contentEl
        var refNode = allChildren[gateStartIdx]; // This element was moved into gatedWrapper
        // Since we moved it, we append outerWrapper to contentEl
        contentEl.appendChild(outerWrapper);

        // Attach form submit handler
        var form = document.getElementById('pb-guide-gate-form');
        if (form) {
            form.addEventListener('submit', handleFormSubmit);
        }
    }

    function handleFormSubmit(e) {
        e.preventDefault();

        var emailInput     = document.getElementById('pb-gate-email');
        var firstNameInput = document.getElementById('pb-gate-firstname');
        var submitBtn      = document.querySelector('.pb-gate-submit');
        var msgEl          = document.getElementById('pb-gate-msg');

        var email     = emailInput ? emailInput.value.trim() : '';
        var firstName = firstNameInput ? firstNameInput.value.trim() : '';

        // Basic client-side validation
        if (!email || !isValidEmail(email)) {
            showMessage(msgEl, 'Please enter a valid email address.', 'error');
            return;
        }

        // Disable submit while in-flight
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Unlocking...';
        }
        hideMessage(msgEl);

        // POST to our server-side proxy
        var payload = JSON.stringify({ email: email, first_name: firstName });

        var xhr = new XMLHttpRequest();
        xhr.open('POST', UNLOCK_ENDPOINT, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.setRequestHeader('X-WP-Nonce', window.pbGuideNonce || '');

        xhr.onload = function() {
            var data = {};
            try { data = JSON.parse(xhr.responseText); } catch(ex) {}

            if (xhr.status === 200 && data.success) {
                // Success
                showMessage(msgEl, 'Check your email for your welcome note. Unlocking now...', 'success');
                markUnlocked();

                setTimeout(function() {
                    revealContent();
                }, 1200);
            } else if (xhr.status === 429) {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Unlock the Full Guide';
                }
                showMessage(msgEl, 'Too many requests. Please wait a moment and try again.', 'error');
            } else {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Unlock the Full Guide';
                }
                var errMsg = (data.message) ? data.message : 'Something went wrong. Please try again.';
                showMessage(msgEl, errMsg, 'error');
            }
        };

        xhr.onerror = function() {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Unlock the Full Guide';
            }
            showMessage(msgEl, 'Network error. Please check your connection and try again.', 'error');
        };

        xhr.send(payload);
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function showMessage(el, text, type) {
        if (!el) return;
        el.textContent = text;
        el.className = 'pb-gate-msg pb-gate-' + type;
        el.style.display = 'block';
    }

    function hideMessage(el) {
        if (!el) return;
        el.style.display = 'none';
    }

    // --- Init ---

    function init() {
        // Check if already unlocked from a previous visit
        if (isAlreadyUnlocked()) {
            // Content will be visible naturally - no gate needed
            // Still build the DOM structure so revealContent() won't error,
            // but immediately reveal
            buildGate();
            revealContent();
            return;
        }

        // Build the gate
        buildGate();
    }

    // Run on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
</script>
    <?php
}, 20 );

// ============================================================
// o) BLOG LISTING POSTS PER PAGE CAP (v4.0.0)
//    Limits the main blog listing page to a maximum of 10 posts.
//    The wp:latest-posts block already has postsToShow:10, but
//    this pre_get_posts filter provides a server-side backstop
//    for any future Elementor or theme-level listing pages.
//
//    Fires on: is_page(319) — the blog listing page.
//    Does NOT affect single posts, archives, or search.
// ============================================================

add_action( 'pre_get_posts', function ( $query ) {
    // Only on the main blog page (ID 319) for non-admin, non-main queries that target posts
    if ( is_admin() ) {
        return;
    }
    // This runs on page 319 when it's being loaded as the blog page
    if ( is_page( 319 ) && ! $query->is_main_query() ) {
        $query->set( 'posts_per_page', 10 );
    }
} );

// ============================================================
// p) SOCIAL SHARING BAR — GEO FIX 3 (v4.2.0)
//    Injects a branded social sharing bar on single blog posts.
//    Buttons: LinkedIn, X (Twitter), Email, Copy Link.
//    Styled in PureBrain brand colors.
//    Positioned before .blog-cta-block via JS DOM insertion.
//    Also un-hides the theme-native .post-social-sharing buttons
//    by overriding the Additional CSS display:none rule.
// ============================================================

// CSS for the sharing bar + un-hide theme native sharing
add_action( 'wp_head', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<style id="purebrain-social-share-css">
/* ============================================================
   SOCIAL SHARING BAR — v4.2.0
   Custom pb-social-share bar + restore theme .post-social-sharing
   ============================================================ */

/* ----- 1. CUSTOM PB SHARING BAR ----- */
#pb-social-share {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    padding: 20px 0 !important;
    margin: 32px 0 16px 0 !important;
    border-top: 1px solid rgba(42, 147, 193, 0.25) !important;
    flex-wrap: wrap !important;
}

#pb-social-share .pb-share-label {
    font-weight: 600 !important;
    color: rgba(255, 255, 255, 0.7) !important;
    font-size: 13px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    margin-right: 4px !important;
}

#pb-social-share .pb-share-btn {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 7px !important;
    padding: 9px 16px !important;
    background: rgba(42, 147, 193, 0.12) !important;
    border: 1px solid rgba(42, 147, 193, 0.35) !important;
    border-radius: 6px !important;
    color: #2a93c1 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    text-decoration: none !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

#pb-social-share .pb-share-btn svg {
    width: 15px !important;
    height: 15px !important;
    fill: currentColor !important;
    flex-shrink: 0 !important;
}

#pb-social-share .pb-share-btn:hover {
    background: #f1420b !important;
    border-color: #f1420b !important;
    color: #ffffff !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(241, 66, 11, 0.3) !important;
}

#pb-social-share .pb-share-btn.pb-copy-done {
    background: rgba(42, 193, 100, 0.15) !important;
    border-color: rgba(42, 193, 100, 0.5) !important;
    color: #2ac164 !important;
}

/* ----- 2. RESTORE THEME-NATIVE .post-social-sharing ----- */
/* Override the Additional CSS "FIX 2: REMOVE SOCIAL SHARE BAR" rule.
   Using maximum specificity + !important to win the load-order battle.
   The Additional CSS hides these with display:none !important — we beat
   it with equal or higher specificity loaded AFTER via wp_head priority 30. */
html body.single-post .post-social-sharing,
html body.single-post div.post-social-sharing {
    display: flex !important;
    gap: 10px !important;
    flex-wrap: wrap !important;
    visibility: visible !important;
    opacity: 1 !important;
    height: auto !important;
    overflow: visible !important;
}

html body.single-post .post-social-sharing ul {
    display: flex !important;
    gap: 10px !important;
    flex-wrap: wrap !important;
    list-style: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

html body.single-post .post-social-sharing ul li {
    display: flex !important;
    visibility: visible !important;
}

html body.single-post .post-social-sharing a {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 40px !important;
    height: 40px !important;
    background: rgba(42, 147, 193, 0.15) !important;
    border: 1px solid rgba(42, 147, 193, 0.3) !important;
    border-radius: 50% !important;
    color: #2a93c1 !important;
    font-size: 16px !important;
    text-decoration: none !important;
    transition: all 0.2s ease !important;
    visibility: visible !important;
    opacity: 1 !important;
}

html body.single-post .post-social-sharing a:hover {
    background: #f1420b !important;
    border-color: #f1420b !important;
    color: #ffffff !important;
    transform: scale(1.08) !important;
}
</style>
    <?php
}, 30 );

// JS: inject the custom pb-social-share bar before .blog-cta-block
add_action( 'wp_footer', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<script id="pb-social-share-js">
(function() {
    'use strict';

    function buildShareBar() {
        var url   = encodeURIComponent(window.location.href);
        var title = encodeURIComponent(document.title);
        var rawUrl = window.location.href;

        var liHTML = '<span class="pb-share-label">Share:</span>';

        // LinkedIn
        liHTML += '<a href="https://www.linkedin.com/sharing/share-offsite/?url=' + url + '" target="_blank" rel="nofollow noopener" class="pb-share-btn" aria-label="Share on LinkedIn">'
            + '<svg viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>'
            + 'LinkedIn</a>';

        // X / Twitter
        liHTML += '<a href="https://twitter.com/intent/tweet?url=' + url + '&text=' + title + '" target="_blank" rel="nofollow noopener" class="pb-share-btn" aria-label="Share on X">'
            + '<svg viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>'
            + 'X</a>';

        // Email
        liHTML += '<a href="mailto:?subject=' + title + '&body=' + url + '" class="pb-share-btn" aria-label="Share via Email">'
            + '<svg viewBox="0 0 24 24"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>'
            + 'Email</a>';

        // Copy Link
        liHTML += '<button class="pb-share-btn" id="pb-copy-link-btn" aria-label="Copy link to clipboard">'
            + '<svg viewBox="0 0 24 24"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>'
            + 'Copy Link</button>';

        var bar = document.createElement('div');
        bar.id = 'pb-social-share';
        bar.innerHTML = liHTML;

        // Copy Link click handler
        var copyBtn = bar.querySelector('#pb-copy-link-btn');
        if (copyBtn) {
            copyBtn.addEventListener('click', function() {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(rawUrl).then(function() {
                        copyBtn.textContent = 'Copied!';
                        copyBtn.classList.add('pb-copy-done');
                        setTimeout(function() {
                            copyBtn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>Copy Link';
                            copyBtn.classList.remove('pb-copy-done');
                        }, 2000);
                    });
                } else {
                    // Fallback for older browsers
                    var ta = document.createElement('textarea');
                    ta.value = rawUrl;
                    ta.style.position = 'fixed';
                    ta.style.opacity = '0';
                    document.body.appendChild(ta);
                    ta.focus();
                    ta.select();
                    try {
                        document.execCommand('copy');
                        copyBtn.textContent = 'Copied!';
                        copyBtn.classList.add('pb-copy-done');
                        setTimeout(function() {
                            copyBtn.innerHTML = '<svg viewBox="0 0 24 24"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>Copy Link';
                            copyBtn.classList.remove('pb-copy-done');
                        }, 2000);
                    } catch(err) {}
                    document.body.removeChild(ta);
                }
            });
        }

        return bar;
    }

    function insertShareBar() {
        // Only on single blog post pages
        if (!document.body.classList.contains('single-post')) {
            return;
        }

        // Don't insert twice
        if (document.getElementById('pb-social-share')) {
            return;
        }

        var shareBar = buildShareBar();

        // Try to insert before .blog-cta-block (same strategy as transparency section)
        var ctaBlock = document.querySelector('.blog-cta-block');
        if (ctaBlock && ctaBlock.parentNode) {
            ctaBlock.parentNode.insertBefore(shareBar, ctaBlock);
            return;
        }

        // Fallback: append to .entry-content or .post-content
        var entryContent = document.querySelector('.entry-content') || document.querySelector('.post-content');
        if (entryContent) {
            entryContent.appendChild(shareBar);
            return;
        }

        // Last resort: find the main post article
        var article = document.querySelector('article.post') || document.querySelector('article');
        if (article) {
            article.appendChild(shareBar);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', insertShareBar);
    } else {
        insertShareBar();
    }
})();
</script>
    <?php
}, 25 );

// ============================================================
// AETHER FOOTER CREDIT BAR (v4.5.0) + WHY PUREBRAIN LINK (v4.6.0)
// Fixed-position bar on ALL pages: "Built by AETHER (an AI) for..."
// v4.6.0: Added "Why Choose PureBrain?" link in footer bar
// ============================================================

add_action( 'wp_footer', function () {
    ?>
<style id="pb-aether-footer-v460">
/* Aether footer credit bar - fixed bottom, full width, all pages */
#pb-aether-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    height: 36px;
    background-color: #080a12;
    border-top: 1px solid rgba(255,255,255,0.06);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1;
    color: #6b7280;
    padding: 0 16px;
    box-sizing: border-box;
    letter-spacing: 0.02em;
    gap: 0;
    flex-wrap: wrap;
}
#pb-aether-footer a {
    text-decoration: none !important;
    transition: color 0.15s ease;
}
#pb-aether-footer a:hover {
    background: none !important;
}
#pb-aether-footer .pb-footer-aether {
    font-weight: 700;
    color: #ffffff;
}
#pb-aether-footer .pb-footer-purebrain {
    color: #f1420b;
}
#pb-aether-footer .pb-footer-blue {
    color: #2a93c1;
}
#pb-aether-footer .pb-footer-blue:hover {
    color: #f1420b !important;
    background: none !important;
}
#pb-aether-footer .pb-footer-sep {
    color: rgba(255,255,255,0.15);
    margin: 0 8px;
}
#pb-aether-footer .pb-footer-why {
    color: #2a93c1;
    font-weight: 600;
}
#pb-aether-footer .pb-footer-why:hover {
    color: #f1420b !important;
    background: none !important;
}
/* Push body content up so footer doesn't overlap */
body {
    padding-bottom: 36px !important;
}
</style>
<div id="pb-aether-footer">
    Built by&nbsp;<span class="pb-footer-aether">AETHER</span>&nbsp;(an AI) for&nbsp;<a href="https://purebrain.ai" target="_blank" rel="noopener" class="pb-footer-purebrain">PureBrain.ai</a>,&nbsp;<a href="https://puremarketing.ai" target="_blank" rel="noopener" class="pb-footer-blue">PureMarketing.ai</a>&nbsp;&amp;&nbsp;<a href="https://puretechnology.nyc" target="_blank" rel="noopener" class="pb-footer-blue">PureTechnology.ai</a><span class="pb-footer-sep">|</span><a href="https://purebrain.ai/why-purebrain/" rel="noopener" class="pb-footer-why">Why Choose PureBrain?</a>
</div>
    <?php
}, 100 );

// ============================================================
// n1) CHATBOX BYPASS OVERRIDE (v4.6.9)
//     Uses DOCUMENT-LEVEL CAPTURING event listeners to intercept
//     form submission BEFORE the chatbox's DOMContentLoaded closure.
//     handleSubmit is NOT global (it's inside Elementor's DOMContentLoaded
//     closure), so we can't override it. Instead we intercept events at
//     the document level in the CAPTURING phase, which fires before any
//     target/bubble phase handlers on the form.
//     Pages: 688 (sandbox), 689 (pay-test-2), 11 (homepage)
//     Also supports URL param: ?bypass=true for instant bypass on load.
// ============================================================
add_action( 'wp_footer', function () {
    if ( ! is_page( array( 688, 689, 11 ) ) ) {
        return;
    }
    ?>
<script id="pb-bypass-override">
(function() {
    'use strict';
    var BYPASS_DONE = false;

    function isBypassCode(value) {
        if (!value) return false;
        var v = value.trim().toLowerCase();
        return v === 'pb-full-bypass'
            || v.indexOf('bypass everything') !== -1
            || v.indexOf("i'm jared") !== -1;
    }

    function escapeHtml(text) {
        var d = document.createElement('div');
        d.textContent = text;
        return d.innerHTML;
    }

    function executeBypass(inputValue) {
        if (BYPASS_DONE) return;
        BYPASS_DONE = true;

        /* 1. Activate chat UI (hide Begin Awakening, show input) */
        var chatInitial = document.getElementById('chatInitial')
                       || document.querySelector('.chat-initial');
        if (chatInitial) chatInitial.style.display = 'none';

        var chatInput = document.getElementById('chatInput');
        if (chatInput) chatInput.classList.add('active');

        var indicator = document.querySelector('.chat-header__indicator');
        if (indicator) {
            indicator.classList.remove('chat-header__indicator--waiting');
            indicator.classList.add('chat-header__indicator--online');
        }

        /* 2. Clear input field */
        var userInput = document.getElementById('userInput');
        if (userInput) {
            userInput.value = '';
            userInput.disabled = false;
        }

        /* 3. Inject messages into chat display */
        var chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            /* User message */
            var userMsg = document.createElement('div');
            userMsg.className = 'message message--user';
            userMsg.innerHTML = '<div class="message__bubble">'
                + escapeHtml(inputValue || 'pb-full-bypass') + '</div>';
            chatMessages.appendChild(userMsg);

            /* AI bypass confirmation */
            var aiMsg = document.createElement('div');
            aiMsg.className = 'message message--ai';
            aiMsg.innerHTML = '<div class="message__bubble">'
                + '<strong>Bypass activated.</strong> I\'m <strong>Nova</strong>. '
                + 'All conversation steps skipped. Pricing revealed below.'
                + '</div>';
            chatMessages.appendChild(aiMsg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        /* 4. Update AI name displays */
        var nameEls = document.querySelectorAll(
            '.ai-name-dynamic, .chat-header__name, [data-ai-name]'
        );
        nameEls.forEach(function(el) {
            el.textContent = 'Nova';
        });
        var chatName = document.getElementById('chatName');
        if (chatName) chatName.textContent = 'Nova';
        var chatStatus = document.getElementById('chatStatus');
        if (chatStatus) chatStatus.textContent = 'Online';

        /* 5. Reveal pricing section */
        var pricing = document.getElementById('pricing');
        if (pricing) {
            pricing.classList.add('active');
            pricing.style.display = 'block';
            pricing.style.opacity = '1';
            pricing.style.visibility = 'visible';
            pricing.style.maxHeight = 'none';
            pricing.style.overflow = 'visible';
        }

        /* 6. Update Discover button with Nova name */
        var seeWhatBtn = document.getElementById('seeWhatBtn');
        if (seeWhatBtn) {
            seeWhatBtn.textContent = 'Discover What Nova Can Do';
        }

        /* 7. Scroll to pricing after short delay */
        setTimeout(function() {
            if (pricing) {
                pricing.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }, 1000);

        console.log('[PB-BYPASS] Bypass activated — Nova ready, pricing revealed');
    }

    /*
     * METHOD 1: Intercept form SUBMIT at document level (capturing phase).
     * Capturing phase on document fires BEFORE the form's own handlers
     * (which are in the target/bubble phase). stopPropagation prevents
     * the event from ever reaching the form.
     */
    document.addEventListener('submit', function(e) {
        var userInput = document.getElementById('userInput');
        if (!userInput) return;
        /* Only intercept the chatbox form, not other forms on the page */
        var form = e.target;
        if (!form || !form.contains(userInput)) return;

        var val = userInput.value;
        if (isBypassCode(val)) {
            e.preventDefault();
            e.stopPropagation();
            executeBypass(val.trim());
        }
    }, true); /* true = capturing phase */

    /*
     * METHOD 2: Intercept ENTER keydown at document level (capturing phase).
     * Fires before the input element's own keydown handlers.
     * Also prevents the browser's default action (form submission via Enter).
     */
    document.addEventListener('keydown', function(e) {
        if (e.key !== 'Enter' && e.keyCode !== 13) return;
        var target = e.target;
        if (!target || target.id !== 'userInput') return;

        var val = target.value;
        if (isBypassCode(val)) {
            e.preventDefault();
            e.stopPropagation();
            executeBypass(val.trim());
        }
    }, true); /* true = capturing phase */

    /*
     * METHOD 3: URL parameter bypass — ?bypass=true triggers instantly.
     * Useful for Jared's quick testing without typing anything.
     */
    if (window.location.search.indexOf('bypass=true') !== -1) {
        function autoBypass() {
            var chatInitial = document.getElementById('chatInitial');
            if (!chatInitial) {
                setTimeout(autoBypass, 500);
                return;
            }
            executeBypass('Auto-bypass via URL parameter');
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                setTimeout(autoBypass, 1000);
            });
        } else {
            setTimeout(autoBypass, 1000);
        }
    }
})();
</script>
    <?php
}, 999 );

// ============================================================
// n1b) CHATBOX DISCOVER BUTTON UX FIX (v4.7.3)
//      Fixes three things on all chatbox pages:
//      1. Button text updated to "Click to discover what [AI NAME] can do"
//      2. Input disabled when discover button appears
//      3. Input re-enabled when discover button is clicked
//      4. Session timer overridden from 15min to 30min
//      Uses MutationObserver to catch dynamically-added discover button.
//      Pages: 688, 689, 11, 439, 468
// ============================================================
add_action( 'wp_footer', function () {
    if ( ! is_page( array( 688, 689, 11, 439, 468 ) ) ) {
        return;
    }
    ?>
<script id="pb-discover-btn-fix">
(function() {
    'use strict';

    /* ---- Fix 1: Override session timer from 15min to 30min ---- */
    function fix30MinTimer() {
        var timerEl = document.querySelector('.awakening-timer__time');
        if (!timerEl) return;
        /* Find the countdown interval and reset it */
        /* Approach: override the displayed time by patching the countdown */
        var totalSeconds = 30 * 60; /* 30 minutes */
        /* If timer shows less than 15:00, it already started at 15min. Recalculate. */
        var parts = timerEl.textContent.split(':');
        if (parts.length === 2) {
            var currentMin = parseInt(parts[0], 10);
            var currentSec = parseInt(parts[1], 10);
            var elapsed15 = (15 * 60) - (currentMin * 60 + currentSec);
            /* Recalculate based on 30min total */
            var remaining30 = (30 * 60) - elapsed15;
            if (remaining30 > 0) {
                /* Start our own countdown that overrides the display */
                clearInterval(window._pb30Timer);
                window._pb30Timer = setInterval(function() {
                    remaining30--;
                    if (remaining30 <= 0) {
                        clearInterval(window._pb30Timer);
                        remaining30 = 0;
                    }
                    var m = Math.floor(remaining30 / 60);
                    var s = remaining30 % 60;
                    timerEl.textContent = (m < 10 ? '0' + m : m) + ':' + (s < 10 ? '0' + s : s);
                }, 1000);
            }
        }
    }

    /* ---- Fix 2: Watch for discover button and manage input ---- */
    function setupDiscoverBtnWatch() {
        var chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) {
            setTimeout(setupDiscoverBtnWatch, 500);
            return;
        }

        new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType !== 1) return;
                    var btn = null;
                    if (node.id === 'seeWhatBtn') btn = node;
                    else if (node.querySelector) btn = node.querySelector('#seeWhatBtn');
                    if (!btn) return;

                    /* Update button text */
                    var aiName = (typeof state !== 'undefined' && state.aiName) ? state.aiName : 'Your PURE BRAIN';
                    btn.innerHTML = '<span class="btn-icon">\u26A1</span> Click to discover what ' + aiName + ' can do';

                    /* Disable input */
                    var userInput = document.getElementById('userInput');
                    if (userInput) {
                        userInput.disabled = true;
                        userInput.placeholder = 'Click the button above \u2191';
                    }

                    /* Fix timer when discover button appears */
                    setTimeout(fix30MinTimer, 500);
                });
            });
        }).observe(chatMessages, { childList: true, subtree: true });
    }

    /* ---- Fix 3: Patch showPersonalizedCapabilities to re-enable input ---- */
    function patchShowCapabilities() {
        if (typeof window.showPersonalizedCapabilities === 'function' && !window._pbDiscoverPatched) {
            var orig = window.showPersonalizedCapabilities;
            window.showPersonalizedCapabilities = function() {
                /* Re-enable input */
                var userInput = document.getElementById('userInput');
                if (userInput) {
                    userInput.disabled = false;
                    userInput.placeholder = 'Type your response...';
                }
                return orig.apply(this, arguments);
            };
            window._pbDiscoverPatched = true;
        }
        if (!window._pbDiscoverPatched) {
            setTimeout(patchShowCapabilities, 500);
        }
    }

    /* ---- Initialize ---- */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setupDiscoverBtnWatch();
            patchShowCapabilities();
        });
    } else {
        setupDiscoverBtnWatch();
        patchShowCapabilities();
    }
})();
</script>
    <?php
}, 998 );

// ============================================================
// n2) SESSION TIMER FIX (v4.6.9)
//     Problem: The session timer (#sessionTimer) shows immediately when
//     the AI declares its name (via name pattern detection in displayAIMessages).
//     Jared wants it to ONLY appear AFTER:
//       1. Naming is complete
//       2. The "Discover" button (#seeWhatBtn) has been clicked
//     Fix: CSS override hides .session-timer.active, and only reveals it
//     when the Discover button is clicked (adds .pb-timer-ready class).
//     Pages: 688 (sandbox), 689 (pay-test-2), 11 (homepage), 439 (pay-test), 468 (pay-test-sandbox)
// ============================================================
add_action( 'wp_head', function () {
    if ( ! is_page( array( 688, 689, 11, 439, 468 ) ) ) {
        return;
    }
    ?>
<style id="pb-session-timer-fix">
/* Override: keep timer hidden even when .active is added by the chatbox JS */
.session-timer.active { display: none !important; }
/* Only show when Discover button has been clicked (plugin adds .pb-timer-ready) */
.session-timer.active.pb-timer-ready { display: flex !important; }
/* Also hide the identity-saved note until timer is ready */
#sessionNote { display: none !important; }
#sessionNote.pb-note-ready { display: block !important; }
</style>
    <?php
}, 999 );

add_action( 'wp_footer', function () {
    if ( ! is_page( array( 688, 689, 11, 439, 468 ) ) ) {
        return;
    }
    ?>
<script id="pb-session-timer-fix-js">
(function() {
    'use strict';
    /*
     * Listen for clicks on the Discover button (#seeWhatBtn).
     * When clicked, reveal the session timer and identity-saved note.
     * Uses event delegation so it works even if the button is added dynamically.
     */
    document.addEventListener('click', function(e) {
        var btn = e.target;
        /* Check if clicked element is the seeWhatBtn or a child of it */
        if (btn.id !== 'seeWhatBtn' && !btn.closest('#seeWhatBtn')) return;

        /* Reveal session timer */
        var timer = document.getElementById('sessionTimer');
        if (timer) timer.classList.add('pb-timer-ready');

        /* Reveal identity-saved note */
        var note = document.getElementById('sessionNote');
        if (note) note.classList.add('pb-note-ready');
    });
})();
</script>
    <?php
}, 999 );

// ============================================================
// n3) PAYPAL BUTTON ROUTING FIX (v4.7.1)
//     ROOT CAUSE: The page has TWO definitions of openWaitlistModal:
//       1. PayPal SDK inline script sets window.openWaitlistModal = PayPal checkout
//       2. DOMContentLoaded callback OVERWRITES it back to waitlist form version
//     After DOMContentLoaded, openWaitlistModal = waitlist (WRONG).
//     But openPayPalCheckout = PayPal checkout (CORRECT, still intact).
//     FIX: After ALL DOMContentLoaded handlers, restore the PayPal version.
//     Pages: 688 (sandbox), 689 (pay-test-2), 11 (homepage)
// ============================================================
add_action( 'wp_footer', function () {
    if ( ! is_page( array( 688, 689, 11 ) ) ) {
        return;
    }
    ?>
<script id="pb-paypal-routing-fix">
(function(){
    /* Wait for DOMContentLoaded to finish, then fix the routing */
    function fixPayPalRouting() {
        /* openPayPalCheckout is the CORRECT PayPal SDK function */
        if (typeof window.openPayPalCheckout === 'function') {
            window.openWaitlistModal = window.openPayPalCheckout;
            window.openPayPalModal = window.openPayPalCheckout;
            console.log('[PB-FIX] PayPal routing restored: openWaitlistModal -> openPayPalCheckout');
        } else {
            console.warn('[PB-FIX] openPayPalCheckout not found, retrying...');
            /* Retry up to 5 times with increasing delays for slow SDK loads */
            if (!window._pbPayPalFixRetries) window._pbPayPalFixRetries = 0;
            window._pbPayPalFixRetries++;
            if (window._pbPayPalFixRetries < 6) {
                setTimeout(fixPayPalRouting, window._pbPayPalFixRetries * 500);
            }
        }
    }

    if (document.readyState === 'loading') {
        /* If still loading, wait for DOMContentLoaded then setTimeout(0) to run last */
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(fixPayPalRouting, 0);
        });
    } else {
        /* Already loaded - run with setTimeout(0) to yield to any pending handlers */
        setTimeout(fixPayPalRouting, 0);
    }
})();
</script>
    <?php
}, 1000 );

// ============================================================
// n4) PAYPAL SANDBOX ENVIRONMENT OVERRIDE (v4.7.2)
//     Page 688 (pay-test-sandbox-2) must use PayPal Sandbox environment
//     for safe testing without real charges.
//     - Replaces production SDK script with sandbox SDK
//     - Swaps client ID to sandbox credentials
//     - Uses createOrder (one-time capture) since sandbox plan IDs
//       don't exist yet (sandbox API credentials need updating)
//     Page 689 (pay-test-2) is NOT affected — stays production.
// ============================================================
add_action( 'wp_footer', function () {
    if ( ! is_page( 688 ) ) {
        return;
    }
    ?>
<script id="pb-sandbox-override">
(function(){
    var SANDBOX_CLIENT_ID = 'AYTFob05DoSn0ZeVtLJ05duKwFHOdAckHgkZ2UJhAXvfJlUXEYM_PFib3HbIuVgauxV_6clZ5FdPRYq_';
    var SANDBOX_SDK_URL = 'https://www.sandbox.paypal.com/sdk/js?client-id=' + SANDBOX_CLIENT_ID + '&currency=USD&intent=capture';

    function applySandboxOverride() {
        /* 1. Remove the production SDK script tag */
        var prodScript = document.querySelector('script[src*="www.paypal.com/sdk/js"]');
        if (prodScript) {
            prodScript.parentNode.removeChild(prodScript);
            console.log('[PB-SANDBOX] Removed production PayPal SDK');
        }

        /* 2. Clear any existing PayPal global */
        if (window.paypal) {
            delete window.paypal;
            console.log('[PB-SANDBOX] Cleared production PayPal global');
        }

        /* 3. Load sandbox SDK */
        var sandboxScript = document.createElement('script');
        sandboxScript.src = SANDBOX_SDK_URL;
        sandboxScript.onload = function() {
            console.log('[PB-SANDBOX] Sandbox PayPal SDK loaded');

            /* 4. Override openWaitlistModal/openPayPalCheckout with sandbox version */
            window.openWaitlistModal = function(tier) {
                var PRICES = {
                    Awakened: '79.00', Bonded: '149.00',
                    Partnered: '499.00', Unified: '999.00'
                };

                var canonicalTier = Object.keys(PRICES).find(function(t) {
                    return t.toLowerCase() === (tier || '').toLowerCase();
                });
                if (!canonicalTier) { canonicalTier = 'Bonded'; }

                var price = PRICES[canonicalTier];

                /* Show the PayPal modal */
                var modal = document.getElementById('pb-paypal-modal');
                if (modal) {
                    modal.style.display = 'block';
                    var title = modal.querySelector('.pb-paypal-modal__tier');
                    if (title) title.textContent = 'PURE BRAIN \u2014 ' + canonicalTier.toUpperCase();
                    var priceEl = modal.querySelector('.pb-paypal-modal__price');
                    if (priceEl) priceEl.innerHTML = '<span class="pb-paypal-modal__amount">$' + parseInt(price) + '</span><span class="pb-paypal-modal__period">/mo</span>';
                }

                /* Render sandbox PayPal buttons with createOrder (one-time capture) */
                var container = document.getElementById('pb-paypal-buttons-container');
                if (container) {
                    container.innerHTML = '';
                    try {
                        window.paypal.Buttons({
                            style: { layout: 'vertical', color: 'gold', shape: 'rect', label: 'pay', tagline: false },
                            createOrder: function(data, actions) {
                                return actions.order.create({
                                    purchase_units: [{
                                        description: 'Pure Brain \u2014 ' + canonicalTier + ' Plan (SANDBOX TEST)',
                                        custom_id: 'PB-SANDBOX-' + canonicalTier.toUpperCase(),
                                        amount: { currency_code: 'USD', value: price }
                                    }]
                                });
                            },
                            onApprove: function(data, actions) {
                                return actions.order.capture().then(function(details) {
                                    console.log('[PB-SANDBOX] Payment captured:', details);
                                    alert('SANDBOX TEST: Payment successful!\nOrder ID: ' + data.orderID + '\nPayer: ' + (details.payer && details.payer.email_address || 'test'));
                                });
                            },
                            onCancel: function() {
                                console.log('[PB-SANDBOX] Payment cancelled');
                            },
                            onError: function(err) {
                                console.error('[PB-SANDBOX] Error:', err);
                            }
                        }).render(container);
                        console.log('[PB-SANDBOX] Sandbox buttons rendered for ' + canonicalTier);
                    } catch(e) {
                        console.error('[PB-SANDBOX] Render error:', e);
                    }
                }
            };
            window.openPayPalCheckout = window.openWaitlistModal;
            window.openPayPalModal = window.openWaitlistModal;
            console.log('[PB-SANDBOX] Sandbox payment functions ready');
        };
        sandboxScript.onerror = function() {
            console.error('[PB-SANDBOX] Failed to load sandbox SDK');
        };
        document.head.appendChild(sandboxScript);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(applySandboxOverride, 100);
        });
    } else {
        setTimeout(applySandboxOverride, 100);
    }
})();
</script>
    <?php
}, 1001 );
