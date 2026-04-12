#!/usr/bin/env python3
"""
Comprehensive visual + functional test for pay-test pages.
v2: Handles WordPress password protection gate.
"""

import os
import sys
import time
import json
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

SCREENSHOTS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
PAGE_PASSWORD = "PureBrain.ai253443$$$"

PAGES = [
    {
        "name": "pay-test",
        "url": "https://purebrain.ai/pay-test/#awakening",
        "base_url": "https://purebrain.ai/pay-test/",
        "slug": "paytest",
    },
    {
        "name": "pay-test-sandbox",
        "url": "https://purebrain.ai/pay-test-sandbox/#awakening",
        "base_url": "https://purebrain.ai/pay-test-sandbox/",
        "slug": "paytestsandbox",
    },
]


def ss(page, label, slug):
    """Take a screenshot with standardized naming."""
    path = f"{SCREENSHOTS_DIR}/{TIMESTAMP}_{slug}_{label}.png"
    page.screenshot(path=path, full_page=False)
    print(f"  [ss] {label} -> {os.path.basename(path)}")
    return path


def unlock_page(page, slug):
    """Enter the WordPress page password and submit."""
    print("  Page is password protected - entering password...")
    try:
        pw_input = page.query_selector('#pwbox-439, #pwbox-468, input[type="password"]')
        if pw_input and pw_input.is_visible():
            pw_input.fill(PAGE_PASSWORD)
            # Click Enter button
            enter_btn = page.query_selector('input[type="submit"], button:has-text("Enter")')
            if enter_btn:
                enter_btn.click()
            else:
                page.keyboard.press("Enter")
            print("  Password submitted - waiting for page to load...")
            time.sleep(5)
            return True
        else:
            print("  Password input not found or not visible")
            return False
    except Exception as e:
        print(f"  ERROR unlocking: {e}")
        return False


def is_password_protected(page):
    """Check if current page is showing password protection."""
    pw_box = page.query_selector('input[type="password"]')
    return pw_box is not None and pw_box.is_visible()


def find_chat_input(page):
    """Find the chat input field with broad selectors."""
    selectors = [
        'input[type="text"]',
        'textarea:not([hidden])',
        '[placeholder*="Type"]',
        '[placeholder*="message"]',
        '[placeholder*="chat"]',
        '[placeholder*="Hello"]',
        '[placeholder*="Ask"]',
        '.chat-input input',
        '.chat-input textarea',
        '#chat-input',
        '.message-input',
        '[class*="chat"] input',
        '[class*="chat"] textarea',
        'input:not([type="hidden"]):not([type="password"]):not([type="submit"])',
    ]
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                return el, sel
        except Exception:
            pass
    return None, None


def get_all_buttons(page):
    """Get all visible buttons on the page."""
    return page.evaluate("""
        () => {
            const buttons = document.querySelectorAll('button, input[type="submit"], a[class*="button"], [role="button"]');
            return Array.from(buttons)
                .filter(b => b.offsetParent !== null)
                .map(b => ({
                    text: b.textContent.trim().substring(0, 80),
                    class: b.className.substring(0, 60),
                    id: b.id || '',
                    type: b.tagName,
                }));
        }
    """)


def get_page_text(page):
    """Get all visible text on the page."""
    return page.evaluate("() => document.body.innerText")


def check_visual_self_tag(page):
    """Check if VISUAL_SELF tag appears anywhere."""
    content = page.content()
    if "VISUAL_SELF" in content:
        visible = page.evaluate("""
            () => {
                const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                let node;
                while (node = walker.nextNode()) {
                    if (node.textContent.includes('VISUAL_SELF')) {
                        return 'FOUND: ' + node.textContent.substring(0, 150);
                    }
                }
                return null;
            }
        """)
        return visible if visible else "IN HTML BUT NOT VISIBLE TEXT"
    return None


def navigate_and_unlock(page, url, slug, label="load"):
    """Navigate to URL and unlock if password protected."""
    print(f"  Navigating to {url}...")
    page.goto(url, timeout=30000, wait_until="domcontentloaded")
    time.sleep(3)

    if is_password_protected(page):
        p = ss(page, f"{label}_password_gate", slug)
        unlocked = unlock_page(page, slug)
        if unlocked:
            # Wait for actual page content
            time.sleep(5)
            p = ss(page, f"{label}_after_unlock", slug)
            return p, True
        return p, False

    p = ss(page, label, slug)
    return p, True


