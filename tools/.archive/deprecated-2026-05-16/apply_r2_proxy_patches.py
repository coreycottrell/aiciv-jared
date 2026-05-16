#!/usr/bin/env python3
"""Apply R2 -> proxy URL patches to all source files. Run once."""

import os
import json

AETHER = "/home/jared/projects/AI-CIV/aether"
OLD_DOMAIN = "pub-8f8cf3b34e354e108283ed11c59db125.r2.dev"


def patch(filepath, replacements):
    """Apply (old, new) replacements to file. Returns True if changed."""
    rel = os.path.relpath(filepath, AETHER)
    if not os.path.exists(filepath):
        print(f"  SKIP (missing): {rel}")
        return False
    with open(filepath, "r") as f:
        content = f.read()
    original = content
    for old, new in replacements:
        if old not in content:
            print(f"  WARN: pattern not found in {rel}: {old[:80]}")
        content = content.replace(old, new)
    if content == original:
        print(f"  NO CHANGE: {rel}")
        return False
    with open(filepath, "w") as f:
        f.write(content)
    print(f"  PATCHED: {rel}")
    return True


def main():
    print("=" * 60)
    print("R2 Public Domain -> Proxy URL: File Patches")
    print("=" * 60)
    patched = 0

    # 1. social-api worker (PRODUCTION - most critical)
    print("\n[1] workers/social-api/src/worker.js")
    if patch(os.path.join(AETHER, "workers/social-api/src/worker.js"), [
        (
            f'const R2_PUBLIC_DOMAIN = "{OLD_DOMAIN}";',
            f'// DEPRECATED 2026-05-04: R2 public domain broken (returns 404). Use proxy.\n'
            f'// const R2_PUBLIC_DOMAIN = "{OLD_DOMAIN}";\n'
            f'const MEDIA_PROXY_BASE = "https://social.purebrain.ai/media";'
        ),
        (
            'const publicUrl = `https://${R2_PUBLIC_DOMAIN}/${encodeURI(key)}`;',
            'const publicUrl = `${MEDIA_PROXY_BASE}/${encodeURI(key)}`;'
        ),
    ]):
        patched += 1

    # 2. exports/content-batch-images-apr30/upload_and_update.py
    print("\n[2] exports/content-batch-images-apr30/upload_and_update.py")
    if patch(os.path.join(AETHER, "exports/content-batch-images-apr30/upload_and_update.py"), [
        (
            f'R2_PUBLIC_DOMAIN = "{OLD_DOMAIN}"',
            f'# DEPRECATED 2026-05-04: R2 public domain broken. Use proxy.\n'
            f'# R2_PUBLIC_DOMAIN = "{OLD_DOMAIN}"\n'
            f'MEDIA_PROXY_BASE = "https://social.purebrain.ai/media"'
        ),
        (
            f'public_url = f"https://{{R2_PUBLIC_DOMAIN}}/{{r2_key}}"',
            f'public_url = f"{{MEDIA_PROXY_BASE}}/{{r2_key}}"'
        ),
    ]):
        patched += 1

    # 3. tools/attach_sunday_batch_may4_images.py (docstring only)
    print("\n[3] tools/attach_sunday_batch_may4_images.py")
    if patch(os.path.join(AETHER, "tools/attach_sunday_batch_may4_images.py"), [
        (
            f'   stores it on R2 (`{OLD_DOMAIN}`) and',
            '   stores it on R2 and returns a proxy URL via social.purebrain.ai/media/ and'
        ),
    ]):
        patched += 1

    # 4. All from-chy worker files
    print("\n[4] from-chy/worker-*.js files")
    chy_dir = os.path.join(AETHER, "from-chy")
    if os.path.isdir(chy_dir):
        for fname in sorted(os.listdir(chy_dir)):
            if not fname.endswith(".js"):
                continue
            filepath = os.path.join(chy_dir, fname)
            with open(filepath, "r") as f:
                content = f.read()
            if OLD_DOMAIN not in content:
                continue
            if patch(filepath, [
                (
                    f'const R2_PUBLIC_DOMAIN = "{OLD_DOMAIN}";',
                    f'// DEPRECATED 2026-05-04: R2 public domain broken. Use proxy.\n'
                    f'// const R2_PUBLIC_DOMAIN = "{OLD_DOMAIN}";\n'
                    f'const MEDIA_PROXY_BASE = "https://social.purebrain.ai/media";'
                ),
                (
                    '`https://${R2_PUBLIC_DOMAIN}/${encodeURI(key)}`',
                    '`${MEDIA_PROXY_BASE}/${encodeURI(key)}`'
                ),
            ]):
                patched += 1

    # Final scan
    print(f"\n{'=' * 60}")
    print(f"Total files patched: {patched}")
    remaining = []
    for root, dirs, files in os.walk(AETHER):
        dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__')]
        for fname in files:
            if not fname.endswith(('.js', '.py')):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'r', errors='ignore') as f:
                    for lineno, line in enumerate(f, 1):
                        if OLD_DOMAIN in line and '# DEPRECATED' not in line and '// DEPRECATED' not in line and 'OLD_DOMAIN' not in line:
                            remaining.append(f"  {os.path.relpath(fpath, AETHER)}:{lineno}")
            except:
                pass
    if remaining:
        print(f"\nACTIVE references remaining ({len(remaining)}):")
        for r in remaining:
            print(r)
    else:
        print("\nAll active references eliminated from .js and .py files.")
    print(f"\nNote: .json data files (r2_upload_results.json, memory files) are historical records")
    print("and do NOT need patching -- they are not used functionally.")


if __name__ == "__main__":
    main()
