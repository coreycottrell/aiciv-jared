#!/usr/bin/env python3
"""
Fix HTML entities inside <script> blocks in Cloudflare Pages deploy files.
WordPress encodes & as &#038; inside script blocks, breaking JavaScript.
This script decodes those entities back to their proper characters.
"""

import re
import html
import shutil
from pathlib import Path

FILES_TO_FIX = [
    "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/pay-test-2/index.html",
    "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/pay-test-sandbox-3/index.html",
]

# HTML entities that are invalid inside <script> blocks
# These are WordPress wpautop/wptexturize artifacts
ENTITIES_TO_FIX_IN_SCRIPTS = {
    "&#038;": "&",   # ampersand - breaks && operators
    "&#8217;": "'",  # right single quote - breaks string literals
    "&#8216;": "'",  # left single quote
    "&#8220;": '"',  # left double quote
    "&#8221;": '"',  # right double quote
    "&#8211;": "-",  # en dash
    "&#8212;": "--", # em dash
    "&amp;": "&",    # HTML ampersand entity
}

def fix_script_entities(content: str) -> tuple[str, int]:
    """
    Find all <script> blocks and decode HTML entities inside them.
    Returns (fixed_content, count_of_fixes)
    """
    total_fixes = 0

    def fix_script_block(match):
        nonlocal total_fixes
        full_tag = match.group(0)
        opening = match.group(1)
        script_content = match.group(2)
        closing = match.group(3)

        # Don't fix JSON-LD scripts (they're valid JSON, not JS)
        if 'type="application/ld+json"' in opening or "type='application/ld+json'" in opening:
            return full_tag

        # Fix entities in JS content
        fixed = script_content
        for entity, replacement in ENTITIES_TO_FIX_IN_SCRIPTS.items():
            count = fixed.count(entity)
            if count > 0:
                fixed = fixed.replace(entity, replacement)
                total_fixes += count
                print(f"  Fixed {count} x {entity} -> {repr(replacement)}")

        return f"{opening}{fixed}{closing}"

    # Match <script...>content</script> including multiline content
    pattern = re.compile(
        r'(<script[^>]*>)(.*?)(</script>)',
        re.DOTALL | re.IGNORECASE
    )

    fixed_content = pattern.sub(fix_script_block, content)
    return fixed_content, total_fixes


def fix_file(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"FILE NOT FOUND: {filepath}")
        return False

    print(f"\nProcessing: {filepath}")
    print(f"  Size: {path.stat().st_size} bytes")

    # Backup original
    backup_path = path.with_suffix(".html.bak")
    shutil.copy2(str(path), str(backup_path))
    print(f"  Backup: {backup_path}")

    # Read file
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Fix entities
    fixed_content, total_fixes = fix_script_entities(content)

    if total_fixes == 0:
        print("  No entities found to fix")
        backup_path.unlink()  # Remove backup if no changes
        return False

    # Write fixed content
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(fixed_content)

    print(f"  Total fixes applied: {total_fixes}")
    print(f"  New size: {path.stat().st_size} bytes")

    # Verify with node
    import subprocess
    import re as re2

    with open(filepath, "r", encoding="utf-8") as f:
        new_content = f.read()

    scripts = re2.findall(r'<script[^>]*>(.*?)</script>', new_content, re2.DOTALL)
    print(f"  Verifying {len(scripts)} script blocks...")

    error_count = 0
    for i, s in enumerate(scripts):
        if len(s.strip()) < 50:
            continue
        if s.strip().startswith("{"):
            continue
        with open("/tmp/verify_script.js", "w") as f:
            f.write(s)
        result = subprocess.run(["node", "--check", "/tmp/verify_script.js"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  Script {i} STILL HAS ERROR: {result.stderr[:200]}")
            error_count += 1

    if error_count == 0:
        print("  Verification PASSED - all scripts valid")
    else:
        print(f"  Verification FAILED - {error_count} scripts still have errors")

    return True


if __name__ == "__main__":
    print("Fixing HTML entities in Cloudflare Pages deploy files...")
    fixed_any = False
    for filepath in FILES_TO_FIX:
        if fix_file(filepath):
            fixed_any = True

    if fixed_any:
        print("\nFiles fixed. Ready to git commit and push to trigger Cloudflare redeploy.")
    else:
        print("\nNo files needed fixing.")
