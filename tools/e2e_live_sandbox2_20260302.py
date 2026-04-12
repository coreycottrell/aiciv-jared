#!/usr/bin/env python3
"""
E2E Full Payment Flow Test: pay-test-sandbox-2 (LIVE PAGE)
Date: 2026-03-02
Focus:
  1. Test the LIVE page (with real WP password gate)
  2. Full flow: pre-payment chat -> bypass -> PayPal bypass -> post-payment chat
  3. SEED FIRE detection at all 3 trigger points
  4. Verify sandbox bypass button works and fires seed #1 (payment_complete)
  5. Navigate post-payment questionnaire
  6. Verify seed #2 and #3 fire

Page: https://purebrain.ai/pay-test-sandbox-2/
Password: PureBrain.ai253443$$$

Seeds in v4.9:
  Stage 1: fireSeed('payment_complete', 1) - fires immediately when post-payment chat inits
  Stage 2: fireSeed('oauth_authenticated', 2) - fires after birth/OAuth
  Stage 3: fireSeed('portal_ready', 3) - fires when portal is ready
"""

import asyncio
import json
import os
import re
import time
from pathlib import Path
from datetime import datetime

SESSION_DIR = f"/home/jared/projects/AI-CIV/aether/exports/screenshots/e2e-live-sandbox2-20260302"
REPORT_PATH = f"/home/jared/projects/AI-CIV/aether/exports/e2e-live-sandbox2-report-20260302.md"
os.makedirs(SESSION_DIR, exist_ok=True)

LIVE_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PAGE_PASSWORD = "PureBrain.ai253443$$$"

# Seed/webhook endpoints to monitor
SEED_ENDPOINTS = ["104.248.239.98", "178.156.229.207", "api.purebrain.ai", "8099", "8200"]

screenshot_count = [0]
network_requests = []
console_all = []
page_errors = []
seed_fires = []
findings = []

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def ss_path(label):
    screenshot_count[0] += 1
    path = f"{SESSION_DIR}/{screenshot_count[0]:03d}-{label}.png"
    return path

def is_seed_request(url, method="", post_data=""):
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
    if "purebrain.ai" in url: return "PUREBRAIN_SITE"
    return "OTHER"

