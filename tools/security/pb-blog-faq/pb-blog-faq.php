<?php
/**
 * Plugin Name: PureBrain Blog FAQ
 * Plugin URI:  https://purebrain.ai
 * Description: Blog post FAQ accordion (three visual structures) and FAQPage JSON-LD schema injection for AEO/GEO. Extracted from purebrain-security-plugin.php (Task 13 of 14).
 * Version:     1.0.0
 * Author:      Pure Technology
 * License:     Proprietary
 *
 * Extracted from purebrain-security-plugin.php (Task 13 of 14)
 * Source lines: 2028–2690
 * Extraction date: 2026-03-07
 *
 * What this plugin does:
 *   j)        FAQ ACCORDION        — wp_head priority 15 — .faq-section > h3 + p (classic structure)
 *   j2)       FAQ ACCORDION EXTENDED — wp_head priority 16 — pb-faq-item/pb-faq-q/pb-faq-a + bare h3+p after <h2>FAQ</h2>
 *   j-schema) FAQPage JSON-LD SCHEMA  — wp_footer priority 14 — server-side parser, all four FAQ structures
 *
 * All hooks are gated to is_single() (single blog posts only).
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
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
// j2) FAQ ACCORDION EXTENDED (Feb 24, 2026 - v5.0.3)
//     Handles TWO additional FAQ structures not covered by j):
//
//     Structure A: pb-faq-item / pb-faq-q / pb-faq-a (Post 879 pattern)
//       Used in: Post 879 (your-next-direct-report-wont-be-human)
//       Fix: CSS hides pb-faq-a by default; JS toggles open/closed on click
//       of pb-faq-q. Chevron added to pb-faq-q.
//
//     Structure B: Bare <h3>Q</h3><p>A</p> pairs after <h2>FAQ</h2>
//       Used in: Post 606 (why-95-percent-of-ai-pilots-fail) and similar
//       Fix: JS wraps each h3+p pair in a .faq-section div so the existing
//       accordion (j) picks them up automatically.
//
//     Global rule: ALL FAQ structures on ALL blog posts start collapsed.
// ============================================================

add_action( 'wp_head', function () {
    if ( ! is_single() ) {
        return;
    }
    ?>
<style id="purebrain-faq-extended">
/* ============================================================
   FAQ EXTENDED STYLES (v5.0.3)
   Handles pb-faq-item/pb-faq-q/pb-faq-a structure (Post 879 pattern).
   All items start collapsed. Click pb-faq-q to expand.
   ============================================================ */

/* Pre-JS: hide pb-faq-a answers immediately so they start collapsed */
body.single-post .post-content .pb-faq-item .pb-faq-a,
body.single-post .post-content .pb-faq-section .pb-faq-item .pb-faq-a {
    max-height: 0 !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
    transition: max-height 0.35s ease, padding 0.25s ease, opacity 0.25s ease !important;
    opacity: 0 !important;
}

/* pb-faq-item: container */
body.single-post .post-content .pb-faq-item {
    border-radius: 10px !important;
    margin-bottom: 10px !important;
    overflow: hidden !important;
    cursor: pointer !important;
    position: relative !important;
    transition: background 0.2s ease !important;
}

/* pb-faq-q: the clickable question */
body.single-post .post-content .pb-faq-item .pb-faq-q {
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
}

body.single-post .post-content .pb-faq-item .pb-faq-q:hover {
    color: #2a93c1 !important;
}

