"""
E2E sandbox3 v8 - DEFINITIVE: Capture GREYED Brain Stream Button in chatbox
Mission: Show the chatbox with "Click to Connect to Your AI's Brain Stream" greyed button visible
Key improvements over v7:
- After orange CTA click: scroll ptc-messages to expose brain stream wrapper
- Also try clicking "Learn more" button inside PTC to scroll underlying page
- Multiple capture angles: full page, ptc element, brain-stream element
- Save to: exports/e2e-sandbox3-complete-flow/ (numbered per mission brief)
"""

import asyncio
import os
import time
import subprocess
from playwright.async_api import async_playwright

PAGE_URL = "https://purebrain.ai/pay-test-sandbox-3/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/e2e-sandbox3-complete-flow"
TG_SEND = "/home/jared/projects/AI-CIV/aether/tools/tg_send.sh"

sc = 0

def tg(msg):
    try:
        subprocess.run([TG_SEND, str(msg)[:4000]], timeout=10, capture_output=True)
        print(f"[TG] {str(msg)[:200]}")
    except Exception as e:
        print(f"[TG ERR] {e}")

def tg_photo(path, cap):
    try:
        subprocess.run([TG_SEND, "--photo", path, str(cap)[:200]], timeout=15, capture_output=True)
        print(f"[TG PHOTO] {path[:50]}: {cap[:60]}")
    except Exception as e:
        print(f"[TG PHOTO ERR] {e}")

async def ss(page, label, send=True):
    global sc
    sc += 1
    fn = f"{sc:02d}-{label}.png"
    path = os.path.join(SCREENSHOT_DIR, fn)
    try:
        await page.screenshot(path=path, full_page=False)
        print(f"[SS] {fn}")
        if send:
            tg_photo(path, f"{sc}: {label}")
    except Exception as e:
        print(f"[SS ERR] {label}: {e}")
    return path

async def ss_el(page, selector, label, send=True):
    global sc
    sc += 1
    fn = f"{sc:02d}-{label}.png"
    path = os.path.join(SCREENSHOT_DIR, fn)
    try:
        el = await page.query_selector(selector)
        if el:
            await el.screenshot(path=path)
            print(f"[SS EL] {fn}")
            if send:
                tg_photo(path, f"{sc}: {label} [element]")
        else:
            await page.screenshot(path=path)
            print(f"[SS EL FALLBACK] {fn}")
            if send:
                tg_photo(path, f"{sc}: {label} [fallback]")
    except Exception as e:
        print(f"[SS EL ERR] {label}: {e}")
    return path

async def wait_input(page, timeout=30):
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

async def send_ptc(page, text):
    for sel in ["#ptc-input", "textarea.ptc-input"]:
        try:
            ta = await page.query_selector(sel)
            if ta and await ta.is_visible():
                await ta.fill(text)
                await asyncio.sleep(0.2)
                for bsel in ["#ptc-send-btn", ".ptc-send-btn", "button[type='submit']"]:
                    btn = await page.query_selector(bsel)
                    if btn:
                        try:
                            await btn.click()
                            return True
                        except:
                            pass
                await ta.press("Enter")
                return True
        except:
            pass
    return False

async def get_visible_btns(page):
    return await page.evaluate("""Array.from(document.querySelectorAll('button, a')).filter(b => {
        var s = window.getComputedStyle(b);
        return s.display !== 'none' && b.offsetParent !== null && b.textContent.trim().length > 0;
    }).map(b => ({text: b.textContent.trim().substring(0,80), cls: b.className.substring(0,60), id: b.id, disabled: b.disabled}))""")

async def click_js(page, text_fragment):
    """JS click by text - no navigation risk."""
    return await page.evaluate(f"""(function(){{
        var el = Array.from(document.querySelectorAll('button, a')).find(e =>
            e.textContent.trim().toLowerCase().includes({repr(text_fragment.lower())}) &&
            window.getComputedStyle(e).display !== 'none' && !e.disabled
        );
        if (el) {{ el.click(); return el.textContent.trim().substring(0,60); }}
        return null;
    }})()""")

