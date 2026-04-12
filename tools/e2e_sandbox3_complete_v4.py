"""
E2E sandbox3 COMPLETION script v4 - faster, tighter timeouts
Starts fresh with JS sim and completes the FULL flow to brain stream
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

sc = 17  # Start from next number

def tg(msg):
    subprocess.run([TG_SEND, str(msg)[:4000]], timeout=10, capture_output=True)
    print(f"[TG] {str(msg)[:200]}")

def tg_photo(path, cap):
    try:
        subprocess.run([TG_SEND, "--photo", path, str(cap)[:200]], timeout=15, capture_output=True)
    except Exception as e:
        print(f"[TG PHOTO ERR] {e}")

async def take_ss(page, label, send_tg=True):
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

async def wait_input(page, timeout=90):
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
        await asyncio.sleep(1)
    return False

async def get_ai_msgs(page):
    try:
        return await page.evaluate("""(function(){
            var els = document.querySelectorAll('.ptc-msg--ai, .ptc-message--ai');
            return Array.from(els).map(e => e.textContent.trim()).filter(t => t.length > 1);
        })()""")
    except: return []

async def ptc_send(page, text):
    for sel in ["#ptc-input", "textarea.ptc-input"]:
        try:
            ta = await page.query_selector(sel)
            if ta and await ta.is_visible():
                await ta.click()
                await asyncio.sleep(0.2)
                await ta.fill("")
                await ta.type(text, delay=10)
                await asyncio.sleep(0.2)
                for bsel in ["#ptc-send-btn", ".ptc-send-btn"]:
                    btn = await page.query_selector(bsel)
                    if btn and await btn.is_visible():
                        await btn.click()
                        return True
                await ta.press("Enter")
                return True
        except Exception as e:
            print(f"[SEND ERR] {e}")
    return False

async def get_visible_btns(page):
    return await page.evaluate("""(function(){
        return Array.from(document.querySelectorAll('button, a.ptc-welcome-btn'))
            .filter(el => {
                var s = window.getComputedStyle(el);
                return s.display !== 'none' && s.visibility !== 'hidden' && el.offsetParent !== null;
            })
            .map(el => ({
                text: el.textContent.trim().substring(0, 100),
                cls: el.className.substring(0, 60),
                id: el.id,
                disabled: el.disabled || false
            }));
    })()""")

async def main():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    tg("=== E2E v4 COMPLETION: Starting fresh run to document full flow ===")

    console_log = []
    page_errors = []
    api_calls = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await ctx.new_page()

        page.on("console", lambda m: console_log.append(f"[{m.type.upper()}] {m.text}"))
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        async def on_resp(r):
            if "purebrain.ai" in r.url or "api.purebrain" in r.url:
                api_calls.append(f"{r.status} {r.url}")
        page.on("response", on_resp)

        # STEP 1: Load + password
        print("=== STEP 1: Load page + password ===")
        tg("Step 1: Loading page...")
        await page.goto(PAGE_URL, wait_until="load", timeout=30000)
        await asyncio.sleep(2)
        await take_ss(page, "load-initial")

        pw_f = await page.query_selector("input[type='password'], input[name='post_password']")
        if pw_f:
            await pw_f.fill(PAGE_PASSWORD)
            sub = await page.query_selector("input[type='submit'], button[type='submit']")
            if sub:
                await sub.click()
            else:
                await pw_f.press("Enter")
            try: await page.wait_for_load_state("load", timeout=10000)
            except: pass
            await asyncio.sleep(5)
            tg("Step 1: Password submitted")
        else:
            tg("Step 1: No password form")

        await take_ss(page, "after-password")

        # STEP 2: Check page content + paypal state
        body = await page.evaluate("document.body.innerText")
        print(f"[2] Page: {body[:300]}")

        all_iframes = page.frames
        pp_frames = [f for f in all_iframes if "paypal.com" in f.url]
        print(f"[2] PayPal frames: {len(pp_frames)}")
        tg(f"Step 2: Page loaded. PayPal frames: {len(pp_frames)}. Iframes: {[f.url[:60] for f in all_iframes[1:5]]}")

        await take_ss(page, "page-with-paypal")

        # Show what the page looks like before payment
        page_state_before = await page.evaluate("""(function(){
            return {
                buttons: Array.from(document.querySelectorAll('button')).map(b => ({
                    text: b.textContent.trim().substring(0,60), visible: window.getComputedStyle(b).display !== 'none'
                })).filter(b=>b.visible),
                iframes: Array.from(document.querySelectorAll('iframe')).map(f => f.src.substring(0,80)),
                paypal_containers: Array.from(document.querySelectorAll('[id*="paypal"],[class*="paypal"]')).map(e => ({
                    id: e.id, cls: e.className.substring(0,50), w: e.offsetWidth, h: e.offsetHeight
                }))
            };
        })()""")
        print(f"[2] State before payment: {page_state_before}")
        tg(f"Before payment: buttons={page_state_before['buttons'][:5]}, iframes={page_state_before['iframes'][:3]}, paypal={page_state_before['paypal_containers'][:3]}")

        # STEP 3: Check if PayPal button visible and attempt real click
        print("=== STEP 3: Attempt real PayPal ===")
        tg("Step 3: Inspecting PayPal frames...")

        # Wait more for PayPal
        for wi in range(15):
            pp_frames = [f for f in page.frames if "paypal.com" in f.url]
            if pp_frames:
                break
            await asyncio.sleep(1)

        pp_frames = [f for f in page.frames if "paypal.com" in f.url]
        tg(f"After wait: {len(pp_frames)} PayPal frames")

        for pf in pp_frames:
            try:
                fc = await pf.evaluate("""(function(){
                    return {
                        bodyLen: document.body ? document.body.innerHTML.length : 0,
                        buttons: Array.from(document.querySelectorAll('button, .paypal-button, [role="button"]')).length,
                        text: document.body ? document.body.innerText.substring(0,100) : ''
                    };
                })()""")
                print(f"[3] PayPal frame {pf.url[:60]}: {fc}")
                tg(f"PayPal frame content: buttons={fc['buttons']}, bodyLen={fc['bodyLen']}")
            except Exception as e:
                print(f"[3] Frame eval error: {e}")

        # STEP 4: JS Simulation (since no PayPal frames loaded = waitlist/PayPal not rendering)
        print("=== STEP 4: JS Simulation ===")
        tg("Step 4: PayPal not rendering in headless - using JS simulation. Documenting FULL post-payment flow.")

        funcs = await page.evaluate("""(function(){
            return {
                onPaymentComplete: typeof window.onPaymentComplete,
                launchPostPaymentFlow: typeof window.launchPostPaymentFlow,
                initPayTestFlow: typeof window.initPayTestFlow,
                sanitizeText: typeof window.sanitizeText,
                showBrainStreamButton: typeof window.showBrainStreamButton
            };
        })()""")
        print(f"[4] Window functions: {funcs}")
        tg(f"Window functions: {funcs}")

        # Trigger payment
        order_id = f"E2E-REAL-TEST-20260304-{int(time.time())}"
        if funcs.get("onPaymentComplete") == "function":
            await page.evaluate(f"window.onPaymentComplete('Awakened', '{order_id}', {{}})")
            tg(f"Triggered onPaymentComplete(orderId={order_id})")
        else:
            tg("ERROR: onPaymentComplete not on window!")
            for err in page_errors:
                tg(f"Page error: {err[:150]}")
            await browser.close()
            return

        await asyncio.sleep(5)

        container = await page.evaluate("""(function(){
            var el = document.getElementById('pay-test-post-payment');
            if (!el) return {found: false};
            return {found: true, children: el.children.length, display: window.getComputedStyle(el).display, text: el.textContent.trim().substring(0,200)};
        })()""")
        print(f"[4] Container: {container}")
        tg(f"Container after payment trigger: {container}")

        await take_ss(page, "after-payment-trigger")

        # STEP 5: Wait for PTC input
        print("=== STEP 5: Wait for PTC input ===")
        tg("Step 5: Waiting for chatbox input...")

        activated = await wait_input(page, 45)
        if not activated:
            tg("ERROR: PTC input not activated after 45s!")
            for err in page_errors[-5:]:
                tg(f"Error: {err[:120]}")
            await take_ss(page, "ptc-not-activated-error")
            await browser.close()
            return

        await take_ss(page, "ptc-ACTIVE-chatbox-open")
        tg("Chatbox ACTIVE! Starting Q&A conversation...")

        # Get initial messages
        await asyncio.sleep(2)
        init_msgs = await get_ai_msgs(page)
        tg(f"AI opening: '{init_msgs[-1][:150] if init_msgs else None}'")
        print(f"[5] Initial AI messages: {init_msgs}")

        # STEP 6: Q&A SEQUENCE
        print("=== STEP 6: Q&A ===")

        qa_data = [
            ("Alex Carter", "name"),
            ("alex.carter.test@example.com", "email"),
            ("Frontier AI Ventures", "company"),
            ("CTO", "role"),
            ("Automate our entire research pipeline and reporting system so our leadership team can focus on strategy and innovation rather than data gathering", "goal"),
        ]

        for answer, label in qa_data:
            print(f"\n[Q&A] {label}: {answer}")

            # Wait for input (shorter timeout - if gone, something changed)
            active = await wait_input(page, 15)
            if not active:
                tg(f"Input gone at {label} - checking state")
                btns = await get_visible_btns(page)
                tg(f"Buttons at {label}: {[b['text'] for b in btns[:5]]}")
                await take_ss(page, f"input-gone-at-{label}")
                break

            sent = await ptc_send(page, answer)
            tg(f"Sent {label}: '{answer[:60]}' - success={sent}")
            await asyncio.sleep(1)
            await take_ss(page, f"qa-{label}-sent")

            # Wait for AI response (max 10s)
            prev_msgs = await get_ai_msgs(page)
            for wi in range(10):
                await asyncio.sleep(1)
                new_msgs = await get_ai_msgs(page)
                if len(new_msgs) > len(prev_msgs):
                    tg(f"AI after {label}: '{new_msgs[-1][:120]}'")
                    print(f"[Q&A] AI: {new_msgs[-1][:100]}")
                    break

            await take_ss(page, f"qa-{label}-ai-response")

        # Check if slides appeared during Q&A
        btns_after_qa = await get_visible_btns(page)
        print(f"[6] Buttons after Q&A: {btns_after_qa}")
        tg(f"After Q&A buttons: {[b['text'] for b in btns_after_qa[:8]]}")

        # STEP 7: SLIDES
        print("\n=== STEP 7: Behind the Curtain SLIDES ===")
        tg("Step 7: Clicking through Behind the Curtain slides...")

        await asyncio.sleep(3)
        await take_ss(page, "slides-phase-begin")

        slides_clicked = 0
        for slide_i in range(15):
            btns = await get_visible_btns(page)
            print(f"[SLIDES {slide_i}] Buttons: {[(b['text'][:40], b['disabled']) for b in btns]}")

            slide_btn = None
            for b in btns:
                t = b['text'].lower()
                # Look for show me more or incredible
                if any(p in t for p in ["show me more", "incredible", "let's go", "show me"]):
                    if not b['disabled']:
                        slide_btn = b
                        break

            if not slide_btn:
                print(f"[SLIDES] No slide btn at {slide_i}")
                if slides_clicked > 0:
                    tg(f"Slides done: {slides_clicked} total")
                break

            btn_text = slide_btn['text']
            print(f"[SLIDES] Clicking: '{btn_text}'")

            # Click it via multiple strategies
            clicked = False
            for strategy in ["text_exact", "text_partial", "js"]:
                try:
                    if strategy == "text_exact":
                        await page.get_by_text(btn_text, exact=True).click(timeout=2000)
                    elif strategy == "text_partial":
                        await page.get_by_text(btn_text[:20], exact=False).first.click(timeout=2000)
                    elif strategy == "js":
                        await page.evaluate(f"""
                            (function(){{
                                var btns = Array.from(document.querySelectorAll('button'));
                                var btn = btns.find(b => b.textContent.trim().startsWith({repr(btn_text[:20])}));
                                if (btn) btn.click();
                            }})()
                        """)
                    clicked = True
                    break
                except:
                    pass

            if not clicked:
                tg(f"Could not click slide btn '{btn_text}'")
                break

            slides_clicked += 1
            await asyncio.sleep(2)
            await take_ss(page, f"slide-{slides_clicked:02d}-clicked")
            tg(f"Slide {slides_clicked}: '{btn_text}'")

            # Check for final slide
            if "incredible" in btn_text.lower() or "let's go" in btn_text.lower():
                tg("Clicked FINAL SLIDE: 'That's incredible — let's go'!")
                await asyncio.sleep(3)
                break

        print(f"[SLIDES] Total: {slides_clicked}")

        # STEP 8: YOUR AI IS READY BUTTON
        print("\n=== STEP 8: Your AI is ready button ===")
        tg("Step 8: Looking for orange 'Your AI is ready — see your next steps' button...")

        await asyncio.sleep(3)
        await take_ss(page, "your-ai-ready-phase")

        btns_at_cta = await get_visible_btns(page)
        print(f"[8] Buttons: {btns_at_cta}")
        tg(f"Buttons at CTA phase: {[(b['text'][:50], b['cls'][:30]) for b in btns_at_cta[:8]]}")

        # Full page inspection
        page_state_cta = await page.evaluate("""(function(){
            return {
                text: document.body.innerText.substring(0, 1000),
                ptc: (function(){
                    var el = document.getElementById('pay-test-post-payment');
                    return el ? {children: el.children.length, text: el.textContent.trim().substring(0,500)} : null;
                })(),
                portal: (function(){
                    var el = document.querySelector('.portal-vortex, #portal-vortex');
                    return el ? {cls: el.className, children: el.children.length, text: el.textContent.trim().substring(0,200)} : null;
                })()
            };
        })()""")
        print(f"[8] Page text: {page_state_cta['text'][:400]}")
        print(f"[8] PTC: {page_state_cta['ptc']}")
        print(f"[8] Portal: {page_state_cta['portal']}")
        tg(f"CTA phase page text: '{page_state_cta['text'][:400]}'")
        tg(f"PTC container: {page_state_cta['ptc']}")
        tg(f"Portal: {page_state_cta['portal']}")

        # Find + click "Your AI is ready"
        your_ai_btn = None
        for b in btns_at_cta:
            if "your ai is ready" in b['text'].lower() or "next steps" in b['text'].lower() or "ptc-welcome" in b['cls'].lower():
                your_ai_btn = b
                break

        if your_ai_btn:
            tg(f"Found 'Your AI is ready': '{your_ai_btn['text']}' - CLICKING (more steps follow!)")
            await take_ss(page, "your-ai-ready-FOUND")

            for strategy in ["text_partial", "cls", "js"]:
                try:
                    if strategy == "text_partial":
                        await page.get_by_text(your_ai_btn['text'][:20], exact=False).first.click(timeout=3000)
                    elif strategy == "cls" and your_ai_btn['id']:
                        await page.click(f"#{your_ai_btn['id']}", timeout=3000)
                    elif strategy == "js":
                        await page.evaluate("""(function(){
                            var btns = document.querySelectorAll('button, a');
                            for(var b of btns){
                                if(b.textContent.includes('Your AI is ready') || b.className.includes('ptc-welcome')){
                                    b.click(); return;
                                }
                            }
                        })()""")
                    break
                except:
                    pass

            await asyncio.sleep(4)
            await take_ss(page, "after-your-ai-ready-click")
            tg("Clicked 'Your AI is ready' - continuing to Brain Stream...")
        else:
            tg("'Your AI is ready' button not found. Checking full state...")
            await take_ss(page, "your-ai-ready-NOT-FOUND")

            # Extra scan - look for any orange button
            all_elements = await page.evaluate("""(function(){
                return Array.from(document.querySelectorAll('*')).filter(el => {
                    var s = window.getComputedStyle(el);
                    var bg = s.backgroundColor;
                    // Orange-ish backgrounds
                    return (bg.includes('241, 66') || bg.includes('255, 165') || bg.includes('255, 120')) &&
                           s.display !== 'none' && el.textContent.trim().length > 0;
                }).map(el => ({
                    tag: el.tagName, text: el.textContent.trim().substring(0,80),
                    cls: el.className.substring(0,50), bg: window.getComputedStyle(el).backgroundColor
                }));
            })()""")
            tg(f"Orange elements: {all_elements[:5]}")

        # STEP 9: MORE MESSAGES AFTER CTA
        print("\n=== STEP 9: Post-CTA messages ===")

        await asyncio.sleep(3)
        post_cta_msgs = await get_ai_msgs(page)
        tg(f"Messages after CTA: {post_cta_msgs[-3:] if post_cta_msgs else 'none'}")

        # Check for more slides or messages
        btns_post_cta = await get_visible_btns(page)
        print(f"[9] Post-CTA buttons: {btns_post_cta}")
        tg(f"Post-CTA buttons: {[(b['text'][:50], b['cls'][:30]) for b in btns_post_cta[:8]]}")

        # Click any remaining CTAs
        for b in btns_post_cta:
            if any(p in b['text'].lower() for p in ["continue", "next", "begin", "enter", "go", "stream", "brain"]):
                if not b['disabled']:
                    tg(f"Clicking post-CTA button: '{b['text']}'")
                    try:
                        await page.get_by_text(b['text'][:20], exact=False).first.click(timeout=3000)
                        await asyncio.sleep(3)
                        await take_ss(page, f"post-cta-{b['text'][:15].replace(' ','-').lower()}")
                    except Exception as e:
                        print(f"[9] Click error: {e}")

        # STEP 10: FINAL STATE - BRAIN STREAM
        print("\n=== STEP 10: FINAL STATE - BRAIN STREAM ===")
        tg("=== STEP 10: ABSOLUTE FINAL STATE - Looking for ENTER BRAIN STREAM ===")

        await asyncio.sleep(5)
        await take_ss(page, "FINAL-STATE-CHECK")

        final = await page.evaluate("""(function(){
            var result = {
                brain_buttons: [],
                portal: null,
                all_visible: [],
                page_text: document.body.innerText
            };

            // Brain stream buttons - search ALL elements
            var all = Array.from(document.querySelectorAll('*'));
            all.forEach(el => {
                var t = el.textContent.trim();
                if (t.length > 0 && t.length < 200) {
                    var tupper = t.toUpperCase();
                    if (tupper.includes('BRAIN STREAM') || tupper.includes('ENTER') ||
                        el.className.toString().includes('brain') || el.id.includes('brain')) {
                        var s = window.getComputedStyle(el);
                        result.brain_buttons.push({
                            tag: el.tagName,
                            text: t.substring(0, 100),
                            cls: el.className.substring(0, 60),
                            id: el.id,
                            display: s.display,
                            opacity: s.opacity,
                            pointerEvents: s.pointerEvents,
                            disabled: el.disabled || false,
                            visible: s.display !== 'none' && el.offsetParent !== null,
                            href: el.href || ''
                        });
                    }
                }
            });

            // Portal
            var portal = document.querySelector('.portal-vortex, #portal-vortex, [class*="portal"]');
            if (portal) {
                var ps = window.getComputedStyle(portal);
                result.portal = {
                    cls: portal.className,
                    text: portal.textContent.trim().substring(0, 300),
                    children: portal.children.length,
                    display: ps.display,
                    childDetails: Array.from(portal.children).map(c => ({
                        tag: c.tagName, cls: c.className.substring(0,40), text: c.textContent.trim().substring(0,60)
                    }))
                };
            }

            // All visible interactive elements
            result.all_visible = Array.from(document.querySelectorAll('button, a[href], input[type="submit"]'))
                .filter(el => {
                    var s = window.getComputedStyle(el);
                    return s.display !== 'none' && el.offsetParent !== null;
                })
                .map(el => ({
                    text: el.textContent.trim().substring(0,80),
                    cls: el.className.substring(0,50),
                    disabled: el.disabled || false,
                    href: el.href || ''
                }));

            return result;
        })()""")

        print(f"\n[FINAL] Brain buttons ({len(final['brain_buttons'])}):")
        for bb in final['brain_buttons']:
            print(f"  {bb}")

        print(f"\n[FINAL] Portal: {final['portal']}")
        print(f"\n[FINAL] All visible ({len(final['all_visible'])}):")
        for v in final['all_visible']:
            print(f"  {v}")

        print(f"\n[FINAL] Page text (1000):\n{final['page_text'][:1000]}")

        tg(f"BRAIN STREAM candidates: {final['brain_buttons'][:5]}")
        tg(f"All visible elements: {[(v['text'][:40], v['disabled']) for v in final['all_visible'][:10]]}")
        tg(f"Portal: {final['portal']}")
        tg(f"Full page text: '{final['page_text'][:800]}'")

        brain_btns = final['brain_buttons']
        if brain_btns:
            for bb in brain_btns:
                is_active = bb['visible'] and not bb['disabled'] and bb['opacity'] not in ('0', '0.5')
                status = "ACTIVE" if is_active else "GREYED/DISABLED"
                tg(f"Brain button: '{bb['text']}' | {status} | opacity={bb.get('opacity','?')} | pointerEvents={bb.get('pointerEvents','?')}")

            active_bb = [bb for bb in brain_btns if bb['visible'] and not bb['disabled'] and bb['opacity'] not in ('0', '0.5')]
            if active_bb:
                tg("BRAIN STREAM IS ACTIVE - CLICKING!")
                await page.evaluate("""(function(){
                    var all = Array.from(document.querySelectorAll('*'));
                    for(var el of all) {
                        var t = el.textContent.trim().toUpperCase();
                        if (t.includes('BRAIN STREAM') || t.includes('ENTER') && t.length < 100) {
                            var s = window.getComputedStyle(el);
                            if (s.display !== 'none' && el.offsetParent) {
                                el.click();
                                return;
                            }
                        }
                    }
                })()""")
                await asyncio.sleep(4)
                await take_ss(page, "brain-stream-CLICKED")
                after = await page.evaluate("document.body.innerText.substring(0, 800)")
                tg(f"After Brain Stream: '{after[:500]}'")
            else:
                tg("Brain Stream button is GREYED OUT/DISABLED = expected final state!")
                tg("This is THE END of the birth pipeline flow. User must wait for system to activate.")
        else:
            tg("No brain stream button found. Final page text sent above.")

        # Final screenshots
        await take_ss(page, "ABSOLUTE-FINAL-STATE")
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)
        await take_ss(page, "final-scroll-top")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        await take_ss(page, "final-scroll-bottom")

        # Final error report
        errors = [e for e in page_errors if e]
        tg(f"=== COMPLETE ===")
        tg(f"Total screenshots: {sc}")
        tg(f"Page errors: {len(errors)}")
        tg(f"API calls: {len(api_calls)}")
        if errors:
            tg(f"Errors: {errors[:3]}")

        # API call summary
        api_unique = list(set(api_calls))
        tg(f"API calls made: {api_unique[:10]}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
