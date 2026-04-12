#!/usr/bin/env python3
"""
E2E Continuation: Click "Your AI is ready" orange button and document EVERYTHING after.
Date: 2026-03-04
Previous test stopped at ptc-welcome-btn. This test clicks it and continues to true end.
"""

import asyncio
import json
import time
import os
from datetime import datetime

OUT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-e2e-continue-20260304"
PAGE_URL = "https://purebrain.ai/pay-test-sandbox-3/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"
TG_SEND = "/home/jared/projects/AI-CIV/aether/tools/tg_send.sh"

TEST_NAME = "Test User"
TEST_EMAIL = "testuser@example.com"
TEST_COMPANY = "Test Corp"
TEST_ROLE = "Marketing Director"
TEST_GOAL = "Streamline content creation"

os.makedirs(OUT_DIR, exist_ok=True)

console_logs = []
network_calls = []
js_errors = []
birth_calls = []
seed_calls = []
all_api_responses = []

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] {msg}", flush=True)

def tg_send(msg, photo=None):
    """Send to Telegram."""
    import subprocess
    if photo:
        subprocess.Popen([TG_SEND, "--photo", photo, msg])
    else:
        subprocess.Popen([TG_SEND, msg])

async def safe_screenshot(page, filename, label="", send_tg=False):
    path = f"{OUT_DIR}/{filename}"
    try:
        await page.screenshot(
            path=path, full_page=False,
            clip={"x": 0, "y": 0, "width": 1440, "height": 900},
            timeout=20000
        )
        log(f"SHOT: {filename} - {label}")
        if send_tg:
            tg_send(f"sandbox3 screenshot: {label}", photo=path)
        return path
    except Exception as e:
        log(f"SHOT-FAIL: {filename}: {e}")
        return None

async def wait_ptc_input_active(page, timeout=90):
    deadline = time.time() + timeout
    while time.time() < deadline:
        display = await page.evaluate("""(function(){
            var row = document.getElementById('ptc-input-row');
            if (!row) return 'not-found';
            return window.getComputedStyle(row).display;
        })()""")
        if display not in ("none", "not-found"):
            return True
        await asyncio.sleep(1)
    return False

