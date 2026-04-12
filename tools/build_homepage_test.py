#!/usr/bin/env python3
"""
Homepage rebuild: merge pay-test-2 (working hero) + homepage CSS fixes.

Strategy:
- Use pay-test-2 as complete base (working video hero)
- Upgrade pb-magic-cursor-body-fix from v4.8.0 to v4.9.0 nuclear fix
- Upgrade pb-video-handler-css from v1.3.0 to v1.4.0 (iOS improvements)
- Update title/OG meta for proper homepage SEO
- Output to exports/cf-pages-deploy/homepage-test/index.html

Run: python3 tools/build_homepage_test.py
"""

import os
import re

BASE_DIR = "/home/jared/projects/AI-CIV/aether"
SOURCE = os.path.join(BASE_DIR, "exports/cf-pages-deploy/pay-test-2/index.html")
OUTPUT_DIR = os.path.join(BASE_DIR, "exports/cf-pages-deploy/homepage-test")
OUTPUT = os.path.join(OUTPUT_DIR, "index.html")

# Read source
with open(SOURCE, "r", encoding="utf-8") as f:
    content = f.read()

print(f"Read {len(content)} chars from pay-test-2")

# ============================================================
# FIX 1: Upgrade pb-magic-cursor-body-fix from v4.8.0 to v4.9.0
# ============================================================
OLD_MAGIC_FIX = '''<style id="pb-magic-cursor-body-fix">
/* FIX v4.8.0: The wp-custom-css Additional CSS has a broad selector:
   [class*="magic"] { color: #f1420b !important; background-color: #f1420b !important; }
   The Artistics theme adds class "tt-magic-cursor" to <body>, so this selector
   matches the body element and turns ALL text and backgrounds orange.
   This is a critical bug affecting any page on the elementor_canvas template.
   Fix: body.tt-magic-cursor uses higher specificity (0,1,1) vs [class*="magic"] (0,1,0)
   with !important, injected in wp_footer at priority 99 — loads last, wins always. */
</style>'''

NEW_MAGIC_FIX = '''<style id="pb-magic-cursor-body-fix">
/* FIX v4.9.0: NUCLEAR anti-orange-flash fix.
   Root cause: [class*="magic"] { background-color: #f1420b !important } in wp-custom-css
   matches body.tt-magic-cursor (body has 'magic' in its class name from artistics theme).
   This makes the ENTIRE body orange on first paint.
   The theme preloader shows on top with a dark background, but the orange is visible
   around it and AFTER the preloader fades.

   v4.9.0 NUCLEAR APPROACH:
   1. Outer <body> gets inline style background:#080a12 (overrides everything)
   2. html element is dark
   3. Body selectors with maximum specificity override the orange
   4. The wp-custom-css [class*="magic"] rule is neutralized by specificity
   5. html.home body also covered for the innermost body.home class merger */
/* Layer 1: html always dark */
html {
    background: #080a12 !important;
    background-color: #080a12 !important;
}
/* Layer 2: body is always dark except video pages (which need transparent) */
html body {
    background: #080a12 !important;
    background-color: #080a12 !important;
    color: #e8edf5 !important;
}
/* Layer 3: override [class*="magic"] for tt-magic-cursor specifically (higher specificity) */
html body.tt-magic-cursor {
    color: #e8edf5 !important;
    background-color: #080a12 !important;
    border-color: inherit !important;
}
/* Layer 4: Homepage and video-bg pages: body must be transparent so fixed video shows through */
html body.home,
html body.home.tt-magic-cursor,
html body.page-id-11,
html body.page-id-11.tt-magic-cursor,
html body.page-id-688.tt-magic-cursor,
html body.page-id-689.tt-magic-cursor,
html body.page-id-1232.tt-magic-cursor,
html body.page-id-319.tt-magic-cursor {
    background: transparent !important;
    background-color: transparent !important;
}
/* Layer 5: Defeat [class*="magic"] svg descendant rules that incorrectly color body children */
html body.tt-magic-cursor svg,
html body.tt-magic-cursor svg path,
html body.tt-magic-cursor svg circle,
html body.tt-magic-cursor svg rect,
html body.tt-magic-cursor svg polygon,
html body.tt-magic-cursor svg line {
    fill: currentColor !important;
    stroke: currentColor !important;
    color: inherit !important;
}
</style>'''

if OLD_MAGIC_FIX in content:
    content = content.replace(OLD_MAGIC_FIX, NEW_MAGIC_FIX)
    print("SUCCESS: Upgraded pb-magic-cursor-body-fix v4.8.0 -> v4.9.0")
else:
    print("WARNING: pb-magic-cursor-body-fix v4.8.0 not found - checking partial match...")
    if 'id="pb-magic-cursor-body-fix"' in content:
        print("  Found pb-magic-cursor-body-fix element but exact text didn't match")
        print("  Manual inspection needed")
    else:
        print("  pb-magic-cursor-body-fix not found at all")

