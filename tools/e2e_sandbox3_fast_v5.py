"""
E2E sandbox3 FAST v5 - Complete flow with minimal waits
Key insight from screenshot 017: "Show Me More" button appears DURING goal Q step
Must handle both goal answer AND slides simultaneously
"""

import asyncio
import os
import time
import subprocess
from playwright.async_api import async_playwright

PAGE_URL = "https://purebrain.ai/pay-test-sandbox-3/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-e2e-full-20260304"
TG_SEND = "/home/jared/projects/AI-CIV/aether/tools/tg_send.sh"

sc = 29  # Continue numbering from v4

def tg(msg):
    try:
        subprocess.run([TG_SEND, str(msg)[:4000]], timeout=10, capture_output=True)
        print(f"[TG] {str(msg)[:200]}")
    except Exception as e:
        print(f"[TG ERR] {e}")

def tg_photo(path, cap):
    try:
        subprocess.run([TG_SEND, "--photo", path, str(cap)[:200]], timeout=15, capture_output=True)
    except Exception as e:
        print(f"[TG PHOTO ERR] {e}")

async def ss(page, label, send_tg=True):
    global sc
    sc += 1
    fn = f"{sc:03d}-{label}.png"
    path = os.path.join(SCREENSHOT_DIR, fn)
    try:
        await page.screenshot(path=path)
        print(f"[SS] {fn}")
        if send_tg:
            tg_photo(path, f"{sc}: {label}")
    except Exception as e:
        print(f"[SS ERR] {label}: {e}")
    return path

async def wait_input(page, timeout=60):
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
        except: pass
        await asyncio.sleep(0.5)
    return False

async def get_msgs(page):
    try:
        return await page.evaluate("""(function(){
            var els = document.querySelectorAll('.ptc-msg--ai, .ptc-message--ai');
            return Array.from(els).map(e => e.textContent.trim()).filter(t => t.length > 1);
        })()""")
    except: return []

async def send_ptc(page, text):
    for sel in ["#ptc-input", "textarea.ptc-input"]:
        try:
            ta = await page.query_selector(sel)
            if ta and await ta.is_visible():
                await ta.click()
                await asyncio.sleep(0.1)
                await ta.fill(text)
                await asyncio.sleep(0.1)
                for bsel in ["#ptc-send-btn", ".ptc-send-btn"]:
                    btn = await page.query_selector(bsel)
                    if btn and await btn.is_visible():
                        await btn.click()
                        return True
                await ta.press("Enter")
                return True
        except Exception as e:
            pass
    return False

async def click_btn_by_text(page, text_fragment):
    """Click button containing text."""
    for strategy in [
        f"button:has-text('{text_fragment[:20]}')",
        f"[class*='btn']:has-text('{text_fragment[:20]}')"
    ]:
        try:
            btn = await page.query_selector(strategy)
            if btn and await btn.is_visible():
                await btn.click()
                return True
        except: pass
    # JS fallback
    result = await page.evaluate(f"""(function(){{
        var els = Array.from(document.querySelectorAll('button, a, span[onclick]'));
        var btn = els.find(el => el.textContent.includes({repr(text_fragment[:20])}) && window.getComputedStyle(el).display !== 'none');
        if (btn) {{ btn.click(); return true; }}
        return false;
    }})()""")
    return result

async def get_state(page):
    """Get comprehensive page state."""
    return await page.evaluate("""(function(){
        var btns = Array.from(document.querySelectorAll('button, a')).filter(el => {
            var s = window.getComputedStyle(el);
            return s.display !== 'none' && el.offsetParent !== null && el.textContent.trim().length > 0;
        }).map(el => ({text: el.textContent.trim().substring(0,80), cls: el.className.substring(0,50), disabled: el.disabled||false}));

        var msgs = Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-message--ai')).map(e => e.textContent.trim());
        var input_display = (function(){
            var r = document.getElementById('ptc-input-row');
            return r ? window.getComputedStyle(r).display : 'not-found';
        })();
        var container = document.getElementById('pay-test-post-payment');
        var portal = document.querySelector('.portal-vortex, #portal-vortex');

        return {
            buttons: btns,
            msg_count: msgs.length,
            last_msg: msgs.length > 0 ? msgs[msgs.length-1].substring(0, 100) : null,
            input_display: input_display,
            page_text: document.body.innerText.substring(0, 1000),
            container_children: container ? container.children.length : 0,
            portal_text: portal ? portal.textContent.trim().substring(0, 200) : null,
            portal_children: portal ? portal.children.length : 0
        };
    })()""")

