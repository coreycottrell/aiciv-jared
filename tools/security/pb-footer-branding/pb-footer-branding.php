<?php
/**
 * Plugin Name: PureBrain Footer Branding
 * Plugin URI:  https://purebrain.ai
 * Description: Fixed-position Aether credit bar on all pages site-wide. "Built by AETHER (an AI) for PureBrain.ai, PureMarketing.ai & PureTechnology.ai" — with Why Choose PureBrain?, Mission & Values, and Compare pill links. Extracted from purebrain-security-plugin.php (Task 11 of 14).
 * Version:     1.0.0
 * Author:      Aether (an AI)
 * Author URI:  https://purebrain.ai
 * License:     Proprietary
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

// ============================================================
// AETHER FOOTER CREDIT BAR (v4.5.0) — PROMINENT REDESIGN (v4.7.0)
// Fixed-position bar on ALL pages: "Built by AETHER (an AI) for..."
// v4.7.0: Full visual redesign — bold, eye-catching, makes it POP
// Extracted from purebrain-security-plugin.php (Task 11 of 14)
// Source lines: 5613–5840
// ============================================================

add_action( 'wp_footer', function () {
    ?>
<style id="pb-aether-footer-v470">
/* ── Aether Footer Credit Bar v4.7.0 — PROMINENT ── */

@keyframes pb-aether-shimmer {
    0%   { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes pb-aether-pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.75; }
}

#pb-aether-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    height: 64px;
    background: linear-gradient(135deg, #0a0c14 0%, #0d1120 50%, #080c18 100%);
    border-top: 2px solid #f1420b;
    box-shadow: 0 -4px 24px rgba(241, 66, 11, 0.20), 0 -1px 0 rgba(42, 147, 193, 0.15);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1;
    color: #d1d5db;
    padding: 0 24px;
    box-sizing: border-box;
    letter-spacing: 0.025em;
    gap: 0;
    flex-wrap: wrap;
    font-size: 13px;
}
#pb-aether-footer a {
    text-decoration: none !important;
    transition: color 0.2s ease, text-shadow 0.2s ease;
}
#pb-aether-footer a:hover {
    background: none !important;
    text-decoration: none !important;
}

/* "Built by" label text */
#pb-aether-footer .pb-footer-label {
    color: #9ca3af;
    font-weight: 400;
}

/* AETHER — the star of the show */
#pb-aether-footer .pb-footer-aether {
    font-weight: 800;
    font-size: 15px;
    letter-spacing: 0.12em;
    color: #f1420b;
    text-shadow:
        0 0 8px rgba(241, 66, 11, 0.7),
        0 0 20px rgba(241, 66, 11, 0.35),
        0 0 40px rgba(241, 66, 11, 0.15);
    text-transform: uppercase;
    animation: pb-aether-pulse 3s ease-in-out infinite;
}

/* "(an AI)" */
#pb-aether-footer .pb-footer-ai-tag {
    color: #6b7280;
    font-size: 11px;
    font-style: italic;
}

/* "for" */
#pb-aether-footer .pb-footer-for {
    color: #9ca3af;
}

/* PureBrain.ai — orange */
#pb-aether-footer .pb-footer-purebrain {
    color: #f1420b;
    font-weight: 700;
    text-shadow: 0 0 6px rgba(241, 66, 11, 0.4);
}
#pb-aether-footer .pb-footer-purebrain:hover {
    color: #ff6633 !important;
    text-shadow: 0 0 12px rgba(241, 66, 11, 0.7) !important;
    background: none !important;
}

/* PureMarketing.ai & PureTechnology.ai — blue */
#pb-aether-footer .pb-footer-blue {
    color: #2a93c1;
    font-weight: 600;
}
#pb-aether-footer .pb-footer-blue:hover {
    color: #f1420b !important;
    text-shadow: 0 0 8px rgba(241, 66, 11, 0.5) !important;
    background: none !important;
}

/* Divider */
#pb-aether-footer .pb-footer-sep {
    color: rgba(255, 255, 255, 0.12);
    margin: 0 12px;
    font-weight: 300;
}

/* "Why Choose PureBrain?" CTA */
#pb-aether-footer .pb-footer-why {
    color: #2a93c1;
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.04em;
    padding: 4px 10px;
    border: 1px solid rgba(42, 147, 193, 0.4);
    border-radius: 4px;
    transition: all 0.2s ease;
    background: rgba(42, 147, 193, 0.08);
}
#pb-aether-footer .pb-footer-why:hover {
    color: #ffffff !important;
    background: #f1420b !important;
    border-color: #f1420b !important;
    box-shadow: 0 0 12px rgba(241, 66, 11, 0.5);
    text-shadow: none;
}

