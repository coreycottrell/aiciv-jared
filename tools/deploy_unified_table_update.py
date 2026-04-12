#!/usr/bin/env python3
"""
CTO-Authorized Deployment: Unified Page Table Update
Website Team (Team A) execution script
Date: 2026-03-06
Page: https://purebrain.ai/unified-how-this-levels-you-up/ (ID: 1263)

Adds 6 new enterprise capabilities to "What This Replaces" table.
Differentiates $999 Unified tier from $499 Partnered tier.
New total: $60,500–$111,000/mo (was $25,000–$47,000/mo)
"""
import subprocess
import json
import re
import sys

WP_USER = "Aether"
WP_PASS = "ZGuh 1W8k WpWM c9iy kqyd buPr"
PAGE_ID = "1263"
WP_BASE = "https://purebrain.ai/wp-json/wp/v2"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

# ── New rows to add (after the existing 9) ────────────────────────────────────
NEW_ROWS = [
    ("Advanced Data Analytics &amp; Forecasting", "Senior data analyst + BI tools", "$8,000&ndash;$15,000/mo"),
    ("Multi-Department AI Coordination", "Operations director + workflow consultant", "$7,000&ndash;$12,000/mo"),
    ("Custom AI Agent Creation &amp; Training", "AI engineer + prompt engineer", "$8,000&ndash;$15,000/mo"),
    ("Enterprise Knowledge Base Management", "Knowledge manager + platform license", "$3,000&ndash;$6,000/mo"),
    ("Custom Integrations (Slack, CRM, ERP)", "Integration consultant + licensing", "$4,000&ndash;$10,000/mo"),
    ("Compliance &amp; Audit Trail Reporting", "Compliance officer + audit software", "$3,500&ndash;$7,000/mo"),
]

OLD_TOTAL_PATTERNS = [
    r'\$25,000.*?\$47,000',
    r'\$25,000[^\$]*\$47,000',
    r'25,000',
]
NEW_TOTAL = "$60,500&ndash;$111,000/mo"
NEW_TOTAL_PLAIN = "$60,500–$111,000/mo"

# Value multiplier patterns to update
OLD_MULTIPLIER_PATTERNS = ["25x", "47x", "25-47x", "25–47x"]
NEW_MULTIPLIER = "60x"


def curl_get(url):
    r = subprocess.run([
        "curl", "-s",
        "-u", f"{WP_USER}:{WP_PASS}",
        "-H", f"User-Agent: {UA}",
        url
    ], capture_output=True, text=True, timeout=30)
    return r.stdout


def curl_post(url, payload):
    r = subprocess.run([
        "curl", "-s", "-X", "POST",
        "-u", f"{WP_USER}:{WP_PASS}",
        "-H", f"User-Agent: {UA}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload),
        url
    ], capture_output=True, text=True, timeout=60)
    return r.stdout


def curl_delete(url):
    r = subprocess.run([
        "curl", "-s", "-X", "DELETE",
        "-u", f"{WP_USER}:{WP_PASS}",
        "-H", f"User-Agent: {UA}",
        url
    ], capture_output=True, text=True, timeout=30)
    return r.stdout


def build_new_row_html(capability, equivalent, cost):
    return (
        f'<tr style="background: rgba(241,66,11,0.08);">'
        f'<td><strong>{capability}</strong></td>'
        f'<td>{equivalent}</td>'
        f'<td>{cost}</td>'
        f'</tr>'
    )