async def wait_for_new_ai_message(page, current_count, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        msgs = await page.query_selector_all(".ptc-msg--ai")
        if len(msgs) > current_count:
            return await msgs[-1].inner_text()
        await asyncio.sleep(0.5)
    return None

async def ptc_send(page, text):
    ta = await page.query_selector("#ptc-input")
    if not ta:
        ta = await page.query_selector("textarea.ptc-input")
    if not ta:
        return False, "no textarea"
    try:
        await ta.click(timeout=8000)
        await asyncio.sleep(0.3)
        await ta.fill("")
        await asyncio.sleep(0.2)
        await ta.type(text, delay=20)
        await asyncio.sleep(0.4)
        send = await page.query_selector("#ptc-send-btn")
        if send and await send.is_visible():
            await send.click()
            return True, "button"
        await ta.press("Enter")
        return True, "Enter"
    except Exception as e:
        return False, str(e)

async def click_btn_by_text(page, text_fragment, timeout=8):
    deadline = time.time() + timeout
    while time.time() < deadline:
        btns = await page.query_selector_all("button")
        for btn in btns:
            try:
                t = (await btn.inner_text()).strip()
                if text_fragment.lower() in t.lower():
                    if await btn.is_visible():
                        await btn.click()
                        return True, t
            except:
                pass
        await asyncio.sleep(0.5)
    return False, "not found"

async def get_full_page_state(page, label=""):
    """Comprehensive page state dump."""
    state = await page.evaluate("""(function() {
        var chatArea = document.getElementById('pay-test-post-payment');
        var fullHtml = chatArea ? chatArea.innerHTML : '';
        var bodyHtml = document.body ? document.body.innerHTML : '';

        // All messages
        var msgs = Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-msg--user')).map(function(m) {
            return {type: m.className.includes('--ai') ? 'ai' : 'user', text: m.innerText.trim().substring(0,500)};
        });

        // All visible buttons anywhere on page
        var allBtns = Array.from(document.querySelectorAll('button')).map(function(b) {
            var s = window.getComputedStyle(b);
            var rect = b.getBoundingClientRect();
            return {
                text: b.innerText.trim().substring(0,100),
                cls: b.className.substring(0,100),
                display: s.display,
                visibility: s.visibility,
                opacity: s.opacity,
                disabled: b.disabled,
                id: b.id,
                rect: {top: Math.round(rect.top), left: Math.round(rect.left), w: Math.round(rect.width), h: Math.round(rect.height)}
            };
        });

        // All visible links anywhere on page
        var allLinks = Array.from(document.querySelectorAll('a')).map(function(a) {
            var s = window.getComputedStyle(a);
            var rect = a.getBoundingClientRect();
            return {
                text: a.innerText.trim().substring(0,100),
                href: (a.href || a.getAttribute('href') || '').substring(0,200),
                cls: a.className.substring(0,60),
                display: s.display,
                id: a.id,
                rect: {top: Math.round(rect.top), left: Math.round(rect.left), w: Math.round(rect.width), h: Math.round(rect.height)}
            };
        });

        // Portal vortex
        var vortex = document.querySelector('.portal-vortex');
        var vortexInfo = null;
        if (vortex) {
            vortexInfo = {
                cls: vortex.className,
                children: vortex.children.length,
                innerText: vortex.innerText.substring(0,300),
                innerHTML_snippet: vortex.innerHTML.substring(0,500),
                display: window.getComputedStyle(vortex).display,
                visibility: window.getComputedStyle(vortex).visibility
            };
        }

        // Welcome button state
        var welcomeBtn = document.querySelector('.ptc-welcome-btn');
        var welcomeInfo = null;
        if (welcomeBtn) {
            var ws = window.getComputedStyle(welcomeBtn);
            welcomeInfo = {
                text: welcomeBtn.innerText.trim(),
                cls: welcomeBtn.className,
                display: ws.display,
                visibility: ws.visibility,
                opacity: ws.opacity,
                disabled: welcomeBtn.disabled,
                href: welcomeBtn.href || welcomeBtn.getAttribute('href') || ''
            };
        }

        // Overlay / modal detection
        var overlays = Array.from(document.querySelectorAll('[class*="overlay"], [class*="modal"], [class*="popup"], [id*="overlay"], [id*="modal"]')).map(function(el) {
            var s = window.getComputedStyle(el);
            return {tag: el.tagName, id: el.id, cls: el.className.substring(0,60), display: s.display, visibility: s.visibility, zIndex: s.zIndex, innerText: el.innerText.substring(0,150)};
        });

        // Check for iframe (portal might open in iframe)
        var iframes = Array.from(document.querySelectorAll('iframe')).map(function(f) {
            return {src: f.src, id: f.id, cls: f.className};
        });

        // Brain stream link
        var brainStreamEl = document.getElementById('brain-stream-link');
        var brainStreamInfo = null;
        if (brainStreamEl) {
            brainStreamInfo = {
                tag: brainStreamEl.tagName,
                id: brainStreamEl.id,
                innerText: brainStreamEl.innerText.substring(0,200),
                innerHTML: brainStreamEl.innerHTML.substring(0,300),
                href: brainStreamEl.href || brainStreamEl.getAttribute('href') || '',
                display: window.getComputedStyle(brainStreamEl).display
            };
        }

        // Any ptc-portal-btn
        var portalBtn = document.querySelector('.ptc-portal-btn');
        var portalBtnInfo = null;
        if (portalBtn) {
            var ps = window.getComputedStyle(portalBtn);
            portalBtnInfo = {
                text: portalBtn.innerText.trim().substring(0,100),
                href: portalBtn.href || portalBtn.getAttribute('href') || '',
                cls: portalBtn.className,
                display: ps.display,
                disabled: portalBtn.disabled
            };
        }

        // Current URL
        var currentUrl = window.location.href;

        // ptc-next-steps div
        var nextSteps = document.querySelector('.ptc-next-steps, #ptc-next-steps, [class*="next-steps"]');
        var nextStepsInfo = nextSteps ? {cls: nextSteps.className, id: nextSteps.id, innerText: nextSteps.innerText.substring(0,500), display: window.getComputedStyle(nextSteps).display} : null;

        return {
            current_url: currentUrl,
            all_messages: msgs,
            all_buttons: allBtns,
            all_links: allLinks,
            portal_vortex: vortexInfo,
            welcome_btn: welcomeInfo,
            overlays: overlays,
            iframes: iframes,
            brain_stream_el: brainStreamInfo,
            portal_btn: portalBtnInfo,
            next_steps: nextStepsInfo,
            has_claude_ai: bodyHtml.includes('claude.ai'),
            has_portal_href: bodyHtml.includes('portal.purebrain') || bodyHtml.includes('/portal/') || bodyHtml.includes('witness.purebrain'),
            has_witness: bodyHtml.includes('witness'),
            full_text_tail: (chatArea ? chatArea.innerText : '').split('').slice(-1500).join(''),
            input_row_display: (function() {
                var r = document.getElementById('ptc-input-row');
                return r ? window.getComputedStyle(r).display : 'not-found';
            })()
        };
    })()""")
    if label:
        log(f"\n--- Page state: {label} ---")
        log(f"  URL: {state['current_url']}")
        log(f"  AI messages: {len(state['all_messages'])}")
        log(f"  Has claude.ai: {state['has_claude_ai']}")
        log(f"  Has portal href: {state['has_portal_href']}")
        log(f"  Has witness: {state['has_witness']}")
        log(f"  Welcome btn: {state['welcome_btn']}")
        log(f"  Portal btn: {state['portal_btn']}")
        log(f"  Brain stream el: {state['brain_stream_el']}")
        log(f"  Next steps: {state['next_steps']}")
        log(f"  Overlays: {[o['cls'][:40] for o in state['overlays'] if o['display'] != 'none']}")
        log(f"  iframes: {state['iframes']}")
        vis_btns = [b for b in state['all_buttons'] if b['display'] != 'none' and b['visibility'] != 'hidden' and b.get('rect', {}).get('w', 0) > 0]
        log(f"  Visible buttons ({len(vis_btns)}): {[(b['text'][:50], b['cls'][:30]) for b in vis_btns]}")
        vis_links = [l for l in state['all_links'] if l['display'] != 'none' and l.get('rect', {}).get('w', 0) > 0 and l['href'] and not l['href'].startswith('#')]
        log(f"  Visible links ({len(vis_links)}): {[(l['text'][:40], l['href'][:80]) for l in vis_links]}")
        if state['portal_vortex']:
            log(f"  Portal vortex: {state['portal_vortex']}")
    return state

async def run():
    from playwright.async_api import async_playwright

    log(f"=== E2E CONTINUE: Past Orange Button ===")
    log(f"URL: {PAGE_URL}")
    log(f"Output: {OUT_DIR}")

    tg_send("sandbox3 E2E continuation started — running full flow to orange button and beyond")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox",
                  "--disable-web-security", "--disable-gpu",
                  "--disable-webgl", "--disable-3d-apis",
                  "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            ignore_https_errors=True
        )
        page = await context.new_page()

        def on_console(msg):
            text = msg.text
            entry = {"type": msg.type, "text": text, "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]}
            console_logs.append(entry)
            if any(kw in text.lower() for kw in ['birth', 'seed', 'payment', 'ptc', 'oauth', 'portal',
                                                   'awaken', 'brain', 'sanitize', 'lets-go', 'incredible',
                                                   'witness', 'welcome', 'next-step', 'redirect', 'navigate']):
                log(f"  CONSOLE:{msg.type.upper()}: {text[:400]}")

        def on_page_error(err):
            js_errors.append({"error": str(err), "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]})
            log(f"  JS-ERROR: {str(err)[:400]}")

        def on_request(req):
            url = req.url
            if any(kw in url for kw in ['birth', 'seed', 'verify', 'log-pay', 'log-conv', 'intake',
                                          'purebrain.ai/api', 'witness', 'portal', 'oauth', 'awaken']):
                entry = {"type": "REQ", "url": url, "method": req.method,
                         "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                         "post_data": req.post_data[:200] if req.post_data else ""}
                network_calls.append(entry)
                log(f"  API-REQ: {req.method} {url[:200]}")

        async def on_response(resp):
            url = resp.url
            if any(kw in url for kw in ['birth', 'seed', 'verify', 'log-pay', 'log-conv', 'intake',
                                          'purebrain.ai/api', 'witness', 'portal', 'oauth', 'awaken']):
                entry = {"type": "RESP", "url": url, "status": resp.status,
                         "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]}
                try:
                    body = await resp.json()
                    entry["body"] = body
                    log(f"  API-RESP-BODY: {resp.status} {url[:120]} -> {json.dumps(body)[:300]}")
                except:
                    try:
                        text = await resp.text()
                        entry["body_text"] = text[:300]
                        log(f"  API-RESP: {resp.status} {url[:120]} -> {text[:200]}")
                    except:
                        log(f"  API-RESP: {resp.status} {url[:120]}")
                all_api_responses.append(entry)
                network_calls.append(entry)
                if 'birth' in url:
                    birth_calls.append(entry)
                if 'seed' in url or 'intake' in url:
                    seed_calls.append(entry)

        def on_popup(popup):
            log(f"  POPUP OPENED: {popup.url}")
            tg_send(f"sandbox3: POPUP opened URL: {popup.url}")

        async def on_page_navigation(url):
            log(f"  NAVIGATION: {url}")

        page.on("console", on_console)
        page.on("pageerror", on_page_error)
        page.on("request", on_request)
        page.on("response", on_response)
        page.on("popup", on_popup)

        # ===== PHASE 1: SETUP (password + payment) =====
        log("\n=== PHASE 1: SETUP ===")
        await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        pw_inp = await page.query_selector('input[type="password"]')
        if pw_inp:
            log("Password gate found - entering password")
            await pw_inp.fill(PAGE_PASSWORD)
            sub = await page.query_selector('input[type="submit"]')
            if sub:
                await sub.click()
            else:
                await pw_inp.press("Enter")
            log("Password submitted, waiting 12s for JS...")
            await asyncio.sleep(12)
        else:
            log("No password gate")
            await asyncio.sleep(5)

        await safe_screenshot(page, "001-after-password.png", "After password entry")

        # Simulate payment
        order_id = f"E2E-CONTINUE-{int(time.time() * 1000)}"
        sim = await page.evaluate(f"""(function() {{
            try {{
                window.onPaymentComplete('Awakened', '{order_id}', {{}});
                return {{ok: true}};
            }} catch(e) {{ return {{ok: false, e: e.toString()}}; }}
        }})()""")
        log(f"Payment sim: {sim}")
        await asyncio.sleep(4)

        tg_send(f"sandbox3: Payment simulated (orderId={order_id}). Waiting for chatbox...")

        # Wait for chatbox input
        active = await wait_ptc_input_active(page, timeout=45)
        log(f"PTC input active: {active}")
        await safe_screenshot(page, "002-chatbox-open.png", "Chatbox opened", send_tg=True)

        # ===== PHASE 2: Q&A (fast) =====
        log("\n=== PHASE 2: Q&A ===")
        mc = len(await page.query_selector_all(".ptc-msg--ai"))
        for val in [TEST_NAME, TEST_EMAIL, TEST_COMPANY, TEST_ROLE]:
            ok, method = await ptc_send(page, val)
            log(f"  Sent '{val}': {ok}/{method}")
            await wait_for_new_ai_message(page, mc, timeout=12)
            mc = len(await page.query_selector_all(".ptc-msg--ai"))
            await asyncio.sleep(0.8)

        # Goal answer
        await ptc_send(page, TEST_GOAL)
        await asyncio.sleep(5)
        mc = len(await page.query_selector_all(".ptc-msg--ai"))
        log(f"After goal: {mc} AI messages")
        await safe_screenshot(page, "003-after-qa.png", "After Q&A complete")

        tg_send(f"sandbox3: Q&A complete ({mc} AI messages). Starting slides...")

        # ===== PHASE 3: SLIDES =====
        log("\n=== PHASE 3: SLIDES ===")
        for i in range(12):
            clicked, text = await click_btn_by_text(page, "Show Me More", timeout=5)
            if not clicked:
                log(f"  No more 'Show Me More' after slide {i}")
                break
            log(f"  Slide {i+1}: '{text[:40]}'")
            await asyncio.sleep(2.5)

        # Look for "incredible" / "lets go"
        await asyncio.sleep(2)
        clicked, text = await click_btn_by_text(page, "incredible", timeout=8)
        log(f"'That's incredible' clicked: {clicked}, text={text}")
        if not clicked:
            # Try alternate
            clicked, text = await click_btn_by_text(page, "let's go", timeout=5)
            log(f"'Let's go' clicked: {clicked}, text={text}")

        await asyncio.sleep(5)
        mc = len(await page.query_selector_all(".ptc-msg--ai"))
        log(f"After 'incredible' click: {mc} AI messages")
        await safe_screenshot(page, "004-after-incredible.png", "After 'That's incredible' click")

        tg_send("sandbox3: 'That's incredible - let's go' clicked. Watching for final AI messages...")

        # Wait for final AI messages (3 expected: machine description, done, worth it)
        await asyncio.sleep(8)
        mc = len(await page.query_selector_all(".ptc-msg--ai"))
        log(f"After wait: {mc} AI messages")

        # Check for welcome button
        pre_btn_state = await get_full_page_state(page, "Before orange button click")
        await safe_screenshot(page, "005-before-orange-btn.png", "Before orange button click", send_tg=True)

        tg_send(f"sandbox3: Pre-orange-button state captured. welcome_btn={pre_btn_state.get('welcome_btn')}")

        # ===== PHASE 4: CLICK ORANGE "YOUR AI IS READY" BUTTON =====
        log("\n=== PHASE 4: CLICKING 'YOUR AI IS READY' ORANGE BUTTON ===")
        log("This is the CONTINUATION point. Watching EVERYTHING...")

        # Wait for the button to appear if not already there
        deadline = time.time() + 30
        orange_btn = None
        while time.time() < deadline:
            orange_btn = await page.query_selector('.ptc-welcome-btn')
            if orange_btn and await orange_btn.is_visible():
                txt = await orange_btn.inner_text()
                log(f"Orange button found: '{txt}'")
                break
            await asyncio.sleep(1)

        if not orange_btn:
            log("WARNING: ptc-welcome-btn not found by class - trying text search")
            clicked_orange, text_orange = await click_btn_by_text(page, "Your AI is ready", timeout=10)
            log(f"Text-search click: {clicked_orange}, '{text_orange}'")
        else:
            btn_text = await orange_btn.inner_text()
            log(f"Clicking orange button: '{btn_text}'")
            await orange_btn.click()
            log("Orange button CLICKED")

        orange_click_time = time.time()

        # ===== PHASE 5: DOCUMENT EVERYTHING AFTER ORANGE BUTTON =====
        log("\n=== PHASE 5: MONITORING POST-ORANGE-CLICK ===")

        # Check for URL navigation immediately
        await asyncio.sleep(0.5)
        current_url = page.url
        log(f"URL immediately after click: {current_url}")

        if current_url != PAGE_URL and current_url != PAGE_URL + "/":
            log(f"NAVIGATION DETECTED! New URL: {current_url}")
            tg_send(f"sandbox3: NAVIGATION after orange btn! URL = {current_url}")

        # Watch for 90 seconds, taking screenshots at key moments
        step = 0
        visited_urls = set([current_url])
        detected_new_page = False
        detected_overlay = False
        detected_redirect = False

        for i in range(90):
            await asyncio.sleep(1)
            step = i + 1

            try:
                new_url = page.url
            except:
                new_url = current_url

            # URL change detection
            if new_url not in visited_urls:
                log(f"\n  t+{step}s: NEW URL: {new_url}")
                tg_send(f"sandbox3: t+{step}s URL changed to: {new_url}")
                visited_urls.add(new_url)
                detected_redirect = True
                await asyncio.sleep(3)  # wait for page load
                shot = await safe_screenshot(page, f"006-new-url-t{step}.png", f"New URL: {new_url}", send_tg=True)
                state_after_nav = await get_full_page_state(page, f"After navigation to {new_url}")

                # Keep clicking through whatever we find
                await click_through_everything(page, step, visited_urls)
                break

            # Snapshot check every 5 seconds in detail
            if step % 5 == 0 or step <= 10:
                state = await page.evaluate("""(function() {
                    // Visible buttons
                    var vis_btns = Array.from(document.querySelectorAll('button')).filter(function(b) {
                        var s = window.getComputedStyle(b);
                        var r = b.getBoundingClientRect();
                        return s.display !== 'none' && s.visibility !== 'hidden' && s.opacity !== '0' && r.width > 0 && r.height > 0;
                    }).map(function(b) { return {text: b.innerText.trim().substring(0,80), cls: b.className.substring(0,60), disabled: b.disabled}; });

                    // Visible links
                    var vis_links = Array.from(document.querySelectorAll('a[href]')).filter(function(a) {
                        var s = window.getComputedStyle(a);
                        var r = a.getBoundingClientRect();
                        var h = a.href || '';
                        return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0 && !h.startsWith('#') && h.length > 1;
                    }).map(function(a) { return {text: a.innerText.trim().substring(0,60), href: (a.href||'').substring(0,200)}; });

                    // New overlays or modals
                    var modals = Array.from(document.querySelectorAll('[class*="modal"],[class*="overlay"],[class*="popup"],[class*="dialog"],[role="dialog"]')).filter(function(el) {
                        var s = window.getComputedStyle(el);
                        var r = el.getBoundingClientRect();
                        return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;
                    }).map(function(el) { return {cls: el.className.substring(0,80), text: el.innerText.substring(0,200)}; });

                    // Iframes
                    var iframes = Array.from(document.querySelectorAll('iframe')).map(function(f) { return {src: f.src, w: f.offsetWidth, h: f.offsetHeight}; });

                    // ptc area text tail
                    var ptcEl = document.getElementById('pay-test-post-payment');
                    var ptcTail = ptcEl ? ptcEl.innerText.split('').slice(-800).join('') : '';

                    // Next steps specific selectors
                    var ns = document.querySelector('.ptc-next-steps, #ptc-next-steps, [data-ptc="next-steps"]');

                    // Brain stream section
                    var bs = document.getElementById('brain-stream-link') || document.querySelector('[id*="brain-stream"]');
                    var bsInfo = bs ? {id: bs.id, tag: bs.tagName, html: bs.innerHTML.substring(0,400), text: bs.innerText.substring(0,200), display: window.getComputedStyle(bs).display} : null;

                    return {
                        url: window.location.href,
                        visible_buttons: vis_btns,
                        visible_links: vis_links,
                        modals: modals,
                        iframes: iframes,
                        ptc_tail: ptcTail,
                        next_steps: ns ? {cls: ns.className, text: ns.innerText.substring(0,300)} : null,
                        brain_stream: bsInfo,
                        body_has_portal: document.body.innerHTML.includes('portal'),
                        body_has_witness: document.body.innerHTML.includes('witness'),
                        body_has_claude: document.body.innerHTML.includes('claude.ai'),
                    };
                })()""")

                log(f"\n  t+{step}s snapshot:")
                log(f"    URL: {state['url']}")
                log(f"    Visible buttons ({len(state['visible_buttons'])}): {[(b['text'][:50], b.get('disabled', False)) for b in state['visible_buttons']]}")
                log(f"    Visible links ({len(state['visible_links'])}): {[(l['text'][:40], l['href'][:80]) for l in state['visible_links']]}")
                if state['modals']:
                    log(f"    MODALS: {state['modals']}")
                if state['iframes']:
                    log(f"    IFRAMES: {state['iframes']}")
                if state['next_steps']:
                    log(f"    NEXT STEPS: {state['next_steps']}")
                if state['brain_stream']:
                    log(f"    BRAIN STREAM: {state['brain_stream']}")
                if state['body_has_portal'] or state['body_has_witness'] or state['body_has_claude']:
                    log(f"    SPECIAL: portal={state['body_has_portal']} witness={state['body_has_witness']} claude={state['body_has_claude']}")
                log(f"    PTC tail: {state['ptc_tail'][-300:]}")

                # Take screenshot at early intervals
                if step <= 15 or step % 15 == 0:
                    shot_label = f"t+{step}s post orange click"
                    send_to_tg = step <= 15 or step % 15 == 0
                    await safe_screenshot(page, f"007-t{step:03d}.png", shot_label, send_tg=send_to_tg)

                # Detect modals or new interactive elements
                if state['modals'] and not detected_overlay:
                    detected_overlay = True
                    log(f"\n  MODAL/OVERLAY DETECTED at t+{step}s!")
                    tg_send(f"sandbox3: t+{step}s MODAL detected: {state['modals'][0]['cls'][:60]}")
                    await safe_screenshot(page, f"008-modal-t{step}.png", "Modal/overlay detected", send_tg=True)

                # Try to click any new visible buttons that appeared after click
                for btn_info in state['visible_buttons']:
                    if btn_info['disabled']:
                        continue
                    txt = btn_info['text'].lower()
                    # Skip buttons we already know about
                    if any(skip in txt for skip in ['show me more', 'incredible', 'your ai is ready']):
                        continue
                    if txt and not txt.startswith('paypal'):
                        log(f"  NEW BUTTON FOUND: '{btn_info['text'][:60]}' - attempting click")
                        clicked_new, clicked_text = await click_btn_by_text(page, btn_info['text'][:30], timeout=3)
                        if clicked_new:
                            log(f"  Clicked new button: '{clicked_text}'")
                            tg_send(f"sandbox3: t+{step}s clicked new button: '{clicked_text[:50]}'")
                            await asyncio.sleep(3)
                            await safe_screenshot(page, f"009-after-btn-t{step}.png", f"After clicking '{clicked_text[:30]}'", send_tg=True)

                # Click visible links (portal/witness/external)
                for link_info in state['visible_links']:
                    href = link_info['href']
                    if any(kw in href for kw in ['portal', 'witness', 'purebrain.ai/login', 'purebrain.ai/portal', 'claude.ai']):
                        log(f"  PORTAL/EXTERNAL LINK: '{link_info['text']}' -> {href}")
                        tg_send(f"sandbox3: PORTAL LINK found: {href}")
                        detected_redirect = True

                # Check brain stream specifically
                if state['brain_stream']:
                    bs = state['brain_stream']
                    log(f"  BRAIN STREAM SECTION: id={bs['id']} display={bs['display']}")
                    if bs['html']:
                        log(f"    HTML: {bs['html'][:300]}")
                    if bs['text']:
                        log(f"    TEXT: {bs['text'][:200]}")

        # Final comprehensive state
        log("\n=== PHASE 6: FINAL STATE ANALYSIS ===")
        final_state = await get_full_page_state(page, "FINAL STATE")
        await safe_screenshot(page, "010-final-state.png", "FINAL STATE", send_tg=True)

        # Try clicking ANY remaining visible buttons we haven't tried
        log("\n=== PHASE 6b: CLICK ANY REMAINING INTERACTIVE ELEMENTS ===")
        await click_through_everything(page, 999, visited_urls)

        # One last screenshot
        await asyncio.sleep(5)
        await safe_screenshot(page, "011-absolute-final.png", "ABSOLUTE FINAL", send_tg=True)
        final_final_state = await get_full_page_state(page, "ABSOLUTE FINAL STATE")

        # ===== WRITE REPORT =====
        report = {
            "date": datetime.now().isoformat(),
            "test": "sandbox3-e2e-continue-beyond-orange-button",
            "order_id": order_id,
            "visited_urls": list(visited_urls),
            "birth_calls": birth_calls,
            "seed_calls": seed_calls,
            "all_api_responses": all_api_responses,
            "all_network": network_calls,
            "js_errors": js_errors,
            "console_logs_relevant": [c for c in console_logs if any(kw in c['text'].lower()
                for kw in ['birth', 'seed', 'payment', 'ptc', 'oauth', 'portal', 'awaken', 'brain',
                           'welcome', 'next-step', 'redirect', 'navigate', 'witness'])],
            "final_state": final_final_state,
            "detected_redirect": detected_redirect,
            "detected_overlay": detected_overlay,
        }

        report_path = "/home/jared/projects/AI-CIV/aether/exports/sandbox3-e2e-continue-report-20260304.md"
        _write_report(report, report_path)
        log(f"Report written: {report_path}")

        tg_send(f"sandbox3 E2E COMPLETE. Report: {report_path}. Visited URLs: {list(visited_urls)}")

        await browser.close()
        return report

async def click_through_everything(page, step_offset, visited_urls):
    """Click through every visible interactive element we find."""
    log(f"\n=== click_through_everything ===")

    # First look at what's in #brain-stream-link specifically
    bs_info = await page.evaluate("""(function() {
        var el = document.getElementById('brain-stream-link');
        if (!el) return null;
        return {
            tag: el.tagName,
            id: el.id,
            cls: el.className,
            innerText: el.innerText.substring(0,500),
            innerHTML: el.innerHTML.substring(0,1000),
            children: el.children.length,
            display: window.getComputedStyle(el).display,
            href: el.href || el.getAttribute('href') || ''
        };
    })()""")
    if bs_info:
        log(f"  #brain-stream-link: {bs_info}")

    # Scroll down to find any hidden content below fold
    await page.evaluate("""window.scrollTo(0, document.body.scrollHeight)""")
    await asyncio.sleep(2)

    scroll_state = await page.evaluate("""(function() {
        var chatArea = document.getElementById('pay-test-post-payment');
        return {
            scroll_y: window.scrollY,
            body_height: document.body.scrollHeight,
            ptc_scroll_top: chatArea ? chatArea.scrollTop : 0,
            ptc_scroll_height: chatArea ? chatArea.scrollHeight : 0,
            ptc_client_height: chatArea ? chatArea.clientHeight : 0
        };
    })()""")
    log(f"  Scroll state: {scroll_state}")

    # Also scroll within the chatbox
    await page.evaluate("""(function() {
        var el = document.getElementById('pay-test-post-payment');
        if (el) el.scrollTo(0, el.scrollHeight);
    })()""")
    await asyncio.sleep(2)

    # Take screenshot scrolled down
    await safe_screenshot(page, f"012-scrolled-down.png", "Scrolled to bottom", send_tg=True)

    # Find every link that might be a portal/next step
    all_clickables = await page.evaluate("""(function() {
        var all = [];
        document.querySelectorAll('a, button').forEach(function(el) {
            var s = window.getComputedStyle(el);
            var r = el.getBoundingClientRect();
            var href = el.href || el.getAttribute('href') || '';
            var text = el.innerText.trim().substring(0, 100);
            all.push({
                tag: el.tagName,
                text: text,
                href: href.substring(0, 200),
                id: el.id,
                cls: el.className.substring(0,80),
                display: s.display,
                visibility: s.visibility,
                opacity: s.opacity,
                disabled: el.disabled || false,
                rect: {top: Math.round(r.top + window.scrollY), left: Math.round(r.left), w: Math.round(r.width), h: Math.round(r.height)}
            });
        });
        return all;
    })()""")

    log(f"  Total clickable elements on page: {len(all_clickables)}")
    log(f"  All clickables:")
    for c in all_clickables:
        log(f"    [{c['tag']}] '{c['text'][:50]}' href={c['href'][:80]} cls={c['cls'][:40]} display={c['display']} visible={c['visibility']} opacity={c['opacity']}")

    # Attempt to click things we haven't tried
    skip_texts = ['show me more', 'incredible', 'your ai is ready', 'send', 'submit', 'paypal']
    for c in all_clickables:
        if c['display'] == 'none' or c['visibility'] == 'hidden' or c['opacity'] == '0':
            continue
        if c['disabled']:
            continue
        txt = c['text'].lower()
        if any(skip in txt for skip in skip_texts):
            continue
        if not txt and not c['href']:
            continue

        # Things we DO want to click
        if c['href'] and not c['href'].startswith('#') and not c['href'].startswith('javascript'):
            log(f"  FOUND EXTERNAL LINK: '{c['text'][:50]}' -> {c['href'][:100]}")
            tg_send(f"sandbox3: EXTERNAL LINK: '{c['text'][:50]}' -> {c['href']}")
        elif c['tag'] == 'BUTTON' and c['text'] and c['rect']['w'] > 0:
            interesting = any(kw in txt for kw in ['portal', 'connect', 'enter', 'access', 'start', 'begin', 'next', 'launch', 'brain', 'go', 'continue', 'ready'])
            if interesting:
                log(f"  INTERESTING BUTTON: '{c['text'][:60]}'")
                try:
                    await click_btn_by_text(page, c['text'][:30], timeout=3)
                    await asyncio.sleep(3)
                    await safe_screenshot(page, f"013-after-interesting-btn.png", f"After '{c['text'][:30]}'", send_tg=True)
                except Exception as e:
                    log(f"    Click failed: {e}")

def _write_report(report, path):
    """Write markdown report from data."""
    lines = [
        f"# Sandbox-3 E2E Continue Report — Beyond Orange Button",
        f"",
        f"**Date**: {report['date'][:10]}",
        f"**Order ID**: {report['order_id']}",
        f"**Test**: Full flow continuation past 'Your AI is ready' orange button",
        f"",
        f"---",
        f"",
        f"## URLs Visited",
        f"",
    ]
    for url in report['visited_urls']:
        lines.append(f"- {url}")
    lines.append("")

    lines += [
        f"## API Calls",
        f"",
        f"### Birth Calls ({len(report['birth_calls'])})",
    ]
    if report['birth_calls']:
        for c in report['birth_calls']:
            lines.append(f"- `{c.get('type','')}` {c.get('status','')} {c['url'][:120]}")
            if c.get('body'):
                lines.append(f"  Body: `{json.dumps(c['body'])[:200]}`")
    else:
        lines.append("- **NONE** — birth/start never called")
    lines.append("")

    lines += [
        f"### Seed/Intake Calls ({len(report['seed_calls'])})",
    ]
    if report['seed_calls']:
        for c in report['seed_calls']:
            lines.append(f"- `{c.get('type','')}` {c.get('status','')} {c['url'][:120]}")
    else:
        lines.append("- **NONE** — intake/seed never called")
    lines.append("")

    lines += [
        f"### All API Calls ({len(report['all_network'])})",
        f"",
    ]
    seen_urls = set()
    for c in report['all_network']:
        key = f"{c.get('method',c.get('type',''))} {c['url'][:80]}"
        if key not in seen_urls:
            lines.append(f"- `{c.get('type','')}` {c.get('status','')} {c.get('method','')} {c['url'][:120]}")
            seen_urls.add(key)
    lines.append("")

    lines += [
        f"## Redirect / Navigation Detected",
        f"**{report['detected_redirect']}**",
        f"",
        f"## Modal / Overlay Detected",
        f"**{report['detected_overlay']}**",
        f"",
        f"## JS Errors",
        f"",
    ]
    if report['js_errors']:
        for e in report['js_errors']:
            lines.append(f"- `{e['time']}`: {e['error'][:200]}")
    else:
        lines.append("- **None**")
    lines.append("")

    lines += [
        f"## Relevant Console Logs",
        f"",
    ]
    for c in report['console_logs_relevant']:
        lines.append(f"- `[{c['time']}] {c['type']}`: {c['text'][:300]}")
    if not report['console_logs_relevant']:
        lines.append("- (none matching keywords)")
    lines.append("")

    lines += [
        f"## Final Page State",
        f"",
        f"```json",
        json.dumps({
            "current_url": report['final_state'].get('current_url'),
            "has_claude_ai": report['final_state'].get('has_claude_ai'),
            "has_portal_href": report['final_state'].get('has_portal_href'),
            "has_witness": report['final_state'].get('has_witness'),
            "welcome_btn": report['final_state'].get('welcome_btn'),
            "portal_btn": report['final_state'].get('portal_btn'),
            "portal_vortex": report['final_state'].get('portal_vortex'),
            "brain_stream_el": report['final_state'].get('brain_stream_el'),
            "next_steps": report['final_state'].get('next_steps'),
            "iframes": report['final_state'].get('iframes'),
        }, indent=2),
        f"```",
        f"",
        f"### Final AI Messages",
        f"",
    ]
    for msg in report['final_state'].get('all_messages', []):
        lines.append(f"**[{msg['type'].upper()}]**: {msg['text'][:300]}")
        lines.append("")

    lines += [
        f"### All Final Buttons",
        f"",
    ]
    for b in report['final_state'].get('all_buttons', []):
        lines.append(f"- `{b.get('cls','')[:40]}` display={b.get('display','')} disabled={b.get('disabled','')} | '{b.get('text','')[:60]}'")
    lines.append("")

    lines += [
        f"### All Final Links",
        f"",
    ]
    for l in report['final_state'].get('all_links', []):
        lines.append(f"- '{l.get('text','')[:50]}' -> {l.get('href','')[:120]}")
    lines.append("")

    lines += [
        f"## Screenshots",
        f"",
        f"Directory: `/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-e2e-continue-20260304/`",
        f"",
    ]
    for f_name in sorted(os.listdir(OUT_DIR)):
        if f_name.endswith('.png'):
            lines.append(f"- `{f_name}`")
    lines.append("")

    with open(path, 'w') as f:
        f.write('\n'.join(lines))

if __name__ == "__main__":
    asyncio.run(run())
