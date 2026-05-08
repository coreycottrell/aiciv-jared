#!/usr/bin/env python3
"""
Fix social.purebrain.ai frontend - CRITICAL: duplicate const breaks ALL JS
"""
import sys

PATH = '/home/jared/projects/AI-CIV/aether/from-chy/DEPLOY-THIS-MOBILE-FIX.html'

with open(PATH, 'r') as f:
    lines = f.readlines()

# ====== FIX 1: Remove duplicate const PLATFORM_COLORS (CRITICAL) ======
first_pc = None
second_pc = None
for i, line in enumerate(lines):
    if "const PLATFORM_COLORS={" in line and "linkedin:" in line:
        if first_pc is None:
            first_pc = i
            # Update first occurrence to have the best instagram color
            lines[i] = line.replace("instagram:'#e1306c'", "instagram:'#e4405f'")
        else:
            second_pc = i
            # Replace second with comment
            lines[i] = "// PLATFORM_COLORS already declared in kanban section\n"
            break

if second_pc:
    print(f"FIX 1: Removed duplicate const PLATFORM_COLORS at line {second_pc+1} (first at {first_pc+1})")
else:
    print("FIX 1: WARNING - second const PLATFORM_COLORS not found!")

# ====== FIX 2: Improve login with console logging ======
for i, line in enumerate(lines):
    if "async function login(){" in line:
        lines[i] = line.replace(
            "async function login(){",
            "async function login(){\n  console.log('[social] login() called');"
        )
        print(f"FIX 2: Added console.log to login() at line {i+1}")
        break

# ====== FIX 3: Improve auto-boot catch handler ======
for i, line in enumerate(lines):
    if "if(TOKEN){bootApp().catch(()=>{});}" in line:
        lines[i] = line.replace(
            "if(TOKEN){bootApp().catch(()=>{});}",
            "if(TOKEN){console.log('[social] Auto-boot with stored token');bootApp().catch(function(e){console.warn('[social] Auto-boot failed:',e);localStorage.removeItem('social_token');TOKEN='';});}"
        )
        print(f"FIX 3: Improved auto-boot catch at line {i+1}")
        break

# ====== FIX 4: Add dayOffset variable ======
for i, line in enumerate(lines):
    if "let monthOffset = 0;" in line:
        lines[i] = line.replace(
            "let monthOffset = 0;",
            "let monthOffset = 0;\nlet dayOffset = 0;"
        )
        print(f"FIX 4: Added dayOffset variable at line {i+1}")
        break

# ====== FIX 5: Add day view toggle button ======
for i, line in enumerate(lines):
    if "setCalendarView('list')\">List</button>" in line:
        indent = line[:len(line) - len(line.lstrip())]
        lines[i] = indent + '<button class="view-toggle-btn" onclick="setCalendarView(\'day\')">Day</button>\n' + line
        print(f"FIX 5: Added Day view button at line {i+1}")
        break

# ====== FIX 6: Add day-view container div ======
for i, line in enumerate(lines):
    if '<div id="list-view-container"' in line:
        indent = line[:len(line) - len(line.lstrip())]
        day_div = indent + '<!-- Day View -->\n'
        day_div += indent + '<div id="day-view-container" style="display:none;">\n'
        day_div += indent + '  <div id="day-view-content"></div>\n'
        day_div += indent + '</div>\n\n'
        lines[i] = day_div + line
        print(f"FIX 6: Added day-view container at line {i+1}")
        break

# ====== FIX 7: Update build comment ======
for i, line in enumerate(lines):
    if "VERIFIED BUILD:" in line:
        lines[i] = "<!-- VERIFIED BUILD: social.purebrain.ai, login-fix+dayview+platform-captions, 2026-04-20 CTO sprint -->\n"
        print(f"FIX 7: Updated build comment at line {i+1}")
        break

# Write result
with open(PATH, 'w') as f:
    f.writelines(lines)

# Verify
with open(PATH, 'r') as f:
    content = f.read()

count = content.count("const PLATFORM_COLORS=")
print(f"\nVerification:")
print(f"  const PLATFORM_COLORS declarations: {count} (must be 1)")
print(f"  login() exists: {'async function login()' in content}")
print(f"  bootApp() exists: {'async function bootApp()' in content}")
print(f"  day-view-container exists: {'day-view-container' in content}")
print(f"  Total lines: {content.count(chr(10))+1}")

if count != 1:
    print("\n*** CRITICAL: const PLATFORM_COLORS count is not 1! ***")
    sys.exit(1)
