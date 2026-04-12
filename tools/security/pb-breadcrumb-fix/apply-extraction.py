#!/usr/bin/env python3
"""
pb-breadcrumb-fix extraction script.

Removes the breadcrumb structured data fix block from purebrain-security-plugin.php
and replaces it with an extraction notice comment.

Run once, then delete this script.
Usage: python3 apply-extraction.py
"""

import sys
import os

SECURITY_PLUGIN = os.path.join(
    os.path.dirname(__file__),
    '../purebrain-security/purebrain-security-plugin.php'
)

OLD_BLOCK = (
    "// ============================================================\n"
    "// BREADCRUMB STRUCTURED DATA FIX (GSC: missing 'item' field)\n"
    "// Yoast SEO omits the 'item' (URL) property from the last\n"
    "// ListItem in BreadcrumbList. Google Search Console flags this\n"
    "// as an error. This filter injects the canonical URL for every\n"
    "// ListItem that is missing the 'item' property.\n"
    "// ============================================================\n"
    "\n"
    "add_filter( 'wpseo_schema_breadcrumb', function ( $schema_data ) {\n"
    "    if ( empty( $schema_data['itemListElement'] ) || ! is_array( $schema_data['itemListElement'] ) ) {\n"
    "        return $schema_data;\n"
    "    }\n"
    "\n"
    "    foreach ( $schema_data['itemListElement'] as &$list_item ) {\n"
    "        // Only fix items that are missing the 'item' property\n"
    "        if ( isset( $list_item['item'] ) ) {\n"
    "            continue;\n"
    "        }\n"
    "\n"
    "        // Determine the canonical URL for this breadcrumb position\n"
    "        $url = '';\n"
    "\n"
    "        if ( is_singular() ) {\n"
    "            // Single post, page, or custom post type \xe2\x80\x94 use the canonical permalink\n"
    "            $url = get_permalink();\n"
    "        } elseif ( is_category() || is_tag() || is_tax() ) {\n"
    "            // Category, tag, or custom taxonomy archive\n"
    "            $term = get_queried_object();\n"
    "            if ( $term && ! is_wp_error( $term ) ) {\n"
    "                $url = get_term_link( $term );\n"
    "                if ( is_wp_error( $url ) ) {\n"
    "                    $url = '';\n"
    "                }\n"
    "            }\n"
    "        } elseif ( is_archive() ) {\n"
    "            // Date archive, author archive, post type archive, etc.\n"
    "            $url = get_pagenum_link( get_query_var( 'paged' ) ? get_query_var( 'paged' ) : 1 );\n"
    "        } elseif ( is_home() || is_front_page() ) {\n"
    "            $url = home_url( '/' );\n"
    "        }\n"
    "\n"
    "        if ( ! empty( $url ) ) {\n"
    "            $list_item['item'] = esc_url( $url );\n"
    "        }\n"
    "    }\n"
    "    unset( $list_item ); // Unset reference to last element\n"
    "\n"
    "    return $schema_data;\n"
    "}, 10, 1 );\n"
)

NEW_BLOCK = (
    "// BREADCRUMB STRUCTURED DATA FIX \xe2\x80\x94 extracted to standalone plugin: pb-breadcrumb-fix (2026-03-07)\n"
)


def main():
    if not os.path.exists(SECURITY_PLUGIN):
        print(f"ERROR: Security plugin not found at {SECURITY_PLUGIN}")
        sys.exit(1)

    with open(SECURITY_PLUGIN, 'r', encoding='utf-8') as f:
        content = f.read()

    if OLD_BLOCK not in content:
        print("ERROR: Breadcrumb block not found in security plugin.")
        print("       The block may have already been extracted, or the file has changed.")
        sys.exit(1)

    occurrences = content.count(OLD_BLOCK)
    if occurrences != 1:
        print(f"ERROR: Expected exactly 1 occurrence of breadcrumb block, found {occurrences}.")
        sys.exit(1)

    new_content = content.replace(OLD_BLOCK, NEW_BLOCK, 1)

    with open(SECURITY_PLUGIN, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("SUCCESS: Breadcrumb block extracted.")
    print(f"  Removed {len(OLD_BLOCK.splitlines())} lines from security plugin.")
    print(f"  Replaced with: {NEW_BLOCK.strip()}")
    print()
    print("Verification — grep for extraction notice:")
    os.system(f"grep -n 'pb-breadcrumb-fix' '{SECURITY_PLUGIN}'")
    print()
    print("Verification — confirm breadcrumb block is gone:")
    result = os.system(f"grep -n 'wpseo_schema_breadcrumb' '{SECURITY_PLUGIN}'")
    if result != 0:
        print("  (No remaining wpseo_schema_breadcrumb hook — extraction confirmed clean)")


if __name__ == '__main__':
    main()
