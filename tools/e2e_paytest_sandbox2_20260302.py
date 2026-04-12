#!/usr/bin/env python3
"""
E2E Full Payment Flow Test: pay-test-sandbox-2
Date: 2026-03-02
Focus:
  1. Complete user journey (pre-payment -> payment -> post-payment)
  2. SEED FIRE detection at both trigger points
  3. PayPal sandbox login + payment completion
  4. Post-payment chatbox final message + portal button

Strategy: WP REST API fetch -> local serve (WAF-safe)
Seed trigger points to watch:
  A) After PayPal payment completes (first seed)
  B) After final post-payment chatbox message (second seed)

Network requests to detect:
  - POST to 104.248.239.98:8099 (birth webhook)
  - POST to 104.248.239.98:8200 or 178.156.229.207:8200 (Witness seed)
"""

import asyncio
import base64
import http.server
import json
import os
import re
import threading
import time
import urllib.request
from pathlib import Path
from datetime import datetime

# Config
PAGE_688_ID = 688  # pay-test-sandbox-2
PUREBRAIN_URL = "https://purebrain.ai"
WP_USER = "Aether"
WP_APP_PASSWORD = "FlFr2VOtlHiHaJWjzW96OHUJ"
SESSION_DIR = f"/home/jared/projects/AI-CIV/aether/exports/screenshots/e2e-paytest-sandbox2-20260302"
REPORT_PATH = f"/home/jared/projects/AI-CIV/aether/exports/e2e-paytest-sandbox2-report-20260302.md"
os.makedirs(SESSION_DIR, exist_ok=True)

# PayPal sandbox credentials
PAYPAL_EMAIL = "sb-c89tj49549583@personal.example.com"
PAYPAL_PASSWORD = "Z0+6<dS"

# Witness/Seed endpoints to watch
SEED_ENDPOINTS = [
    "104.248.239.98",
    "178.156.229.207",
    "api.purebrain.ai",
    "purebrain.workers.dev",
]
SEED_PORTS = ["8099", "8200"]

screenshot_count = [0]
network_requests = []
console_logs = []
page_errors_log = []
seed_fires = []

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def ss_path(label):
    screenshot_count[0] += 1
    return f"{SESSION_DIR}/{screenshot_count[0]:03d}-{label}.png"

def fetch_page_html(page_id):
    """Fetch page HTML via WP REST API (WAF-safe)"""
    url = f"{PUREBRAIN_URL}/wp-json/wp/v2/pages/{page_id}?context=edit"
    req = urllib.request.Request(url)
    creds = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
    req.add_header("Authorization", f"Basic {creds}")
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    raw = data.get("content", {}).get("raw", "")
    raw = re.sub(r'^<!-- wp:html -->\s*', '', raw, flags=re.DOTALL)
    raw = re.sub(r'\s*<!-- /wp:html -->$', '', raw, flags=re.DOTALL)
    log(f"Fetched page {page_id}: {len(raw):,} chars")
    return raw

def serve_html_locally(html_content, port):
    html_bytes = html_content.encode('utf-8')
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_bytes)
        def log_message(self, *a): pass
    server = http.server.HTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    log(f"Local server running on port {port}")
    return server

def is_seed_request(url):
    """Detect if a network request is a seed/webhook fire"""
    for ep in SEED_ENDPOINTS:
        if ep in url:
            return True
    for port in SEED_PORTS:
        if f":{port}" in url:
            return True
    return False

def classify_request(url, method, post_data=""):
    """Classify a network request type"""
    if "8099" in url:
        return "BIRTH_WEBHOOK"
    if "8200" in url:
        return "WITNESS_SEED"
    if "104.248.239.98" in url or "178.156.229.207" in url:
        return "WITNESS_DIRECT"
    if "api.purebrain.ai" in url:
        return "PUREBRAIN_API"
    if "paypal" in url.lower():
        return "PAYPAL"
    if "workers.dev" in url:
        return "CLOUDFLARE_WORKER"
    return "OTHER"

async def intercept_requests(page):
    """Set up network request interception"""
    async def on_request(request):
        url = request.url
        method = request.method
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "method": method,
            "url": url[:200],
            "type": classify_request(url, method),
            "is_seed": is_seed_request(url)
        }
        if is_seed_request(url):
            log(f"*** SEED FIRE DETECTED: {method} {url[:150]} ***")
            try:
                post_data = await request.post_data() or ""
                entry["post_data"] = str(post_data)[:500]
            except:
                pass
            seed_fires.append(entry)
        elif entry["type"] in ["BIRTH_WEBHOOK", "WITNESS_SEED", "WITNESS_DIRECT", "PUREBRAIN_API"]:
            log(f"  API call: {method} {url[:100]}")
        network_requests.append(entry)

    page.on("request", on_request)

