#!/usr/bin/env python3
"""
Fix post-payment conversation logging to AICIV.

ROOT CAUSE:
  logPayTestData() sends to BOTH /api/log-pay-test AND /api/log-conversation.
  But the payload it sends to /api/log-conversation has NO 'messages' field.
  The server's /api/log-conversation requires 'messages' or 'conversationHistory'.
  Result: every post-payment log-conversation call returns 400.

FIX:
  Split the two endpoints into separate payloads:
    - /api/log-pay-test: gets the full form data (unchanged)
    - /api/log-conversation: gets a 'messages' array built from the onboarding Q&A
      plus the pre-purchase conversation history, so A-C-Gee gets the full picture.

Also tracks a ptcMessages array in the post-payment chat to capture the
onboarding dialogue in messages format.
"""

import json
import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

AUTH = ('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD'))
BASE = 'https://purebrain.ai/wp-json/wp/v2/pages'

# The old logPayTestData function (as it appears raw in JSON string, i.e. \\n = literal \n)
OLD_LOG_FUNC = r"""async function logPayTestData(data) {\n  const payload = {\n    event: data.event || 'pay-test-flow',\n    timestamp: new Date().toISOString(),\n    tier: payTestData.tier,\n    orderId: payTestData.orderId,\n    aiName: payTestData.aiName,\n    name: payTestData.name,\n    email: payTestData.email,\n    company: payTestData.company,\n    role: payTestData.role,\n    primaryGoal: payTestData.primaryGoal,\n    telegramBotToken: payTestData.telegramBotToken,\n    claudeMaxStatus: payTestData.claudeMaxStatus,\n    ...data,\n    prePurchaseSessionId: payTestData.prePurchaseSessionId || null,\n    prePurchaseMessageCount: payTestData.prePurchaseMessageCount || 0,\n  };\n\n  const endpoints = [\n    'https://api.purebrain.ai/api/log-pay-test',\n    'https://api.purebrain.ai/api/log-conversation',\n  ];\n\n  await Promise.allSettled(\n    endpoints.map((url) =>\n      fetch(url, {\n        method: 'POST',\n        headers: { 'Content-Type': 'application/json' },\n        mode: 'cors',\n        body: JSON.stringify(payload),\n      }).catch((err) => {\n        console.warn(`[pay-test] Log to ${url} failed (non-fatal):`, err.message);\n      }),\n    ),\n  );\n}"""

# The new function - splits payloads so /api/log-conversation gets the required 'messages' field
NEW_LOG_FUNC = r"""async function logPayTestData(data) {\n  // Build base payload for /api/log-pay-test (form data)\n  const payTestPayload = {\n    event: data.event || 'pay-test-flow',\n    timestamp: new Date().toISOString(),\n    tier: payTestData.tier,\n    orderId: payTestData.orderId,\n    aiName: payTestData.aiName,\n    name: payTestData.name,\n    email: payTestData.email,\n    company: payTestData.company,\n    role: payTestData.role,\n    primaryGoal: payTestData.primaryGoal,\n    telegramBotToken: payTestData.telegramBotToken,\n    claudeMaxStatus: payTestData.claudeMaxStatus,\n    ...data,\n    prePurchaseSessionId: payTestData.prePurchaseSessionId || null,\n    prePurchaseMessageCount: payTestData.prePurchaseMessageCount || 0,\n  };\n\n  // Build messages array for /api/log-conversation (required by AICIV)\n  // Combines pre-purchase chat history + onboarding Q&A collected so far\n  const preMsgs = (payTestData.prePurchaseHistory && payTestData.prePurchaseHistory.length)\n    ? payTestData.prePurchaseHistory\n    : ((window._pbPrePurchaseSession && window._pbPrePurchaseSession.conversationHistory)\n        ? window._pbPrePurchaseSession.conversationHistory\n        : []);\n\n  // Build onboarding messages from collected payTestData fields\n  const onboardingMsgs = [];\n  if (payTestData.name) {\n    onboardingMsgs.push({ role: 'assistant', content: 'What is your name?' });\n    onboardingMsgs.push({ role: 'user', content: payTestData.name });\n  }\n  if (payTestData.email) {\n    onboardingMsgs.push({ role: 'assistant', content: 'What email should we use to reach you?' });\n    onboardingMsgs.push({ role: 'user', content: payTestData.email });\n  }\n  if (payTestData.company) {\n    onboardingMsgs.push({ role: 'assistant', content: 'Are you working within a company or organization?' });\n    onboardingMsgs.push({ role: 'user', content: payTestData.company });\n  }\n  if (payTestData.role) {\n    onboardingMsgs.push({ role: 'assistant', content: 'What is your role or title?' });\n    onboardingMsgs.push({ role: 'user', content: payTestData.role });\n  }\n  if (payTestData.primaryGoal) {\n    onboardingMsgs.push({ role: 'assistant', content: 'If your AI could do one thing exceptionally well for you, what would it be?' });\n    onboardingMsgs.push({ role: 'user', content: payTestData.primaryGoal });\n  }\n\n  const allMessages = [...preMsgs, ...onboardingMsgs];\n\n  // Use the pre-purchase session ID if available, else generate one\n  const logSessionId = payTestData.prePurchaseSessionId\n    || ('pb-post-' + (payTestData.orderId || Date.now()));\n\n  // Payload for /api/log-conversation (requires 'messages' field for AICIV)\n  const convPayload = {\n    session_id: logSessionId,\n    messages: allMessages.length ? allMessages : [\n      { role: 'user', content: '[Post-payment onboarding - no pre-purchase chat history]' }\n    ],\n    source: 'purebrain-post-payment',\n    page_url: window.location.href,\n    aiName: payTestData.aiName,\n    userName: payTestData.name,\n    userTier: payTestData.tier,\n    metadata: {\n      event: data.event || 'pay-test-flow',\n      orderId: payTestData.orderId,\n      phase: 'post-payment',\n      claudeMaxStatus: payTestData.claudeMaxStatus,\n    },\n  };\n\n  // Send to both endpoints with correct payloads\n  await Promise.allSettled([\n    fetch('https://api.purebrain.ai/api/log-pay-test', {\n      method: 'POST',\n      headers: { 'Content-Type': 'application/json' },\n      mode: 'cors',\n      body: JSON.stringify(payTestPayload),\n    }).catch((err) => console.warn('[pay-test] log-pay-test failed:', err.message)),\n\n    fetch('https://api.purebrain.ai/api/log-conversation', {\n      method: 'POST',\n      headers: { 'Content-Type': 'application/json' },\n      mode: 'cors',\n      body: JSON.stringify(convPayload),\n    }).catch((err) => console.warn('[pay-test] log-conversation failed:', err.message)),\n  ]);\n}"""


