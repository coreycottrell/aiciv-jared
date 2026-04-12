#!/usr/bin/env python3
"""
Build purebrain-security-plugin-v481.php from v480.

Changes made:
1. Update plugin version header: 4.7.9 -> 4.8.1
2. Add v4.8.1 GA4 entry to Description and Changelog
3. Update CSP connect-src: add www.google-analytics.com + www.googletagmanager.com
4. Add GA4 gtag.js wp_head hook (priority 1, ALL pages) — before Layer 1 dark bg
5. Add GA4 tracking functions + auto-wiring wp_footer hook (priority 999, ALL pages)

Critical rules obeyed:
- No display:none added to anything
- No modification to CSP script-src (www.googletagmanager.com already there)
- No changes to existing functionality
- Follows same coding patterns as existing plugin
"""

import sys
import os

SRC = '/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v480.php'
DST = '/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v481.php'

with open(SRC, 'r', encoding='utf-8') as f:
    content = f.read()

original_len = len(content)
print(f"Source file: {original_len:,} characters")

# ============================================================
# CHANGE 1: Version number in plugin header
# ============================================================
MARKER_VERSION = ' * Version:     4.7.9'
REPLACEMENT_VERSION = ' * Version:     4.8.1'
assert MARKER_VERSION in content, f"MISSING: {MARKER_VERSION}"
content = content.replace(MARKER_VERSION, REPLACEMENT_VERSION, 1)
print("DONE: Version header updated to 4.8.1")

# ============================================================
# CHANGE 2: Add v4.8.1 to Description string
# ============================================================
MARKER_DESC_END = (
    'WordPress does not allow numeric slugs via REST API; this rewrite rule serves the page '
    'at /2 path while preserving native WP password protection.'
)
REPLACEMENT_DESC_END = (
    'WordPress does not allow numeric slugs via REST API; this rewrite rule serves the page '
    'at /2 path while preserving native WP password protection. '
    'GA4 Direct Tracking (v4.8.1): injects Google Analytics 4 gtag.js (G-86325WBT3P) '
    'on ALL pages via wp_head priority 1. Five conversion tracking functions added: '
    'trackFormSubmission, trackChatboxOpen, trackChatboxMessage, trackPurchase, '
    'trackAssessmentStart, trackNewsletterSignup. Auto-wiring JS in wp_footer hooks into '
    'assessment pages, Brevo form success events, and all form submissions. '
    'CSP connect-src updated to allow www.google-analytics.com and '
    'www.googletagmanager.com analytics beacon endpoints.'
)
assert MARKER_DESC_END in content, f"MISSING desc end marker"
content = content.replace(MARKER_DESC_END, REPLACEMENT_DESC_END, 1)
print("DONE: Description updated")

# ============================================================
# CHANGE 3: Add changelog entries (v4.8.1 and v4.8.0)
# ============================================================
MARKER_CHANGELOG = (
    ' * Changelog:\n'
    ' *   v4.7.9 - VIDEO MODAL CLOSE BUTTON FIX'
)
REPLACEMENT_CHANGELOG = (
    ' * Changelog:\n'
    ' *   v4.8.1 - GA4 DIRECT TRACKING: Google Analytics 4 (G-86325WBT3P) injected on ALL\n'
    ' *            pages via wp_head priority 1 (direct gtag.js, no GTM required). Loads\n'
    ' *            before all other scripts for maximum coverage. Five conversion tracking\n'
    ' *            functions registered as window globals: trackFormSubmission(formName),\n'
    ' *            trackChatboxOpen(), trackChatboxMessage(), trackPurchase(txId, val, tier),\n'
    ' *            trackAssessmentStart(type), trackNewsletterSignup(source). Auto-wiring JS\n'
    ' *            in wp_footer (priority 999, ALL pages) hooks into: assessment page URL/DOM\n'
    ' *            detection, Brevo sib_form_submit_success event, and all form submissions\n'
    ' *            via document event delegation. CSP connect-src updated: added\n'
    ' *            www.google-analytics.com and www.googletagmanager.com for GA4 beacon\n'
    ' *            endpoints. No existing functionality changed. No display:none added.\n'
    ' *   v4.8.0 - PRICING BUTTON DIRECT OVERRIDE: direct onclick overrides on pricing\n'
    ' *            CTA buttons (pages 688/689) to restore PayPal checkout after page edits.\n'
    ' *   v4.7.9 - VIDEO MODAL CLOSE BUTTON FIX'
)
assert MARKER_CHANGELOG in content, f"MISSING changelog marker"
content = content.replace(MARKER_CHANGELOG, REPLACEMENT_CHANGELOG, 1)
print("DONE: Changelog entries added")

