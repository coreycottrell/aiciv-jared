#!/usr/bin/env python3
"""
Pay-test page comprehensive test v3.
Properly navigates: unlock -> scroll to awakening -> click Begin Awakening -> interact with chat.
"""

import os
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
        "slug": "paytest",
    },
    {
        "name": "pay-test-sandbox",
        "url": "https://purebrain.ai/pay-test-sandbox/#awakening",
        "slug": "paytestsandbox",
    },
]


def ss(page, label, slug):
    path = f"{SCREENSHOTS_DIR}/{TIMESTAMP}_{slug}_{label}.png"
    try:
        page.screenshot(path=path, full_page=False)
        print(f"  [ss] {label} -> {os.path.basename(path)}")
    except Exception as e:
        print(f"  [ss] FAILED {label}: {e}")
    return path


def unlock_wp_page(page, slug):
    """Submit WP page password."""
    try:
        pw = page.query_selector('input[type="password"]')
        if pw and pw.is_visible():
            pw.fill(PAGE_PASSWORD)
            time.sleep(0.3)
            btn = page.query_selector('input[type="submit"]')
            if btn:
                btn.click()
            else:
                page.keyboard.press("Enter")
            time.sleep(6)
            print("  Password entered and submitted")
            return True
    except Exception as e:
        print(f"  Unlock error: {e}")
    return False


def navigate_unlock_scroll(page, url, slug, label_prefix=""):
    """Full navigation: go to URL, unlock if needed, scroll to #awakening."""
    screenshots = []

    page.goto(url, timeout=30000, wait_until="domcontentloaded")
    time.sleep(3)

    # Check for password gate
    if page.query_selector('input[type="password"]'):
        p = ss(page, f"{label_prefix}pw_gate", slug)
        screenshots.append(p)
        unlock_wp_page(page, slug)

    # Now on real page - scroll to #awakening anchor
    print("  Scrolling to #awakening section...")
    page.evaluate("""
        () => {
            const el = document.getElementById('awakening');
            if (el) {
                el.scrollIntoView({behavior: 'instant', block: 'start'});
            } else {
                // Try anchor link
                window.scrollTo(0, document.documentElement.scrollHeight * 0.5);
            }
        }
    """)
    time.sleep(2)

    p = ss(page, f"{label_prefix}at_awakening", slug)
    screenshots.append(p)

    return screenshots


def click_begin_awakening(page, slug, label_prefix=""):
    """Click 'Begin Awakening' button to open the chat interface."""
    # Look for the Begin Awakening button
    btn = page.query_selector('.chat-initial__btn, button:has-text("Begin Awakening")')
    if btn:
        print("  'Begin Awakening' button found - clicking...")
        try:
            btn.scroll_into_view_if_needed()
            time.sleep(0.5)
            p = ss(page, f"{label_prefix}before_begin_click", slug)
            btn.click()
            time.sleep(3)
            p2 = ss(page, f"{label_prefix}after_begin_click", slug)
            return True, [p, p2]
        except Exception as e:
            print(f"  Click error: {e}")
    else:
        print("  'Begin Awakening' button NOT found")
        # Check if chat is already open
        chat_input = page.query_selector('#userInput')
        if chat_input and chat_input.is_visible():
            print("  Chat input already visible (no button needed)")
            return True, []
    return False, []


def wait_for_chat_input(page, timeout=10):
    """Wait for chat input to become visible."""
    for _ in range(timeout):
        inp = page.query_selector('#userInput')
        if inp and inp.is_visible():
            return inp
        # Also check textarea
        ta = page.query_selector('textarea.chat-input__field, .chat-input__field')
        if ta and ta.is_visible():
            return ta
        time.sleep(1)
    return None


def get_page_text(page):
    return page.evaluate("() => document.body.innerText")


def check_visual_self(page):
    content = page.content()
    if "VISUAL_SELF" not in content:
        return None
    return page.evaluate("""
        () => {
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            let n;
            while (n = walker.nextNode()) {
                if (n.textContent.includes('VISUAL_SELF')) return 'VISIBLE: ' + n.textContent.substring(0, 100);
            }
            return 'IN_HTML_NOT_VISIBLE';
        }
    """)


