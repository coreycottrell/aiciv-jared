#!/usr/bin/env python3
"""
Fix the double-apostrophe issue in expand_and_update.py, then run it.

Usage: python3 exports/content-expand/run.py
"""
import os

script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expand_and_update.py")

with open(script_path) as f:
    content = f.read()

# Insert cleanup line before STEP 3
marker = "# STEP 3: UPDATE D1"
cleanup = """# Clean up double-apostrophes from content (not needed with parameterized queries)
EXPANDED = {k: v.replace("''", "'") for k, v in EXPANDED.items()}

# """

if "Clean up double-apostrophes" not in content:
    content = content.replace("# " + marker, cleanup + marker)
    with open(script_path, "w") as f:
        f.write(content)
    print("[FIX] Added apostrophe cleanup to expand_and_update.py")
else:
    print("[OK] Apostrophe cleanup already present")

# Now run it
print("[RUN] Executing expand_and_update.py...\n")
exec(compile(open(script_path).read(), script_path, "exec"))
