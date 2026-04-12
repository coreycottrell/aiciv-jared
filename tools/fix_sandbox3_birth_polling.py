#!/usr/bin/env python3
"""
Fix pay-test-sandbox-3 (page 1232): Add birth/start seed + portal polling.

The greyed-out Brain Stream button was injected but:
1. No seed is sent to Witness to start the birth
2. payTestData.containerName is never set
3. runPortalButtonWatcher never runs (bails on null containerName)

This fix:
- After the greyed-out button is injected, sends a seed to /api/birth/start
- Gets containerName from server response
- Sets payTestData.containerName
- Calls runPortalButtonWatcher() which polls /api/birth/portal-status/{container}
"""

import json
import os
import requests
import sys

# Load credentials
env_path = '/home/jared/projects/AI-CIV/aether/.env'
wp_pass = None
with open(env_path) as f:
    for line in f:
        if line.startswith('PUREBRAIN_WP_APP_PASSWORD='):
            wp_pass = line.strip().split('=', 1)[1]

if not wp_pass:
    print("ERROR: PUREBRAIN_WP_APP_PASSWORD not found")
    sys.exit(1)

PAGE_ID = 1232
WP_API = f'https://purebrain.ai/wp-json/wp/v2/pages/{PAGE_ID}'
AUTH = ('Aether', wp_pass)

# 1. Fetch current page
print(f"Fetching page {PAGE_ID}...")
resp = requests.get(f'{WP_API}?context=edit', auth=AUTH)
data = resp.json()
ed = data['meta']['_elementor_data']
print(f"  _elementor_data length: {len(ed)}")

# 2. Find the injection point - after portalBtnRow is appended
OLD = (
    "msgList.appendChild(portalBtnRow);\\n"
    "  msgList.scrollTop = msgList.scrollHeight;\\n"
    "}"
)

NEW = (
    "msgList.appendChild(portalBtnRow);\\n"
    "  msgList.scrollTop = msgList.scrollHeight;\\n"
    "\\n"
    "  // ── Send seed to Witness + start portal polling ──\\n"
    "  // Derive container name: ainame + human firstname (lowercase, no spaces)\\n"
    "  const seedName = (payTestData.name || firstName || 'human').toLowerCase().replace(/[^a-z]/g, '');\\n"
    "  const seedAiName = (aiName || 'ai').toLowerCase().replace(/[^a-z]/g, '');\\n"
    "  const derivedContainer = seedAiName + seedName;\\n"
    "  payTestData.containerName = derivedContainer;\\n"
    "  logPayTestData({ ...payTestData, event: 'birth:seed:sending', containerName: derivedContainer });\\n"
    "\\n"
    "  // Fire seed to Witness via our proxy (non-blocking — don't await)\\n"
    "  fetch(`${WITNESS_WEBHOOK_HOST}/api/birth/start`, {\\n"
    "    method: 'POST',\\n"
    "    headers: { 'Content-Type': 'application/json' },\\n"
    "    body: JSON.stringify({\\n"
    "      name: payTestData.name || firstName,\\n"
    "      email: payTestData.email || '',\\n"
    "      human_name: payTestData.name || firstName,\\n"
    "      ai_name: aiName,\\n"
    "      tier: payTestData.tierPaid || 'awakened',\\n"
    "      container: derivedContainer,\\n"
    "    }),\\n"
    "  }).then(r => r.json())\\n"
    "    .then(d => {\\n"
    "      console.log('[ptc-v5] birth/start response:', d);\\n"
    "      // If server returns a different container, use that\\n"
    "      if (d.container) payTestData.containerName = d.container;\\n"
    "      logPayTestData({ ...payTestData, event: 'birth:seed:sent', serverContainer: d.container || derivedContainer });\\n"
    "    })\\n"
    "    .catch(err => {\\n"
    "      console.warn('[ptc-v5] birth/start failed (will still poll with derived name):', err.message);\\n"
    "      logPayTestData({ ...payTestData, event: 'birth:seed:failed', error: err.message });\\n"
    "    });\\n"
    "\\n"
    "  // Start portal polling immediately with derived container name\\n"
    "  // (if server corrects the name, the watcher already has a reference)\\n"
    "  runPortalButtonWatcher(dom, aiName);\\n"
    "}"
)

idx = ed.find(OLD)
if idx == -1:
    print("ERROR: Could not find injection point in _elementor_data")
    print("Looking for:", repr(OLD[:80]))
    sys.exit(1)

print(f"  Found injection point at position {idx}")

# 3. Replace
ed_new = ed[:idx] + NEW + ed[idx + len(OLD):]
print(f"  New _elementor_data length: {len(ed_new)} (added {len(ed_new) - len(ed)} chars)")

# 4. Validate JSON
try:
    json.loads(ed_new)
    print("  JSON validation: PASSED")
except json.JSONDecodeError as e:
    print(f"  JSON validation: FAILED — {e}")
    sys.exit(1)

# 5. Save to WordPress
print(f"Saving to page {PAGE_ID}...")
save_resp = requests.post(
    WP_API,
    auth=AUTH,
    json={'meta': {'_elementor_data': ed_new}},
)
if save_resp.status_code == 200:
    print("  Saved successfully!")
else:
    print(f"  ERROR: {save_resp.status_code} — {save_resp.text[:200]}")
    sys.exit(1)

# 6. Clear Elementor cache
print("Clearing Elementor cache...")
cache_resp = requests.delete(
    'https://purebrain.ai/wp-json/elementor/v1/cache',
    auth=AUTH,
)
print(f"  Cache clear: {cache_resp.status_code}")

print("\nDONE! Page 1232 now sends seed + polls for magic link.")
print(f"Container naming: {{aiName}}{{humanName}} — e.g. 'keenjared'")