# ============================================================
# CHANGE 4: CSP connect-src — add Google Analytics domains
# The R2 bucket entry is the last item in connect-src.
# Change it from R2; to R2 [space] and then add GA4 entries.
# ============================================================
MARKER_CSP = (
    '         .     "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev; "')

REPLACEMENT_CSP = (
    '         .     "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev "\n'
    '         // Google Analytics 4 beacon endpoints (v4.8.1)\n'
    '         // GA4 sends measurement hits to google-analytics.com\n'
    '         // www.googletagmanager.com was already in script-src (v4.7.0)\n'
    '         // Added here to connect-src for gtag() fetch/XHR analytics calls\n'
    '         .     "https://www.google-analytics.com "\n'
    '         .     "https://www.googletagmanager.com; "'
)
assert MARKER_CSP in content, f"MISSING CSP marker"
content = content.replace(MARKER_CSP, REPLACEMENT_CSP, 1)
print("DONE: CSP connect-src updated with GA4 domains")

# Also update the CSP changelog comment block
MARKER_CSP_COMMENT = (
    '    //   v4.6.3 - Added cdn.jsdelivr.net to connect-src (Three.js dynamic import fix)\n'
    '    $csp = "default-src \'self\'; "'
)
REPLACEMENT_CSP_COMMENT = (
    '    //   v4.6.3 - Added cdn.jsdelivr.net to connect-src (Three.js dynamic import fix)\n'
    '    //   v4.8.1 - Added www.google-analytics.com + www.googletagmanager.com to\n'
    '    //            connect-src for GA4 gtag.js analytics beacon endpoints.\n'
    '    $csp = "default-src \'self\'; "'
)
assert MARKER_CSP_COMMENT in content, f"MISSING CSP comment marker"
content = content.replace(MARKER_CSP_COMMENT, REPLACEMENT_CSP_COMMENT, 1)
print("DONE: CSP comment updated")

# ============================================================
# CHANGE 5: Add GA4 gtag.js wp_head hook (priority 1, ALL pages)
# Insert BEFORE the Layer 1 dark background CSS hook
# ============================================================
MARKER_LAYER1 = (
    '// LAYER 1: Fire at priority 1 \u2014 before ALL other CSS\n'
    "add_action( 'wp_head', function () {"
)
REPLACEMENT_LAYER1 = (
    '// ============================================================\n'
    '// GA4 DIRECT TRACKING (v4.8.1)\n'
    '// Measurement ID: G-86325WBT3P\n'
    '// Injects async gtag.js script on ALL pages (priority 1).\n'
    '// Direct implementation — no GTM container required.\n'
    '// Tracking functions + auto-wiring added in wp_footer below.\n'
    '// ============================================================\n'
    '\n'
    "add_action( 'wp_head', function () {\n"
    '    echo "<!-- Google Analytics 4 (PureBrain.ai | G-86325WBT3P) -->\\n";\n'
    '    echo \'<script async src="https://www.googletagmanager.com/gtag/js?id=G-86325WBT3P"></script>\' . "\\n";\n'
    "    echo '<script id=\"pb-ga4-init\">' . \"\\n\";\n"
    '    echo "window.dataLayer = window.dataLayer || [];\\n";\n'
    "    echo \"function gtag(){dataLayer.push(arguments);}\\n\";\n"
    "    echo \"gtag('js', new Date());\\n\";\n"
    "    echo \"gtag('config', 'G-86325WBT3P');\\n\";\n"
    "    echo '</script>' . \"\\n\";\n"
    '}, 1 );\n'
    '\n'
    '// LAYER 1: Fire at priority 1 \u2014 before ALL other CSS\n'
    "add_action( 'wp_head', function () {"
)
assert MARKER_LAYER1 in content, f"MISSING Layer 1 marker"
content = content.replace(MARKER_LAYER1, REPLACEMENT_LAYER1, 1)
print("DONE: GA4 wp_head hook added (priority 1)")

