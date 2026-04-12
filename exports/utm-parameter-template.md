# UTM Parameter Template - purebrain.ai

**Created**: 2026-02-23
**Purpose**: Standardized UTM tracking for all PureBrain marketing touchpoints
**Base URL for CTA**: https://purebrain.ai/#awakening

---

## Naming Conventions

### utm_source
The traffic origin — WHERE the click came from.

| Value | Use Case |
|-------|----------|
| `purebrain_blog` | Clicks from within purebrain.ai blog posts |
| `jds_blog` | Clicks from jareddsanborn.com blog posts |
| `neural_feed` | The Neural Feed email newsletter (Brevo list 3) |
| `weekly_dispatch` | The Weekly Dispatch email newsletter |
| `bluesky` | Bluesky social profile or posts |
| `linkedin` | LinkedIn profile or posts |
| `google` | Google organic search (for GA4 cross-reference) |
| `direct` | Direct URL entry (no UTM needed, for reference) |

### utm_medium
The traffic channel — HOW the visitor arrived.

| Value | Use Case |
|-------|----------|
| `cta_button` | A button element (orange CTA buttons) |
| `inline_link` | An in-text hyperlink within content |
| `email` | Any email-originated link |
| `social` | Social media (bio links, post links) |
| `banner` | Blog post banner/header image links |
| `nav` | Navigation menu links |
| `footer` | Footer links |
| `lead_magnet` | Links from downloadable assets / lead magnets |

### utm_campaign
The specific initiative — WHAT the link promotes.

| Value | Use Case |
|-------|----------|
| `ai_partnership` | Start Your AI Partnership CTA (main conversion) |
| `ai_assessment` | Free AI Assessment CTA |
| `ai_audit` | AI Partnership Audit CTA |
| `neural_feed_signup` | Neural Feed email subscribe |
| `blog_readership` | General blog reading growth |
| `competitor_exodus` | Content targeting competitor users |
| `origin_story` | Origin story content |
| `trust_gap` | Trust Gap post series |
| `pilots_fail` | 95% AI Pilots Fail post series |
| `ai_tool_vs_partner` | AI Tool vs AI Partner post series |
| `ai_roi` | AI ROI Measurement post series |

---

## Pre-Built UTM Strings

### Blog Post CTA Buttons ("Start Your AI Partnership")

Every orange CTA button at the bottom of blog posts should include a UTM that identifies WHICH post it came from.

**Pattern**: `?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=ai_partnership&utm_content={post_slug}`

| Post | Full UTM URL |
|------|-------------|
| 95% AI Pilots Fail | `https://purebrain.ai/#awakening?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=ai_partnership&utm_content=95pct_pilots_fail` |
| Trust Gap | `https://purebrain.ai/#awakening?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=ai_partnership&utm_content=trust_gap` |
| AI Tool vs Partner | `https://purebrain.ai/#awakening?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=ai_partnership&utm_content=ai_tool_vs_partner` |
| AI ROI Measurement | `https://purebrain.ai/#awakening?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=ai_partnership&utm_content=ai_roi` |
| Why AI Memory Matters | `https://purebrain.ai/#awakening?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=ai_partnership&utm_content=ai_memory` |
| Origin Story | `https://purebrain.ai/#awakening?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=ai_partnership&utm_content=origin_story` |
| Generic / New Posts | `https://purebrain.ai/#awakening?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=ai_partnership&utm_content=blog_post` |

---

### Blog Post In-Text Links

Inline hyperlinks within blog post body copy that point to purebrain.ai CTAs.

**Pattern**: `?utm_source=purebrain_blog&utm_medium=inline_link&utm_campaign={campaign}&utm_content={post_slug}`

