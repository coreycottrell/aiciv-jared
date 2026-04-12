#!/usr/bin/env python3
"""
pb-301-redirects extraction script.

Removes the 301 redirect block from purebrain-security-plugin.php
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
    "// b2) 301 REDIRECTS FOR OLD SLUGS (v6.1.0)\n"
    "//     /ai-adoption-assessment was returning 404. Permanent 301\n"
    "//     so search engines transfer link equity to canonical URL.\n"
    "// ============================================================\n"
    "\n"
    "add_action( 'template_redirect', function () {\n"
    "    $request_uri = isset( $_SERVER['REQUEST_URI'] ) ? $_SERVER['REQUEST_URI'] : '';\n"
    "    $path        = trim( parse_url( $request_uri, PHP_URL_PATH ), '/' );\n"
    "\n"
    "    $redirects = array(\n"
    "        'ai-adoption-assessment' => '/ai-partnership-assessment/',\n"
    "    );\n"
    "\n"
    "    if ( isset( $redirects[ $path ] ) ) {\n"
    "        wp_redirect( home_url( $redirects[ $path ] ), 301 );\n"
    "        exit;\n"
    "    }\n"
    "}, 1 );\n"
)

NEW_BLOCK = (
    "// b2) 301 REDIRECTS — extracted to standalone plugin: pb-301-redirects (2026-03-07)\n"
)

def main():
    if not os.path.exists(SECURITY_PLUGIN):
        print(f"ERROR: Security plugin not found at {SECURITY_PLUGIN}")
        sys.exit(1)

    with open(SECURITY_PLUGIN, 'r', encoding='utf-8') as f:
        content = f.read()

    if OLD_BLOCK not in content:
        print("ERROR: Redirect block not found in security plugin.")
        print("       The block may have already been extracted, or the file has changed.")
        sys.exit(1)

    occurrences = content.count(OLD_BLOCK)
    if occurrences != 1:
        print(f"ERROR: Expected exactly 1 occurrence of redirect block, found {occurrences}.")
        sys.exit(1)

    new_content = content.replace(OLD_BLOCK, NEW_BLOCK, 1)

    with open(SECURITY_PLUGIN, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("SUCCESS: Redirect block extracted.")
    print(f"  Removed {len(OLD_BLOCK.splitlines())} lines from security plugin.")
    print(f"  Replaced with: {NEW_BLOCK.strip()}")
    print()
    print("Verification — grep for extraction notice:")
    os.system(f"grep -n 'pb-301-redirects' '{SECURITY_PLUGIN}'")
    print()
    print("Verification — confirm redirect block is gone:")
    result = os.system(f"grep -n 'ai-adoption-assessment.*ai-partnership-assessment' '{SECURITY_PLUGIN}' | grep -v '^34:'")
    if result != 0:
        print("  (No remaining code references — extraction confirmed clean)")

if __name__ == '__main__':
    main()
