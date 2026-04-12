"""
OAuth Button Diagnosis Script v3 - 2026-02-27
Completes the full PTC questionnaire flow to reach the OAuth button.
Also separately tests the production page script differences.
"""

import asyncio
import json
import os
import re
from datetime import datetime
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/oauth-diagnosis-20260227"
PASSWORD = "PureBrain.ai253443$$$"

all_console_logs = {"sandbox": [], "production": []}
all_network_events = {"sandbox": [], "production": []}


def ts():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


async def screenshot(page, label, page_key):
    path = f"{SCREENSHOTS_DIR}/{page_key}-v3-{label}.png"
    await page.screenshot(path=path, full_page=False)
    print(f"  [{ts()}] Screenshot: {os.path.basename(path)}")
    return path


async def wait_for_ptc_message(page, timeout_sec=15):
    """Wait for new AI message to appear in PTC."""
    start = asyncio.get_event_loop().time()
    prev_count = await page.evaluate("document.querySelectorAll('.ptc-msg--ai').length")
    while asyncio.get_event_loop().time() - start < timeout_sec:
        count = await page.evaluate("document.querySelectorAll('.ptc-msg--ai').length")
        if count > prev_count:
            await asyncio.sleep(1)  # Let message finish rendering
            return True
        await asyncio.sleep(0.5)
    return False


async def get_latest_ptc_message(page):
    return await page.evaluate("""() => {
        const msgs = document.querySelectorAll('.ptc-msg--ai');
        return msgs.length > 0 ? msgs[msgs.length - 1].textContent.trim() : '';
    }""")


async def get_ptc_buttons(page):
    return await page.evaluate("""() => {
        return Array.from(document.querySelectorAll('.ptc-btn')).map(b => ({
            id: b.id,
            class: b.className,
            text: b.textContent.trim().substring(0, 100),
            visible: b.getBoundingClientRect().height > 0,
            display: window.getComputedStyle(b).display,
            disabled: b.disabled,
        }));
    }""")


async def send_ptc_message(page, text):
    """Type and send a message in PTC."""
    textarea = page.locator("textarea[placeholder*='Message'], textarea[placeholder*='message']")
    await textarea.fill(text)
    await asyncio.sleep(0.3)
    # Click send button
    send_btn = page.locator("button.ptc-send-btn")
    if await send_btn.count() > 0:
        await send_btn.click()
    else:
        await page.keyboard.press("Enter")
    await asyncio.sleep(0.5)


async def click_ptc_primary_button(page):
    """Click the first visible primary PTC button."""
    btns = await get_ptc_buttons(page)
    for btn in btns:
        if btn['visible'] and 'primary' in btn['class']:
            btn_locator = page.locator(f".ptc-btn--primary").first
            await btn_locator.click(force=True)
            return btn['text']
    # Fallback: try any visible ptc-btn
    for btn in btns:
        if btn['visible']:
            await page.evaluate(f"""() => {{
                const btns = document.querySelectorAll('.ptc-btn');
                for (const b of btns) {{
                    if (b.getBoundingClientRect().height > 0) {{
                        b.click();
                        return;
                    }}
                }}
            }}""")
            return btn['text']
    return None


