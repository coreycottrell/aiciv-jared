#!/usr/bin/env python3
"""
Fix post-payment chat logging continuity + UI polish on pay-test pages (439, 468).

PART 1: Chat log continuity
- Pass session_id from pre-purchase chat to post-purchase flow
- Carry conversationHistory across the payment boundary
- Include session_id in all logPayTestData calls

PART 2: Post-purchase UI polish
- 2.1: Replace opaque logo with transparent spirograph PNG
- 2.2: Responsive padding: 7% mobile, 10% tablet, 15% desktop
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

AUTH = ('Aether', os.getenv('PUREBRAIN_WP_APP_PASSWORD'))
BASE = 'https://purebrain.ai/wp-json/wp/v2/pages'
PAGES = [439, 468]

TRANSPARENT_LOGO_URL = 'https://purebrain.ai/wp-content/uploads/2026/02/purebrain-spirograph-transparent.png'
OLD_LOGO_URL = 'https://purebrain.ai/wp-content/uploads/2026/02/purebrain-hexagon-icon.jpg'


def fix_page(page_id):
    print(f"\n{'='*60}")
    print(f"Fixing page {page_id}...")

    resp = requests.get(f'{BASE}/{page_id}?context=edit', auth=AUTH)
    data = resp.json()
    elem_str = data['meta']['_elementor_data']
    elements = json.loads(elem_str)
    changes = []

    def walk(els):
        for el in els:
            settings = el.get('settings', {})
            if not isinstance(settings, dict):
                continue
            for field in ('editor', 'html'):
                html = settings.get(field, '')
                if not isinstance(html, str) or not html:
                    continue
                if 'addMessage' not in html and 'initPayTestFlow' not in html:
                    continue

                # ============================================================
                # PART 1: LOGGING CONTINUITY
                # ============================================================

                # 1a. Pass session_id + conversationHistory to onPaymentComplete
                if 'window.onPaymentComplete = function(tier, orderId, payerInfo)' in html:
                    old_payment = 'window.onPaymentComplete = function(tier, orderId, payerInfo) {'
                    new_payment = (
                        'window.onPaymentComplete = function(tier, orderId, payerInfo) {\n'
                        '    // PART 1 FIX: Carry pre-purchase session context forward\n'
                        '    window._pbPrePurchaseSession = {\n'
                        '      sessionId: typeof sessionId !== "undefined" ? sessionId : null,\n'
                        '      conversationHistory: (typeof state !== "undefined" && state.conversationHistory) ? JSON.parse(JSON.stringify(state.conversationHistory)) : [],\n'
                        '      aiName: (typeof state !== "undefined" && state.aiName) ? state.aiName : null,\n'
                        '      messageCount: (typeof state !== "undefined") ? state.messageCount : 0\n'
                        '    };'
                    )
                    if '_pbPrePurchaseSession' not in html:
                        html = html.replace(old_payment, new_payment)
                        changes.append("PART1: Pre-purchase session context saved in onPaymentComplete")

                # 1b. In initPayTestFlow, pick up the pre-purchase session and inject into payTestData
                if 'payTestData.timestamps.started' in html and 'payTestData.prePurchaseSessionId' not in html:
                    old_seed = "payTestData.timestamps.started = new Date().toISOString();"
                    new_seed = (
                        "payTestData.timestamps.started = new Date().toISOString();\n\n"
                        "  // PART 1 FIX: Link to pre-purchase session\n"
                        "  if (window._pbPrePurchaseSession) {\n"
                        "    payTestData.prePurchaseSessionId = window._pbPrePurchaseSession.sessionId;\n"
                        "    payTestData.prePurchaseHistory = window._pbPrePurchaseSession.conversationHistory;\n"
                        "    payTestData.prePurchaseMessageCount = window._pbPrePurchaseSession.messageCount;\n"
                        "  }"
                    )
                    html = html.replace(old_seed, new_seed)
                    changes.append("PART1: Pre-purchase session linked in initPayTestFlow")

                # 1c. Include session linkage in logPayTestData payload
                if 'event: data.event' in html and 'prePurchaseSessionId' not in html.split('logPayTestData')[1].split('endpoints')[0]:
                    old_payload_end = "...data,\n  };"
                    new_payload_end = (
                        "...data,\n"
                        "    prePurchaseSessionId: payTestData.prePurchaseSessionId || null,\n"
                        "    prePurchaseMessageCount: payTestData.prePurchaseMessageCount || 0,\n"
                        "  };"
                    )
                    if 'prePurchaseSessionId: payTestData' not in html:
                        html = html.replace(old_payload_end, new_payload_end)
                        changes.append("PART1: Session linkage added to log payload")

                # 1d. Also log full pre-purchase conversation at flow start
                if "event: 'questionnaire:name'" in html and "event: 'flow:start:pre-purchase-history'" not in html:
                    # Add initial log right after flow starts
                    old_start = "await runQuestionnaire(dom, aiName);"
                    new_start = (
                        "// PART 1 FIX: Log pre-purchase history at flow start for linkage\n"
                        "    if (window._pbPrePurchaseSession && window._pbPrePurchaseSession.conversationHistory.length > 0) {\n"
                        "      await logPayTestData({\n"
                        "        ...payTestData,\n"
                        "        event: 'flow:start:pre-purchase-history',\n"
                        "        prePurchaseHistory: window._pbPrePurchaseSession.conversationHistory,\n"
                        "        prePurchaseSessionId: window._pbPrePurchaseSession.sessionId,\n"
                        "      });\n"
                        "    }\n\n"
                        "    await runQuestionnaire(dom, aiName);"
                    )
                    html = html.replace(old_start, new_start)
                    changes.append("PART1: Pre-purchase conversation history logged at flow start")

                # ============================================================
                # PART 2: UI POLISH
                # ============================================================

                # 2.1: Replace old opaque logo with transparent spirograph
                if OLD_LOGO_URL in html:
                    html = html.replace(OLD_LOGO_URL, TRANSPARENT_LOGO_URL)
                    count = html.count(TRANSPARENT_LOGO_URL)
                    changes.append(f"PART2.1: Logo replaced with transparent spirograph ({count} locations)")

                # 2.2: Responsive padding on post-payment container
                if 'pay-test-post-payment' in html and 'padding: 15%' not in html:
                    # The container is created in launchPostPaymentFlow with full viewport
                    old_container_style = (
                        "'position: fixed',\n"
                        "        'top: 0',\n"
                        "        'left: 0',\n"
                        "        'width: 100vw',\n"
                        "        'height: 100vh',\n"
                        "        'z-index: 999999',\n"
                        "        'background: #0a0a0a',\n"
                        "        'overflow-y: auto',"
                    )
                    new_container_style = (
                        "'position: fixed',\n"
                        "        'top: 0',\n"
                        "        'left: 0',\n"
                        "        'width: 100vw',\n"
                        "        'height: 100vh',\n"
                        "        'z-index: 999999',\n"
                        "        'background: #0a0a0a',\n"
                        "        'overflow-y: auto',\n"
                        "        'padding: 15%',\n"
                        "        'box-sizing: border-box',"
                    )
                    if old_container_style in html:
                        html = html.replace(old_container_style, new_container_style)
                        changes.append("PART2.2: Desktop 15% padding added to container")

                # 2.2b: Add responsive media queries for tablet/mobile padding
                if '.ptc-wrapper {' in html and '@media (max-width: 1024px)' not in html.split('ptc-wrapper')[0] + html.split('ptc-wrapper')[1][:2000]:
                    # Add responsive padding overrides after ptc-wrapper styles
                    responsive_css = (
                        '\n\n    /* ── Responsive padding for post-payment container ─── */\n'
                        '    @media (max-width: 1024px) {\n'
                        '      #pay-test-post-payment { padding: 10% !important; }\n'
                        '    }\n'
                        '    @media (max-width: 768px) {\n'
                        '      #pay-test-post-payment { padding: 7% !important; }\n'
                        '    }\n'
                    )
                    # Insert before the closing of the style block
                    # Find the end of the ptc injectStyles content
                    inject_idx = html.find('.ptc-welcome-btn')
                    if inject_idx > 0:
                        # Find the next closing brace of the CSS rule after welcome-btn
                        close_idx = html.find('\n  `;\n', inject_idx)
                        if close_idx > 0:
                            html = html[:close_idx] + responsive_css + html[close_idx:]
                            changes.append("PART2.2: Responsive padding media queries added (7%/10%/15%)")

                settings[field] = html

            if 'elements' in el:
                walk(el['elements'])

    walk(elements)

    if not changes:
        print("  No changes needed")
        return True

    new_elem_str = json.dumps(elements, ensure_ascii=False)
    try:
        json.loads(new_elem_str)
    except json.JSONDecodeError as e:
        print(f"  [CRITICAL] JSON INVALID: {e}")
        return False

    save_resp = requests.post(
        f'{BASE}/{page_id}',
        auth=AUTH,
        json={'meta': {'_elementor_data': new_elem_str}}
    )

    if save_resp.status_code == 200:
        print(f"  SAVED ({len(new_elem_str)} chars)")
        for c in changes:
            print(f"    + {c}")
        return True
    else:
        print(f"  [ERROR] {save_resp.status_code}: {save_resp.text[:200]}")
        return False


def clear_cache():
    resp = requests.delete(
        'https://purebrain.ai/wp-json/elementor/v1/cache',
        auth=AUTH
    )
    print(f"\nElementor cache: {'cleared' if resp.status_code == 200 else f'status {resp.status_code}'}")


if __name__ == '__main__':
    results = {}
    for pid in PAGES:
        results[pid] = fix_page(pid)
    clear_cache()
    print(f"\n{'='*60}")
    print("SUMMARY:")
    for pid, ok in results.items():
        print(f"  Page {pid}: {'OK' if ok else 'FAILED'}")
