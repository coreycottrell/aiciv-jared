#!/usr/bin/env python3
"""
Inject GTM and Microsoft Clarity tracking into CF Pages HTML files.

GTM ID: GTM-WTDXL4VJ
Clarity Project: viy9bnc56x

Safety:
- Only modifies <head> sections
- Never touches PayPal, pricing, or seed flow code
- Skips files that already have the tracking
- Dry-run mode by default
"""

import os
import sys
import re

DEPLOY_DIR = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy"

GTM_HEAD_SNIPPET = """<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-WTDXL4VJ');</script>
<!-- End Google Tag Manager -->"""

GTM_BODY_SNIPPET = """<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WTDXL4VJ"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->"""

CLARITY_SNIPPET = """<!-- Microsoft Clarity -->
<script type="text/javascript">
(function(c,l,a,r,i,t,y){
    c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
    t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
    y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
})(window, document, "clarity", "script", "viy9bnc56x");
</script>"""


def find_all_html(base_dir):
    """Find all index.html files."""
    results = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f == "index.html":
                results.append(os.path.join(root, f))
    return sorted(results)


def needs_gtm(content):
    return "GTM-WTDXL4VJ" not in content


def needs_clarity(content):
    return "clarity.ms" not in content and "viy9bnc56x" not in content


def inject_tracking(filepath, dry_run=True):
    """Inject missing tracking into a single file. Returns (gtm_added, clarity_added)."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    original = content
    gtm_added = False
    clarity_added = False

    # Check what's needed
    add_gtm = needs_gtm(content)
    add_clarity = needs_clarity(content)

    if not add_gtm and not add_clarity:
        return False, False

    # Strategy: Insert right after <head> (or after <head>\n)
    # For GTM: goes first after <head>
    # For Clarity: goes after GTM (or after <head> if GTM already present)

    # Find the <head> tag - handle variations
    head_match = re.search(r'<head[^>]*>', content, re.IGNORECASE)
    if not head_match:
        print(f"  WARNING: No <head> tag found in {filepath}")
        return False, False

    head_end_pos = head_match.end()

    # Build injection string
    injection = ""
    if add_gtm:
        injection += "\n" + GTM_HEAD_SNIPPET
        gtm_added = True
    if add_clarity:
        injection += "\n" + CLARITY_SNIPPET
        clarity_added = True

    # Insert after <head>
    content = content[:head_end_pos] + injection + content[head_end_pos:]

    # For GTM, also add noscript tag after <body>
    if add_gtm:
        body_match = re.search(r'<body[^>]*>', content, re.IGNORECASE)
        if body_match:
            body_end_pos = body_match.end()
            content = content[:body_end_pos] + "\n" + GTM_BODY_SNIPPET + content[body_end_pos:]

    if not dry_run and content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    return gtm_added, clarity_added


def main():
    dry_run = "--apply" not in sys.argv

    if dry_run:
        print("=== DRY RUN MODE (pass --apply to write changes) ===\n")
    else:
        print("=== APPLYING CHANGES ===\n")

    html_files = find_all_html(DEPLOY_DIR)
    print(f"Found {len(html_files)} index.html files\n")

    gtm_needed = []
    clarity_needed = []
    gtm_fixed = []
    clarity_fixed = []
    errors = []

    for filepath in html_files:
        rel = os.path.relpath(filepath, DEPLOY_DIR)
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            if needs_gtm(content):
                gtm_needed.append(rel)
            if needs_clarity(content):
                clarity_needed.append(rel)

            g, c = inject_tracking(filepath, dry_run=dry_run)
            if g:
                gtm_fixed.append(rel)
            if c:
                clarity_fixed.append(rel)
        except Exception as e:
            errors.append((rel, str(e)))

    print(f"--- SUMMARY ---")
    print(f"Total pages: {len(html_files)}")
    print(f"Pages missing GTM: {len(gtm_needed)}")
    print(f"Pages missing Clarity: {len(clarity_needed)}")
    print(f"GTM {'would be' if dry_run else 'was'} added to: {len(gtm_fixed)} pages")
    print(f"Clarity {'would be' if dry_run else 'was'} added to: {len(clarity_fixed)} pages")

    if errors:
        print(f"\nErrors: {len(errors)}")
        for rel, err in errors:
            print(f"  {rel}: {err}")

    print(f"\n--- Pages needing GTM ({len(gtm_needed)}) ---")
    for p in gtm_needed:
        print(f"  {p}")

    print(f"\n--- Pages needing Clarity ({len(clarity_needed)}) ---")
    for p in clarity_needed:
        print(f"  {p}")


if __name__ == "__main__":
    main()