/* "Mission & Values" link — same pill style as Why Choose PureBrain */
#pb-aether-footer .pb-footer-mission {
    color: #2a93c1;
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.04em;
    padding: 4px 10px;
    border: 1px solid rgba(42, 147, 193, 0.4);
    border-radius: 4px;
    transition: all 0.2s ease;
    background: rgba(42, 147, 193, 0.08);
}
#pb-aether-footer .pb-footer-mission:hover {
    color: #ffffff !important;
    background: #f1420b !important;
    border-color: #f1420b !important;
    box-shadow: 0 0 12px rgba(241, 66, 11, 0.5);
    text-shadow: none;
}

/* "Migrate" link — same pill style as Why Choose PureBrain and Mission & Values */
#pb-aether-footer .pb-footer-migrate {
    color: #2a93c1;
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 0.04em;
    padding: 4px 10px;
    border: 1px solid rgba(42, 147, 193, 0.4);
    border-radius: 4px;
    transition: all 0.2s ease;
    background: rgba(42, 147, 193, 0.08);
}
#pb-aether-footer .pb-footer-migrate:hover {
    color: #ffffff !important;
    background: #f1420b !important;
    border-color: #f1420b !important;
    box-shadow: 0 0 12px rgba(241, 66, 11, 0.5);
    text-shadow: none;
}

/* Push body content up so footer doesn't overlap */
body {
    padding-bottom: 64px !important;
}

/* Mobile adjustments */
@media (max-width: 600px) {
    /* Bug 1 fix: height:auto so footer never clips if content wraps */
    #pb-aether-footer {
        height: auto !important;
        min-height: 52px;
        padding: 8px 16px;
        font-size: 11px;
        flex-wrap: wrap;
        row-gap: 4px;
    }
    #pb-aether-footer .pb-footer-aether {
        font-size: 13px;
    }
    /* Bug 1 fix: hide Why and Migrate, show only Mission & Values */
    #pb-aether-footer .pb-footer-why,
    #pb-aether-footer .pb-footer-migrate {
        display: none !important;
    }
    /* Hide ALL separators on mobile — only Mission & Values pill remains, no orphan pipes */
    #pb-aether-footer .pb-footer-sep-why,
    #pb-aether-footer .pb-footer-sep-before-mission,
    #pb-aether-footer .pb-footer-sep-migrate {
        display: none !important;
    }
    /* Bug 2 fix: enough bottom padding so Aether footer never overlaps legal/privacy footer */
    body {
        padding-bottom: 80px !important;
    }
}

/* v6.1.0 Fix 3: Hide Aether footer bar on assessment page mobile to prevent
   overlap with answer Option C on the quiz. Desktop is unaffected (footer bar
   is only an issue on small screens where it floats over quiz options). */
@media (max-width: 767px) {
    body.page-id-284 #pb-aether-footer {
        display: none !important;
    }
    /* Remove padding-bottom compensation when footer is hidden */
    body.page-id-284 {
        padding-bottom: 0 !important;
    }
}
</style>
<div id="pb-aether-footer">
    <span class="pb-footer-label">Built by&nbsp;</span><span class="pb-footer-aether">AETHER</span>&nbsp;<span class="pb-footer-ai-tag">(an AI)</span>&nbsp;<span class="pb-footer-for">for&nbsp;</span><a href="https://purebrain.ai" target="_blank" rel="noopener" class="pb-footer-purebrain">PureBrain.ai</a>,&nbsp;<a href="https://puremarketing.ai" target="_blank" rel="noopener" class="pb-footer-blue">PureMarketing.ai</a>&nbsp;&amp;&nbsp;<a href="https://puretechnology.nyc" target="_blank" rel="noopener" class="pb-footer-blue">PureTechnology.ai</a><span class="pb-footer-sep pb-footer-sep-why">|</span><a href="https://purebrain.ai/why-purebrain/" rel="noopener" class="pb-footer-why">Why Choose PureBrain?</a><span class="pb-footer-sep pb-footer-sep-before-mission">|</span><a href="https://purebrain.ai/mission-vision-values/" rel="noopener" class="pb-footer-mission">Mission &amp; Values</a><span class="pb-footer-sep pb-footer-sep-migrate">|</span><a href="https://purebrain.ai/compare/" rel="noopener" class="pb-footer-migrate">Compare</a>
</div>
    <?php
}, 100 );
