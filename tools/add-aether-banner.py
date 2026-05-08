#!/usr/bin/env python3
"""Add 'Built by Aether' footer banner to all CF Pages deploy pages.
Excludes investor pages, internal infrastructure, and pages that already have the banner."""

import os
import re

DEPLOY_DIR = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy"

# Directories to EXCLUDE (no banner)
EXCLUDE_DIRS = {
    # Investor / Chy pages
    "investment-opportunity",
    "investment-opportunity-backup",
    "investment-opportunity-backup-2",
    "investor-avatar",
    "investor-avatar-max",
    "investor-avatar-v2",
    "investor-avatar-v3",
    "investor-intelligence",
    "investor-one-pager",
    "investor-tracking",
    "investors",
    "investors-ask-aether",
    "investors-ask-aether-v2",
    "investors-ask-aether-v3",
    "investors-ask-aether-v4",
    "investors-onepager",
    "investors-onepager-3d",
    "investors-v5-fluid",
    "investors-v6",
    "investors-v7",
    "investors-v8",
    "investors-v9",
    "investors-v10",
    "investors-v11",
    "investors-v12",
    "investors-v13",
    "investors-v14",
    "investors-v15",
    "investors-v16",
    "investor-entrance",
    "invest",
    # Other investor/Chy pages from banner doc
    "aether-awakening",
    "gifts",
    "chy-guardian",
    "aether-guardian",
    "aether-guardian-template",
    # Internal infrastructure
    "777-command-center",
    "ceo-dashboard",
    "triangle-os",
    "functions",
    # Prototypes/experiments from banner doc
    "avatar-builder",
    "avatar-prototype",
    "avatar-prototype-v2",
    "avatar-demo",
    # 3d prototypes
    "3d-brain",
    "3d-brain-homepage",
    "3d-brain-immersive",
    "3d-brain-v2",
    "3d-brain-v3",
    "3d-homepage",
    "3d-homepage-v2",
    "3d-homepage-v3",
    "3d-training",
    # Test/sandbox pages
    "pay-test",
    "pay-test-2",
    "pay-test-3",
    "pay-test-4",
    "pay-test-5",
    "home-test",
    "home-test-1",
    "home-test-2",
    "home-test-3",
    "home-test-4",
    "home-test-5",
    "home-experiment",
    "home-experiment-1",
    "home-experiment-2",
    # WP artifacts
    "elementor-hf",
    # Static asset dirs (no index.html typically but just in case)
    "assets",
    "css",
    "js",
    "wp-content",
    "d1-migrations",
}

# Also exclude patterns
EXCLUDE_PREFIXES = [
    "investor-",  # catch any investor- pages not explicitly listed
    "investors-v",  # catch investors-v5 through v16+
]

BANNER_CSS = """
/* Built by Aether Footer */
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
#pb-aether-footer a { text-decoration: none !important; transition: color 0.2s ease, text-shadow 0.2s ease; }
#pb-aether-footer a:hover { background: none !important; text-decoration: none !important; }
#pb-aether-footer .pb-footer-label { color: #9ca3af; font-weight: 400; }
#pb-aether-footer .pb-footer-aether {
    font-weight: 800; font-size: 15px; letter-spacing: 0.12em;
    color: #f1420b;
    text-shadow: 0 0 8px rgba(241, 66, 11, 0.7), 0 0 20px rgba(241, 66, 11, 0.35), 0 0 40px rgba(241, 66, 11, 0.15);
    text-transform: uppercase;
    animation: pb-aether-pulse 3s ease-in-out infinite;
}
#pb-aether-footer .pb-footer-ai-tag { color: #6b7280; font-size: 11px; font-style: italic; }
#pb-aether-footer .pb-footer-for { color: #9ca3af; }
#pb-aether-footer .pb-footer-purebrain { color: #f1420b; font-weight: 700; text-shadow: 0 0 6px rgba(241, 66, 11, 0.4); }
#pb-aether-footer .pb-footer-purebrain:hover { color: #ff6633 !important; text-shadow: 0 0 12px rgba(241, 66, 11, 0.7) !important; }
#pb-aether-footer .pb-footer-blue { color: #2a93c1; font-weight: 600; }
#pb-aether-footer .pb-footer-blue:hover { color: #f1420b !important; text-shadow: 0 0 8px rgba(241, 66, 11, 0.5) !important; }
#pb-aether-footer .pb-footer-sep { color: rgba(255, 255, 255, 0.12); margin: 0 12px; font-weight: 300; }
#pb-aether-footer .pb-footer-why,
#pb-aether-footer .pb-footer-mission,
#pb-aether-footer .pb-footer-migrate {
    color: #2a93c1; font-weight: 700; font-size: 12px; letter-spacing: 0.04em;
    padding: 4px 10px; border: 1px solid rgba(42, 147, 193, 0.4); border-radius: 4px;
    transition: all 0.2s ease; background: rgba(42, 147, 193, 0.08);
}
#pb-aether-footer .pb-footer-why:hover,
#pb-aether-footer .pb-footer-mission:hover,
#pb-aether-footer .pb-footer-migrate:hover {
    color: #ffffff !important; background: #f1420b !important; border-color: #f1420b !important;
    box-shadow: 0 0 12px rgba(241, 66, 11, 0.5); text-shadow: none;
}
@media (max-width: 600px) {
    #pb-aether-footer { height: auto !important; min-height: 52px; padding: 8px 16px; font-size: 11px; flex-wrap: wrap; row-gap: 4px; }
    #pb-aether-footer .pb-footer-aether { font-size: 13px; }
    #pb-aether-footer .pb-footer-why, #pb-aether-footer .pb-footer-migrate { display: none !important; }
    #pb-aether-footer .pb-footer-sep-why, #pb-aether-footer .pb-footer-sep-before-mission, #pb-aether-footer .pb-footer-sep-migrate { display: none !important; }
    body { padding-bottom: 80px !important; }
}
body { padding-bottom: 64px !important; }
"""

