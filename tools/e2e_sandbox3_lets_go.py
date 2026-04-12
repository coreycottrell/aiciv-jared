#!/usr/bin/env python3
"""
Final part of E2E: Click "That's incredible - let's go" and observe BIRTH + portal button.
Date: 2026-03-04
"""

import asyncio
import json
import time
import os
from datetime import datetime

OUT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-e2e-20260304"
PAGE_URL = "https://purebrain.ai/pay-test-sandbox-3/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"

TEST_NAME = "Test User"
TEST_EMAIL = "testuser@example.com"
TEST_COMPANY = "Test Corp"
TEST_ROLE = "Marketing Director"
TEST_GOAL = "Streamline content creation and automate customer outreach"

os.makedirs(OUT_DIR, exist_ok=True)

console_logs = []
network_calls = []
js_errors = []

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] {msg}")

async def safe_screenshot(page, filename, label=""):
    path = f"{OUT_DIR}/{filename}"
    try:
        await page.screenshot(
            path=path, clip={"x": 0, "y": 0, "width": 1440, "height": 900}, timeout=20000
        )
        log(f"SHOT: {filename} - {label}")
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

async def wait_for_new_ai_message(page, current_count, timeout=12):
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
        await ta.type(text, delay=30)
        await asyncio.sleep(0.5)
        send = await page.query_selector("#ptc-send-btn")
        if send and await send.is_visible():
            await send.click()
            return True, "button"
        await ta.press("Enter")
        return True, "Enter"
    except Exception as e:
        return False, str(e)

async def click_btn_by_text(page, text_fragment, timeout=10):
    """Click button containing text."""
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

