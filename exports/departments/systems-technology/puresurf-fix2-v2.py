#!/usr/bin/env python3
"""FIX 2 v2: Fix the indentation of the TLS pre-navigation block."""
import re

filepath = '/opt/baas/baas_server_simple.py'

with open(filepath, 'r') as f:
    lines = f.readlines()

# Find and fix the TLS block (lines around 2126-2137)
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]

    # Find the comment "# Step 1: Navigate to establish TLS session"
    if '# Step 1: Navigate to establish TLS session with each auth domain' in line:
        # Write the comment line as-is (it's correct)
        new_lines.append(line)
        i += 1

        # Now fix the next lines until we hit "# Step 2"
        while i < len(lines):
            curr = lines[i]
            stripped = curr.strip()

            if '# Step 2:' in curr:
                # This is the end marker, write it and break
                new_lines.append(curr)
                i += 1
                break
            elif stripped == '':
                new_lines.append('\n')
                i += 1
                continue
            elif stripped.startswith("if 'linkedin.com'"):
                new_lines.append('                if ' + stripped[3:] + '\n')
                i += 1
            elif stripped.startswith('log.info') and 'establishing TLS' in stripped:
                new_lines.append('                    ' + stripped + '\n')
                i += 1
            elif stripped == 'try:':
                new_lines.append('                    try:\n')
                i += 1
            elif stripped.startswith('await page.goto') or stripped.startswith('await asyncio.sleep'):
                new_lines.append('                        ' + stripped + '\n')
                i += 1
            elif stripped.startswith('log.info') and 'TLS session established' in stripped:
                new_lines.append('                        ' + stripped + '\n')
                i += 1
            elif stripped.startswith('except'):
                new_lines.append('                    ' + stripped + '\n')
                i += 1
            elif stripped.startswith('log.warning') and 'TLS pre-navigation' in stripped:
                new_lines.append('                        ' + stripped + '\n')
                i += 1
            else:
                new_lines.append(curr)
                i += 1
    else:
        new_lines.append(line)
        i += 1

with open(filepath, 'w') as f:
    f.writelines(new_lines)

print("FIX 2 v2: COMPLETE — TLS pre-navigation indentation fixed")
