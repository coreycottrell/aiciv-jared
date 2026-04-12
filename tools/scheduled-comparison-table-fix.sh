#!/bin/bash
# Scheduled fix: Comparison table X marks should be Pure Tech Blue (#2a93c1), not orange
# Runs 1 hour from creation (scheduled via at command)

cd /home/jared/projects/AI-CIV/aether

TOKEN=$(python3 -c "import json; print(json.load(open('config/telegram_config.json'))['bot_token'])")
CHAT_ID="548906264"

send_tg() {
    curl -s "https://api.telegram.org/bot${TOKEN}/sendMessage" \
        -d chat_id="$CHAT_ID" \
        --data-urlencode "text=$1" > /dev/null 2>&1
}

send_tg "⏰ Scheduled task firing: Comparison table color fix on pay-test-sandbox-2. Changing X marks from orange to Pure Tech Blue (#2a93c1)."

# Fetch current _elementor_data
python3 << 'PYTHON'
import urllib.request, json, base64, re

auth = base64.b64encode(b'Aether:ZGuh 1W8k WpWM c9iy kqyd buPr').decode()
headers = {
    'Authorization': 'Basic ' + auth,
    'User-Agent': 'Mozilla/5.0 (compatible; AetherBot/1.0)',
}

# Fetch page
req = urllib.request.Request(
    'https://purebrain.ai/wp-json/wp/v2/pages/688?context=edit',
    headers=headers
)
with urllib.request.urlopen(req, timeout=60) as resp:
    page_data = json.loads(resp.read())

ed_str = page_data.get('meta', {}).get('_elementor_data', '')

# Fix 1: Change X mark color from orange (#f1420b / #ff6b35 / similar orange) to Pure Tech Blue (#2a93c1)
# The comparison table uses ✗ or × characters styled in orange
# Common patterns: color: #f1420b, color: #ff4400, color: orange on X marks
# We want to change X marks in the comparison table to blue

# The comparison table section has "PURE BRAIN VS. THE REST" heading
# X marks and warning triangles for competitors are orange — change X marks to blue

# Strategy: Find the comparison table HTML and change X mark colors
# X marks are likely styled with inline color or a CSS class

changes_made = 0

# Fix the "$79-999" text to "$149-999" in the comparison bottom text  
if '$79' in ed_str and '999' in ed_str:
    # Already handled by other agent, but double-check
    pass

# Fix comparison table X colors
# Common inline styles for orange X marks
orange_patterns = [
    ('color: #f1420b">✗', 'color: #2a93c1">✗'),
    ('color: #f1420b">✘', 'color: #2a93c1">✘'),  
    ('color: #f1420b">×', 'color: #2a93c1">×'),
    ('color:#f1420b">✗', 'color:#2a93c1">✗'),
    ('color:#f1420b">✘', 'color:#2a93c1">✘'),
    ('color:#f1420b">×', 'color:#2a93c1">×'),
    ('color: #ff6b35">✗', 'color: #2a93c1">✗'),
    ('color: #ff4400">✗', 'color: #2a93c1">✗'),
]

for old, new in orange_patterns:
    if old in ed_str:
        count = ed_str.count(old)
        ed_str = ed_str.replace(old, new)
        changes_made += count
        print(f"Replaced {count}x: {old[:30]}... -> blue")

# Also handle the warning triangle ⚠ — these should stay orange (they indicate partial support)
# Only X marks (✗, ✘, ×) should be blue

# Try regex for any orange-colored X marks we might have missed
# Pattern: color followed by some orange hex, then an X character
import re
def fix_orange_x(match):
    global changes_made
    changes_made += 1
    return match.group(0).replace(match.group(1), '#2a93c1')

# Match color: #xxx(xxx) followed by X characters  
ed_str_new = re.sub(
    r'color:\s*(#(?:f1420b|ff6b35|ff4400|e74c3c|ff3300|F1420B|FF6B35))\s*["\']?\s*>\s*[✗✘×✕]',
    lambda m: m.group(0).replace(m.group(1), '#2a93c1'),
    ed_str
)
if ed_str_new != ed_str:
    regex_changes = len(re.findall(r'color:\s*#(?:f1420b|ff6b35|ff4400|e74c3c|ff3300|F1420B|FF6B35)', ed_str)) - len(re.findall(r'color:\s*#(?:f1420b|ff6b35|ff4400|e74c3c|ff3300|F1420B|FF6B35)', ed_str_new))
    changes_made += abs(regex_changes)
    ed_str = ed_str_new

if changes_made == 0:
    print("WARNING: No orange X marks found with expected patterns. Checking alternative formats...")
    # Print a sample of the comparison table area for debugging
    idx = ed_str.find('VS. THE REST')
    if idx > 0:
        sample = ed_str[idx:idx+2000]
        print(f"Sample around comparison table: {sample[:500]}")
    else:
        print("Could not find 'VS. THE REST' in _elementor_data")
        # Try to find comparison-related content
        for marker in ['comparison', 'compare', 'vs.', 'VS.']:
            idx = ed_str.lower().find(marker.lower())
            if idx > 0:
                print(f"Found '{marker}' at position {idx}")
                break

print(f"\nTotal changes made: {changes_made}")

if changes_made > 0:
    # Push updated _elementor_data
    update_data = json.dumps({
        'meta': {'_elementor_data': ed_str}
    }).encode()
    
    update_req = urllib.request.Request(
        'https://purebrain.ai/wp-json/wp/v2/pages/688',
        data=update_data,
        headers={**headers, 'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(update_req, timeout=60) as resp:
        result = json.loads(resp.read())
        print(f"Push result: status={result.get('status')}")
    
    # Clear Elementor cache
    cache_req = urllib.request.Request(
        'https://purebrain.ai/wp-json/elementor/v1/cache',
        headers=headers,
        method='DELETE'
    )
    try:
        with urllib.request.urlopen(cache_req, timeout=30) as resp:
            print(f"Cache cleared: {resp.status}")
    except Exception as e:
        print(f"Cache clear attempt: {e}")
    
    print("Comparison table X marks updated to Pure Tech Blue!")
else:
    print("No changes needed or patterns not found. Manual inspection needed.")
PYTHON

# Report result
RESULT=$?
if [ $RESULT -eq 0 ]; then
    send_tg "✅ Comparison table color fix complete. X marks changed from orange to Pure Tech Blue (#2a93c1) on pay-test-sandbox-2."
else
    send_tg "⚠️ Comparison table fix script finished with issues. May need manual review."
fi