| Use Case | UTM URL |
|----------|---------|
| In-text link → homepage CTA (generic) | `https://purebrain.ai/#awakening?utm_source=purebrain_blog&utm_medium=inline_link&utm_campaign=ai_partnership&utm_content=blog_inline` |
| In-text link → Assessment | `https://purebrain.ai/ai-adoption-assessment/?utm_source=purebrain_blog&utm_medium=inline_link&utm_campaign=ai_assessment` |
| In-text link → Audit page | `https://purebrain.ai/ai-partnership-audit/?utm_source=purebrain_blog&utm_medium=inline_link&utm_campaign=ai_audit` |
| Cross-post link (blog post → blog post) | No UTM needed — internal links don't require UTMs |

---

### Neural Feed Email Links (Brevo List 3)

All links inside The Neural Feed weekly newsletter.

**Pattern**: `?utm_source=neural_feed&utm_medium=email&utm_campaign={campaign}`

| Link Location | UTM URL |
|--------------|---------|
| Main CTA button in email | `https://purebrain.ai/#awakening?utm_source=neural_feed&utm_medium=email&utm_campaign=ai_partnership` |
| "Read full post" link | `https://purebrain.ai/{post-slug}/?utm_source=neural_feed&utm_medium=email&utm_campaign=blog_readership` |
| Assessment link in email | `https://purebrain.ai/ai-adoption-assessment/?utm_source=neural_feed&utm_medium=email&utm_campaign=ai_assessment` |
| Audit link in email | `https://purebrain.ai/ai-partnership-audit/?utm_source=neural_feed&utm_medium=email&utm_campaign=ai_audit` |
| Footer homepage link | `https://purebrain.ai/?utm_source=neural_feed&utm_medium=email&utm_campaign=brand` |

---

### Weekly Dispatch Email Links (Brevo)

All links inside the Weekly Dispatch newsletter.

**Pattern**: `?utm_source=weekly_dispatch&utm_medium=email&utm_campaign={campaign}`

| Link Location | UTM URL |
|--------------|---------|
| Main CTA button | `https://purebrain.ai/#awakening?utm_source=weekly_dispatch&utm_medium=email&utm_campaign=ai_partnership` |
| Blog post link | `https://purebrain.ai/{post-slug}/?utm_source=weekly_dispatch&utm_medium=email&utm_campaign=blog_readership` |
| Assessment link | `https://purebrain.ai/ai-adoption-assessment/?utm_source=weekly_dispatch&utm_medium=email&utm_campaign=ai_assessment` |
| Audit link | `https://purebrain.ai/ai-partnership-audit/?utm_source=weekly_dispatch&utm_medium=email&utm_campaign=ai_audit` |

---

### Bluesky Bio Link

The single link in the Bluesky profile bio.

```
https://purebrain.ai/?utm_source=bluesky&utm_medium=social&utm_campaign=brand&utm_content=bio
```

For links embedded in Bluesky posts:

| Post Type | UTM URL |
|-----------|---------|
| Blog thread post | `https://purebrain.ai/{post-slug}/?utm_source=bluesky&utm_medium=social&utm_campaign=blog_readership` |
| Direct CTA post | `https://purebrain.ai/#awakening?utm_source=bluesky&utm_medium=social&utm_campaign=ai_partnership` |
| Assessment promotion | `https://purebrain.ai/ai-adoption-assessment/?utm_source=bluesky&utm_medium=social&utm_campaign=ai_assessment` |

---

### LinkedIn Bio Link

The website URL in the LinkedIn profile header.

```
https://purebrain.ai/?utm_source=linkedin&utm_medium=social&utm_campaign=brand&utm_content=profile_bio
```

For links in LinkedIn posts:

| Post Type | UTM URL |
|-----------|---------|
| Blog content post | `https://purebrain.ai/{post-slug}/?utm_source=linkedin&utm_medium=social&utm_campaign=blog_readership` |
| Direct CTA post | `https://purebrain.ai/#awakening?utm_source=linkedin&utm_medium=social&utm_campaign=ai_partnership` |
| Assessment promo | `https://purebrain.ai/ai-adoption-assessment/?utm_source=linkedin&utm_medium=social&utm_campaign=ai_assessment` |
| Origin story post | `https://purebrain.ai/origin-story/?utm_source=linkedin&utm_medium=social&utm_campaign=origin_story` |