def test_page(pw, page_info):
    name = page_info["name"]
    url = page_info["url"]
    slug = page_info["slug"]

    print(f"\n{'='*60}\nTESTING: {name}\nURL: {url}\n{'='*60}")

    result = {
        "name": name,
        "url": url,
        "screenshots": [],
        # Section A
        "page_loads": False,
        "sandbox_banner": False,
        "begin_awakening_btn": False,
        "chat_input_visible": False,
        "hello_sent": False,
        "ai_responded": False,
        "response_text": None,
        "visual_self_tag": None,
        # Section B
        "bypass_sent": False,
        "bypass_response_text": None,
        "keen_name": False,
        "discover_button": False,
        "bypass_works": False,
        # Section C
        "pricing_visible": False,
        "tiers_found": [],
        "paypal_detected": False,
        # Logo check
        "logo_images": [],
        # Section E
        "mobile_loads": False,
        "mobile_no_horizontal_scroll": False,
        "mobile_padding_px": None,
        "mobile_awakening_padding": None,
        # Errors
        "console_errors": [],
        "errors": [],
    }

    # ================================================================
    # SECTION A: Normal chat pre-purchase flow
    # ================================================================
    print("\n[A] Chat Pre-Purchase Flow")
    console_errors = []

    browser = pw.chromium.launch(
        args=["--ignore-certificate-errors", "--ignore-ssl-errors"],
        headless=True,
    )
    ctx = browser.new_context(
        viewport={"width": 1440, "height": 900},
        ignore_https_errors=True,
    )
    ctx.on("console", lambda m: console_errors.append(f"[{m.type}] {m.text[:150]}") if m.type in ("error", "warning") else None)
    page = ctx.new_page()
    page.on("pageerror", lambda e: console_errors.append(f"[pageerror] {str(e)[:200]}"))

    try:
        screenshots = navigate_unlock_scroll(page, url, slug, "A_")
        result["screenshots"] += screenshots
        result["page_loads"] = True

        # Check sandbox banner
        page_text = get_page_text(page)
        result["sandbox_banner"] = "SANDBOX MODE" in page_text or "No real charges" in page_text

        # Screenshot the initial state after unlocking
        p = ss(page, "A1_unlocked_hero", slug)
        result["screenshots"].append(p)

        # Click Begin Awakening
        clicked, click_ss = click_begin_awakening(page, slug, "A_")
        result["screenshots"] += click_ss
        result["begin_awakening_btn"] = clicked

        if clicked:
            # Wait for chat input to appear
            chat_input = wait_for_chat_input(page, timeout=15)
            if chat_input:
                result["chat_input_visible"] = True
                print("  Chat input visible after Begin Awakening click")

                p = ss(page, "A2_chat_open", slug)
                result["screenshots"].append(p)

                # Send "hello"
                print("  Typing 'hello'...")
                chat_input.click()
                time.sleep(0.5)
                chat_input.fill("hello")
                time.sleep(0.3)
                p = ss(page, "A3_hello_typed", slug)
                result["screenshots"].append(p)

                page.keyboard.press("Enter")
                result["hello_sent"] = True
                print("  'hello' sent - waiting 12s for AI response...")
                time.sleep(12)

                p = ss(page, "A4_after_hello_response", slug)
                result["screenshots"].append(p)

                # Get response
                new_text = get_page_text(page)
                # Response is anything after "hello" in the chat
                if len(new_text) > len(page_text) + 20:
                    result["ai_responded"] = True
                    # Extract just the chat portion
                    response_text = page.evaluate("""
                        () => {
                            const chat = document.querySelector('.chat-messages, .chat-container, #chatMessages, [class*="messages"]');
                            return chat ? chat.innerText.substring(0, 400) : null;
                        }
                    """)
                    result["response_text"] = response_text or "Text grew (detected)"
                    print(f"  AI responded: {(response_text or '')[:150]}")

                # VISUAL_SELF check
                vs = check_visual_self(page)
                result["visual_self_tag"] = vs
                print(f"  VISUAL_SELF: {vs or 'NOT FOUND (good)'}")

            else:
                print("  Chat input still not visible after clicking Begin Awakening")
                p = ss(page, "A2_chat_not_visible", slug)
                result["screenshots"].append(p)
                # Dump DOM around chat area
                chat_area = page.evaluate("""
                    () => {
                        const el = document.getElementById('awakening');
                        return el ? el.innerHTML.substring(0, 500) : 'awakening div not found';
                    }
                """)
                print(f"  Awakening div HTML: {chat_area[:300]}")
        else:
            p = ss(page, "A2_no_begin_btn", slug)
            result["screenshots"].append(p)

        # Final state screenshot
        p = ss(page, "A_final", slug)
        result["screenshots"].append(p)

    except Exception as e:
        result["errors"].append(f"Section A: {e}")
        print(f"  FATAL: {e}")
        import traceback; traceback.print_exc()

    browser.close()

    # ================================================================
    # SECTION B+C: Bypass testing + pricing
    # ================================================================
    print("\n[B] Bypass Testing + [C] Pricing (fresh session)")

    browser2 = pw.chromium.launch(
        args=["--ignore-certificate-errors", "--ignore-ssl-errors"],
        headless=True,
    )
    ctx2 = browser2.new_context(
        viewport={"width": 1440, "height": 900},
        ignore_https_errors=True,
    )
    page2 = ctx2.new_page()

    try:
        navigate_unlock_scroll(page2, url, slug, "B_")

        clicked2, _ = click_begin_awakening(page2, slug, "B_")
        if not clicked2:
            p = ss(page2, "B_no_begin_btn", slug)
            result["screenshots"].append(p)
        else:
            chat_input2 = wait_for_chat_input(page2, timeout=15)
            if chat_input2:
                print("  Chat input visible in fresh session")
                print("  Typing 'pb-full-bypass'...")
                chat_input2.click()
                time.sleep(0.5)
                chat_input2.fill("pb-full-bypass")
                time.sleep(0.3)
                p = ss(page2, "B1_bypass_typed", slug)
                result["screenshots"].append(p)

                page2.keyboard.press("Enter")
                result["bypass_sent"] = True
                print("  Bypass sent - waiting 12s...")
                time.sleep(12)

                p = ss(page2, "B2_bypass_response", slug)
                result["screenshots"].append(p)

                page_text2 = get_page_text(page2)
                result["bypass_response_text"] = page_text2[:600]
                print(f"  Page text after bypass: {page_text2[:400]}")

                result["keen_name"] = "Keen" in page_text2
                print(f"  Keen name: {result['keen_name']}")

                # Discover button check
                discover_btn = page2.query_selector(
                    'button:has-text("Discover"), a:has-text("Discover")'
                )
                result["discover_button"] = (discover_btn is not None) or ("discover" in page_text2.lower())
                print(f"  Discover button/text: {result['discover_button']}")
                result["bypass_works"] = result["keen_name"] or result["discover_button"]

                # ============================================================
                # SECTION C: Pricing
                # ============================================================
                print("\n[C] Pricing UI")

                if discover_btn:
                    print("  Clicking Discover button...")
                    try:
                        discover_btn.scroll_into_view_if_needed()
                        discover_btn.click()
                        time.sleep(4)
                        p = ss(page2, "C1_after_discover", slug)
                        result["screenshots"].append(p)
                    except Exception as e:
                        print(f"  Discover click error: {e}")

                # Scroll to find pricing
                for scroll_pct in [0.4, 0.6, 0.8, 1.0]:
                    page2.evaluate(f"window.scrollTo(0, document.documentElement.scrollHeight * {scroll_pct})")
                    time.sleep(1)
                    pricing_text = get_page_text(page2)
                    if any(t in pricing_text for t in ["Awakened", "Bonded", "Partnered", "Unified"]):
                        break

                p = ss(page2, "C2_pricing_area", slug)
                result["screenshots"].append(p)

                pricing_text = get_page_text(page2)
                tiers = []
                for tier_name, price in [("Awakened", "$79"), ("Bonded", "$149"), ("Partnered", "$499"), ("Unified", "$999"), ("Enterprise", None)]:
                    if tier_name in pricing_text:
                        tiers.append(tier_name)
                        price_str = f" at {price}" if (price and price in pricing_text) else " (price TBD)"
                        print(f"  Tier: {tier_name}{price_str}")

                result["tiers_found"] = tiers
                result["pricing_visible"] = len(tiers) > 0

                # Logo check
                logos = page2.evaluate("""
                    () => {
                        return Array.from(document.querySelectorAll('img')).filter(img =>
                            img.src && (img.src.includes('logo') || img.src.includes('icon') ||
                            img.src.includes('spiral') || img.src.includes('hex') || img.src.includes('brain'))
                        ).map(img => ({
                            file: img.src.substring(img.src.lastIndexOf('/') + 1, img.src.lastIndexOf('/') + 50),
                            width: img.naturalWidth,
                            height: img.naturalHeight,
                        }));
                    }
                """)
                result["logo_images"] = logos
                print(f"  Logo images: {json.dumps(logos, indent=2)}")

                # Try to trigger PayPal by clicking a plan button
                if tiers:
                    # Look for subscribe/select buttons
                    plan_buttons = page2.evaluate("""
                        () => {
                            const all = document.querySelectorAll('button, [class*="plan"] button, [class*="tier"] button, [class*="paypal"]');
                            return Array.from(all).filter(b => b.offsetParent !== null).map(b => ({
                                text: b.textContent.trim().substring(0, 60),
                                class: b.className.substring(0, 60),
                            })).filter(b => b.text.length > 0);
                        }
                    """)
                    print(f"  Plan buttons: {json.dumps(plan_buttons[:8], indent=2)}")

                    # Try to click Awakened plan button
                    plan_btn = page2.query_selector(
                        'button:has-text("Choose"), button:has-text("Subscribe"), button:has-text("Get Started"), '
                        'button:has-text("Awakened"), button:has-text("Select")'
                    )
                    if plan_btn:
                        print(f"  Clicking plan button: {plan_btn.text_content()[:50]}")
                        plan_btn.scroll_into_view_if_needed()
                        plan_btn.click()
                        time.sleep(6)
                        p = ss(page2, "C3_paypal_modal", slug)
                        result["screenshots"].append(p)

                        paypal = page2.evaluate("""
                            () => {
                                for (const f of document.querySelectorAll('iframe')) {
                                    if (f.src && f.src.includes('paypal')) return 'iframe: ' + f.src.substring(0,80);
                                }
                                if (document.querySelector('[class*="paypal"]')) return 'paypal class element';
                                if (document.body.innerHTML.includes('paypal.com')) return 'paypal.com in HTML';
                                return null;
                            }
                        """)
                        result["paypal_detected"] = paypal is not None
                        print(f"  PayPal: {paypal or 'NOT detected'}")

            else:
                print("  Chat input not visible in bypass session")
                p = ss(page2, "B_no_chat", slug)
                result["screenshots"].append(p)

    except Exception as e:
        result["errors"].append(f"Section B/C: {e}")
        print(f"  ERROR: {e}")
        import traceback; traceback.print_exc()

    browser2.close()

    # ================================================================
    # SECTION E: Mobile viewport
    # ================================================================
    print("\n[E] Mobile Viewport (375x812)")

    browser3 = pw.chromium.launch(
        args=["--ignore-certificate-errors", "--ignore-ssl-errors"],
        headless=True,
    )
    ctx3 = browser3.new_context(
        viewport={"width": 375, "height": 812},
        ignore_https_errors=True,
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    )
    page3 = ctx3.new_page()

    try:
        navigate_unlock_scroll(page3, url, slug, "E_")

        p = ss(page3, "E1_mobile_top", slug)
        result["screenshots"].append(p)
        result["mobile_loads"] = True

        # Check horizontal scroll
        metrics = page3.evaluate("""
            () => ({
                viewport_width: window.innerWidth,
                scroll_width: document.documentElement.scrollWidth,
                no_horizontal_scroll: document.documentElement.scrollWidth <= window.innerWidth,
            })
        """)
        result["mobile_no_horizontal_scroll"] = metrics["no_horizontal_scroll"]
        print(f"  Viewport: {metrics['viewport_width']}px, ScrollWidth: {metrics['scroll_width']}px")
        print(f"  No horizontal scroll: {metrics['no_horizontal_scroll']}")

        # Get container padding
        container_padding = page3.evaluate("""
            () => {
                const containers = document.querySelectorAll('.container, main, .main-content');
                for (const c of containers) {
                    const cs = window.getComputedStyle(c);
                    const pl = parseFloat(cs.paddingLeft);
                    if (pl > 0) return {el: c.tagName + '.' + c.className.split(' ')[0], paddingLeft: cs.paddingLeft, paddingRight: cs.paddingRight};
                }
                return null;
            }
        """)
        result["mobile_padding_px"] = container_padding
        print(f"  Container padding: {container_padding}")

        # Check awakening section padding
        awakening_padding = page3.evaluate("""
            () => {
                const el = document.getElementById('awakening') || document.querySelector('[id*="awakening"]');
                if (!el) return null;
                const cs = window.getComputedStyle(el);
                return {paddingLeft: cs.paddingLeft, paddingRight: cs.paddingRight, padding: cs.padding};
            }
        """)
        result["mobile_awakening_padding"] = awakening_padding
        print(f"  Awakening section padding: {awakening_padding}")

        # Scroll to see awakening
        page3.evaluate("document.getElementById('awakening') && document.getElementById('awakening').scrollIntoView()")
        time.sleep(1)
        p = ss(page3, "E2_mobile_awakening", slug)
        result["screenshots"].append(p)

        # Click Begin Awakening on mobile
        begin_btn_mobile = page3.query_selector('.chat-initial__btn, button:has-text("Begin Awakening")')
        if begin_btn_mobile:
            print("  Begin Awakening visible on mobile - clicking...")
            begin_btn_mobile.click()
            time.sleep(3)
            p = ss(page3, "E3_mobile_chat_open", slug)
            result["screenshots"].append(p)

    except Exception as e:
        result["errors"].append(f"Section E: {e}")
        print(f"  ERROR: {e}")
    finally:
        browser3.close()

    result["console_errors"] = console_errors[:20]
    return result


