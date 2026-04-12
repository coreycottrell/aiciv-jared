#!/usr/bin/env python3
"""
Comprehensive visual + functional test for pay-test pages.
Tests: pay-test and pay-test-sandbox, both awakening anchors.
"""

import os
import sys
import time
import json
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

SCREENSHOTS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

PAGES = [
    {
        "name": "pay-test",
        "url": "https://purebrain.ai/pay-test/#awakening",
        "slug": "paytest",
    },
    {
        "name": "pay-test-sandbox",
        "url": "https://purebrain.ai/pay-test-sandbox/#awakening",
        "slug": "paytestsandbox",
    },
]

results = {}


def ss(page, label, slug):
    """Take a screenshot with standardized naming."""
    path = f"{SCREENSHOTS_DIR}/{TIMESTAMP}_{slug}_{label}.png"
    page.screenshot(path=path, full_page=False)
    print(f"  [screenshot] {label} -> {os.path.basename(path)}")
    return path


def check_visual_self_tag(page):
    """Check if VISUAL_SELF tag appears anywhere visible in the chat."""
    content = page.content()
    if "VISUAL_SELF" in content:
        # Check if it's in visible text (not just hidden HTML)
        visible = page.evaluate("""
            () => {
                const all = document.querySelectorAll('*');
                for (const el of all) {
                    if (el.childNodes) {
                        for (const node of el.childNodes) {
                            if (node.nodeType === 3 && node.textContent.includes('VISUAL_SELF')) {
                                return 'FOUND IN TEXT: ' + node.textContent.substring(0, 100);
                            }
                        }
                    }
                }
                return null;
            }
        """)
        return visible if visible else "FOUND IN HTML BUT NOT VISIBLE TEXT"
    return None


def wait_for_chat_response(page, timeout=15000):
    """Wait for a chat response to appear after sending a message."""
    try:
        # Wait for a new assistant/bot message to appear
        page.wait_for_selector('.message.assistant, .chat-message.bot, [data-role="assistant"], .ai-message',
                                timeout=timeout)
        return True
    except PlaywrightTimeout:
        return False


def find_chat_input(page):
    """Find the chat input field."""
    selectors = [
        'input[type="text"]',
        'textarea',
        '[placeholder*="Type"]',
        '[placeholder*="message"]',
        '[placeholder*="chat"]',
        '.chat-input input',
        '.chat-input textarea',
        '#chat-input',
        '.message-input',
    ]
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                return el, sel
        except:
            pass
    return None, None


def find_send_button(page):
    """Find the send button."""
    selectors = [
        'button[type="submit"]',
        '.send-button',
        '.chat-send',
        'button:has-text("Send")',
        'button svg',  # icon button
        '[aria-label="Send"]',
    ]
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                return el, sel
        except:
            pass
    return None, None


