#!/usr/bin/env python3
"""
Phase-1 self-grading frontmatter migration (aiciv-native-org integration).

Adds ONLY these fields to every .claude/skills/*/SKILL.md frontmatter:
    status: provisional
    tick_count: 0
    last_used: <git last-commit date | mtime fallback; YYYY-MM-DD>
    introduced: <git first-commit date | mtime fallback; YYYY-MM-DD>

SAFETY:
  - Line-based, not full YAML rewrite. Existing keys/values/order preserved byte-for-byte.
  - If `status:` already present -> SKIP (idempotent).
  - If file has frontmatter -> insert ONLY missing fields inside the existing block.
  - If file has NO frontmatter -> PREPEND a new block, body unchanged.
  - The SKILL body (everything after the closing `---`) is NEVER touched.

Usage:
    python3 tools/skill_frontmatter_migrate.py --dry-run
    python3 tools/skill_frontmatter_migrate.py
"""
import argparse
import datetime
import glob
import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILLS_GLOB = os.path.join(REPO_ROOT, ".claude", "skills", "*", "SKILL.md")

NEW_FIELDS = ("status", "tick_count", "last_used", "introduced")


def _git_date(path, reverse):
    """Return YYYY-MM-DD from git, or None if no history."""
    args = ["git", "log", "--format=%cs", "--", path]
    if reverse:
        args.insert(2, "--reverse")
    try:
        out = subprocess.run(
            args, cwd=REPO_ROOT, capture_output=True, text=True, check=False
        ).stdout.strip().splitlines()
    except Exception:
        return None
    if not out:
        return None
    return out[0].strip() if reverse else out[0].strip()


def _mtime_date(path):
    ts = os.path.getmtime(path)
    return datetime.date.fromtimestamp(ts).strftime("%Y-%m-%d")


def compute_dates(path):
    last = _git_date(path, reverse=False) or _mtime_date(path)
    introduced = _git_date(path, reverse=True) or _mtime_date(path)
    return last, introduced


def build_field_lines(path):
    last, introduced = compute_dates(path)
    return {
        "status": "status: provisional",
        "tick_count": "tick_count: 0",
        "last_used": f"last_used: {last}",
        "introduced": f"introduced: {introduced}",
    }


def split_frontmatter(text):
    """
    If text starts with a '---' frontmatter block, return
    (fm_lines, body_text) where fm_lines is the list of lines BETWEEN the
    opening and closing '---' (exclusive), and body_text is everything from
    the closing '---' onward (inclusive of the closing '---').
    Returns (None, text) if no valid frontmatter block.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, text
    # find closing '---'
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm_lines = lines[1:i]
            # body = closing '---' line onward, rejoined
            body = "\n".join(lines[i:])
            return fm_lines, body
    # opened but never closed -> treat as no frontmatter (do not corrupt)
    return None, text


def fm_has_status(fm_lines):
    for ln in fm_lines:
        stripped = ln.lstrip()
        if stripped.split(":", 1)[0].strip() == "status":
            return True
    return False


def fm_existing_keys(fm_lines):
    keys = set()
    for ln in fm_lines:
        stripped = ln.lstrip()
        if ":" in stripped and not stripped.startswith("#"):
            keys.add(stripped.split(":", 1)[0].strip())
    return keys


def migrate_file(path, dry_run):
    """Return (changed: bool, action: str, sample: dict|None)."""
    with open(path, "r", encoding="utf-8") as fh:
        original = fh.read()

    fm_lines, body = split_frontmatter(original)
    field_lines = build_field_lines(path)

    if fm_lines is not None:
        # Existing frontmatter
        if fm_has_status(fm_lines):
            return False, "SKIP (status present)", None
        existing_keys = fm_existing_keys(fm_lines)
        to_add = [field_lines[k] for k in NEW_FIELDS if k not in existing_keys]
        new_fm_lines = list(fm_lines) + to_add
        new_text = "---\n" + "\n".join(new_fm_lines) + "\n" + body
        action = "ADD fields to existing frontmatter"
    else:
        # No frontmatter -> prepend new block
        block = "---\n" + "\n".join(field_lines[k] for k in NEW_FIELDS) + "\n---\n"
        new_text = block + original
        action = "PREPEND new frontmatter block"

    if new_text == original:
        return False, "NO CHANGE", None

    before_sample = "\n".join(original.split("\n")[:10])
    after_sample = "\n".join(new_text.split("\n")[:12])
    sample = {"before": before_sample, "after": after_sample}

    if not dry_run:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new_text)

    return True, action, sample


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print changes, write nothing")
    ap.add_argument("--samples", nargs="*", default=[],
                    help="explicit file paths to print before/after samples for")
    args = ap.parse_args()

    files = sorted(glob.glob(SKILLS_GLOB))
    changed = 0
    skipped = 0
    sample_store = {}

    for path in files:
        did, action, sample = migrate_file(path, args.dry_run)
        rel = os.path.relpath(path, REPO_ROOT)
        if did:
            changed += 1
            if args.dry_run:
                print(f"[WOULD {action}] {rel}")
        else:
            skipped += 1
        if sample is not None:
            sample_store[rel] = sample

    print(f"\n{'DRY-RUN' if args.dry_run else 'APPLIED'}: "
          f"{changed} changed, {skipped} skipped, {len(files)} total")

    # Print explicit before/after for requested samples
    for want in args.samples:
        rel = os.path.relpath(os.path.abspath(want), REPO_ROOT)
        if rel in sample_store:
            s = sample_store[rel]
            print(f"\n===== SAMPLE: {rel} =====")
            print("----- BEFORE (first 10 lines) -----")
            print(s["before"])
            print("----- AFTER (first 12 lines) -----")
            print(s["after"])
        else:
            print(f"\n===== SAMPLE: {rel} ===== (no change or not found)")


if __name__ == "__main__":
    sys.exit(main())
