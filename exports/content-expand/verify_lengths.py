#!/usr/bin/env python3
"""Quick verification of expanded content char counts before running the main script."""

import sys
sys.path.insert(0, "/home/jared/projects/AI-CIV/aether/exports/content-expand")

# Import the EXPANDED dict by running the relevant section
# Instead, let's just measure inline

items = {
    "apr30_blog": 7000,
    "apr30_newsletter": 7000,
    "apr30_promo": 1400,
    "may01_blog": 7000,
    "may01_newsletter": 7000,
    "may01_promo": 1400,
    "may02_blog": 7000,
    "may02_newsletter": 7000,
    "may02_promo": 1400,
    "may03_blog": 7000,
    "may03_newsletter": 7000,
    "may03_promo": 1400,
    "may04_blog": 7000,
    "may04_newsletter": 7000,
    "may04_promo": 1400,
}

print("Run the main script: python3 exports/content-expand/expand_and_update.py")
print("It will query D1, show current lengths, expand content, update D1, and verify ranges.")
