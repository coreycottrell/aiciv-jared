#!/usr/bin/env python3
"""Fetch WordPress page content via REST API with auth"""
import subprocess
import json
import sys

page_id = sys.argv[1] if len(sys.argv) > 1 else "1263"
url = f"https://purebrain.ai/wp-json/wp/v2/pages/{page_id}?context=edit&_fields=id,title,content,meta"

result = subprocess.run([
    "curl", "-s",
    "-u", "Aether:ZGuh 1W8k WpWM c9iy kqyd buPr",
    "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    url
], capture_output=True, text=True)

data = json.loads(result.stdout)
content = data.get("content", {}).get("raw", "")
print(content[:5000])
print("\n\n--- FULL LENGTH:", len(content))
