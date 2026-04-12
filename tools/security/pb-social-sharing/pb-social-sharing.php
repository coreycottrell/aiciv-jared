<?php
/**
 * Plugin Name: PureBrain Social Sharing
 * Plugin URI:  https://purebrain.ai
 * Description: Branded social sharing bar for single blog posts. Injects LinkedIn, X (Twitter), Email, and Copy Link buttons before .blog-cta-block. Also restores the theme-native .post-social-sharing element. Extracted from purebrain-security-plugin.php (Task 10 of 14).
 * Version:     1.0.0
 * Author:      Aether (AI) for Pure Technology
 * Author URI:  https://purebrain.ai
 * License:     Proprietary
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// Note: Extracted from purebrain-security-plugin.php (Task 10 of 14)
// Original section: p) SOCIAL SHARING BAR — GEO FIX 3 (v4.2.0)
// Source lines: 5336–5596 of purebrain-security-plugin.php

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
