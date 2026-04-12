#!/usr/bin/env python3
"""
Continue E2E: Click through all 10 slides, observe what happens at end.
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
            path=path,
            clip={"x": 0, "y": 0, "width": 1440, "height": 900},
            timeout=20000
        )
        log(f"SHOT: {filename}")
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

async def get_slide_state(page):
    """Get current slide number and content."""
    return await page.evaluate("""(function() {
        // Look for slide counter
        var counters = document.querySelectorAll('[class*="slide"], [class*="curtain"]');
        var slideText = '';
        counters.forEach(function(el) {
            slideText += el.innerText + ' | ';
        });

        // Find "Show Me More" or "Next" button
        var showMore = document.querySelector('.ptc-slide-btn, [class*="slide-btn"], [class*="show-more"]');
        var allBtns = Array.from(document.querySelectorAll('button')).filter(function(b) {
            var t = b.innerText.trim();
            return t.includes('Show Me More') || t.includes('Next') || t.includes('→') || t.includes('Continue');
        });

        // Find slide card
        var slideCard = document.querySelector('.ptc-slide-card, [class*="slide-card"], [class*="curtain-card"]');
        var slideContent = slideCard ? slideCard.innerText.substring(0, 300) : '';

        // Look for "OF" pattern like "1 OF 10"
        var ofPattern = document.body.innerHTML.match(/(\d+)\s+OF\s+(\d+)/i);
        var slideNum = ofPattern ? ofPattern[1] : null;
        var totalSlides = ofPattern ? ofPattern[2] : null;

        // Look for "BEHIND THE CURTAIN" text
        var btc = document.querySelector('[class*="btc"], [class*="behind"], [class*="curtain"]');
        var btcText = btc ? btc.innerText.substring(0, 100) : '';

        // Portal button check
        var portalBtn = document.querySelector('.ptc-portal-btn, [class*="portal-btn"]');
        var portalInfo = null;
        if (portalBtn) {
            var s = window.getComputedStyle(portalBtn);
            portalInfo = {
                text: portalBtn.innerText.substring(0, 100),
                href: portalBtn.href || portalBtn.getAttribute('href') || '',
                display: s.display,
                opacity: s.opacity,
                cls: portalBtn.className
            };
        }

        // All buttons in chatbox area
        var chatArea = document.getElementById('pay-test-post-payment');
        var chatBtns = [];
        if (chatArea) {
            chatArea.querySelectorAll('button, a').forEach(function(el) {
                var t = el.innerText.trim().substring(0, 80);
                var s = window.getComputedStyle(el);
                if (t && s.display !== 'none') {
                    chatBtns.push({
                        tag: el.tagName,
                        text: t,
                        href: el.href || el.getAttribute('href') || '',
                        cls: el.className.substring(0, 60),
                        display: s.display
                    });
                }
            });
        }

        // full visible text of post payment area
        var visibleText = chatArea ? chatArea.innerText.substring(chatArea.innerText.length - 800) : '';

        return {
            slide_num: slideNum,
            total_slides: totalSlides,
            btc_text: btcText,
            slide_content: slideContent,
            show_more_buttons: allBtns.map(function(b) { return b.innerText.trim().substring(0, 60); }),
            portal_button: portalInfo,
            chat_buttons: chatBtns,
            visible_text_tail: visibleText,
            input_row_display: (function() {
                var r = document.getElementById('ptc-input-row');
                return r ? window.getComputedStyle(r).display : 'not-found';
            })()
        };
    })()""")

async def click_show_more(page):
    """Click 'Show Me More' button."""
    try:
        # Try specific selectors first
        for sel in ['.ptc-slide-btn', '[class*="slide-btn"]', '[class*="show-more"]']:
            btn = await page.query_selector(sel)
            if btn and await btn.is_visible():
                await btn.click()
                return True, sel

        # Try by text content
        btns = await page.query_selector_all("button")
        for btn in btns:
            try:
                text = await btn.inner_text()
                text = text.strip()
                if 'Show Me More' in text or ('Next' in text and len(text) < 20):
                    if await btn.is_visible():
                        await btn.click()
                        return True, f"text:{text[:40]}"
            except:
                pass

        return False, "not found"
    except Exception as e:
        return False, str(e)

async def run():
    from playwright.async_api import async_playwright

    log(f"Starting slides test on {PAGE_URL}")

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

        def on_console(msg):
            text = msg.text
            console_logs.append({"type": msg.type, "text": text,
                                  "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]})
            if any(kw in text.lower() for kw in ['birth', 'seed', 'payment', 'ptc', 'oauth', 'portal', 'slide', 'curtain', 'pb-', 'sanitize']):
                log(f"  CONSOLE:{msg.type.upper()}: {text[:300]}")

        def on_page_error(err):
            js_errors.append({"error": str(err), "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]})
            log(f"  JS-ERROR: {str(err)[:300]}")

        def on_request(req):
            url = req.url
            if any(kw in url for kw in ['birth', 'seed', 'verify', 'log-pay', 'log-conv', 'intake']):
                entry = {"type": "REQ", "url": url, "method": req.method,
                         "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]}
                network_calls.append(entry)
                log(f"  API-REQ: {req.method} {url[:120]}")

        def on_response(resp):
            url = resp.url
            if any(kw in url for kw in ['birth', 'seed', 'verify', 'log-pay', 'log-conv', 'intake']):
                entry = {"type": "RESP", "url": url, "status": resp.status,
                         "time": datetime.now().strftime("%H:%M:%S.%f")[:-3]}
                network_calls.append(entry)
                log(f"  API-RESP: {resp.status} {url[:120]}")
                if 'birth' in url:
                    birth_calls.append(entry)
                if 'seed' in url or 'intake' in url:
                    seed_calls.append(entry)

        page.on("console", on_console)
        page.on("pageerror", on_page_error)
        page.on("request", on_request)
        page.on("response", on_response)

        # === SETUP: Navigate, password, simulate payment ===
        log("=== SETUP: Navigate and simulate payment ===")
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
                if (typeof window.onPaymentComplete === 'function') {
                    window.onPaymentComplete('Awakened', 'SLIDES-TEST-'+Date.now(), {});
                    return {ok: true};
                }
                return {ok: false, reason: typeof window.onPaymentComplete};
            } catch(e) { return {ok: false, reason: e.toString()}; }
        })()""")
        log(f"Simulation: {sim}")
        await asyncio.sleep(4)

        # Wait for PTC
        ptc_active = await wait_ptc_input_active(page, timeout=45)
        log(f"PTC active: {ptc_active}")
        if not ptc_active:
            log("FAIL: PTC not active")
            await browser.close()
            return

        # === Q&A sequence ===
        log("=== Q&A SEQUENCE ===")
        msg_count = len(await page.query_selector_all(".ptc-msg--ai"))

        # Name
        await ptc_send(page, TEST_NAME)
        await wait_for_new_ai_message(page, msg_count, timeout=12)
        msg_count = len(await page.query_selector_all(".ptc-msg--ai"))
        await asyncio.sleep(1)

        # Email
        await ptc_send(page, TEST_EMAIL)
        await wait_for_new_ai_message(page, msg_count, timeout=12)
        msg_count = len(await page.query_selector_all(".ptc-msg--ai"))
        await asyncio.sleep(1)

        # Company
        await ptc_send(page, TEST_COMPANY)
        await wait_for_new_ai_message(page, msg_count, timeout=12)
        msg_count = len(await page.query_selector_all(".ptc-msg--ai"))
        await asyncio.sleep(1)

        # Role
        await ptc_send(page, TEST_ROLE)
        await wait_for_new_ai_message(page, msg_count, timeout=12)
        msg_count = len(await page.query_selector_all(".ptc-msg--ai"))
        await asyncio.sleep(1)

        # Goal
        log("Sending goal...")
        await ptc_send(page, TEST_GOAL)
        await asyncio.sleep(4)  # Wait for slide to render
        msg_count = len(await page.query_selector_all(".ptc-msg--ai"))
        log(f"After goal: {msg_count} AI messages")

        await safe_screenshot(page, "C01-slide-1.png", "Slide 1 of 10")

        # === CLICK THROUGH ALL 10 SLIDES ===
        log("\n=== CLICKING THROUGH SLIDES ===")

        slide_contents = []
        for slide_num in range(1, 12):  # Click up to 11 times to be safe
            state = await get_slide_state(page)
            log(f"\n--- SLIDE STATE ---")
            log(f"  Slide: {state['slide_num']} of {state['total_slides']}")
            log(f"  Show More buttons: {state['show_more_buttons']}")
            log(f"  Portal button: {state['portal_button']}")
            log(f"  Chat buttons: [{', '.join([b['text'][:40] for b in state['chat_buttons']])}]")
            log(f"  Input row: {state['input_row_display']}")
            log(f"  Visible text tail: {state['visible_text_tail'][-300:]}")

            slide_contents.append({
                "slide_attempt": slide_num,
                "state": state,
                "birth_calls_so_far": len(birth_calls),
                "seed_calls_so_far": len(seed_calls)
            })

            # Check if we've hit the portal button (no more slides)
            if state['portal_button'] and state['portal_button'].get('href'):
                log(f"PORTAL BUTTON FOUND with href: {state['portal_button']['href']}")
                await safe_screenshot(page, f"C{slide_num+1:02d}-portal-found.png", "Portal button found")
                break

            # Check if there's no "Show Me More" button
            if not state['show_more_buttons']:
                # Check if we're done with slides
                if state['slide_num'] and state['total_slides']:
                    if state['slide_num'] == state['total_slides']:
                        log("Last slide reached - no Show Me More button")
                        await safe_screenshot(page, f"C{slide_num+1:02d}-last-slide.png", "Last slide")
                        break

            # Click Show Me More
            ok, how = await click_show_more(page)
            log(f"Clicked Show Me More: ok={ok}, how={how}")

            if not ok:
                # No button found - maybe we're done
                log("No Show Me More button - checking full state")
                await safe_screenshot(page, f"C{slide_num+1:02d}-no-btn.png", "No button")

                # Wait a bit - maybe something is loading
                for w in range(10):
                    await asyncio.sleep(1)
                    state = await get_slide_state(page)
                    if state['show_more_buttons'] or (state['portal_button'] and state['portal_button'].get('href')):
                        log(f"  Found after {w+1}s wait: buttons={state['show_more_buttons']}, portal={state['portal_button']}")
                        break
                    if w == 4:
                        await safe_screenshot(page, f"C{slide_num+1:02d}-waiting-{w}.png", f"Waiting {w}s")
                else:
                    log("Still no button after 10s - ending slide loop")
                    break

            await asyncio.sleep(3)  # Wait for next slide to render
            await safe_screenshot(page, f"C{slide_num+1:02d}-slide-{slide_num+1}.png", f"After click {slide_num}")

        # === FINAL STATE AFTER ALL SLIDES ===
        log("\n=== FINAL STATE AFTER SLIDES ===")
        await asyncio.sleep(5)  # Wait for any delayed triggers

        final_state = await page.evaluate("""(function() {
            var chatArea = document.getElementById('pay-test-post-payment');
            var fullHtml = chatArea ? chatArea.innerHTML : '';
            var fullText = chatArea ? chatArea.innerText : '';

            // Find ALL links and buttons
            var all_interactive = [];
            if (chatArea) {
                chatArea.querySelectorAll('a, button, [role="button"]').forEach(function(el) {
                    var s = window.getComputedStyle(el);
                    var href = el.href || el.getAttribute('href') || '';
                    var text = el.innerText.trim().substring(0, 100);
                    if (s.display !== 'none' && (text || href)) {
                        all_interactive.push({
                            tag: el.tagName,
                            text: text,
                            href: href.substring(0, 200),
                            cls: el.className.substring(0, 60),
                            display: s.display,
                            opacity: s.opacity
                        });
                    }
                });
            }

            // Specifically find portal/brain-stream button
            var portalBtn = document.querySelector('.ptc-portal-btn');
            var brainStreamBtn = document.querySelector('[class*="brain-stream"]') ||
                                 document.querySelector('[href*="brain-stream"]') ||
                                 document.querySelector('[href*="portal"]');
            var enterBrainBtn = Array.from(document.querySelectorAll('a, button')).find(function(el) {
                var t = el.innerText.trim().toLowerCase();
                return t.includes('enter') && (t.includes('brain') || t.includes('stream'));
            });

            // Check for OAuth URL
            var oauthSearch = fullHtml.match(/href="([^"]*claude\.ai[^"]*)/);
            var claudeAiUrl = oauthSearch ? oauthSearch[1] : null;

            // All messages
            var msgs = [];
            document.querySelectorAll('.ptc-msg--ai, .ptc-msg--user').forEach(function(m) {
                msgs.push({type: m.className.includes('ai') ? 'ai' : 'user', text: m.innerText.trim().substring(0, 300)});
            });

            return {
                portal_btn_found: !!portalBtn,
                portal_btn_info: portalBtn ? {
                    text: portalBtn.innerText.trim(),
                    href: portalBtn.href || portalBtn.getAttribute('href') || '',
                    cls: portalBtn.className,
                    display: window.getComputedStyle(portalBtn).display,
                    opacity: window.getComputedStyle(portalBtn).opacity
                } : null,
                brain_stream_btn: brainStreamBtn ? {
                    text: brainStreamBtn.innerText.trim().substring(0, 100),
                    href: brainStreamBtn.href || brainStreamBtn.getAttribute('href') || '',
                    cls: brainStreamBtn.className
                } : null,
                enter_brain_btn: enterBrainBtn ? {
                    text: enterBrainBtn.innerText.trim().substring(0, 100),
                    href: enterBrainBtn.href || enterBrainBtn.getAttribute('href') || ''
                } : null,
                claude_ai_url: claudeAiUrl,
                has_oauth: fullHtml.includes('claude.ai') || fullHtml.includes('oauth'),
                all_interactive_elements: all_interactive,
                all_messages: msgs,
                full_text_tail: fullText.substring(Math.max(0, fullText.length - 1000)),
                input_row_display: (function() {
                    var r = document.getElementById('ptc-input-row');
                    return r ? window.getComputedStyle(r).display : 'not-found';
                })(),
                html_has_brain_stream: fullHtml.includes('brain-stream'),
                html_has_enter: fullHtml.toLowerCase().includes('enter your') || fullHtml.toLowerCase().includes("enter sage") || fullHtml.toLowerCase().includes('brain stream')
            };
        })()""")

        log("\n=== DEFINITIVE PORTAL/BUTTON FINDINGS ===")
        log(f"Portal button found: {final_state['portal_btn_found']}")
        log(f"Portal button info: {json.dumps(final_state['portal_btn_info'], indent=2)}")
        log(f"Brain stream button: {final_state['brain_stream_btn']}")
        log(f"Enter brain button: {final_state['enter_brain_btn']}")
        log(f"Claude.ai URL: {final_state['claude_ai_url']}")
        log(f"Has OAuth: {final_state['has_oauth']}")
        log(f"Has brain-stream in HTML: {final_state['html_has_brain_stream']}")
        log(f"Input row display: {final_state['input_row_display']}")
        log(f"\nAll interactive elements:")
        for el in final_state['all_interactive_elements']:
            log(f"  {el['tag']}.{el['cls'][:40]}: '{el['text'][:60]}' href={el['href'][:80]} display={el['display']}")

        log(f"\nFull text tail (last 1000 chars):")
        log(final_state['full_text_tail'])

        log(f"\nAll messages ({len(final_state['all_messages'])}):")
        for msg in final_state['all_messages']:
            log(f"  [{msg['type'].upper()}]: {msg['text'][:200]}")

        log(f"\n=== BIRTH/SEED API CALLS ===")
        log(f"Birth calls: {len(birth_calls)}")
        for c in birth_calls:
            log(f"  {c}")
        log(f"Seed/intake calls: {len(seed_calls)}")
        log(f"Total API calls: {len(network_calls)}")

        await safe_screenshot(page, "C-FINAL.png", "Final state")

        # Save report
        report = {
            "date": datetime.now().isoformat(),
            "slide_walk": slide_contents,
            "final_state": final_state,
            "birth_calls": birth_calls,
            "seed_calls": seed_calls,
            "network_calls": network_calls,
            "js_errors": js_errors
        }
        report_path = f"{OUT_DIR}/slides-report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        log(f"\nReport: {report_path}")

        await browser.close()
        return report

if __name__ == "__main__":
    asyncio.run(run())