async def run_live_e2e():
    from playwright.async_api import async_playwright

    log("="*60)
    log("E2E LIVE TEST: pay-test-sandbox-2")
    log(f"URL: {LIVE_URL}")
    log("="*60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
            ]
        )

        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await ctx.new_page()

        # Console + error tracking
        page.on("console", lambda m: console_all.append({
            "type": m.type,
            "text": m.text,
            "ts": datetime.now().strftime("%H:%M:%S")
        }))
        page.on("pageerror", lambda e: page_errors.append(str(e)))

        # Network request interception
        async def on_request(request):
            url = request.url
            method = request.method
            req_type = classify_url(url)
            entry = {
                "ts": datetime.now().strftime("%H:%M:%S"),
                "method": method,
                "url": url[:200],
                "type": req_type,
                "is_seed": is_seed_request(url)
            }
            if entry["is_seed"]:
                log(f"*** SEED FIRE: {method} {url[:150]} ***")
                try:
                    pd = await request.post_data()
                    if pd:
                        entry["payload"] = pd[:800]
                except:
                    pass
                seed_fires.append(entry)
            elif req_type in ["BIRTH_WEBHOOK", "WITNESS_SEED", "WITNESS_DIRECT", "PUREBRAIN_API", "CF_WORKER"]:
                log(f"  [{req_type}] {method} {url[:100]}")
            network_requests.append(entry)

        page.on("request", on_request)

        # ---- PHASE 0: Navigate to live page ----
        log("\n--- PHASE 0: Navigate to live page ---")
        try:
            await page.goto(LIVE_URL, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(2)
        except Exception as e:
            log(f"Navigation error: {e}")

        p0 = ss_path("phase0-page-load")
        await page.screenshot(path=p0)
        log(f"SS saved: {p0}")

        # Check if password gate is showing
        page_state = await page.evaluate('''() => ({
            title: document.title,
            url: window.location.href,
            has_password_form: !!document.querySelector('input[name="post_password"], input[type="password"]'),
            has_begin_btn: !!document.querySelector(".chat-initial__btn"),
            body_preview: document.body.innerText.substring(0, 300),
        })''')
        log(f"Page state: {json.dumps(page_state)}")

        # ---- PHASE 1: Password unlock ----
        if page_state.get("has_password_form"):
            log("\n--- PHASE 1: Password unlock ---")
            pw_input = await page.query_selector('input[name="post_password"], input[type="password"]')
            if pw_input:
                await pw_input.fill(PAGE_PASSWORD)
                # Submit the form
                form = await page.query_selector('form[action*="wp-login"], form[method="post"]')
                if form:
                    await form.evaluate('f => f.submit()')
                else:
                    submit_btn = await page.query_selector('input[type="submit"], button[type="submit"]')
                    if submit_btn:
                        await submit_btn.click()
                    else:
                        await pw_input.press("Enter")

                log("Password submitted, waiting for page load...")
                await asyncio.sleep(5)

                p1 = ss_path("phase1-after-password")
                await page.screenshot(path=p1)
                log(f"SS saved: {p1}")

                post_pw_state = await page.evaluate('''() => ({
                    title: document.title,
                    url: window.location.href,
                    has_begin_btn: !!document.querySelector(".chat-initial__btn"),
                    has_password_form: !!document.querySelector('input[name="post_password"]'),
                    captcha: document.body.innerText.includes("verify you are human"),
                    body_preview: document.body.innerText.substring(0, 200),
                })''')
                log(f"Post-password state: {json.dumps(post_pw_state)}")

                if post_pw_state.get("captcha"):
                    log("[CAPTCHA] WAF rate limit hit - 'verify you are human' shown")
                    findings.append({
                        "type": "CRITICAL",
                        "title": "WAF Rate Limit (CAPTCHA)",
                        "detail": "GoDaddy WAF blocked access. Recovery requires 15-20 min wait."
                    })
                    # Try to continue anyway
        else:
            log("No password form found - page may already be unlocked or using different auth")

        # ---- PHASE 2: Pre-payment chat ----
        log("\n--- PHASE 2: Pre-payment chatbox ---")
        await asyncio.sleep(3)

        begin_btn = await page.query_selector(".chat-initial__btn")
        if not begin_btn:
            log("Begin button not found - checking current state")
            current = await page.evaluate('''() => ({
                begin_btn: !!document.querySelector(".chat-initial__btn"),
                url: window.location.href,
                title: document.title,
                body_text: document.body.innerText.substring(0, 400),
                has_recaptcha: !!document.querySelector("#recaptcha, .g-recaptcha"),
                has_sandbox_banner: !!document.getElementById("sandbox-banner"),
            })''')
            log(f"Current state: {json.dumps(current)}")

            p_debug = ss_path("phase2-no-begin-btn-debug")
            await page.screenshot(path=p_debug, full_page=True)
            log(f"Debug screenshot: {p_debug}")
        else:
            log("Begin Awakening button found")
            p2a = ss_path("phase2-begin-btn-visible")
            await page.screenshot(path=p2a)
            log(f"SS saved: {p2a}")

            # Take full page screenshot
            p2b = ss_path("phase2-full-page-initial")
            await page.screenshot(path=p2b, full_page=True)
            log(f"SS saved (full page): {p2b}")

            # Click Begin Awakening
            log("Clicking Begin Awakening...")
            await begin_btn.click()
            await asyncio.sleep(3)

            p2c = ss_path("phase2-after-begin-click")
            await page.screenshot(path=p2c)
            log(f"SS saved: {p2c}")

            # Enter bypass code
            user_input = await page.query_selector("#userInput")
            if user_input:
                is_visible = await user_input.is_visible()
                log(f"#userInput visible: {is_visible}")

                await user_input.fill("pb-full-bypass")
                submit = await page.query_selector("#submitBtn")
                if submit:
                    await submit.click()
                else:
                    await user_input.press("Enter")
                log("Sent bypass code 'pb-full-bypass'")
                await asyncio.sleep(4)

                p2d = ss_path("phase2-after-bypass-code")
                await page.screenshot(path=p2d)
                log(f"SS saved: {p2d}")

                # Analyze post-bypass state
                bypass_state = await page.evaluate('''() => {
                    const msgs = document.querySelectorAll(".message--ai");
                    const lastMsg = msgs.length > 0 ? msgs[msgs.length-1].innerText : null;
                    const procta = document.querySelector("#proCta");
                    const pricing = document.querySelector("#pricing, .pricing-section");
                    return {
                        ai_msg_count: msgs.length,
                        last_ai_msg: lastMsg ? lastMsg.substring(0,200) : null,
                        procta_exists: !!procta,
                        procta_text: procta ? procta.innerText.trim() : null,
                        pricing_visible: pricing ? window.getComputedStyle(pricing).display !== "none" : false,
                    };
                }''')
                log(f"After bypass: {json.dumps(bypass_state, indent=2)}")

        # ---- PHASE 3: Click "Activate Now" or pricing button ----
        log("\n--- PHASE 3: Payment trigger ---")

        # First look for #proCta (Discover/Activate Now)
        pro_cta = await page.query_selector("#proCta")
        if pro_cta:
            cta_text = await pro_cta.inner_text()
            log(f"Found #proCta: '{cta_text.strip()}'")
            await pro_cta.scroll_into_view_if_needed()
            await pro_cta.click()
            log("Clicked #proCta")
            await asyncio.sleep(3)

            p3a = ss_path("phase3-after-procta")
            await page.screenshot(path=p3a)
            log(f"SS saved: {p3a}")

        # Check for sandbox bypass button (should appear in PayPal modal for sandbox pages)
        log("Looking for sandbox bypass button...")
        await asyncio.sleep(2)

        sandbox_btn = await page.query_selector("#pb-sandbox-bypass-btn")
        if sandbox_btn:
            sb_text = await sandbox_btn.inner_text()
            log(f"Found sandbox bypass button: '{sb_text.strip()}'")

            p3b = ss_path("phase3-sandbox-bypass-visible")
            await page.screenshot(path=p3b)
            log(f"SS saved: {p3b}")

            # Record seed count before bypass
            seeds_before = len(seed_fires)

            await sandbox_btn.scroll_into_view_if_needed()
            await sandbox_btn.click()
            log("Clicked sandbox bypass button (simulating payment)")

            # Wait for post-payment to initialize
            await asyncio.sleep(5)

            seeds_after = len(seed_fires)
            log(f"Seeds fired by payment simulation: {seeds_after - seeds_before}")
            if seed_fires:
                for sf in seed_fires[seeds_before:]:
                    log(f"  Stage: {sf['type']} | URL: {sf['url'][:100]}")

            p3c = ss_path("phase3-after-sandbox-bypass")
            await page.screenshot(path=p3c)
            log(f"SS saved: {p3c}")

        else:
            log("Sandbox bypass button not found - checking PayPal overlay state")
            overlay_state = await page.evaluate('''() => {
                const overlay = document.getElementById("pb-paypal-overlay");
                const modal_visible = overlay ? window.getComputedStyle(overlay).display !== "none" : false;
                const overlay_active = overlay ? overlay.classList.contains("pb-active") : false;
                return {
                    overlay_exists: !!overlay,
                    overlay_visible: modal_visible,
                    overlay_active: overlay_active,
                    overlay_html: overlay ? overlay.innerHTML.substring(0, 300) : null,
                    bypass_in_dom: !!document.getElementById("pb-sandbox-bypass-btn"),
                };
            }''')
            log(f"PayPal overlay state: {json.dumps(overlay_state, indent=2)}")

            p3_debug = ss_path("phase3-no-bypass-debug")
            await page.screenshot(path=p3_debug)
            log(f"Debug screenshot: {p3_debug}")

            # Try to force-trigger the sandbox bypass via JS
            log("Attempting to find sandbox bypass button via JS evaluation...")
            sandbox_check = await page.evaluate('''() => {
                // Check if sandbox bypass exists anywhere in DOM
                const btn = document.getElementById("pb-sandbox-bypass-btn");
                if (btn) return {found: true, id: btn.id, text: btn.innerText};

                // Check if sandbox overlay div exists
                const div = document.querySelector(".pb-sandbox-overlay, #pb-sandbox-overlay");
                if (div) return {found: false, sandbox_div: div.id || div.className};

                // Check if there's a trigger function
                const hasSandboxTrigger = typeof window.simulateSandboxPayment !== "undefined" ||
                    typeof window.triggerSandboxPayment !== "undefined";
                return {found: false, has_trigger: hasSandboxTrigger};
            }''')
            log(f"Sandbox check: {json.dumps(sandbox_check)}")

        # ---- PHASE 4: Post-payment chatbox ----
        log("\n--- PHASE 4: Post-payment chatbox ---")
        await asyncio.sleep(5)

        ptc_state = await page.evaluate('''() => {
            const wrapper = document.querySelector(".ptc-wrapper, #pay-test-post-payment");
            const msgs = document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai");
            const inputs = document.querySelectorAll("textarea[placeholder*='Message'], .ptc-input");
            return {
                ptc_found: !!wrapper,
                ptc_visible: wrapper ? window.getComputedStyle(wrapper).display !== "none" : false,
                msg_count: msgs.length,
                first_msg: msgs.length > 0 ? msgs[0].innerText.substring(0, 200) : null,
                last_msg: msgs.length > 0 ? msgs[msgs.length-1].innerText.substring(0, 200) : null,
                inputs_count: inputs.length,
                runBirthInit_ready: typeof window.runBirthInit === "function",
            };
        }''')
        log(f"Post-payment chatbox state: {json.dumps(ptc_state, indent=2)}")

        p4a = ss_path("phase4-post-payment-initial")
        await page.screenshot(path=p4a)
        log(f"SS saved: {p4a}")

        if ptc_state.get("ptc_found") and ptc_state.get("ptc_visible"):
            log("Post-payment chatbox is visible - navigating questionnaire")

            # Helper: get current AI message count
            async def get_msg_count():
                return await page.evaluate(
                    'document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai").length'
                )

            async def wait_for_next_message(prev, timeout=15):
                deadline = time.time() + timeout
                while time.time() < deadline:
                    current = await get_msg_count()
                    if current > prev:
                        await asyncio.sleep(1.5)
                        return True
                    await asyncio.sleep(0.5)
                return False

            async def get_last_ai_message():
                return await page.evaluate('''() => {
                    const msgs = document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai");
                    return msgs.length > 0 ? msgs[msgs.length-1].innerText.trim() : null;
                }''')

            async def send_text(text):
                inp = await page.query_selector("textarea[placeholder*='Message'], .ptc-input, #ptcInput")
                if inp:
                    await inp.fill(text)
                    send = await page.query_selector("button.ptc-send-btn, .ptc-send")
                    if send:
                        await send.click()
                    else:
                        await inp.press("Enter")
                    log(f"Sent: '{text}'")
                    return True
                return False

            async def click_primary_button(label_hint=""):
                """Click the first visible primary button"""
                btn = await page.evaluate('''() => {
                    const btns = document.querySelectorAll(".ptc-btn.ptc-btn--primary, .ptc-btn--primary");
                    const visible = Array.from(btns).filter(b =>
                        window.getComputedStyle(b).display !== "none" &&
                        b.offsetHeight > 0
                    );
                    if (visible.length > 0) {
                        visible[0].click();
                        return {clicked: true, text: visible[0].innerText.trim()};
                    }
                    return {clicked: false};
                }''')
                if btn.get("clicked"):
                    log(f"Clicked primary button: '{btn.get('text', '')}'")
                return btn

            # Check if Claude Max question is first (v4.9 new feature)
            last_msg = await get_last_ai_message()
            log(f"First AI message: {last_msg}")

            # Handle Claude Max question (v4.9)
            if last_msg and ("Claude Max" in last_msg or "claude.ai" in last_msg.lower()):
                log("Claude Max question detected (v4.9 feature)")
                prev = await get_msg_count()
                # Click "Yes" (assumes they have Claude Max)
                yes_clicked = await page.evaluate('''() => {
                    const btns = document.querySelectorAll(".ptc-btn, button");
                    const yes = Array.from(btns).find(b =>
                        b.innerText.includes("Yes") && !b.innerText.includes("No")
                    );
                    if (yes) { yes.click(); return {text: yes.innerText}; }
                    return null;
                }''')
                if yes_clicked:
                    log(f"Clicked 'Yes' for Claude Max: {yes_clicked}")
                    await wait_for_next_message(prev)

            # Q1: Name
            prev = await get_msg_count()
            await send_text("Alex TestUser")
            await wait_for_next_message(prev)
            p4_name = ss_path("phase4-after-name")
            await page.screenshot(path=p4_name)
            log(f"SS saved: {p4_name}")

            # Q2: Email
            prev = await get_msg_count()
            await send_text("alex@testcompany.com")
            await wait_for_next_message(prev)
            p4_email = ss_path("phase4-after-email")
            await page.screenshot(path=p4_email)
            log(f"SS saved: {p4_email}")

            # Q3: Company
            prev = await get_msg_count()
            await send_text("TestCo Industries")
            await wait_for_next_message(prev)
            p4_company = ss_path("phase4-after-company")
            await page.screenshot(path=p4_company)
            log(f"SS saved: {p4_company}")

            # Q4: Role
            seeds_before_role = len(seed_fires)
            prev = await get_msg_count()
            await send_text("CEO")
            await wait_for_next_message(prev)
            p4_role = ss_path("phase4-after-role")
            await page.screenshot(path=p4_role)
            log(f"SS saved: {p4_role}")

            # After Q4, check for birth init auto-fire (v4.5+: auto-fire, no button)
            await asyncio.sleep(5)  # Give birth init time to run
            seeds_after_role = len(seed_fires)
            log(f"Seeds fired after Q4 (role): {seeds_after_role - seeds_before_role}")

            last_msg = await get_last_ai_message()
            log(f"Last AI message after role: {last_msg}")

            # Check for "Start AI Birth" button (if using older v4.3.2 manual mode)
            birth_btn = await page.evaluate('''() => {
                const btns = Array.from(document.querySelectorAll("button, .ptc-btn"));
                const match = btns.find(b =>
                    b.innerText.includes("Birth") || b.innerText.includes("Start AI")
                );
                if (match) return {found: true, text: match.innerText.trim()};
                return {found: false};
            }''')

            if birth_btn.get("found"):
                log(f"Manual Birth button found: '{birth_btn.get('text')}' - clicking")
                seeds_before_birth = len(seed_fires)
                await page.evaluate('''() => {
                    const btns = Array.from(document.querySelectorAll("button, .ptc-btn"));
                    const match = btns.find(b =>
                        b.innerText.includes("Birth") || b.innerText.includes("Start AI")
                    );
                    if (match) match.click();
                }''')
                await asyncio.sleep(5)
                seeds_after_birth = len(seed_fires)
                log(f"Seeds fired by birth button: {seeds_after_birth - seeds_before_birth}")

                p4_birth = ss_path("phase4-after-birth-btn")
                await page.screenshot(path=p4_birth)
                log(f"SS saved: {p4_birth}")

            # Q5: Primary Goal
            await asyncio.sleep(2)
            last_msg = await get_last_ai_message()
            log(f"After birth init - last message: {last_msg}")

            # Check if primary goal question appeared
            primary_goal_appeared = last_msg and any(
                x in last_msg.lower() for x in
                ["goal", "do one thing", "exceptionally well", "what would it be"]
            )
            if primary_goal_appeared:
                prev = await get_msg_count()
                await send_text("Help me automate my business operations so I can focus on growth.")
                await wait_for_next_message(prev)
                p4_goal = ss_path("phase4-after-primary-goal")
                await page.screenshot(path=p4_goal)
                log(f"SS saved: {p4_goal}")

            # Navigate slides
            log("\n--- Navigating Behind the Curtain slides ---")
            for slide_i in range(15):
                await asyncio.sleep(1)
                clicked = await click_primary_button(f"slide-{slide_i}")
                if not clicked.get("clicked"):
                    break
                btn_text = clicked.get("text", "")
                if "Let's go" in btn_text or "incredible" in btn_text.lower() or "keep going" in btn_text.lower():
                    log(f"  Final slide button clicked: '{btn_text}'")
                    await asyncio.sleep(2)
                    break

            p4_slides = ss_path("phase4-after-slides")
            await page.screenshot(path=p4_slides)
            log(f"SS saved: {p4_slides}")

            # Handle Telegram
            await asyncio.sleep(2)
            last_msg = await get_last_ai_message()
            log(f"After slides - last message: {last_msg[:100] if last_msg else 'None'}")

            if last_msg and "Telegram" in last_msg:
                log("Telegram question appeared - clicking 'Yes, I have Telegram'")
                tg_result = await page.evaluate('''() => {
                    const btns = Array.from(document.querySelectorAll("button, .ptc-btn"));
                    const yes = btns.find(b => b.innerText.includes("Yes") && b.innerText.includes("Telegram"));
                    if (yes) { yes.click(); return yes.innerText; }
                    const skip = btns.find(b => b.innerText.includes("Skip") || b.innerText.includes("skip"));
                    if (skip) { skip.click(); return "Skipped: " + skip.innerText; }
                    return null;
                }''')
                log(f"Telegram response: {tg_result}")
                await asyncio.sleep(3)

            # Phase 5: Thank You / Learn More
            await asyncio.sleep(2)
            last_msg = await get_last_ai_message()
            log(f"After Telegram - last message: {last_msg[:150] if last_msg else 'None'}")

            p4_prelearn = ss_path("phase4-pre-learn-more")
            await page.screenshot(path=p4_prelearn)
            log(f"SS saved: {p4_prelearn}")

            # Click "Learn more" button to start portal watcher
            learn_clicked = await page.evaluate('''() => {
                const btns = Array.from(document.querySelectorAll("button, .ptc-btn, a.ptc-btn"));
                const learn = btns.find(b =>
                    b.innerText.includes("Learn more") || b.innerText.includes("learn more")
                );
                if (learn) { learn.click(); return learn.innerText; }
                return null;
            }''')
            if learn_clicked:
                log(f"Clicked 'Learn more': '{learn_clicked}'")
                await asyncio.sleep(3)

            p4_learn = ss_path("phase4-after-learn-more")
            await page.screenshot(path=p4_learn)
            log(f"SS saved: {p4_learn}")

        else:
            log("[INFO] Post-payment chatbox not visible yet")

        # ---- PHASE 5: Monitor for portal button + seed stage 3 ----
        log("\n--- PHASE 5: Portal button + final seed ---")

        # Wait up to 30 seconds for portal to appear
        portal_appeared = False
        for check_i in range(6):
            await asyncio.sleep(5)
            portal_state = await page.evaluate('''() => {
                const portal_links = document.querySelectorAll(".ptc-portal-btn, a[href*='portal']");
                const last_ptc_msg = document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai");
                const msg_count = last_ptc_msg.length;
                const last_msg = msg_count > 0 ? last_ptc_msg[msg_count-1].innerText.trim().substring(0, 300) : null;
                return {
                    portal_links_count: portal_links.length,
                    portal_hrefs: Array.from(portal_links).map(a => a.href || a.getAttribute("href")),
                    total_ptc_messages: msg_count,
                    last_ptc_message: last_msg,
                    has_welcome: document.body.innerText.includes("Welcome to the Family"),
                };
            }''')
            log(f"[Check {check_i+1}] Portal state: {json.dumps(portal_state)}")

            if portal_state.get("portal_links_count", 0) > 0:
                log("PORTAL BUTTON APPEARED!")
                portal_appeared = True
                p5_portal = ss_path("phase5-portal-button")
                await page.screenshot(path=p5_portal)
                log(f"SS saved: {p5_portal}")
                break

            # Also take periodic screenshot
            if check_i % 2 == 0:
                p5_wait = ss_path(f"phase5-waiting-{check_i+1}")
                await page.screenshot(path=p5_wait)

        # Final state
        p_final = ss_path("final-state")
        await page.screenshot(path=p_final)
        p_final_full = ss_path("final-full-page")
        await page.screenshot(path=p_final_full, full_page=True)
        log(f"Final screenshots saved")

        final_eval = await page.evaluate('''() => {
            const ptc_msgs = document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai");
            return {
                ptc_msg_count: ptc_msgs.length,
                last_ptc_msg: ptc_msgs.length > 0 ? ptc_msgs[ptc_msgs.length-1].innerText.trim().substring(0, 400) : null,
                portal_btn_exists: !!document.querySelector(".ptc-portal-btn, a[href*='portal']"),
                portal_href: (document.querySelector(".ptc-portal-btn, a[href*='portal']") || {}).href,
                welcome_card_visible: document.body.innerText.includes("Welcome to the Family"),
            };
        }''')
        log(f"Final eval: {json.dumps(final_eval, indent=2)}")

        await ctx.close()
        await browser.close()

    # ---- Summary ----
    log("\n" + "="*60)
    log("SEED FIRE SUMMARY")
    log("="*60)
    log(f"Total seed fires: {len(seed_fires)}")
    for i, sf in enumerate(seed_fires, 1):
        log(f"  Seed #{i}: [{sf['type']}] {sf['method']} {sf['url'][:100]}")
        if 'payload' in sf:
            try:
                payload = json.loads(sf['payload'])
                log(f"    Payload type: {payload.get('type', '?')}")
                log(f"    Event: {payload.get('metadata', {}).get('event_type', '?')}")
                log(f"    Stage: {payload.get('metadata', {}).get('stage', '?')}")
            except:
                log(f"    Payload: {sf['payload'][:200]}")

    log("\n" + "="*60)
    log("CONSOLE SUMMARY")
    log("="*60)
    errors = [c for c in console_all if c["type"] == "error"]
    warnings = [c for c in console_all if c["type"] in ["warning", "warn"]]
    pb_logs = [c for c in console_all if any(x in c["text"].lower() for x in
               ["purebrain", "seed", "witness", "birth", "webhook", "paypal", "ptc", "bypass", "fireSeed"])]
    log(f"Total: {len(console_all)}, Errors: {len(errors)}, Warnings: {len(warnings)}, PB-related: {len(pb_logs)}")
    if errors:
        log("Errors:")
        for e in errors[:15]:
            log(f"  [{e['ts']}] {e['text'][:200]}")
    if pb_logs:
        log("PureBrain/Seed logs:")
        for l in pb_logs[:30]:
            log(f"  [{l['ts']}] {l['text'][:200]}")

    all_ss = sorted(Path(SESSION_DIR).glob("*.png"))
    log(f"\nScreenshots: {len(all_ss)} in {SESSION_DIR}")
    log("="*60)

    # Generate report
    report = [
        "# E2E Live Pay-Test-Sandbox-2 Full Flow Audit",
        "",
        f"**Date**: 2026-03-02",
        f"**URL**: {LIVE_URL}",
        f"**Page version**: v4.9 (Claude Max account check + 3-stage seed firing)",
        "",
        "---",
        "",
        "## Seed Fire Results",
        "",
        f"**Total seed fires**: {len(seed_fires)}",
        "",
    ]

    if seed_fires:
        for i, sf in enumerate(seed_fires, 1):
            report.extend([
                f"### Seed Fire #{i}",
                f"- **Time**: {sf['ts']}",
                f"- **Type**: {sf['type']}",
                f"- **Method**: {sf['method']}",
                f"- **URL**: `{sf['url']}`",
            ])
            if 'payload' in sf:
                try:
                    payload = json.loads(sf['payload'])
                    report.append(f"- **Event type**: `{payload.get('metadata', {}).get('event_type', '?')}`")
                    report.append(f"- **Stage**: `{payload.get('metadata', {}).get('stage', '?')}`")
                    report.append(f"- **Human name**: `{payload.get('human', {}).get('name', '?')}`")
                    report.append(f"- **Human email**: `{payload.get('human', {}).get('email', '?')}`")
                except:
                    report.append(f"- **Payload**: `{sf.get('payload', '')[:300]}`")
            report.append("")
    else:
        report.extend([
            "NO SEED FIRES DETECTED",
            "",
            "This could mean:",
            "1. WAF blocked the page load (CAPTCHA triggered)",
            "2. Payment simulation did not complete",
            "3. Seeds fire to external endpoints but browser blocked them in headless mode",
            "",
        ])

    report.extend([
        "## Console Errors",
        "",
        f"**Total**: {len(errors)}",
        "",
    ])
    for e in errors[:15]:
        report.append(f"- `[{e['ts']}] {e['text'][:200]}`")

    report.extend([
        "",
        "## PureBrain Console Logs",
        "",
    ])
    for l in pb_logs[:20]:
        report.append(f"- `[{l['ts']}] {l['text'][:200]}`")

    report.extend([
        "",
        "## Screenshots",
        "",
        f"**Location**: `{SESSION_DIR}/`",
        "",
    ])
    for ss in all_ss:
        report.append(f"- `{ss.name}`")

    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(report))
    log(f"Report saved: {REPORT_PATH}")

    return {
        "seed_fires": seed_fires,
        "errors": errors,
        "pb_logs": pb_logs,
        "screenshots": [str(s) for s in all_ss],
        "final_eval": final_eval,
    }

if __name__ == "__main__":
    asyncio.run(run_live_e2e())
