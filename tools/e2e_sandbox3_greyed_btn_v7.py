"""
E2E sandbox3 v7 - MISSION: Find greyed ENTER [AI NAME]'S BRAIN STREAM button
Goal: Get to chatbox post-CTA state, scroll within chatbox, capture greyed button
Key difference from v6: DO NOT navigate away. Stay in chatbox. Scroll inside chatbox.
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
        print(f"[TG] {str(msg)[:300]}")
    except Exception as e:
        print(f"[TG ERR] {e}")

def tg_photo(path, cap):
    try:
        subprocess.run([TG_SEND, "--photo", path, str(cap)[:200]], timeout=15, capture_output=True)
        print(f"[TG PHOTO] {path}: {cap[:80]}")
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

async def ss_element(page, selector, label, send=True):
    """Screenshot a specific element."""
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
            await page.screenshot(path=path, full_page=False)
            print(f"[SS EL FALLBACK] {fn} (selector not found)")
            if send:
                tg_photo(path, f"{sc}: {label} [fallback-no-element]")
    except Exception as e:
        print(f"[SS EL ERR] {label}: {e}")
        # fallback to full page
        try:
            await page.screenshot(path=path, full_page=False)
        except: pass
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
                for bsel in ["#ptc-send-btn", ".ptc-send-btn", "button[type='submit']"]:
                    btn = await page.query_selector(bsel)
                    if btn and await btn.is_visible():
                        await btn.click()
                        return True
                await ta.press("Enter")
                return True
        except: pass
    return False

async def get_all_buttons(page):
    return await page.evaluate("""(function(){
        return Array.from(document.querySelectorAll('button, a')).filter(el => {
            var s = window.getComputedStyle(el);
            return s.display !== 'none' && el.offsetParent !== null && el.textContent.trim().length > 0;
        }).map(el => ({
            text: el.textContent.trim().substring(0,100),
            cls: el.className.substring(0,80),
            id: el.id,
            disabled: el.disabled||false,
            opacity: window.getComputedStyle(el).opacity,
            pointerEvents: window.getComputedStyle(el).pointerEvents,
            href: el.href || null
        }));
    })()""")

async def click_text_safe(page, text, avoid_nav=True):
    """Click button matching text. If avoid_nav=True, use JS click instead of Playwright click to prevent navigation."""
    result = await page.evaluate(f"""(function(){{
        var els = Array.from(document.querySelectorAll('button, a'));
        var el = els.find(e => e.textContent.trim().toLowerCase().includes({repr(text.lower()[:30])}) && window.getComputedStyle(e).display !== 'none' && !e.disabled);
        if (el) {{
            el.click();
            return el.textContent.trim().substring(0,80);
        }}
        return null;
    }})()""")
    return result

async def get_ptc_full_state(page):
    """Get the full state of the PTC (post-payment chatbox) container."""
    return await page.evaluate("""(function(){
        var ptc = document.getElementById('pay-test-post-payment');
        if (!ptc) return {found: false};

        // Get all buttons inside PTC
        var ptcBtns = Array.from(ptc.querySelectorAll('button, a')).map(el => ({
            text: el.textContent.trim().substring(0,120),
            cls: el.className.substring(0,80),
            id: el.id,
            disabled: el.disabled||false,
            opacity: window.getComputedStyle(el).opacity,
            pointerEvents: window.getComputedStyle(el).pointerEvents,
            display: window.getComputedStyle(el).display,
            visible: window.getComputedStyle(el).display !== 'none' && el.offsetParent !== null,
            tag: el.tagName
        }));

        // Get all elements with brain/stream/enter in text inside PTC
        var brainEls = Array.from(ptc.querySelectorAll('*')).filter(el => {
            var t = el.textContent.trim().toUpperCase();
            return (t.includes('BRAIN') || t.includes('STREAM') || t.includes('ENTER'))
                && t.length < 200 && el.children.length === 0;
        }).map(el => ({
            tag: el.tagName, text: el.textContent.trim().substring(0,120), cls: el.className.substring(0,80),
            display: window.getComputedStyle(el).display,
            opacity: window.getComputedStyle(el).opacity,
            disabled: el.disabled||false,
            visible: window.getComputedStyle(el).display !== 'none' && el.offsetParent !== null
        }));

        // Get all AI messages
        var msgs = Array.from(ptc.querySelectorAll('.ptc-msg--ai, .ptc-message--ai, [class*="ptc-msg"]')).map(e => e.textContent.trim());

        // Get portal elements
        var portal = ptc.querySelector('.portal-vortex, #portal-vortex, [id*="brain-stream"], [class*="brain-stream"], [class*="portal"]');
        var portalInfo = null;
        if (portal) {
            portalInfo = {
                cls: portal.className, id: portal.id,
                text: portal.textContent.trim().substring(0,400),
                children: portal.children.length,
                display: window.getComputedStyle(portal).display
            };
        }

        // Full PTC text
        var ptcText = ptc.innerText;

        // Scroll height
        var msgContainer = ptc.querySelector('.ptc-messages, #ptc-messages, [class*="messages"]');

        return {
            found: true,
            ptcBtns: ptcBtns,
            brainEls: brainEls,
            msgs: msgs,
            portal: portalInfo,
            ptcText: ptcText,
            children: ptc.children.length,
            scrollHeight: msgContainer ? msgContainer.scrollHeight : ptc.scrollHeight,
            innerHTML_snippet: ptc.innerHTML.substring(0, 3000)
        };
    })()""")

async def scroll_ptc_and_capture(page, label_prefix):
    """Scroll inside the PTC message container to expose hidden content, take screenshots."""
    global sc

    # Scroll message container to bottom
    await page.evaluate("""(function(){
        var containers = [
            document.querySelector('.ptc-messages'),
            document.querySelector('#ptc-messages'),
            document.querySelector('[class*="ptc-messages"]'),
            document.getElementById('pay-test-post-payment')
        ];
        containers.forEach(c => {
            if (c) {
                c.scrollTop = c.scrollHeight;
            }
        });
        // Also try scrolling the main ptc
        var ptc = document.getElementById('pay-test-post-payment');
        if (ptc) ptc.scrollTop = ptc.scrollHeight;
    })()""")
    await asyncio.sleep(0.5)

    # Take screenshot at scroll bottom
    path = await ss(page, f"{label_prefix}-scrolled-bottom")

    # Also capture PTC element specifically
    await ss_element(page, "#pay-test-post-payment", f"{label_prefix}-ptc-element")

    return path

async def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    tg("=== E2E v7: MISSION - Find GREYED Brain Stream Button ===")
    tg("Strategy: Full flow, then stay in chatbox, scroll to find greyed button")
    t0 = time.time()

    page_errors = []
    api_calls = []
    console_msgs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-setuid-sandbox"]
        )
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx.new_page()

        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.on("console", lambda m: console_msgs.append(f"{m.type}: {m.text[:100]}"))

        async def on_resp(r):
            url = r.url
            if "purebrain.ai" in url or "api.purebrain" in url:
                api_calls.append(f"{r.status} {url}")
        page.on("response", on_resp)

        # PHASE 1: LOAD + PASSWORD
        print(f"\n[{int(time.time()-t0)}s] === PHASE 1: LOAD + PASSWORD ===")
        tg("PHASE 1: Loading page + password...")

        await page.goto(PAGE_URL, wait_until="load", timeout=30000)
        await asyncio.sleep(2)

        pw = await page.query_selector("input[type='password'], input[name='post_password']")
        if pw:
            await pw.fill(PAGE_PASSWORD)
            sub = await page.query_selector("input[type='submit']")
            if sub:
                await sub.click()
            else:
                await pw.press("Enter")
            try:
                await page.wait_for_load_state("load", timeout=8000)
            except: pass
            await asyncio.sleep(4)
            tg("Password submitted. Page loaded.")

        await ss(page, "01-password-gate")

        # Check page state
        page_text = await page.evaluate("document.body.innerText.substring(0, 500)")
        tg(f"Page after password: '{page_text[:300]}'")

        # PHASE 2: PAYMENT TRIGGER
        print(f"\n[{int(time.time()-t0)}s] === PHASE 2: PAYMENT TRIGGER ===")
        tg("PHASE 2: Triggering payment simulation...")

        funcs = await page.evaluate("""(function(){
            return {
                onPaymentComplete: typeof window.onPaymentComplete,
                launchPostPaymentFlow: typeof window.launchPostPaymentFlow,
                sanitizeText: typeof window.sanitizeText,
                showBrainStreamButton: typeof window.showBrainStreamButton,
                fireSeed: typeof window.fireSeed
            };
        })()""")
        print(f"[{int(time.time()-t0)}s] Functions: {funcs}")
        tg(f"Functions available: {funcs}")

        order_id = f"E2E-V7-{int(time.time())}"

        if funcs.get("onPaymentComplete") == "function":
            await page.evaluate(f"window.onPaymentComplete('Awakened', '{order_id}', {{}})")
            tg(f"Payment simulated! orderId={order_id}")
        else:
            tg(f"ERROR: onPaymentComplete not found! funcs={funcs}")
            tg(f"Errors so far: {page_errors[:3]}")
            await ss(page, "02-ERROR-no-onPaymentComplete")
            await browser.close()
            return

        await asyncio.sleep(5)
        await ss(page, "02-post-payment")

        # PHASE 3: WAIT FOR CHATBOX
        print(f"\n[{int(time.time()-t0)}s] === PHASE 3: WAIT FOR CHATBOX ===")
        tg("PHASE 3: Waiting for chatbox...")

        if not await wait_input(page, 30):
            tg("ERROR: Chatbox input not active after 30s!")
            ptc_state = await get_ptc_full_state(page)
            tg(f"PTC state: found={ptc_state.get('found')}, children={ptc_state.get('children')}")
            tg(f"Errors: {page_errors[:3]}")
            await ss(page, "03-ERROR-no-chatbox")
            await browser.close()
            return

        await asyncio.sleep(2)
        await ss(page, "03-chatbox-active")
        tg("Chatbox ACTIVE!")

        # Get opening AI message
        ptc_state = await get_ptc_full_state(page)
        tg(f"Opening msg: '{ptc_state.get('msgs', [''])[0][:100] if ptc_state.get('msgs') else 'no msgs yet'}'")

        # PHASE 4: Q&A (5 QUESTIONS)
        print(f"\n[{int(time.time()-t0)}s] === PHASE 4: Q&A ===")
        tg("PHASE 4: Starting Q&A (5 questions)...")

        qa_pairs = [
            ("Alex Carter", "name"),
            ("alex.carter@purebrain.ai", "email"),
            ("Frontier AI Ventures", "company"),
            ("CTO and Co-Founder", "role"),
            ("Automate our entire research pipeline and make reporting 10x faster", "goal"),
        ]

        for answer, label in qa_pairs:
            # Check if input still active
            d = await page.evaluate("""(function(){
                var r = document.getElementById('ptc-input-row');
                return r ? window.getComputedStyle(r).display : 'not-found';
            })()""")

            if d in ("none", "not-found"):
                print(f"[{int(time.time()-t0)}s] Input hidden at {label} - slides started")
                tg(f"Input hidden during {label} - slides may have started")
                break

            sent = await send_ptc(page, answer)
            print(f"[{int(time.time()-t0)}s] Q&A '{label}': sent={sent}")
            tg(f"Q&A {label}: '{answer}' sent={sent}")
            await asyncio.sleep(0.5)
            await ss(page, f"04-qa-{label}", send=False)

            # Wait up to 8s for response OR slide button
            for wi in range(8):
                await asyncio.sleep(1)
                btns = await page.evaluate("""Array.from(document.querySelectorAll('button')).filter(b => {
                    var s = window.getComputedStyle(b);
                    return s.display !== 'none' && b.offsetParent !== null && !b.disabled;
                }).map(b => b.textContent.trim().substring(0,60))""")
                has_slide = any("show me more" in b.lower() or "incredible" in b.lower() for b in btns)
                if has_slide:
                    tg(f"Slide button appeared during {label}!")
                    break

        print(f"[{int(time.time()-t0)}s] Q&A phase complete")
        await asyncio.sleep(2)
        await ss(page, "05-qa-complete")

        # Report Q&A state
        qa_state = await get_ptc_full_state(page)
        tg(f"Post-Q&A msgs: {len(qa_state.get('msgs', []))} AI msgs")
        tg(f"Last msg: '{(qa_state.get('msgs') or [''])[-1][:120]}'")

        # PHASE 5: SLIDES (10 SLIDES)
        print(f"\n[{int(time.time()-t0)}s] === PHASE 5: SLIDES ===")
        tg("PHASE 5: Clicking through 10 slides...")

        slides_done = 0
        max_slide_wait = 20  # seconds to wait for first slide

        # Wait for slides to appear
        slide_deadline = time.time() + max_slide_wait
        while time.time() < slide_deadline:
            btns = await page.evaluate("""Array.from(document.querySelectorAll('button')).filter(b => {
                var s = window.getComputedStyle(b);
                return s.display !== 'none' && b.offsetParent !== null && !b.disabled;
            }).map(b => b.textContent.trim().substring(0,60))""")
            has_slide = any("show me more" in b.lower() or "incredible" in b.lower() for b in btns)
            if has_slide:
                break
            await asyncio.sleep(1)

        # Click through all slides
        for si in range(15):
            btns_raw = await page.evaluate("""Array.from(document.querySelectorAll('button')).map(b => ({
                text: b.textContent.trim().substring(0,80),
                disabled: b.disabled,
                display: window.getComputedStyle(b).display,
                visible: window.getComputedStyle(b).display !== 'none' && b.offsetParent !== null
            }))""")

            btns_active = [b for b in btns_raw if b['visible'] and not b['disabled']]

            incredible = next((b for b in btns_active if "incredible" in b['text'].lower() or "let's go" in b['text'].lower()), None)
            show_more = next((b for b in btns_active if "show me more" in b['text'].lower()), None)

            if incredible:
                tg(f"FINAL SLIDE (slide {slides_done+1}): '{incredible['text']}' - clicking!")
                await click_text_safe(page, incredible['text'][:20])
                slides_done += 1
                await asyncio.sleep(2)
                await ss(page, f"06-slide-FINAL-{slides_done:02d}")
                tg(f"Final slide clicked! Total slides: {slides_done}")
                break
            elif show_more:
                await click_text_safe(page, "Show Me More")
                slides_done += 1
                print(f"[{int(time.time()-t0)}s] Slide {slides_done}")
                await asyncio.sleep(1.5)
                if slides_done % 3 == 0:
                    await ss(page, f"06-slide-{slides_done:02d}", send=False)
                if slides_done == 1:
                    await ss(page, "06-slide-01-first")
                    tg(f"Slide 1 clicked! Continuing to slide 10...")
            else:
                print(f"[{int(time.time()-t0)}s] No slide btn at iteration {si}")
                tg(f"No slide btn at iteration {si}. Active buttons: {[b['text'][:40] for b in btns_active[:5]]}")
                await asyncio.sleep(2)
                # One more attempt
                btns2 = await page.evaluate("""Array.from(document.querySelectorAll('button')).filter(b => {
                    var s = window.getComputedStyle(b);
                    return s.display !== 'none' && b.offsetParent !== null && !b.disabled;
                }).map(b => b.textContent.trim().substring(0,60))""")
                if any("show me more" in b.lower() for b in btns2):
                    continue
                break

        print(f"[{int(time.time()-t0)}s] Slides done: {slides_done}")
        tg(f"Slides complete: {slides_done}/10")
        await asyncio.sleep(3)

        state_post_slides = await get_ptc_full_state(page)
        tg(f"Post-slides buttons: {[b['text'][:60] for b in state_post_slides.get('ptcBtns', [])[:6]]}")
        await ss(page, "07-post-slides-state")

        # PHASE 6: YOUR AI IS READY (orange CTA)
        print(f"\n[{int(time.time()-t0)}s] === PHASE 6: YOUR AI IS READY CTA ===")
        tg("PHASE 6: Looking for 'Your AI is ready' orange CTA...")

        # Wait up to 15s for the CTA button
        cta_found = False
        cta_deadline = time.time() + 15
        while time.time() < cta_deadline:
            all_btns = await get_all_buttons(page)
            cta = next((b for b in all_btns if "your ai is ready" in b['text'].lower() or "next steps" in b['text'].lower() or "ptc-welcome" in b['cls'].lower()), None)
            if cta:
                cta_found = True
                tg(f"'Your AI is ready' CTA FOUND: '{cta['text']}'")
                break
            await asyncio.sleep(1)

        if not cta_found:
            all_btns = await get_all_buttons(page)
            tg(f"CTA NOT found after 15s. All buttons: {[(b['text'][:50], b['cls'][:30]) for b in all_btns[:10]]}")
            ptc_s = await get_ptc_full_state(page)
            tg(f"PTC text: '{ptc_s.get('ptcText', '')[:400]}'")

        await ss(page, "08-before-your-ai-ready-click")

        if cta_found:
            # Click the CTA
            await click_text_safe(page, "your ai is ready")
            tg("'Your AI is ready' clicked!")
            await asyncio.sleep(4)
            await ss(page, "09-after-your-ai-ready-click")
            tg("After 'Your AI is ready' click - now capturing chatbox state...")

        # PHASE 7: POST-CTA STATE - FIND GREYED BRAIN STREAM BUTTON
        print(f"\n[{int(time.time()-t0)}s] === PHASE 7: FIND GREYED BRAIN STREAM BUTTON ===")
        tg("PHASE 7: Searching for GREYED ENTER [AI NAME]'S BRAIN STREAM button...")

        await asyncio.sleep(3)

        # Full chatbox state inspection
        ptc_post_cta = await get_ptc_full_state(page)

        tg(f"PTC found: {ptc_post_cta.get('found')}")
        tg(f"PTC children: {ptc_post_cta.get('children')}")
        tg(f"PTC buttons: {[(b['text'][:60], b['disabled'], b['opacity']) for b in ptc_post_cta.get('ptcBtns', [])[:10]]}")
        tg(f"Brain elements in PTC: {ptc_post_cta.get('brainEls', [])}")
        tg(f"PTC text: '{ptc_post_cta.get('ptcText', '')[:600]}'")

        # Screenshot the full chatbox
        await ss(page, "10-post-cta-chatbox-state")
        await ss_element(page, "#pay-test-post-payment", "11-ptc-element-full")

        # Scroll inside PTC to find greyed button
        tg("Scrolling inside PTC to find brain stream button...")
        await scroll_ptc_and_capture(page, "12-ptc")

        # Also scroll the page body
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(0.5)
        await ss(page, "13-page-scrolled-bottom")

        # PHASE 8: EXHAUSTIVE BRAIN STREAM SEARCH
        print(f"\n[{int(time.time()-t0)}s] === PHASE 8: EXHAUSTIVE BRAIN STREAM SEARCH ===")
        tg("PHASE 8: Exhaustive search for brain stream button...")

        brain_search = await page.evaluate("""(function(){
            var results = [];

            // Search ALL elements for brain/stream/enter keywords
            document.querySelectorAll('*').forEach(el => {
                var t = el.textContent.trim();
                if (t.length > 0 && t.length < 300) {
                    var tu = t.toUpperCase();
                    if (tu.includes('BRAIN STREAM') || tu.includes('ENTER') && (tu.includes('BRAIN') || tu.includes('STREAM'))) {
                        var s = window.getComputedStyle(el);
                        if (el.children.length <= 2) {  // leaf or near-leaf
                            results.push({
                                tag: el.tagName,
                                text: t.substring(0, 150),
                                cls: el.className.substring(0, 100),
                                id: el.id,
                                display: s.display,
                                opacity: s.opacity,
                                pointerEvents: s.pointerEvents,
                                disabled: el.disabled || false,
                                visible: s.display !== 'none' && el.offsetParent !== null,
                                color: s.color,
                                background: s.backgroundColor,
                                cursor: s.cursor
                            });
                        }
                    }
                }
            });

            // Also search by class name patterns
            var byClass = Array.from(document.querySelectorAll('[class*="brain"], [class*="stream"], [id*="brain"], [id*="stream"], [class*="portal-btn"], [id*="portal-btn"], [class*="brain-stream"]')).map(el => ({
                tag: el.tagName,
                text: el.textContent.trim().substring(0, 150),
                cls: el.className.substring(0, 100),
                id: el.id,
                display: window.getComputedStyle(el).display,
                opacity: window.getComputedStyle(el).opacity,
                disabled: el.disabled || false,
                visible: window.getComputedStyle(el).display !== 'none'
            }));

            // Check portal-vortex content
            var portal = document.querySelector('.portal-vortex, #portal-vortex');
            var portalContent = null;
            if (portal) {
                portalContent = {
                    outerHTML: portal.outerHTML.substring(0, 2000),
                    text: portal.textContent.trim().substring(0, 400),
                    children: portal.children.length,
                    childDetails: Array.from(portal.children).map(c => ({
                        tag: c.tagName, cls: c.className.substring(0, 60), id: c.id,
                        text: c.textContent.trim().substring(0, 80),
                        display: window.getComputedStyle(c).display,
                        opacity: window.getComputedStyle(c).opacity
                    }))
                };
            }

            // Check hash links
            var hashLinks = Array.from(document.querySelectorAll('a[href*="#"]')).map(a => ({
                text: a.textContent.trim().substring(0,60),
                href: a.href,
                cls: a.className.substring(0,60),
                visible: window.getComputedStyle(a).display !== 'none' && a.offsetParent !== null
            }));

            // Full ptc innerHTML
            var ptc = document.getElementById('pay-test-post-payment');
            var ptcHTML = ptc ? ptc.innerHTML : 'NOT FOUND';

            return {
                brainResults: results,
                byClass: byClass,
                portalContent: portalContent,
                hashLinks: hashLinks,
                ptcHTML: ptcHTML.substring(0, 5000),
                allButtonsOnPage: Array.from(document.querySelectorAll('button')).map(b => ({
                    text: b.textContent.trim().substring(0, 80),
                    cls: b.className.substring(0, 80),
                    id: b.id,
                    disabled: b.disabled,
                    opacity: window.getComputedStyle(b).opacity,
                    display: window.getComputedStyle(b).display,
                    visible: window.getComputedStyle(b).display !== 'none' && b.offsetParent !== null
                }))
            };
        })()""")

        tg(f"Brain search results: {brain_search.get('brainResults', [])}")
        tg(f"By class results: {brain_search.get('byClass', [])}")
        tg(f"Portal content: {brain_search.get('portalContent')}")
        tg(f"Hash links: {[(l['text'][:40], l['href']) for l in brain_search.get('hashLinks', []) if l['visible']]}")
        tg(f"ALL page buttons: {[(b['text'][:50], b['disabled'], b['opacity']) for b in brain_search.get('allButtonsOnPage', []) if b['visible']]}")

        print(f"[BRAIN] Results: {brain_search.get('brainResults')}")
        print(f"[PORTAL] Content: {brain_search.get('portalContent')}")

        # PHASE 9: WAIT AND POLL FOR BRAIN STREAM BUTTON ACTIVATION
        # The button may appear after birth pipeline fires (up to 30s delay)
        print(f"\n[{int(time.time()-t0)}s] === PHASE 9: WAIT FOR BRAIN STREAM ACTIVATION ===")
        tg("PHASE 9: Waiting up to 60s for brain stream button to appear/activate...")

        brain_btn_found = False
        for poll_i in range(12):  # 12 x 5s = 60s
            await asyncio.sleep(5)

            # Check for brain stream button
            brain_check = await page.evaluate("""(function(){
                var ptc = document.getElementById('pay-test-post-payment');
                if (!ptc) return {ptcFound: false};

                // Check all buttons
                var allBtns = Array.from(ptc.querySelectorAll('button, a, [role="button"]')).map(el => ({
                    text: el.textContent.trim().substring(0,120),
                    cls: el.className.substring(0,80),
                    id: el.id,
                    disabled: el.disabled || false,
                    opacity: window.getComputedStyle(el).opacity,
                    display: window.getComputedStyle(el).display,
                    visible: window.getComputedStyle(el).display !== 'none' && el.offsetParent !== null
                }));

                // Search globally too
                var brainBtns = Array.from(document.querySelectorAll('button, a, [role="button"]')).filter(el => {
                    var t = el.textContent.trim().toUpperCase();
                    return t.includes('BRAIN STREAM') || (t.includes('ENTER') && t.includes('BRAIN'));
                }).map(el => ({
                    text: el.textContent.trim().substring(0,120),
                    cls: el.className.substring(0,80),
                    id: el.id,
                    disabled: el.disabled || false,
                    opacity: window.getComputedStyle(el).opacity,
                    display: window.getComputedStyle(el).display,
                    visible: window.getComputedStyle(el).display !== 'none'
                }));

                // Check for watcher function
                var watcherAvail = typeof window.runPortalButtonWatcher === 'function';
                var showBrainAvail = typeof window.showBrainStreamButton === 'function';

                return {
                    ptcFound: true,
                    allBtns: allBtns,
                    brainBtns: brainBtns,
                    watcherAvail: watcherAvail,
                    showBrainAvail: showBrainAvail,
                    ptcText: ptc.innerText.substring(0, 600)
                };
            })()""")

            brain_btns = brain_check.get('brainBtns', [])

            print(f"[{int(time.time()-t0)}s] Poll {poll_i+1}/12: brainBtns={brain_btns}")

            if brain_btns:
                brain_btn_found = True
                tg(f"BRAIN STREAM BUTTON FOUND at poll {poll_i+1}!")
                tg(f"Buttons: {brain_btns}")
                await ss(page, f"14-BRAIN-STREAM-FOUND-poll{poll_i+1:02d}")
                await ss_element(page, "#pay-test-post-payment", f"15-BRAIN-STREAM-PTC-poll{poll_i+1:02d}")

                # Scroll to bottom to make sure button is visible
                await scroll_ptc_and_capture(page, f"16-brain-stream-scrolled")
                break

            if poll_i % 3 == 0:
                tg(f"Poll {poll_i+1}/12: No brain stream yet. PTC buttons: {[(b['text'][:40], b['disabled']) for b in brain_check.get('allBtns', []) if b['visible']]}")
                if poll_i == 0:
                    # Try manually triggering watcher
                    if brain_check.get('watcherAvail'):
                        tg("Triggering runPortalButtonWatcher manually...")
                        await page.evaluate("window.runPortalButtonWatcher && window.runPortalButtonWatcher()")
                    if brain_check.get('showBrainAvail'):
                        tg("Trying showBrainStreamButton manually...")
                        await page.evaluate("window.showBrainStreamButton && window.showBrainStreamButton()")
                        await asyncio.sleep(2)
                        await ss(page, f"14-after-showBrain-manual")

        if not brain_btn_found:
            tg("Brain stream button NOT found after 60s polling. Capturing final state...")

        # PHASE 10: FINAL STATE CAPTURE
        print(f"\n[{int(time.time()-t0)}s] === PHASE 10: FINAL STATE CAPTURE ===")
        tg("PHASE 10: Final state capture...")

        await asyncio.sleep(2)

        # Multiple final screenshots
        await ss(page, "17-FINAL-STATE-full-page")
        await ss_element(page, "#pay-test-post-payment", "18-FINAL-ptc-element")

        # Scroll to top of page then capture
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)
        await ss(page, "19-FINAL-page-top")

        # Scroll to bottom
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(0.5)
        await ss(page, "20-FINAL-page-bottom")

        # Get final PTC state
        final_ptc = await get_ptc_full_state(page)
        tg(f"FINAL PTC state:")
        tg(f"  buttons: {[(b['text'][:60], b['disabled'], b['opacity']) for b in final_ptc.get('ptcBtns', [])[:8]]}")
        tg(f"  brainEls: {final_ptc.get('brainEls', [])}")
        tg(f"  portal: {final_ptc.get('portal')}")
        tg(f"  text: '{final_ptc.get('ptcText', '')[:500]}'")

        # Full page text
        final_page_text = await page.evaluate("document.body.innerText")
        tg(f"Full page text (first 800): '{final_page_text[:800]}'")

        # API calls summary
        api_unique = list(set(api_calls))
        tg(f"API calls: {api_unique[:15]}")

        # Errors
        if page_errors:
            tg(f"Page errors: {page_errors[:5]}")

        # Console important msgs
        important_console = [m for m in console_msgs if any(k in m.lower() for k in ['error', 'warn', 'brain', 'stream', 'portal', 'watcher', 'seed', 'birth'])]
        if important_console:
            tg(f"Important console: {important_console[:10]}")

        elapsed = int(time.time() - t0)
        tg(f"=== v7 COMPLETE. Time: {elapsed}s. Screenshots: {sc}. ===")
        tg(f"Brain stream found: {brain_btn_found}")
        tg(f"Screenshots dir: {SCREENSHOT_DIR}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
