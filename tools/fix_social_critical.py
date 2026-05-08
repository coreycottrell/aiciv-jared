#!/usr/bin/env python3
"""CRITICAL FIX: Remove duplicate const PLATFORM_COLORS that breaks ALL JS on social.purebrain.ai"""
import sys

PATH = '/home/jared/projects/AI-CIV/aether/from-chy/DEPLOY-THIS-MOBILE-FIX.html'

with open(PATH, 'r') as f:
    content = f.read()

# Count before
before = content.count("const PLATFORM_COLORS=")
print(f"Before: {before} declarations of const PLATFORM_COLORS")

if before != 2:
    print(f"Expected 2, got {before}. Aborting.")
    sys.exit(1)

# Fix: Replace the SECOND occurrence only
# The second one is in the analytics section
old_second = "// ========== ANALYTICS ==========\nconst PLATFORM_COLORS={linkedin:'#0a66c2',twitter:'#1da1f2',bluesky:'#0085ff',instagram:'#e4405f',facebook:'#1877f2',tiktok:'#69c9d0',reddit:'#ff4500',threads:'#000'};"
new_second = "// ========== ANALYTICS ==========\n// PLATFORM_COLORS: using declaration from kanban section above"

if old_second not in content:
    print("ERROR: Could not find second PLATFORM_COLORS block with exact match")
    # Try alternate
    alt = "const PLATFORM_COLORS={linkedin:'#0a66c2',twitter:'#1da1f2',bluesky:'#0085ff',instagram:'#e4405f',facebook:'#1877f2',tiktok:'#69c9d0',reddit:'#ff4500',threads:'#000'};"
    idx1 = content.find(alt)
    if idx1 == -1:
        print("ERROR: Cannot find second declaration at all")
        sys.exit(1)
    # Find the second occurrence
    idx2 = content.find(alt, idx1 + 1)
    if idx2 == -1:
        # The first occurrence has different instagram color - find both
        first_decl = "const PLATFORM_COLORS={linkedin:'#0a66c2',twitter:'#1da1f2',bluesky:'#0085ff',threads:'#000',instagram:'#e1306c',facebook:'#1877f2',tiktok:'#69c9d0',reddit:'#ff4500'};"
        second_decl = alt
        if first_decl in content and second_decl in content:
            # Update first to use #e4405f for instagram, remove second
            content = content.replace(first_decl, first_decl.replace("instagram:'#e1306c'", "instagram:'#e4405f'"))
            content = content.replace(second_decl, "// PLATFORM_COLORS: using declaration from kanban section above")
            print("Fixed via separate find-and-replace")
        else:
            print("Cannot locate declarations. Manual fix needed.")
            sys.exit(1)
    else:
        # Replace from idx2
        content = content[:idx2] + "// PLATFORM_COLORS: using declaration from kanban section above" + content[idx2+len(alt):]
        print("Fixed via index-based replacement")
else:
    content = content.replace(old_second, new_second)
    print("Fixed via exact match replacement")

# Also update first declaration's instagram color
content = content.replace("instagram:'#e1306c'", "instagram:'#e4405f'")

# Count after
after = content.count("const PLATFORM_COLORS=")
print(f"After: {after} declarations of const PLATFORM_COLORS")

if after != 1:
    print(f"CRITICAL: Expected 1 after fix, got {after}!")
    sys.exit(1)

# Also add console.log to login function
content = content.replace(
    "async function login(){\n  const btn=document.getElementById",
    "async function login(){\n  console.log('[social] login() called');\n  const btn=document.getElementById"
)

# Improve auto-boot catch handler
content = content.replace(
    "if(TOKEN){bootApp().catch(()=>{});}",
    "if(TOKEN){console.log('[social] Auto-boot with stored token');bootApp().catch(function(e){console.warn('[social] Auto-boot failed:',e);localStorage.removeItem('social_token');TOKEN='';});}"
)

# Update build comment
content = content.replace(
    "<!-- VERIFIED BUILD: 3185 lines, LinkedIn preview + Trello cards, 2026-04-20 10:15 UTC -->",
    "<!-- VERIFIED BUILD: login-fix+dayview+platform-captions, 2026-04-20 CTO sprint -->"
)

with open(PATH, 'w') as f:
    f.write(content)

print(f"\nVerification:")
print(f"  const PLATFORM_COLORS count: {content.count('const PLATFORM_COLORS=')}")
print(f"  login() console.log: {'[social] login() called' in content}")
print(f"  auto-boot improved: {'Auto-boot with stored token' in content}")
print(f"  Total lines: {len(content.splitlines())}")
print("\nSUCCESS - Critical fix applied!")