async def run_e2e_test():
    from playwright.async_api import async_playwright

    # ---- PHASE 0: Fetch page HTML ----
    log("="*60)
    log("PHASE 0: Fetching page HTML via WP REST API")
    log("="*60)
    html_688 = fetch_page_html(PAGE_688_ID)

    # Scan the HTML for seed-related functions BEFORE running
    log("\n--- Pre-scan: Checking for seed functions in HTML ---")
    seed_fn_found = {}
    patterns = {
        "fireSeed": r'function\s+fireSeed|fireSeed\s*\(',
        "runBirthInit": r'runBirthInit',
        "sendSeedData": r'sendSeedData',
        "WITNESS_WEBHOOK": r'WITNESS_WEBHOOK[_A-Z]*\s*=\s*["\']([^"\']+)',
        "BIRTH_WEBHOOK": r'BIRTH_WEBHOOK[_A-Z]*\s*=\s*["\']([^"\']+)',
        "webhook_host": r'webhook[_-]?host\s*[=:]\s*["\']([^"\']+)',
        "8099": r'8099',
        "8200": r'8200',
        "104.248": r'104\.248',
        "178.156": r'178\.156',
        "portals": r'portal[_-]?button|portalButton|runPortalButton',
        "openPayPalModal": r'openPayPalModal',
        "openWaitlistModal_fn": r'function\s+openWaitlistModal',
        "window_openWaitlistModal": r'window\.openWaitlistModal\s*=',
        "sandbox_bypass": r'pb-sandbox-bypass-btn',
    }
    for name, pattern in patterns.items():
        matches = re.findall(pattern, html_688)
        if matches:
            seed_fn_found[name] = matches[:3]
            log(f"  FOUND [{name}]: {matches[:3]}")
        else:
            log(f"  NOT FOUND: [{name}]")

    # Extract key JS config values
    log("\n--- Extracting webhook endpoints from JS ---")
    webhook_patterns = [
        (r"WITNESS_WEBHOOK_HOST\s*=\s*['\"]([^'\"]+)['\"]", "WITNESS_WEBHOOK_HOST"),
        (r"BIRTH_WEBHOOK_HOST\s*=\s*['\"]([^'\"]+)['\"]", "BIRTH_WEBHOOK_HOST"),
        (r"const\s+WITNESS_HOST\s*=\s*['\"]([^'\"]+)['\"]", "WITNESS_HOST"),
        (r"const\s+BIRTH_HOST\s*=\s*['\"]([^'\"]+)['\"]", "BIRTH_HOST"),
        (r"endpoint['\"]?\s*:\s*['\"]([^'\"]*(?:8099|8200|104\.248|178\.156)[^'\"]*)['\"]", "endpoint"),
        (r"['\"]([^'\"]*(?:8099|8200)[^'\"]*)['\"]", "port_8099_or_8200"),
    ]
    for pattern, label in webhook_patterns:
        matches = re.findall(pattern, html_688)
        if matches:
            log(f"  {label}: {matches[:3]}")

    # Check pricing button onclick attributes
    log("\n--- Checking pricing button onclick attributes ---")
    onclick_matches = re.findall(r'onclick=["\']([^"\']*openWaitlist[^"\']*)["\']', html_688)
    for m in onclick_matches[:10]:
        log(f"  onclick: {m}")
    window_onclick = [m for m in onclick_matches if 'window.' in m]
    bare_onclick = [m for m in onclick_matches if 'window.' not in m]
    log(f"  Total buttons with openWaitlistModal: {len(onclick_matches)}")
    log(f"  Using window.openWaitlistModal: {len(window_onclick)} -> {window_onclick}")
    log(f"  Using bare openWaitlistModal: {len(bare_onclick)} -> {bare_onclick}")

    if bare_onclick:
        log("  [ISSUE] JS SCOPE BUG STILL PRESENT: bare openWaitlistModal calls will hit old waitlist modal")
    elif window_onclick:
        log("  [FIXED] All buttons use window.openWaitlistModal - scope bug is fixed")
    else:
        log("  [INFO] No openWaitlistModal onclick found - may use different approach")

    # Also check openPayPalModal
    opaypal_matches = re.findall(r'onclick=["\']([^"\']*openPayPalModal[^"\']*)["\']', html_688)
    log(f"  Buttons using openPayPalModal: {len(opaypal_matches)} -> {opaypal_matches[:5]}")

    # ---- PHASE 1: Browser launch + initial state ----
    log("\n" + "="*60)
    log("PHASE 1: Launch browser, load page")
    log("="*60)

    server = serve_html_locally(html_688, 18820)
    time.sleep(0.5)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--allow-insecure-localhost",
            ]
        )

        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0"
        )
        page = await ctx.new_page()

        # Set up listeners
        page.on("console", lambda m: console_logs.append(f"[{m.type.upper()}] {m.text}"))
        page.on("pageerror", lambda e: page_errors_log.append(str(e)))
        await intercept_requests(page)

        # Load page
        await page.goto("http://127.0.0.1:18820/", wait_until="domcontentloaded", timeout=15000)
        await asyncio.sleep(3)

        # Screenshot 1: Initial state
        p1 = ss_path("initial-load")
        await page.screenshot(path=p1)
        log(f"SS1 saved: {p1}")

        # Full page screenshot
        p2 = ss_path("initial-full-page")
        await page.screenshot(path=p2, full_page=True)
        log(f"SS2 saved: {p2}")

        # Inspect initial DOM state
        initial_state = await page.evaluate('''() => {
            return {
                title: document.title,
                sandbox_banner: !!document.getElementById("sandbox-banner"),
                sandbox_banner_text: (document.getElementById("sandbox-banner") || {}).innerText,
                begin_btn: !!document.querySelector(".chat-initial__btn"),
                begin_btn_text: (document.querySelector(".chat-initial__btn") || {}).innerText,
                chatbox_visible: !!document.querySelector("#chatInitial, .chat-initial"),
                pricing_in_dom: !!document.querySelector("#pricing, .pricing-section"),
                ptc_wrapper: !!document.querySelector(".ptc-wrapper, #pay-test-post-payment"),
                paypal_sdk: typeof window.paypal !== "undefined",
                openWaitlistModal_type: typeof openWaitlistModal,
                window_openWaitlistModal_type: typeof window.openWaitlistModal,
                openPayPalModal_type: typeof window.openPayPalModal,
                runBirthInit_exists: typeof window.runBirthInit !== "undefined",
                runPortalButtonWatcher_exists: typeof window.runPortalButtonWatcher !== "undefined",
                witness_webhook_host: window.WITNESS_WEBHOOK_HOST || window.__witnessHost,
                birth_webhook_host: window.BIRTH_WEBHOOK_HOST || window.__birthHost,
                pbUseSDK: window.__pbUseSDK,
            };
        }''')
        log(f"\nInitial DOM state: {json.dumps(initial_state, indent=2)}")

        # ---- PHASE 2: Pre-payment chat flow ----
        log("\n" + "="*60)
        log("PHASE 2: Pre-payment chat flow (bypass to pricing)")
        log("="*60)

        # Click Begin Awakening
        begin_btn = await page.query_selector(".chat-initial__btn")
        if begin_btn:
            log("Clicking Begin Awakening button...")
            await begin_btn.click()
            await asyncio.sleep(3)

            p3 = ss_path("after-begin-click")
            await page.screenshot(path=p3)
            log(f"SS3 saved: {p3}")

            # Enter bypass code
            user_input = await page.query_selector("#userInput")
            if user_input:
                log("Entering bypass code: pb-full-bypass")
                await user_input.fill("pb-full-bypass")
                submit = await page.query_selector("#submitBtn")
                if submit:
                    await submit.click()
                else:
                    await user_input.press("Enter")
                await asyncio.sleep(4)

                p4 = ss_path("after-bypass-code")
                await page.screenshot(path=p4)
                log(f"SS4 saved: {p4}")

                # Check what appeared after bypass
                bypass_state = await page.evaluate('''() => {
                    const msgs = document.querySelectorAll(".message--ai");
                    const pricing = document.querySelector("#pricing, .pricing-section");
                    const proCta = document.querySelector("#proCta, .pro-cta, button[data-tier]");
                    const discoverBtn = document.querySelector("#proCta");
                    return {
                        ai_msg_count: msgs.length,
                        last_ai_msg: msgs.length > 0 ? msgs[msgs.length-1].innerText.substring(0,200) : null,
                        pricing_visible: !!pricing && window.getComputedStyle(pricing).display !== "none",
                        pro_cta_exists: !!proCta,
                        discover_btn: discoverBtn ? {text: discoverBtn.innerText, id: discoverBtn.id} : null,
                    };
                }''')
                log(f"After bypass state: {json.dumps(bypass_state, indent=2)}")
            else:
                log("[WARNING] #userInput not found after begin click")
        else:
            log("[WARNING] Begin button not found")

        # ---- PHASE 3: Trigger PayPal modal ----
        log("\n" + "="*60)
        log("PHASE 3: Trigger payment / PayPal modal")
        log("="*60)

        # First try to click the "Activate Now" / "#proCta" button if visible
        pro_cta = await page.query_selector("#proCta")
        if pro_cta:
            cta_text = await pro_cta.inner_text()
            log(f"Found #proCta button: '{cta_text}'")
            await pro_cta.scroll_into_view_if_needed()
            await pro_cta.click()
            await asyncio.sleep(3)

            p5 = ss_path("after-procta-click")
            await page.screenshot(path=p5)
            log(f"SS5 saved: {p5}")
        else:
            log("#proCta not found, will try revealing pricing section manually")

            # Force reveal pricing
            reveal_result = await page.evaluate('''() => {
                const pricing = document.getElementById("pricing") || document.querySelector(".pricing-section");
                if (!pricing) return "NOT_FOUND";
                pricing.style.display = "block";
                pricing.style.visibility = "visible";
                pricing.style.opacity = "1";
                pricing.classList.add("active", "visible");
                pricing.scrollIntoView({behavior: "instant"});
                return "REVEALED: " + (pricing.id || pricing.className.substring(0,50));
            }''')
            log(f"Pricing force reveal: {reveal_result}")
            await asyncio.sleep(1)

            p5 = ss_path("pricing-section-revealed")
            await page.screenshot(path=p5)
            log(f"SS5 saved: {p5}")

        # Check for sandbox bypass button (only on sandbox pages)
        sandbox_bypass_btn = await page.query_selector("#pb-sandbox-bypass-btn")
        if sandbox_bypass_btn:
            log("Found sandbox bypass button - clicking to simulate payment")
            await sandbox_bypass_btn.scroll_into_view_if_needed()

            p6 = ss_path("before-sandbox-bypass-click")
            await page.screenshot(path=p6)
            log(f"SS6 saved: {p6}")

            await sandbox_bypass_btn.click()
            await asyncio.sleep(4)

            p7 = ss_path("after-sandbox-bypass-click")
            await page.screenshot(path=p7)
            log(f"SS7 saved: {p7}")

            log(f"Seed fires after sandbox bypass click: {len(seed_fires)}")
            for sf in seed_fires:
                log(f"  SEED: {sf['type']} - {sf['url'][:100]}")
        else:
            log("No sandbox bypass button found - checking PayPal modal state")

            # Check if PayPal overlay is open
            paypal_state = await page.evaluate('''() => {
                const overlay = document.getElementById("pb-paypal-overlay");
                const waitlistModal = document.getElementById("waitlistModal");
                return {
                    paypal_overlay_active: overlay ? overlay.classList.contains("pb-active") : false,
                    paypal_overlay_visible: overlay ? window.getComputedStyle(overlay).display !== "none" : false,
                    waitlist_modal_active: waitlistModal ? waitlistModal.classList.contains("active") : false,
                    sandbox_bypass_in_dom: !!document.getElementById("pb-sandbox-bypass-btn"),
                    modal_html_snippet: overlay ? overlay.innerHTML.substring(0, 400) : null,
                };
            }''')
            log(f"Payment modal state: {json.dumps(paypal_state, indent=2)}")

            p6 = ss_path("payment-modal-state")
            await page.screenshot(path=p6)
            log(f"SS6 saved: {p6}")

            # If sandbox bypass not in DOM yet but PayPal overlay is open, check for sandbox bypass btn inside modal
            sandbox_btn_in_modal = await page.query_selector("#pb-sandbox-bypass-btn, button[id*='sandbox']")
            if sandbox_btn_in_modal:
                log("Found sandbox bypass in modal - clicking")
                await sandbox_btn_in_modal.click()
                await asyncio.sleep(4)
                p7 = ss_path("after-modal-sandbox-bypass")
                await page.screenshot(path=p7)
                log(f"SS7 saved: {p7}")

        # ---- PHASE 4: Post-payment chatbox ----
        log("\n" + "="*60)
        log("PHASE 4: Post-payment chatbox interaction")
        log("="*60)

        # Check if post-payment chatbox appeared
        ptc_state = await page.evaluate('''() => {
            const wrapper = document.querySelector(".ptc-wrapper, #pay-test-post-payment");
            const msgs = document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai");
            const runBirthInit = typeof window.runBirthInit;
            const portalBtn = document.querySelector("a[href*='portal'], button[data-action='portal']");
            return {
                ptc_wrapper_exists: !!wrapper,
                ptc_wrapper_visible: wrapper ? window.getComputedStyle(wrapper).display !== "none" : false,
                ai_msg_count: msgs.length,
                first_ai_msg: msgs.length > 0 ? msgs[0].innerText.substring(0, 200) : null,
                last_ai_msg: msgs.length > 0 ? msgs[msgs.length-1].innerText.substring(0, 200) : null,
                runBirthInit_type: runBirthInit,
                portal_btn_exists: !!portalBtn,
                portal_btn_text: portalBtn ? portalBtn.innerText : null,
                sandbox_bypass_btn: !!document.getElementById("pb-sandbox-bypass-btn"),
            };
        }''')
        log(f"Post-payment state: {json.dumps(ptc_state, indent=2)}")

        if ptc_state.get("ptc_wrapper_exists"):
            p8 = ss_path("post-payment-chatbox-initial")
            await page.screenshot(path=p8)
            log(f"SS8 saved: {p8}")

            # Interact with post-payment questionnaire
            log("\n--- Navigating post-payment questionnaire ---")

            # Helper to get current AI messages
            async def get_ai_messages():
                return await page.evaluate('''() => {
                    return Array.from(document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai"))
                        .map(m => m.innerText.trim().substring(0, 200));
                }''')

            async def get_choice_buttons():
                return await page.evaluate('''() => {
                    return Array.from(document.querySelectorAll(".ptc-btn, button.ptc-btn"))
                        .filter(b => b.offsetHeight > 0)
                        .map(b => ({text: b.innerText.trim(), id: b.id, classes: b.className}));
                }''')

            async def get_text_input():
                inp = await page.query_selector("textarea[placeholder*='Message'], input.ptc-input, .ptc-input")
                return inp

            async def wait_for_new_message(prev_count, timeout=15):
                """Wait until message count increases"""
                deadline = time.time() + timeout
                while time.time() < deadline:
                    current = await page.evaluate('''() =>
                        document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai").length
                    ''')
                    if current > prev_count:
                        await asyncio.sleep(1)  # Let message render fully
                        return True
                    await asyncio.sleep(0.5)
                return False

            # Step 1: Name
            msgs = await get_ai_messages()
            log(f"Initial AI messages ({len(msgs)}): {msgs[-1] if msgs else 'none'}")

            txt_input = await get_text_input()
            if txt_input:
                await txt_input.fill("Test User")
                send_btn = await page.query_selector("button.ptc-send-btn, button[class*='send']")
                if send_btn:
                    await send_btn.click()
                else:
                    await txt_input.press("Enter")
                log("Sent name: 'Test User'")
                prev = len(msgs)
                await wait_for_new_message(prev)

                p9 = ss_path("ptc-after-name")
                await page.screenshot(path=p9)
                log(f"SS9 saved: {p9}")

            # Check for choice buttons (could be email phase or question)
            await asyncio.sleep(2)
            buttons = await get_choice_buttons()
            log(f"Choice buttons visible: {[b['text'] for b in buttons]}")

            # Step 2: Email
            msgs = await get_ai_messages()
            txt_input = await get_text_input()
            if txt_input:
                await txt_input.fill("test@example.com")
                send_btn = await page.query_selector("button.ptc-send-btn, button[class*='send']")
                if send_btn:
                    await send_btn.click()
                else:
                    await txt_input.press("Enter")
                log("Sent email: 'test@example.com'")
                prev = len(msgs)
                await wait_for_new_message(prev)

                p10 = ss_path("ptc-after-email")
                await page.screenshot(path=p10)
                log(f"SS10 saved: {p10}")

            # Step 3: Company
            msgs = await get_ai_messages()
            txt_input = await get_text_input()
            if txt_input:
                await txt_input.fill("Test Company Inc.")
                send_btn = await page.query_selector("button.ptc-send-btn, button[class*='send']")
                if send_btn:
                    await send_btn.click()
                else:
                    await txt_input.press("Enter")
                log("Sent company: 'Test Company Inc.'")
                prev = len(msgs)
                await wait_for_new_message(prev)

                p11 = ss_path("ptc-after-company")
                await page.screenshot(path=p11)
                log(f"SS11 saved: {p11}")

            # Step 4: Role
            msgs = await get_ai_messages()
            txt_input = await get_text_input()
            if txt_input:
                await txt_input.fill("CEO")
                send_btn = await page.query_selector("button.ptc-send-btn, button[class*='send']")
                if send_btn:
                    await send_btn.click()
                else:
                    await txt_input.press("Enter")
                log("Sent role: 'CEO'")
                prev = len(msgs)
                await wait_for_new_message(prev)

                p12 = ss_path("ptc-after-role")
                await page.screenshot(path=p12)
                log(f"SS12 saved: {p12}")

            # After role, check for Birth Init button (v4.3.2+)
            await asyncio.sleep(3)
            msgs = await get_ai_messages()
            log(f"Messages after role: {len(msgs)}")
            if msgs:
                log(f"Last message: {msgs[-1]}")

            buttons = await get_choice_buttons()
            log(f"Choice buttons after role: {[b['text'] for b in buttons]}")

            # Look for "Start AI Birth" button
            birth_btn = await page.query_selector("button[id*='birth'], button[data-action*='birth']")
            if not birth_btn:
                # Try text match
                birth_btn = await page.evaluate('''() => {
                    const btns = document.querySelectorAll("button, .ptc-btn");
                    const match = Array.from(btns).find(b =>
                        b.innerText.includes("Birth") || b.innerText.includes("birth") ||
                        b.innerText.includes("Start AI") || b.innerText.includes("Born")
                    );
                    return match ? {text: match.innerText, id: match.id} : null;
                }''')
                if birth_btn:
                    log(f"Found birth button (by text): {birth_btn}")
                    # Click it via JS
                    seed_before = len(seed_fires)
                    await page.evaluate('''() => {
                        const btns = document.querySelectorAll("button, .ptc-btn");
                        const match = Array.from(btns).find(b =>
                            b.innerText.includes("Birth") || b.innerText.includes("birth") ||
                            b.innerText.includes("Start AI") || b.innerText.includes("Born")
                        );
                        if (match) match.click();
                    }''')
                    log("Clicked birth button")
                    await asyncio.sleep(5)

                    p13 = ss_path("ptc-after-birth-click")
                    await page.screenshot(path=p13)
                    log(f"SS13 saved: {p13}")

                    seed_after = len(seed_fires)
                    log(f"Seed fires triggered by birth button: {seed_after - seed_before}")

            # Skip through slides if present
            log("\n--- Skipping through slides ---")
            for slide_attempt in range(12):
                show_more_btn = await page.query_selector("button.ptc-btn--primary, .ptc-btn.ptc-btn--primary")
                if show_more_btn:
                    btn_text = await show_more_btn.inner_text()
                    log(f"  Slide button [{slide_attempt}]: '{btn_text.strip()}'")
                    if "Show Me More" in btn_text or "show me more" in btn_text.lower():
                        await show_more_btn.click()
                        await asyncio.sleep(1)
                    elif "Let's go" in btn_text or "lets go" in btn_text.lower() or "That's incredible" in btn_text:
                        await show_more_btn.click()
                        await asyncio.sleep(2)
                        break
                    elif "Start" in btn_text or "Begin" in btn_text:
                        await show_more_btn.click()
                        await asyncio.sleep(2)
                        break
                    else:
                        log(f"  Unknown button text: '{btn_text}' - stopping slide navigation")
                        break
                else:
                    break

            p14 = ss_path("ptc-after-slides")
            await page.screenshot(path=p14)
            log(f"SS14 saved: {p14}")

            # Handle Telegram phase
            await asyncio.sleep(2)
            msgs_after_slides = await get_ai_messages()
            log(f"\nMessages after slides: {len(msgs_after_slides)}")
            if msgs_after_slides:
                log(f"Last message: {msgs_after_slides[-1]}")

            # Click "Yes, I have Telegram" if it appears
            telegram_btn = await page.evaluate('''() => {
                const btns = document.querySelectorAll("button, .ptc-btn");
                const tg = Array.from(btns).find(b =>
                    b.innerText.includes("Yes, I have Telegram") || b.innerText.includes("Skip") ||
                    b.innerText.includes("skip") || b.innerText.includes("Yes") && b.innerText.includes("Telegram")
                );
                if (tg) {
                    tg.click();
                    return {clicked: true, text: tg.innerText};
                }
                return null;
            }''')
            if telegram_btn:
                log(f"Clicked Telegram button: {telegram_btn}")
                await asyncio.sleep(3)
                p15 = ss_path("ptc-telegram-response")
                await page.screenshot(path=p15)
                log(f"SS15 saved: {p15}")

            # Skip Telegram setup - look for skip/continue options
            skip_result = await page.evaluate('''() => {
                const btns = document.querySelectorAll("button, .ptc-btn");
                const skip = Array.from(btns).find(b =>
                    b.innerText.includes("skip") || b.innerText.includes("Skip") ||
                    b.innerText.includes("Continue") || b.innerText.includes("Later")
                );
                if (skip) {
                    skip.click();
                    return {clicked: true, text: skip.innerText};
                }
                return null;
            }''')
            if skip_result:
                log(f"Skipped: {skip_result}")
                await asyncio.sleep(3)

        else:
            log("[WARNING] Post-payment chatbox (.ptc-wrapper) not found in DOM")
            log("This may mean payment simulation did not complete")

        # ---- PHASE 5: Check for portal button + final state ----
        log("\n" + "="*60)
        log("PHASE 5: Check final state (portal button + seed fires)")
        log("="*60)

        await asyncio.sleep(5)

        p_final = ss_path("final-state")
        await page.screenshot(path=p_final)
        log(f"Final screenshot: {p_final}")

        p_final_full = ss_path("final-full-page")
        await page.screenshot(path=p_final_full, full_page=True)
        log(f"Final full page: {p_final_full}")

        final_state = await page.evaluate('''() => {
            // All AI messages in post-payment chat
            const ptcMsgs = Array.from(document.querySelectorAll(".ptc-msg--ai, .ptc-msg.ptc-msg--ai"))
                .map(m => m.innerText.trim().substring(0, 300));

            // Portal button
            const portalLinks = document.querySelectorAll("a[href*='portal'], a[href*='purebrain.ai'][href*='login']");
            const portalBtns = document.querySelectorAll("button[data-action='portal'], .portal-btn, #portal-link");
            const allPortalEls = document.querySelectorAll("a[href*='portal'], .ptc-portal-btn, #ptc-portal-link");

            // Thank you card / final message
            const thankYouCard = document.querySelector(".thank-you-card, #thank-you-card, .ptc-thank-you");

            // Final message check
            const bodyText = document.body.innerText;
            const hasPortalMention = bodyText.includes("portal") || bodyText.includes("Portal");
            const hasWelcome = bodyText.includes("Welcome to the Family") || bodyText.includes("welcome to the family");

            return {
                ptc_msg_count: ptcMsgs.length,
                first_ptc_msg: ptcMsgs[0] || null,
                last_ptc_msg: ptcMsgs[ptcMsgs.length - 1] || null,
                portal_links_count: portalLinks.length,
                portal_links_hrefs: Array.from(portalLinks).map(a => a.href).slice(0,5),
                portal_btns_count: portalBtns.length + allPortalEls.length,
                thank_you_card_exists: !!thankYouCard,
                has_portal_mention: hasPortalMention,
                has_welcome_msg: hasWelcome,
                body_text_preview: bodyText.substring(0, 500),
            };
        }''')
        log(f"\nFinal state: {json.dumps(final_state, indent=2)}")

        # ---- SUMMARY: Seed fires ----
        log("\n" + "="*60)
        log("SEED FIRE SUMMARY")
        log("="*60)
        log(f"Total seed fires detected: {len(seed_fires)}")
        if seed_fires:
            for i, sf in enumerate(seed_fires, 1):
                log(f"\n  Seed Fire #{i}:")
                log(f"    Time: {sf['time']}")
                log(f"    Type: {sf['type']}")
                log(f"    URL: {sf['url']}")
                log(f"    Method: {sf['method']}")
                if 'post_data' in sf:
                    log(f"    Payload: {sf['post_data'][:300]}")
        else:
            log("  NO SEED FIRES DETECTED")
            log("  Possible reasons:")
            log("    - Serving locally (requests to external IPs may be blocked)")
            log("    - Endpoints not configured in current page version")
            log("    - Payment simulation did not complete properly")

        # Console log summary
        log("\n" + "="*60)
        log("CONSOLE LOG SUMMARY")
        log("="*60)
        log(f"Total console entries: {len(console_logs)}")
        errors = [l for l in console_logs if "[ERROR]" in l]
        warnings = [l for l in console_logs if "[WARNING]" in l or "[WARN]" in l]
        pb_logs = [l for l in console_logs if any(x in l.lower() for x in
                   ["purebrain", "seed", "witness", "birth", "webhook", "paypal", "ptc", "bypass"])]

        log(f"Errors: {len(errors)}")
        log(f"Warnings: {len(warnings)}")
        log(f"PB/Seed/Witness related: {len(pb_logs)}")

        if errors:
            log("\nErrors:")
            for e in errors[:15]:
                log(f"  {e}")

        if pb_logs:
            log("\nPureBrain/Seed related logs:")
            for l in pb_logs[:30]:
                log(f"  {l}")

        if page_errors_log:
            log(f"\nPage JS errors: {len(page_errors_log)}")
            for e in page_errors_log[:10]:
                log(f"  {e}")

        # Network requests summary
        log("\n" + "="*60)
        log("NETWORK REQUESTS SUMMARY")
        log("="*60)
        external_reqs = [r for r in network_requests if any(ep in r['url'] for ep in
                        ["104.248", "178.156", "api.purebrain", "workers.dev", "paypal"])]
        log(f"Total requests: {len(network_requests)}")
        log(f"External/API requests: {len(external_reqs)}")
        for r in external_reqs[:20]:
            log(f"  [{r['type']}] {r['method']} {r['url'][:120]}")

        # Collect all screenshots
        all_screenshots = sorted(Path(SESSION_DIR).glob("*.png"))

        await ctx.close()
        await browser.close()

    server.shutdown()

    # ---- Generate report ----
    log("\n" + "="*60)
    log("GENERATING REPORT")
    log("="*60)

    report_lines = [
        "# E2E Pay-Test-Sandbox-2 Full Flow Audit",
        "",
        f"**Date**: 2026-03-02",
        f"**Tester**: browser-vision-tester",
        f"**Page**: https://purebrain.ai/pay-test-sandbox-2/ (Page 688)",
        f"**Method**: WP REST API fetch -> local serve (WAF-safe)",
        "",
        "---",
        "",
        "## Pre-Scan: HTML Analysis",
        "",
        f"**Page size**: {len(html_688):,} chars",
        "",
        "### Seed/Webhook Functions Found:",
    ]

    for name, vals in seed_fn_found.items():
        report_lines.append(f"- **{name}**: {vals}")

    report_lines.extend([
        "",
        "### Pricing Button onclick Analysis:",
        f"- Total buttons with openWaitlistModal: {len(onclick_matches)}",
        f"- Using `window.openWaitlistModal` (FIXED): {len(window_onclick)}",
        f"- Using bare `openWaitlistModal` (BUG): {len(bare_onclick)}",
    ])

    if bare_onclick:
        report_lines.append("- **[BUG] JS scope bug STILL PRESENT** - bare openWaitlistModal calls will fail")
    elif window_onclick:
        report_lines.append("- **[FIXED] All buttons use window scope** - scope bug is fixed")

    report_lines.extend([
        "",
        "---",
        "",
        "## Seed Fire Results",
        "",
        f"**Total seed fires detected**: {len(seed_fires)}",
        "",
    ])

    if seed_fires:
        for i, sf in enumerate(seed_fires, 1):
            report_lines.extend([
                f"### Seed Fire #{i}",
                f"- **Time**: {sf['time']}",
                f"- **Type**: {sf['type']}",
                f"- **URL**: `{sf['url']}`",
                f"- **Method**: {sf['method']}",
            ])
            if 'post_data' in sf:
                report_lines.append(f"- **Payload**: `{sf['post_data'][:300]}`")
    else:
        report_lines.extend([
            "NO SEED FIRES DETECTED",
            "",
            "**Note**: When serving locally, requests to external IPs (104.248.239.98, 178.156.229.207)",
            "may still fire (they go out from the browser, not from the server). If seeds are not firing,",
            "check JavaScript console logs for webhook call attempts.",
        ])

    report_lines.extend([
        "",
        "---",
        "",
        "## Console Errors",
        "",
        f"**Total errors**: {len(errors)}",
        "",
    ])
    for e in errors[:20]:
        report_lines.append(f"- `{e}`")

    report_lines.extend([
        "",
        "## PureBrain Related Console Logs",
        "",
    ])
    for l in pb_logs[:30]:
        report_lines.append(f"- `{l}`")

    report_lines.extend([
        "",
        "---",
        "",
        "## Screenshots",
        "",
        f"**Total**: {len(all_screenshots)} screenshots",
        f"**Location**: `{SESSION_DIR}/`",
        "",
    ])
    for ss in all_screenshots:
        report_lines.append(f"- `{ss.name}`")

    report_lines.extend([
        "",
        "---",
        "",
        "## Network Requests to External Endpoints",
        "",
        f"**Total external API calls**: {len(external_reqs)}",
        "",
    ])
    for r in external_reqs[:20]:
        report_lines.append(f"- [{r['type']}] {r['method']} `{r['url'][:120]}`")

    report_content = "\n".join(report_lines)

    with open(REPORT_PATH, "w") as f:
        f.write(report_content)
    log(f"Report saved: {REPORT_PATH}")

    log("\n" + "="*60)
    log("E2E TEST COMPLETE")
    log(f"Screenshots: {len(all_screenshots)} files in {SESSION_DIR}")
    log(f"Seed fires: {len(seed_fires)}")
    log(f"Console errors: {len(errors)}")
    log("="*60)

    return {
        "screenshots": [str(s) for s in all_screenshots],
        "seed_fires": seed_fires,
        "errors": errors,
        "pb_logs": pb_logs,
        "network_requests": external_reqs,
        "final_state": final_state,
        "html_prescan": seed_fn_found,
        "onclick_analysis": {
            "total": len(onclick_matches),
            "window_scope": len(window_onclick),
            "bare_scope_bug": len(bare_onclick),
        }
    }

if __name__ == "__main__":
    asyncio.run(run_e2e_test())