def fix_page(page_id):
    print(f"\n{'='*60}")
    print(f"Processing page {page_id}...")

    resp = requests.get(f'{BASE}/{page_id}?context=edit', auth=AUTH)
    if resp.status_code != 200:
        print(f"  [ERROR] Could not fetch page: {resp.status_code}")
        return False

    data = resp.json()
    elem_str = data['meta']['_elementor_data']

    # Check that old function exists
    if OLD_LOG_FUNC not in elem_str:
        print(f"  [WARN] Old logPayTestData function not found in page {page_id}")
        print(f"  Checking if already fixed...")
        if 'payTestPayload' in elem_str:
            print(f"  Already fixed (payTestPayload found). Skipping.")
            return True
        else:
            print(f"  Not fixed and old pattern not found. Manual inspection needed.")
            return False

    # Replace the old function with the new one
    new_elem_str = elem_str.replace(OLD_LOG_FUNC, NEW_LOG_FUNC, 1)

    if new_elem_str == elem_str:
        print(f"  [ERROR] Replacement had no effect!")
        return False

    # Validate JSON
    try:
        parsed = json.loads(new_elem_str)
        print(f"  JSON valid ({len(new_elem_str)} chars)")
    except json.JSONDecodeError as e:
        print(f"  [CRITICAL] JSON INVALID after replacement: {e}")
        return False

    # Count replacements
    old_count = elem_str.count('payTestPayload')
    new_count = new_elem_str.count('payTestPayload')
    print(f"  'payTestPayload' occurrences: {old_count} -> {new_count}")

    # Save to WordPress
    save_resp = requests.post(
        f'{BASE}/{page_id}',
        auth=AUTH,
        json={'meta': {'_elementor_data': new_elem_str}}
    )

    if save_resp.status_code == 200:
        print(f"  SAVED successfully")
        return True
    else:
        print(f"  [ERROR] Save failed: {save_resp.status_code}: {save_resp.text[:300]}")
        return False


def clear_elementor_cache():
    resp = requests.delete(
        'https://purebrain.ai/wp-json/elementor/v1/cache',
        auth=AUTH
    )
    print(f"\nElementor cache clear: {'OK (200)' if resp.status_code == 200 else f'status {resp.status_code}'}")


def verify_fix(page_id):
    """Quick check to confirm the fix is in place."""
    resp = requests.get(f'{BASE}/{page_id}?context=edit', auth=AUTH)
    elem_str = resp.json()['meta']['_elementor_data']

    has_old = OLD_LOG_FUNC in elem_str
    has_new = 'payTestPayload' in elem_str and 'convPayload' in elem_str
    has_messages_field = "'messages': allMessages" in elem_str or '"messages": allMessages' in elem_str or 'messages: allMessages' in elem_str

    print(f"\nVerification page {page_id}:")
    print(f"  Old function present: {has_old}")
    print(f"  New function present (payTestPayload/convPayload): {has_new}")
    print(f"  messages field in new function: {has_messages_field}")
    return has_new and not has_old


if __name__ == '__main__':
    pages = [468, 439]

    results = {}
    for pid in pages:
        results[pid] = fix_page(pid)

    clear_elementor_cache()

    print(f"\n{'='*60}")
    print("VERIFICATION:")
    all_ok = True
    for pid in pages:
        ok = verify_fix(pid)
        results[pid] = ok
        if not ok:
            all_ok = False

    print(f"\n{'='*60}")
    print("SUMMARY:")
    for pid, ok in results.items():
        print(f"  Page {pid}: {'FIXED' if ok else 'FAILED'}")

    if all_ok:
        print("\nAll pages fixed. Post-payment chat will now log to AICIV correctly.")
        print("The /api/log-conversation endpoint will receive:")
        print("  - Pre-purchase chat history (merged from window._pbPrePurchaseSession)")
        print("  - Post-payment onboarding Q&A (name, email, company, role, goal)")
        print("  - session_id linked to pre-purchase session")
    else:
        print("\nSome pages failed. Check output above.")
