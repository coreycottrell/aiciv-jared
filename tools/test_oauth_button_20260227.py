"""
OAuth Button Visual Test - 2026-02-27
Tests pay-test-sandbox-2 vs pay-test-2 for OAuth/birth button behavior.

Memory context loaded:
- sandbox-2: has runBirthInit + Witness v4 code + #pb-sandbox-bypass-btn
- pay-test-2: may have different/older version of post-payment chat
- Password: PureBrain.ai253443$$$
- Bypass code: pb-full-bypass
- WAF risk: keep requests minimal
"""

import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

# Directories
SCREENSHOTS_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/oauth-test-20260227")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

PASSWORD = "PureBrain.ai253443$$$"
BYPASS_CODE = "pb-full-bypass"

PAGES = [
    {
        "name": "pay-test-sandbox-2",
        "url": "https://purebrain.ai/pay-test-sandbox-2/",
        "slug": "sandbox2",
    },
    {
        "name": "pay-test-2",
        "url": "https://purebrain.ai/pay-test-2/",
        "slug": "paytest2",
    },
]

results = {}


async def screenshot(page, name, slug):
    path = str(SCREENSHOTS_DIR / f"{slug}-{name}.png")
    await page.screenshot(path=path, full_page=True)
    print(f"  [SCREENSHOT] {path}")
    return path