def test_page(playwright, page_info):
    """Run all tests on a single pay-test page."""
    name = page_info["name"]
    url = page_info["url"]
    slug = page_info["slug"]

    print(f"\n{'='*60}")
    print(f"TESTING: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    result = {
        "name": name,
        "url": url,
        "screenshots": [],
        "chat_loads": False,
        "chat_input_found": False,
        "chat_input_selector": None,
        "hello_sent": False,
        "ai_responded": False,
        "response_text": None,
        "visual_self_tag": None,
        "bypass_works": False,
        "keen_name": False,
        "discover_button": False,
        "pricing_visible": False,
        "tiers_found": [],
        "paypal_modal": False,
        "errors": [],
        "console_errors": [],
    }

    console_errors = []

    # --- SECTION A: Normal chat flow ---
    print("\n[A] Chat Pre-Purchase Flow (normal session)")

    browser = playwright.chromium.launch(
        args=[
            "--ignore-certificate-errors",
            "--ignore-ssl-errors",
            "--disable-web-security",
        ]
    )
    context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        ignore_https_errors=True,
    )
    context.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)

    page = context.new_page()
    page.on("pageerror", lambda err: console_errors.append(f"[pageerror] {err}"))

    # A1: Navigate
    print(f"  Navigating to {url}...")
    try:
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        time.sleep(3)  # Let heavy JS load
        p = ss(page, "A1_initial_load", slug)
        result["screenshots"].append(p)
        result["chat_loads"] = True
        print("  Page loaded OK")
    except Exception as e:
        result["errors"].append(f"Navigation failed: {e}")
        print(f"  ERROR: {e}")
        browser.close()
        return result

    # A2: Check chat widget
    print("  Checking chat widget...")
    # Look for any chat-like container
    chat_containers = page.query_selector_all(
        '.chat-container, .chat-widget, #chat, .chatbox, [class*="chat"]'
    )
    print(f"  Found {len(chat_containers)} chat-related elements")

    # Try to find the input
    chat_input, input_sel = find_chat_input(page)
    if chat_input:
        result["chat_input_found"] = True
        result["chat_input_selector"] = input_sel
        print(f"  Chat input found: {input_sel}")
    else:
        print("  WARNING: Chat input not found with standard selectors")
        # Try to get page structure
        inputs = page.evaluate("""
            () => {
                const inputs = document.querySelectorAll('input, textarea');
                return Array.from(inputs).map(el => ({
                    tag: el.tagName,
                    type: el.type || '',
                    placeholder: el.placeholder || '',
                    id: el.id || '',
                    class: el.className || '',
                    visible: el.offsetParent !== null
                }));
            }
        """)
        print(f"  All inputs on page: {json.dumps(inputs, indent=2)}")

    # A3: Type "hello" and send
    if chat_input:
        print("  Typing 'hello'...")
        try:
            chat_input.click()
            time.sleep(0.5)
            chat_input.fill("hello")
            time.sleep(0.5)
            p = ss(page, "A3_hello_typed", slug)
            result["screenshots"].append(p)

            # Try Enter key first
            page.keyboard.press("Enter")
            result["hello_sent"] = True
            print("  'hello' sent via Enter")

            # Wait for response
            time.sleep(8)  # Chat responses can be slow
            p = ss(page, "A4_after_hello", slug)
            result["screenshots"].append(p)

            # Check for response text
            response_text = page.evaluate("""
                () => {
                    // Look for AI/bot messages
                    const selectors = [
                        '.message.assistant', '.ai-message', '[data-role="assistant"]',
                        '.chat-message-bot', '.bot-message', '.assistant-message'
                    ];
                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el) return el.textContent.trim().substring(0, 200);
                    }
                    // Fallback: find any recent message
                    const msgs = document.querySelectorAll('[class*="message"]');
                    const last = msgs[msgs.length - 1];
                    return last ? last.textContent.trim().substring(0, 200) : null;
                }
            """)
            if response_text:
                result["ai_responded"] = True
                result["response_text"] = response_text
                print(f"  AI responded: {response_text[:100]}...")
            else:
                print("  No AI response detected yet")

            # A5: Check VISUAL_SELF tag
            vs = check_visual_self_tag(page)
            result["visual_self_tag"] = vs
            if vs:
                print(f"  WARNING: VISUAL_SELF tag found: {vs}")
            else:
                print("  VISUAL_SELF tag: not found (good)")

        except Exception as e:
            result["errors"].append(f"Chat interaction failed: {e}")
            print(f"  ERROR in chat: {e}")

    browser.close()

    # --- SECTION B: Bypass testing (fresh/incognito session) ---
    print("\n[B] Bypass Testing (fresh incognito session)")

    browser2 = playwright.chromium.launch(
        args=[
            "--ignore-certificate-errors",
            "--ignore-ssl-errors",
        ]
    )
    context2 = browser2.new_context(
        viewport={"width": 1440, "height": 900},
        ignore_https_errors=True,
    )
    page2 = context2.new_page()

    try:
        print(f"  Navigating (fresh session)...")
        page2.goto(url, timeout=30000, wait_until="domcontentloaded")
        time.sleep(3)

        chat_input2, sel2 = find_chat_input(page2)
        if chat_input2:
            print("  Typing bypass code: pb-full-bypass")
            chat_input2.click()
            time.sleep(0.5)
            chat_input2.fill("pb-full-bypass")
            time.sleep(0.3)
            p = ss(page2, "B1_bypass_typed", slug)
            result["screenshots"].append(p)

            page2.keyboard.press("Enter")
            print("  Bypass sent - waiting for response...")
            time.sleep(8)

            p = ss(page2, "B2_bypass_response", slug)
            result["screenshots"].append(p)

            # Check for Keen and Discover button
            page_text = page2.evaluate("() => document.body.innerText")

            if "Keen" in page_text:
                result["keen_name"] = True
                print("  'Keen' name found in response")
            else:
                print("  'Keen' NOT found in response text")

            # Look for Discover button
            discover_btn = page2.query_selector(
                'button:has-text("Discover"), a:has-text("Discover"), [class*="discover"]'
            )
            if discover_btn:
                result["discover_button"] = True
                print("  'Discover' button found")
            else:
                print("  'Discover' button NOT found")
                # Full text check
                if "discover" in page_text.lower():
                    result["discover_button"] = True
                    print("  'discover' text found in page (may be button)")

            result["bypass_works"] = result["keen_name"] or result["discover_button"]
        else:
            print("  Chat input not found in fresh session")
            p = ss(page2, "B_no_input", slug)
            result["screenshots"].append(p)
    except Exception as e:
        result["errors"].append(f"Bypass test failed: {e}")
        print(f"  ERROR: {e}")

    # --- SECTION C: Pricing/Payment UI ---
    print("\n[C] Pricing and Payment UI")

    try:
        # If we have the page2 with bypass done, look for pricing
        # Try clicking Discover button
        if result["discover_button"]:
            discover_btn = page2.query_selector(
                'button:has-text("Discover"), a:has-text("Discover"), button:has-text("discover")'
            )
            if discover_btn:
                print("  Clicking Discover button...")
                discover_btn.click()
                time.sleep(3)
                p = ss(page2, "C1_after_discover", slug)
                result["screenshots"].append(p)

        # Look for pricing tiers
        page_text = page2.evaluate("() => document.body.innerText")
        tiers = []
        tier_checks = [
            ("Awakened", "$79"),
            ("Bonded", "$149"),
            ("Partnered", "$499"),
            ("Unified", "$999"),
            ("Enterprise", None),
        ]
        for tier_name, price in tier_checks:
            if tier_name in page_text:
                tiers.append(tier_name)
                if price and price in page_text:
                    print(f"  Found tier: {tier_name} at {price}")
                else:
                    print(f"  Found tier name: {tier_name} (price not confirmed)")

        result["tiers_found"] = tiers
        result["pricing_visible"] = len(tiers) > 0

        p = ss(page2, "C2_pricing_view", slug)
        result["screenshots"].append(p)

        # Try to click a pricing button to see PayPal modal
        if tiers:
            # Look for a subscribe/choose/select button
            subscribe_btn = page2.query_selector(
                'button:has-text("Choose"), button:has-text("Subscribe"), button:has-text("Get Started"), '
                'button:has-text("Select"), [class*="paypal"]'
            )
            if not subscribe_btn:
                # Try to find any button near pricing
                buttons = page2.evaluate("""
                    () => {
                        const buttons = document.querySelectorAll('button, a.button, [role="button"]');
                        return Array.from(buttons).map(b => ({
                            text: b.textContent.trim().substring(0, 50),
                            class: b.className.substring(0, 50)
                        })).filter(b => b.text.length > 0);
                    }
                """)
                print(f"  Available buttons: {json.dumps(buttons[:15], indent=2)}")

            if subscribe_btn:
                print("  Clicking pricing button to test PayPal modal...")
                subscribe_btn.click()
                time.sleep(5)
                p = ss(page2, "C3_paypal_modal", slug)
                result["screenshots"].append(p)

                # Check if PayPal appeared
                paypal_present = page2.evaluate("""
                    () => {
                        const iframes = document.querySelectorAll('iframe');
                        for (const f of iframes) {
                            if (f.src && f.src.includes('paypal')) return true;
                            if (f.name && f.name.includes('paypal')) return true;
                        }
                        return document.body.innerHTML.includes('paypal') ||
                               document.body.innerHTML.includes('PayPal');
                    }
                """)
                result["paypal_modal"] = paypal_present
                if paypal_present:
                    print("  PayPal modal/widget detected")
                else:
                    print("  PayPal modal NOT detected")

    except Exception as e:
        result["errors"].append(f"Pricing test failed: {e}")
        print(f"  ERROR: {e}")

    browser2.close()

    # --- SECTION E: Mobile viewport ---
    print("\n[E] Mobile Viewport Test (375x812)")

    browser3 = playwright.chromium.launch(
        args=[
            "--ignore-certificate-errors",
            "--ignore-ssl-errors",
        ]
    )
    context3 = browser3.new_context(
        viewport={"width": 375, "height": 812},
        ignore_https_errors=True,
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    )
    page3 = context3.new_page()

    try:
        print(f"  Loading on mobile viewport (375x812)...")
        page3.goto(url, timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)

        p = ss(page3, "E1_mobile_initial", slug)
        result["screenshots"].append(p)
        print("  Mobile screenshot captured")

        # Check padding via JS
        padding_info = page3.evaluate("""
            () => {
                const body = document.body;
                const style = window.getComputedStyle(body);
                const main = document.querySelector('main, .main-content, #main');
                const mainStyle = main ? window.getComputedStyle(main) : null;
                return {
                    body_padding_left: style.paddingLeft,
                    body_padding_right: style.paddingRight,
                    body_margin_left: style.marginLeft,
                    body_margin_right: style.marginRight,
                    main_padding: mainStyle ? mainStyle.padding : 'N/A',
                    viewport_width: window.innerWidth,
                    scroll_width: document.documentElement.scrollWidth,
                };
            }
        """)
        print(f"  Mobile padding info: {json.dumps(padding_info, indent=2)}")
        result["mobile_padding"] = padding_info

        # Scroll to check bottom
        page3.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        time.sleep(1)
        p = ss(page3, "E2_mobile_scrolled", slug)
        result["screenshots"].append(p)

    except Exception as e:
        result["errors"].append(f"Mobile test failed: {e}")
        print(f"  ERROR: {e}")
    finally:
        browser3.close()

    # Capture console errors
    result["console_errors"] = console_errors[:20]  # cap at 20

    return result


