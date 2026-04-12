#!/usr/bin/env python3
"""
Continue E2E test: Send goal answer, observe BIRTH API trigger, check portal button.
This runs fresh from top, gets to role, sends goal, observes what happens.
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

async def run():
    from playwright.async_api import async_playwright

    log(f"Starting goal+birth test on {PAGE_URL}")

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
            if any(kw in text.lower() for kw in ['birth', 'seed', 'payment', 'ptc', 'oauth', 'portal', 'init', 'sanitize', 'pb-']):
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

        # --- Navigate and setup ---
        log("=== NAVIGATE ===")
        await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)
        await safe_screenshot(page, "B01-initial.png", "Initial load")

        pw_inp = await page.query_selector('input[type="password"]')
        if pw_inp:
            log("Password gate found - entering password")
            await pw_inp.fill(PAGE_PASSWORD)
            sub = await page.query_selector('input[type="submit"]')
            if sub:
                await sub.click()
            else:
                await pw_inp.press("Enter")
            await asyncio.sleep(12)
            await safe_screenshot(page, "B02-after-password.png", "After password")
        else:
            await asyncio.sleep(5)

        # Verify sanitizeText is available
        fn_check = await page.evaluate("""(function() {
            return {
                sanitizeText: typeof window.sanitizeText,
                onPaymentComplete: typeof window.onPaymentComplete,
                launchPostPaymentFlow: typeof window.launchPostPaymentFlow,
                initPayTestFlow: typeof window.initPayTestFlow
            };
        })()""")
        log(f"Function availability: {json.dumps(fn_check)}")

        # --- Simulate payment ---
        log("\n=== SIMULATE PAYMENT ===")
        sim_result = await page.evaluate("""(function() {
            try {
                if (typeof window.onPaymentComplete === 'function') {
                    window.onPaymentComplete('Awakened', 'BIRTH-TEST-'+Date.now(), {});
                    return {called: true};
                }
                return {called: false, reason: 'not a function: ' + typeof window.onPaymentComplete};
            } catch(e) {
                return {called: false, reason: e.toString()};
            }
        })()""")
        log(f"Simulation result: {sim_result}")

        await asyncio.sleep(4)

        # --- Wait for PTC ---
        log("\n=== WAIT FOR PTC ===")
        ptc_active = await wait_ptc_input_active(page, timeout=45)
        log(f"PTC active: {ptc_active}")
        await safe_screenshot(page, "B03-ptc-active.png", "PTC active state")

        if not ptc_active:
            log("FAIL: PTC not active - aborting")
            await browser.close()
            return

        # --- Get initial AI message count ---
        initial_msgs = await page.query_selector_all(".ptc-msg--ai")
        msg_count = len(initial_msgs)
        log(f"Initial AI message count: {msg_count}")

        # Get first AI message
        if initial_msgs:
            first_msg_text = await initial_msgs[-1].inner_text()
            log(f"First AI message: {first_msg_text[:100]}")

        # --- Q1: Name ---
        log("\n=== Q1: SEND NAME ===")
        ok, how = await ptc_send(page, TEST_NAME)
        log(f"Sent name '{TEST_NAME}': ok={ok}, how={how}")
        new_msg = await wait_for_new_ai_message(page, msg_count, timeout=15)
        msg_count = len(await page.query_selector_all(".ptc-msg--ai"))
        log(f"AI reply to name: {(new_msg or 'timeout')[:100]}")
        await asyncio.sleep(1)

        # --- Q2: Email ---
        log("\n=== Q2: SEND EMAIL ===")
        ok, how = await ptc_send(page, TEST_EMAIL)
        log(f"Sent email: ok={ok}, how={how}")
        new_msg = await wait_for_new_ai_message(page, msg_count, timeout=15)
        msg_count = len(await page.query_selector_all(".ptc-msg--ai"))
        log(f"AI reply to email: {(new_msg or 'timeout')[:100]}")
        await asyncio.sleep(1)

        # --- Q3: Company ---
        log("\n=== Q3: SEND COMPANY ===")
        ok, how = await ptc_send(page, TEST_COMPANY)
        log(f"Sent company: ok={ok}, how={how}")
        new_msg = await wait_for_new_ai_message(page, msg_count, timeout=15)
        msg_count = len(await page.query_selector_all(".ptc-msg--ai"))
        log(f"AI reply to company: {(new_msg or 'timeout')[:100]}")
        await asyncio.sleep(1)

        # --- Q4: Role ---
        log("\n=== Q4: SEND ROLE ===")
        ok, how = await ptc_send(page, TEST_ROLE)
        log(f"Sent role: ok={ok}, how={how}")
        new_msg = await wait_for_new_ai_message(page, msg_count, timeout=15)
        msg_count = len(await page.query_selector_all(".ptc-msg--ai"))
        log(f"AI reply to role: {(new_msg or 'timeout')[:150]}")
        await safe_screenshot(page, "B04-before-goal.png", "Before goal - role answered")
        await asyncio.sleep(1)

        # Check if BIRTH was already triggered by role (as in sandbox-2 behavior)
        birth_triggered_before_goal = len(birth_calls) > 0
        log(f"BIRTH triggered before goal answer: {birth_triggered_before_goal} (birth_calls={len(birth_calls)})")

        # --- Q5: GOAL (KEY STEP) ---
        log("\n=== Q5: SEND GOAL (KEY STEP - watch for BIRTH) ===")
        log(f"Current birth_calls count: {len(birth_calls)}")
        log(f"Sending goal: '{TEST_GOAL}'")

        goal_start_time = time.time()
        try:
            ok, how = await ptc_send(page, TEST_GOAL)
            log(f"Goal send result: ok={ok}, how={how}")
        except Exception as e:
            log(f"Goal send EXCEPTION: {e}")
            ok = False

        # Watch carefully for 30 seconds - capture BIRTH trigger timing
        log("Watching for BIRTH API call for 30 seconds...")
        birth_before = len(birth_calls)
        for i in range(30):
            await asyncio.sleep(1)
            if len(birth_calls) > birth_before:
                log(f"BIRTH API CALLED at t+{i+1}s after goal send!")
                break
            if i % 5 == 0:
                log(f"  Waiting... t+{i}s, birth_calls={len(birth_calls)}, seed_calls={len(seed_calls)}")

        await safe_screenshot(page, "B05-after-goal.png", "After goal sent")

        # --- Check state after goal ---
        log("\n=== STATE AFTER GOAL ===")
        post_goal_state = await page.evaluate("""(function() {
            var result = {
                messages: [],
                input_row_display: 'unknown',
                portal_button: null,
                brain_stream_link: null,
                oauth_elements: [],
                i_have_key: [],
                authorize_buttons: []
            };

            // All messages
            document.querySelectorAll('.ptc-msg--ai, .ptc-msg--user').forEach(function(m) {
                result.messages.push({
                    type: m.className.includes('ai') ? 'ai' : 'user',
                    text: m.innerText.substring(0, 300)
                });
            });

            // Input row
            var row = document.getElementById('ptc-input-row');
            if (row) {
                result.input_row_display = window.getComputedStyle(row).display;
            }

            // Portal button
            var portalBtn = document.querySelector('.ptc-portal-btn');
            if (portalBtn) {
                var s = window.getComputedStyle(portalBtn);
                result.portal_button = {
                    href: portalBtn.href || portalBtn.getAttribute('href') || '',
                    text: portalBtn.innerText.substring(0, 100),
                    display: s.display,
                    opacity: s.opacity,
                    cls: portalBtn.className
                };
            }

            // Brain stream link
            var bsl = document.querySelector('[class*="brain-stream"], [href*="brain-stream"]');
            if (bsl) {
                result.brain_stream_link = {
                    href: bsl.href || bsl.getAttribute('href') || '',
                    text: bsl.innerText.substring(0, 80),
                    cls: bsl.className
                };
            }

            // Look for ALL links and buttons in the chat area
            var chatArea = document.getElementById('pay-test-post-payment');
            if (chatArea) {
                chatArea.querySelectorAll('a, button').forEach(function(el) {
                    var href = el.href || el.getAttribute('href') || '';
                    var text = el.innerText.trim().substring(0, 100);
                    var cls = el.className || '';
                    var s = window.getComputedStyle(el);
                    if (text || href) {
                        if (text.toLowerCase().includes('authorize') || href.includes('claude.ai') || href.includes('oauth')) {
                            result.authorize_buttons.push({tag: el.tagName, text: text, href: href, display: s.display});
                        }
                        if (text.toLowerCase().includes('key') || text.toLowerCase().includes('have my key')) {
                            result.i_have_key.push({tag: el.tagName, text: text, href: href});
                        }
                        if (text.toLowerCase().includes('brain') || text.toLowerCase().includes('portal') || href.includes('portal')) {
                            result.oauth_elements.push({tag: el.tagName, text: text, href: href.substring(0,150), cls: cls.substring(0,60), display: s.display});
                        }
                    }
                });
            }

            return result;
        })()""")

        log(f"\nPost-goal state:")
        log(f"  Total messages: {len(post_goal_state['messages'])}")
        log(f"  Input row display: {post_goal_state['input_row_display']}")
        log(f"  Portal button: {post_goal_state['portal_button']}")
        log(f"  Brain stream link: {post_goal_state['brain_stream_link']}")
        log(f"  Authorize buttons: {post_goal_state['authorize_buttons']}")
        log(f"  'I have my key' buttons: {post_goal_state['i_have_key']}")
        log(f"  OAuth elements in chat: {post_goal_state['oauth_elements']}")

        log(f"\n  ALL MESSAGES:")
        for msg in post_goal_state['messages']:
            log(f"  [{msg['type'].upper()}]: {msg['text'][:200]}")

        # --- Wait longer and check for birth-related UI changes ---
        log("\n=== WATCHING FOR UI CHANGES (30 more seconds) ===")
        for i in range(30):
            await asyncio.sleep(1)

            # Check for any new elements
            new_elements = await page.evaluate("""(function() {
                var chatArea = document.getElementById('pay-test-post-payment');
                if (!chatArea) return null;
                var links = Array.from(chatArea.querySelectorAll('a')).map(function(a) {
                    return {href: a.href||a.getAttribute('href')||'', text: a.innerText.trim().substring(0,80), cls: a.className};
                });
                var btns = Array.from(chatArea.querySelectorAll('button')).map(function(b) {
                    return {text: b.innerText.trim().substring(0,80), cls: b.className};
                });
                var portal = document.querySelector('.ptc-portal-btn');
                return {
                    links: links,
                    buttons: btns,
                    portal_found: !!portal,
                    birth_calls_in_page: (document.body.innerHTML.match(/birth\\/start/g)||[]).length
                };
            })()""")

            if new_elements:
                has_oauth_link = any('claude.ai' in (l.get('href','')) or 'oauth' in (l.get('href','')) for l in new_elements['links'])
                portal_found = new_elements.get('portal_found', False)

                if has_oauth_link or portal_found or len(birth_calls) > birth_before:
                    log(f"  t+{i+1}s: CHANGE DETECTED! oauth_link={has_oauth_link}, portal={portal_found}, birth_calls={len(birth_calls)}")
                    await safe_screenshot(page, f"B06-change-t{i+1}.png", f"Change at t+{i+1}s")

                    # Get full state
                    if new_elements['links']:
                        log(f"  Links: {[(l['text'][:40], l['href'][:60]) for l in new_elements['links'] if l['href'] or l['text']]}")
                    break

                if i % 10 == 9:
                    log(f"  t+{i+1}s: No changes yet. birth_calls={len(birth_calls)}, links={len(new_elements['links'])}")
                    await safe_screenshot(page, f"B06-waiting-t{i+1}.png", f"Waiting at t+{i+1}s")
        else:
            log("  No UI changes detected in 30s after goal")

        await safe_screenshot(page, "B07-post-goal-final.png", "Post-goal final state")

        # --- Get FULL final state ---
        log("\n=== FINAL COMPLETE STATE ===")
        final = await page.evaluate("""(function() {
            var chatArea = document.getElementById('pay-test-post-payment');
            var fullHtml = chatArea ? chatArea.innerHTML : '';

            // Find portal button with ALL properties
            var portalBtn = document.querySelector('.ptc-portal-btn') ||
                            document.querySelector('[class*="portal"]') ||
                            chatArea && chatArea.querySelector('a[href*="portal"], a[href*="brain-stream"]');

            var portalInfo = null;
            if (portalBtn) {
                var s = window.getComputedStyle(portalBtn);
                portalInfo = {
                    found: true,
                    tag: portalBtn.tagName,
                    text: portalBtn.innerText.trim(),
                    href: portalBtn.href || portalBtn.getAttribute('href') || '',
                    cls: portalBtn.className,
                    display: s.display,
                    opacity: s.opacity,
                    backgroundColor: s.backgroundColor,
                    color: s.color,
                    disabled: portalBtn.disabled || portalBtn.getAttribute('disabled') !== null,
                    ariaDisabled: portalBtn.getAttribute('aria-disabled')
                };
            }

            // Check for OAuth URL in the page
            var oauthUrlMatch = fullHtml.match(/https:\/\/claude\.ai[^"'\\s]*/);
            var oauthUrl = oauthUrlMatch ? oauthUrlMatch[0] : null;

            // All messages in order
            var msgs = [];
            document.querySelectorAll('.ptc-msg--ai, .ptc-msg--user').forEach(function(m) {
                msgs.push({type: m.className.includes('ai') ? 'ai' : 'user', text: m.innerText.trim().substring(0,300)});
            });

            // Check ptc-input-row
            var inputRow = document.getElementById('ptc-input-row');
            var inputRowDisplay = inputRow ? window.getComputedStyle(inputRow).display : 'not-found';

            // Any "authorize" or "connect" buttons
            var authBtns = [];
            document.querySelectorAll('[class*="authorize"], [class*="connect"], [class*="oauth"], [id*="oauth"]').forEach(function(el) {
                authBtns.push({tag: el.tagName, cls: el.className.substring(0,60), text: el.innerText.substring(0,80), display: window.getComputedStyle(el).display});
            });

            return {
                portal_button: portalInfo,
                oauth_url_in_html: oauthUrl,
                message_count: msgs.length,
                messages: msgs,
                input_row_display: inputRowDisplay,
                authorize_buttons: authBtns,
                full_html_length: fullHtml.length,
                has_brain_stream: fullHtml.includes('brain-stream') || fullHtml.includes('brain stream'),
                has_claude_ai: fullHtml.includes('claude.ai')
            };
        })()""")

        log(f"\n=== DEFINITIVE FINDINGS ===")
        log(f"Total messages: {final['message_count']}")
        log(f"Input row display: {final['input_row_display']}")
        log(f"Portal button: {json.dumps(final['portal_button'], indent=2)}")
        log(f"OAuth URL in HTML: {final['oauth_url_in_html']}")
        log(f"Has brain-stream: {final['has_brain_stream']}")
        log(f"Has claude.ai: {final['has_claude_ai']}")
        log(f"Authorize buttons: {final['authorize_buttons']}")
        log(f"\nAll messages:")
        for msg in final['messages']:
            log(f"  [{msg['type'].upper()}]: {msg['text'][:200]}")

        log(f"\n=== API CALL SUMMARY ===")
        log(f"Birth API calls: {len(birth_calls)}")
        for c in birth_calls:
            log(f"  {c['type']} {c.get('status','')} {c['url'][:100]} @ {c['time']}")
        log(f"Seed/intake calls: {len(seed_calls)}")
        for c in seed_calls:
            log(f"  {c['type']} {c.get('status','')} {c['url'][:100]} @ {c['time']}")
        log(f"All API calls: {len(network_calls)}")
        for c in network_calls:
            log(f"  {c['type']} {c.get('status','')} {c.get('method','')} {c['url'][:100]} @ {c['time']}")

        log(f"\n=== CONSOLE ERRORS ===")
        for e in console_logs:
            if e['type'] == 'error' and not any(n in e['text'] for n in ['google-analytics', 'clarity', 'secureserver']):
                log(f"  ERROR [{e['time']}]: {e['text'][:250]}")

        log(f"\n=== JS PAGE ERRORS ===")
        for e in js_errors:
            log(f"  [{e['time']}]: {e['error'][:250]}")

        # Save combined report
        report = {
            "date": datetime.now().isoformat(),
            "url": PAGE_URL,
            "birth_calls": birth_calls,
            "seed_calls": seed_calls,
            "all_network_calls": network_calls,
            "final_state": final,
            "js_errors": js_errors,
            "console_errors": [l for l in console_logs if l['type'] == 'error'],
            "birth_triggered_before_goal": birth_triggered_before_goal,
            "ptc_was_active": ptc_active
        }
        report_path = f"{OUT_DIR}/goal-birth-report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        log(f"\nReport saved: {report_path}")

        await browser.close()
        return report

if __name__ == "__main__":
    asyncio.run(run())