async def run():
    from playwright.async_api import async_playwright

    log(f"Starting 'lets go' test on {PAGE_URL}")

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

        birth_calls = []
        seed_calls = []
        response_bodies = {}

        def on_console(msg):
            text = msg.text
            console_logs.append({"type": msg.type, "text": text,
                                  "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]})
            if any(kw in text.lower() for kw in ['birth', 'seed', 'payment', 'ptc', 'oauth', 'portal',
                                                   'awaken', 'pb-', 'brain', 'sanitize', 'lets-go', 'incredible']):
                log(f"  CONSOLE:{msg.type.upper()}: {text[:300]}")

        def on_page_error(err):
            js_errors.append({"error": str(err), "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]})
            log(f"  JS-ERROR: {str(err)[:300]}")

        def on_request(req):
            url = req.url
            if any(kw in url for kw in ['birth', 'seed', 'verify', 'log-pay', 'log-conv', 'intake', 'purebrain.ai/api']):
                entry = {"type": "REQ", "url": url, "method": req.method,
                         "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]}
                network_calls.append(entry)
                log(f"  API-REQ: {req.method} {url[:120]}")

        async def on_response(resp):
            url = resp.url
            if any(kw in url for kw in ['birth', 'seed', 'verify', 'log-pay', 'log-conv', 'intake', 'purebrain.ai/api']):
                entry = {"type": "RESP", "url": url, "status": resp.status,
                         "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]}
                # Try to read response body for birth calls
                if 'birth' in url:
                    try:
                        body = await resp.json()
                        entry["body"] = body
                        log(f"  BIRTH-BODY: {json.dumps(body)[:300]}")
                    except:
                        try:
                            text = await resp.text()
                            entry["body_text"] = text[:300]
                            log(f"  BIRTH-TEXT: {text[:300]}")
                        except:
                            pass
                    birth_calls.append(entry)

                network_calls.append(entry)
                log(f"  API-RESP: {resp.status} {url[:120]}")
                if 'seed' in url or 'intake' in url:
                    seed_calls.append(entry)

        page.on("console", on_console)
        page.on("pageerror", on_page_error)
        page.on("request", on_request)
        page.on("response", on_response)

        # === FULL SETUP ===
        log("=== FULL SETUP ===")
        await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        pw_inp = await page.query_selector('input[type="password"]')
        if pw_inp:
            await pw_inp.fill(PAGE_PASSWORD)
            sub = await page.query_selector('input[type="submit"]')
            if sub:
                await sub.click()
            else:
                await pw_inp.press("Enter")
            await asyncio.sleep(12)

        # Simulate payment
        sim = await page.evaluate("""(function() {
            try {
                window.onPaymentComplete('Awakened', 'LETSGO-'+Date.now(), {});
                return {ok: true};
            } catch(e) { return {ok: false, e: e.toString()}; }
        })()""")
        log(f"Sim: {sim}")
        await asyncio.sleep(4)

        await wait_ptc_input_active(page, timeout=45)

        # Q&A
        log("=== Q&A ===")
        mc = len(await page.query_selector_all(".ptc-msg--ai"))
        for val in [TEST_NAME, TEST_EMAIL, TEST_COMPANY, TEST_ROLE]:
            await ptc_send(page, val)
            await wait_for_new_ai_message(page, mc, timeout=12)
            mc = len(await page.query_selector_all(".ptc-msg--ai"))
            await asyncio.sleep(1)

        # Goal
        await ptc_send(page, TEST_GOAL)
        await asyncio.sleep(5)
        mc = len(await page.query_selector_all(".ptc-msg--ai"))
        log(f"After goal: {mc} AI messages")

        # Click through ALL slides
        log("=== CLICKING THROUGH SLIDES ===")
        for i in range(12):
            clicked, text = await click_btn_by_text(page, "Show Me More", timeout=5)
            if not clicked:
                break
            log(f"  Clicked slide {i+1}: {text[:40]}")
            await asyncio.sleep(3)

        # Check for "That's incredible" button
        await asyncio.sleep(2)
        has_incredible = await page.evaluate("""(function() {
            var btns = Array.from(document.querySelectorAll('button'));
            return btns.filter(function(b) { return b.innerText.includes("incredible"); })
                       .map(function(b) { return b.innerText.trim(); });
        })()""")
        log(f"'Incredible' buttons: {has_incredible}")

        await safe_screenshot(page, "D01-before-letsgo.png", "Before 'lets go' click")

        # === CLICK "THAT'S INCREDIBLE - LET'S GO" ===
        log("\n=== CLICKING 'THAT'S INCREDIBLE - LET'S GO' ===")
        log("This is the BIRTH trigger. Watching ALL API calls...")

        birth_before = len(birth_calls)
        letsgo_start = time.time()

        clicked, text = await click_btn_by_text(page, "incredible", timeout=10)
        log(f"Clicked: ok={clicked}, text={text}")

        # Watch carefully for 60 seconds
        log("Watching for 60 seconds post-click...")
        portal_found = False
        for i in range(60):
            await asyncio.sleep(1)

            new_birth = len(birth_calls) > birth_before
            if new_birth and i < 20:
                log(f"  t+{i+1}s: BIRTH API CALLED! Total birth calls: {len(birth_calls)}")

            # Check for portal button and OAuth
            state = await page.evaluate("""(function() {
                var chatArea = document.getElementById('pay-test-post-payment');
                var fullHtml = chatArea ? chatArea.innerHTML : '';

                // Portal button
                var portalBtn = document.querySelector('.ptc-portal-btn');
                var brainStreamLink = chatArea ? chatArea.querySelector('[href*="portal"], [href*="brain"], [href*="oauth"]') : null;
                var enterBtn = Array.from(document.querySelectorAll('a, button')).find(function(el) {
                    var t = (el.innerText||'').trim().toLowerCase();
                    var h = (el.href||el.getAttribute('href')||'').toLowerCase();
                    return (t.includes('enter') && t.includes('brain')) ||
                           (t.includes('connect') && t.includes('brain')) ||
                           h.includes('portal') ||
                           h.includes('claude.ai');
                });

                // All visible buttons in chatbox
                var visibleBtns = [];
                if (chatArea) {
                    chatArea.querySelectorAll('button, a').forEach(function(el) {
                        var s = window.getComputedStyle(el);
                        if (s.display !== 'none' && s.visibility !== 'hidden' && s.opacity !== '0') {
                            var t = (el.innerText||'').trim();
                            var h = el.href || el.getAttribute('href') || '';
                            if (t || h) {
                                visibleBtns.push({tag: el.tagName, text: t.substring(0,80), href: h.substring(0,150)});
                            }
                        }
                    });
                }

                // Latest AI messages
                var aiMsgs = Array.from(document.querySelectorAll('.ptc-msg--ai'));
                var lastAiMsg = aiMsgs.length ? aiMsgs[aiMsgs.length-1].innerText.substring(0,300) : '';

                return {
                    portal_btn: portalBtn ? {
                        text: portalBtn.innerText.trim(),
                        href: portalBtn.href || portalBtn.getAttribute('href') || '',
                        cls: portalBtn.className,
                        display: window.getComputedStyle(portalBtn).display
                    } : null,
                    brain_stream: brainStreamLink ? {
                        tag: brainStreamLink.tagName,
                        text: brainStreamLink.innerText.trim().substring(0,80),
                        href: brainStreamLink.href || brainStreamLink.getAttribute('href') || ''
                    } : null,
                    enter_btn: enterBtn ? {
                        text: enterBtn.innerText.trim().substring(0,80),
                        href: enterBtn.href || enterBtn.getAttribute('href') || ''
                    } : null,
                    has_claude_ai: fullHtml.includes('claude.ai'),
                    has_portal_href: fullHtml.includes('/portal/') || fullHtml.includes('portal.purebrain'),
                    visible_buttons: visibleBtns,
                    last_ai_msg: lastAiMsg,
                    ai_msg_count: aiMsgs.length
                };
            })()""")

            if state['portal_btn'] or state['enter_btn'] or state['brain_stream'] or state['has_claude_ai']:
                log(f"  t+{i+1}s: PORTAL/OAUTH DETECTED!")
                log(f"    portal_btn: {state['portal_btn']}")
                log(f"    enter_btn: {state['enter_btn']}")
                log(f"    brain_stream: {state['brain_stream']}")
                log(f"    has_claude_ai: {state['has_claude_ai']}")
                log(f"    visible_buttons: {[(b['text'][:40], b['href'][:60]) for b in state['visible_buttons']]}")
                await safe_screenshot(page, f"D02-portal-detected-t{i+1}.png", "Portal detected!")
                portal_found = True
                break

            if i % 10 == 9:
                log(f"  t+{i+1}s: No portal yet. birth_calls={len(birth_calls)}, ai_msgs={state['ai_msg_count']}")
                log(f"    Last AI msg: {state['last_ai_msg'][:100]}")
                log(f"    Visible buttons: {[(b['text'][:30], b['href'][:40]) for b in state['visible_buttons']]}")
                await safe_screenshot(page, f"D02-waiting-t{i+1}.png", f"Waiting at t+{i+1}s")

        if not portal_found:
            log("No portal detected in 60s")

        await safe_screenshot(page, "D03-final.png", "Final state")

        # === COMPLETE FINAL ANALYSIS ===
        log("\n=== COMPLETE FINAL ANALYSIS ===")

        final = await page.evaluate("""(function() {
            var chatArea = document.getElementById('pay-test-post-payment');
            var fullHtml = chatArea ? chatArea.innerHTML : '';
            var fullText = chatArea ? chatArea.innerText : '';

            var msgs = Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-msg--user')).map(function(m) {
                return {type: m.className.includes('ai') ? 'ai' : 'user', text: m.innerText.trim().substring(0,400)};
            });

            var allLinks = Array.from(chatArea ? chatArea.querySelectorAll('a') : []).map(function(a) {
                return {text: a.innerText.trim().substring(0,80), href: a.href||a.getAttribute('href')||'', cls: a.className};
            });

            var allBtns = Array.from(chatArea ? chatArea.querySelectorAll('button') : []).map(function(b) {
                var s = window.getComputedStyle(b);
                return {text: b.innerText.trim().substring(0,80), cls: b.className, display: s.display};
            });

            // Find portal vortex or any brain-stream element
            var vortex = document.querySelector('.portal-vortex');
            var vortexInfo = vortex ? {
                cls: vortex.className,
                children: vortex.children.length,
                text: vortex.innerText.substring(0,100),
                display: window.getComputedStyle(vortex).display
            } : null;

            return {
                all_messages: msgs,
                all_links: allLinks,
                all_buttons: allBtns,
                portal_vortex: vortexInfo,
                has_claude_ai: fullHtml.includes('claude.ai'),
                full_text_tail: fullText.substring(Math.max(0, fullText.length - 1200)),
                html_length: fullHtml.length,
                input_row: (function() {
                    var r = document.getElementById('ptc-input-row');
                    return r ? window.getComputedStyle(r).display : 'not-found';
                })()
            };
        })()""")

        log(f"\nAll messages ({len(final['all_messages'])}):")
        for msg in final['all_messages']:
            log(f"  [{msg['type'].upper()}]: {msg['text'][:200]}")

        log(f"\nAll links in chat area:")
        for l in final['all_links']:
            log(f"  '{l['text']}' -> {l['href'][:100]}")

        log(f"\nAll buttons in chat area:")
        for b in final['all_buttons']:
            log(f"  '{b['text']}' cls={b['cls'][:60]} display={b['display']}")

        log(f"\nPortal vortex: {final['portal_vortex']}")
        log(f"Has claude.ai: {final['has_claude_ai']}")
        log(f"Input row: {final['input_row']}")

        log(f"\nFull text tail (last 1200 chars):")
        log(final['full_text_tail'])

        log(f"\n=== API CALLS ===")
        log(f"Birth calls ({len(birth_calls)}):")
        for c in birth_calls:
            log(f"  {c.get('type')} {c.get('status','')} {c['url'][:100]}")
            if c.get('body'):
                log(f"  BODY: {json.dumps(c['body'])[:300]}")
        log(f"Seed calls ({len(seed_calls)}):")
        for c in seed_calls:
            log(f"  {c}")
        log(f"All API calls ({len(network_calls)}):")
        for c in network_calls:
            log(f"  {c.get('type')} {c.get('status','')} {c.get('method','')} {c['url'][:100]}")

        log(f"\n=== CONSOLE ERRORS ===")
        for e in console_logs:
            if e['type'] == 'error' and not any(n in e['text'] for n in ['google-analytics', 'clarity', 'secureserver']):
                log(f"  [{e['time']}]: {e['text'][:250]}")

        log(f"\n=== JS ERRORS ===")
        for e in js_errors:
            log(f"  [{e['time']}]: {e['error'][:250]}")

        report = {
            "date": datetime.now().isoformat(),
            "final": final,
            "birth_calls": birth_calls,
            "seed_calls": seed_calls,
            "all_network": network_calls,
            "js_errors": js_errors,
            "portal_found": portal_found
        }
        rpath = f"{OUT_DIR}/letsgo-report.json"
        with open(rpath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        log(f"Report: {rpath}")

        await browser.close()
        return report

if __name__ == "__main__":
    asyncio.run(run())
