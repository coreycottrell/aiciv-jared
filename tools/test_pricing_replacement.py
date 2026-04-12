#!/usr/bin/env python3
"""
Dry-run test: verify the replacement logic works on the actual Elementor JSON
without pushing anything to WordPress.
"""

import json
import sys

# Import the replacement functions
sys.path.insert(0, '/home/jared/projects/AI-CIV/aether/tools')
from update_pricing_tiers_688 import build_new_pricing_grid, find_and_replace_pricing_in_widget

def main():
    print("Loading Elementor JSON...")
    with open('/home/jared/projects/AI-CIV/aether/exports/package-sandbox-2/page688_elementor_data.json', 'r') as f:
        elementor_data_str = f.read()
    print(f"  Loaded {len(elementor_data_str)} chars")

    print("Building new pricing grid...")
    new_grid_html = build_new_pricing_grid()
    print(f"  New grid: {len(new_grid_html)} chars")

    print("Testing replacement logic...")
    try:
        new_data = find_and_replace_pricing_in_widget(elementor_data_str, new_grid_html)
        print(f"  Replacement succeeded, new length: {len(new_data)}")

        # Spot-check the new data contains expected strings (JSON-escaped)
        checks = [
            ("Awakened $149", '\\$149'),
            ("Partnered", 'Partnered'),
            ("Unified", 'Unified'),
            ("Enterprise", 'Enterprise'),
            ("Strikethrough $197", '\\$197\\/month\\*'),
            ("Footnote", 'Lock in the savings today'),
            ("MOST POPULAR", 'MOST POPULAR'),
            ("CLAIM THIS SPOT", 'CLAIM THIS SPOT'),
            ("No more Bonded", 'Bonded'),  # This should NOT be in new data
            ("PayPal preserved", 'openPayPalModal'),
        ]

        for name, pattern in checks:
            if name == "No more Bonded":
                found = pattern in new_data
                status = "FAIL (Bonded still present)" if found else "PASS (Bonded removed)"
            else:
                found = pattern in new_data
                status = "PASS" if found else "FAIL (not found)"
            print(f"  [{status}] {name}")

        # Save the result for inspection
        out_path = '/home/jared/projects/AI-CIV/aether/exports/package-sandbox-2/page688_elementor_data_UPDATED.json'
        with open(out_path, 'w') as f:
            f.write(new_data)
        print(f"\nTest output saved to: {out_path}")

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
