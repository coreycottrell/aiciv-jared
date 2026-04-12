#!/usr/bin/env python3
"""
E2E Full Payment Flow Test: pay-test-sandbox-2 (LIVE PAGE) - v2
Date: 2026-03-02
Fixed: Use JS click for #proCta (element exists but not viewport-visible)
"""

import asyncio
import json
import os
import re
import time
from pathlib import Path
from datetime import datetime

SESSION_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/e2e-live-sandbox2-20260302"
REPORT_PATH = "/home/jared/projects/AI-CIV/aether/exports/e2e-live-sandbox2-report-20260302.md"
os.makedirs(SESSION_DIR, exist_ok=True)

LIVE_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"

SEED_ENDPOINTS = ["104.248.239.98", "178.156.229.207", "api.purebrain.ai/api/intake", "8099", "8200"]

screenshot_count = [0]
network_requests = []
console_all = []
page_errors = []
seed_fires = []

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def ss_path(label):
    screenshot_count[0] += 1
    return f"{SESSION_DIR}/{screenshot_count[0]:03d}-{label}.png"

def is_seed_request(url):
    for ep in SEED_ENDPOINTS:
        if ep in url:
            return True
    return False

def classify_url(url):
    if "8099" in url: return "BIRTH_WEBHOOK"
    if "8200" in url: return "WITNESS_SEED"
    if "104.248" in url or "178.156" in url: return "WITNESS_DIRECT"
    if "api.purebrain.ai" in url: return "PUREBRAIN_API"
    if "paypal" in url.lower(): return "PAYPAL"
    if "workers.dev" in url: return "CF_WORKER"
    if "claude.ai" in url: return "CLAUDE_API"
    return "OTHER"