# ============================================================
# CHANGE 6: Add GA4 tracking functions + auto-wiring wp_footer hook
# Append at the END of the file
# ============================================================
GA4_FOOTER = r"""

// ============================================================
// GA4 CONVERSION TRACKING FUNCTIONS + AUTO-WIRING (v4.8.1)
// ALL pages, ALL post types, ALL templates.
//
// Registers 5 tracking functions as window globals:
//   window.trackFormSubmission(formName)
//   window.trackChatboxOpen()
//   window.trackChatboxMessage()
//   window.trackPurchase(transactionId, value, tierName)
//   window.trackAssessmentStart(assessmentType)
//   window.trackNewsletterSignup(signupSource)
//
// Auto-wiring:
//   1. Assessment page detection (URL + DOM element check)
//   2. Brevo sib_form_submit_success event (neural feed signups)
//   3. All form submit events via document event delegation
//
// Requires: gtag() initialized via wp_head GA4 hook above.
//
// NOTE for Jared: After deployment, mark these as conversions
// in GA4 Admin > Events: purchase, newsletter_signup, form_submission
// ============================================================

add_action( 'wp_footer', function () {
    // Don't inject on admin pages
    if ( is_admin() ) {
        return;
    }
    ?>
<script id="pb-ga4-tracking-functions">
/* =============================================================
   GA4 Conversion Tracking Functions — PureBrain.ai (v4.8.1)
   Measurement ID: G-86325WBT3P
   Requires gtag() initialized in wp_head above
   ============================================================= */
(function() {
    'use strict';

    /* Safety guard: ensure gtag is callable */
    function safeGtag() {
        if (typeof gtag === 'function') {
            gtag.apply(null, arguments);
        }
    }

    /* -------------------------------------------------------
       1. FORM SUBMISSION
       Call: window.trackFormSubmission('assessment_form')
       form_name values:
         'assessment_form'   — AI Adoption Assessment
         'contact_form'      — contact/inquiry form
         'waitlist_form'     — invite/waitlist signups
         'demo_request_form' — demo request forms
    ------------------------------------------------------- */
    window.trackFormSubmission = function(formName) {
        safeGtag('event', 'form_submission', {
            form_name: String(formName || 'unknown_form'),
            page_location: window.location.href
        });
    };

    /* -------------------------------------------------------
       2. CHATBOX INTERACTIONS
       Call: window.trackChatboxOpen() — when chatbox opens
       Call: window.trackChatboxMessage() — when user sends msg
       Add to chatbox JS: trackChatboxOpen() on toggle click,
       trackChatboxMessage() on first send button click.
    ------------------------------------------------------- */
    window.trackChatboxOpen = function() {
        safeGtag('event', 'chatbox_interaction', {
            interaction_type: 'chatbox_opened',
            page_location: window.location.href
        });
    };

    window.trackChatboxMessage = function() {
        safeGtag('event', 'chatbox_interaction', {
            interaction_type: 'message_sent',
            page_location: window.location.href
        });
    };

    /* -------------------------------------------------------
       3. PURCHASE (PayPal payment completion)
       Call: window.trackPurchase(orderId, amount, tierName)
       tierName: 'starter', 'pro', 'awakened', 'enterprise'
       Add to PayPal onApprove() success callback.
    ------------------------------------------------------- */
    window.trackPurchase = function(transactionId, value, tierName) {
        safeGtag('event', 'purchase', {
            transaction_id: String(transactionId || ''),
            value: parseFloat(value) || 0,
            currency: 'USD',
            items: [{
                item_id: String(tierName || 'unknown'),
                item_name: 'PureBrain ' + String(tierName || 'unknown'),
                item_category: 'AI Partnership Plan',
                price: parseFloat(value) || 0,
                quantity: 1
            }]
        });
    };

    /* -------------------------------------------------------
       4. ASSESSMENT START
       Call: window.trackAssessmentStart('ai_adoption_assessment')
       Auto-wired below via URL + DOM detection.
    ------------------------------------------------------- */
    window.trackAssessmentStart = function(assessmentType) {
        safeGtag('event', 'assessment_start', {
            assessment_type: String(assessmentType || 'ai_adoption_assessment'),
            page_location: window.location.href
        });
    };

    /* -------------------------------------------------------
       5. NEWSLETTER SIGNUP (Neural Feed)
       Call: window.trackNewsletterSignup('blog_inline')
       signup_source values:
         'homepage', 'blog_inline', 'blog_sidebar',
         'popup', 'footer', 'assessment_thank_you'
       Auto-wired below via sib_form_submit_success event.
    ------------------------------------------------------- */
    window.trackNewsletterSignup = function(signupSource) {
        safeGtag('event', 'newsletter_signup', {
            signup_source: String(signupSource || 'unknown'),
            page_location: window.location.href
        });
    };

    /* =======================================================
       AUTO-WIRING: Hooks into existing page elements
    ======================================================= */

    /* AUTO-WIRE 1: Assessment page detection
       Fires trackAssessmentStart on load when page is the
       AI Adoption Assessment (URL or DOM element match).
       Small delay ensures gtag config has settled. */
    (function detectAssessmentPage() {
        var url = window.location.href.toLowerCase();
        var isAssessment = (
            url.indexOf('assessment') > -1 ||
            url.indexOf('ai-adoption') > -1 ||
            !!document.querySelector(
                '.assessment-container, #assessment-container, ' +
                '.assessment-form, #assessment-form, ' +
                '[data-assessment-type], .ai-assessment-widget'
            )
        );
        if (isAssessment) {
            setTimeout(function() {
                window.trackAssessmentStart('ai_adoption_assessment');
            }, 500);
        }
    })();

    /* AUTO-WIRE 2: Brevo newsletter form success
       Brevo fires 'sib_form_submit_success' on successful
       form submission. Detects current page type to set source. */
    window.addEventListener('sib_form_submit_success', function() {
        var source = 'unknown';
        var body = document.body;
        if (body.classList.contains('home')) {
            source = 'homepage';
        } else if (body.classList.contains('single-post')) {
            source = 'blog_inline';
        } else if (body.classList.contains('category') ||
                   body.classList.contains('archive') ||
                   body.classList.contains('tag')) {
            source = 'blog_sidebar';
        }
        window.trackNewsletterSignup(source);
    });

    /* AUTO-WIRE 3: All form submission tracking
       Uses event delegation on document to catch every form.
       Builds a human-readable form name from available attrs.
       Skips Brevo's embedded forms (tracked via event above).
       useCapture=true fires before form's own submit handler. */
    document.addEventListener('submit', function(e) {
        var form = e.target;
        if (!form || form.tagName !== 'FORM') return;

        /* Skip Brevo embedded forms — already tracked via sib_form_submit_success */
        if (form.hasAttribute('data-form-id') ||
            (form.id && form.id.indexOf('sib') === 0)) {
            return;
        }

        /* Build descriptive form name (normalized, max 64 chars) */
        var rawName = (
            form.getAttribute('name') ||
            form.getAttribute('id') ||
            form.getAttribute('data-form-name') ||
            form.getAttribute('aria-label') ||
            form.className ||
            'form'
        );
        var formName = String(rawName)
            .split(/\s+/)[0]
            .replace(/[^a-zA-Z0-9_\-]/g, '_')
            .substring(0, 64);

        window.trackFormSubmission(formName || 'unknown_form');
    }, true);

})();
</script>
    <?php
}, 999 );
"""

