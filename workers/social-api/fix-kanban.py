#!/usr/bin/env python3
"""Fix kanban CSS issues in worker.js and DEPLOY-THIS-MOBILE-FIX.html"""
import re

files = [
    '/home/jared/projects/AI-CIV/aether/workers/social-api/src/worker.js',
    '/home/jared/projects/AI-CIV/aether/from-chy/DEPLOY-THIS-MOBILE-FIX.html',
]

for fpath in files:
    with open(fpath, 'r') as f:
        content = f.read()

    original = content

    # Fix 1: .kanban-col — remove max-width, change min-width to 300px
    content = content.replace(
        '.kanban-col{flex:1;min-width:280px;max-width:420px;',
        '.kanban-col{flex:1;min-width:300px;'
    )

    # Fix 2: .kanban-card — add flex-shrink:0
    content = content.replace(
        '.kanban-card{background:rgba(255,255,255,0.025);',
        '.kanban-card{flex-shrink:0;background:rgba(255,255,255,0.025);'
    )

    if content != original:
        with open(fpath, 'w') as f:
            f.write(content)
        print(f"FIXED: {fpath}")

        # Verify changes
        if 'min-width:300px' in content and 'max-width:420px' not in content.split('.kanban-col{')[1].split('}')[0]:
            print(f"  OK: .kanban-col min-width:300px, no max-width cap")
        if '.kanban-card{flex-shrink:0;' in content:
            print(f"  OK: .kanban-card has flex-shrink:0")
    else:
        print(f"NO CHANGES: {fpath}")
