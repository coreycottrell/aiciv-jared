#!/usr/bin/env python3
"""
QA Test: pay-test-sandbox-2 PayPal Modal Visual Test
Date: 2026-03-01
Strategy: Serve locally (WAF-safe), use domcontentloaded to avoid networkidle timeout
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

PAGE_688_ID = 688
PAGE_689_ID = 689
PUREBRAIN_URL = "https://purebrain.ai"
WP_USER = "Aether"
WP_APP_PASSWORD = "FlFr2VOtlHiHaJWjzW96OHUJ"
SESSION_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox2-qa-20260301"
os.makedirs(SESSION_DIR, exist_ok=True)

def log(msg):
    print(f"[QA] {msg}", flush=True)

def fetch_page_html(page_id):
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
    log(f"Page {page_id}: {len(raw)} chars")
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
    log(f"Local server port {port}")
    return server

async def run_visual_qa():
    from playwright.async_api import async_playwright

    html_688 = fetch_page_html(PAGE_688_ID)
    html_689 = fetch_page_html(PAGE_689_ID)

    server_688 = serve_html_locally(html_688, 18810)
    server_689 = serve_html_locally(html_689, 18811)
    time.sleep(0.5)

    sc = [0]
    def screenshot(page, label):
        sc[0] += 1
        return f"{SESSION_DIR}/{sc[0]:03d}-{label}.png"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-web-security",
                  "--disable-features=VizDisplayCompositor"]
        )

        console_688 = []
        errors_688 = []

        # ==== PAGE 688: pay-test-sandbox-2 ====
        log("\n=== TESTING PAGE 688: pay-test-sandbox-2 ===")
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0"
        )
        page = await ctx.new_page()
        page.on("console", lambda m: console_688.append(f"[{m.type.upper()}] {m.text}"))
        page.on("pageerror", lambda e: errors_688.append(f"[PAGE-ERROR] {e}"))

        # Use domcontentloaded - avoids waiting for PayPal SDK (external)
        await page.goto("http://127.0.0.1:18810/", wait_until="domcontentloaded", timeout=15000)
        await asyncio.sleep(3)  # Let JS run

        # Screenshot 1: Initial page state
        p = screenshot(page, "p688-initial-load")
        await page.screenshot(path=p, full_page=False)
        log(f"SS1: {p}")

        # Check sandbox banner
        banner_check = await page.evaluate('''() => {
            const banner = document.getElementById("sandbox-banner");
            if (!banner) return {found: false};
            const style = window.getComputedStyle(banner);
            return {
                found: true,
                visible: style.display !== "none" && style.visibility !== "hidden",
                text: banner.innerText.trim()
            };
        }''')
        log(f"Sandbox banner: {banner_check}")

        # Scroll down to take a full-page screenshot too
        p = screenshot(page, "p688-full-page")
        await page.screenshot(path=p, full_page=True)
        log(f"SS2 (full page): {p}")

        # Check begin button
        begin_btn = await page.query_selector(".chat-initial__btn")
        log(f"Begin button found: {begin_btn is not None}")

        # Click begin to start chatbox
        if begin_btn:
            await begin_btn.click()
            await asyncio.sleep(2)
            p = screenshot(page, "p688-after-begin-click")
            await page.screenshot(path=p, full_page=False)
            log(f"SS3 (after begin): {p}")

            # Try bypass code
            user_input = await page.query_selector("#userInput")
            if user_input:
                await user_input.fill("pb-full-bypass")
                submit = await page.query_selector("#submitBtn")
                if submit:
                    await submit.click()
                else:
                    await user_input.press("Enter")
                await asyncio.sleep(3)
                p = screenshot(page, "p688-after-bypass-code")
                await page.screenshot(path=p, full_page=False)
                log(f"SS4 (after bypass): {p}")

        # Force reveal pricing section
        reveal = await page.evaluate('''() => {
            const pricing = document.getElementById("pricing") || document.querySelector(".pricing-section");
            if (!pricing) return "NOT_FOUND";
            pricing.style.display = "block";
            pricing.style.visibility = "visible";
            pricing.style.opacity = "1";
            pricing.classList.add("active");
            pricing.scrollIntoView({behavior: "instant"});
            return `REVEALED: ${pricing.id || pricing.className}`;
        }''')
        log(f"Pricing reveal: {reveal}")
        await asyncio.sleep(1)

        p = screenshot(page, "p688-pricing-section")
        await page.screenshot(path=p, full_page=False)
        log(f"SS5 (pricing section): {p}")

        # Get card info
        card_info = await page.evaluate('''() => {
            const cards = document.querySelectorAll(".pricing-card");
            return Array.from(cards).slice(0, 5).map(c => ({
                text: c.innerText.substring(0, 100).trim(),
                btn_onclick: (c.querySelector("button") || {}).getAttribute ? (c.querySelector("button") || {}).getAttribute("onclick") : null
            }));
        }''')
        log(f"Pricing cards: {json.dumps(card_info, indent=2)}")

        # Get the page-level openWaitlistModal state
        fn_info = await page.evaluate('''() => {
            return {
                openWaitlistModal_type: typeof openWaitlistModal,
                openPayPalCheckout_type: typeof window.openPayPalCheckout,
                window_openWaitlistModal_defined: typeof window.openWaitlistModal !== "undefined",
                pbUseSDK: window.__pbUseSDK,
                paypal_sdk_loaded: typeof window.paypal !== "undefined"
            };
        }''')
        log(f"Function state: {json.dumps(fn_info)}")

        # Now call openWaitlistModal directly to trigger the PayPal modal
        log("\n--- Calling openWaitlistModal('Awakened') directly ---")
        call_result = await page.evaluate('''async () => {
            try {
                // First check which openWaitlistModal will execute
                const fnStr = (window.openWaitlistModal || openWaitlistModal).toString().substring(0, 300);

                // Call it
                if (typeof window.openWaitlistModal === "function") {
                    window.openWaitlistModal("Awakened");
                } else if (typeof openWaitlistModal === "function") {
                    openWaitlistModal("Awakened");
                } else {
                    return {error: "openWaitlistModal not found"};
                }

                // Wait for modal to render
                await new Promise(r => setTimeout(r, 2000));

                // Check what opened
                const overlay = document.getElementById("pb-paypal-overlay");
                const waitlistModal = document.getElementById("waitlistModal");
                const tierName = document.getElementById("pb-paypal-tier-name");
                const priceEl = document.getElementById("pb-paypal-price-line");
                const paypalContainer = document.getElementById("pb-paypal-buttons-container");
                const paypalBtns = document.querySelectorAll(".paypal-buttons");

                // Also check for fallback button
                const fallbackBtn = document.querySelector("#pb-paypal-buttons-container a, #pb-paypal-buttons-container button");

                return {
                    fn_used: fnStr,
                    pb_paypal_overlay_active: overlay && overlay.classList.contains("pb-active"),
                    pb_paypal_overlay_visible: !!overlay && window.getComputedStyle(overlay).display !== "none",
                    waitlist_modal_active: waitlistModal && waitlistModal.classList.contains("active"),
                    tier_name_text: tierName ? tierName.innerText : null,
                    price_text: priceEl ? priceEl.innerText : null,
                    paypal_container_html: paypalContainer ? paypalContainer.innerHTML.substring(0, 300) : null,
                    paypal_sdk_buttons: paypalBtns.length,
                    fallback_btn: fallbackBtn ? fallbackBtn.outerHTML.substring(0, 200) : null,
                    sandbox_badge_visible: document.body.innerHTML.includes("SANDBOX TEST")
                };
            } catch(e) {
                return {error: e.message, stack: e.stack};
            }
        }''')
        log(f"openWaitlistModal call result: {json.dumps(call_result, indent=2)}")

        await asyncio.sleep(2)
        p = screenshot(page, "p688-after-openWaitlistModal-Awakened")
        await page.screenshot(path=p, full_page=False)
        log(f"SS6 (after openWaitlistModal Awakened): {p}")

        # If waitlist modal opened instead of PayPal, screenshot that too
        wm_check = await page.evaluate('''() => {
            const wm = document.getElementById("waitlistModal");
            if (!wm) return null;
            return {
                active: wm.classList.contains("active"),
                visible: window.getComputedStyle(wm).display !== "none",
                html_snippet: wm.innerHTML.substring(0, 400)
            };
        }''')
        if wm_check:
            log(f"Waitlist modal state: {json.dumps(wm_check)}")

        # Try clicking a pricing card button
        tier_btns = await page.query_selector_all("button[onclick*='openWaitlistModal']")
        log(f"Tier buttons with openWaitlistModal onclick: {len(tier_btns)}")

        if tier_btns and len(tier_btns) > 0:
            # Close any open modal first
            await page.evaluate('''() => {
                const overlay = document.getElementById("pb-paypal-overlay");
                if (overlay) overlay.classList.remove("pb-active");
                const wm = document.getElementById("waitlistModal");
                if (wm) wm.classList.remove("active");
            }''')

            # Click first button
            btn = tier_btns[0]
            btn_text = await btn.inner_text()
            btn_onclick = await btn.get_attribute("onclick")
            log(f"Clicking button: '{btn_text.strip()}' onclick='{btn_onclick}'")

            p = screenshot(page, "p688-before-card-btn-click")
            await page.screenshot(path=p, full_page=False)

            await btn.scroll_into_view_if_needed()
            await btn.click()
            await asyncio.sleep(2)

            p = screenshot(page, "p688-after-card-btn-click")
            await page.screenshot(path=p, full_page=False)
            log(f"SS7-8 (card button click): {p}")

            # Final modal check
            modal_state = await page.evaluate('''() => {
                const overlay = document.getElementById("pb-paypal-overlay");
                const wm = document.getElementById("waitlistModal");
                const tierEl = document.getElementById("pb-paypal-tier-name");
                const priceEl = document.getElementById("pb-paypal-price-line");
                const container = document.getElementById("pb-paypal-buttons-container");
                return {
                    paypal_modal_active: overlay ? overlay.classList.contains("pb-active") : false,
                    waitlist_modal_active: wm ? wm.classList.contains("active") : false,
                    tier_name: tierEl ? tierEl.innerText : null,
                    price: priceEl ? priceEl.innerText : null,
                    container_content: container ? container.innerHTML.substring(0, 500) : null,
                    paypal_btns_rendered: document.querySelectorAll(".paypal-buttons").length,
                    body_overflow: document.body.style.overflow
                };
            }''')
            log(f"Final modal state: {json.dumps(modal_state, indent=2)}")

        # Console log summary
        log(f"\n--- Console Logs Summary (page 688) ---")
        log(f"Total entries: {len(console_688)}")
        pb_logs = [l for l in console_688 if "PB" in l or "paypal" in l.lower() or "sandbox" in l.lower()]
        errs = [l for l in console_688 if "ERROR" in l or "error" in l.lower()]
        log(f"PB/PayPal/Sandbox related: {len(pb_logs)}")
        log(f"Errors: {len(errs)}")
        for l in pb_logs[:15]:
            log(f"  {l}")
        if errs:
            log("Errors:")
            for l in errs[:10]:
                log(f"  {l}")

        # Page errors
        log(f"Page JS errors: {len(errors_688)}")
        for e in errors_688[:5]:
            log(f"  {e}")

        await ctx.close()

        # ==== PAGE 689: pay-test-2 SCREENSHOT ONLY ====
        log("\n=== TESTING PAGE 689: pay-test-2 (screenshot only, no PayPal interaction) ===")
        console_689 = []
        ctx2 = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0"
        )
        page2 = await ctx2.new_page()
        page2.on("console", lambda m: console_689.append(f"[{m.type.upper()}] {m.text}"))

        await page2.goto("http://127.0.0.1:18811/", wait_until="domcontentloaded", timeout=15000)
        await asyncio.sleep(3)

        p = screenshot(page2, "p689-initial-load")
        await page2.screenshot(path=p, full_page=False)
        log(f"SS (page 689 initial): {p}")

        p = screenshot(page2, "p689-full-page")
        await page2.screenshot(path=p, full_page=True)
        log(f"SS (page 689 full page): {p}")

        p689_state = await page2.evaluate('''() => {
            return {
                begin_btn: !!document.querySelector(".chat-initial__btn"),
                chat_initial: !!document.querySelector(".chat-initial, #chatInitial"),
                pricing_in_dom: !!document.querySelector("#pricing, .pricing-section"),
                title: document.title,
                sandbox_banner: !!document.getElementById("sandbox-banner")
            };
        }''')
        log(f"Page 689 state: {json.dumps(p689_state)}")

        p689_errors = [l for l in console_689 if "ERROR" in l]
        log(f"Page 689 errors: {len(p689_errors)}")

        await ctx2.close()
        await browser.close()

    server_688.shutdown()
    server_689.shutdown()

    # Final summary
    log("\n" + "="*60)
    log("QA TEST COMPLETE")
    log("="*60)
    all_ss = sorted(Path(SESSION_DIR).glob("*.png"))
    log(f"Screenshots saved: {len(all_ss)} files")
    for ss in all_ss:
        log(f"  {ss}")

if __name__ == "__main__":
    asyncio.run(run_visual_qa())