def update_table_in_content(content):
    """
    Strategy: find </tbody> or the total row, inject new rows before total,
    update total value.
    """
    updated = content

    # Find the closing total row (various patterns)
    # Pattern 1: explicit total row with $25,000
    total_patterns = [
        r'(<tr[^>]*>.*?\$25,000.*?\$47,000.*?</tr>)',
        r'(\$25,000.*?\$47,000[^\n]*)',
    ]

    # First check if new rows already exist
    if "Advanced Data Analytics" in content or "60,500" in content:
        print("WARNING: New rows or updated total already exist in content!")
        print("Skipping to avoid duplicate rows.")
        return None

    # Build the new rows HTML block
    new_rows_html = "\n".join(
        build_new_row_html(cap, eq, cost) for cap, eq, cost in NEW_ROWS
    )

    # Strategy: find </tbody> and insert before it
    # Or find the total row and insert before it
    # Or find </table> and insert before it

    # Try inserting before closing total row
    # Look for total row pattern
    total_row_patterns = [
        r'(<tr[^>]*>\s*<td[^>]*>\s*(?:<strong>)?(?:TOTAL|Total)[^<]*(?:</strong>)?\s*</td>)',
        r'(<td[^>]*>\s*\$25,000)',
    ]

    inserted = False
    for pat in total_row_patterns:
        match = re.search(pat, updated, re.DOTALL | re.IGNORECASE)
        if match:
            insert_pos = match.start()
            updated = updated[:insert_pos] + new_rows_html + "\n" + updated[insert_pos:]
            print(f"Inserted new rows before total row (pattern: {pat[:40]})")
            inserted = True
            break

    if not inserted:
        # Try before </tbody>
        if "</tbody>" in updated.lower():
            idx = updated.lower().rfind("</tbody>")
            updated = updated[:idx] + new_rows_html + "\n" + updated[idx:]
            print("Inserted new rows before </tbody>")
            inserted = True
        elif "</table>" in updated.lower():
            idx = updated.lower().rfind("</table>")
            updated = updated[:idx] + new_rows_html + "\n" + updated[idx:]
            print("Inserted new rows before </table>")
            inserted = True

    if not inserted:
        print("ERROR: Could not find insertion point for new rows")
        return None

    # Update total values
    updated = re.sub(r'\$25,000', '$60,500', updated)
    updated = re.sub(r'\$47,000', '$111,000', updated)
    updated = re.sub(r'25,000.*?47,000', '60,500–111,000', updated)

    # Update multiplier text
    for old_mult in OLD_MULTIPLIER_PATTERNS:
        updated = updated.replace(old_mult, NEW_MULTIPLIER)

    return updated


def update_elementor_data(elementor_json_str):
    """
    Search through Elementor JSON for the table content and update it.
    Elementor stores content as nested JSON with widget HTML.
    """
    # The table might be in a widget's editor/html content
    # We search for known content markers and update the JSON string directly

    updated = elementor_json_str

    if "Advanced Data Analytics" in updated or "60,500" in updated:
        print("WARNING: New content already present in elementor_data!")
        return None

    # Strategy: find the table marker and inject new rows
    # Look for the last existing row before the total
    # Then find </tbody> or total row and insert before

    # Build plain text rows for JSON (no HTML entities that get double-escaped)
    new_rows_for_elementor = ""
    for cap, eq, cost in NEW_ROWS:
        # In elementor JSON, special chars are escaped
        cap_clean = cap.replace("&amp;", "&").replace("&ndash;", "–")
        cost_clean = cost.replace("&ndash;", "–")
        new_rows_for_elementor += (
            f'<tr style=\\"background: rgba(241,66,11,0.08);\\"><td><strong>{cap_clean}</strong>'
            f'</td><td>{eq}</td><td>{cost_clean}</td></tr>'
        )

    # Find insertion point - before </tbody> or total row
    patterns = [
        '\\\\u003c/tbody\\\\u003e',  # unicode-escaped
        '</tbody>',
        r'\\u003c\/tbody\\u003e',
    ]

    for pat in patterns:
        if pat in updated:
            idx = updated.rfind(pat)
            updated = updated[:idx] + new_rows_for_elementor + updated[idx:]
            print(f"Inserted rows in elementor_data (pattern: {repr(pat[:30])})")
            # Update totals
            updated = updated.replace("$25,000", "$60,500").replace("$47,000", "$111,000")
            for old_mult in OLD_MULTIPLIER_PATTERNS:
                updated = updated.replace(old_mult, NEW_MULTIPLIER)
            return updated

    return None


# ── MAIN ──────────────────────────────────────────────────────────────────────
print("=" * 60)
print("UNIFIED PAGE TABLE UPDATE — CTO Website Team (Team A)")
print("=" * 60)

# Step 1: Fetch page
print("\nSTEP 1: Fetching page 1263...")
raw = curl_get(f"{WP_BASE}/pages/{PAGE_ID}?context=edit")
try:
    page_data = json.loads(raw)