def test_page(playwright, page_info):
    """Run all tests on a single pay-test page."""
    name = page_info["name"]
    url = page_info["url"]
    base_url = page_info["base_url"]
    slug = page_info["slug"]

    print(f"\n{'='*60}")
    print(f"TESTING: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    result = {
        "name": name,
        "url": url,
        "screenshots": [],
        "password_required": False,
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
        "mobile_padding": {},
        "mobile_scroll_width_ok": False,
        "errors": [],
        "console_errors": [],
        "all_page_buttons": [],
    }

    console_errors = []

    # ================================================================
    # SECTION A: Normal chat flow
    # ================================================================
    print("\n[A] Chat Pre-Purchase Flow (normal session)")

    browser = playwright.chromium.launch(
        args=[
            "--ignore-certificate-errors",
            "--ignore-ssl-errors",
            "--disable-web-security",
        ],
        headless=True,
    )
    context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        ignore_https_errors=True,
    )
    context.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ("error", "warning") else None)

    page = context.new_page()
    page.on("pageerror", lambda err: console_errors.append(f"[pageerror] {str(err)[:200]}"))

    try:
        p, unlocked = navigate_and_unlock(page, url, slug, "A1_initial")
        result["screenshots"].append(p)

        if not unlocked:
            result["errors"].append("Could not bypass password protection")
            browser.close()
            return result

        result["chat_loads"] = True
        result["password_required"] = True  # it was password protected

        # Dump all inputs for diagnostics
        all_inputs = page.evaluate("""
            () => {
                const inputs = document.querySelectorAll('input, textarea');
                return Array.from(inputs).map(el => ({
                    tag: el.tagName,
                    type: el.type || '',
                    placeholder: el.placeholder || '',
                    id: el.id || '',
                    class: el.className.substring(0, 60) || '',
                    visible: el.offsetParent !== null
                }));
            }
        """)
        print(f"  Inputs after unlock: {json.dumps(all_inputs, indent=2)}")

        # Get visible text snippet
        page_text = get_page_text(page)
        print(f"  First 500 chars of page text: {page_text[:500]}")

        # Get all buttons
        buttons = get_all_buttons(page)
        result["all_page_buttons"] = buttons
        print(f"  Visible buttons ({len(buttons)}): {json.dumps(buttons[:10], indent=2)}")

        # Scroll down to find chat
        page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight * 0.3)")
        time.sleep(1)
        p = ss(page, "A2_scrolled_down", slug)
        result["screenshots"].append(p)

        # Find chat input
        chat_input, input_sel = find_chat_input(page)
        if chat_input:
            result["chat_input_found"] = True
            result["chat_input_selector"] = input_sel
            print(f"  Chat input found: {input_sel}")
        else:
            print("  Chat input NOT found - checking iframes...")
            # Check for iframes (chat might be in an iframe)
            iframes = page.frames
            print(f"  Frames on page: {len(iframes)}")
            for i, frame in enumerate(iframes):
                try:
                    fname = frame.url
                    print(f"  Frame {i}: {fname[:80]}")
                    frame_input = frame.query_selector('input[type="text"], textarea')
                    if frame_input and frame_input.is_visible():
                        print(f"  Found input in frame {i}!")
                        chat_input = frame_input
                        result["chat_input_found"] = True
                        result["chat_input_selector"] = f"iframe[{i}] input"
                        break
                except Exception as fe:
                    print(f"  Frame {i} error: {fe}")

        # A3-A4: Type hello
        if chat_input:
            print("  Typing 'hello'...")
            try:
                chat_input.scroll_into_view_if_needed()
                chat_input.click()
                time.sleep(0.5)
                chat_input.fill("hello")
                time.sleep(0.5)
                p = ss(page, "A3_hello_typed", slug)
                result["screenshots"].append(p)

                page.keyboard.press("Enter")
                result["hello_sent"] = True
                print("  'hello' sent - waiting for AI response (10s)...")
                time.sleep(10)

                p = ss(page, "A4_after_hello_response", slug)
                result["screenshots"].append(p)

                # Detect response
                response_text = page.evaluate("""
                    () => {
                        const selectors = [
                            '.message.assistant', '.ai-message', '[data-role="assistant"]',
                            '.chat-message-bot', '.bot-message', '.assistant-message',
                            '[class*="assistant"]', '[class*="bot"]'
                        ];
                        for (const sel of selectors) {
                            const el = document.querySelector(sel);
                            if (el) return el.textContent.trim().substring(0, 300);
                        }
                        // Fallback - look for messages that came after user input
                        const msgs = document.querySelectorAll('[class*="message"]');
                        if (msgs.length > 1) {
                            return msgs[msgs.length - 1].textContent.trim().substring(0, 300);
                        }
                        return null;
                    }
                """)
                if response_text:
                    result["ai_responded"] = True
                    result["response_text"] = response_text
                    print(f"  AI responded: {response_text[:150]}...")
                else:
                    # Check if page text changed significantly
                    new_text = get_page_text(page)
                    if len(new_text) > len(page_text) + 50:
                        result["ai_responded"] = True
                        result["response_text"] = "Response detected (text grew)"
                        print("  Response detected (page text grew)")
                    else:
                        print("  No AI response detected")

                # A5: VISUAL_SELF check
                vs = check_visual_self_tag(page)
                result["visual_self_tag"] = vs
                if vs:
                    print(f"  VISUAL_SELF FOUND: {vs}")
                else:
                    print("  VISUAL_SELF: not found (good)")

            except Exception as e:
                result["errors"].append(f"Chat interaction: {e}")
                print(f"  ERROR: {e}")

        # Full page screenshot
        p = ss(page, "A5_full_state", slug)
        result["screenshots"].append(p)

    except Exception as e:
        result["errors"].append(f"Section A fatal: {e}")
        print(f"  FATAL: {e}")

    browser.close()

    # ================================================================
    # SECTION B: Bypass testing (fresh incognito)
    # ================================================================
    print("\n[B] Bypass Testing (fresh incognito)")

    browser2 = playwright.chromium.launch(
        args=["--ignore-certificate-errors", "--ignore-ssl-errors"],
        headless=True,
    )
    context2 = browser2.new_context(
        viewport={"width": 1440, "height": 900},
        ignore_https_errors=True,
    )
    page2 = context2.new_page()

    try:
        p, unlocked2 = navigate_and_unlock(page2, url, slug, "B0_fresh")
        result["screenshots"].append(p)

        if not unlocked2:
            result["errors"].append("Bypass: Could not unlock page")
        else:
            # Wait for JS to initialize
            time.sleep(3)

            chat_input2, sel2 = find_chat_input(page2)
            if chat_input2:
                print(f"  Chat input found: {sel2}")
                print("  Typing 'pb-full-bypass'...")
                chat_input2.scroll_into_view_if_needed()
                chat_input2.click()
                time.sleep(0.5)
                chat_input2.fill("pb-full-bypass")
                time.sleep(0.3)
                p = ss(page2, "B1_bypass_typed", slug)
                result["screenshots"].append(p)

                page2.keyboard.press("Enter")
                print("  Bypass sent - waiting 10s for response...")
                time.sleep(10)

                p = ss(page2, "B2_bypass_response", slug)
                result["screenshots"].append(p)

                # Check results
                page_text2 = get_page_text(page2)
                html2 = page2.content()

                print(f"  Page text snippet after bypass: {page_text2[:400]}")

                result["keen_name"] = "Keen" in page_text2 or "keen" in page_text2.lower()
                print(f"  Keen found: {result['keen_name']}")

                # Check for Discover button
                discover_text = "discover" in page_text2.lower() or "Discover" in page_text2
                discover_btn2 = page2.query_selector(
                    'button:has-text("Discover"), a:has-text("Discover")'
                )
                result["discover_button"] = discover_text or (discover_btn2 is not None)
                print(f"  Discover button/text: {result['discover_button']}")

                result["bypass_works"] = result["keen_name"] or result["discover_button"]

                # ================================================================
                # SECTION C: Pricing
                # ================================================================
                print("\n[C] Pricing UI")

                if discover_btn2:
                    print("  Clicking Discover button...")
                    try:
                        discover_btn2.scroll_into_view_if_needed()
                        discover_btn2.click()
                        time.sleep(4)
                        p = ss(page2, "C1_after_discover_click", slug)
                        result["screenshots"].append(p)
                    except Exception as e:
                        print(f"  Discover click failed: {e}")

                # Scroll down to find pricing
                page2.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
                time.sleep(2)
                p = ss(page2, "C2_scrolled_for_pricing", slug)
                result["screenshots"].append(p)

                page_text_pricing = get_page_text(page2)
                tiers = []
                tier_checks = [
                    ("Awakened", "$79"),
                    ("Bonded", "$149"),
                    ("Partnered", "$499"),
                    ("Unified", "$999"),
                    ("Enterprise", None),
                ]
                for tier_name, price in tier_checks:
                    if tier_name in page_text_pricing:
                        tiers.append(tier_name)
                        if price and price in page_text_pricing:
                            print(f"  Tier found: {tier_name} at {price}")
                        else:
                            print(f"  Tier name found: {tier_name} (price not confirmed)")

                result["tiers_found"] = tiers
                result["pricing_visible"] = len(tiers) > 0

                # Get all buttons when pricing is visible
                all_btns = get_all_buttons(page2)
                print(f"  Buttons in pricing state: {json.dumps(all_btns[:10], indent=2)}")

                # Try to click a plan button
                plan_btn = page2.query_selector(
                    'button:has-text("Choose"), button:has-text("Subscribe"), '
                    'button:has-text("Get Started"), button:has-text("Awakened"), '
                    'button:has-text("Select Plan"), [class*="plan-btn"], [class*="paypal-button"]'
                )
                if not plan_btn and tiers:
                    # Try first visible button after pricing text
                    plan_btn = page2.query_selector('button:not([disabled])')

                if plan_btn:
                    print("  Clicking plan button to test PayPal...")
                    try:
                        plan_btn.scroll_into_view_if_needed()
                        plan_btn.click()
                        time.sleep(6)
                        p = ss(page2, "C3_paypal_test", slug)
                        result["screenshots"].append(p)

                        # Check for PayPal
                        paypal_check = page2.evaluate("""
                            () => {
                                const iframes = document.querySelectorAll('iframe');
                                for (const f of iframes) {
                                    if ((f.src && f.src.includes('paypal')) ||
                                        (f.name && f.name.toLowerCase().includes('paypal'))) {
                                        return 'iframe: ' + f.src.substring(0, 80);
                                    }
                                }
                                const bodyHtml = document.body.innerHTML;
                                if (bodyHtml.includes('paypal.com')) return 'paypal.com in HTML';
                                if (bodyHtml.includes('PayPal')) return 'PayPal text in HTML';
                                return null;
                            }
                        """)
                        result["paypal_modal"] = paypal_check is not None
                        if paypal_check:
                            print(f"  PayPal detected: {paypal_check}")
                        else:
                            print("  PayPal NOT detected after button click")
                    except Exception as e:
                        print(f"  Plan button click failed: {e}")

                # Check for spirograph logo (not white-background hexagon)
                logo_check = page2.evaluate("""
                    () => {
                        const imgs = document.querySelectorAll('img');
                        const result = [];
                        for (const img of imgs) {
                            if (img.src && (img.src.includes('logo') || img.src.includes('icon') ||
                                img.src.includes('spirograph') || img.src.includes('hex'))) {
                                result.push({
                                    src: img.src.substring(img.src.lastIndexOf('/') + 1),
                                    class: img.className.substring(0, 50),
                                });
                            }
                        }
                        return result;
                    }
                """)
                print(f"  Logo images found: {json.dumps(logo_check, indent=2)}")
                result["logo_images"] = logo_check

            else:
                print("  Chat input NOT found in fresh session")
                page_text2 = get_page_text(page2)
                print(f"  Page text snippet: {page_text2[:300]}")
                p = ss(page2, "B_no_chat_found", slug)
                result["screenshots"].append(p)

    except Exception as e:
        result["errors"].append(f"Section B/C: {e}")
        print(f"  ERROR: {e}")

    browser2.close()

    # ================================================================
    # SECTION E: Mobile viewport
    # ================================================================
    print("\n[E] Mobile Viewport (375x812 iPhone)")

    browser3 = playwright.chromium.launch(
        args=["--ignore-certificate-errors", "--ignore-ssl-errors"],
        headless=True,
    )
    context3 = browser3.new_context(
        viewport={"width": 375, "height": 812},
        ignore_https_errors=True,
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15",
    )
    page3 = context3.new_page()

    try:
        p, unlocked3 = navigate_and_unlock(page3, url, slug, "E0_mobile")
        result["screenshots"].append(p)

        if unlocked3:
            time.sleep(3)
            p = ss(page3, "E1_mobile_loaded", slug)
            result["screenshots"].append(p)

            # Check padding
            padding_info = page3.evaluate("""
                () => {
                    const body = document.body;
                    const style = window.getComputedStyle(body);
                    // Check if any container has padding
                    const containers = document.querySelectorAll('main, .main, #main, .container, .wrapper, .page-content, .entry-content');
                    const containerPaddings = Array.from(containers).map(c => {
                        const cs = window.getComputedStyle(c);
                        return {
                            el: c.tagName + (c.id ? '#'+c.id : '') + (c.className ? '.'+c.className.split(' ')[0] : ''),
                            paddingLeft: cs.paddingLeft,
                            paddingRight: cs.paddingRight,
                        };
                    });
                    return {
                        body_padding: style.padding,
                        viewport_width: window.innerWidth,
                        scroll_width: document.documentElement.scrollWidth,
                        no_horizontal_scroll: document.documentElement.scrollWidth <= window.innerWidth,
                        containers: containerPaddings,
                    };
                }
            """)
            result["mobile_padding"] = padding_info
            result["mobile_scroll_width_ok"] = padding_info.get("no_horizontal_scroll", False)
            print(f"  Mobile padding: viewport={padding_info['viewport_width']}, scrollWidth={padding_info['scroll_width']}")
            print(f"  No horizontal scroll: {padding_info['no_horizontal_scroll']}")
            if padding_info.get("containers"):
                print(f"  Containers: {json.dumps(padding_info['containers'][:5], indent=2)}")

            # Scroll to see more
            page3.evaluate("window.scrollBy(0, 300)")
            time.sleep(1)
            p = ss(page3, "E2_mobile_scrolled", slug)
            result["screenshots"].append(p)

            # Check specific 7% padding on chat/awakening container
            padding_pct_check = page3.evaluate("""
                () => {
                    const awakening = document.querySelector('#awakening, .awakening, [id*="awakening"]');
                    if (awakening) {
                        const cs = window.getComputedStyle(awakening);
                        return {found: true, padding: cs.padding, paddingLeft: cs.paddingLeft};
                    }
                    // Fallback: check first section
                    const section = document.querySelector('section, .section');
                    if (section) {
                        const cs = window.getComputedStyle(section);
                        return {found: true, el: 'section', padding: cs.padding, paddingLeft: cs.paddingLeft};
                    }
                    return {found: false};
                }
            """)
            print(f"  Awakening section padding: {padding_pct_check}")
            result["awakening_padding"] = padding_pct_check

    except Exception as e:
        result["errors"].append(f"Section E: {e}")
        print(f"  ERROR: {e}")
    finally:
        browser3.close()

    result["console_errors"] = console_errors[:30]
    return result


