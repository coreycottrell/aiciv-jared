#!/usr/bin/env python3
"""
Pay-test page comprehensive test - FINAL version.
Single browser session, careful delays, handles WAF and WP password.
Tests both pages sequentially in one browser to minimize WAF triggers.
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
        print(f"  [ss] {label}")
    except Exception as e:
        print(f"  [ss] FAIL {label}: {e}")
    return path


def is_captcha_page(page):
    text = page.evaluate("() => document.body.innerText")
    return "Please verify you are human" in text or "I'm not a robot" in text


def is_password_page(page):
    pw = page.query_selector('input[type="password"]')
    return pw is not None and pw.is_visible()


def enter_wp_password(page, slug):
    """Enter WordPress page password."""
    print("  Entering page password...")
    pw = page.query_selector('input[type="password"]')
    if pw and pw.is_visible():
        pw.fill(PAGE_PASSWORD)
        time.sleep(0.5)
        btn = page.query_selector('input[type="submit"]')
        if btn:
            btn.click()
        else:
            page.keyboard.press("Enter")
        time.sleep(8)  # More generous wait after password
        return True
    return False


def check_and_handle_blockers(page, slug, label=""):
    """Check for captcha or password gates."""
    if is_captcha_page(page):
        p = ss(page, f"{label}captcha_block", slug)
        return False, "captcha"
    if is_password_page(page):
        p = ss(page, f"{label}pw_gate", slug)
        entered = enter_wp_password(page, slug)
        if not entered:
            return False, "pw_failed"
        # Check again after password
        if is_captcha_page(page):
            return False, "captcha_after_pw"
        return True, "unlocked"
    return True, "open"


def dump_page_structure(page):
    """Get all inputs and buttons for debugging."""
    inputs = page.evaluate("""
        () => Array.from(document.querySelectorAll('input, textarea, button')).map(el => ({
            tag: el.tagName, type: el.type || '', placeholder: el.placeholder || '',
            id: el.id || '', class: el.className.substring(0, 50),
            text: el.textContent.trim().substring(0, 40),
            visible: el.offsetParent !== null
        })).filter(el => el.visible)
    """)
    return inputs


def find_chat_input(page):
    """Find visible chat input."""
    for sel in ['#userInput', '.chat-input__field', 'input[placeholder*="response"]',
                'input[placeholder*="Type"]', 'textarea[placeholder*="Type"]']:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                return el, sel
        except:
            pass
    return None, None


def test_single_page(page, page_info):
    """Test a single page using the already-open browser page."""
    name = page_info["name"]
    url = page_info["url"]
    slug = page_info["slug"]
    result = {
        "name": name,
        "url": url,
        "screenshots": [],
        "blocked": False,
        "block_reason": None,
        "page_loads": False,
        "sandbox_banner": False,
        "begin_awakening_visible": False,
        "chat_input_visible": False,
        "hello_sent": False,
        "ai_responded": False,
        "response_text": None,
        "visual_self_tag": None,
        "bypass_sent": False,
        "bypass_response": None,
        "keen_name": False,
        "discover_button": False,
        "bypass_works": False,
        "pricing_visible": False,
        "tiers_found": [],
        "paypal_detected": False,
        "logo_images": [],
        "errors": [],
        "console_errors": [],
    }

    print(f"\n--- Testing {name} ---")

    # Navigate
    print(f"  Navigating to {url}...")
    page.goto(url, timeout=45000, wait_until="domcontentloaded")
    time.sleep(5)

    # Handle blockers
    ok, status = check_and_handle_blockers(page, slug, "A_")
    if not ok:
        result["blocked"] = True
        result["block_reason"] = status
        p = ss(page, "blocked", slug)
        result["screenshots"].append(p)
        print(f"  BLOCKED: {status}")
        return result

    result["page_loads"] = True
    p = ss(page, "A1_loaded", slug)
    result["screenshots"].append(p)

    # Check sandbox banner
    body_text = page.evaluate("() => document.body.innerText")
    result["sandbox_banner"] = "SANDBOX" in body_text or "No real charges" in body_text
    print(f"  Sandbox banner: {result['sandbox_banner']}")
    print(f"  Page text preview: {body_text[:200]}")

    # Dump all visible interactive elements
    structure = dump_page_structure(page)
    print(f"  Visible elements: {json.dumps(structure[:15], indent=2)}")

    # ================================================================
    # SECTION A: Find the chat interface
    # ================================================================

    # Scroll to look for awakening section
    print("  Scrolling through page to find chat...")
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(1)

    # Try scrolling down gradually to find the chat
    for scroll_pct in [0.2, 0.4, 0.6, 0.8, 1.0]:
        page.evaluate(f"window.scrollTo(0, document.documentElement.scrollHeight * {scroll_pct})")
        time.sleep(1.5)
        # Check if Begin Awakening button appeared
        begin_btn = page.query_selector('.chat-initial__btn')
        if begin_btn and begin_btn.is_visible():
            print(f"  Found Begin Awakening button at {scroll_pct*100}% scroll")
            result["begin_awakening_visible"] = True
            break
        # Check if chat input appeared
        chat_inp, sel = find_chat_input(page)
        if chat_inp:
            print(f"  Chat input found at {scroll_pct*100}% scroll: {sel}")
            result["chat_input_visible"] = True
            break

    p = ss(page, "A2_after_scroll", slug)
    result["screenshots"].append(p)

    # Try clicking "Awaken Your PURE BRAIN" button to navigate to chat section
    if not result["begin_awakening_visible"] and not result["chat_input_visible"]:
        print("  Trying 'Awaken Your PURE BRAIN' button...")
        awaken_btn = page.query_selector('.btn--primary, button:has-text("Awaken")')
        if awaken_btn and awaken_btn.is_visible():
            print("  Clicking Awaken Your PURE BRAIN...")
            awaken_btn.click()
            time.sleep(3)
            p = ss(page, "A2b_after_awaken_click", slug)
            result["screenshots"].append(p)

            begin_btn = page.query_selector('.chat-initial__btn')
            if begin_btn and begin_btn.is_visible():
                result["begin_awakening_visible"] = True
                print("  Begin Awakening now visible")

    # Try scrolling to #awakening anchor
    if not result["begin_awakening_visible"]:
        print("  Scrolling to #awakening via JS...")
        page.evaluate("""
            () => {
                const el = document.getElementById('awakening');
                if (el) { el.scrollIntoView({block:'center'}); return 'found'; }
                return 'not_found';
            }
        """)
        time.sleep(2)
        p = ss(page, "A3_scrolled_to_awakening", slug)
        result["screenshots"].append(p)

        begin_btn = page.query_selector('.chat-initial__btn')
        if begin_btn:
            if begin_btn.is_visible():
                result["begin_awakening_visible"] = True
                print("  Begin Awakening visible after #awakening scroll")
            else:
                # Force visibility check
                is_hidden = page.evaluate("""
                    () => {
                        const btn = document.querySelector('.chat-initial__btn');
                        if (!btn) return 'btn_not_found';
                        const style = window.getComputedStyle(btn);
                        const rect = btn.getBoundingClientRect();
                        return {
                            display: style.display,
                            visibility: style.visibility,
                            opacity: style.opacity,
                            top: rect.top,
                            bottom: rect.bottom,
                            inViewport: rect.top >= 0 && rect.bottom <= window.innerHeight
                        };
                    }
                """)
                print(f"  Begin Awakening button state: {is_hidden}")
                if isinstance(is_hidden, dict) and is_hidden.get("inViewport"):
                    result["begin_awakening_visible"] = True

    # Click Begin Awakening if found
    if result["begin_awakening_visible"]:
        print("  Clicking Begin Awakening...")
        begin_btn = page.query_selector('.chat-initial__btn')
        if begin_btn:
            try:
                begin_btn.scroll_into_view_if_needed()
                time.sleep(0.5)
                begin_btn.click()
                time.sleep(4)
                p = ss(page, "A4_after_begin_click", slug)
                result["screenshots"].append(p)
            except Exception as e:
                print(f"  Click error: {e}")
                # Try JS click
                page.evaluate("document.querySelector('.chat-initial__btn') && document.querySelector('.chat-initial__btn').click()")
                time.sleep(4)
                p = ss(page, "A4b_after_js_click", slug)
                result["screenshots"].append(p)

    # Check for chat input
    chat_input, sel = find_chat_input(page)
    if chat_input and chat_input.is_visible():
        result["chat_input_visible"] = True
        print(f"  Chat input visible: {sel}")

        p = ss(page, "A5_chat_ready", slug)
        result["screenshots"].append(p)

        # ================================================================
        # A: Send "hello"
        # ================================================================
        print("  Sending 'hello'...")
        chat_input.click()
        time.sleep(0.5)
        chat_input.fill("hello")
        time.sleep(0.3)
        p = ss(page, "A6_hello_typed", slug)
        result["screenshots"].append(p)

        page.keyboard.press("Enter")
        result["hello_sent"] = True
        print("  Waiting 15s for AI response...")
        time.sleep(15)

        p = ss(page, "A7_hello_response", slug)
        result["screenshots"].append(p)

        # Get chat text
        chat_text = page.evaluate("""
            () => {
                const chat = document.querySelector('.chat-messages, #chatMessages, .chat-body, [class*="messages"]');
                if (chat) return chat.innerText.substring(0, 500);
                // Try all text in chat area
                const awakening = document.getElementById('awakening');
                return awakening ? awakening.innerText.substring(0, 500) : null;
            }
        """)
        if chat_text and len(chat_text) > 20:
            result["ai_responded"] = True
            result["response_text"] = chat_text
            print(f"  AI response: {chat_text[:200]}")

        # Check VISUAL_SELF
        result["visual_self_tag"] = "VISUAL_SELF" in page.content() and "FOUND" or None
        if not result["visual_self_tag"]:
            result["visual_self_tag"] = None
        print(f"  VISUAL_SELF: {result['visual_self_tag'] or 'not found (good)'}")

        # ================================================================
        # B: Bypass test (same session - just clear and re-type)
        # ================================================================
        # We need a fresh session for bypass. Navigate away and back.
        print("\n  [B] Bypass - navigating fresh to same URL...")
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        time.sleep(4)

        ok2, st2 = check_and_handle_blockers(page, slug, "B_")
        if ok2:
            time.sleep(3)
            # Scroll to chat
            page.evaluate("const el = document.getElementById('awakening'); if(el) el.scrollIntoView({block:'center'})")
            time.sleep(2)

            begin_btn2 = page.query_selector('.chat-initial__btn')
            if begin_btn2 and begin_btn2.is_visible():
                begin_btn2.click()
                time.sleep(4)

            chat_input2, _ = find_chat_input(page)
            if chat_input2 and chat_input2.is_visible():
                print("  Sending bypass code 'pb-full-bypass'...")
                chat_input2.click()
                time.sleep(0.5)
                chat_input2.fill("pb-full-bypass")
                time.sleep(0.3)
                p = ss(page, "B1_bypass_typed", slug)
                result["screenshots"].append(p)

                page.keyboard.press("Enter")
                result["bypass_sent"] = True
                print("  Waiting 15s for bypass response...")
                time.sleep(15)

                p = ss(page, "B2_bypass_response", slug)
                result["screenshots"].append(p)

                bypass_text = page.evaluate("() => document.body.innerText")
                result["bypass_response"] = bypass_text[:600]
                print(f"  Bypass page text: {bypass_text[:300]}")

                result["keen_name"] = "Keen" in bypass_text
                result["discover_button"] = "discover" in bypass_text.lower() or "Discover" in bypass_text
                result["bypass_works"] = result["keen_name"] or result["discover_button"]
                print(f"  Keen: {result['keen_name']}, Discover: {result['discover_button']}")

                # ============================================================
                # C: Pricing
                # ============================================================
                print("\n  [C] Looking for pricing...")

                # Scroll down to find pricing
                for pct in [0.3, 0.5, 0.7, 0.9, 1.0]:
                    page.evaluate(f"window.scrollTo(0, document.documentElement.scrollHeight * {pct})")
                    time.sleep(1)
                    pt = page.evaluate("() => document.body.innerText")
                    if any(t in pt for t in ["Awakened", "Bonded", "Partnered", "$79", "$149"]):
                        print(f"  Pricing found at {pct*100}% scroll")
                        break

                p = ss(page, "C1_pricing_area", slug)
                result["screenshots"].append(p)

                pricing_text = page.evaluate("() => document.body.innerText")
                tiers = []
                for tier, price in [("Awakened", "$79"), ("Bonded", "$149"), ("Partnered", "$499"), ("Unified", "$999"), ("Enterprise", None)]:
                    if tier in pricing_text:
                        tiers.append(tier)
                        print(f"  Tier: {tier} {'at '+price if price and price in pricing_text else '(price not confirmed)'}")
                result["tiers_found"] = tiers
                result["pricing_visible"] = len(tiers) > 0

                # Check logos
                logos = page.evaluate("""
                    () => Array.from(document.querySelectorAll('img')).filter(img =>
                        img.src && (img.src.includes('logo') || img.src.includes('icon') ||
                        img.src.includes('spiral') || img.src.includes('hex') || img.src.includes('brain'))
                    ).map(img => ({
                        file: img.src.split('/').pop().substring(0, 50),
                        w: img.naturalWidth, h: img.naturalHeight
                    }))
                """)
                result["logo_images"] = logos
                print(f"  Logos: {logos}")

                # Try to click a plan button
                all_btns = page.evaluate("""
                    () => Array.from(document.querySelectorAll('button, [class*="plan"] a, [class*="tier"] a')).filter(b => b.offsetParent !== null).map(b => ({
                        text: b.textContent.trim().substring(0, 60), class: b.className.substring(0, 50)
                    })).filter(b => b.text)
                """)
                print(f"  Buttons available: {json.dumps(all_btns[:8], indent=2)}")

                # Try clicking first non-Enterprise plan button
                plan_btn = page.query_selector(
                    'button:has-text("Choose"), button:has-text("Subscribe"), '
                    'button:has-text("Get Started"), button:has-text("Select"), '
                    '[class*="plan-cta"], [class*="tier-btn"]'
                )
                if plan_btn and plan_btn.is_visible():
                    print(f"  Clicking plan button: {plan_btn.text_content()[:50]}")
                    plan_btn.scroll_into_view_if_needed()
                    plan_btn.click()
                    time.sleep(8)
                    p = ss(page, "C2_after_plan_click", slug)
                    result["screenshots"].append(p)

                    paypal = page.evaluate("""
                        () => {
                            for (const f of document.querySelectorAll('iframe'))
                                if (f.src && f.src.includes('paypal')) return 'paypal iframe: '+f.src.substring(0,80);
                            if (document.querySelector('.paypal-button-container, [class*="paypal"]')) return 'paypal class found';
                            if (document.body.innerHTML.includes('paypal.com')) return 'paypal.com in HTML';
                            return null;
                        }
                    """)
                    result["paypal_detected"] = paypal is not None
                    print(f"  PayPal: {paypal or 'not detected'}")
            else:
                print("  Chat input not visible for bypass test")
                p = ss(page, "B_no_chat", slug)
                result["screenshots"].append(p)
        else:
            print(f"  Bypass blocked: {st2}")

    else:
        print("  Chat input NOT found/visible after all attempts")
        # Dump DOM for debugging
        awakening_html = page.evaluate("""
            () => {
                const el = document.getElementById('awakening') || document.querySelector('[id*="awaken"]');
                if (el) return el.outerHTML.substring(0, 1000);
                return 'awakening element not found. Available IDs: ' +
                    Array.from(document.querySelectorAll('[id]')).map(e => e.id).join(', ').substring(0, 200);
            }
        """)
        print(f"  Awakening element: {awakening_html[:400]}")
        result["errors"].append(f"Chat input not found. DOM: {awakening_html[:200]}")

    return result


def test_mobile(page, page_info):
    """Quick mobile viewport test."""
    url = page_info["url"]
    slug = page_info["slug"]
    result = {"mobile_loads": False, "mobile_no_horizontal_scroll": False, "mobile_padding": None, "screenshots": []}

    print(f"\n  [E] Mobile test for {page_info['name']}...")

    page.goto(url, timeout=30000, wait_until="domcontentloaded")
    time.sleep(4)

    ok, st = check_and_handle_blockers(page, slug, "E_")
    if not ok:
        print(f"  Mobile blocked: {st}")
        return result

    result["mobile_loads"] = True
    p = ss(page, "E1_mobile_loaded", slug)
    result["screenshots"].append(p)

    # Check metrics
    m = page.evaluate("""
        () => ({
            viewport: window.innerWidth,
            scrollWidth: document.documentElement.scrollWidth,
            noHScroll: document.documentElement.scrollWidth <= window.innerWidth,
        })
    """)
    result["mobile_no_horizontal_scroll"] = m["noHScroll"]
    print(f"  Viewport: {m['viewport']}px, ScrollWidth: {m['scrollWidth']}px, No h-scroll: {m['noHScroll']}")

    # Get container padding
    padding = page.evaluate("""
        () => {
            for (const sel of ['.container', 'main', '#main', '.page-content']) {
                const el = document.querySelector(sel);
                if (el) {
                    const cs = window.getComputedStyle(el);
                    if (parseFloat(cs.paddingLeft) > 0)
                        return {el: sel, paddingLeft: cs.paddingLeft, paddingRight: cs.paddingRight};
                }
            }
            return null;
        }
    """)
    result["mobile_padding"] = padding
    print(f"  Container padding: {padding}")

    # Scroll to chat section
    page.evaluate("const el = document.getElementById('awakening'); if(el) el.scrollIntoView()")
    time.sleep(2)
    p = ss(page, "E2_mobile_chat_area", slug)
    result["screenshots"].append(p)

    return result


def main():
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    print(f"Pay-Test Final Audit | {TIMESTAMP}")

    all_results = {}

    with sync_playwright() as pw:
        # Single browser, careful session management
        browser = pw.chromium.launch(
            args=[
                "--ignore-certificate-errors",
                "--ignore-ssl-errors",
                "--disable-blink-features=AutomationControlled",
            ],
            headless=True,
        )

        # Desktop tests
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        )
        console_errors_store = {}
        page = ctx.new_page()

        for page_info in PAGES:
            console_errors = []
            page.on("console", lambda m, ce=console_errors: ce.append(f"[{m.type}] {m.text[:120]}") if m.type in ("error", "warning") else None)
            page.on("pageerror", lambda e, ce=console_errors: ce.append(f"[pageerror] {str(e)[:150]}"))

            print(f"\n{'='*60}")
            print(f"DESKTOP TEST: {page_info['name']}")
            print(f"{'='*60}")

            try:
                r = test_single_page(page, page_info)
                r["console_errors"] = console_errors[:20]
                all_results[page_info["name"]] = r
            except Exception as e:
                all_results[page_info["name"]] = {"name": page_info["name"], "fatal": str(e)}
                import traceback; traceback.print_exc()

            # Big delay between pages to avoid WAF
            print(f"\nWaiting 15s before next page...")
            time.sleep(15)

        ctx.close()

        # Mobile tests - separate context
        print(f"\n{'='*60}")
        print("MOBILE TESTS")
        print(f"{'='*60}")

        mobile_ctx = browser.new_context(
            viewport={"width": 375, "height": 812},
            ignore_https_errors=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        )
        mobile_page = mobile_ctx.new_page()

        for page_info in PAGES:
            time.sleep(8)  # Delay between mobile tests
            try:
                mobile_r = test_mobile(mobile_page, page_info)
                if page_info["name"] in all_results:
                    all_results[page_info["name"]].update(mobile_r)
                    all_results[page_info["name"]]["screenshots"] = (
                        all_results[page_info["name"]].get("screenshots", []) +
                        mobile_r.get("screenshots", [])
                    )
                else:
                    all_results[page_info["name"]] = mobile_r
            except Exception as e:
                print(f"  Mobile test error for {page_info['name']}: {e}")

        mobile_ctx.close()
        browser.close()

    # Save results
    results_path = f"{SCREENSHOTS_DIR}/{TIMESTAMP}_final_results.json"
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2)

    # Print summary
    print(f"\n{'='*60}\nFINAL SUMMARY\n{'='*60}")
    for name, r in all_results.items():
        if "fatal" in r:
            print(f"\n{name}: FATAL - {r['fatal']}")
            continue
        ok = lambda x: "YES" if x else "NO"
        print(f"\n{name}:")
        print(f"  Page loads:           {ok(r.get('page_loads'))}")
        if r.get("blocked"):
            print(f"  BLOCKED:              {r.get('block_reason')}")
        print(f"  Sandbox banner:       {ok(r.get('sandbox_banner'))}")
        print(f"  Begin Awakening btn:  {ok(r.get('begin_awakening_visible'))}")
        print(f"  Chat input visible:   {ok(r.get('chat_input_visible'))}")
        print(f"  Hello sent:           {ok(r.get('hello_sent'))}")
        print(f"  AI responded:         {ok(r.get('ai_responded'))}")
        if r.get("response_text"):
            print(f"  Response:             {str(r['response_text'])[:120]}")
        print(f"  VISUAL_SELF tag:      {r.get('visual_self_tag') or 'NOT FOUND (good)'}")
        print(f"  Bypass sent:          {ok(r.get('bypass_sent'))}")
        print(f"  Keen name:            {ok(r.get('keen_name'))}")
        print(f"  Discover button:      {ok(r.get('discover_button'))}")
        print(f"  Bypass works:         {ok(r.get('bypass_works'))}")
        print(f"  Pricing visible:      {ok(r.get('pricing_visible'))}")
        print(f"  Tiers found:          {r.get('tiers_found', [])}")
        print(f"  PayPal detected:      {ok(r.get('paypal_detected'))}")
        print(f"  Mobile loads:         {ok(r.get('mobile_loads'))}")
        print(f"  Mobile no h-scroll:   {ok(r.get('mobile_no_horizontal_scroll'))}")
        print(f"  Mobile padding:       {r.get('mobile_padding')}")
        ss_count = len(r.get("screenshots", []))
        print(f"  Screenshots:          {ss_count}")
        for e in r.get("console_errors", [])[:3]:
            print(f"  Console: {e[:120]}")
        if r.get("errors"):
            for er in r["errors"][:3]:
                print(f"  Test error: {er[:120]}")

    print(f"\nResults: {results_path}")
    print(f"Screenshots prefix: {TIMESTAMP}_")
    return all_results


if __name__ == "__main__":
    main()
