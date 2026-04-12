"""
OAuth Button Test v2 - 2026-02-27
Smarter flow: inspect DOM at each step to find what's actually there.
Uses force_click/evaluate for elements not directly visible.
"""

import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

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


async def ss(page, label, slug):
    path = str(SCREENSHOTS_DIR / f"{slug}-{label}.png")
    await page.screenshot(path=path, full_page=True, timeout=15000)
    print(f"  [SS] {path}")
    return path


async def dump_dom_state(page, label):
    """Dump visible/relevant DOM state for debugging."""
    state = await page.evaluate("""
        () => {
            const info = {};

            // Chat-related elements
            info.chatInitBtn = !!document.querySelector('.chat-initial__btn');
            info.userInput = !!document.querySelector('#userInput');
            info.submitBtn = !!document.querySelector('#submitBtn');
            info.seeWhatBtn = !!document.querySelector('#seeWhatBtn');
            info.proCta = !!document.querySelector('#proCta');
            info.sandboxBypassBtn = !!document.querySelector('#pb-sandbox-bypass-btn');
            info.ptcWrapper = !!document.querySelector('.ptc-wrapper, #pay-test-post-payment');

            // Pricing section
            const pricing = document.querySelector('.pricing-section');
            info.pricingDisplay = pricing ? window.getComputedStyle(pricing).display : 'N/A';

            // What buttons exist right now?
            const allBtns = Array.from(document.querySelectorAll('button')).map(b => ({
                text: b.textContent.trim().substring(0, 60),
                id: b.id,
                class: b.className.substring(0, 60),
                display: window.getComputedStyle(b).display,
                visible: b.offsetWidth > 0 && b.offsetHeight > 0,
            })).filter(b => b.display !== 'none' || b.visible);
            info.visibleButtons = allBtns.slice(0, 15);

            // Console of #chatMessages
            const chatMsgs = document.querySelector('#chatMessages');
            info.chatMessagesExists = !!chatMsgs;
            info.chatMessageCount = chatMsgs ? chatMsgs.children.length : 0;

            // PTC messages
            const ptcMsgs = document.querySelector('.ptc-messages');
            info.ptcMessagesExists = !!ptcMsgs;
            info.ptcMessageCount = ptcMsgs ? ptcMsgs.children.length : 0;

            // AI typing indicator
            info.typingIndicator = !!document.querySelector('#typingIndicator');

            return info;
        }
    """)
    print(f"  [DOM at {label}]: {json.dumps(state, indent=4)}")
    return state