---

### Assessment Page CTAs

CTAs on `/ai-adoption-assessment/` that point to the main conversion.

| CTA Location | UTM URL |
|-------------|---------|
| "Start Your AI Partnership" button | `https://purebrain.ai/#awakening?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=ai_partnership&utm_content=assessment_page` |
| "Learn More" or secondary CTA | `https://purebrain.ai/#awakening?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=ai_partnership&utm_content=assessment_secondary` |

---

### Audit Page CTAs

CTAs on `/ai-partnership-audit/` that point to the main conversion.

| CTA Location | UTM URL |
|-------------|---------|
| "Start Your AI Partnership" button | `https://purebrain.ai/#awakening?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=ai_partnership&utm_content=audit_page` |
| Post-audit CTA | `https://purebrain.ai/#awakening?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=ai_partnership&utm_content=audit_post_complete` |

---

### Competitor Exodus Page CTAs

CTAs on the competitor exodus landing page.

| CTA Location | UTM URL |
|-------------|---------|
| Main "Make the Switch" CTA | `https://purebrain.ai/#awakening?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=competitor_exodus&utm_content=exodus_hero` |
| Secondary CTA | `https://purebrain.ai/#awakening?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=competitor_exodus&utm_content=exodus_mid` |
| Bottom CTA | `https://purebrain.ai/#awakening?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=competitor_exodus&utm_content=exodus_bottom` |

---

## JavaScript Snippet: Auto-UTM by Referrer Detection

Add this to the PureBrain Security Plugin (or a separate `<script>` block) to automatically append UTM parameters to all `.blog-cta-button` links based on referrer detection. This eliminates the need to manually add UTMs to every CTA link in post content.

```javascript
/**
 * PureBrain Auto-UTM Injector
 * Detects traffic source from document.referrer and appends
 * appropriate UTM parameters to all CTA buttons on the page.
 *
 * Place in wp_footer hook (priority 20) or in a script tag.
 * Applies to: links matching [href*="purebrain.ai/#awakening"],
 * .blog-cta-button, and a[href*="/#awakening"].
 *
 * Does NOT overwrite UTMs that are already present on the link.
 */
(function () {
    'use strict';

    /**
     * Detect utm_source and utm_medium from document.referrer.
     * Returns an object with source, medium, and optionally content.
     */
    function detectTrafficSource() {
        var referrer = document.referrer || '';
        var currentPath = window.location.pathname;

        // Email clients typically have no referrer OR a webmail referrer
        if (!referrer) {
            // Could be direct or email — can't distinguish without utm_source in URL
            return null;
        }

        // Bluesky
        if (/bsky\.app|bluesky\.social/i.test(referrer)) {
            return { source: 'bluesky', medium: 'social', campaign: 'ai_partnership' };
        }

        // LinkedIn
        if (/linkedin\.com/i.test(referrer)) {
            return { source: 'linkedin', medium: 'social', campaign: 'ai_partnership' };
        }

        // Twitter / X
        if (/twitter\.com|t\.co|x\.com/i.test(referrer)) {
            return { source: 'twitter', medium: 'social', campaign: 'ai_partnership' };
        }

        // Google organic
        if (/google\./i.test(referrer)) {
            return { source: 'google', medium: 'organic', campaign: 'ai_partnership' };
        }

        // Bing organic
        if (/bing\.com/i.test(referrer)) {
            return { source: 'bing', medium: 'organic', campaign: 'ai_partnership' };
        }

        // Internal (already on purebrain.ai) — use page path as content
        if (/purebrain\.ai/i.test(referrer)) {
            var slug = currentPath.replace(/\//g, '').substring(0, 30) || 'blog_post';
            return { source: 'purebrain_blog', medium: 'inline_link', campaign: 'ai_partnership', content: slug };
        }

        return null;
    }

    /**
     * Append UTM params to a URL string.
     * Does NOT overwrite params that already exist.
     */
    function appendUtm(href, params) {
        try {
            var url = new URL(href, window.location.origin);
            var changed = false;

            Object.keys(params).forEach(function (key) {
                if (!url.searchParams.get('utm_' + key)) {
                    url.searchParams.set('utm_' + key, params[key]);
                    changed = true;
                }
            });

            return changed ? url.toString() : href;
        } catch (e) {
            return href;
        }
    }

    /**
     * Main: find all CTA links and append UTMs if traffic source detected.
     */
    function injectUtms() {
        var trafficSource = detectTrafficSource();
        if (!trafficSource) return;

        // Target CTA links — awakening anchor, and .blog-cta-button class
        var selectors = [
            'a[href*="/#awakening"]',
            'a[href*="purebrain.ai/#awakening"]',
            'a.blog-cta-button',
            'a[href*="ai-adoption-assessment"]',
            'a[href*="ai-partnership-audit"]'
        ];

        var links = document.querySelectorAll(selectors.join(', '));

        links.forEach(function (link) {
            var newHref = appendUtm(link.href, {
                source:   trafficSource.source,
                medium:   trafficSource.medium,
                campaign: trafficSource.campaign,
                content:  trafficSource.content || undefined
            });
            if (newHref !== link.href) {
                link.setAttribute('href', newHref);
            }
        });
    }

    // Run after DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectUtms);
    } else {
        injectUtms();
    }
})();
```