# Strip trailing whitespace from content then append
content = content.rstrip('\n') + '\n' + GA4_FOOTER

# Write output
with open(DST, 'w', encoding='utf-8') as f:
    f.write(content)

new_len = len(open(DST, encoding='utf-8').read())
print(f"\nOutput file: {new_len:,} characters ({new_len - original_len:+,} chars added)")

# ============================================================
# VERIFICATION
# ============================================================
with open(DST, 'r', encoding='utf-8') as f:
    result = f.read()

checks = [
    # Header changes
    (' * Version:     4.8.1',
     'Version 4.8.1 in header'),
    ('v4.8.1 - GA4 DIRECT TRACKING',
     'GA4 changelog entry present'),
    ('v4.8.0 - PRICING BUTTON',
     'v4.8.0 changelog entry present'),
    # GA4 script tag
    ('googletagmanager.com/gtag/js?id=G-86325WBT3P',
     'gtag.js script tag with correct ID'),
    ("gtag('config', 'G-86325WBT3P')",
     'gtag config call with correct ID'),
    ('id="pb-ga4-init"',
     'GA4 init script has id attribute'),
    # CSP
    ('https://www.google-analytics.com ',
     'google-analytics.com in CSP connect-src'),
    ('https://www.googletagmanager.com; "',
     'googletagmanager.com as last connect-src entry'),
    # Tracking functions
    ('window.trackFormSubmission = function',
     'trackFormSubmission registered as window global'),
    ('window.trackChatboxOpen = function',
     'trackChatboxOpen registered as window global'),
    ('window.trackChatboxMessage = function',
     'trackChatboxMessage registered as window global'),
    ('window.trackPurchase = function',
     'trackPurchase registered as window global'),
    ('window.trackAssessmentStart = function',
     'trackAssessmentStart registered as window global'),
    ('window.trackNewsletterSignup = function',
     'trackNewsletterSignup registered as window global'),
    # Auto-wiring
    ('detectAssessmentPage',
     'Assessment page auto-detection present'),
    ("sib_form_submit_success",
     'Brevo form success auto-wiring present'),
    ("document.addEventListener('submit'",
     'Form delegation auto-wiring present'),
    # Safety: existing functionality preserved
    ('n5) PRICING BUTTON DIRECT OVERRIDE (v4.8.0)',
     'v4.8.0 pricing button fix preserved'),
    ('PUREBRAIN_INDEXNOW_KEY',
     'IndexNow integration preserved'),
    ('purebrain_brevo_subscribe',
     'Brevo subscribe endpoint preserved'),
    # Safety: no regressions
    ('pb-dark-bg-layer1',
     'Dark bg Layer 1 preserved'),
    ('pb-dark-bg-layer2',
     'Dark bg Layer 2 preserved'),
    # CRITICAL: no display:none on new code
    # (check GA4 footer section doesn't have it)
    ('id="pb-ga4-tracking-functions"',
     'GA4 tracking script has correct id'),
]