async def test_page(browser, cfg):
    slug = cfg["slug"]
    url = cfg["url"]
    name = cfg["name"]
    screenshots = []
    console_errors = []
    birth_logs = []
    network_birth = []

    print(f"\n{'='*60}\nTESTING: {name}\n{'='*60}")

    context = await browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    )
    page = await context.new_page()

    def on_console(msg):
        text = msg.text
        if msg.type == "error":
            console_errors.append(text)
        if any(k in text.lower() for k in ["birth", "oauth", "witness", "runbirth", "portal", "container"]):
            birth_logs.append(f"{msg.type}: {text}")
            print(f"  [BIRTH LOG] {text[:300]}")

    def on_request(req):
        if any(k in req.url for k in ["birth", "oauth", "104.248", "witness"]):
            network_birth.append({"method": req.method, "url": req.url})
            print(f"  [NET REQ] {req.method} {req.url}")

    def on_response(resp):
        if any(k in resp.url for k in ["birth", "oauth", "104.248", "witness"]):
            print(f"  [NET RESP] {resp.status} {resp.url}")

    page.on("console", on_console)
    page.on("request", on_request)
    page.on("response", on_response)

    result = {
        "name": name, "url": url, "screenshots": [],
        "console_errors": [], "birth_logs": [], "network_birth": [],
        "step_results": {}, "final_assessment": {}
    }

    # NAVIGATE
    print(f"[NAV] {url}")
    try:
        await page.goto(url, wait_until="networkidle", timeout=25000)
    except:
        await page.goto(url, wait_until="domcontentloaded", timeout=25000)
    await asyncio.sleep(2)

    p = await ss(page, "01-initial", slug)
    result["screenshots"].append(p)

    # PASSWORD
    pw = await page.query_selector("input[id^='pwbox-']")
    if pw:
        print("[PW] Entering password")
        await pw.fill(PASSWORD)
        await pw.press("Enter")
        await page.wait_for_load_state("domcontentloaded", timeout=10000)
        await asyncio.sleep(3)
        p = await ss(page, "02-unlocked", slug)
        result["screenshots"].append(p)

    # Dump DOM state after unlock
    await dump_dom_state(page, "after-unlock")

    # Check functions available
    funcs = await page.evaluate("""
        () => ({
            runBirthInit: typeof window.runBirthInit,
            runPortalButtonWatcher: typeof window.runPortalButtonWatcher,
            startConversation: typeof window.startConversation,
            WITNESS_WEBHOOK_HOST: window.WITNESS_WEBHOOK_HOST || 'NOT SET',
            _pbContainerName: window._pbContainerName || 'NOT SET',
        })
    """)
    result["step_results"]["functions_at_load"] = funcs
    print(f"  [FUNCTIONS] {json.dumps(funcs, indent=2)}")

    # Script scan
    scripts = await page.evaluate("""
        () => {
            const ss = document.querySelectorAll('script');
            let total = 0, withBirth = 0, withOauth = 0;
            let largestScript = 0;
            for (const s of ss) {
                const t = s.textContent || '';
                total += t.length;
                if (t.includes('runBirthInit')) withBirth++;
                if (t.includes('oauth') || t.includes('OAuth') || t.includes('oauthUrl')) withOauth++;
                if (t.length > largestScript) largestScript = t.length;
            }
            return { script_count: ss.length, total_chars: total, with_runBirthInit: withBirth, with_oauth: withOauth, largest_script: largestScript };
        }
    """)
    result["step_results"]["script_scan"] = scripts
    print(f"  [SCRIPTS] {json.dumps(scripts, indent=2)}")

    # BEGIN AWAKENING
    begin = await page.query_selector(".chat-initial__btn")
    if not begin:
        print("[ERROR] No .chat-initial__btn found - page structure different?")
        p = await ss(page, "03-no-begin-btn", slug)
        result["screenshots"].append(p)
        result["final_assessment"]["error"] = "No begin button found"
        await context.close()
        return result

    print("[CLICK] .chat-initial__btn")
    await begin.click()
    await asyncio.sleep(2)

    # Wait for chat to appear
    await page.wait_for_selector("#userInput", timeout=10000)
    await asyncio.sleep(1)
    p = await ss(page, "03-chat-open", slug)
    result["screenshots"].append(p)
    await dump_dom_state(page, "chat-open")

    # TYPE BYPASS
    user_input = await page.query_selector("#userInput")
    if user_input:
        print(f"[TYPE] Bypass code: {BYPASS_CODE}")
        await user_input.fill(BYPASS_CODE)
        await asyncio.sleep(0.5)

        submit = await page.query_selector("#submitBtn")
        if submit:
            await submit.click()
        else:
            await user_input.press("Enter")

        # Wait for AI response
        await asyncio.sleep(6)
        p = await ss(page, "04-after-bypass", slug)
        result["screenshots"].append(p)
        await dump_dom_state(page, "after-bypass")

    # Look for seeWhatBtn OR proCta
    # May need to scroll to find them
    await page.evaluate("window.scrollTo(0, 500)")
    await asyncio.sleep(1)

    see_what = await page.query_selector("#seeWhatBtn")
    pro_cta = await page.query_selector("#proCta")

    print(f"  #seeWhatBtn: {see_what is not None}")
    print(f"  #proCta: {pro_cta is not None}")

    # Check if they're visible
    if see_what:
        see_display = await see_what.evaluate("el => window.getComputedStyle(el).display")
        print(f"  #seeWhatBtn display: {see_display}")
        if see_display != "none":
            print("[CLICK] #seeWhatBtn")
            await see_what.click()
            await asyncio.sleep(3)
            p = await ss(page, "05-after-seewhat", slug)
            result["screenshots"].append(p)
            await dump_dom_state(page, "after-seewhat")

    # Recheck proCta
    pro_cta = await page.query_selector("#proCta")
    if pro_cta:
        pro_display = await pro_cta.evaluate("el => window.getComputedStyle(el).display")
        print(f"  #proCta display: {pro_display}")

        if pro_display != "none":
            print("[CLICK] #proCta (Activate Now) via JS to avoid visibility check")
            await page.evaluate("document.querySelector('#proCta').click()")
            await asyncio.sleep(3)
            p = await ss(page, "06-after-procta", slug)
            result["screenshots"].append(p)
            await dump_dom_state(page, "after-procta")
        else:
            # Force click via JS
            print("[CLICK] Force-clicking #proCta via JS (not visible)")
            await page.evaluate("document.querySelector('#proCta').click()")
            await asyncio.sleep(3)
            p = await ss(page, "06-procta-forced", slug)
            result["screenshots"].append(p)

    # Check for sandbox bypass button (only appears on sandbox URLs)
    sandbox_btn = await page.query_selector("#pb-sandbox-bypass-btn")
    result["step_results"]["sandbox_bypass_found"] = sandbox_btn is not None
    print(f"  [SANDBOX BYPASS] #pb-sandbox-bypass-btn: {sandbox_btn is not None}")

    if sandbox_btn:
        print("[CLICK] Sandbox bypass button -> simulating payment")
        await page.evaluate("document.querySelector('#pb-sandbox-bypass-btn').click()")
        await asyncio.sleep(5)

        p = await ss(page, "07-after-payment-sim", slug)
        result["screenshots"].append(p)
        await dump_dom_state(page, "after-payment-sim")

        # Post-payment chat should now be visible
        ptc = await page.query_selector(".ptc-wrapper, #pay-test-post-payment")
        if ptc:
            ptc_display = await ptc.evaluate("el => window.getComputedStyle(el).display")
            print(f"  [PTC] Post-payment chat display: {ptc_display}")
            result["step_results"]["ptc_display_after_payment"] = ptc_display

            if ptc_display != "none":
                # Walk questionnaire to reach birth init
                await asyncio.sleep(3)
                p = await ss(page, "08-ptc-started", slug)
                result["screenshots"].append(p)

                await walk_to_birth(page, slug, result)
    else:
        # On pay-test-2 - check what appears after proCta
        print("[INFO] No sandbox bypass - checking what's available after Activate Now")
        await asyncio.sleep(3)

        # Check if post-payment chat appeared anyway (via Jared's real payment test?)
        ptc = await page.query_selector(".ptc-wrapper, #pay-test-post-payment")
        if ptc:
            ptc_display = await ptc.evaluate("el => window.getComputedStyle(el).display")
            print(f"  [PTC] Post-payment chat display: {ptc_display}")
            result["step_results"]["ptc_display"] = ptc_display
        else:
            print("  [PTC] No post-payment chat element found")

        # Check all elements on page that mention birth/oauth
        birth_dom = await page.evaluate("""
            () => {
                const results = [];
                // All text nodes containing birth/oauth
                const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                let node;
                while (node = walker.nextNode()) {
                    if (/birth|oauth|OAuth|runBirth/i.test(node.textContent)) {
                        results.push({type: 'text', value: node.textContent.trim().substring(0, 100), parent: node.parentElement?.tagName});
                    }
                }
                return results.slice(0, 20);
            }
        """)
        result["step_results"]["birth_text_nodes"] = birth_dom
        print(f"  [BIRTH TEXT NODES] {len(birth_dom)} found: {birth_dom[:5]}")

        p = await ss(page, "07-paytest2-state", slug)
        result["screenshots"].append(p)
        await dump_dom_state(page, "paytest2-final")

    result["console_errors"] = console_errors
    result["birth_logs"] = birth_logs
    result["network_birth"] = network_birth

    print(f"\n[FINAL SUMMARY: {name}]")
    print(f"  Console errors: {len(console_errors)}")
    print(f"  Birth-related logs: {len(birth_logs)}")
    print(f"  Birth-related network calls: {len(network_birth)}")
    print(f"  runBirthInit available: {funcs.get('runBirthInit')}")
    print(f"  Sandbox bypass found: {result['step_results'].get('sandbox_bypass_found')}")

    await context.close()
    return result


