#!/usr/bin/env python3
"""
Fix blog post transparency and CTA button issues across all 24 CF Pages blog posts.

FIX 1 — Background transparency:
  BEFORE: html, body { background: #0a0a0f !important; ... }
  AFTER:  html { background: #0a0a0f !important; ... }
          body { background: transparent !important; ... }

  Rationale: The video element (z-index: -3, position: fixed) sits beneath body.
  An opaque body background blocks it entirely. Keeping html dark prevents
  white/orange flash, making body transparent lets the video show through.

FIX 2 — CTA button hover specificity:
  The rule `article.pb-blog-post a:hover` applies background: #f1420b and
  padding: 0 3px to ALL anchors inside the article, including the CTA button.
  This overrides .pb-recap-live-cta:hover because it has higher specificity
  (type + class + element vs just class).

  Fix: Add `article.pb-blog-post .pb-recap-live-cta:hover` with !important
  overrides for background, padding, transform, and border-bottom.
"""

import os
import re

BLOG_DIR = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog"

# The exact string we are replacing for Fix 1
OLD_HTML_BODY = "html, body {\n    background: #0a0a0f !important;"

NEW_HTML_BODY = "html {\n    background: #0a0a0f !important;\n    color: #ffffff;\n}\nbody {\n    background: transparent !important;"

# For Fix 2 — we append a higher-specificity override after the existing CTA hover block.
# We find the closing brace of .pb-recap-live-cta:hover { ... } and insert after it.
CTA_HOVER_OVERRIDE = """
/* CTA button specificity override — beats article.pb-blog-post a:hover */
article.pb-blog-post .pb-recap-live-cta:hover {
    background: #2a93c1 !important;
    box-shadow: 0 4px 16px rgba(42, 147, 193, 0.4) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    transform: none !important;
    padding: 10px 24px !important;
    border-bottom: none !important;
    border-radius: 7px !important;
}"""

# Also fix the base CTA rule to not inherit border-bottom from article a rule
CTA_BASE_OVERRIDE = """
/* CTA button base specificity override — beats article.pb-blog-post a */
article.pb-blog-post .pb-recap-live-cta {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border-bottom: none !important;
    text-decoration: none !important;
}"""


def fix_file(filepath: str) -> tuple[bool, str]:
    """Apply both fixes to a single blog post HTML file. Returns (changed, message)."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    changes = []

    # ── FIX 1: html/body transparency ────────────────────────────────────────
    # The pattern is: "html, body {\n    background: #0a0a0f !important;\n    color: #ffffff;\n..."
    # We need to split color out of the combined block.
    # Strategy: replace the combined html, body rule with separate html and body rules.
    #
    # Find the full html, body { ... } block
    html_body_pattern = re.compile(
        r'html, body \{\n(    background: #0a0a0f !important;\n    color: #ffffff;\n)(.*?)\}',
        re.DOTALL
    )
    match = html_body_pattern.search(content)
    if match:
        full_match = match.group(0)
        inner = match.group(2)  # everything after color line, before closing brace
        # Build replacement: html keeps background+color, body gets transparent bg
        replacement = (
            "html {\n"
            "    background: #0a0a0f !important;\n"
            "    color: #ffffff;\n"
            "}\n"
            "body {\n"
            "    background: transparent !important;\n"
            "    color: #ffffff;\n"
            + inner +
            "}"
        )
        content = content.replace(full_match, replacement, 1)
        changes.append("Fix 1: html/body transparency applied")
    else:
        # Fallback: simpler replacement if the pattern differs slightly
        if "html, body {\n    background: #0a0a0f !important;" in content:
            content = content.replace(
                "html, body {\n    background: #0a0a0f !important;",
                "html {\n    background: #0a0a0f !important;\n}\nbody {\n    background: transparent !important;"
            )
            changes.append("Fix 1: html/body transparency applied (fallback pattern)")
        else:
            changes.append("Fix 1: SKIPPED — pattern not found (already fixed or different structure)")

    # ── FIX 2: CTA button hover specificity ──────────────────────────────────
    # Find the end of the .pb-recap-live-cta:hover { ... } block and insert overrides after
    cta_hover_end = ".pb-recap-live-cta:hover {\n    background: #2a93c1;\n    box-shadow: 0 4px 16px rgba(42, 147, 193, 0.4);\n    color: #ffffff !important;\n    -webkit-text-fill-color: #ffffff;\n    transform: none;\n}"

    if cta_hover_end in content and CTA_HOVER_OVERRIDE not in content:
        content = content.replace(
            cta_hover_end,
            cta_hover_end + CTA_HOVER_OVERRIDE + CTA_BASE_OVERRIDE
        )
        changes.append("Fix 2: CTA hover specificity override injected")
    elif CTA_HOVER_OVERRIDE in content:
        changes.append("Fix 2: SKIPPED — CTA override already present")
    else:
        changes.append("Fix 2: SKIPPED — CTA hover block not found in expected form")

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True, " | ".join(changes)
    else:
        return False, "No changes made: " + " | ".join(changes)


def main():
    posts = sorted([
        d for d in os.listdir(BLOG_DIR)
        if os.path.isdir(os.path.join(BLOG_DIR, d))
           and os.path.isfile(os.path.join(BLOG_DIR, d, "index.html"))
    ])

    print(f"Processing {len(posts)} blog posts...\n")
    changed_count = 0
    skipped_count = 0

    for post in posts:
        filepath = os.path.join(BLOG_DIR, post, "index.html")
        changed, msg = fix_file(filepath)
        status = "CHANGED" if changed else "SKIPPED"
        if changed:
            changed_count += 1
        else:
            skipped_count += 1
        print(f"[{status}] {post}: {msg}")

    print(f"\nDone. {changed_count} files changed, {skipped_count} unchanged.")


if __name__ == "__main__":
    main()