# Also check: GA4 head hook fires at priority 1 (before Layer 1)
ga4_head_pos = result.find('pb-ga4-init')
layer1_pos = result.find('pb-dark-bg-layer1')
checks.append((
    ga4_head_pos < layer1_pos,
    f'GA4 head hook (pos {ga4_head_pos}) appears before Layer 1 dark bg (pos {layer1_pos})'
))

# Check no display:none in the new GA4 footer block
footer_start = result.find('id="pb-ga4-tracking-functions"')
footer_end = result.find('}, 999 );', footer_start) + 20
new_ga4_block = result[footer_start:footer_end] if footer_start > 0 else ''
has_display_none_in_ga4 = 'display:none' in new_ga4_block or 'display: none' in new_ga4_block
checks.append((
    not has_display_none_in_ga4,
    'No display:none in GA4 tracking block (safety check)'
))

print("\n--- VERIFICATION RESULTS ---")
all_pass = True
for item, label in checks:
    if isinstance(item, str):
        passed = item in result
    else:
        passed = bool(item)
    status = "PASS" if passed else "FAIL"
    if not passed:
        all_pass = False
    print(f"  [{status}] {label}")

file_size = os.path.getsize(DST)
print(f"\nFile size: {file_size:,} bytes")
print(f"Status: {'ALL CHECKS PASS - READY FOR REVIEW' if all_pass else 'SOME CHECKS FAILED - REVIEW NEEDED'}")
