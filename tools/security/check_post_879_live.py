#!/usr/bin/env python3
import requests, re, sys

r = requests.get("https://purebrain.ai/blog/your-next-direct-report-wont-be-human/", timeout=15)
html = r.text

# Check j5 rule
if "pb-inline-cta a" in html:
    print("j5 rule: PRESENT")
else:
    print("j5 rule: MISSING - plugin CSS may need redeploy")

# Check assessment links
assessment_links = re.findall(r'href=["\']([^"\']*ai-partnership-assessment[^"\']*)["\']', html)
print(f"Assessment links in rendered page: {len(assessment_links)}")
for l in assessment_links:
    print(f"  {l}")

# Check no awakening in rendered
awakening_hrefs = re.findall(r'href=["\']([^"\']*#awakening[^"\']*)["\']', html)
if awakening_hrefs:
    print(f"PROBLEM: Awakening hrefs still in rendered HTML: {awakening_hrefs}")
else:
    print("Awakening hrefs in rendered HTML: NONE (clean)")

# Check webkit in rendered content
webkit_count = html.count("-webkit-text-fill-color")
print(f"-webkit-text-fill-color in rendered HTML: {webkit_count}")

sys.exit(0)
