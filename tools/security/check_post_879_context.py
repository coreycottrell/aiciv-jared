#!/usr/bin/env python3
import requests, re, sys

r = requests.get("https://purebrain.ai/blog/your-next-direct-report-wont-be-human/", timeout=15)
html = r.text

# Find context around awakening link
for m in re.finditer(r'.{0,200}#awakening.{0,200}', html, re.DOTALL):
    print("=== AWAKENING CONTEXT ===")
    print(m.group()[:500])
    print()
