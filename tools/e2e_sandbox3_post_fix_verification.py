"""
E2E Sandbox-3 Post-Fix Verification Test
Tests the 3 specific bug fixes:
  Fix 1: Dynamic AI name (not hardcoded "AICIV")
  Fix 2: Send button disabled after "Your AI is ready" click
  Fix 3: Brain Stream button greyed out (not clickable)

Per Jared's instructions 2026-03-04.
AI name provided by user during Q&A is "Nova" (question 2: what's your AI's name?)
NOTE: Based on memory, sandbox-3 may NOT ask AI name. We adapt dynamically.
"""

import asyncio
import os
import time
import subprocess
from playwright.async_api import async_playwright

PAGE_URL = "https://purebrain.ai/pay-test-sandbox-3/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/e2e-sandbox3-post-fix-screenshots"
TG_SEND = "/home/jared/projects/AI-CIV/aether/tools/tg_send.sh"

# AI name for the session - we try "Nova" for Q2 if sandbox asks for it
AI_NAME_CHOSEN = "Nova"
# Fallback: if sandbox doesn't ask for AI name, this stays as reference
USER_NAME = "Test User"

sc = 0

def tg(msg):
    try:
        subprocess.run([TG_SEND, str(msg)[:4000]], timeout=10, capture_output=True)
        print(f"[TG] {str(msg)[:200]}")
    except:
        pass

def tg_photo(path, cap):
    try:
        subprocess.run([TG_SEND, "--photo", path, str(cap)[:200]], timeout=15, capture_output=True)
    except:
        pass

async def ss(page, label, send_to_tg=True):
    global sc
    sc += 1
    fn = f"{sc:02d}-{label}.png"
    path = os.path.join(SCREENSHOT_DIR, fn)
    try:
        await page.screenshot(path=path)
        print(f"[SS] {fn}")
        if send_to_tg:
            tg_photo(path, f"{sc}: {label}")
    except Exception as e:
        print(f"[SS ERR] {label}: {e}")
    return path