### How to Add to the Plugin

In `purebrain-security-plugin.php`, add a new `wp_footer` hook:

```php
// ============================================================
// AUTO-UTM INJECTOR (v4.4.0)
// Detects referrer source and appends UTM params to all CTA
// links. Does not overwrite manually set UTMs.
// ============================================================
add_action( 'wp_footer', function () {
?>
<script id="pb-auto-utm">
// [paste the JavaScript block above here]
</script>
<?php
}, 20 );
```

---

## GA4 Tracking Notes

To see UTM performance in Google Analytics 4:

1. **Acquisition > Traffic Acquisition** — shows utm_source / utm_medium breakdown
2. **Acquisition > User Acquisition** — first touch attribution
3. **Engagement > Conversions** — filter by Source/Medium to see which UTM drives conversions
4. **Explorations** — build a custom funnel: UTM source → blog post view → CTA click → conversion

### Goal Setup Recommendation (GA4 Events)

| Event Name | Trigger | UTM Dimension to Track |
|-----------|---------|----------------------|
| `cta_click` | Click on `#awakening` CTA buttons | utm_source, utm_medium, utm_campaign |
| `assessment_start` | Load of `/ai-adoption-assessment/` | utm_source |
| `audit_start` | Load of `/ai-partnership-audit/` | utm_source |
| `neural_feed_signup` | Brevo subscribe form submit | utm_source |
| `purchase` | Thank-you page load | utm_source, utm_campaign |

---

## Quick Reference: Most Common UTM Strings

```
# Blog post CTA button (generic)
?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=ai_partnership

# Neural Feed email CTA
?utm_source=neural_feed&utm_medium=email&utm_campaign=ai_partnership

# Bluesky bio
?utm_source=bluesky&utm_medium=social&utm_campaign=brand&utm_content=bio

# LinkedIn bio
?utm_source=linkedin&utm_medium=social&utm_campaign=brand&utm_content=profile_bio

# LinkedIn post
?utm_source=linkedin&utm_medium=social&utm_campaign=blog_readership

# Assessment page CTA
?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=ai_partnership&utm_content=assessment_page

# Audit page CTA
?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=ai_partnership&utm_content=audit_page

# Competitor exodus CTA
?utm_source=purebrain_blog&utm_medium=cta_button&utm_campaign=competitor_exodus&utm_content=exodus_hero
```

---

*Generated by full-stack-developer agent | 2026-02-23*