/* Chevron on pb-faq-q */
body.single-post .post-content .pb-faq-item .pb-faq-q::after {
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
body.single-post .post-content .pb-faq-item.pb-faq-open .pb-faq-q::after {
    transform: translateY(-50%) rotate(180deg) !important;
}

/* Answer visible when open */
body.single-post .post-content .pb-faq-item.pb-faq-open .pb-faq-a {
    max-height: 800px !important;
    padding: 0 20px 18px 20px !important;
    opacity: 1 !important;
    color: #b0b8c4 !important;
    font-size: 15px !important;
    line-height: 1.7 !important;
}

/* Active item accent border */
body.single-post .post-content .pb-faq-item.pb-faq-open {
    border-left: 3px solid #2a93c1 !important;
    background: rgba(42, 147, 193, 0.06) !important;
}
</style>
<script id="purebrain-faq-extended-js">
(function() {
    'use strict';

    function initExtendedFaqAccordion() {
        if (!document.body.classList.contains('single-post')) return;

        // -------------------------------------------------------
        // Structure A: pb-faq-item / pb-faq-q / pb-faq-a
        // -------------------------------------------------------
        var pbItems = document.querySelectorAll('.post-content .pb-faq-item');
        if (pbItems.length) {
            pbItems.forEach(function(item) {
                var trigger = item.querySelector('.pb-faq-q');
                if (!trigger) return;

                trigger.addEventListener('click', function() {
                    var isOpen = item.classList.contains('pb-faq-open');

                    // Close all pb-faq-items (accordion: one open at a time)
                    pbItems.forEach(function(other) {
                        other.classList.remove('pb-faq-open');
                    });

                    // If it wasn't open before, open it now
                    if (!isOpen) {
                        item.classList.add('pb-faq-open');
                    }
                });
            });
        }

        // -------------------------------------------------------
        // Structure B: Bare h3+p pairs after <h2>FAQ</h2>
        // Wrap them in .faq-section divs so the main accordion picks them up
        // -------------------------------------------------------
        var postContent = document.querySelector('.post-content');
        if (!postContent) return;

        // Find all h2 elements that contain "FAQ" text
        var h2s = postContent.querySelectorAll('h2');
        h2s.forEach(function(h2) {
            var text = (h2.textContent || h2.innerText || '').trim().toLowerCase();
            if (text.indexOf('faq') === -1) return;

            // Collect consecutive h3+p sibling pairs after this h2
            var sibling = h2.nextElementSibling;
            var pairs = [];

            while (sibling) {
                if (sibling.nodeName === 'H3') {
                    var pSibling = sibling.nextElementSibling;
                    if (pSibling && pSibling.nodeName === 'P') {
                        pairs.push({h3: sibling, p: pSibling});
                        sibling = pSibling.nextElementSibling;
                        continue;
                    }
                }
                // Stop at next h2/h1
                if (sibling.nodeName === 'H2' || sibling.nodeName === 'H1') break;
                sibling = sibling.nextElementSibling;
            }

            // Wrap each pair in a .faq-section div (if not already wrapped)
            pairs.forEach(function(pair) {
                if (pair.h3.parentNode &&
                    pair.h3.parentNode.classList &&
                    pair.h3.parentNode.classList.contains('faq-section')) return;
                var wrapper = document.createElement('div');
                wrapper.className = 'faq-section';
                pair.h3.parentNode.insertBefore(wrapper, pair.h3);
                wrapper.appendChild(pair.h3);
                wrapper.appendChild(pair.p);
            });

            if (!pairs.length) return;

            // Re-init accordion for newly-wrapped .faq-section items
            var newItems = postContent.querySelectorAll('.faq-section');
            newItems.forEach(function(item) {
                // Skip already-initialized items (they already have a .faq-answer child)
                if (item.querySelector('.faq-answer')) return;

                // Wrap direct <p> children in .faq-answer
                var paragraphs = [];
                var children = item.childNodes;
                for (var i = 0; i < children.length; i++) {
                    if (children[i].nodeName === 'P') {
                        paragraphs.push(children[i]);
                    }
                }
                if (paragraphs.length > 0) {
                    var answerWrapper = document.createElement('div');
                    answerWrapper.className = 'faq-answer';
                    item.insertBefore(answerWrapper, paragraphs[0]);
                    paragraphs.forEach(function(p) { answerWrapper.appendChild(p); });
                }

                // Attach click handler
                var trigger = item.querySelector('h3');
                if (!trigger) return;

                trigger.addEventListener('click', function() {
                    var isOpen = item.classList.contains('faq-open');
                    newItems.forEach(function(other) { other.classList.remove('faq-open'); });
                    if (!isOpen) { item.classList.add('faq-open'); }
                });
            });
        });
    }

    // Run as soon as possible
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initExtendedFaqAccordion);
    } else {
        initExtendedFaqAccordion();
    }
})();
</script>
    <?php
}, 16 );

// ============================================================
// j-schema) FAQPage JSON-LD SCHEMA (Feb 24, 2026 - v5.8.0)
//     AEO/GEO structured data gap fix.
//     Parses the post content server-side for ALL four FAQ structures
//     and outputs a <script type="application/ld+json"> FAQPage block
//     in wp_footer so Google / AI search engines can consume it.
//
//     Four structures handled:
//       A) .faq-section > h3 + p            (classic — posts 565/480/381/316/373/172/98)
//       B) .pb-faq-item > .pb-faq-q + .pb-faq-a  (post 879 pattern)
//       C) <details><summary>Q</summary>A</details>  (post 631)
//       D) bare <h3>Q</h3><p>A</p> after <h2>FAQ</h2>  (post 606)
//
//     Backward compat: if the post's saved content already contains a
//     FAQPage script block (manually added in earlier sessions), this
//     hook skips that post — no duplicate schema.
//
//     Priority 14 (runs before the accordion hooks at 15/16, but those
//     are wp_head hooks so timing doesn't really conflict — cleaner this way).
// ============================================================