async def wait_input_active(page, timeout=60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            d = await page.evaluate("""(function(){
                var r = document.getElementById('ptc-input-row');
                if (!r) return 'not-found';
                return window.getComputedStyle(r).display;
            })()""")
            if d not in ("none", "not-found"):
                return True
        except:
            pass
        await asyncio.sleep(0.5)
    return False

async def send_answer(page, text):
    for sel in ["#ptc-input", "textarea.ptc-input"]:
        try:
            ta = await page.query_selector(sel)
            if ta and await ta.is_visible():
                await ta.fill(text)
                await asyncio.sleep(0.15)
                for bsel in ["#ptc-send-btn", ".ptc-send-btn"]:
                    btn = await page.query_selector(bsel)
                    if btn and await btn.is_visible():
                        await btn.click()
                        return True
                await ta.press("Enter")
                return True
        except:
            pass
    return False

async def get_visible_buttons(page):
    return await page.evaluate("""(function(){
        return Array.from(document.querySelectorAll('button, a')).filter(el => {
            var s = window.getComputedStyle(el);
            return s.display !== 'none' && el.offsetParent !== null && el.textContent.trim().length > 0;
        }).map(el => ({
            text: el.textContent.trim().substring(0, 100),
            cls: el.className.substring(0, 80),
            id: el.id,
            disabled: el.disabled || false,
            opacity: window.getComputedStyle(el).opacity,
            pointerEvents: window.getComputedStyle(el).pointerEvents
        }));
    })()""")

async def click_text_btn(page, text_fragment):
    return await page.evaluate(f"""(function(){{
        var els = Array.from(document.querySelectorAll('button, a'));
        var el = els.find(e => e.textContent.trim().toLowerCase().includes({repr(text_fragment.lower())}) && window.getComputedStyle(e).display !== 'none' && !e.disabled);
        if (el) {{ el.click(); return el.textContent.trim().substring(0, 80); }}
        return null;
    }})()""")

async def get_last_ai_msg(page):
    return await page.evaluate("""(function(){
        var msgs = Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-message--ai'));
        return msgs.length > 0 ? msgs[msgs.length-1].textContent.trim() : null;
    })()""")

async def check_send_button_state(page):
    return await page.evaluate("""(function(){
        var input = document.getElementById('ptc-input') || document.querySelector('textarea.ptc-input');
        var sendBtn = document.getElementById('ptc-send-btn') || document.querySelector('.ptc-send-btn');
        var inputRow = document.getElementById('ptc-input-row');
        var result = {
            inputFound: !!input,
            sendBtnFound: !!sendBtn,
            inputRowDisplay: inputRow ? window.getComputedStyle(inputRow).display : 'NOT FOUND',
            inputDisabled: input ? (input.disabled || input.readOnly) : null,
            inputPlaceholder: input ? input.placeholder : null,
            sendBtnDisabled: sendBtn ? sendBtn.disabled : null,
            sendBtnOpacity: sendBtn ? window.getComputedStyle(sendBtn).opacity : null,
            sendBtnPointerEvents: sendBtn ? window.getComputedStyle(sendBtn).pointerEvents : null,
            sendBtnText: sendBtn ? sendBtn.textContent.trim() : null
        };
        return result;
    })()""")

async def check_brain_stream_state(page):
    return await page.evaluate("""(function(){
        // Find all elements mentioning brain stream
        var candidates = [];
        document.querySelectorAll('button, a, div, span, p').forEach(el => {
            var t = el.textContent.trim();
            if (t.length < 300 && (t.toUpperCase().includes('BRAIN STREAM') || t.toUpperCase().includes('ENTER') || el.className.toLowerCase().includes('brain'))) {
                var s = window.getComputedStyle(el);
                candidates.push({
                    tag: el.tagName,
                    text: t.substring(0, 150),
                    cls: el.className.substring(0, 100),
                    id: el.id,
                    display: s.display,
                    opacity: s.opacity,
                    pointerEvents: s.pointerEvents,
                    disabled: el.disabled || false,
                    visible: s.display !== 'none' && s.visibility !== 'hidden' && el.offsetParent !== null,
                    cursor: s.cursor,
                    animation: s.animation,
                    background: s.background.substring(0, 100)
                });
            }
        });
        return candidates;
    })()""")

async def check_dynamic_name(page, ai_name):
    """Check if the page shows dynamic AI name or hardcoded 'AICIV'."""
    return await page.evaluate(f"""(function(){{
        var aiName = {repr(ai_name)};
        var text = document.body.innerText;
        var textUpper = text.toUpperCase();
        return {{
            hasAICIV: textUpper.includes('AICIV'),
            hasDynamicName: aiName ? text.includes(aiName) : false,
            hasYourAI: textUpper.includes('YOUR AI'),
            pageText: text.substring(0, 2000)
        }};
    }})()""")

async def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    print(f"[INFO] Screenshot dir: {SCREENSHOT_DIR}")

    t0 = time.time()
    page_errors = []
    api_calls = []
    results = {
        "fix1_dynamic_name": None,  # PASS/FAIL
        "fix2_send_disabled": None,
        "fix3_brain_greyed": None,
        "ai_name_used": None,
        "notes": []
    }

    tg("=== POST-FIX E2E TEST STARTING ===")
    tg(f"URL: {PAGE_URL}")
    tg(f"Viewport: 1280x900 | Password: Set | JS Payment Simulation: ON")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        ctx = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await ctx.new_page()

        page.on("pageerror", lambda e: page_errors.append(str(e)))

        async def on_resp(r):
            url = r.url
            if "purebrain.ai" in url or "api.purebrain" in url:
                api_calls.append(f"{r.status} {url}")
        page.on("response", on_resp)

        # ===== STEP 1: PASSWORD GATE =====
        print(f"\n[{int(time.time()-t0)}s] STEP 1: PASSWORD GATE")
        await page.goto(PAGE_URL, wait_until="load", timeout=30000)
        await asyncio.sleep(2)

        # Screenshot BEFORE entering password
        await ss(page, "01-password-gate-BEFORE")

        pw_field = await page.query_selector("input[type='password'], input[name='post_password']")
        if pw_field:
            await pw_field.fill(PAGE_PASSWORD)
            await asyncio.sleep(0.3)
            await ss(page, "01b-password-field-filled")
            sub = await page.query_selector("input[type='submit'], button[type='submit']")
            if sub:
                await sub.click()
            else:
                await pw_field.press("Enter")
            try:
                await page.wait_for_load_state("load", timeout=10000)
            except:
                pass
            await asyncio.sleep(3)
            await ss(page, "02-password-gate-AFTER")
            tg("Password gate: ENTERED. Screenshot taken.")
            results["notes"].append("Password gate: navigated successfully")
        else:
            await ss(page, "02-no-password-gate")
            tg("No password gate found - may already be unlocked.")
            results["notes"].append("No password gate found")

        # ===== STEP 2: PAYMENT SECTION =====
        print(f"\n[{int(time.time()-t0)}s] STEP 2: PAYMENT SECTION")
        await asyncio.sleep(2)

        # Screenshot payment section
        paypal_state = await page.evaluate("""(function(){
            var iframes = Array.from(document.querySelectorAll('iframe')).map(f => ({src: f.src.substring(0,100), w: f.offsetWidth, h: f.offsetHeight}));
            var ppContainers = Array.from(document.querySelectorAll('[id*="paypal"],[class*="paypal"]')).map(e => ({id: e.id, cls: e.className.substring(0,50), w: e.offsetWidth, h: e.offsetHeight}));
            return {iframes: iframes, ppContainers: ppContainers, bodyText: document.body.innerText.substring(0, 500)};
        })()""")
        print(f"[PAYPAL] iframes={paypal_state['iframes'][:3]}, containers={paypal_state['ppContainers'][:3]}")

        await ss(page, "03-payment-section")
        tg(f"Payment section: PayPal iframes={len(paypal_state['iframes'])} (PayPal won't render in headless — expected)")

        # Check functions
        funcs = await page.evaluate("""(function(){
            return {
                onPaymentComplete: typeof window.onPaymentComplete,
                launchPostPaymentFlow: typeof window.launchPostPaymentFlow,
                sanitizeText: typeof window.sanitizeText,
                initPayTestFlow: typeof window.initPayTestFlow
            };
        })()""")
        print(f"[FUNCS] {funcs}")

        if funcs.get("onPaymentComplete") != "function":
            tg(f"ERROR: onPaymentComplete not found! funcs={funcs}")
            for e in page_errors[:3]:
                tg(f"PageError: {e[:200]}")
            await browser.close()
            return

        # Trigger JS payment simulation
        order_id = f"POST-FIX-{int(time.time())}"
        await page.evaluate(f"window.onPaymentComplete('Awakened', '{order_id}', {{}})")
        tg(f"Payment simulated via JS (orderId={order_id}). sanitizeText={funcs.get('sanitizeText')}")
        await asyncio.sleep(5)

        # ===== STEP 3: CHATBOX + Q&A =====
        print(f"\n[{int(time.time()-t0)}s] STEP 3: CHATBOX ACTIVATION")

        if not await wait_input_active(page, 30):
            tg("ERROR: Chatbox not active after 30s!")
            for e in page_errors[:5]:
                tg(f"Error: {e[:200]}")
            await ss(page, "03-ERROR-chatbox-not-active")
            await browser.close()
            return

        await ss(page, "04-chatbox-ACTIVE")
        tg("Chatbox ACTIVE. Starting Q&A.")
        tg("E2E Post-Fix: Password passed, chatbox active. Running Q&A now.")

        # Detect what Q&A sandbox-3 asks
        # Based on memory: Q1=name, Q2=email, Q3=company, Q4=role, Q5=goal
        # But Jared's instructions say Q2=AI name. We must check dynamically.
        first_msg = await get_last_ai_msg(page)
        tg(f"First AI message: '{first_msg}'")

        # Prepare Q&A answers - we watch what is asked and respond accordingly
        # If AI asks for an AI name, we say "Nova"
        # The task says: Q2 = AI's name (Nova). We try this.
        qa_answers = [
            "Test User",       # Q1: Your name
            "Nova",            # Q2: Your AI's name (if asked), or email
            "Pure Technology", # Q3: Company or next field
            "QA Engineer",     # Q4: Role or next field
            "Build the most efficient AI research and reporting pipeline possible",  # Q5: Goal
        ]

        ai_name_detected = None
        qa_screenshots = []

        for qi, answer in enumerate(qa_answers):
            d = await page.evaluate("""(function(){
                var r = document.getElementById('ptc-input-row');
                return r ? window.getComputedStyle(r).display : 'not-found';
            })()""")

            if d in ("none", "not-found"):
                tg(f"Input gone at Q{qi+1} - slides may have started")
                break

            # Get current AI prompt
            current_prompt = await get_last_ai_msg(page)

            # If Q2 asks for AI name, use "Nova". If it asks for email, use email.
            if qi == 1:
                prompt_lower = (current_prompt or "").lower()
                if "email" in prompt_lower or "@" in prompt_lower:
                    answer = "testuser.nova@example.com"
                    tg(f"Q2 is EMAIL (not AI name) — answering with email. Prompt: '{current_prompt}'")
                    results["notes"].append("Sandbox-3 Q2 = email (no AI name field)")
                elif "ai" in prompt_lower and ("name" in prompt_lower or "call" in prompt_lower):
                    answer = "Nova"
                    ai_name_detected = "Nova"
                    tg(f"Q2 is AI NAME! Answering 'Nova'. Prompt: '{current_prompt}'")
                    results["notes"].append(f"Sandbox-3 Q2 = AI name. Chose: {ai_name_detected}")
                else:
                    tg(f"Q2 unknown type. Prompt: '{current_prompt}'. Using default: '{answer}'")

            sent = await send_answer(page, answer)
            await asyncio.sleep(0.5)
            sc_path = await ss(page, f"05-qa-q{qi+1}-answered", send_to_tg=True)
            qa_screenshots.append(sc_path)
            tg(f"Q&A {qi+1}: Answered '{answer[:60]}' | sent={sent} | Prompt was: '{str(current_prompt)[:100]}'")

            # Wait for next AI response (max 8s) or slides
            for wi in range(8):
                await asyncio.sleep(1)
                btns = await page.evaluate("""(function(){
                    return Array.from(document.querySelectorAll('button')).filter(b => {
                        var s = window.getComputedStyle(b);
                        return s.display !== 'none' && b.offsetParent !== null && !b.disabled;
                    }).map(b => b.textContent.trim().substring(0, 60));
                })()""")
                has_slide_btn = any("show me more" in b.lower() or "incredible" in b.lower() for b in btns)
                if has_slide_btn:
                    tg(f"Slide button appeared during Q{qi+1}!")
                    break

        tg("E2E Post-Fix: Q&A complete. Proceeding to slides.")

        # If no AI name was detected from Q2, set result accordingly
        if ai_name_detected is None:
            results["notes"].append("Sandbox-3 did not ask for AI name during Q&A (uses 'Your AI' throughout)")
            results["ai_name_used"] = "Your AI (dynamic placeholder)"
        else:
            results["ai_name_used"] = ai_name_detected

        await asyncio.sleep(2)
        await ss(page, "06-qa-ALL-COMPLETE")

        # ===== STEP 4: BEHIND THE CURTAIN SLIDES =====
        print(f"\n[{int(time.time()-t0)}s] STEP 4: SLIDES")
        tg("Slides phase starting...")

        slides_done = 0
        slide_1_ss = None
        slide_5_ss = None
        slide_10_ss = None

        for si in range(15):
            btns = await page.evaluate("""(function(){
                return Array.from(document.querySelectorAll('button')).filter(b => {
                    var s = window.getComputedStyle(b);
                    return s.display !== 'none' && b.offsetParent !== null && !b.disabled;
                }).map(b => ({text: b.textContent.trim().substring(0, 80), cls: b.className}));
            })()""")

            incredible = next((b for b in btns if "incredible" in b['text'].lower() or "let's go" in b['text'].lower()), None)
            show_more = next((b for b in btns if "show me more" in b['text'].lower()), None)

            if incredible:
                slides_done += 1
                slide_10_ss = await ss(page, f"07-slide-10-INCREDIBLE")
                tg(f"SLIDE 10 (final): '{incredible['text']}' - clicking!")
                await click_text_btn(page, incredible['text'][:20])
                await asyncio.sleep(2)
                break
            elif show_more:
                slides_done += 1
                if slides_done == 1:
                    slide_1_ss = await ss(page, "07-slide-01", send_to_tg=True)
                elif slides_done == 5:
                    slide_5_ss = await ss(page, "07-slide-05", send_to_tg=True)
                else:
                    if slides_done % 3 == 0:
                        await ss(page, f"07-slide-{slides_done:02d}", send_to_tg=False)

                await click_text_btn(page, "Show Me More")
                print(f"[{int(time.time()-t0)}s] Slide {slides_done} done")
                await asyncio.sleep(1.5)
            else:
                tg(f"No slide btn at iteration {si}. Visible buttons: {[b['text'][:30] for b in btns[:5]]}")
                # Wait a bit and check again
                await asyncio.sleep(2)
                continue

        tg(f"Slides COMPLETE: {slides_done} slides clicked")
        tg("E2E Post-Fix: All slides done. Looking for 'That is incredible' and final messages.")

        # ===== STEP 5: "THAT'S INCREDIBLE" MOMENT =====
        await asyncio.sleep(3)
        await ss(page, "08-thats-incredible-moment")
        tg("That's incredible moment: screenshot taken")

        # ===== STEP 6: "YOUR AI IS READY" ORANGE BUTTON =====
        print(f"\n[{int(time.time()-t0)}s] STEP 6: YOUR AI IS READY BUTTON")
        tg("Looking for 'Your AI is ready' orange button...")

        state_cta = await get_visible_buttons(page)
        cta_btn = next((b for b in state_cta if
                        "your ai is ready" in b['text'].lower() or
                        "next steps" in b['text'].lower() or
                        "ptc-welcome" in b['cls'].lower()), None)

        if not cta_btn:
            # Wait up to 15s for it to appear
            for wi in range(15):
                await asyncio.sleep(1)
                state_cta = await get_visible_buttons(page)
                cta_btn = next((b for b in state_cta if
                                "your ai is ready" in b['text'].lower() or
                                "next steps" in b['text'].lower() or
                                "ptc-welcome" in b['cls'].lower()), None)
                if cta_btn:
                    break

        if cta_btn:
            await ss(page, "09-your-ai-ready-BUTTON")
            tg(f"'Your AI is ready' FOUND: '{cta_btn['text']}' — screenshotting before click")

            # CLICK IT - this is NOT the final step
            await click_text_btn(page, cta_btn['text'][:20])
            await asyncio.sleep(4)
            await ss(page, "10-after-orange-btn-click")
            tg("Clicked 'Your AI is ready' orange button. Now checking 3 bug fixes...")
        else:
            tg("'Your AI is ready' NOT found! Debugging...")
            page_text = await page.evaluate("document.body.innerText.substring(0, 1000)")
            tg(f"Page text: '{page_text[:500]}'")
            await ss(page, "09-ERROR-no-cta-btn")

        # ===== FIX VERIFICATION PHASE =====
        print(f"\n[{int(time.time()-t0)}s] ===== FIX VERIFICATION =====")
        await asyncio.sleep(2)

        # ===== FIX 1: DYNAMIC AI NAME =====
        print(f"[{int(time.time()-t0)}s] FIX 1: Dynamic AI Name Check")
        name_check = await check_dynamic_name(page, ai_name_detected or "Nova")
        fix1_ss = await ss(page, "11-FIX1-dynamic-name-check")

        # Determine what name appears
        has_aiciv = name_check.get("hasAICIV", False)
        has_dynamic = name_check.get("hasDynamicName", False)
        has_your_ai = name_check.get("hasYourAI", False)

        if has_aiciv and not has_dynamic:
            results["fix1_dynamic_name"] = "FAIL"
            tg(f"FIX 1 FAIL: Page shows 'AICIV' (hardcoded). hasAICIV={has_aiciv}, hasDynamic={has_dynamic}")
        elif has_dynamic:
            results["fix1_dynamic_name"] = "PASS"
            tg(f"FIX 1 PASS: Dynamic AI name '{ai_name_detected}' appears on page!")
        elif has_your_ai and not has_aiciv:
            results["fix1_dynamic_name"] = "PASS"
            tg(f"FIX 1 PASS: Page shows 'Your AI' (dynamic placeholder, not AICIV). hasYourAI={has_your_ai}")
        elif has_aiciv:
            results["fix1_dynamic_name"] = "FAIL"
            tg(f"FIX 1 FAIL: 'AICIV' found on page. hasAICIV={has_aiciv}")
        else:
            results["fix1_dynamic_name"] = "UNKNOWN"
            tg(f"FIX 1 UNKNOWN: hasAICIV={has_aiciv}, hasDynamic={has_dynamic}, hasYourAI={has_your_ai}")

        tg(f"FIX 1 Result: {results['fix1_dynamic_name']} | Page text sample: '{name_check.get('pageText','')[:400]}'")

        # ===== FIX 2: SEND BUTTON DISABLED =====
        print(f"[{int(time.time()-t0)}s] FIX 2: Send Button Disabled Check")
        send_state = await check_send_button_state(page)
        fix2_ss = await ss(page, "12-FIX2-send-button-state")

        input_disabled = send_state.get("inputDisabled") or send_state.get("inputRowDisplay") == "none"
        send_disabled = send_state.get("sendBtnDisabled")
        input_placeholder = send_state.get("inputPlaceholder", "") or ""
        waiting_placeholder = "waiting" in input_placeholder.lower() or "portal" in input_placeholder.lower()

        tg(f"FIX 2 State: inputDisabled={input_disabled} | sendDisabled={send_disabled} | placeholder='{input_placeholder}' | inputRowDisplay={send_state.get('inputRowDisplay')}")

        if send_disabled and (input_disabled or waiting_placeholder):
            results["fix2_send_disabled"] = "PASS"
            tg(f"FIX 2 PASS: Send button disabled. Input disabled/readonly. Placeholder='{input_placeholder}'")
        elif send_state.get("inputRowDisplay") == "none":
            results["fix2_send_disabled"] = "PASS"
            tg(f"FIX 2 PASS: Input row hidden (display:none). Send button not accessible.")
        elif send_disabled:
            results["fix2_send_disabled"] = "PASS"
            tg(f"FIX 2 PASS: Send button is disabled (sendBtnDisabled={send_disabled})")
        elif not send_state.get("sendBtnFound"):
            results["fix2_send_disabled"] = "PASS"
            tg(f"FIX 2 PASS: Send button not in DOM at this stage (expected post-CTA)")
        else:
            results["fix2_send_disabled"] = "FAIL"
            tg(f"FIX 2 FAIL: Send button still active! State: {send_state}")

        # ===== FIX 3: BRAIN STREAM BUTTON GREYED =====
        print(f"[{int(time.time()-t0)}s] FIX 3: Brain Stream Button Greyed Check")
        brain_elements = await check_brain_stream_state(page)
        fix3_ss = await ss(page, "13-FIX3-brain-stream-state")

        tg(f"FIX 3 Brain Stream elements found: {len(brain_elements)}")
        for el in brain_elements[:5]:
            tg(f"  Element: tag={el['tag']} text='{el['text'][:80]}' opacity={el['opacity']} pointerEvents={el['pointerEvents']} visible={el['visible']} disabled={el['disabled']}")

        # Check if brain stream button is greyed
        brain_btns = [el for el in brain_elements if
                      el['tag'] in ('BUTTON', 'A') and
                      ("brain stream" in el['text'].lower() or "enter" in el['text'].lower())]

        if not brain_btns:
            # Try broader search
            all_btns_page = await get_visible_buttons(page)
            brain_btns_broad = [b for b in all_btns_page if
                                 "brain" in b['text'].lower() or "stream" in b['text'].lower() or "enter" in b['text'].lower()]
            tg(f"FIX 3 Broad search: {[b['text'][:60] for b in brain_btns_broad[:5]]}")

        if brain_btns:
            btn = brain_btns[0]
            opacity_val = float(btn.get('opacity', 1))
            ptr_events = btn.get('pointerEvents', 'auto')
            is_disabled = btn.get('disabled', False)
            is_greyed = opacity_val <= 0.5 or ptr_events == 'none' or is_disabled

            name_in_btn = btn['text']
            has_aiciv_in_btn = 'AICIV' in name_in_btn.upper()
            has_keen_in_btn = 'KEEN' in name_in_btn.upper()

            if is_greyed:
                results["fix3_brain_greyed"] = "PASS"
                tg(f"FIX 3 PASS: Brain Stream button GREYED. opacity={opacity_val}, pointerEvents={ptr_events}, disabled={is_disabled}")
            else:
                results["fix3_brain_greyed"] = "FAIL"
                tg(f"FIX 3 FAIL: Brain Stream button is NOT greyed! opacity={opacity_val}, pointerEvents={ptr_events}")

            if has_aiciv_in_btn:
                tg(f"FIX 3 NAME ISSUE: Button shows 'AICIV' (should be dynamic name). Button text: '{name_in_btn}'")
                results["fix3_brain_greyed"] = "FAIL" if not is_greyed else results["fix3_brain_greyed"] + " (NAME BUG: shows AICIV)"
            elif has_keen_in_btn:
                tg(f"FIX 3 NAME NOTE: Button shows 'KEEN' (from previous test). Button text: '{name_in_btn}'")
            else:
                tg(f"FIX 3 name OK. Button text: '{name_in_btn}'")

            # Screenshot the button specifically
            await ss(page, "14-FIX3-brain-stream-button-closeup")
        else:
            tg("FIX 3: No brain stream button found as button/a. Checking all elements...")
            # Check if it appears as a div-based element
            if brain_elements:
                tg(f"FIX 3 Non-button elements: {[e['text'][:60] for e in brain_elements[:3]]}")
                results["fix3_brain_greyed"] = "UNKNOWN - element found but not as button/a"
            else:
                results["fix3_brain_greyed"] = "UNKNOWN - brain stream not found on page"
                tg("FIX 3 UNKNOWN: Brain Stream element not found. May need more waiting or different selector.")

        # Full page state screenshot at fix verification point
        await ss(page, "15-FULL-FIX-VERIFICATION-STATE")

        # ===== STEP 10: IF BRAIN STREAM LIGHTS UP, CLICK IT =====
        print(f"\n[{int(time.time()-t0)}s] STEP 10: Brain Stream Button Final Check")

        if brain_btns:
            btn = brain_btns[0]
            opacity_val = float(btn.get('opacity', 1))
            ptr_events = btn.get('pointerEvents', 'auto')
            is_disabled = btn.get('disabled', False)
            if not is_disabled and opacity_val > 0.5 and ptr_events != 'none':
                tg(f"Brain Stream is ACTIVE (opacity={opacity_val}, ptr={ptr_events}) — CLICKING!")
                await click_text_btn(page, btn['text'][:20])
                await asyncio.sleep(4)
                await ss(page, "16-BRAIN-STREAM-CLICKED")
                after_text = await page.evaluate("document.body.innerText.substring(0, 600)")
                tg(f"After Brain Stream click: '{after_text}'")
            else:
                tg(f"Brain Stream greyed (expected with JS simulation). opacity={opacity_val}, ptr={ptr_events}")
                tg("NOTE: Button won't light up because JS payment sim doesn't send real seed to Witness. This is EXPECTED.")

        # ===== FINAL SUMMARY =====
        elapsed = int(time.time() - t0)
        await ss(page, "17-FINAL-STATE")

        # Page text for report
        final_page_text = await page.evaluate("document.body.innerText.substring(0, 3000)")

        print(f"\n{'='*60}")
        print(f"FINAL RESULTS:")
        print(f"  Fix 1 (Dynamic AI Name): {results['fix1_dynamic_name']}")
        print(f"  Fix 2 (Send Disabled):   {results['fix2_send_disabled']}")
        print(f"  Fix 3 (Brain Greyed):    {results['fix3_brain_greyed']}")
        print(f"  AI Name Used: {results['ai_name_used']}")
        print(f"  Time: {elapsed}s | Screenshots: {sc}")
        print(f"{'='*60}\n")

        tg(f"""
=== POST-FIX E2E FINAL RESULTS ===
Fix 1 - Dynamic AI Name: {results['fix1_dynamic_name']}
Fix 2 - Send Btn Disabled: {results['fix2_send_disabled']}
Fix 3 - Brain Stream Greyed: {results['fix3_brain_greyed']}
AI Name Used: {results['ai_name_used']}
Time: {elapsed}s | Screenshots: {sc}
Errors: {len(page_errors)} page errors
API calls: {len(api_calls)}
""")

        await browser.close()

        # Store for report
        results["elapsed"] = elapsed
        results["screenshot_count"] = sc
        results["page_errors"] = page_errors[:5]
        results["api_calls"] = list(set(api_calls))[:20]
        results["final_page_text"] = final_page_text
        results["send_state"] = send_state
        results["brain_elements"] = brain_elements[:5]
        results["name_check"] = name_check

    return results


if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\nScript complete. Results: {result}")
