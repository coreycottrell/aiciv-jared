#!/usr/bin/env python3
"""Deploy PureSurf Mega-Upgrade: Replace 3 tab panels + inject new CSS/JS"""

import re
import sys

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def main():
    # Read existing index.html
    html = read_file('/var/www/puresurf/index.html')

    # Read upgrade components
    tab_workflows = read_file('/tmp/puresurf-upgrade/tab-workflows.html')
    tab_smart_nav = read_file('/tmp/puresurf-upgrade/tab-smart-nav.html')
    tab_orchestration = read_file('/tmp/puresurf-upgrade/tab-orchestration.html')
    mega_css = read_file('/tmp/puresurf-upgrade/mega-upgrade-styles.css')
    mega_js = read_file('/tmp/puresurf-upgrade/mega-upgrade-js.js')

    # 1. Replace workflows panel
    # Find existing panel-workflows and replace
    wf_pattern = r'<div id="panel-workflows" class="panel">.*?</div>\s*</div>\s*</div>\s*</div>'
    if re.search(wf_pattern, html, re.DOTALL):
        html = re.sub(wf_pattern, tab_workflows.strip(), html, count=1, flags=re.DOTALL)
        print("[OK] Replaced workflows panel")
    else:
        # Try simpler pattern
        wf_start = html.find('<div id="panel-workflows" class="panel">')
        if wf_start >= 0:
            # Find the next panel or main closing tag
            wf_end = html.find('<div id="panel-smart-nav"', wf_start)
            if wf_end > wf_start:
                html = html[:wf_start] + tab_workflows.strip() + '\n' + html[wf_end:]
                print("[OK] Replaced workflows panel (simple)")
            else:
                print("[WARN] Could not find workflows panel end")
        else:
            print("[WARN] Could not find workflows panel")

    # 2. Replace smart-nav panel
    sn_start = html.find('<div id="panel-smart-nav" class="panel">')
    if sn_start >= 0:
        sn_end = html.find('<div id="panel-orchestration"', sn_start)
        if sn_end > sn_start:
            html = html[:sn_start] + tab_smart_nav.strip() + '\n' + html[sn_end:]
            print("[OK] Replaced smart-nav panel")
        else:
            print("[WARN] Could not find smart-nav panel end")
    else:
        print("[WARN] Could not find smart-nav panel")

    # 3. Replace orchestration panel
    orch_start = html.find('<div id="panel-orchestration" class="panel">')
    if orch_start >= 0:
        # Find the closing - look for the next panel or proxy-settings
        orch_end = html.find('<div class="panel" id="panel-proxy-settings">', orch_start)
        if orch_end < 0:
            orch_end = html.find('<div id="panel-proxy-settings"', orch_start)
        if orch_end > orch_start:
            html = html[:orch_start] + tab_orchestration.strip() + '\n' + html[orch_end:]
            print("[OK] Replaced orchestration panel")
        else:
            print("[WARN] Could not find orchestration panel end")
    else:
        print("[WARN] Could not find orchestration panel")

    # 4. Inject mega CSS before </style> (the first one)
    css_inject = '\n/* ==================== MEGA-UPGRADE STYLES ==================== */\n' + mega_css
    # Find the main </style> tag
    style_end = html.find('</style>')
    if style_end >= 0:
        html = html[:style_end] + css_inject + '\n' + html[style_end:]
        print("[OK] Injected mega CSS")

    # 5. Inject mega JS before </body>
    js_inject = '\n<script>\n/* ==================== MEGA-UPGRADE JS ==================== */\n' + mega_js + '\n</script>\n'
    body_end = html.rfind('</body>')
    if body_end >= 0:
        html = html[:body_end] + js_inject + html[body_end:]
        print("[OK] Injected mega JS")

    # 6. Remove old WF/SN JS modules that conflict (the IIFE at the beginning)
    # Remove the old (function() { ... WF module from the first <script> block
    # We keep the ORCH IIFE since our code extends it

    # Write output
    with open('/var/www/puresurf/index.html', 'w') as f:
        f.write(html)

    print(f"\n[DONE] Deployed! File size: {len(html)} bytes ({len(html.splitlines())} lines)")

if __name__ == '__main__':
    main()