def main():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    print(f"Pay-Test Page Comprehensive Audit")
    print(f"Timestamp: {TIMESTAMP}")
    print(f"Screenshots dir: {SCREENSHOTS_DIR}")

    all_results = {}

    with sync_playwright() as playwright:
        for page_info in PAGES:
            try:
                result = test_page(playwright, page_info)
                all_results[page_info["name"]] = result
            except Exception as e:
                all_results[page_info["name"]] = {
                    "name": page_info["name"],
                    "error": f"Fatal error: {e}",
                }
                print(f"FATAL ERROR testing {page_info['name']}: {e}")

    # Save results
    results_path = f"{SCREENSHOTS_DIR}/{TIMESTAMP}_test_results.json"
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved: {results_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for name, r in all_results.items():
        print(f"\n{name}:")
        if "error" in r and not r.get("chat_loads"):
            print(f"  FATAL: {r.get('error')}")
            continue
        print(f"  Page loads:        {'YES' if r.get('chat_loads') else 'NO'}")
        print(f"  Chat input found:  {'YES (' + r.get('chat_input_selector','') + ')' if r.get('chat_input_found') else 'NO'}")
        print(f"  Hello sent:        {'YES' if r.get('hello_sent') else 'NO'}")
        print(f"  AI responded:      {'YES' if r.get('ai_responded') else 'NO'}")
        print(f"  VISUAL_SELF tag:   {r.get('visual_self_tag') or 'NOT FOUND (good)'}")
        print(f"  Bypass works:      {'YES' if r.get('bypass_works') else 'NO'}")
        print(f"  Keen name:         {'YES' if r.get('keen_name') else 'NO'}")
        print(f"  Discover button:   {'YES' if r.get('discover_button') else 'NO'}")
        print(f"  Pricing visible:   {'YES' if r.get('pricing_visible') else 'NO'}")
        print(f"  Tiers found:       {r.get('tiers_found', [])}")
        print(f"  PayPal modal:      {'YES' if r.get('paypal_modal') else 'NO'}")
        print(f"  Screenshots:       {len(r.get('screenshots', []))}")
        print(f"  Console errors:    {len(r.get('console_errors', []))}")
        if r.get("errors"):
            print(f"  Test errors:       {r['errors']}")

    return all_results


if __name__ == "__main__":
    main()