add_action( 'wp_footer', function () {
    if ( ! is_single() ) {
        return;
    }

    $post = get_post();
    if ( ! $post ) {
        return;
    }

    $raw_content = $post->post_content;

    // Backward compat: skip posts that already have a manually-added FAQPage schema
    if ( strpos( $raw_content, '"FAQPage"' ) !== false || strpos( $raw_content, "'FAQPage'" ) !== false ) {
        return;
    }

    // -------------------------------------------------------
    // Parse FAQ Q&A pairs from the post content.
    // We use PHP DOMDocument for reliable HTML parsing.
    // libxml errors are suppressed (post content is not valid XHTML).
    // -------------------------------------------------------

    $faq_pairs = array();

    // Wrap in a body tag so DOMDocument doesn't prepend <html><body>
    $wrapped = '<div id="pb-faq-parse-root">' . $raw_content . '</div>';

    $dom = new DOMDocument( '1.0', 'UTF-8' );
    libxml_use_internal_errors( true );
    // Use UTF-8 meta so DOMDocument doesn't mangle non-ASCII characters
    $dom->loadHTML( '<?xml encoding="UTF-8">' . $wrapped );
    libxml_clear_errors();

    $xpath = new DOMXPath( $dom );

    // -------------------------------------------------------
    // Structure A: <div class="faq-section"><h3>Q</h3><p>A</p></div>
    // -------------------------------------------------------
    $faq_section_nodes = $xpath->query( '//*[contains(concat(" ", normalize-space(@class), " "), " faq-section ")]' );
    if ( $faq_section_nodes && $faq_section_nodes->length > 0 ) {
        foreach ( $faq_section_nodes as $section ) {
            $h3_nodes = $xpath->query( './/h3', $section );
            $p_nodes  = $xpath->query( './/p',  $section );
            if ( $h3_nodes->length > 0 && $p_nodes->length > 0 ) {
                $question = trim( $h3_nodes->item(0)->textContent );
                // Collect all <p> text as one answer string
                $answer_parts = array();
                foreach ( $p_nodes as $p ) {
                    $text = trim( $p->textContent );
                    if ( $text !== '' ) {
                        $answer_parts[] = $text;
                    }
                }
                $answer = implode( ' ', $answer_parts );
                if ( $question !== '' && $answer !== '' ) {
                    $faq_pairs[] = array( 'q' => $question, 'a' => $answer );
                }
            }
        }
    }

    // -------------------------------------------------------
    // Structure B: <div class="pb-faq-item">
    //                <p class="pb-faq-q">Q</p>
    //                <p class="pb-faq-a">A</p>
    //              </div>
    // -------------------------------------------------------
    if ( empty( $faq_pairs ) || strpos( $raw_content, 'pb-faq-item' ) !== false ) {
        $pb_item_nodes = $xpath->query( '//*[contains(concat(" ", normalize-space(@class), " "), " pb-faq-item ")]' );
        if ( $pb_item_nodes && $pb_item_nodes->length > 0 ) {
            foreach ( $pb_item_nodes as $item ) {
                $q_nodes = $xpath->query( './/*[contains(concat(" ", normalize-space(@class), " "), " pb-faq-q ")]', $item );
                $a_nodes = $xpath->query( './/*[contains(concat(" ", normalize-space(@class), " "), " pb-faq-a ")]', $item );
                if ( $q_nodes->length > 0 && $a_nodes->length > 0 ) {
                    $question = trim( $q_nodes->item(0)->textContent );
                    $answer   = trim( $a_nodes->item(0)->textContent );
                    if ( $question !== '' && $answer !== '' ) {
                        // Avoid duplicates from Structure A
                        $already = false;
                        foreach ( $faq_pairs as $pair ) {
                            if ( $pair['q'] === $question ) { $already = true; break; }
                        }
                        if ( ! $already ) {
                            $faq_pairs[] = array( 'q' => $question, 'a' => $answer );
                        }
                    }
                }
            }
        }
    }

    // -------------------------------------------------------
    // Structure C: <details><summary>Q</summary>A</details>
    // -------------------------------------------------------
    if ( strpos( $raw_content, '<details' ) !== false ) {
        $details_nodes = $xpath->query( '//details' );
        if ( $details_nodes && $details_nodes->length > 0 ) {
            foreach ( $details_nodes as $details ) {
                $summary_nodes = $xpath->query( './summary', $details );
                if ( $summary_nodes->length > 0 ) {
                    $question = trim( $summary_nodes->item(0)->textContent );
                    // Answer = all text in <details> except the <summary>
                    $answer_parts = array();
                    foreach ( $details->childNodes as $child ) {
                        if ( $child->nodeName === 'summary' ) continue;
                        $text = trim( $child->textContent );
                        if ( $text !== '' ) {
                            $answer_parts[] = $text;
                        }
                    }
                    $answer = implode( ' ', $answer_parts );
                    if ( $question !== '' && $answer !== '' ) {
                        $already = false;
                        foreach ( $faq_pairs as $pair ) {
                            if ( $pair['q'] === $question ) { $already = true; break; }
                        }
                        if ( ! $already ) {
                            $faq_pairs[] = array( 'q' => $question, 'a' => $answer );
                        }
                    }
                }
            }
        }
    }

    // -------------------------------------------------------
    // Structure D: bare <h3>Q</h3><p>A</p> after <h2>FAQ</h2>
    // Only runs if no faq-section / pb-faq-item divs were found.
    // -------------------------------------------------------
    if ( empty( $faq_pairs ) ) {
        $h2_nodes = $xpath->query( '//h2' );
        if ( $h2_nodes ) {
            foreach ( $h2_nodes as $h2 ) {
                $h2_text = strtolower( trim( $h2->textContent ) );
                if ( strpos( $h2_text, 'faq' ) === false && strpos( $h2_text, 'frequently asked' ) === false ) {
                    continue;
                }
                // Walk siblings: collect consecutive h3+p pairs
                $sibling = $h2->nextSibling;
                while ( $sibling ) {
                    // Skip text nodes / whitespace
                    if ( $sibling->nodeType === XML_TEXT_NODE ) {
                        $sibling = $sibling->nextSibling;
                        continue;
                    }
                    if ( $sibling->nodeName === 'h3' ) {
                        $question    = trim( $sibling->textContent );
                        $next        = $sibling->nextSibling;
                        // Skip whitespace text nodes
                        while ( $next && $next->nodeType === XML_TEXT_NODE ) {
                            $next = $next->nextSibling;
                        }
                        if ( $next && $next->nodeName === 'p' ) {
                            $answer = trim( $next->textContent );
                            if ( $question !== '' && $answer !== '' ) {
                                $faq_pairs[] = array( 'q' => $question, 'a' => $answer );
                            }
                            $sibling = $next->nextSibling;
                            continue;
                        }
                    }
                    // Stop at next h1/h2
                    if ( $sibling->nodeName === 'h1' || $sibling->nodeName === 'h2' ) {
                        break;
                    }
                    $sibling = $sibling->nextSibling;
                }
            }
        }
    }

    // Nothing found — nothing to output
    if ( empty( $faq_pairs ) ) {
        return;
    }

    // -------------------------------------------------------
    // Build the FAQPage JSON-LD array
    // -------------------------------------------------------
    $main_entity = array();
    foreach ( $faq_pairs as $pair ) {
        // Sanitize: strip HTML tags from extracted text (DOMDocument may include child-element text)
        $question_clean = wp_strip_all_tags( $pair['q'] );
        $answer_clean   = wp_strip_all_tags( $pair['a'] );
        // Normalize whitespace
        $question_clean = preg_replace( '/\s+/', ' ', $question_clean );
        $answer_clean   = preg_replace( '/\s+/', ' ', $answer_clean );

        if ( $question_clean === '' || $answer_clean === '' ) continue;

        $main_entity[] = array(
            '@type'          => 'Question',
            'name'           => $question_clean,
            'acceptedAnswer' => array(
                '@type' => 'Answer',
                'text'  => $answer_clean,
            ),
        );
    }

    if ( empty( $main_entity ) ) {
        return;
    }

    $schema = array(
        '@context'   => 'https://schema.org',
        '@type'      => 'FAQPage',
        'mainEntity' => $main_entity,
    );

    // JSON_UNESCAPED_UNICODE keeps non-ASCII readable; JSON_UNESCAPED_SLASHES avoids \/ in URLs
    $json = wp_json_encode( $schema, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT );

    if ( ! $json ) {
        return;
    }

    echo "\n<!-- FAQPage JSON-LD schema: auto-generated by pb-blog-faq.php v1.0.0 -->\n";
    echo '<script type="application/ld+json">' . "\n" . $json . "\n" . '</script>' . "\n";

}, 14 );