def main():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    print(f"Pay-Test Comprehensive Audit v3 | {TIMESTAMP}")

    all_results = {}

    with sync_playwright() as pw:
        for page_info in PAGES:
            try:
                r = test_page(pw, page_info)
                all_results[page_info["name"]] = r
            except Exception as e:
                all_results[page_info["name"]] = {"name": page_info["name"], "fatal": str(e)}
                print(f"FATAL for {page_info['name']}: {e}")

    # Save JSON
    results_path = f"{SCREENSHOTS_DIR}/{TIMESTAMP}_test_results_v3.json"
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults: {results_path}")

    # Print summary
    print(f"\n{'='*60}\nSUMMARY\n{'='*60}")
    for name, r in all_results.items():
        if "fatal" in r:
            print(f"\n{name}: FATAL - {r['fatal']}")
            continue
        ok = lambda x: "YES" if x else "NO"
        print(f"\n{name}:")
        print(f"  Page loads:              {ok(r.get('page_loads'))}")
        print(f"  Sandbox banner:          {ok(r.get('sandbox_banner'))}")
        print(f"  Begin Awakening btn:     {ok(r.get('begin_awakening_btn'))}")
        print(f"  Chat input visible:      {ok(r.get('chat_input_visible'))}")
        print(f"  Hello sent:              {ok(r.get('hello_sent'))}")
        print(f"  AI responded:            {ok(r.get('ai_responded'))}")
        resp = r.get('response_text', '')
        if resp:
            print(f"  Response preview:        {str(resp)[:120]}")
        print(f"  VISUAL_SELF tag:         {r.get('visual_self_tag') or 'NOT FOUND (good)'}")
        print(f"  Bypass sent:             {ok(r.get('bypass_sent'))}")
        print(f"  Keen name in response:   {ok(r.get('keen_name'))}")
        print(f"  Discover button:         {ok(r.get('discover_button'))}")
        print(f"  Bypass works:            {ok(r.get('bypass_works'))}")
        print(f"  Pricing visible:         {ok(r.get('pricing_visible'))}")
        print(f"  Tiers found:             {r.get('tiers_found', [])}")
        print(f"  PayPal detected:         {ok(r.get('paypal_detected'))}")
        print(f"  Mobile loads:            {ok(r.get('mobile_loads'))}")
        print(f"  Mobile no h-scroll:      {ok(r.get('mobile_no_horizontal_scroll'))}")
        print(f"  Mobile padding:          {r.get('mobile_padding_px')}")
        print(f"  Awakening padding:       {r.get('mobile_awakening_padding')}")
        print(f"  Screenshots taken:       {len(r.get('screenshots', []))}")
        errs = r.get('console_errors', [])
        if errs:
            print(f"  Console errors ({len(errs)}):")
            for e in errs[:5]:
                print(f"    {e[:120]}")
        if r.get("errors"):
            print(f"  Test errors:             {r['errors']}")

    print(f"\nAll screenshots in: {SCREENSHOTS_DIR}/")
    print(f"Prefix: {TIMESTAMP}_")


if __name__ == "__main__":
    main()