async def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    # Clear existing screenshots for fresh numbered set
    import glob
    existing = glob.glob(os.path.join(SCREENSHOT_DIR, "*.png"))
    for f in existing:
        os.remove(f)
    print(f"[INIT] Cleared {len(existing)} existing screenshots for fresh run")

    tg("=== E2E v8 DEFINITIVE: Sandbox-3 Full Flow to Brain Stream Button ===")
    t0 = time.time()

    page_errors = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-setuid-sandbox",
                  "--disable-web-security", "--disable-features=VizDisplayCompositor"]
        )
        ctx = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await ctx.new_page()
        page.on("pageerror", lambda e: page_errors.append(str(e)))

        # =====================
        # PHASE 1: PASSWORD GATE
        # =====================
        print(f"\n[{int(time.time()-t0)}s] PHASE 1: Password Gate")
        tg("PHASE 1: Loading page + entering password...")

        await page.goto(PAGE_URL, wait_until="load", timeout=30000)
        await asyncio.sleep(2)

        # Screenshot before password
        await ss(page, "01-password-gate")

        # Enter password
        pw = await page.query_selector("input[type='password'], input[name='post_password']")
        if pw:
            await pw.fill(PAGE_PASSWORD)
            await ss(page, "01b-password-filled", send=False)
            sub = await page.query_selector("input[type='submit']")
            if sub:
                await sub.click()
            else:
                await pw.press("Enter")
            try:
                await page.wait_for_load_state("load", timeout=10000)
            except:
                pass
            await asyncio.sleep(4)
            tg("Password submitted.")
        else:
            tg("No password field found - page may be already unlocked")

        await ss(page, "02-post-password-load")

        # =====================
        # PHASE 2: PRE-PAYMENT (bypass mode)
        # =====================
        print(f"\n[{int(time.time()-t0)}s] PHASE 2: Pre-payment bypass")
        tg("PHASE 2: Checking functions + simulating payment...")

        # Check available JS functions
        funcs = await page.evaluate("""(function(){
            return {
                onPaymentComplete: typeof window.onPaymentComplete,
                sanitizeText: typeof window.sanitizeText,
                showBrainStreamButton: typeof window.showBrainStreamButton,
                fireSeed: typeof window.fireSeed,
                runPortalButtonWatcher: typeof window.runPortalButtonWatcher
            };
        })()""")
        print(f"Functions: {funcs}")
        tg(f"Functions: {funcs}")

        # Simulate payment
        order_id = f"E2E-V8-{int(time.time())}"
        if funcs.get("onPaymentComplete") == "function":
            await page.evaluate(f"window.onPaymentComplete('Awakened', '{order_id}', {{}})")
            tg(f"Payment simulated! orderId={order_id}")
        else:
            tg(f"ERROR: onPaymentComplete not available! Errors: {page_errors[:3]}")
            await ss(page, "ERROR-no-payment-fn")
            await browser.close()
            return

        await asyncio.sleep(5)
        await ss(page, "03-post-payment")

        # =====================
        # PHASE 3: WAIT FOR CHATBOX
        # =====================
        print(f"\n[{int(time.time()-t0)}s] PHASE 3: Wait for chatbox")
        tg("PHASE 3: Waiting for chatbox to activate...")

        if not await wait_input(page, 30):
            tg(f"ERROR: Chatbox did not activate. Errors: {page_errors[:3]}")
            await ss(page, "ERROR-no-chatbox")
            await browser.close()
            return

        await asyncio.sleep(2)
        tg("Chatbox ACTIVE!")
        await ss(page, "04-chatbox-active")

        # =====================
        # PHASE 4: Q&A (5 QUESTIONS)
        # =====================
        print(f"\n[{int(time.time()-t0)}s] PHASE 4: Q&A")
        tg("PHASE 4: Answering 5 Q&A questions...")

        qa_answers = [
            ("Alex Carter", "name"),
            ("alex.carter@purebrain.ai", "email"),
            ("Frontier AI Ventures", "company"),
            ("CTO and Co-Founder", "role"),
            ("Build an AI research pipeline that makes reporting 10x faster", "goal"),
        ]

        for answer, label in qa_answers:
            # Check if input row is still visible
            d = await page.evaluate("""(function(){
                var r = document.getElementById('ptc-input-row');
                return r ? window.getComputedStyle(r).display : 'not-found';
            })()""")
            if d in ("none", "not-found"):
                print(f"Input hidden at {label} - slides likely started")
                tg(f"Input hidden at {label} - moving to slides")
                break

            sent = await send_ptc(page, answer)
            print(f"[{int(time.time()-t0)}s] Sent {label}: {sent}")
            await asyncio.sleep(0.5)
            await ss(page, f"05-qa-{label}", send=False)

            # Wait for AI response or slide button (up to 8s)
            for _ in range(8):
                await asyncio.sleep(1)
                btns = await page.evaluate("""Array.from(document.querySelectorAll('button')).filter(b => {
                    var s = window.getComputedStyle(b);
                    return s.display !== 'none' && b.offsetParent !== null && !b.disabled;
                }).map(b => b.textContent.trim().toLowerCase())""")
                if any("show me more" in b or "incredible" in b for b in btns):
                    tg(f"Slide button appeared during {label}!")
                    break

        await asyncio.sleep(2)
        await ss(page, "06-qa-complete")
        tg("Q&A phase complete")

        # =====================
        # PHASE 5: SLIDES (10)
        # =====================
        print(f"\n[{int(time.time()-t0)}s] PHASE 5: Slides")
        tg("PHASE 5: Clicking through 10 slides...")

        slides_done = 0
        # Wait for first slide
        slide_deadline = time.time() + 20
        while time.time() < slide_deadline:
            btns = await page.evaluate("""Array.from(document.querySelectorAll('button')).filter(b => {
                var s = window.getComputedStyle(b);
                return s.display !== 'none' && b.offsetParent !== null && !b.disabled;
            }).map(b => b.textContent.trim().toLowerCase())""")
            if any("show me more" in b or "incredible" in b for b in btns):
                break
            await asyncio.sleep(1)

        # Click through slides
        for si in range(15):
            btns_raw = await page.evaluate("""Array.from(document.querySelectorAll('button')).map(b => ({
                text: b.textContent.trim().substring(0,80),
                vis: window.getComputedStyle(b).display !== 'none' && b.offsetParent !== null,
                dis: b.disabled
            }))""")
            active = [b for b in btns_raw if b['vis'] and not b['dis']]
            final_btn = next((b for b in active if "incredible" in b['text'].lower() or "let's go" in b['text'].lower()), None)
            more_btn = next((b for b in active if "show me more" in b['text'].lower()), None)

            if final_btn:
                await click_js(page, final_btn['text'][:20])
                slides_done += 1
                tg(f"FINAL SLIDE clicked: '{final_btn['text']}' (total={slides_done})")
                await asyncio.sleep(2)
                await ss(page, f"07-slide-final-{slides_done:02d}")
                break
            elif more_btn:
                await click_js(page, "Show Me More")
                slides_done += 1
                await asyncio.sleep(1.5)
                if slides_done == 1:
                    await ss(page, "07-slide-01-first")
                    tg("Slide 1 done, continuing to slide 10...")
                elif slides_done % 3 == 0:
                    await ss(page, f"07-slide-{slides_done:02d}", send=False)
            else:
                await asyncio.sleep(2)
                print(f"No slide btn at iteration {si}, active: {[b['text'][:30] for b in active[:5]]}")
                btns2 = await page.evaluate("""Array.from(document.querySelectorAll('button')).filter(b => {
                    var s = window.getComputedStyle(b);
                    return s.display !== 'none' && b.offsetParent !== null && !b.disabled;
                }).map(b => b.textContent.trim())""")
                if any("show me more" in b.lower() for b in btns2):
                    continue
                if any("incredible" in b.lower() for b in btns2):
                    continue
                break

        tg(f"Slides done: {slides_done}")
        await asyncio.sleep(3)

        # =====================
        # PHASE 6: "YOUR AI IS READY" CTA
        # =====================
        print(f"\n[{int(time.time()-t0)}s] PHASE 6: Orange CTA")
        tg("PHASE 6: Looking for 'Your AI is ready' orange CTA...")

        cta_found = False
        cta_deadline = time.time() + 20
        while time.time() < cta_deadline:
            all_btns = await get_visible_btns(page)
            cta = next((b for b in all_btns if "your ai is ready" in b['text'].lower()
                       or "next steps" in b['text'].lower()
                       or "ptc-welcome" in b.get('cls', '').lower()), None)
            if cta:
                cta_found = True
                tg(f"CTA found: '{cta['text']}'")
                break
            await asyncio.sleep(1)

        await ss(page, "08-before-orange-cta")

        if cta_found:
            # Use Playwright native click (most reliable for this button)
            try:
                await page.click('button:has-text("ready")', timeout=5000)
                tg("Orange CTA clicked via Playwright!")
            except:
                # Fallback to JS click
                result = await click_js(page, "your ai is ready")
                tg(f"Orange CTA clicked via JS: {result}")

            await asyncio.sleep(5)
            await ss(page, "09-after-orange-cta-click")
            tg("After orange CTA click")
        else:
            all_btns = await get_visible_btns(page)
            tg(f"CTA NOT found! All visible buttons: {[(b['text'][:50], b['cls'][:30]) for b in all_btns[:10]]}")
            # Try to capture current state and proceed anyway
            ptc_text = await page.evaluate("document.getElementById('pay-test-post-payment') ? document.getElementById('pay-test-post-payment').innerText.substring(0,600) : 'PTC not found'")
            tg(f"PTC text: '{ptc_text}'")

        # =====================
        # PHASE 7: FIND + CAPTURE BRAIN STREAM BUTTON
        # =====================
        print(f"\n[{int(time.time()-t0)}s] PHASE 7: Capture Brain Stream Button")
        tg("PHASE 7: Finding and capturing the GREYED brain stream button...")

        await asyncio.sleep(3)

        # Step 7a: Full page screenshot
        await ss(page, "10-post-cta-full-page")

        # Step 7b: PTC element screenshot
        await ss_el(page, "#pay-test-post-payment", "11-ptc-chatbox-element")

        # Step 7c: Scroll ptc-messages to bottom to expose any hidden content
        await page.evaluate("""(function(){
            var containers = [
                document.querySelector('#ptc-messages'),
                document.querySelector('.ptc-messages'),
                document.querySelector('[class*="ptc-messages"]')
            ];
            containers.forEach(c => { if(c) { c.scrollTop = c.scrollHeight; } });
        })()""")
        await asyncio.sleep(1)
        await ss(page, "12-ptc-messages-scrolled-bottom")

        # Step 7d: Check if "Learn more" button exists inside PTC and click it
        learn_more = await page.evaluate("""(function(){
            var ptc = document.getElementById('pay-test-post-payment');
            if (!ptc) return null;
            var btn = Array.from(ptc.querySelectorAll('button, a')).find(e =>
                e.textContent.trim().toLowerCase().includes('learn more') &&
                window.getComputedStyle(e).display !== 'none'
            );
            if (btn) {
                return {text: btn.textContent.trim(), cls: btn.className, tag: btn.tagName};
            }
            return null;
        })()""")
        tg(f"Learn more button inside PTC: {learn_more}")

        if learn_more:
            tg("Clicking 'Learn more' inside chatbox...")
            await page.evaluate("""(function(){
                var ptc = document.getElementById('pay-test-post-payment');
                if (!ptc) return;
                var btn = Array.from(ptc.querySelectorAll('button, a')).find(e =>
                    e.textContent.trim().toLowerCase().includes('learn more')
                );
                if (btn) btn.click();
            })()""")
            await asyncio.sleep(3)
            await ss(page, "13-after-learn-more-click")

        # Step 7e: Now look for brain stream wrapper on the underlying page
        # It's at y=3744+ in document coords, revealed when underlying page scrolls
        brain_state = await page.evaluate("""(function(){
            // Check brain stream wrapper
            var wrapper = document.getElementById('pb-brain-stream-wrapper');
            var btn = document.getElementById('pb-brain-stream-btn');

            // Also search by class
            var byClass = Array.from(document.querySelectorAll('[class*="brain-stream"], [id*="brain-stream"], [class*="brain_stream"]')).map(el => ({
                tag: el.tagName, id: el.id, cls: el.className.substring(0,80),
                text: el.textContent.trim().substring(0,150),
                opacity: window.getComputedStyle(el).opacity,
                display: window.getComputedStyle(el).display,
                pointerEvents: window.getComputedStyle(el).pointerEvents,
                cursor: window.getComputedStyle(el).cursor,
                position: window.getComputedStyle(el).position,
                rect: (() => { var r = el.getBoundingClientRect(); return {x:r.x, y:r.y, w:r.width, h:r.height}; })()
            }));

            // Search PTC for any brain/stream text
            var ptc = document.getElementById('pay-test-post-payment');
            var ptcBrainText = null;
            if (ptc) {
                var allInPtc = Array.from(ptc.querySelectorAll('*')).filter(e =>
                    e.textContent.trim().toLowerCase().includes('brain') ||
                    e.textContent.trim().toLowerCase().includes('stream') ||
                    e.textContent.trim().toLowerCase().includes('connect')
                );
                ptcBrainText = allInPtc.slice(0,5).map(e => ({
                    tag: e.tagName, text: e.textContent.trim().substring(0,120),
                    cls: e.className.substring(0,60), display: window.getComputedStyle(e).display
                }));
            }

            return {
                wrapperFound: !!wrapper,
                wrapperOpacity: wrapper ? window.getComputedStyle(wrapper).opacity : null,
                wrapperDisplay: wrapper ? window.getComputedStyle(wrapper).display : null,
                wrapperPointerEvents: wrapper ? window.getComputedStyle(wrapper).pointerEvents : null,
                wrapperRect: wrapper ? (() => { var r=wrapper.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height}; })() : null,
                btnFound: !!btn,
                btnText: btn ? btn.textContent.trim() : null,
                btnOpacity: btn ? window.getComputedStyle(btn).opacity : null,
                btnCursor: btn ? window.getComputedStyle(btn).cursor : null,
                btnBackground: btn ? window.getComputedStyle(btn).backgroundColor : null,
                byClass: byClass,
                ptcBrainElements: ptcBrainText
            };
        })()""")

        print(f"[BRAIN STATE] {brain_state}")
        tg(f"Brain stream state: wrapper={brain_state.get('wrapperFound')}, opacity={brain_state.get('wrapperOpacity')}")
        tg(f"Brain btn: found={brain_state.get('btnFound')}, text='{brain_state.get('btnText')}', opacity={brain_state.get('btnOpacity')}, cursor={brain_state.get('btnCursor')}")
        tg(f"By class: {brain_state.get('byClass', [])}")
        tg(f"PTC brain elements: {brain_state.get('ptcBrainElements')}")

        # Step 7f: If wrapper exists, scroll the page to bring it into viewport
        if brain_state.get("wrapperFound"):
            tg("Brain stream wrapper found! Scrolling to it...")

            # The brain stream wrapper is on the underlying page, below the chatbox
            # We need to scroll the PAGE (not the chatbox) to bring it into view
            # But the chatbox is position:fixed with z-index:999999 so it covers everything

            # Option A: Try scrollIntoView on the wrapper
            await page.evaluate("""(function(){
                var wrapper = document.getElementById('pb-brain-stream-wrapper');
                if (wrapper) {
                    wrapper.scrollIntoView({behavior: 'instant', block: 'center'});
                }
            })()""")
            await asyncio.sleep(1)
            await ss(page, "14-after-wrapper-scroll-into-view")

            # Check if wrapper is now in viewport
            wrapper_rect = await page.evaluate("""(function(){
                var w = document.getElementById('pb-brain-stream-wrapper');
                if (!w) return null;
                var r = w.getBoundingClientRect();
                return {x: r.x, y: r.y, width: r.width, height: r.height};
            })()""")
            tg(f"Wrapper rect after scroll: {wrapper_rect}")

            # Take screenshot of just the wrapper element
            await ss_el(page, "#pb-brain-stream-wrapper", "15-BRAIN-STREAM-WRAPPER-ELEMENT")
            await ss_el(page, "#pb-brain-stream-btn", "16-BRAIN-STREAM-BTN-ELEMENT")

            # Step 7g: Temporarily hide the chatbox to see the brain stream button underneath
            tg("Temporarily hiding chatbox to capture brain stream button...")
            await page.evaluate("""(function(){
                var ptc = document.getElementById('pay-test-post-payment');
                if (ptc) ptc.style.display = 'none';
            })()""")
            await asyncio.sleep(0.5)
            await ss(page, "17-BRAIN-STREAM-VISIBLE-chatbox-hidden")
            await ss_el(page, "#pb-brain-stream-wrapper", "18-BRAIN-STREAM-WRAPPER-ZOOMED")
            tg("Brain stream button captured with chatbox hidden!")

            # Restore chatbox
            await page.evaluate("""(function(){
                var ptc = document.getElementById('pay-test-post-payment');
                if (ptc) ptc.style.display = '';
            })()""")
            await asyncio.sleep(0.5)
            await ss(page, "19-chatbox-restored")

        else:
            tg("Brain stream wrapper NOT found. Checking all possible selectors...")
            # Exhaustive DOM check
            all_brain = await page.evaluate("""(function(){
                var candidates = [];
                document.querySelectorAll('button, a, [role="button"]').forEach(el => {
                    var t = el.textContent.trim().toUpperCase();
                    if (t.includes('BRAIN') || t.includes('STREAM') || t.includes('CONNECT') || t.includes('ENTER')) {
                        var s = window.getComputedStyle(el);
                        candidates.push({
                            tag: el.tagName, id: el.id, cls: el.className.substring(0,80),
                            text: el.textContent.trim().substring(0,100),
                            opacity: s.opacity, display: s.display, disabled: el.disabled || false
                        });
                    }
                });
                return candidates;
            })()""")
            tg(f"All brain/stream/connect/enter elements: {all_brain}")

        # =====================
        # PHASE 8: FINAL STATE SCREENSHOTS
        # =====================
        print(f"\n[{int(time.time()-t0)}s] PHASE 8: Final state screenshots")
        tg("PHASE 8: Taking final state screenshots...")

        # Restore chatbox if hidden
        await page.evaluate("""(function(){
            var ptc = document.getElementById('pay-test-post-payment');
            if (ptc && window.getComputedStyle(ptc).display === 'none') {
                ptc.style.display = '';
            }
        })()""")

        # Scroll ptc-messages to bottom one more time
        await page.evaluate("""(function(){
            var m = document.querySelector('#ptc-messages') || document.querySelector('.ptc-messages');
            if (m) m.scrollTop = m.scrollHeight;
        })()""")
        await asyncio.sleep(1)

        await ss(page, "20-FINAL-STATE-full-page")
        await ss_el(page, "#pay-test-post-payment", "21-FINAL-ptc-chatbox")

        # DOM state summary
        final_state = await page.evaluate("""(function(){
            var ptc = document.getElementById('pay-test-post-payment');
            var wrapper = document.getElementById('pb-brain-stream-wrapper');
            var btn = document.getElementById('pb-brain-stream-btn');
            var input = document.getElementById('ptc-input');
            var sendBtn = document.getElementById('ptc-send-btn');

            return {
                ptcFound: !!ptc,
                ptcText_last200: ptc ? ptc.innerText.trim().slice(-400) : null,
                wrapperFound: !!wrapper,
                wrapperOpacity: wrapper ? window.getComputedStyle(wrapper).opacity : null,
                wrapperPointerEvents: wrapper ? window.getComputedStyle(wrapper).pointerEvents : null,
                btnText: btn ? btn.textContent.trim() : null,
                btnOpacity: btn ? window.getComputedStyle(btn).opacity : null,
                btnBackground: btn ? window.getComputedStyle(btn).backgroundColor : null,
                btnCursor: btn ? window.getComputedStyle(btn).cursor : null,
                inputDisabled: input ? input.disabled : null,
                sendBtnDisabled: sendBtn ? sendBtn.disabled : null,
                sendBtnOpacity: sendBtn ? window.getComputedStyle(sendBtn).opacity : null
            };
        })()""")

        print(f"\n[FINAL STATE]")
        for k, v in final_state.items():
            print(f"  {k}: {v}")

        tg(f"FINAL STATE:")
        tg(f"  Brain wrapper: found={final_state.get('wrapperFound')}, opacity={final_state.get('wrapperOpacity')}, pointerEvents={final_state.get('wrapperPointerEvents')}")
        tg(f"  Brain btn text: '{final_state.get('btnText')}'")
        tg(f"  Brain btn: opacity={final_state.get('btnOpacity')}, bg={final_state.get('btnBackground')}, cursor={final_state.get('btnCursor')}")
        tg(f"  Input disabled: {final_state.get('inputDisabled')}, Send disabled: {final_state.get('sendBtnDisabled')}, Send opacity: {final_state.get('sendBtnOpacity')}")
        tg(f"  Last PTC text: '{final_state.get('ptcText_last200', '')}'")

        total_time = int(time.time() - t0)
        ss_count = sc
        tg(f"=== E2E v8 COMPLETE: {total_time}s, {ss_count} screenshots ===")
        tg(f"Screenshots: {SCREENSHOT_DIR}")

        if page_errors:
            tg(f"Page errors encountered: {page_errors[:5]}")

        await browser.close()
        print(f"\n[DONE] {total_time}s, {ss_count} screenshots in {SCREENSHOT_DIR}")

if __name__ == "__main__":
    asyncio.run(main())