except Exception as e:
    print(f"FATAL: Could not parse response: {e}")
    print(f"Response: {raw[:300]}")
    sys.exit(1)

content_raw = page_data.get("content", {}).get("raw", "")
meta = page_data.get("meta", {})
elementor_data = meta.get("_elementor_data", "")

print(f"Raw content: {len(content_raw)} chars")
print(f"Elementor data: {len(elementor_data)} chars")

# Step 2: Determine update strategy
print("\nSTEP 2: Determining update strategy...")

update_payload = {}
strategy = None

if "<table" in content_raw.lower() and ("3,000" in content_raw or "help desk" in content_raw.lower()):
    print("Strategy: Update table in raw content")
    strategy = "raw_content"
    new_content = update_table_in_content(content_raw)
    if new_content:
        update_payload["content"] = new_content
elif elementor_data and ("3,000" in elementor_data or "help desk" in elementor_data.lower() or "25,000" in elementor_data):
    print("Strategy: Update table in elementor_data")
    strategy = "elementor_data"
    new_elementor = update_elementor_data(elementor_data)
    if new_elementor:
        update_payload["meta"] = {"_elementor_data": new_elementor}
else:
    print("DIAGNOSTIC: Searching for any pricing content...")
    for field_name, field_val in [("raw", content_raw), ("elementor", elementor_data)]:
        for marker in ["3,000", "help desk", "25,000", "replaces", "table"]:
            if marker.lower() in field_val.lower():
                idx = field_val.lower().find(marker.lower())
                print(f"\nFound '{marker}' in {field_name} at {idx}:")
                print(field_val[max(0,idx-100):idx+500])
                break

    print("\nCould not determine update strategy. Manual intervention needed.")
    print("Saving raw content to /tmp/unified_raw_content.txt for inspection...")
    with open("/tmp/unified_raw_content.txt", "w") as f:
        f.write(content_raw)
    with open("/tmp/unified_elementor.txt", "w") as f:
        f.write(elementor_data[:50000])
    print("Saved. Check these files.")
    sys.exit(1)

if not update_payload:
    print("ERROR: Update returned no changes. Aborting.")
    sys.exit(1)

# Step 3: Push update
print(f"\nSTEP 3: Pushing update via REST API (strategy={strategy})...")
response_raw = curl_post(f"{WP_BASE}/pages/{PAGE_ID}", update_payload)
try:
    response = json.loads(response_raw)
    if response.get("id") == int(PAGE_ID):
        print(f"SUCCESS: Page {PAGE_ID} updated. Status: {response.get('status')}")
    elif "message" in response:
        print(f"API Error: {response.get('message')}")
        sys.exit(1)
    else:
        print(f"Unexpected response: {response_raw[:500]}")
except Exception as e:
    print(f"Response parse error: {e}")
    print(f"Response: {response_raw[:500]}")
    sys.exit(1)

# Step 4: Clear Elementor cache
print("\nSTEP 4: Clearing Elementor cache...")
cache_response = curl_delete(f"https://purebrain.ai/wp-json/elementor/v1/cache")
print(f"Cache clear response: {cache_response[:200]}")

# Step 5: Verify
print("\nSTEP 5: Verifying update...")
verify_raw = curl_get(f"{WP_BASE}/pages/{PAGE_ID}?context=edit&_fields=id,content,meta")
verify_data = json.loads(verify_raw)
verify_content = verify_data.get("content", {}).get("raw", "")
verify_elementor = verify_data.get("meta", {}).get("_elementor_data", "")

checks = {
    "Advanced Data Analytics present": "Advanced Data Analytics" in verify_content or "Advanced Data Analytics" in verify_elementor,
    "New total $60,500 present": "60,500" in verify_content or "60,500" in verify_elementor,
    "Old total $25,000 removed": "25,000" not in verify_content and "25,000" not in verify_elementor,
}

print("\nVerification results:")
all_pass = True
for check, result in checks.items():
    status = "PASS" if result else "FAIL"
    if not result:
        all_pass = False
    print(f"  [{status}] {check}")

if all_pass:
    print("\nALL CHECKS PASSED. Deployment complete.")
else:
    print("\nSOME CHECKS FAILED. Manual review needed.")

print(f"\nView live: https://purebrain.ai/unified-how-this-levels-you-up/")