async def run_full_ptc_flow(page, page_key):
    """Navigate through the complete PTC questionnaire to find OAuth button."""
    print(f"\n  [PTC Flow] Starting full questionnaire navigation")
    results = {
        "phases": [],
        "oauth_button_found": False,
        "oauth_button_details": None,
        "birth_start_network": None,
        "oauth_url": None,
        "errors": [],
    }

    # Phase 1: Name
    print(f"\n  [PTC Phase 1] Sending name")
    await send_ptc_message(page, "Jared Sanborn")
    await wait_for_ptc_message(page, timeout_sec=12)
    msg = await get_latest_ptc_message(page)
    print(f"    AI response: {msg[:150]}")
    results["phases"].append({"phase": "name", "response": msg[:200]})
    await screenshot(page, "ptc-01-name", page_key)

    # Phase 2: Email
    print(f"\n  [PTC Phase 2] Sending email")
    await send_ptc_message(page, "jared@puretechnology.nyc")
    await wait_for_ptc_message(page, timeout_sec=12)
    msg = await get_latest_ptc_message(page)
    print(f"    AI response: {msg[:150]}")
    results["phases"].append({"phase": "email", "response": msg[:200]})
    await screenshot(page, "ptc-02-email", page_key)

    # Phase 3: Company
    print(f"\n  [PTC Phase 3] Sending company")
    await send_ptc_message(page, "Pure Technology")
    await wait_for_ptc_message(page, timeout_sec=12)
    msg = await get_latest_ptc_message(page)
    print(f"    AI response: {msg[:150]}")
    results["phases"].append({"phase": "company", "response": msg[:200]})
    await screenshot(page, "ptc-03-company", page_key)

    # Phase 4: Role
    print(f"\n  [PTC Phase 4] Sending role")
    await send_ptc_message(page, "CEO")
    await wait_for_ptc_message(page, timeout_sec=15)  # This triggers runBirthInit
    msg = await get_latest_ptc_message(page)
    print(f"    AI response: {msg[:200]}")
    results["phases"].append({"phase": "role", "response": msg[:300]})
    await screenshot(page, "ptc-04-role", page_key)

    # After role, check for OAuth button (runBirthInit fires after role in v4.3.3)
    await asyncio.sleep(3)  # Wait for /api/birth/start response

    print(f"\n  [PTC Phase 5 - CRITICAL] Checking for OAuth button after role entry")
    btns = await get_ptc_buttons(page)
    msg = await get_latest_ptc_message(page)
    print(f"    Latest message: {msg[:250]}")
    print(f"    Current buttons: {btns}")
    await screenshot(page, "ptc-05-post-role-oauth-check", page_key)

    # Check if oauth button or birth-related elements appeared
    oauth_check = await page.evaluate("""() => {
        const allText = document.body.textContent;
        const hasOAuth = allText.toLowerCase().includes('oauth') ||
                         allText.toLowerCase().includes('authorize') ||
                         allText.toLowerCase().includes('connect') && allText.toLowerCase().includes('claude');

        // Check for specific OAuth button elements
        const oauthBtns = Array.from(document.querySelectorAll('[id*="oauth"], [class*="oauth"], [onclick*="oauth"]'));

        // Check for "I have my key" button
        const keyBtn = Array.from(document.querySelectorAll('.ptc-btn')).filter(b =>
            b.textContent.toLowerCase().includes('key') ||
            b.textContent.toLowerCase().includes('authorize') ||
            b.textContent.toLowerCase().includes('connect')
        );

        // Get ALL ptc-btn content right now
        const allPtcBtns = Array.from(document.querySelectorAll('.ptc-btn')).map(b => ({
            text: b.textContent.trim(),
            visible: b.getBoundingClientRect().height > 0,
        }));

        // Get ALL messages to understand flow state
        const allMessages = Array.from(document.querySelectorAll('.ptc-msg--ai')).map(m =>
            m.textContent.trim().substring(0, 150)
        );

        // Look for Birth Init "start" button
        const birthStartBtn = document.getElementById('birthInitBtn') ||
                              document.querySelector('[id*="birth"]') ||
                              null;

        return {
            hasOAuthText: hasOAuth,
            oauthBtns: oauthBtns.map(b => ({ id: b.id, class: b.className, text: b.textContent.trim().substring(0, 80) })),
            keyOrAuthBtns: keyBtn.map(b => ({ text: b.textContent.trim(), visible: b.getBoundingClientRect().height > 0 })),
            allPtcBtns: allPtcBtns,
            allMessages: allMessages,
            birthStartBtn: birthStartBtn ? { id: birthStartBtn.id, text: birthStartBtn.textContent.trim().substring(0, 80) } : null,
        };
    }""")

    print(f"    Has OAuth text: {oauth_check['hasOAuthText']}")
    print(f"    OAuth buttons: {oauth_check['oauthBtns']}")
    print(f"    Key/Auth buttons: {oauth_check['keyOrAuthBtns']}")
    print(f"    All PTC buttons: {oauth_check['allPtcBtns']}")
    print(f"    Birth start btn: {oauth_check['birthStartBtn']}")
    print(f"    All messages so far:")
    for m in oauth_check['allMessages']:
        print(f"      {m[:150]}")

    results["phases"].append({"phase": "oauth_check_post_role", "oauth_data": oauth_check})

    # If there's a birth start button, click it
    if oauth_check['birthStartBtn']:
        print(f"\n  [PTC] Found birth init button! Clicking it...")
        await page.evaluate("document.querySelector('[id*=\"birth\"]').click()")
        await asyncio.sleep(5)
        await screenshot(page, "ptc-06-after-birth-init", page_key)
        btns = await get_ptc_buttons(page)
        msg = await get_latest_ptc_message(page)
        print(f"    After birth init - message: {msg[:250]}")
        print(f"    After birth init - buttons: {btns}")

    # Continue interacting - if there are "next" or primary buttons, click them
    # (to advance to the OAuth phase if we haven't reached it)
    for attempt in range(3):
        btns = await get_ptc_buttons(page)
        visible_btns = [b for b in btns if b['visible']]
        if not visible_btns:
            break

        # Check if any button looks like it's related to OAuth/auth
        auth_btn = next((b for b in visible_btns
                         if any(word in b['text'].lower() for word in ['key', 'authorize', 'auth', 'connect', 'claude', 'start ai', 'birth'])), None)
        if auth_btn:
            print(f"\n  [PTC] Found auth-related button: {auth_btn['text']}")
            await click_ptc_primary_button(page)
            await asyncio.sleep(5)
            await screenshot(page, f"ptc-07-auth-btn-{attempt}", page_key)
            msg = await get_latest_ptc_message(page)
            print(f"    After clicking: {msg[:250]}")
            results["phases"].append({"phase": f"auth_btn_click_{attempt}", "btn": auth_btn['text'], "response": msg[:200]})
            break

        # Otherwise just click the primary button to advance
        first_btn = next((b for b in visible_btns if 'primary' in b['class']), visible_btns[0] if visible_btns else None)
        if first_btn:
            print(f"\n  [PTC] Advancing with button: {first_btn['text']}")
            clicked = await click_ptc_primary_button(page)
            await wait_for_ptc_message(page, timeout_sec=10)
            msg = await get_latest_ptc_message(page)
            print(f"    Button clicked: {clicked} | Response: {msg[:150]}")
            results["phases"].append({"phase": f"advance_{attempt}", "btn": clicked, "response": msg[:200]})
        else:
            break

    await screenshot(page, "ptc-08-final-state", page_key)

    # Final comprehensive check for OAuth button
    final_check = await page.evaluate("""() => {
        // Exhaustive search for anything OAuth-related
        const results = {
            domHasOAuth: document.body.innerHTML.toLowerCase().includes('oauth'),
            domHasAuthorize: document.body.innerHTML.toLowerCase().includes('authorize'),
            domHasClaudeAi: document.body.innerHTML.toLowerCase().includes('claude.ai'),
            oauthLinks: [],
            allCurrentBtns: [],
            latestMessages: [],
            networkInterceptors: null,
        };

        // Check for anchor tags with claude.ai
        document.querySelectorAll('a').forEach(a => {
            if (a.href && (a.href.includes('claude.ai') || a.href.includes('oauth') || a.href.includes('anthropic'))) {
                results.oauthLinks.push({ href: a.href, text: a.textContent.trim().substring(0, 80) });
            }
        });

        // All current visible buttons
        document.querySelectorAll('button, a.ptc-btn').forEach(b => {
            if (b.getBoundingClientRect().height > 0) {
                results.allCurrentBtns.push({
                    tag: b.tagName,
                    id: b.id,
                    text: b.textContent.trim().substring(0, 80),
                    href: b.href || '',
                    onclick: (b.getAttribute('onclick') || '').substring(0, 100),
                });
            }
        });

        // Last 3 messages
        const msgs = document.querySelectorAll('.ptc-msg--ai');
        results.latestMessages = Array.from(msgs).slice(-3).map(m => m.textContent.trim().substring(0, 200));

        return results;
    }""")

    print(f"\n  [PTC Final Check]")
    print(f"    DOM has OAuth: {final_check['domHasOAuth']}")
    print(f"    DOM has authorize: {final_check['domHasAuthorize']}")
    print(f"    DOM has claude.ai: {final_check['domHasClaudeAi']}")
    print(f"    OAuth links: {final_check['oauthLinks']}")
    print(f"    Current visible buttons: {final_check['allCurrentBtns']}")
    print(f"    Latest messages: {final_check['latestMessages']}")

    results["final_oauth_check"] = final_check
    results["oauth_button_found"] = final_check['domHasOAuth'] or len(final_check['oauthLinks']) > 0

    return results


