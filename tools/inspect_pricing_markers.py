#!/usr/bin/env python3
"""
Inspect the Elementor JSON to find exact marker strings around the pricing section.
"""
import sys

with open('/home/jared/projects/AI-CIV/aether/exports/package-sandbox-2/page688_elementor_data.json', 'r') as f:
    data = f.read()

print(f"Total chars: {len(data)}")
print(f"Is valid JSON string: starts with {data[:10]!r}")

# Search for pricing-grid in raw string
import re

# Find all occurrences of pricing-grid
positions = [m.start() for m in re.finditer(r'pricing-grid', data)]
print(f"\n'pricing-grid' found at {len(positions)} positions: {positions[:10]}")

if positions:
    # Show context around first occurrence
    p = positions[0]
    context = data[max(0, p-50):p+200]
    print(f"\nContext around first 'pricing-grid' at {p}:")
    print(repr(context))

# Search for pricing-requirements
positions2 = [m.start() for m in re.finditer(r'pricing-requirements', data)]
print(f"\n'pricing-requirements' found at {len(positions2)} positions: {positions2[:5]}")

if positions2:
    p2 = positions2[0]
    context2 = data[max(0, p2-100):p2+100]
    print(f"\nContext around 'pricing-requirements' at {p2}:")
    print(repr(context2))

# Search for Bonded tier
bonded_positions = [m.start() for m in re.finditer(r'Bonded', data)]
print(f"\n'Bonded' found at {len(bonded_positions)} positions: {bonded_positions[:5]}")

# Search for MOST POPULAR
mp_positions = [m.start() for m in re.finditer(r'MOST POPULAR', data)]
print(f"\n'MOST POPULAR' found at {len(mp_positions)} positions: {mp_positions[:5]}")
if mp_positions:
    p3 = mp_positions[0]
    print(f"Context: {repr(data[max(0,p3-100):p3+100])}")
