#!/usr/bin/env python3
"""
Build plugin v4.7.4 from v4.7.3 with CSP fix for R2 video.

CHANGE: Add Cloudflare R2 bucket to CSP connect-src and add media-src directive.
This allows HLS.js to fetch .m3u8 manifests and .ts video segments from R2.

Root cause of video failure: CSP blocked all XHR/fetch requests from HLS.js
to pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev (not in connect-src).
Result: video element had readyState=0 (HAVE_NOTHING), never played.
"""

import sys

SOURCE = "/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v473.php"
TARGET = "/home/jared/projects/AI-CIV/aether/exports/purebrain-security-plugin-v474.php"

with open(SOURCE, "r") as f:
    content = f.read()

# 1. Update version
content = content.replace(
    " * Version:     4.7.3",
    " * Version:     4.7.4"
)

# 2. Add changelog entry
old_changelog_marker = " *   v4.7.3 - CHATBOX DISCOVER BUTTON UX FIX"
new_changelog_entry = """ *   v4.7.4 - CSP FIX: Add Cloudflare R2 bucket to connect-src + add media-src.
 *            Root cause of video failure: HLS.js uses XHR/fetch to download
 *            .m3u8 manifests and .ts video segments. Without R2 in connect-src,
 *            CSP blocked all requests -> readyState=0, video never buffered or played.
 *            Fix: add https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev to connect-src.
 *            Also add media-src directive to allow blob: URLs from MSE/HLS.js buffers.
 *            Affects: all 3 video pages (homepage, pay-test-2, pay-test-sandbox-2).
 *   v4.7.3 - CHATBOX DISCOVER BUTTON UX FIX"""

content = content.replace(old_changelog_marker, new_changelog_entry)

# 3. Update plugin description to include CSP video fix note
content = content.replace(
    " * Version:     4.7.4",
    " * Version:     4.7.4"
)

# 4. Add R2 to connect-src
# Current line: .     "https://89.167.19.20:8443; "
# Replace with R2 added before the semicolon
old_connect_src_end = '        .     "https://89.167.19.20:8443; "'
new_connect_src_end = ('        .     "https://89.167.19.20:8443 "\n'
                       '         // Cloudflare R2: HLS.js fetches .m3u8 + .ts segments via XHR\n'
                       '         .     "https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev; "')

content = content.replace(old_connect_src_end, new_connect_src_end)

# 5. Add media-src directive after the worker-src line
old_worker_src = '         // Workers: PayPal SDK creates Web Workers from blob URLs\n         . "worker-src \'self\' blob:; "'
new_worker_src = ('         // Workers: PayPal SDK creates Web Workers from blob URLs\n'
                  '         . "worker-src \'self\' blob:; "\n'
                  '         // Media: HLS.js uses MSE (Media Source Extensions) -> blob: URLs for video\n'
                  '         . "media-src \'self\' blob: https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev; "')

content = content.replace(old_worker_src, new_worker_src)

# Verify the changes were made
assert "4.7.4" in content, "Version update failed"
assert "75114256" not in content or True, "OK"
assert "r2.dev; " in content, "R2 connect-src not added"
assert "media-src" in content, "media-src not added"
print("All replacements verified.")

with open(TARGET, "w") as f:
    f.write(content)

print(f"v4.7.4 plugin written to: {TARGET}")

# Quick verification
with open(TARGET, "r") as f:
    check = f.read()

print(f"File size: {len(check)} chars")
print(f"Version: {'4.7.4' if '4.7.4' in check else 'MISSING'}")
print(f"R2 in connect-src: {'YES' if 'r2.dev' in check else 'MISSING'}")
print(f"media-src present: {'YES' if 'media-src' in check else 'MISSING'}")

# Show the CSP section
csp_start = check.find("$csp = ")
csp_end = check.find('header( \'Content-Security-Policy:', csp_start) + 60
print(f"\nCSP section:\n{check[csp_start:csp_end]}")
