#!/usr/bin/env python3
"""
CTO Fix: Headline Capitalization - ALL PAGES
Adds text-transform: uppercase to pb-demo-section__heading
Fixes brand color spans on pay-test-2 and pay-test-sandbox-3
Date: 2026-03-14
"""

import re

BASE = "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy"

FILES = {
    "homepage": f"{BASE}/index.html",
    "pay-test-2": f"{BASE}/pay-test-2/index.html",
    "pay-test-sandbox-3": f"{BASE}/pay-test-sandbox-3/index.html",
}

# --- FIX 1: index.html ---
# The heading block has NO span rule (correct), just needs text-transform added.

OLD_HEADING_INDEX = """\
        .pb-demo-section__heading {
            font-size: clamp(28px, 4vw, 44px);
            font-weight: 700;
            color: #ffffff;
            margin: 0 0 12px 0;
            line-height: 1.15;
            letter-spacing: -0.02em;
        }

        /* heading spans use inline color styles */"""

NEW_HEADING_INDEX = """\
        .pb-demo-section__heading {
            font-size: clamp(28px, 4vw, 44px);
            font-weight: 700;
            color: #ffffff;
            margin: 0 0 12px 0;
            line-height: 1.15;
            letter-spacing: -0.02em;
            text-transform: uppercase;
        }

        /* heading spans use inline color styles — no CSS override */"""

# --- FIX 2: pay-test-2 and pay-test-sandbox-3 ---
# These have a span rule that overrides the inline brand colors.
# Remove that rule and add text-transform.

OLD_HEADING_PAY = """\
        .pb-demo-section__heading {
            font-size: clamp(28px, 4vw, 44px);
            font-weight: 700;
            color: #ffffff;
            margin: 0 0 12px 0;
            line-height: 1.15;
            letter-spacing: -0.02em;
        }

        .pb-demo-section__heading span {
            background: linear-gradient(135deg, #f1420b 0%, #ff6b35 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }"""

NEW_HEADING_PAY = """\
        .pb-demo-section__heading {
            font-size: clamp(28px, 4vw, 44px);
            font-weight: 700;
            color: #ffffff;
            margin: 0 0 12px 0;
            line-height: 1.15;
            letter-spacing: -0.02em;
            text-transform: uppercase;
        }

        /* heading spans use inline color styles — brand: PUREBR=#2a93c1 AI=#f1420b N=#2a93c1 */"""


def fix_file(path, old, new, label):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if old not in content:
        print(f"[WARN] Pattern not found in {label}: {path}")
        return False

    new_content = content.replace(old, new, 1)

    if new_content == content:
        print(f"[WARN] No change made to {label}")
        return False

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"[OK] Fixed: {label}")
    return True


results = {}

results["homepage"] = fix_file(
    FILES["homepage"],
    OLD_HEADING_INDEX,
    NEW_HEADING_INDEX,
    "homepage (index.html)",
)

results["pay-test-2"] = fix_file(
    FILES["pay-test-2"],
    OLD_HEADING_PAY,
    NEW_HEADING_PAY,
    "pay-test-2",
)

results["pay-test-sandbox-3"] = fix_file(
    FILES["pay-test-sandbox-3"],
    OLD_HEADING_PAY,
    NEW_HEADING_PAY,
    "pay-test-sandbox-3",
)

print("\n=== Summary ===")
for name, ok in results.items():
    status = "FIXED" if ok else "FAILED/SKIPPED"
    print(f"  {name}: {status}")

all_ok = all(results.values())
print(f"\nAll fixes applied: {all_ok}")
