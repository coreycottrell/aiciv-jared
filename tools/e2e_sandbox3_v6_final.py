"""
E2E sandbox3 v6 FINAL - Optimized for speed, no waiting for AI responses
Just fire and move to next step quickly.
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

sc = 36

def tg(msg):
    try:
        subprocess.run([TG_SEND, str(msg)[:4000]], timeout=10, capture_output=True)
        print(f"[TG] {str(msg)[:200]}")
    except: pass

def tg_photo(path, cap):
    try:
        subprocess.run([TG_SEND, "--photo", path, str(cap)[:200]], timeout=15, capture_output=True)
    except: pass

async def ss(page, label, send=True):
    global sc
    sc += 1
    fn = f"{sc:03d}-{label}.png"
    path = os.path.join(SCREENSHOT_DIR, fn)
    try:
        await page.screenshot(path=path)
        print(f"[SS] {fn}")
        if send:
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

async def send_ptc(page, text):
    for sel in ["#ptc-input", "textarea.ptc-input"]:
        try:
            ta = await page.query_selector(sel)
            if ta and await ta.is_visible():
                await ta.fill(text)
                await asyncio.sleep(0.1)
                for bsel in ["#ptc-send-btn", ".ptc-send-btn"]:
                    btn = await page.query_selector(bsel)
                    if btn and await btn.is_visible():
                        await btn.click()
                        return True
                await ta.press("Enter")
                return True
        except: pass
    return False

async def get_state(page):
    return await page.evaluate("""(function(){
        var btns = Array.from(document.querySelectorAll('button, a')).filter(el => {
            var s = window.getComputedStyle(el);
            return s.display !== 'none' && el.offsetParent !== null && el.textContent.trim().length > 0;
        }).map(el => ({text: el.textContent.trim().substring(0,100), cls: el.className.substring(0,50), disabled: el.disabled||false, opacity: window.getComputedStyle(el).opacity}));
        var msgs = Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-message--ai')).map(e => e.textContent.trim());
        var input_d = (function(){
            var r = document.getElementById('ptc-input-row');
            return r ? window.getComputedStyle(r).display : 'not-found';
        })();
        return {
            buttons: btns,
            msg_count: msgs.length,
            last_msg: msgs.length > 0 ? msgs[msgs.length-1].substring(0,150) : null,
            input_display: input_d,
            page_text: document.body.innerText.substring(0, 1500)
        };
    })()""")

async def click_text(page, text):
    result = await page.evaluate(f"""(function(){{
        var els = Array.from(document.querySelectorAll('button, a'));
        var el = els.find(e => e.textContent.trim().toLowerCase().includes({repr(text.lower()[:30])}) && window.getComputedStyle(e).display !== 'none' && !e.disabled);
        if (el) {{ el.click(); return el.textContent.trim().substring(0,60); }}
        return null;
    }})()""")
    return result

async def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    tg("=== E2E v6 FINAL: Fast complete run ===")
    t0 = time.time()

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

        # LOAD + PASSWORD
        print(f"[{int(time.time()-t0)}s] Loading page...")
        await page.goto(PAGE_URL, wait_until="load", timeout=30000)
        await asyncio.sleep(2)

        pw = await page.query_selector("input[type='password'], input[name='post_password']")
        if pw:
            await pw.fill(PAGE_PASSWORD)
            sub = await page.query_selector("input[type='submit']")
            if sub: await sub.click()
            else: await pw.press("Enter")
            try: await page.wait_for_load_state("load", timeout=8000)
            except: pass
            await asyncio.sleep(4)

        print(f"[{int(time.time()-t0)}s] Password done. Triggering payment...")
        await ss(page, "loaded-pre-payment")

        # CHECK PAYPAL STATE BEFORE SIMULATION
        paypal_state = await page.evaluate("""(function(){
            var frames = [];
            // Can't access frames here, but can check DOM
            var iframes = Array.from(document.querySelectorAll('iframe')).map(f => ({
                src: f.src.substring(0, 100),
                name: f.name,
                w: f.offsetWidth,
                h: f.offsetHeight
            }));
            var ppContainers = Array.from(document.querySelectorAll('[id*="paypal"],[class*="paypal"]')).map(e => ({
                id: e.id, cls: e.className.substring(0,50), w: e.offsetWidth, h: e.offsetHeight, children: e.children.length
            }));
            return {iframes: iframes, ppContainers: ppContainers, bodyText: document.body.innerText.substring(0, 300)};
        })()""")
        print(f"[{int(time.time()-t0)}s] PayPal state: {paypal_state}")
        tg(f"PayPal state: iframes={paypal_state['iframes'][:3]}, containers={paypal_state['ppContainers'][:3]}")
        tg(f"Page body: '{paypal_state['bodyText'][:200]}'")

        # PAYMENT TRIGGER
        funcs = await page.evaluate("""(function(){
            return {
                onPaymentComplete: typeof window.onPaymentComplete,
                launchPostPaymentFlow: typeof window.launchPostPaymentFlow,
                sanitizeText: typeof window.sanitizeText
            };
        })()""")
        print(f"[{int(time.time()-t0)}s] Functions: {funcs}")
        tg(f"Functions: {funcs}")

        order_id = f"E2E-V6-{int(time.time())}"
        if funcs.get("onPaymentComplete") == "function":
            await page.evaluate(f"window.onPaymentComplete('Awakened', '{order_id}', {{}})")
            tg(f"Payment triggered (orderId={order_id})")
        else:
            tg("ERROR: onPaymentComplete not found!")
            for e in page_errors[:3]: tg(f"Error: {e[:100]}")
            await browser.close()
            return

        await asyncio.sleep(5)
        print(f"[{int(time.time()-t0)}s] Waiting for chatbox...")

        # WAIT FOR INPUT - MAX 30s
        if not await wait_input(page, 30):
            tg("ERROR: Chatbox not active after 30s")
            state = await get_state(page)
            tg(f"State: {state['page_text'][:300]}")
            for e in page_errors[:3]: tg(f"Error: {e[:100]}")
            await ss(page, "chatbox-not-active-ERROR")
            await browser.close()
            return

        print(f"[{int(time.time()-t0)}s] Chatbox active! Starting Q&A...")
        await ss(page, "chatbox-ACTIVE")
        tg("Chatbox ACTIVE!")

        state = await get_state(page)
        tg(f"Opening message: '{state['last_msg']}'")

        # Q&A - send answers fast, no waiting for responses
        qa_pairs = [
            ("Alex Carter", "name"),
            ("alex.carter.test@example.com", "email"),
            ("Frontier AI Ventures", "company"),
            ("CTO", "role"),
            ("Automate our entire research pipeline and reporting system", "goal"),
        ]

        for answer, label in qa_pairs:
            # Check if input active (brief check)
            d = await page.evaluate("""(function(){
                var r = document.getElementById('ptc-input-row');
                return r ? window.getComputedStyle(r).display : 'not-found';
            })()""")

            if d in ("none", "not-found"):
                tg(f"Input gone at {label} - slides may have started")
                break

            sent = await send_ptc(page, answer)
            print(f"[{int(time.time()-t0)}s] Q&A {label}: sent={sent}")
            tg(f"Q&A {label}: '{answer[:60]}' sent={sent}")
            await ss(page, f"qa-{label}", send=False)

            # Wait for AI response - but ALSO check for Show Me More button
            # Only wait 8 seconds max
            for wi in range(8):
                await asyncio.sleep(1)
                # Check for slide buttons (which may appear mid-sequence)
                btns = await page.evaluate("""(function(){
                    return Array.from(document.querySelectorAll('button')).filter(b => {
                        var s = window.getComputedStyle(b);
                        return s.display !== 'none' && b.offsetParent !== null && !b.disabled;
                    }).map(b => b.textContent.trim().substring(0,60));
                })()""")
                has_show_more = any("show me more" in b.lower() or "incredible" in b.lower() for b in btns)
                if has_show_more:
                    print(f"[{int(time.time()-t0)}s] Slide button appeared at {label}!")
                    tg(f"SLIDE button appeared during {label}! Buttons: {btns}")
                    break

        print(f"[{int(time.time()-t0)}s] Q&A complete. Checking state...")
        await asyncio.sleep(3)
        await ss(page, "qa-ALL-COMPLETE")

        state_post_qa = await get_state(page)
        tg(f"Post Q&A - buttons: {[b['text'][:40] for b in state_post_qa['buttons'][:8]]}")
        tg(f"Post Q&A - last msg: '{state_post_qa['last_msg']}'")
        tg(f"Post Q&A - page text: '{state_post_qa['page_text'][:400]}'")

        # SLIDES PHASE - tight loop
        print(f"[{int(time.time()-t0)}s] SLIDES phase...")
        tg("SLIDES phase: clicking all slides...")

        slides_done = 0
        for si in range(15):
            state = await get_state(page)
            btns = state['buttons']

            incredible = next((b for b in btns if ("incredible" in b['text'].lower() or "let's go" in b['text'].lower()) and not b['disabled']), None)
            show_more = next((b for b in btns if "show me more" in b['text'].lower() and not b['disabled']), None)

            if incredible:
                tg(f"FINAL SLIDE: '{incredible['text']}' - clicking!")
                result = await click_text(page, incredible['text'][:20])
                slides_done += 1
                await asyncio.sleep(2)
                await ss(page, "slides-FINAL-incredible")
                tg(f"Clicked final slide! Result: {result}")
                break
            elif show_more:
                result = await click_text(page, "Show Me More")
                slides_done += 1
                print(f"[{int(time.time()-t0)}s] Slide {slides_done} clicked")
                await asyncio.sleep(1.5)
                if slides_done % 3 == 0:
                    await ss(page, f"slide-{slides_done:02d}", send=False)
            else:
                print(f"[{int(time.time()-t0)}s] No slide btn at {si}")
                tg(f"No slide btn at {si}. Buttons: {[b['text'][:30] for b in btns[:5]]}")
                break

        tg(f"Slides done: {slides_done}")
        print(f"[{int(time.time()-t0)}s] Slides complete: {slides_done}")

        # YOUR AI IS READY
        await asyncio.sleep(3)
        print(f"[{int(time.time()-t0)}s] Your AI Is Ready phase...")
        tg("Looking for 'Your AI is ready' button...")

        state_cta = await get_state(page)
        tg(f"CTA state - buttons: {[b['text'][:50] for b in state_cta['buttons'][:8]]}")
        tg(f"CTA state - page text: '{state_cta['page_text'][:600]}'")
        await ss(page, "your-ai-ready-search")

        cta_btn = next((b for b in state_cta['buttons'] if "your ai is ready" in b['text'].lower() or "next steps" in b['text'].lower() or "ptc-welcome" in b['cls'].lower()), None)

        if cta_btn:
            tg(f"'Your AI is ready' FOUND: '{cta_btn['text']}' - CLICKING (NOT the final step!)")
            await ss(page, "your-ai-ready-FOUND")
            await click_text(page, cta_btn['text'][:20])
            await asyncio.sleep(4)
            await ss(page, "after-your-ai-click")
            tg("Clicked 'Your AI is ready'. Proceeding to Brain Stream...")
        else:
            tg("'Your AI is ready' NOT found. Checking full page...")
            tg(f"All buttons: {[b['text'][:50] for b in state_cta['buttons']]}")

            # Try scrolling and looking
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)
            await ss(page, "your-ai-scrolled-bottom")
            state_s = await get_state(page)
            tg(f"After scroll - buttons: {[b['text'][:40] for b in state_s['buttons'][:8]]}")

            # Check if slides are still needed
            remaining_slides = [b for b in state_s['buttons'] if "show me more" in b['text'].lower() and not b['disabled']]
            if remaining_slides:
                tg(f"Still have slide buttons! {[b['text'] for b in remaining_slides]}")
                for b in remaining_slides[:5]:
                    await click_text(page, b['text'][:20])
                    await asyncio.sleep(1.5)
                    slides_done += 1

                # Try CTA again
                await asyncio.sleep(3)
                state_retry = await get_state(page)
                cta_btn2 = next((b for b in state_retry['buttons'] if "your ai is ready" in b['text'].lower() or "ptc-welcome" in b['cls'].lower()), None)
                if cta_btn2:
                    tg(f"CTA found after extra slides: '{cta_btn2['text']}'")
                    await click_text(page, cta_btn2['text'][:20])
                    await asyncio.sleep(4)
                    await ss(page, "your-ai-after-extra-slides")

        # POST-CTA interactions
        await asyncio.sleep(3)
        state_post_cta = await get_state(page)
        tg(f"Post-CTA: {[b['text'][:50] for b in state_post_cta['buttons'][:8]]}")
        tg(f"Post-CTA text: '{state_post_cta['page_text'][:500]}'")

        # Click any remaining flow buttons
        for b in state_post_cta['buttons']:
            t = b['text'].lower()
            if not b['disabled'] and any(p in t for p in ["continue", "begin", "enter", "stream", "brain", "start", "open"]):
                tg(f"Clicking post-CTA: '{b['text']}'")
                await click_text(page, b['text'][:20])
                await asyncio.sleep(3)
                await ss(page, f"post-cta-click")

        # FINAL STATE - BRAIN STREAM
        print(f"[{int(time.time()-t0)}s] FINAL STATE CHECK")
        tg("=== ABSOLUTE FINAL STATE: BRAIN STREAM ===")
        await asyncio.sleep(5)
        await ss(page, "FINAL-STATE")

        final = await page.evaluate("""(function(){
            // Search ALL elements for BRAIN STREAM
            var brain = [];
            document.querySelectorAll('*').forEach(el => {
                var t = el.textContent.trim();
                if (t.length > 0 && t.length < 200) {
                    var tu = t.toUpperCase();
                    if (tu.includes('BRAIN STREAM') || tu.includes('BRAIN STREAM') || el.className.includes('brain-stream')) {
                        var s = window.getComputedStyle(el);
                        brain.push({
                            tag: el.tagName, text: t.substring(0,100), cls: el.className.substring(0,60), id: el.id,
                            display: s.display, opacity: s.opacity, pointerEvents: s.pointerEvents,
                            disabled: el.disabled||false, visible: s.display !== 'none' && el.offsetParent !== null
                        });
                    }
                }
            });

            // Portal
            var portal = document.querySelector('.portal-vortex, #portal-vortex, [class*="portal"]');
            var portal_info = null;
            if (portal) {
                portal_info = {
                    cls: portal.className, text: portal.textContent.trim().substring(0,400),
                    children: portal.children.length, display: window.getComputedStyle(portal).display,
                    childDetails: Array.from(portal.children).map(c => ({tag: c.tagName, cls: c.className.substring(0,40), text: c.textContent.trim().substring(0,80)}))
                };
            }

            // PTC
            var ptc = document.getElementById('pay-test-post-payment');
            var ptc_info = null;
            if (ptc) {
                ptc_info = {children: ptc.children.length, display: window.getComputedStyle(ptc).display, text: ptc.textContent.trim().substring(0, 1000)};
            }

            return {
                brain: brain,
                portal: portal_info,
                ptc: ptc_info,
                all_btns: Array.from(document.querySelectorAll('button, a')).filter(el => {
                    var s = window.getComputedStyle(el);
                    return s.display !== 'none' && el.offsetParent !== null;
                }).map(el => ({text: el.textContent.trim().substring(0,80), cls: el.className.substring(0,50), disabled: el.disabled||false, opacity: window.getComputedStyle(el).opacity})),
                page_text: document.body.innerText
            };
        })()""")

        print(f"\n[FINAL] Brain: {final['brain']}")
        print(f"[FINAL] Portal: {final['portal']}")
        print(f"[FINAL] PTC: {final['ptc']}")
        print(f"[FINAL] All btns: {final['all_btns']}")
        print(f"[FINAL] Page text (1000):\n{final['page_text'][:1000]}")

        tg("=== FINAL STATE FULL REPORT ===")
        tg(f"Brain Stream elements: {final['brain'][:5]}")
        tg(f"Portal: {final['portal']}")
        tg(f"PTC children: {final['ptc']['children'] if final['ptc'] else 'NOT FOUND'}")
        tg(f"PTC text: '{final['ptc']['text'][:600] if final['ptc'] else 'N/A'}'")
        tg(f"All visible buttons: {[(b['text'][:40], b['disabled'], b['opacity']) for b in final['all_btns'][:10]]}")
        tg(f"Full page text: '{final['page_text'][:1000]}'")

        brain = final['brain']
        if brain:
            for bb in brain:
                tg(f"BRAIN: '{bb['text']}' | visible={bb['visible']} | disabled={bb['disabled']} | opacity={bb['opacity']} | ptr={bb['pointerEvents']}")

            active = [bb for bb in brain if bb['visible'] and not bb['disabled'] and bb['opacity'] not in ('0', '0.3', '0.5')]
            if active:
                tg(f"BRAIN STREAM ACTIVE - CLICKING: '{active[0]['text']}'")
                await page.evaluate("""(function(){
                    document.querySelectorAll('*').forEach(el => {
                        var t = el.textContent.trim().toUpperCase();
                        var s = window.getComputedStyle(el);
                        if (s.display !== 'none' && el.offsetParent && !el.disabled && t.includes('BRAIN STREAM')) {
                            el.click();
                        }
                    });
                })()""")
                await asyncio.sleep(4)
                await ss(page, "BRAIN-STREAM-CLICKED")
                after = await page.evaluate("document.body.innerText")
                tg(f"After Brain Stream: '{after[:600]}'")
            else:
                tg("Brain Stream is GREYED/DISABLED - EXPECTED FINAL STATE. System must activate.")
        else:
            tg("No brain stream button. Full page text above.")

        api_unique = list(set(api_calls))
        tg(f"API calls: {api_unique[:10]}")
        if page_errors:
            tg(f"Errors: {page_errors[:3]}")

        await ss(page, "ABSOLUTE-FINAL-999")
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)
        await ss(page, "999-top")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(0.5)
        await ss(page, "999-bottom")

        elapsed = int(time.time() - t0)
        tg(f"=== v6 COMPLETE. Time: {elapsed}s. Screenshots: {sc}. ===")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