async def walk_to_birth(page, slug, result):
    """Walk through PTC questionnaire to reach birth init phase."""
    print(f"\n  [QUESTIONNAIRE] Walking through to birth init...")

    answers = ["TestUser", "test@test.com", "TestCo", "CEO"]
    labels = ["name", "email", "company", "role"]

    for answer, label in zip(answers, labels):
        # Try textarea first
        textarea = await page.query_selector("textarea[placeholder*='Message'], textarea[placeholder*='message']")
        if textarea:
            await textarea.fill(answer)
            send = await page.query_selector("button.ptc-send-btn")
            if send:
                await send.click()
            else:
                await textarea.press("Enter")
            await asyncio.sleep(3)
            print(f"    Answered {label}: '{answer}'")
        else:
            # Check for choice buttons
            btn = await page.query_selector(".ptc-btn:not([disabled])")
            if btn:
                btn_text = await btn.text_content()
                await btn.click()
                await asyncio.sleep(2)
                print(f"    Clicked button: '{btn_text}' (for {label})")

    # At this point we should be at Claude auth or birth init
    await asyncio.sleep(5)
    p_path = str(SCREENSHOTS_DIR / f"{slug}-09-questionnaire-done.png")
    await page.screenshot(path=p_path, full_page=True, timeout=15000)
    result["screenshots"].append(p_path)
    print(f"  [SS] {p_path}")

    # Check what's visible now
    ptc_state = await page.evaluate("""
        () => {
            const msgs = Array.from(document.querySelectorAll('.ptc-msg--ai')).map(m => m.textContent.trim().substring(0, 150));
            const btns = Array.from(document.querySelectorAll('.ptc-btn, .ptc-btn--primary')).map(b => ({
                text: b.textContent.trim().substring(0, 80),
                id: b.id,
                display: window.getComputedStyle(b).display,
            }));
            const hasApiKeyPrompt = document.body.innerHTML.includes('sk-ant') || document.body.innerHTML.includes('API key') || document.body.innerHTML.includes('Claude Console');
            const hasBirthPrompt = document.body.innerHTML.includes('ready to be born') || document.body.innerHTML.includes('Start AI Birth') || document.body.innerHTML.includes('runBirthInit');
            const hasOauthBtn = document.body.innerHTML.includes('oauth') || document.body.innerHTML.includes('OAuth');
            return {
                msg_count: msgs.length,
                last_3_msgs: msgs.slice(-3),
                visible_buttons: btns.filter(b => b.display !== 'none'),
                has_api_key_prompt: hasApiKeyPrompt,
                has_birth_prompt: hasBirthPrompt,
                has_oauth_text: hasOauthBtn,
                window_runBirthInit: typeof window.runBirthInit,
                window_pbContainerName: window._pbContainerName || 'NOT SET',
                window_pbBirthOauthUrl: window._pbBirthOauthUrl || 'NOT SET',
            };
        }
    """)
    result["step_results"]["ptc_state_after_questionnaire"] = ptc_state
    print(f"  [PTC STATE AFTER QUESTIONNAIRE]: {json.dumps(ptc_state, indent=4)}")

    # If we see the API key prompt (old Claude auth flow)
    if ptc_state.get("has_api_key_prompt"):
        print("  [FOUND] Claude API key prompt detected")
        # Find and click "I have my key" button
        key_btn = await page.query_selector(".ptc-btn, .ptc-btn--primary")
        if key_btn:
            key_text = await key_btn.text_content()
            print(f"  [CLICK] Key button: '{key_text}'")
            await key_btn.click()
            await asyncio.sleep(2)
            # Enter fake key
            textarea = await page.query_selector("textarea")
            if textarea:
                await textarea.fill("sk-ant-api03-testkey12345678901234567890")
                send = await page.query_selector("button.ptc-send-btn")
                if send:
                    await send.click()
                await asyncio.sleep(5)

    # If we see birth prompt
    if ptc_state.get("has_birth_prompt"):
        print("  [FOUND] Birth prompt detected! Looking for Start AI Birth button")
        birth_btn = None
        for btn_info in ptc_state.get("visible_buttons", []):
            if "birth" in btn_info["text"].lower() or "start" in btn_info["text"].lower():
                print(f"  [CLICK] Birth button: '{btn_info['text']}'")
                # Find and click it
                all_btns = await page.query_selector_all(".ptc-btn, .ptc-btn--primary, button")
                for btn in all_btns:
                    txt = await btn.text_content()
                    if "birth" in txt.lower() or "start" in txt.lower():
                        await btn.click()
                        await asyncio.sleep(5)
                        break

        p_path = str(SCREENSHOTS_DIR / f"{slug}-10-after-birth-click.png")
        await page.screenshot(path=p_path, full_page=True, timeout=15000)
        result["screenshots"].append(p_path)
        print(f"  [SS] {p_path}")

        # Check for OAuth URL appearing
        oauth_check = await page.evaluate("""
            () => {
                return {
                    pbBirthOauthUrl: window._pbBirthOauthUrl || 'NOT SET',
                    pbContainerName: window._pbContainerName || 'NOT SET',
                    pbBirthAuthenticated: window._pbBirthAuthenticated || 'NOT SET',
                    oauth_links: Array.from(document.querySelectorAll('a[href*="oauth"], a[href*="claude.ai"]')).map(a => a.href),
                    oauth_text_in_dom: document.body.innerHTML.includes('oauthUrl') || document.body.innerHTML.includes('OAuth'),
                }
            }
        """)
        result["step_results"]["oauth_check_after_birth"] = oauth_check
        print(f"  [OAUTH CHECK] {json.dumps(oauth_check, indent=4)}")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

        all_results = {}

        for cfg in PAGES:
            print(f"\n{'#'*70}\n# {cfg['name']}\n{'#'*70}")
            try:
                r = await test_page(browser, cfg)
                all_results[cfg["slug"]] = r
            except Exception as e:
                import traceback
                print(f"ERROR: {e}")
                traceback.print_exc()
                all_results[cfg["slug"]] = {"error": str(e), "traceback": traceback.format_exc()}

            print("\nWaiting 25s between pages...")
            await asyncio.sleep(25)

        await browser.close()

        out = "/home/jared/projects/AI-CIV/aether/exports/oauth-test-v2-results-20260227.json"
        with open(out, "w") as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"\nResults: {out}")
        return all_results


if __name__ == "__main__":
    asyncio.run(main())
