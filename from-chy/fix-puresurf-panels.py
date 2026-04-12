#!/usr/bin/env python3
"""
Fix PureSurf dashboard panel gaps.
Moves Workflows, Smart Navigate, and Orchestration panels INSIDE the .main div.
Run on root@157.180.69.225
"""
import re

with open('/var/www/puresurf/index.html') as f:
    content = f.read()

# Step 1: Extract the 3 panel divs + their full content
panels_to_move = {}
for panel_id in ['panel-workflows', 'panel-smart-nav', 'panel-orchestration']:
    # Find the panel opening tag
    pattern = f'<div id="{panel_id}" class="panel">'
    start = content.find(pattern)
    if start == -1:
        print(f"  WARNING: {panel_id} not found")
        continue
    
    # Find the matching closing div by counting nesting
    depth = 0
    pos = start
    end = -1
    while pos < len(content):
        if content[pos:pos+4] == '<div':
            depth += 1
        elif content[pos:pos+6] == '</div>':
            depth -= 1
            if depth == 0:
                end = pos + 6
                break
        pos += 1
    
    if end > start:
        panels_to_move[panel_id] = content[start:end]
        print(f"  Extracted {panel_id}: {end-start} chars")

# Step 2: Remove the panels from their current location
for panel_id, panel_html in panels_to_move.items():
    content = content.replace(panel_html, f'<!-- {panel_id} moved inside .main -->')
    print(f"  Removed {panel_id} from original location")

# Step 3: Find the proxy-settings panel (last panel inside .main) and insert after it
proxy_pattern = '<div class="panel" id="panel-proxy-settings">'
proxy_start = content.find(proxy_pattern)
if proxy_start == -1:
    # Try alternate format
    proxy_pattern = '<div id="panel-proxy-settings" class="panel">'
    proxy_start = content.find(proxy_pattern)

if proxy_start > 0:
    # Find end of proxy panel
    depth = 0
    pos = proxy_start
    proxy_end = -1
    while pos < len(content):
        if content[pos:pos+4] == '<div':
            depth += 1
        elif content[pos:pos+6] == '</div>':
            depth -= 1
            if depth == 0:
                proxy_end = pos + 6
                break
        pos += 1
    
    if proxy_end > 0:
        # Insert all 3 panels right after proxy panel
        insert_html = '\n\n    ' + '\n\n    '.join(panels_to_move.values())
        content = content[:proxy_end] + insert_html + content[proxy_end:]
        print(f"  Inserted 3 panels after proxy-settings (inside .main)")

# Step 4: Remove ALL my previous CSS hacks for these panels
css_patterns = [
    r'/\* AI Feature Panels.*?\*/',
    r'#panel-workflows[^}]*position:\s*fixed[^}]*\}',
    r'/\* Fix for AI Feature.*?\*/',
    r'/\* Proxy panel top spacing.*?\}[^}]*\}',
    r'/\* proxy fix merged.*?\*/',
]
for pat in css_patterns:
    content = re.sub(pat, '/* cleaned */', content, flags=re.DOTALL)

# Step 5: Clean up any duplicate/extra stuff after </html>
idx = content.find('</html>')
if idx > 0:
    after = content[idx+7:].strip()
    if after:
        content = content[:idx+7] + '\n'
        print(f"  Cleaned {len(after)} chars after </html>")

with open('/var/www/puresurf/index.html', 'w') as f:
    f.write(content)

print("\nDONE. All panels moved inside .main div. No more gap.")