async def run_live_e2e():
    from playwright.async_api import async_playwright

    log("="*60)
    log("E2E LIVE TEST v2: pay-test-sandbox-2")
    log(f"URL: {LIVE_URL}")
    log("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-web-security"]
        )

        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0"
        )
        page = await ctx.new_page()

        page.on("console", lambda m: console_all.append({
            "type": m.type, "text": m.text, "ts": datetime.now().strftime("%H:%M:%S")
        }))
        page.on("pageerror", lambda e: page_errors.append(str(e)))

        async def on_request(request):
            url = request.url
            entry = {
                "ts": datetime.now().strftime("%H:%M:%S"),
                "method": request.method,
                "url": url[:200],
                "type": classify_url(url),
                "is_seed": is_seed_request(url)
            }
            if entry["is_seed"]:
                log(f"*** SEED FIRE DETECTED: {request.method} {url[:150]} ***")
                try:
                    pd = await request.post_data()
                    if pd:
                        entry["payload"] = pd[:1000]
                except:
                    pass
                seed_fires.append(entry)
            elif entry["type"] in ["BIRTH_WEBHOOK", "WITNESS_SEED", "WITNESS_DIRECT", "PUREBRAIN_API", "CF_WORKER"]:
                log(f"  [{entry['type']}] {request.method} {url[:100]}")
            network_requests.append(entry)

        page.on("request", on_request)

        # ---- PHASE 0: Load page ----
        log("\n--- PHASE 0: Load page ---")
        await page.goto(LIVE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        p0 = ss_path("p0-initial-load")
        await page.screenshot(path=p0)
        log(f"SS: {p0}")

        has_pw_form = await page.query_selector('input[name="post_password"]')
        if has_pw_form:
            log("Password form detected")

            # ---- PHASE 1: Password unlock ----
            log("\n--- PHASE 1: Password unlock ---")
            await has_pw_form.fill(PAGE_PASSWORD)

            submit_btn = await page.query_selector('input[type="submit"], button[type="submit"]')
            if submit_btn:
                await submit_btn.click()
            else:
                await has_pw_form.press("Enter")

            log("Waiting for unlock...")
            await asyncio.sleep(8)

            p1 = ss_path("p1-after-password")
            await page.screenshot(path=p1)
            log(f"SS: {p1}")

            pw_state = await page.evaluate('''() => ({
                url: window.location.href,
                has_begin: !!document.querySelector(".chat-initial__btn"),
                captcha: document.body.innerText.includes("verify you are human"),
                title: document.title,
            })''')
            log(f"Post-pw: {json.dumps(pw_state)}")

            if pw_state.get("captcha"):
                log("[CRITICAL] WAF CAPTCHA triggered - test cannot proceed")
                await ctx.close()
                await browser.close()
                return {"error": "WAF_CAPTCHA"}

        # Wait a bit more for page to fully render
        await asyncio.sleep(5)

        # ---- PHASE 2: Pre-payment chatbox ----
        log("\n--- PHASE 2: Pre-payment chatbox ---")

        p2_full = ss_path("p2-full-page")
        await page.screenshot(path=p2_full, full_page=True)
        log(f"SS (full): {p2_full}")

        begin_btn = await page.query_selector(".chat-initial__btn")
        log(f"Begin btn found: {begin_btn is not None}")

        if begin_btn:
            # Scroll to it and click
            await page.evaluate("document.querySelector('.chat-initial__btn').scrollIntoView({block:'center'})")
            await asyncio.sleep(1)
            await page.evaluate("document.querySelector('.chat-initial__btn').click()")
            log("Clicked Begin Awakening (via JS)")
            await asyncio.sleep(4)

            p2a = ss_path("p2-after-begin")
            await page.screenshot(path=p2a)
            log(f"SS: {p2a}")

            # Enter bypass code
            user_input = await page.query_selector("#userInput")
            if user_input:
                await page.evaluate("""
                    document.getElementById('userInput').value = 'pb-full-bypass';
                    document.getElementById('userInput').dispatchEvent(new Event('input', {bubbles:true}));
                """)
                await asyncio.sleep(0.5)
                submit = await page.query_selector("#submitBtn")
                if submit:
                    await page.evaluate("document.getElementById('submitBtn').click()")
                else:
                    await user_input.press("Enter")
                log("Sent bypass code 'pb-full-bypass'")
                await asyncio.sleep(5)

                p2b = ss_path("p2-after-bypass")
                await page.screenshot(path=p2b)
                log(f"SS: {p2b}")

                bypass_state = await page.evaluate('''() => {
                    const msgs = document.querySelectorAll(".message--ai");
                    const procta = document.querySelector("#proCta");
                    return {
                        ai_msg_count: msgs.length,
                        last_ai_msg: msgs.length > 0 ? msgs[msgs.length-1].innerText.substring(0,200) : null,
                        procta_exists: !!procta,
                        procta_text: procta ? procta.innerText.trim() : null,
                        procta_rect: procta ? JSON.stringify(procta.getBoundingClientRect()) : null,
                    };
                }''')
                log(f"After bypass: {json.dumps(bypass_state, indent=2)}")

        # ---- PHASE 3: Trigger PayPal checkout ----
        log("\n--- PHASE 3: Payment trigger ---")

        # Check for #proCta via JS (element may be off-screen)
        procta_state = await page.evaluate('''() => {
            const el = document.getElementById("proCta") || document.querySelector("#proCta, .pro-cta");
            if (!el) return {found: false};
            const rect = el.getBoundingClientRect();
            return {
                found: true,
                text: el.innerText.trim(),
                visible_in_viewport: rect.top >= 0 && rect.top <= window.innerHeight,
                rect: {top: rect.top, left: rect.left, width: rect.width, height: rect.height},
                display: window.getComputedStyle(el).display,
                visibility: window.getComputedStyle(el).visibility,
            };
        }''')
        log(f"#proCta state: {json.dumps(procta_state)}")

        if procta_state.get("found"):
            log("Clicking #proCta via JS (may not be in viewport)")
            await page.evaluate("document.getElementById('proCta').click()")
            log("Clicked #proCta")
            await asyncio.sleep(4)

            p3a = ss_path("p3-after-procta")
            await page.screenshot(path=p3a)
            log(f"SS: {p3a}")

        # Check for sandbox bypass button
        await asyncio.sleep(2)
        sandbox_state = await page.evaluate('''() => {
            const btn = document.getElementById("pb-sandbox-bypass-btn");
            const overlay = document.getElementById("pb-paypal-overlay");
            const waitlistModal = document.getElementById("waitlistModal");
            return {
                sandbox_btn_exists: !!btn,
                sandbox_btn_visible: btn ? window.getComputedStyle(btn).display !== "none" : false,
                sandbox_btn_text: btn ? btn.innerText.trim() : null,
                paypal_overlay_active: overlay ? overlay.classList.contains("pb-active") : false,
                waitlist_modal_active: waitlistModal ? waitlistModal.classList.contains("active") : false,
                openPayPalModal_type: typeof window.openPayPalModal,
                openWaitlistModal_type: typeof openWaitlistModal,
            };
        }''')
        log(f"Sandbox state: {json.dumps(sandbox_state, indent=2)}")

        p3b = ss_path("p3-payment-modal-state")
        await page.screenshot(path=p3b)
        log(f"SS: {p3b}")

        sandbox_btn_found = sandbox_state.get("sandbox_btn_exists")

        if not sandbox_btn_found:
            log("Sandbox bypass btn not in DOM yet - trying to open PayPal modal first")
            # Try clicking the first pricing tier button via JS
            open_result = await page.evaluate('''() => {
                // Try window.openPayPalModal
                if (typeof window.openPayPalModal === "function") {
                    window.openPayPalModal("Awakened");
                    return "called window.openPayPalModal(Awakened)";
                }
                // Try window.openWaitlistModal
                if (typeof window.openWaitlistModal === "function") {
                    window.openWaitlistModal("Awakened");
                    return "called window.openWaitlistModal(Awakened)";
                }
                return "no modal function found";
            }''')
            log(f"Modal open result: {open_result}")
            await asyncio.sleep(3)

            p3c = ss_path("p3-after-modal-open")
            await page.screenshot(path=p3c)
            log(f"SS: {p3c}")

            # Re-check for sandbox bypass btn
            sandbox_btn_found = await page.evaluate(
                '!!document.getElementById("pb-sandbox-bypass-btn")'
            )
            log(f"Sandbox btn after modal open: {sandbox_btn_found}")

        if sandbox_btn_found:
            seeds_before = len(seed_fires)

            # Click sandbox bypass btn
            await page.evaluate('''() => {
                const btn = document.getElementById("pb-sandbox-bypass-btn");
                if (btn) {
                    btn.scrollIntoView({behavior:"instant", block:"center"});
                    btn.click();
                }
            }''')
            log("Clicked sandbox bypass button (simulating PayPal payment)")
            await asyncio.sleep(6)

            seeds_after = len(seed_fires)
            log(f"Seeds fired by payment simulation: {seeds_after - seeds_before}")

            p3d = ss_path("p3-after-sandbox-bypass")
            await page.screenshot(path=p3d)
            log(f"SS: {p3d}")

        # ---- PHASE 4: Post-payment chatbox ----
        log("\n--- PHASE 4: Post-payment chatbox ---")
        await asyncio.sleep(5)

        ptc_state = await page.evaluate('''() => {
            const wrapper = document.querySelector(".ptc-wrapper, #pay-test-post-payment");
            const msgs = document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai");
            return {
                ptc_exists: !!wrapper,
                ptc_visible: wrapper ? window.getComputedStyle(wrapper).display !== "none" : false,
                msg_count: msgs.length,
                first_msg: msgs.length > 0 ? msgs[0].innerText.substring(0, 200) : null,
                last_msg: msgs.length > 0 ? msgs[msgs.length-1].innerText.substring(0, 200) : null,
                has_input: !!document.querySelector("textarea[placeholder*='Message'], .ptc-input"),
                runBirthInit_fn: typeof window.runBirthInit,
            };
        }''')
        log(f"Post-payment chatbox: {json.dumps(ptc_state, indent=2)}")

        p4a = ss_path("p4-post-payment-initial")
        await page.screenshot(path=p4a)
        log(f"SS: {p4a}")

        if ptc_state.get("ptc_exists") and ptc_state.get("ptc_visible"):
            log("Post-payment chatbox is ACTIVE")

            async def get_msg_count():
                return await page.evaluate(
                    'document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai").length'
                )

            async def get_last_msg():
                return await page.evaluate('''() => {
                    const msgs = document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai");
                    return msgs.length > 0 ? msgs[msgs.length-1].innerText.trim() : null;
                }''')

            async def wait_for_msg(prev, timeout=20):
                deadline = time.time() + timeout
                while time.time() < deadline:
                    current = await get_msg_count()
                    if current > prev:
                        await asyncio.sleep(2)
                        return True
                    await asyncio.sleep(0.5)
                return False

            async def send_ptc(text):
                result = await page.evaluate(f'''() => {{
                    const inputs = document.querySelectorAll("textarea, input.ptc-input, #ptcInput");
                    const visible = Array.from(inputs).filter(i =>
                        window.getComputedStyle(i).display !== "none"
                    );
                    if (visible.length > 0) {{
                        visible[0].value = {json.dumps(text)};
                        visible[0].dispatchEvent(new Event('input', {{bubbles: true}}));
                        const send = document.querySelector("button.ptc-send-btn, .ptc-send");
                        if (send) {{ send.click(); return "sent via button"; }}
                        visible[0].dispatchEvent(new KeyboardEvent('keydown', {{key:'Enter',bubbles:true}}));
                        return "sent via enter";
                    }}
                    return "no visible input";
                }}''')
                log(f"Sent '{text}': {result}")
                return result

            async def click_visible_primary():
                return await page.evaluate('''() => {
                    const btns = document.querySelectorAll(".ptc-btn.ptc-btn--primary, .ptc-btn--primary");
                    const vis = Array.from(btns).filter(b =>
                        window.getComputedStyle(b).display !== "none" && b.offsetHeight > 0
                    );
                    if (vis.length > 0) { vis[0].click(); return {clicked: true, text: vis[0].innerText.trim()}; }
                    return {clicked: false};
                }''')

            # Check for Claude Max question (v4.9)
            last = await get_last_msg()
            log(f"First post-payment message: {last}")

            if last and ("Claude Max" in last or "claude.ai" in last.lower() or "Max account" in last):
                log("v4.9 Claude Max check detected")
                prev = await get_msg_count()
                yes_result = await page.evaluate('''() => {
                    const btns = Array.from(document.querySelectorAll("button, .ptc-btn"));
                    const yes = btns.find(b =>
                        (b.innerText.includes("Yes") || b.innerText.includes("yes")) &&
                        !b.innerText.includes("No")
                    );
                    if (yes) { yes.click(); return yes.innerText.trim(); }
                    // Try primary button
                    const primary = document.querySelector(".ptc-btn.ptc-btn--primary");
                    if (primary) { primary.click(); return "primary: " + primary.innerText.trim(); }
                    return null;
                }''')
                log(f"Claude Max answer: {yes_result}")
                await wait_for_msg(prev)
                last = await get_last_msg()
                log(f"After Claude Max answer: {last}")

            # Q1: Name
            prev = await get_msg_count()
            await send_ptc("Alex TestUser")
            got_msg = await wait_for_msg(prev)
            log(f"Q1 name - got response: {got_msg}")
            p4_n = ss_path("p4-q1-name")
            await page.screenshot(path=p4_n)
            log(f"SS: {p4_n}")

            # Q2: Email
            prev = await get_msg_count()
            await send_ptc("alex@testcompany.com")
            got_msg = await wait_for_msg(prev)
            log(f"Q2 email - got response: {got_msg}")
            p4_e = ss_path("p4-q2-email")
            await page.screenshot(path=p4_e)
            log(f"SS: {p4_e}")

            # Q3: Company
            prev = await get_msg_count()
            await send_ptc("TestCo Industries")
            got_msg = await wait_for_msg(prev)
            log(f"Q3 company - got response: {got_msg}")
            p4_c = ss_path("p4-q3-company")
            await page.screenshot(path=p4_c)
            log(f"SS: {p4_c}")

            # Q4: Role
            seeds_before_q4 = len(seed_fires)
            prev = await get_msg_count()
            await send_ptc("CEO")
            got_msg = await wait_for_msg(prev)
            log(f"Q4 role - got response: {got_msg}")

            # Wait extra for birth init auto-fire (v4.5+)
            await asyncio.sleep(8)
            seeds_after_q4 = len(seed_fires)
            log(f"Seeds after Q4 (birth init auto-fire): {seeds_after_q4 - seeds_before_q4}")

            p4_r = ss_path("p4-q4-role")
            await page.screenshot(path=p4_r)
            log(f"SS: {p4_r}")

            last = await get_last_msg()
            log(f"After Q4: {last}")

            # Check for manual "Start AI Birth" button (if present)
            birth_btn = await page.evaluate('''() => {
                const btns = Array.from(document.querySelectorAll("button, .ptc-btn"));
                const match = btns.find(b =>
                    b.innerText.includes("Birth") || b.innerText.includes("Start AI") || b.innerText.includes("born")
                );
                if (match) return {found: true, text: match.innerText.trim()};
                return {found: false};
            }''')
            if birth_btn.get("found"):
                log(f"Manual birth button found: '{birth_btn.get('text')}' - clicking")
                seeds_before_birth = len(seed_fires)
                await page.evaluate('''() => {
                    const btns = Array.from(document.querySelectorAll("button, .ptc-btn"));
                    const match = btns.find(b =>
                        b.innerText.includes("Birth") || b.innerText.includes("Start AI")
                    );
                    if (match) match.click();
                }''')
                await asyncio.sleep(8)
                seeds_after_birth = len(seed_fires)
                log(f"Seeds fired by manual birth: {seeds_after_birth - seeds_before_birth}")

                p4_birth = ss_path("p4-after-birth-btn")
                await page.screenshot(path=p4_birth)
                log(f"SS: {p4_birth}")

            # Q5: Primary goal
            await asyncio.sleep(2)
            last = await get_last_msg()
            log(f"After birth init: {last}")

            if last and any(x in last.lower() for x in ["goal", "do one thing", "one thing"]):
                prev = await get_msg_count()
                await send_ptc("Help me automate my business operations")
                got_msg = await wait_for_msg(prev)
                log(f"Q5 goal - got response: {got_msg}")
                p4_g = ss_path("p4-q5-goal")
                await page.screenshot(path=p4_g)
                log(f"SS: {p4_g}")

            # Navigate slides
            log("\n--- Slides ---")
            for i in range(15):
                await asyncio.sleep(0.8)
                clicked = await click_visible_primary()
                if not clicked.get("clicked"):
                    log(f"  No primary button at slide {i}")
                    break
                txt = clicked.get("text", "")
                log(f"  Slide {i}: '{txt}'")
                if any(x in txt.lower() for x in ["let's go", "incredible", "keep going", "connection established"]):
                    await asyncio.sleep(2)
                    break

            p4_s = ss_path("p4-after-slides")
            await page.screenshot(path=p4_s)
            log(f"SS: {p4_s}")

            # Telegram
            await asyncio.sleep(2)
            last = await get_last_msg()
            log(f"After slides: {last[:100] if last else 'None'}")

            if last and "Telegram" in last:
                tg = await page.evaluate('''() => {
                    const btns = Array.from(document.querySelectorAll("button, .ptc-btn"));
                    const yes = btns.find(b => b.innerText.includes("Yes") && b.innerText.includes("Telegram"));
                    if (yes) { yes.click(); return yes.innerText; }
                    return null;
                }''')
                log(f"Telegram choice: {tg}")
                await asyncio.sleep(4)

            # Learn more button (triggers portal watcher)
            p4_pre_learn = ss_path("p4-pre-learn")
            await page.screenshot(path=p4_pre_learn)
            log(f"SS: {p4_pre_learn}")

            learn = await page.evaluate('''() => {
                const btns = Array.from(document.querySelectorAll("button, .ptc-btn, a.ptc-btn"));
                const b = btns.find(b => b.innerText.toLowerCase().includes("learn more"));
                if (b) { b.click(); return b.innerText; }
                return null;
            }''')
            if learn:
                log(f"Clicked 'Learn more': '{learn}'")
                await asyncio.sleep(3)

        else:
            log("[WARNING] Post-payment chatbox not visible")

            # Try triggering initPayTestFlow directly
            log("Attempting to call initPayTestFlow directly...")
            init_result = await page.evaluate('''() => {
                if (typeof window.initPayTestFlow === "function") {
                    try {
                        window.initPayTestFlow({aiName: "Keen", tier: "Awakened", orderId: "test-001"});
                        return "initPayTestFlow called";
                    } catch(e) {
                        return "Error: " + e.message;
                    }
                }
                return "initPayTestFlow not found";
            }''')
            log(f"initPayTestFlow result: {init_result}")
            await asyncio.sleep(5)

            p4_debug = ss_path("p4-debug-after-init")
            await page.screenshot(path=p4_debug)
            log(f"SS: {p4_debug}")

        # ---- PHASE 5: Portal + final seed ----
        log("\n--- PHASE 5: Portal button monitoring ---")

        for check_i in range(8):
            await asyncio.sleep(5)
            portal = await page.evaluate('''() => {
                const btn = document.querySelector(".ptc-portal-btn, a[href*='portal']");
                const msgs = document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai");
                return {
                    portal_found: !!btn,
                    portal_href: btn ? (btn.href || btn.getAttribute("href")) : null,
                    msg_count: msgs.length,
                    last_msg: msgs.length > 0 ? msgs[msgs.length-1].innerText.substring(0, 300) : null,
                };
            }''')
            log(f"  [Check {check_i+1}] Portal: {portal.get('portal_found')}, msgs: {portal.get('msg_count')}")
            if portal.get('last_msg'):
                log(f"    Last msg: {portal['last_msg'][:100]}")

            if portal.get("portal_found"):
                log("PORTAL BUTTON APPEARED!")
                p5_portal = ss_path("p5-portal-button")
                await page.screenshot(path=p5_portal)
                log(f"SS: {p5_portal}")
                log(f"Portal href: {portal.get('portal_href')}")
                break

            if check_i % 2 == 0:
                p5_w = ss_path(f"p5-wait-{check_i+1}")
                await page.screenshot(path=p5_w)

        # Final screenshots
        p_final = ss_path("FINAL-state")
        await page.screenshot(path=p_final)
        p_final_fp = ss_path("FINAL-full-page")
        await page.screenshot(path=p_final_fp, full_page=True)
        log(f"Final screenshots: {p_final}, {p_final_fp}")

        final = await page.evaluate('''() => {
            const msgs = document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai");
            return {
                total_ptc_msgs: msgs.length,
                last_ptc_msg: msgs.length > 0 ? msgs[msgs.length-1].innerText.substring(0, 400) : null,
                portal_btn: !!document.querySelector(".ptc-portal-btn"),
                welcome_card: document.body.innerText.includes("Welcome to the Family"),
            };
        }''')
        log(f"FINAL: {json.dumps(final, indent=2)}")

        await ctx.close()
        await browser.close()

    # ---- Report ----
    log("\n" + "="*60)
    log("SEED FIRE SUMMARY")
    log("="*60)
    log(f"Total seed fires: {len(seed_fires)}")
    for i, sf in enumerate(seed_fires, 1):
        log(f"\n  Seed #{i}:")
        log(f"    Time: {sf['ts']}")
        log(f"    Type: {sf['type']}")
        log(f"    URL: {sf['url']}")
        log(f"    Method: {sf['method']}")
        if 'payload' in sf:
            try:
                payload = json.loads(sf['payload'])
                log(f"    Event: {payload.get('metadata', {}).get('event_type', '?')}")
                log(f"    Stage: {payload.get('metadata', {}).get('stage', '?')}")
                log(f"    Human name: {payload.get('human', {}).get('name', '?')}")
                log(f"    Human email: {payload.get('human', {}).get('email', '?')}")
                log(f"    AI name: {payload.get('ai_identity', {}).get('name', '?')}")
                log(f"    Tier: {payload.get('metadata', {}).get('tier', '?')}")
                log(f"    Container: {payload.get('metadata', {}).get('containerName', '?')}")
                log(f"    Conversation history len: {len(payload.get('conversation_history', []))}")
            except Exception as e:
                log(f"    Payload (raw): {sf['payload'][:400]}")

    log("\n" + "="*60)
    log("CONSOLE SUMMARY")
    log("="*60)
    errors = [c for c in console_all if c["type"] == "error"]
    pb_logs = [c for c in console_all if any(x in c["text"].lower() for x in
               ["seed", "witness", "birth", "webhook", "paypal", "ptc", "bypass", "initpay", "fireseed", "purebrain api"])]
    log(f"Total: {len(console_all)}, Errors: {len(errors)}, PB-related: {len(pb_logs)}")

    if errors:
        log("Errors (first 15):")
        for e in errors[:15]:
            log(f"  [{e['ts']}] {e['text'][:200]}")

    if pb_logs:
        log("PureBrain logs:")
        for l in pb_logs[:30]:
            log(f"  [{l['ts']}] {l['text'][:200]}")

    all_ss = sorted(Path(SESSION_DIR).glob("*.png"))
    log(f"\nTotal screenshots: {len(all_ss)}")
    log("="*60)

    # Write report
    lines = [
        "# E2E Pay-Test-Sandbox-2 Live Flow Audit",
        "",
        f"**Date**: 2026-03-02",
        f"**Script version**: v4.9",
        f"**URL**: {LIVE_URL}",
        "",
        "---",
        "",
        "## Seed Fire Results",
        f"**Total seeds fired**: {len(seed_fires)}",
        "",
    ]

    if seed_fires:
        for i, sf in enumerate(seed_fires, 1):
            lines.append(f"### Seed #{i}: {sf['type']}")
            lines.append(f"- Time: {sf['ts']}")
            lines.append(f"- URL: `{sf['url']}`")
            lines.append(f"- Method: {sf['method']}")
            if 'payload' in sf:
                try:
                    p = json.loads(sf['payload'])
                    lines.append(f"- Event: `{p.get('metadata', {}).get('event_type', '?')}`")
                    lines.append(f"- Stage: `{p.get('metadata', {}).get('stage', '?')}`")
                    lines.append(f"- Human: {p.get('human', {})}")
                    lines.append(f"- AI name: `{p.get('ai_identity', {}).get('name', '?')}`")
                    lines.append(f"- Container: `{p.get('metadata', {}).get('containerName', '?')}`")
                    lines.append(f"- Conv history: {len(p.get('conversation_history', []))} messages")
                except:
                    lines.append(f"- Payload: `{sf['payload'][:300]}`")
            lines.append("")
    else:
        lines.append("**NO SEED FIRES DETECTED**")
        lines.append("")

    lines.extend([
        "## Console Errors",
        f"Total: {len(errors)}",
        "",
    ])
    for e in errors[:15]:
        lines.append(f"- `{e['text'][:200]}`")

    lines.extend([
        "",
        "## PureBrain Console Logs",
        "",
    ])
    for l in pb_logs[:20]:
        lines.append(f"- `[{l['ts']}] {l['text'][:200]}`")

    lines.extend([
        "",
        f"## Final State",
        f"```json",
        json.dumps(final, indent=2),
        "```",
        "",
        "## Screenshots",
        f"Location: `{SESSION_DIR}/`",
    ])
    for ss in all_ss:
        lines.append(f"- `{ss.name}`")

    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(lines))
    log(f"Report: {REPORT_PATH}")

    return {"seed_fires": seed_fires, "errors": errors, "final": final}

if __name__ == "__main__":
    asyncio.run(run_live_e2e())