async def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    tg("=== E2E v5 FAST: Starting complete fresh run ===")

    page_errors = []
    api_calls = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx.new_page()

        page.on("pageerror", lambda e: page_errors.append(str(e)))
        async def on_resp(r):
            if "purebrain.ai" in r.url or "api.purebrain" in r.url:
                api_calls.append(f"{r.status} {r.url}")
        page.on("response", on_resp)

        # ===========================
        # PHASE 1: LOAD + PASSWORD
        # ===========================
        tg("Phase 1: Load page + password")
        await page.goto(PAGE_URL, wait_until="load", timeout=30000)
        await asyncio.sleep(2)

        pw = await page.query_selector("input[type='password'], input[name='post_password']")
        if pw:
            await pw.fill(PAGE_PASSWORD)
            sub = await page.query_selector("input[type='submit'], button[type='submit']")
            if sub: await sub.click()
            else: await pw.press("Enter")
            try: await page.wait_for_load_state("load", timeout=8000)
            except: pass
            await asyncio.sleep(4)
            tg("Phase 1: Password submitted")
        else:
            tg("Phase 1: No password form")

        await ss(page, "phase1-loaded")

        # ===========================
        # PHASE 2: TRIGGER PAYMENT
        # ===========================
        tg("Phase 2: Triggering payment simulation")

        funcs = await page.evaluate("""(function(){
            return {
                onPaymentComplete: typeof window.onPaymentComplete,
                launchPostPaymentFlow: typeof window.launchPostPaymentFlow,
                sanitizeText: typeof window.sanitizeText
            };
        })()""")
        print(f"[2] Functions: {funcs}")
        tg(f"Window functions: {funcs}")

        order_id = f"E2E-FAST-20260304-{int(time.time())}"
        if funcs.get("onPaymentComplete") == "function":
            await page.evaluate(f"window.onPaymentComplete('Awakened', '{order_id}', {{}})")
            tg(f"Payment triggered: orderId={order_id}")
        else:
            tg("ERROR: onPaymentComplete not found!")
            for e in page_errors: tg(f"Error: {e[:100]}")
            await browser.close()
            return

        await asyncio.sleep(5)
        await ss(page, "phase2-payment-triggered")

        # ===========================
        # PHASE 3: WAIT FOR CHATBOX
        # ===========================
        tg("Phase 3: Waiting for chatbox...")
        if not await wait_input(page, 30):
            tg("ERROR: Chatbox not active after 30s")
            for e in page_errors[-3:]: tg(f"Error: {e[:100]}")
            await ss(page, "phase3-chatbox-not-active")
            await browser.close()
            return

        await ss(page, "phase3-chatbox-ACTIVE")
        await asyncio.sleep(2)
        state = await get_state(page)
        tg(f"Chatbox active! First msg: '{state['last_msg']}'")

        # ===========================
        # PHASE 4: Q&A SEQUENCE
        # ===========================
        tg("Phase 4: Q&A sequence")

        qa_answers = [
            ("Alex Carter", "name"),
            ("alex.carter.test@example.com", "email"),
            ("Frontier AI Ventures", "company"),
            ("CTO", "role"),
        ]

        for answer, label in qa_answers:
            active = await wait_input(page, 15)
            if not active:
                state = await get_state(page)
                tg(f"Input gone at {label}. State: {state['buttons'][:5]}")
                await ss(page, f"qa-{label}-input-gone")
                break

            await send_ptc(page, answer)
            tg(f"Q&A {label}: sent '{answer}'")
            await asyncio.sleep(1)
            await ss(page, f"qa-{label}-sent")

            # Quick wait for AI (5s max)
            prev_count = len(await get_msgs(page))
            for _ in range(5):
                await asyncio.sleep(1)
                new_msgs = await get_msgs(page)
                if len(new_msgs) > prev_count:
                    tg(f"AI after {label}: '{new_msgs[-1][:100]}'")
                    break

        # After role, goal question should appear + "Show Me More" may appear simultaneously
        # Check current state
        await asyncio.sleep(2)
        state_after_role = await get_state(page)
        print(f"[4] After role - buttons: {state_after_role['buttons']}")
        print(f"[4] After role - last AI: {state_after_role['last_msg']}")
        tg(f"After Role - buttons: {[b['text'][:40] for b in state_after_role['buttons'][:8]]}")
        tg(f"After Role - last AI msg: '{state_after_role['last_msg']}'")

        await ss(page, "qa-role-response-state")

        # Send goal if input is active
        goal_answer = "Automate our entire research pipeline and reporting so our leadership team can focus on strategy instead of manual data work"

        # Check for "Show Me More" button - it may have appeared with or before goal
        has_show_more = any("show me more" in b['text'].lower() for b in state_after_role['buttons'])
        input_active = state_after_role['input_display'] not in ('none', 'not-found')

        if input_active and not has_show_more:
            # Send goal first
            await send_ptc(page, goal_answer)
            tg(f"Q&A goal: sent")
            await asyncio.sleep(1)
            await ss(page, "qa-goal-sent")

            # Wait for AI response + possible Show Me More
            for wait_i in range(15):
                await asyncio.sleep(1)
                state_check = await get_state(page)
                has_show_more = any("show me more" in b['text'].lower() for b in state_check['buttons'])
                if has_show_more:
                    tg(f"Show Me More appeared after goal! Last AI: '{state_check['last_msg']}'")
                    break

            await ss(page, "qa-goal-ai-response")
        elif has_show_more:
            tg("Show Me More appeared before goal was sent - sending goal and proceeding")
            # Send goal if input is still available
            if input_active:
                await send_ptc(page, goal_answer)
                await asyncio.sleep(2)
                await ss(page, "qa-goal-sent-with-slides-visible")
        else:
            tg(f"Unusual state at goal: input={input_active}, show_more={has_show_more}")

        # Final Q&A state
        final_qa_state = await get_state(page)
        tg(f"Q&A complete. Buttons: {[b['text'][:40] for b in final_qa_state['buttons'][:8]]}")
        tg(f"Msg count: {final_qa_state['msg_count']}")

        # ===========================
        # PHASE 5: SLIDES
        # ===========================
        tg("Phase 5: Behind the Curtain SLIDES")
        await asyncio.sleep(2)
        await ss(page, "phase5-slides-start")

        slides_done = 0
        for slide_i in range(15):
            state = await get_state(page)
            print(f"[SLIDE {slide_i}] buttons: {[(b['text'][:40], b['disabled']) for b in state['buttons']]}")

            show_more = None
            incredible = None
            for b in state['buttons']:
                t = b['text'].lower()
                if "show me more" in t and not b['disabled']:
                    show_more = b
                if ("incredible" in t or "let's go" in t) and not b['disabled']:
                    incredible = b

            if incredible:
                # Final slide button
                tg(f"FINAL SLIDE: '{incredible['text']}' - clicking!")
                await click_btn_by_text(page, incredible['text'][:20])
                slides_done += 1
                await asyncio.sleep(2)
                await ss(page, "slides-final-incredible")
                tg("Clicked 'That's incredible — let's go'!")
                break
            elif show_more:
                tg(f"Slide {slide_i + 1}: '{show_more['text']}'")
                await click_btn_by_text(page, show_more['text'][:20])
                slides_done += 1
                await asyncio.sleep(1.5)
                await ss(page, f"slide-{slides_done:02d}", send_tg=False)
            else:
                tg(f"No slide button at step {slide_i}. Current buttons: {[b['text'][:30] for b in state['buttons'][:5]]}")
                break

        tg(f"Slides clicked: {slides_done}")

        # ===========================
        # PHASE 6: YOUR AI IS READY
        # ===========================
        tg("Phase 6: Looking for 'Your AI is ready' button...")
        await asyncio.sleep(3)

        state_cta = await get_state(page)
        tg(f"CTA phase buttons: {[b['text'][:50] for b in state_cta['buttons'][:8]]}")
        tg(f"Page text at CTA: '{state_cta['page_text'][:400]}'")
        await ss(page, "phase6-your-ai-ready-search")

        # Find button
        cta_btn = None
        for b in state_cta['buttons']:
            t = b['text'].lower()
            if "your ai is ready" in t or "next steps" in t or "ptc-welcome" in b['cls'].lower():
                cta_btn = b
                break

        if cta_btn:
            tg(f"Found 'Your AI is ready': '{cta_btn['text']}' - CLICKING!")
            await ss(page, "phase6-your-ai-ready-FOUND")
            await click_btn_by_text(page, cta_btn['text'][:20])
            await asyncio.sleep(4)
            await ss(page, "phase6-after-your-ai-click")
            tg("Clicked 'Your AI is ready' - checking what follows...")
        else:
            tg("'Your AI is ready' not found! Checking page state...")
            tg(f"Page text: '{state_cta['page_text'][:600]}'")
            await ss(page, "phase6-your-ai-NOT-FOUND")

            # Try scrolling down
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)
            await ss(page, "phase6-scrolled-down")
            state_scrolled = await get_state(page)
            tg(f"After scroll - buttons: {[b['text'][:40] for b in state_scrolled['buttons'][:8]]}")

            # Try to click any CTA
            for b in state_scrolled['buttons']:
                t = b['text'].lower()
                if any(p in t for p in ["your ai", "ready", "next steps", "begin", "enter"]):
                    tg(f"Clicking possible CTA: '{b['text']}'")
                    await click_btn_by_text(page, b['text'][:20])
                    await asyncio.sleep(3)
                    break

        # Check for more messages/interactions after CTA
        await asyncio.sleep(3)
        state_post_cta = await get_state(page)
        tg(f"Post-CTA state: {[b['text'][:50] for b in state_post_cta['buttons'][:8]]}")
        tg(f"Post-CTA page: '{state_post_cta['page_text'][:500]}'")

        # Click any remaining buttons
        for b in state_post_cta['buttons']:
            t = b['text'].lower()
            if not b['disabled'] and any(p in t for p in ["continue", "begin", "enter", "stream", "brain", "next"]):
                tg(f"Clicking post-CTA: '{b['text']}'")
                await click_btn_by_text(page, b['text'][:20])
                await asyncio.sleep(3)
                await ss(page, f"post-cta-{b['text'][:15].replace(' ','-').lower()}")

        # ===========================
        # PHASE 7: FINAL STATE
        # ===========================
        tg("=== PHASE 7: ABSOLUTE FINAL STATE - BRAIN STREAM ===")
        await asyncio.sleep(5)
        await ss(page, "PHASE7-FINAL-STATE")

        final = await page.evaluate("""(function(){
            // Deep search for brain stream button
            var brain_candidates = [];
            var all_els = Array.from(document.querySelectorAll('*'));

            all_els.forEach(el => {
                var t = el.textContent.trim();
                var tupper = t.toUpperCase();
                if (t.length > 2 && t.length < 200) {
                    if (tupper.includes('BRAIN STREAM') || tupper.includes('ENTER') ||
                        (el.tagName === 'BUTTON' || el.tagName === 'A') && tupper.includes('BRAIN')) {
                        var s = window.getComputedStyle(el);
                        brain_candidates.push({
                            tag: el.tagName,
                            text: t.substring(0, 100),
                            cls: el.className.substring(0, 60),
                            id: el.id,
                            display: s.display,
                            opacity: s.opacity,
                            pointerEvents: s.pointerEvents,
                            disabled: el.disabled || false,
                            visible: s.display !== 'none' && el.offsetParent !== null
                        });
                    }
                }
            });

            // Portal div
            var portal = document.querySelector('.portal-vortex, [class*="portal-vortex"]');
            var portal_data = null;
            if (portal) {
                portal_data = {
                    cls: portal.className,
                    text: portal.textContent.trim().substring(0, 300),
                    children: portal.children.length,
                    display: window.getComputedStyle(portal).display,
                    childDetails: Array.from(portal.children).map(c => ({
                        tag: c.tagName, cls: c.className.substring(0,40),
                        text: c.textContent.trim().substring(0,80),
                        display: window.getComputedStyle(c).display
                    }))
                };
            }

            // PTC container final state
            var ptc_el = document.getElementById('pay-test-post-payment');
            var ptc_data = null;
            if (ptc_el) {
                ptc_data = {
                    children: ptc_el.children.length,
                    display: window.getComputedStyle(ptc_el).display,
                    text: ptc_el.textContent.trim().substring(0, 800)
                };
            }

            return {
                brain_candidates: brain_candidates,
                portal: portal_data,
                ptc: ptc_data,
                page_text: document.body.innerText,
                all_buttons: Array.from(document.querySelectorAll('button, a')).filter(el => {
                    var s = window.getComputedStyle(el);
                    return s.display !== 'none' && el.offsetParent !== null;
                }).map(el => ({
                    text: el.textContent.trim().substring(0,80),
                    cls: el.className.substring(0,50),
                    disabled: el.disabled || false,
                    opacity: window.getComputedStyle(el).opacity
                }))
            };
        })()""")

        # Report everything
        print(f"\n[FINAL] Brain candidates: {final['brain_candidates']}")
        print(f"\n[FINAL] Portal: {final['portal']}")
        print(f"\n[FINAL] PTC: {final['ptc']}")
        print(f"\n[FINAL] All buttons: {final['all_buttons']}")
        print(f"\n[FINAL] Full page text:\n{final['page_text'][:1500]}")

        tg("=== FINAL STATE REPORT ===")
        tg(f"Brain Stream candidates: {final['brain_candidates'][:5]}")
        tg(f"Portal: {final['portal']}")
        tg(f"PTC full text: '{final['ptc']['text'][:600] if final['ptc'] else 'NOT FOUND'}'")
        tg(f"All visible buttons: {[(b['text'][:40], b['disabled'], b['opacity']) for b in final['all_buttons'][:10]]}")
        tg(f"Full page text: '{final['page_text'][:1000]}'")

        # Brain button analysis
        brain_btns = final['brain_candidates']
        if brain_btns:
            tg(f"BRAIN BUTTONS FOUND ({len(brain_btns)}):")
            for bb in brain_btns:
                is_disabled = bb['disabled'] or bb['opacity'] in ('0', '0.3', '0.5')
                tg(f"  '{bb['text']}' | visible={bb['visible']} | disabled={bb['disabled']} | opacity={bb['opacity']} | ptr={bb['pointerEvents']}")

            # Try to click active ones
            active = [bb for bb in brain_btns if bb['visible'] and not bb['disabled'] and bb['opacity'] not in ('0', '0.3', '0.5')]
            if active:
                tg(f"BRAIN STREAM IS ACTIVE - CLICKING: '{active[0]['text']}'")
                await page.evaluate("""(function(){
                    var all = Array.from(document.querySelectorAll('*'));
                    for(var el of all) {
                        var t = el.textContent.trim();
                        var s = window.getComputedStyle(el);
                        if (s.display !== 'none' && el.offsetParent && !el.disabled &&
                            (t.toUpperCase().includes('BRAIN STREAM') || (el.tagName === 'BUTTON' && t.includes('ENTER')))) {
                            el.click();
                            return;
                        }
                    }
                })()""")
                await asyncio.sleep(4)
                await ss(page, "brain-stream-CLICKED")
                after = await page.evaluate("document.body.innerText")
                tg(f"After Brain Stream click: '{after[:600]}'")
            else:
                tg("Brain Stream GREYED/DISABLED - user must wait for system activation. This is EXPECTED FINAL STATE.")
        else:
            tg("No brain stream button found.")

        # API call analysis
        tg(f"API calls ({len(api_calls)}): {list(set(api_calls))[:10]}")

        # Error report
        if page_errors:
            tg(f"Page errors ({len(page_errors)}): {page_errors[:3]}")

        await ss(page, "ABSOLUTE-FINAL")
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)
        await ss(page, "final-top-view")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(0.5)
        await ss(page, "final-bottom-view")

        tg(f"=== E2E v5 COMPLETE. Screenshots: {sc}. Dir: {SCREENSHOT_DIR} ===")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