BANNER_HTML = """<!-- Built by Aether Credit Bar -->
<div id="pb-aether-footer">
    <span class="pb-footer-label">Built by&nbsp;</span><span class="pb-footer-aether">AETHER</span>&nbsp;<span class="pb-footer-ai-tag">(an AI)</span>&nbsp;<span class="pb-footer-for">for&nbsp;</span><a href="https://purebrain.ai" target="_blank" rel="noopener" class="pb-footer-purebrain"><span style="color:#2a93c1">PureBr</span><span style="color:#f1420b">ai</span><span style="color:#2a93c1">n</span>.ai</a>,&nbsp;<a href="https://puremarketing.ai" target="_blank" rel="noopener" class="pb-footer-blue">PureMarketing.ai</a>&nbsp;&amp;&nbsp;<a href="https://puretechnology.nyc" target="_blank" rel="noopener" class="pb-footer-blue">PureTechnology.ai</a><span class="pb-footer-sep pb-footer-sep-why">|</span><a href="https://purebrain.ai/why-purebrain/" rel="noopener" class="pb-footer-why">Why Choose PureBrain?</a><span class="pb-footer-sep pb-footer-sep-before-mission">|</span><a href="https://purebrain.ai/mission-vision-values/" rel="noopener" class="pb-footer-mission">Mission &amp; Values</a><span class="pb-footer-sep pb-footer-sep-migrate">|</span><a href="https://purebrain.ai/compare/" rel="noopener" class="pb-footer-migrate">Compare</a>
</div>
"""

def should_exclude(dirname):
    """Check if a directory should be excluded from banner injection."""
    if dirname in EXCLUDE_DIRS:
        return True
    for prefix in EXCLUDE_PREFIXES:
        if dirname.startswith(prefix):
            return True
    return False

def add_banner(filepath):
    """Add banner CSS and HTML to an index.html file. Returns status string."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Already has banner?
    if 'pb-aether-footer' in content:
        return 'already_has_banner'

    # Must have </body> and (</head> or <style>)
    if '</body>' not in content.lower():
        return 'no_body_tag'

    modified = content

    # Add CSS: prefer inserting before </head>, or inside last <style> block
    if '</head>' in modified:
        modified = modified.replace('</head>', f'<style>{BANNER_CSS}</style>\n</head>', 1)
    elif '</HEAD>' in modified:
        modified = modified.replace('</HEAD>', f'<style>{BANNER_CSS}</style>\n</HEAD>', 1)
    else:
        # No head tag - add style before body
        modified = f'<style>{BANNER_CSS}</style>\n' + modified

    # Add HTML before </body>
    if '</body>' in modified:
        modified = modified.replace('</body>', f'{BANNER_HTML}\n</body>', 1)
    elif '</BODY>' in modified:
        modified = modified.replace('</BODY>', f'{BANNER_HTML}\n</BODY>', 1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(modified)

    return 'modified'

def main():
    modified = []
    skipped_already = []
    excluded_investor = []
    excluded_other = []
    skipped_no_body = []
    skipped_homepage = False

    for entry in sorted(os.listdir(DEPLOY_DIR)):
        index_path = os.path.join(DEPLOY_DIR, entry, "index.html")

        # Root index.html
        if entry == "index.html":
            print(f"SKIP (homepage): {DEPLOY_DIR}/index.html")
            skipped_homepage = True
            continue

        if not os.path.isdir(os.path.join(DEPLOY_DIR, entry)):
            continue

        if not os.path.exists(index_path):
            continue

        # Check exclusion
        if should_exclude(entry):
            excluded_investor.append(entry)
            print(f"EXCLUDE: {entry}/")
            continue

        # Process the file
        status = add_banner(index_path)

        if status == 'modified':
            modified.append(entry)
            print(f"MODIFIED: {entry}/")
        elif status == 'already_has_banner':
            skipped_already.append(entry)
            print(f"SKIP (already has banner): {entry}/")
        elif status == 'no_body_tag':
            skipped_no_body.append(entry)
            print(f"SKIP (no </body> tag): {entry}/")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Modified:                {len(modified)}")
    print(f"Skipped (already):       {len(skipped_already)}")
    print(f"Skipped (homepage):      {1 if skipped_homepage else 0}")
    print(f"Skipped (no body tag):   {len(skipped_no_body)}")
    print(f"Excluded (investor/etc): {len(excluded_investor)}")
    print(f"Total pages found:       {len(modified) + len(skipped_already) + len(excluded_investor) + len(skipped_no_body) + (1 if skipped_homepage else 0)}")

    if skipped_no_body:
        print(f"\nPages with no </body> tag: {skipped_no_body}")

    if skipped_already:
        print(f"\nPages already with banner: {skipped_already[:10]}{'...' if len(skipped_already) > 10 else ''}")

if __name__ == "__main__":
    main()