async def extract_oauth_from_script(page, page_key):
    """Extract the complete OAuth implementation from the 88k script."""
    print(f"\n[Script Deep Extraction - {page_key}]")
    result = await page.evaluate("""() => {
        const scripts = Array.from(document.querySelectorAll('script'));
        const ptcScript = scripts.find(s => s.src === '' && s.textContent.length > 80000);
        if (!ptcScript) return { error: 'No large script found' };

        const text = ptcScript.textContent;
        const lines = text.split('\\n');

        // Find ALL lines with oauth (case insensitive)
        const oauthContext = [];
        lines.forEach((line, idx) => {
            if (/oauth/i.test(line)) {
                const start = Math.max(0, idx - 3);
                const end = Math.min(lines.length - 1, idx + 8);
                const context = lines.slice(start, end).join('\\n');
                oauthContext.push({
                    lineNum: idx,
                    context: context.substring(0, 600),
                });
            }
        });

        // Find birthOauthUrl assignment
        const birthOauthMatch = text.match(/birthOauthUrl[^;]+;/g);
        const oauthUrlVar = birthOauthMatch ? birthOauthMatch.slice(0, 5) : [];

        // Find /api/birth/start call
        const birthStartMatch = text.match(/\\/api\\/birth\\/start[^'"]{0,200}/g);

        // Find what happens after birth/start responds (the then() block)
        const birthStartThenIdx = text.indexOf('/api/birth/start');
        let birthStartContext = '';
        if (birthStartThenIdx > 0) {
            birthStartContext = text.substring(birthStartThenIdx - 200, birthStartThenIdx + 800);
        }

        // Find startOAuth or similar function
        const oauthFunctions = [];
        const fnPattern = /(?:function|const|let|var)\\s+(\\w*[Oo]auth\\w*)\\s*[=({]/g;
        let match;
        while ((match = fnPattern.exec(text)) !== null) {
            const fnStart = match.index;
            oauthFunctions.push({
                name: match[1],
                code: text.substring(fnStart, fnStart + 500),
            });
        }

        // Extract the entire birth init section
        const birthInitIdx = text.indexOf('runBirthInit');
        let birthInitCode = '';
        if (birthInitIdx > 0) {
            birthInitCode = text.substring(birthInitIdx, birthInitIdx + 2000);
        }

        return {
            scriptSize: text.length,
            oauthContextCount: oauthContext.length,
            oauthContexts: oauthContext.slice(0, 8),
            oauthUrlVarRefs: oauthUrlVar,
            birthStartRefs: birthStartMatch ? birthStartMatch.slice(0, 5) : [],
            birthStartContext: birthStartContext.substring(0, 1200),
            oauthFunctions: oauthFunctions.slice(0, 5),
            birthInitCode: birthInitCode.substring(0, 2000),
        };
    }""")

    print(f"  Script size: {result.get('scriptSize')}")
    print(f"  OAuth context count: {result.get('oauthContextCount')}")
    print(f"\n  OAuth code contexts:")
    for ctx in result.get('oauthContexts', []):
        print(f"\n    --- Line {ctx['lineNum']} ---")
        print(f"    {ctx['context']}")

    print(f"\n  birthOauthUrl refs: {result.get('oauthUrlVarRefs', [])}")
    print(f"\n  /api/birth/start refs: {result.get('birthStartRefs', [])}")
    print(f"\n  /api/birth/start context:\n{result.get('birthStartContext', '')[:1000]}")
    print(f"\n  runBirthInit code:\n{result.get('birthInitCode', '')[:1500]}")

    return result


