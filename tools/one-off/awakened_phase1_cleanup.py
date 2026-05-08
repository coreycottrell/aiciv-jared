#!/usr/bin/env python3
"""
Phase 1 contamination cleanup for /insiders/awakened/ pages.
Delegated by dept-systems-technology under ST# directive 2026-04-14.

Applies 4 targeted patches:
  1. Delete line 2857 (wpadminbar single-line div)
  2. Delete Elementor + media-modal <script type="text/template"> blocks
     starting at line 11109 mid-line and ending at the first legitimate
     non-WP-template line after 11260.
  3. Fix canonical URL (elementor-1502 -> insiders/awakened)
  4. Fix JSON-LD schema (names + URLs)

Preserves:
  - PayPal SDK integration
  - RETURN_URL / CANCEL_URL (per-file)
  - form_submit_success dataLayer push (line ~10514)

Stage only. Does NOT deploy.
"""
import re
import sys
from pathlib import Path

ROOT = Path("/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/insiders")
FILES = [
    ("awakened",         ROOT / "awakened" / "index.html"),
    ("pay-test-awakened", ROOT / "pay-test-awakened" / "index.html"),
]

# All admin-template / WP-admin script IDs that must be stripped.
# These are <script type="text/template" id="..."> or
# <script type="text/html" id="tmpl-..."> blocks that ship the WP admin UI.
WP_TEMPLATE_IDS = re.compile(
    r'tmpl-elementor|tmpl-media-|tmpl-uploader-|tmpl-attachment|'
    r'tmpl-image-details|tmpl-edit-attachment|tmpl-audio-details|'
    r'tmpl-video-details|tmpl-embed-|tmpl-crop-content|tmpl-file-|'
    r'tmpl-image-editor|tmpl-iframe-|tmpl-site-icon-|'
    r'tmpl-gallery-|tmpl-playlist-|tmpl-media-library-|'
    r'tmpl-uploader-window|tmpl-uploader-editor|tmpl-uploader-inline|'
    r'tmpl-uploader-status'
)


def patch_file(label: str, path: Path) -> dict:
    assert path.exists(), f"Missing: {path}"
    original = path.read_text(encoding="utf-8")
    before_size = len(original.encode("utf-8"))
    lines = original.split("\n")

    removed = {
        "wpadminbar_line": 0,
        "template_blocks": 0,
        "canonical_fixed": 0,
        "schema_fixed": 0,
        "og_title_fixed": 0,
        "twitter_title_fixed": 0,
    }

    # ------------------------------------------------------------------
    # Patch 1: delete wpadminbar line (single-line, 41 chars unopened div
    # that pulled the entire admin bar DOM as a sibling via WP output).
    # The actual content is line 2857 = '\t\t<div id="wpadminbar" class="nojq nojs">'
    # Since the admin bar closing tags are interleaved in later lines we
    # remove the opening tag only (browser will not render an unopened div
    # correctly — but the CSS already hides #wpadminbar via !important).
    # For safety we keep existing CSS hide rules intact.
    # ------------------------------------------------------------------
    new_lines = []
    for idx, line in enumerate(lines, start=1):
        if idx == 2857 and 'id="wpadminbar"' in line:
            removed["wpadminbar_line"] += 1
            continue  # drop it
        new_lines.append(line)
    lines = new_lines

    # ------------------------------------------------------------------
    # Patch 2: strip WP template blocks.
    # Strategy: rebuild source, find every <script type="text/(template|html)"
    # id="(tmpl-...)"> ... </script> whose id matches WP_TEMPLATE_IDS and
    # remove the whole block (inline or multi-line).
    # ------------------------------------------------------------------
    src = "\n".join(lines)

    # Regex: match script open tag with WP tmpl id + lazy content + </script>
    # The type can be "text/template" or "text/html" (uploader blocks use html).
    tmpl_pattern = re.compile(
        r'<script\s+type="text/(?:template|html)"\s+id="('
        + WP_TEMPLATE_IDS.pattern
        + r')[^"]*"[^>]*>.*?</script>',
        flags=re.DOTALL,
    )
    removed["template_blocks"] = len(tmpl_pattern.findall(src))
    src = tmpl_pattern.sub("", src)

    # ------------------------------------------------------------------
    # Patch 3: canonical URL + og:url fix
    # ------------------------------------------------------------------
    target_slug = "insiders/awakened" if label == "awakened" else "insiders/pay-test-awakened"
    # Canonical + og:url
    canonical_re = re.compile(r'https://purebrain\.ai/elementor-1502/?')
    count_before = len(canonical_re.findall(src))
    src = canonical_re.sub(f"https://purebrain.ai/{target_slug}/", src)
    removed["canonical_fixed"] = count_before

    # ------------------------------------------------------------------
    # Patch 4: JSON-LD schema + og:title + twitter:title + <title>
    # Replace "Elementor #1502 - Pure Brain" and "Elementor #1502"
    # ------------------------------------------------------------------
    page_name = "Awakened - Pure Brain" if label == "awakened" else "Pay Test Awakened - Pure Brain"
    short_name = "Awakened" if label == "awakened" else "Pay Test Awakened"

    c1 = src.count("Elementor #1502 - Pure Brain")
    src = src.replace("Elementor #1502 - Pure Brain", page_name)
    c2 = src.count("Elementor #1502")
    src = src.replace("Elementor #1502", short_name)
    removed["schema_fixed"] = c1 + c2

    # Write
    path.write_text(src, encoding="utf-8")
    after_size = len(src.encode("utf-8"))

    return {
        "label": label,
        "path": str(path),
        "before_bytes": before_size,
        "after_bytes": after_size,
        "delta_bytes": before_size - after_size,
        "removed": removed,
    }


def verify_payment_guard(path: Path) -> dict:
    """Payment guard: PayPal + RETURN_URL + CANCEL_URL + form_submit_success intact."""
    content = path.read_text(encoding="utf-8")
    checks = {
        "paypal_client_id_present": "PAYPAL_CLIENT_ID" in content,
        "paypal_sdk_script": "paypal.com/sdk/js" in content or "paypalobjects" in content or "AWgWNlBQAy5BMXKB5xbaMwSk" in content,
        "return_url_present": "RETURN_URL" in content,
        "cancel_url_present": "CANCEL_URL" in content,
        "form_submit_success_datalayer": "form_submit_success" in content,
        "pb_paypal_overlay_css": "pb-paypal-overlay" in content,
    }
    checks["ALL_PASS"] = all(v for k, v in checks.items() if k != "ALL_PASS")
    return checks


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 1 AWAKENED CONTAMINATION CLEANUP")
    print("=" * 70)
    results = []
    for label, path in FILES:
        print(f"\n[{label}] {path}")
        r = patch_file(label, path)
        results.append(r)
        print(f"  Before: {r['before_bytes']:,} bytes")
        print(f"  After:  {r['after_bytes']:,} bytes")
        print(f"  Saved:  {r['delta_bytes']:,} bytes")
        print(f"  Removed: {r['removed']}")

    print("\n" + "=" * 70)
    print("PAYMENT GUARD VERIFICATION")
    print("=" * 70)
    for label, path in FILES:
        g = verify_payment_guard(path)
        status = "PASS" if g["ALL_PASS"] else "FAIL"
        print(f"\n[{label}] Payment Guard: {status}")
        for k, v in g.items():
            if k != "ALL_PASS":
                print(f"    {'OK ' if v else 'XX '} {k}")

    print("\nDONE. Staged — NOT deployed.")
