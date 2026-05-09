#!/usr/bin/env python3
"""Query D1 for pending content items to expand."""
import json
import urllib.request

CF_ACCOUNT_ID = "d526a3e9498dd167509003004df03290"
D1_DB_ID = "625dde70-0a60-45e7-bf81-e18e5ac4d854"
CF_TOKEN = "[REDACTED-2026-05-09-LEAK-CFUT]"

url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/d1/database/{D1_DB_ID}/query"

sql = """SELECT id, body, content_type, scheduled_at, status FROM content_items
WHERE content_type IN ('blog','newsletter','newsletter_promo')
AND (status = 'pending_review' OR status = 'draft')
AND scheduled_at >= '2026-04-30'
ORDER BY scheduled_at"""

payload = {"sql": sql}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {CF_TOKEN}",
        "Content-Type": "application/json",
    },
)

resp = urllib.request.urlopen(req)
result = json.loads(resp.read())

if result.get("success"):
    rows = result["result"][0]["results"]
    print(f"Found {len(rows)} items\n")
    for row in rows:
        body_len = len(row["body"]) if row["body"] else 0
        print(f"ID: {row['id']}")
        print(f"  Type: {row['content_type']}")
        print(f"  Date: {row['scheduled_at']}")
        print(f"  Status: {row['status']}")
        print(f"  Body length: {body_len} chars")
        print(f"  Body preview: {(row['body'] or '')[:200]}...")
        print()

    # Save full data for processing
    with open("/home/jared/projects/AI-CIV/aether/exports/content-expand/current_content.json", "w") as f:
        json.dump(rows, f, indent=2)
    print("Full data saved to current_content.json")
else:
    print(f"Error: {result.get('errors')}")