async def diagnose_page(playwright, page_key, url):
    print(f"\n{'='*60}")
    print(f"DIAGNOSING: {page_key.upper()} -> {url}")
    print(f"{'='*60}")

    browser = await playwright.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    context = await browser.new_context(
        viewport={"width": 1440, "height": 900},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        ignore_https_errors=True,
    )
    page = await context.new_page()

    def on_console(msg):
        entry = {"type": msg.type, "text": msg.text, "time": ts()}
        all_console_logs[page_key].append(entry)
        if msg.type in ("error",) and "birth" in msg.text.lower() or "oauth" in msg.text.lower():
            print(f"  [{ts()}] CONSOLE {msg.type.upper()}: {msg.text[:200]}")

    def on_request(request):
        if any(k in request.url for k in ["api/birth", "api/verify", "oauth", "anthropic.com", "claude.ai", "purebrain.ai/api"]):
            entry = {"type": "request", "method": request.method, "url": request.url, "time": ts(), "post_data": None}
            try:
                entry["post_data"] = request.post_data
            except:
                pass
            all_network_events[page_key].append(entry)
            print(f"  [{ts()}] REQ: {request.method} {request.url[:130]}")

    def on_response(response):
        if any(k in response.url for k in ["api/birth", "api/verify", "oauth", "anthropic.com", "claude.ai", "purebrain.ai/api"]):
            entry = {"type": "response", "status": response.status, "url": response.url, "time": ts()}
            all_network_events[page_key].append(entry)
            status_ok = "OK" if response.status < 400 else "FAIL"
            print(f"  [{ts()}] RES [{status_ok}] {response.status}: {response.url[:130]}")

    def on_request_failed(request):
        if any(k in request.url for k in ["api/birth", "oauth", "purebrain.ai/api"]):
            entry = {"type": "failed", "url": request.url, "failure": request.failure, "time": ts()}
            all_network_events[page_key].append(entry)
            print(f"  [{ts()}] FAILED: {request.url[:130]} | {request.failure}")

    page.on("console", on_console)
    page.on("request", on_request)
    page.on("response", on_response)
    page.on("requestfailed", on_request_failed)

    results = {"page_key": page_key, "url": url}

    # Navigate
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await asyncio.sleep(3)
    await screenshot(page, "00-load", page_key)

    # Password
    pw = page.locator("input[id^='pwbox-']")
    if await pw.count() > 0:
        await pw.fill(PASSWORD)
        await page.keyboard.press("Enter")
        await asyncio.sleep(7)
        await screenshot(page, "01-unlocked", page_key)

    # Extract script info
    results["script_info"] = await extract_oauth_from_script(page, page_key)

    # --- For sandbox: run complete flow ---
    if page_key == "sandbox":
        # Begin pre-payment chat
        begin = page.locator(".chat-initial__btn")
        if await begin.count() > 0:
            await begin.click()
            await asyncio.sleep(7)

        # Bypass
        user_input = page.locator("#userInput")
        if await user_input.count() > 0:
            await user_input.fill("pb-full-bypass")
            sub = page.locator("#submitBtn")
            if await sub.count() > 0:
                await sub.click()
            else:
                await page.keyboard.press("Enter")
            await asyncio.sleep(8)
            await screenshot(page, "02-bypass-done", page_key)

        # JS click to reveal pricing and open PayPal modal
        await page.evaluate("""() => {
            const pricingSection = document.querySelector('.pricing-section');
            if (pricingSection) pricingSection.style.display = 'block';
            const proCta = document.getElementById('proCta');
            if (proCta) proCta.click();
        }""")
        await asyncio.sleep(4)

        # Click sandbox bypass
        bypass_btn = page.locator("#pb-sandbox-bypass-btn")
        if await bypass_btn.count() > 0:
            print("  Clicking sandbox payment bypass...")
            await bypass_btn.click(force=True)
        else:
            # Try JS click
            await page.evaluate("""() => {
                const btn = document.getElementById('pb-sandbox-bypass-btn');
                if (btn) btn.click();
            }""")
        await asyncio.sleep(5)
        await screenshot(page, "03-ptc-loaded", page_key)

        # Check PTC loaded
        ptc = await page.evaluate("!!document.querySelector('.ptc-wrapper')")
        print(f"  PTC wrapper loaded: {ptc}")

        if ptc:
            # Run the full questionnaire
            ptc_results = await run_full_ptc_flow(page, page_key)
            results["ptc_flow"] = ptc_results
        else:
            print("  PTC not loaded — checking state")
            state = await page.evaluate("""() => ({
                sandboxBypassExists: !!document.getElementById('pb-sandbox-bypass-btn'),
                ptcExists: !!document.querySelector('.ptc-wrapper'),
                visibleElements: Array.from(document.querySelectorAll('[class*="ptc"]')).map(e => ({
                    class: e.className, display: window.getComputedStyle(e).display
                })).slice(0, 10),
            })""")
            print(f"  State: {state}")
            results["ptc_flow"] = {"error": "PTC not loaded", "state": state}

    # --- For production: just extract script info + test API ---
    else:
        # Begin chat and observe
        begin = page.locator(".chat-initial__btn")
        if await begin.count() > 0:
            await begin.click()
            await asyncio.sleep(5)
            await screenshot(page, "02-chat-started", page_key)

        # Test /api/birth/start from production page context
        birth_test = await page.evaluate("""async () => {
            try {
                const res = await fetch('/api/birth/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ container: 'test-prod', email: 'test@test.com' }),
                });
                const text = await res.text();
                return { status: res.status, body: text.substring(0, 400) };
            } catch(e) { return { error: e.message }; }
        }""")
        print(f"  Production /api/birth/start test: {birth_test}")
        results["birth_api_test"] = birth_test

    # Console summary
    errors = [l for l in all_console_logs[page_key] if l["type"] == "error"]
    results["console_errors"] = errors[:20]
    results["network_events"] = all_network_events[page_key]

    await browser.close()
    return results