def main():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    print(f"Pay-Test Page Comprehensive Audit v2")
    print(f"Timestamp: {TIMESTAMP}")
    print(f"Screenshots: {SCREENSHOTS_DIR}")

    all_results = {}

    with sync_playwright() as playwright:
        for page_info in PAGES:
            try:
                result = test_page(playwright, page_info)
                all_results[page_info["name"]] = result
            except Exception as e:
                all_results[page_info["name"]] = {
                    "name": page_info["name"],
                    "error": f"Fatal: {e}",
                }
                import traceback
                traceback.print_exc()

    # Save results
    results_path = f"{SCREENSHOTS_DIR}/{TIMESTAMP}_test_results_v2.json"
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults: {results_path}")

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for name, r in all_results.items():
        print(f"\n{name}:")
        if "error" in r and not r.get("chat_loads"):
            print(f"  FATAL: {r.get('error')}")
            continue
        status = lambda x: "YES" if x else "NO"
        print(f"  Page loads:          {status(r.get('chat_loads'))}")
        print(f"  Password required:   {status(r.get('password_required'))}")
        print(f"  Chat input found:    {status(r.get('chat_input_found'))} ({r.get('chat_input_selector', '')})")
        print(f"  Hello sent:          {status(r.get('hello_sent'))}")
        print(f"  AI responded:        {status(r.get('ai_responded'))}")
        print(f"  VISUAL_SELF tag:     {r.get('visual_self_tag') or 'NOT FOUND (good)'}")
        print(f"  Bypass (pb-full):    {status(r.get('bypass_works'))}")
        print(f"  Keen name:           {status(r.get('keen_name'))}")
        print(f"  Discover button:     {status(r.get('discover_button'))}")
        print(f"  Pricing visible:     {status(r.get('pricing_visible'))}")
        print(f"  Tiers found:         {r.get('tiers_found', [])}")
        print(f"  PayPal modal:        {status(r.get('paypal_modal'))}")
        print(f"  Mobile no-h-scroll:  {status(r.get('mobile_scroll_width_ok'))}")
        print(f"  Screenshots:         {len(r.get('screenshots', []))}")
        if r.get("console_errors"):
            print(f"  Console errors:      {len(r['console_errors'])}")
            for err in r["console_errors"][:5]:
                print(f"    {err[:120]}")
        if r.get("errors"):
            print(f"  Test errors:         {r['errors']}")

    print(f"\nScreenshots saved to: {SCREENSHOTS_DIR}/")
    print("Files: " + ", ".join([
        f"{TIMESTAMP}_{s}_{l}.png"
        for s in ["paytest", "paytestsandbox"]
        for l in ["A1_initial", "A2_scrolled", "A3_hello_typed", "A4_after_hello_response", "B2_bypass_response", "E1_mobile_loaded"]
    ]))

    return all_results


if __name__ == "__main__":
    main()
