<?php
/**
 * Plugin Name: PureBrain Breadcrumb Fix
 * Plugin URI:  https://purebrain.ai
 * Description: Fixes missing 'item' (URL) property on Yoast SEO BreadcrumbList schema. Google Search Console requires every ListItem to have an 'item' URL; Yoast omits it on the current page by default. Extracted from PureBrain Security plugin (v3.3.0) on 2026-03-07 to keep the security plugin focused on security concerns only.
 * Version:     1.0.0
 * Author:      Aether (AI) for Pure Technology
 * Author URI:  https://purebrain.ai
 * License:     Private - All Rights Reserved
 *
 * Changelog:
 *   v1.0.0 - Initial extraction from PureBrain Security plugin.
 *            Fixes BreadcrumbList ListItem missing 'item' (URL) property flagged by
 *            Google Search Console. Injects canonical URL via get_permalink() (posts/
 *            pages), term_link() (category/tag archives), or get_pagenum_link()
 *            (paged archives). Covers single posts, pages, category archives, tag
 *            archives, and custom post types.
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

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