async def main():
    print(f"\nOAuth Diagnosis v3 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    async with async_playwright() as playwright:
        print("\n### SANDBOX ###")
        results["sandbox"] = await diagnose_page(playwright, "sandbox", "https://purebrain.ai/pay-test-sandbox-2/")

        print(f"\nWaiting 25 seconds for WAF cooldown...")
        await asyncio.sleep(25)

        print("\n### PRODUCTION ###")
        results["production"] = await diagnose_page(playwright, "production", "https://purebrain.ai/pay-test-2/")

    # Final comparison
    print("\n" + "="*70)
    print("COMPARISON SUMMARY")
    print("="*70)

    s = results["sandbox"]
    p = results["production"]

    s_script = s.get("script_info", {})
    p_script = p.get("script_info", {})

    print("\n[Script Sizes]")
    print(f"  Sandbox:    {s_script.get('scriptSize')}")
    print(f"  Production: {p_script.get('scriptSize')}")
    same = s_script.get('scriptSize') == p_script.get('scriptSize')
    print(f"  SAME SCRIPT? {same}")

    print("\n[/api/birth/start context - sandbox]")
    print(s_script.get('birthStartContext', '')[:600])
    print("\n[/api/birth/start context - production]")
    print(p_script.get('birthStartContext', '')[:600])

    print("\n[Network Events - Sandbox]")
    for ev in s.get('network_events', []):
        print(f"  {ev['type']}: {ev.get('method', '')} {ev['url'][:120]} {ev.get('status', ev.get('failure', ''))}")

    print("\n[Network Events - Production]")
    for ev in p.get('network_events', []):
        print(f"  {ev['type']}: {ev.get('method', '')} {ev['url'][:120]} {ev.get('status', ev.get('failure', ''))}")

    ptc_flow = s.get("ptc_flow", {})
    print("\n[PTC Flow Result - Sandbox]")
    print(f"  OAuth button found: {ptc_flow.get('oauth_button_found')}")
    final = ptc_flow.get('final_oauth_check', {})
    if final:
        print(f"  DOM has OAuth: {final.get('domHasOAuth')}")
        print(f"  OAuth links: {final.get('oauthLinks')}")
        print(f"  Latest messages: {final.get('latestMessages')}")

    # Save
    output_path = f"{SCREENSHOTS_DIR}/oauth_v3_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