async def test_page(browser, page_cfg):
    slug = page_cfg["slug"]
    url = page_cfg["url"]
    name = page_cfg["name"]

    print(f"\n{'='*60}")
    print(f"TESTING: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    context = await browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    )

    page = await context.new_page()

    # Capture console events
    console_errors = []
    console_warnings = []
    console_logs = []
    birth_logs = []

    def on_console(msg):
        text = msg.text
        if msg.type == "error":
            console_errors.append(text)
            print(f"  [CONSOLE ERROR] {text[:200]}")
        elif msg.type == "warning":
            console_warnings.append(text)
        else:
            console_logs.append(text)
            # Capture anything birth/oauth related
            if any(k in text.lower() for k in ["birth", "oauth", "witness", "runbirth", "portal"]):
                birth_logs.append(f"{msg.type}: {text}")
                print(f"  [BIRTH LOG] {msg.type}: {text[:200]}")

    page.on("console", on_console)

    # Track network requests related to Witness/birth
    network_birth = []

    def on_request(req):
        if any(k in req.url for k in ["birth", "oauth", "witness", "104.248"]):
            print(f"  [NETWORK REQUEST] {req.method} {req.url}")
            network_birth.append({"method": req.method, "url": req.url})

    def on_response(resp):
        if any(k in resp.url for k in ["birth", "oauth", "witness", "104.248"]):
            print(f"  [NETWORK RESPONSE] {resp.status} {resp.url}")

    page.on("request", on_request)
    page.on("response", on_response)

    page_result = {
        "name": name,
        "url": url,
        "screenshots": [],
        "console_errors": [],
        "console_warnings": [],
        "birth_logs": [],
        "network_birth": [],
        "oauth_elements": [],
        "birth_functions_available": {},
        "script_analysis": {},
        "post_payment_visible": False,
        "sandbox_bypass_exists": False,
    }

    # ---- STEP 1: Navigate ----
    print(f"\n[STEP 1] Navigating to {url}")
    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
    except Exception as e:
        print(f"  [WARN] networkidle timeout: {e}")
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)

    await asyncio.sleep(2)
    ss = await screenshot(page, "01-initial", slug)
    page_result["screenshots"].append(ss)

    # ---- STEP 2: Check if password protected ----
    pw_field = await page.query_selector("input[id^='pwbox-']")
    if pw_field:
        print("[STEP 2] Page is password protected - entering password")
        await pw_field.fill(PASSWORD)
        submit = await page.query_selector("input[name='Submit']")
        if submit:
            await submit.click()
        else:
            form = await page.query_selector("form#pwbox-form, form[method='post']")
            if form:
                await form.evaluate("f => f.submit()")
        await page.wait_for_load_state("networkidle", timeout=15000)
        await asyncio.sleep(3)
        ss = await screenshot(page, "02-after-password", slug)
        page_result["screenshots"].append(ss)
    else:
        print("[STEP 2] Page is NOT password protected")

    # ---- STEP 3: Analyze page scripts for OAuth/birth functions ----
    print("\n[STEP 3] Analyzing page scripts for birth/OAuth functions")

    # Check which functions exist in window scope
    func_check = await page.evaluate("""
        () => {
            return {
                runBirthInit: typeof window.runBirthInit,
                runPortalButtonWatcher: typeof window.runPortalButtonWatcher,
                startConversation: typeof window.startConversation,
                pbFullBypass: typeof window.pbFullBypass,
                initPTC: typeof window.initPTC,
                WITNESS_WEBHOOK_HOST: typeof window.WITNESS_WEBHOOK_HOST !== 'undefined' ? window.WITNESS_WEBHOOK_HOST : 'NOT SET',
                _pbContainerName: typeof window._pbContainerName !== 'undefined' ? window._pbContainerName : 'NOT SET',
            }
        }
    """)
    page_result["birth_functions_available"] = func_check
    print(f"  Functions: {json.dumps(func_check, indent=2)}")

    # Check for sandbox bypass
    sandbox_bypass = await page.query_selector("#pb-sandbox-bypass-btn")
    page_result["sandbox_bypass_exists"] = sandbox_bypass is not None
    print(f"  Sandbox bypass button (#pb-sandbox-bypass-btn): {'EXISTS' if sandbox_bypass else 'NOT FOUND'}")

    # Scan page HTML for script keywords
    script_content = await page.evaluate("""
        () => {
            const scripts = document.querySelectorAll('script');
            let birthScripts = 0;
            let oauthScripts = 0;
            let witnessScripts = 0;
            let totalInlineLength = 0;

            for (const s of scripts) {
                const txt = s.textContent || '';
                totalInlineLength += txt.length;
                if (txt.includes('runBirthInit')) birthScripts++;
                if (txt.includes('oauth') || txt.includes('OAuth')) oauthScripts++;
                if (txt.includes('WITNESS') || txt.includes('witness')) witnessScripts++;
            }

            return {
                total_scripts: scripts.length,
                scripts_with_runBirthInit: birthScripts,
                scripts_with_oauth: oauthScripts,
                scripts_with_witness: witnessScripts,
                total_inline_length: totalInlineLength,
            };
        }
    """)
    page_result["script_analysis"] = script_content
    print(f"  Script analysis: {json.dumps(script_content, indent=2)}")

    # ---- STEP 4: Check for OAuth/birth DOM elements right now ----
    print("\n[STEP 4] Scanning current DOM for OAuth/birth elements")

    oauth_dom = await page.evaluate("""
        () => {
            const results = [];

            // Search by various patterns
            const selectors = [
                '[class*="oauth"]',
                '[id*="oauth"]',
                '[class*="birth"]',
                '[id*="birth"]',
                'button[onclick*="birth"]',
                'button[onclick*="oauth"]',
                '[id*="pb-sandbox"]',
                '[class*="ptc-"]',
                '#pay-test-post-payment',
                '.ptc-wrapper',
                '.ptc-messages',
            ];

            for (const sel of selectors) {
                try {
                    const els = document.querySelectorAll(sel);
                    if (els.length > 0) {
                        for (const el of els) {
                            results.push({
                                selector: sel,
                                tagName: el.tagName,
                                id: el.id,
                                className: el.className.substring(0, 100),
                                text: (el.textContent || '').trim().substring(0, 100),
                                visible: el.offsetParent !== null || el.style.display !== 'none',
                                display: window.getComputedStyle(el).display,
                            });
                        }
                    }
                } catch(e) {}
            }
            return results;
        }
    """)
    page_result["oauth_elements"] = oauth_dom
    if oauth_dom:
        print(f"  Found {len(oauth_dom)} matching elements:")
        for el in oauth_dom:
            print(f"    - [{el['tagName']}#{el['id']}.{el['className'][:40]}] text='{el['text'][:60]}' display={el['display']}")
    else:
        print("  No OAuth/birth DOM elements found at initial load")

    # ---- STEP 5: Check if post-payment chat is visible ----
    ptc = await page.query_selector("#pay-test-post-payment, .ptc-wrapper")
    if ptc:
        display = await ptc.evaluate("el => window.getComputedStyle(el).display")
        page_result["post_payment_visible"] = display != "none"
        print(f"\n[STEP 5] Post-payment chat element found, display={display}")
    else:
        print("\n[STEP 5] No post-payment chat element (#pay-test-post-payment) found")

    # ---- STEP 6: Try to navigate through pre-payment flow ----
    print("\n[STEP 6] Attempting pre-payment flow navigation")

    begin_btn = await page.query_selector(".chat-initial__btn")
    if begin_btn:
        print("  Found '.chat-initial__btn' - clicking Begin Awakening")
        await begin_btn.click()
        await asyncio.sleep(3)
        ss = await screenshot(page, "03-after-begin", slug)
        page_result["screenshots"].append(ss)

        # Type bypass code
        user_input = await page.query_selector("#userInput")
        if user_input:
            print(f"  Typing bypass code: {BYPASS_CODE}")
            await user_input.fill(BYPASS_CODE)
            submit_btn = await page.query_selector("#submitBtn")
            if submit_btn:
                await submit_btn.click()
            else:
                await page.keyboard.press("Enter")
            await asyncio.sleep(5)
            ss = await screenshot(page, "04-after-bypass", slug)
            page_result["screenshots"].append(ss)

            # Look for pricing/discover button
            discover_btn = await page.query_selector("#seeWhatBtn, .chat-discover-btn")
            pro_cta = await page.query_selector("#proCta")

            if discover_btn:
                print("  Found discover button - clicking")
                await discover_btn.click()
                await asyncio.sleep(3)
                ss = await screenshot(page, "05-after-discover", slug)
                page_result["screenshots"].append(ss)

            if pro_cta:
                print("  Found #proCta (Activate Now) - clicking")
                await pro_cta.click()
                await asyncio.sleep(3)
                ss = await screenshot(page, "06-after-procta", slug)
                page_result["screenshots"].append(ss)

                # Look for sandbox bypass button
                sandbox_btn = await page.query_selector("#pb-sandbox-bypass-btn")
                if sandbox_btn:
                    print("  Found sandbox bypass button - clicking to simulate payment")
                    await sandbox_btn.click()
                    await asyncio.sleep(5)
                    ss = await screenshot(page, "07-after-sandbox-bypass", slug)
                    page_result["screenshots"].append(ss)

                    # Now check for post-payment chat
                    ptc_check = await page.query_selector(".ptc-wrapper, #pay-test-post-payment")
                    if ptc_check:
                        disp = await ptc_check.evaluate("el => window.getComputedStyle(el).display")
                        print(f"  Post-payment chat after sandbox bypass: display={disp}")
                        page_result["post_payment_visible"] = disp != "none"

                        # Wait for questionnaire to start
                        await asyncio.sleep(3)
                        ss = await screenshot(page, "08-ptc-initial", slug)
                        page_result["screenshots"].append(ss)

                        # Walk through questionnaire quickly to reach birth init
                        await walk_questionnaire(page, page_cfg, page_result)
                    else:
                        print("  Post-payment chat NOT found after sandbox bypass")
                else:
                    print("  No sandbox bypass button - this is pay-test-2 (production page)")
                    # On pay-test-2, check what happens after clicking Activate Now
                    await asyncio.sleep(5)
                    ss = await screenshot(page, "07-paypal-or-other", slug)
                    page_result["screenshots"].append(ss)

                    # Check current DOM state
                    current_dom = await page.evaluate("""
                        () => {
                            return {
                                ptc_exists: !!document.querySelector('#pay-test-post-payment, .ptc-wrapper'),
                                paypal_visible: !!document.querySelector('.paypal-buttons-container, #paypal-button-container'),
                                overlay_visible: !!document.querySelector('.pay-overlay, .payment-overlay'),
                                visible_buttons: Array.from(document.querySelectorAll('button:not([style*="display: none"])')).map(b => b.textContent.trim().substring(0, 50)).slice(0, 10),
                            }
                        }
                    """)
                    print(f"  DOM after Activate Now: {json.dumps(current_dom, indent=2)}")
                    page_result["current_dom_after_activate"] = current_dom
    else:
        print("  No '.chat-initial__btn' found - page may have different structure")
        ss = await screenshot(page, "03-no-begin-btn", slug)
        page_result["screenshots"].append(ss)

    # ---- Final: Save all console data ----
    page_result["console_errors"] = console_errors
    page_result["console_warnings"] = console_warnings[:20]
    page_result["birth_logs"] = birth_logs
    page_result["network_birth"] = network_birth

    print(f"\n[SUMMARY for {name}]")
    print(f"  Console errors: {len(console_errors)}")
    print(f"  Console warnings: {len(console_warnings)}")
    print(f"  Birth-related logs: {len(birth_logs)}")
    print(f"  Birth-related network: {len(network_birth)}")
    print(f"  Post-payment visible: {page_result['post_payment_visible']}")
    print(f"  runBirthInit: {func_check.get('runBirthInit', 'N/A')}")
    print(f"  WITNESS_WEBHOOK_HOST: {func_check.get('WITNESS_WEBHOOK_HOST', 'N/A')}")

    await context.close()
    return page_result