# ============================================================
# FIX 2: Upgrade pb-video-handler-css from v1.3.0 to v1.4.0
# ============================================================
OLD_VIDEO_CSS_START = '<style id="pb-video-handler-css">\n/* v1.3.0:'
NEW_VIDEO_CSS = '''<style id="pb-video-handler-css">
/* v1.4.0: Fix .video-background__video sizing + iOS play button hide.
   width:100%/height:100%/object-fit:cover is universally supported.
   iOS Low Power Mode blocks autoplay — hide the ugly native play button
   so the page looks clean with the dark poster/gradient fallback. */
.video-background__video {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    object-fit: cover !important;
    transform: none !important;
    min-width: unset !important;
    min-height: unset !important;
}
/* Hide iOS Safari native video play button overlay */
.video-background__video::-webkit-media-controls-panel,
.video-background__video::-webkit-media-controls-play-button,
.video-background__video::-webkit-media-controls-start-playback-button,
.video-background__video::-webkit-media-controls {
    display: none !important;
    -webkit-appearance: none !important;
    opacity: 0 !important;
    pointer-events: none !important;
}
/* Ensure video background has dark fallback when video can't autoplay */
.video-background {
    background: #080a12 !important;
}

/* Mobile: video background visible, living-background ALSO visible (fallback for iOS).
   JS will hide living-background only when video actually starts playing. */
@media (max-width: 767px) {
    body.home .video-background,
    body.page-id-11 .video-background,
    body.page-id-689 .video-background,
    body.page-id-688 .video-background,
    body.page-id-1232 .video-background,
    body.page-id-319 .video-background {
        z-index: 0 !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    /* living-background stays VISIBLE on mobile — serves as iOS video fallback */
    /* JS adds .video-playing class to body when video starts → hides it then */
    body.video-playing .living-background {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        z-index: -999 !important;
    }
    body.video-playing .living-background * {
        display: none !important;
        visibility: hidden !important;
    }
    body.home #content,
    body.home .site-content,
    body.home .elementor,
    body.page-id-11 #content,
    body.page-id-11 .site-content,
    body.page-id-11 .elementor,
    body.page-id-689 #content,
    body.page-id-689 .site-content,
    body.page-id-689 .elementor,
    body.page-id-688 #content,
    body.page-id-688 .site-content,
    body.page-id-688 .elementor,
    body.page-id-1232 #content,
    body.page-id-1232 .site-content,
    body.page-id-1232 .elementor,
    body.page-id-319 #content,
    body.page-id-319 .site-content,
    body.page-id-319 .elementor {
        position: relative;
        z-index: 1;
    }


    /* v1.5.0 MOBILE: Only hide vortex when video IS playing.
       When video can't play (iOS), vortex serves as the animated background. */
    body.video-playing .portal-vortex,
    body.video-playing .vortex-ring {
        display: none !important;
        visibility: hidden !important;
    }
    body.video-playing .hero__particles {
        display: none !important;
    }
    .hero__logo {
        width: 70px !important;
        height: 70px !important;
        margin-bottom: 15px !important;
    }
    .hero__logo-glow {
        opacity: 0.1 !important;
        filter: blur(20px) !important;
    }
}
</style>'''

# Find the end of the old video handler css block
# Pattern: from '<style id="pb-video-handler-css">' to the closing '</style>'
video_css_pattern = r'<style id="pb-video-handler-css">.*?</style>'
match = re.search(video_css_pattern, content, re.DOTALL)
if match:
    old_video_block = match.group(0)
    if 'v1.3.0' in old_video_block:
        content = content.replace(old_video_block, NEW_VIDEO_CSS)
        print("SUCCESS: Upgraded pb-video-handler-css v1.3.0 -> v1.4.0/v1.5.0")
    else:
        print(f"WARNING: pb-video-handler-css found but version not v1.3.0 - skipping")
        version_match = re.search(r'v[\d.]+', old_video_block)
        if version_match:
            print(f"  Found version: {version_match.group(0)}")
else:
    print("WARNING: pb-video-handler-css not found")

# ============================================================
# FIX 3: Update title for proper homepage SEO
# ============================================================
OLD_TITLE = '\t<title>Elementor #1502 - Pure Brain</title>'
NEW_TITLE = '\t<title>PURE BRAIN &#8211; Your Brain. Your AI. Actual Intelligence!</title>'

if OLD_TITLE in content:
    content = content.replace(OLD_TITLE, NEW_TITLE)
    print("SUCCESS: Updated page title")
else:
    print("WARNING: Title not found for replacement")

# ============================================================
# FIX 4: Update OG title
# ============================================================
OLD_OG_TITLE = '\t<meta property="og:title" content="Elementor #1502 - Pure Brain" class="yoast-seo-meta-tag" />'
NEW_OG_TITLE = '\t<meta property="og:title" content="PURE BRAIN - Your Brain. Your AI. Actual Intelligence!" class="yoast-seo-meta-tag" />'

if OLD_OG_TITLE in content:
    content = content.replace(OLD_OG_TITLE, NEW_OG_TITLE)
    print("SUCCESS: Updated OG title")

# ============================================================
# FIX 5: Update canonical URL to homepage
# ============================================================
OLD_CANONICAL = '\t<link rel="canonical" href="https://purebrain.ai/elementor-1502/" class="yoast-seo-meta-tag" />'
NEW_CANONICAL = '\t<link rel="canonical" href="https://purebrain.ai/" class="yoast-seo-meta-tag" />'

if OLD_CANONICAL in content:
    content = content.replace(OLD_CANONICAL, NEW_CANONICAL)
    print("SUCCESS: Updated canonical URL to /")

# ============================================================
# FIX 6: Update twitter title tags
# ============================================================
content = content.replace(
    '<meta name="twitter:title" content="Elementor #1502" />',
    '<meta name="twitter:title" content="PURE BRAIN - Your Brain. Your AI. Actual Intelligence!" />'
)
print("SUCCESS: Updated twitter title")

# ============================================================
# Write output
# ============================================================
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nOutput written to: {OUTPUT}")
print(f"Output size: {len(content)} chars")
print("\nReady to deploy to CF Pages as homepage-test/")