async def walk_questionnaire(page, page_cfg, page_result):
    """Walk through questionnaire to reach OAuth/birth init phase."""
    slug = page_cfg["slug"]
    name = page_cfg["name"]

    print(f"\n  [QUESTIONNAIRE] Walking through to reach birth init on {name}")

    # Name
    await answer_ptc(page, "TestUser")
    await asyncio.sleep(3)

    # Email
    await answer_ptc(page, "test@test.com")
    await asyncio.sleep(3)

    # Company
    await answer_ptc(page, "TestCo")
    await asyncio.sleep(3)

    # Role
    await answer_ptc(page, "CEO")
    await asyncio.sleep(4)

    ss = await screenshot(page, "09-after-role", slug)
    page_result["screenshots"].append(ss)

    # Check if there's an "I have my key" button (v4.3 removed this)
    key_btn = await page.query_selector(".ptc-btn")
    if key_btn:
        text = await key_btn.text_content()
        print(f"  [QUESTIONNAIRE] Found ptc-btn: '{text}'")
        if "key" in text.lower() or "have" in text.lower():
            print("  [QUESTIONNAIRE] Claude API key step present - clicking")
            await key_btn.click()
            await asyncio.sleep(2)
            # Enter fake key
            textarea = await page.query_selector("textarea[placeholder*='sk-ant']")
            if textarea:
                await textarea.fill("sk-ant-api03-testkey12345")
                send_btn = await page.query_selector("button.ptc-send-btn")
                if send_btn:
                    await send_btn.click()
                await asyncio.sleep(3)

    ss = await screenshot(page, "10-post-role", slug)
    page_result["screenshots"].append(ss)

    # Look for birth init - "Your AI is ready to be born" / "Start AI Birth"
    await asyncio.sleep(5)

    birth_elements = await page.evaluate("""
        () => {
            const results = [];
            // Look for birth-related text anywhere in ptc messages
            const msgs = document.querySelectorAll('.ptc-msg--ai, .ptc-msg');
            for (const msg of msgs) {
                const text = msg.textContent || '';
                if (text.includes('birth') || text.includes('Birth') || text.includes('ready to be born') || text.includes('OAuth') || text.includes('oauth')) {
                    results.push({type: 'message', text: text.trim().substring(0, 200)});
                }
            }

            // Look for buttons with birth/oauth text
            const btns = document.querySelectorAll('button, .ptc-btn, a.ptc-btn');
            for (const btn of btns) {
                const text = btn.textContent || '';
                if (text.includes('birth') || text.includes('Birth') || text.includes('Start') || text.includes('OAuth') || text.includes('oauth') || text.includes('Continue')) {
                    results.push({
                        type: 'button',
                        text: text.trim().substring(0, 100),
                        id: btn.id,
                        class: btn.className.substring(0, 80),
                        display: window.getComputedStyle(btn).display,
                    });
                }
            }

            // Check for OAuth link
            const links = document.querySelectorAll('a[href*="oauth"], a[href*="claude.ai"]');
            for (const link of links) {
                results.push({type: 'oauth-link', href: link.href, text: link.textContent.trim()});
            }

            return results;
        }
    """)

    print(f"  [QUESTIONNAIRE] Birth/OAuth elements found: {len(birth_elements)}")
    for el in birth_elements:
        print(f"    - {el}")
    page_result["birth_elements_in_ptc"] = birth_elements

    ss = await screenshot(page, "11-birth-check", slug)
    page_result["screenshots"].append(ss)

    # Also check window state
    window_state = await page.evaluate("""
        () => {
            return {
                runBirthInit: typeof window.runBirthInit,
                _pbBirthOauthUrl: typeof window._pbBirthOauthUrl !== 'undefined' ? window._pbBirthOauthUrl : 'NOT SET',
                _pbContainerName: typeof window._pbContainerName !== 'undefined' ? window._pbContainerName : 'NOT SET',
                _pbBirthAuthenticated: typeof window._pbBirthAuthenticated !== 'undefined' ? window._pbBirthAuthenticated : 'NOT SET',
            }
        }
    """)
    print(f"  [QUESTIONNAIRE] Window state: {json.dumps(window_state, indent=2)}")
    page_result["window_state_at_birth"] = window_state


async def answer_ptc(page, text):
    """Type an answer in the post-payment chat and submit."""
    textarea = await page.query_selector("textarea[placeholder*='Message'], textarea[placeholder*='message']")
    if textarea:
        await textarea.fill(text)
        send_btn = await page.query_selector("button.ptc-send-btn")
        if send_btn:
            await send_btn.click()
        else:
            await page.keyboard.press("Enter")
        await asyncio.sleep(3)
        print(f"    Answered: '{text}'")
    else:
        # Try ptc-btn choices
        choice_btn = await page.query_selector(".ptc-btn:not([disabled])")
        if choice_btn:
            btn_text = await choice_btn.text_content()
            await choice_btn.click()
            await asyncio.sleep(2)
            print(f"    Clicked choice: '{btn_text}'")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"],
        )

        all_results = {}

        for page_cfg in PAGES:
            print(f"\n{'#'*70}")
            print(f"# STARTING TEST: {page_cfg['name']}")
            print(f"{'#'*70}")

            try:
                result = await test_page(browser, page_cfg)
                all_results[page_cfg["slug"]] = result
            except Exception as e:
                print(f"ERROR testing {page_cfg['name']}: {e}")
                import traceback
                traceback.print_exc()
                all_results[page_cfg["slug"]] = {"error": str(e)}

            # Wait between pages to avoid WAF
            print(f"\nWaiting 20 seconds before next page (WAF protection)...")
            await asyncio.sleep(20)

        await browser.close()

        # Save results
        results_path = "/home/jared/projects/AI-CIV/aether/exports/oauth-test-results-20260227.json"
        with open(results_path, "w") as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"\nResults saved to: {results_path}")

        return all_results


if __name__ == "__main__":
    asyncio.run(main())
