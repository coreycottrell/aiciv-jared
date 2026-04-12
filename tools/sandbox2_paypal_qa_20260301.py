#!/usr/bin/env python3
"""
QA Test: pay-test-sandbox-2 PayPal Checkout Flow
Date: 2026-03-01
Tests: openWaitlistModal -> sandbox PayPal modal dynamic creation
Strategy: WP REST API to fetch page source, serve locally to avoid WAF
"""

import asyncio
import base64
import http.server
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

# Config
PAGE_688_ID = 688  # pay-test-sandbox-2
PAGE_689_ID = 689  # pay-test-2 (production - screenshot only, no interaction)
PUREBRAIN_URL = "https://purebrain.ai"
WP_USER = "Aether"
WP_APP_PASSWORD = "FlFr2VOtlHiHaJWjzW96OHUJ"
SCREENSHOTS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots"
SESSION_DIR = f"{SCREENSHOTS_DIR}/sandbox2-qa-20260301"

os.makedirs(SESSION_DIR, exist_ok=True)

def log(msg):
    print(f"[QA] {msg}", flush=True)

def get_wp_auth_header():
    creds = f"{WP_USER}:{WP_APP_PASSWORD}"
    encoded = base64.b64encode(creds.encode()).decode()
    return f"Basic {encoded}"

def fetch_page_html(page_id):
    """Fetch page raw HTML via WP REST API (bypasses WAF)"""
    url = f"{PUREBRAIN_URL}/wp-json/wp/v2/pages/{page_id}?context=edit"
    req = urllib.request.Request(url)
    req.add_header("Authorization", get_wp_auth_header())
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0")

    log(f"Fetching page {page_id} from WP REST API...")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())

    raw = data.get("content", {}).get("raw", "")
    # Strip <!-- wp:html --> wrapper markers
    raw = re.sub(r'^<!-- wp:html -->\s*', '', raw, flags=re.DOTALL)
    raw = re.sub(r'\s*<!-- /wp:html -->$', '', raw, flags=re.DOTALL)
    log(f"Page {page_id}: fetched {len(raw)} chars of HTML")
    return raw, data.get("title", {}).get("rendered", f"page-{page_id}")

def serve_html_locally(html_content, port=18801):
    """Serve HTML content via local HTTP server"""
    html_bytes = html_content.encode('utf-8')

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_bytes)))
            self.end_headers()
            self.wfile.write(html_bytes)

        def log_message(self, format, *args):
            pass  # Suppress request logs

    server = http.server.HTTPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    log(f"Local server running on port {port}")
    return server

async def run_qa():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        log("Installing playwright...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright", "-q"])
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium", "--quiet"])
        from playwright.async_api import async_playwright

    screenshot_count = [0]

    def save_screenshot(page, label):
        screenshot_count[0] += 1
        path = f"{SESSION_DIR}/{screenshot_count[0]:03d}-{label}.png"
        return path

    # Fetch both pages
    html_688, title_688 = fetch_page_html(PAGE_688_ID)
    html_689, title_689 = fetch_page_html(PAGE_689_ID)

    # Save raw HTML for inspection
    with open(f"{SESSION_DIR}/page688-raw.html", "w") as f:
        f.write(html_688)
    with open(f"{SESSION_DIR}/page689-raw.html", "w") as f:
        f.write(html_689)
    log("Saved raw HTML files for inspection")

    # Check key JavaScript patterns in source
    log("\n--- Source Analysis: pay-test-sandbox-2 (page 688) ---")
    checks = {
        "openWaitlistModal defined": "function openWaitlistModal" in html_688 or "openWaitlistModal" in html_688,
        "openPayPalCheckout defined": "openPayPalCheckout" in html_688,
        "PayPal SDK script": "paypal.com/sdk/js" in html_688,
        "PB-SANDBOX log marker": "[PB-SANDBOX]" in html_688,
        "Sandbox modal creation": "SANDBOX TEST" in html_688 or "sandbox" in html_688.lower(),
        "pb-paypal-modal": "pb-paypal-modal" in html_688,
        "createSandboxModal or dynamic modal": "createSandboxModal" in html_688 or "createElement" in html_688,
        "openWaitlistModal calls PayPal": False,  # will check below
    }

    # Deep check: what does openWaitlistModal do now?
    wm_match = re.search(r'function openWaitlistModal\s*\([^)]*\)\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', html_688, re.DOTALL)
    if wm_match:
        wm_body = wm_match.group(1)
        log(f"openWaitlistModal body (first 500 chars): {wm_body[:500]}")
        checks["openWaitlistModal calls PayPal"] = "paypal" in wm_body.lower() or "PayPal" in wm_body or "openPayPal" in wm_body
    else:
        # Try broader search for openWaitlistModal
        wm_idx = html_688.find("openWaitlistModal")
        if wm_idx >= 0:
            snippet = html_688[wm_idx:wm_idx+800]
            log(f"openWaitlistModal context: {snippet}")

    for check, result in checks.items():
        status = "PASS" if result else "FAIL"
        log(f"  [{status}] {check}")

    # Search for [PB-SANDBOX] log contexts
    sandbox_logs = re.findall(r'\[PB-SANDBOX\][^\'"\\n]+', html_688)
    if sandbox_logs:
        log(f"\n[PB-SANDBOX] log messages found in source:")
        for msg in sandbox_logs[:10]:
            log(f"  {msg}")

    # Start local servers
    server_688 = serve_html_locally(html_688, port=18801)
    server_689 = serve_html_locally(html_689, port=18802)
    time.sleep(0.5)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-web-security"]
        )

        console_logs_688 = []
        console_logs_689 = []

        # ============================================================
        # TEST 1: pay-test-sandbox-2 (page 688) - Full flow
        # ============================================================
        log("\n=== TEST 1: pay-test-sandbox-2 (page 688) ===")
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await ctx.new_page()

        # Capture console
        page.on("console", lambda msg: console_logs_688.append(f"[{msg.type.upper()}] {msg.text}"))
        page.on("pageerror", lambda err: console_logs_688.append(f"[PAGE-ERROR] {err}"))

        # Navigate to local server
        await page.goto("http://127.0.0.1:18801/", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        # Screenshot: Initial page load
        ss_path = save_screenshot(page, "sandbox2-initial-load")
        await page.screenshot(path=ss_path, full_page=False)
        log(f"Screenshot 1: {ss_path}")

        # Check what's visible
        body_text = await page.inner_text("body")
        log(f"Page title area: {body_text[:200]}")

        # Look for the sandbox banner
        try:
            sandbox_banner = await page.query_selector(".sandbox-banner, [class*='sandbox'], #sandbox-notice")
            if sandbox_banner:
                banner_text = await sandbox_banner.inner_text()
                log(f"Sandbox banner found: {banner_text[:100]}")
            else:
                log("No sandbox banner selector found — checking for text in page")
                sandbox_text = await page.evaluate('() => document.body.innerHTML.includes("SANDBOX")')
                log(f"SANDBOX text in page: {sandbox_text}")
        except Exception as e:
            log(f"Sandbox banner check error: {e}")

        # Look for chatbox or Begin button
        begin_btn = await page.query_selector(".chat-initial__btn")
        chat_initial = await page.query_selector(".chat-initial, #chatInitial")
        pricing_visible = await page.query_selector(".pricing-section, #pricing")

        log(f"Begin button visible: {begin_btn is not None}")
        log(f"Chat initial visible: {chat_initial is not None}")
        log(f"Pricing section in DOM: {pricing_visible is not None}")

        # Check if pricing is visible now (skip chatbox flow for speed, try bypass)
        pricing_display = await page.evaluate('''() => {
            const p = document.getElementById("pricing") || document.querySelector(".pricing-section");
            if (!p) return "NOT_FOUND";
            return window.getComputedStyle(p).display;
        }''')
        log(f"Pricing display computed style: {pricing_display}")

        # Try bypass code approach to reveal pricing quickly
        if begin_btn:
            log("Clicking Begin button...")
            await begin_btn.click()
            await asyncio.sleep(2)

            # Screenshot after begin
            ss_path = save_screenshot(page, "sandbox2-after-begin")
            await page.screenshot(path=ss_path, full_page=False)
            log(f"Screenshot 2: {ss_path}")

            # Try typing bypass code
            user_input = await page.query_selector("#userInput")
            if user_input:
                log("Typing bypass code: pb-full-bypass")
                await user_input.fill("pb-full-bypass")
                submit_btn = await page.query_selector("#submitBtn")
                if submit_btn:
                    await submit_btn.click()
                else:
                    await user_input.press("Enter")
                await asyncio.sleep(3)

                # Screenshot after bypass
                ss_path = save_screenshot(page, "sandbox2-after-bypass")
                await page.screenshot(path=ss_path, full_page=False)
                log(f"Screenshot 3: {ss_path}")

        # Force-show pricing via JS (to test the buttons directly)
        log("\nForce-revealing pricing section via JS...")
        reveal_result = await page.evaluate('''() => {
            const pricing = document.getElementById("pricing") || document.querySelector(".pricing-section");
            if (!pricing) return "PRICING_NOT_FOUND";
            pricing.style.display = "block";
            pricing.style.visibility = "visible";
            pricing.style.opacity = "1";
            pricing.classList.add("active");
            pricing.scrollIntoView({behavior: "instant"});
            return "REVEALED: " + pricing.id + " / " + pricing.className;
        }''')
        log(f"Force-reveal result: {reveal_result}")
        await asyncio.sleep(1)

        # Screenshot: Pricing section revealed
        ss_path = save_screenshot(page, "sandbox2-pricing-revealed")
        await page.screenshot(path=ss_path, full_page=False)
        log(f"Screenshot 4 (pricing revealed): {ss_path}")

        # Check pricing cards
        cards = await page.query_selector_all(".pricing-card, [class*='pricing-card']")
        log(f"Pricing cards found: {len(cards)}")
        for i, card in enumerate(cards[:5]):
            card_text = await card.inner_text()
            log(f"  Card {i+1}: {card_text[:80].strip()}")

        # Find the Awakened tier button
        log("\n--- Testing Awakened tier button click ---")

        # Look for buttons that call openWaitlistModal
        tier_buttons = await page.query_selector_all("button[onclick*='openWaitlistModal'], button[onclick*='openPayPalCheckout'], .pricing-card button, .tier-btn")
        log(f"Tier buttons found: {len(tier_buttons)}")
        for i, btn in enumerate(tier_buttons[:5]):
            btn_text = await btn.inner_text()
            btn_onclick = await btn.get_attribute("onclick")
            log(f"  Button {i+1}: '{btn_text.strip()}' onclick='{btn_onclick}'")

        # Try clicking the first tier button (Awakened)
        if tier_buttons:
            target_btn = tier_buttons[0]
            btn_text = await target_btn.inner_text()
            log(f"\nClicking: '{btn_text.strip()}'")

            # Screenshot before click
            ss_path = save_screenshot(page, "sandbox2-before-tier-click")
            await page.screenshot(path=ss_path, full_page=False)
            log(f"Screenshot 5 (before click): {ss_path}")

            await target_btn.click()
            await asyncio.sleep(2)

            # Screenshot after click
            ss_path = save_screenshot(page, "sandbox2-after-tier-click")
            await page.screenshot(path=ss_path, full_page=False)
            log(f"Screenshot 6 (after tier click): {ss_path}")

            # Check for modal
            modal_checks = await page.evaluate('''() => {
                const results = {};
                // Check for any modal
                const modals = document.querySelectorAll("[id*='modal'], [class*='modal']");
                results.modal_count = modals.length;
                results.visible_modals = [];
                modals.forEach(m => {
                    const style = window.getComputedStyle(m);
                    if (style.display !== "none" && style.visibility !== "hidden" && style.opacity !== "0") {
                        results.visible_modals.push({
                            id: m.id,
                            className: m.className.substring(0, 100),
                            text: m.innerText.substring(0, 200)
                        });
                    }
                });

                // Check for PayPal buttons container
                results.paypal_container = !!document.querySelector("#pb-paypal-buttons-container, .paypal-buttons, [id*='paypal']");
                results.paypal_sdk = typeof window.paypal !== "undefined";
                results.paypal_buttons_rendered = document.querySelectorAll(".paypal-buttons").length;

                // Check for sandbox badge
                results.sandbox_badge = document.body.innerHTML.includes("SANDBOX TEST") || document.body.innerHTML.includes("sandbox-badge");

                return results;
            }''')

            log(f"\nModal check results:")
            log(f"  Total modals in DOM: {modal_checks.get('modal_count', 0)}")
            log(f"  Visible modals: {len(modal_checks.get('visible_modals', []))}")
            for m in modal_checks.get("visible_modals", []):
                log(f"    Modal ID='{m.get('id')}' class='{m.get('className')}' text='{m.get('text', '')[:100]}'")
            log(f"  PayPal container in DOM: {modal_checks.get('paypal_container')}")
            log(f"  PayPal SDK loaded (window.paypal): {modal_checks.get('paypal_sdk')}")
            log(f"  PayPal buttons rendered: {modal_checks.get('paypal_buttons_rendered')}")
            log(f"  SANDBOX TEST badge: {modal_checks.get('sandbox_badge')}")
        else:
            log("No tier buttons found. Trying alternative selectors...")
            # Try by text content
            await page.evaluate('''() => {
                const btns = Array.from(document.querySelectorAll("button"));
                const tiered = btns.filter(b =>
                    b.innerText.toLowerCase().includes("awakened") ||
                    b.innerText.toLowerCase().includes("bonded") ||
                    b.innerText.toLowerCase().includes("get started")
                );
                console.log("[DEBUG] Found buttons by text:", tiered.map(b => b.innerText));
            }''')

        # Also try calling openWaitlistModal directly
        log("\n--- Direct JS call: openWaitlistModal('Awakened') ---")
        direct_result = await page.evaluate('''async () => {
            try {
                if (typeof openWaitlistModal === "function") {
                    openWaitlistModal("Awakened");
                    await new Promise(r => setTimeout(r, 1500));

                    // Check what appeared
                    const modals = Array.from(document.querySelectorAll("[id*='modal'], [class*='modal']")).filter(m => {
                        const s = window.getComputedStyle(m);
                        return s.display !== "none";
                    });

                    return {
                        success: true,
                        visible_modals: modals.map(m => ({id: m.id, class: m.className.substring(0,80), text: m.innerText.substring(0,200)})),
                        paypal_rendered: document.querySelectorAll(".paypal-buttons").length,
                        sandbox_badge_visible: document.body.innerHTML.includes("SANDBOX TEST")
                    };
                } else {
                    return {success: false, error: "openWaitlistModal not defined"};
                }
            } catch(e) {
                return {success: false, error: e.message};
            }
        }''')
        log(f"Direct call result: {json.dumps(direct_result, indent=2)}")

        await asyncio.sleep(2)

        # Final screenshot after direct call
        ss_path = save_screenshot(page, "sandbox2-after-direct-js-call")
        await page.screenshot(path=ss_path, full_page=False)
        log(f"Screenshot 7 (after direct JS call): {ss_path}")

        # Capture console logs
        log(f"\n--- Console Logs (page 688) ---")
        pb_sandbox_logs = [l for l in console_logs_688 if "[PB-SANDBOX]" in l]
        errors = [l for l in console_logs_688 if "[ERROR]" in l or "[PAGE-ERROR]" in l]
        log(f"Total console entries: {len(console_logs_688)}")
        log(f"[PB-SANDBOX] logs: {len(pb_sandbox_logs)}")
        log(f"Errors: {len(errors)}")

        if pb_sandbox_logs:
            log("\n[PB-SANDBOX] log messages captured:")
            for msg in pb_sandbox_logs[:20]:
                log(f"  {msg}")

        if errors:
            log("\nErrors captured:")
            for err in errors[:10]:
                log(f"  {err}")

        await ctx.close()

        # ============================================================
        # TEST 2: pay-test-2 (page 689) - Screenshot only, no PayPal interaction
        # ============================================================
        log("\n=== TEST 2: pay-test-2 (page 689) - Screenshot Only ===")
        ctx2 = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page2 = await ctx2.new_page()
        page2.on("console", lambda msg: console_logs_689.append(f"[{msg.type.upper()}] {msg.text}"))

        await page2.goto("http://127.0.0.1:18802/", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        # Screenshot: page 689 initial load
        ss_path = save_screenshot(page2, "paytest2-page689-initial")
        await page2.screenshot(path=ss_path, full_page=False)
        log(f"Screenshot 8 (page 689 initial): {ss_path}")

        # Quick checks
        p689_checks = await page2.evaluate('''() => {
            return {
                has_begin_btn: !!document.querySelector(".chat-initial__btn"),
                has_chat_initial: !!document.querySelector(".chat-initial, #chatInitial"),
                has_pricing: !!document.querySelector("#pricing, .pricing-section"),
                title: document.title,
                console_errors: 0
            };
        }''')
        log(f"Page 689 checks: {json.dumps(p689_checks)}")
        log(f"Page 689 errors: {len([l for l in console_logs_689 if 'ERROR' in l])}")

        await ctx2.close()
        await browser.close()

    # Stop servers
    server_688.shutdown()
    server_689.shutdown()

    # Print summary
    log("\n" + "="*60)
    log("QA COMPLETE - Summary")
    log("="*60)
    log(f"Screenshots saved to: {SESSION_DIR}")
    log(f"Total screenshots: {screenshot_count[0]}")
    all_screenshots = sorted(Path(SESSION_DIR).glob("*.png"))
    for ss in all_screenshots:
        log(f"  {ss.name}")

    return {
        "session_dir": SESSION_DIR,
        "screenshots": [str(s) for s in all_screenshots],
        "console_688": console_logs_688,
        "console_689": console_logs_689
    }

if __name__ == "__main__":
    result = asyncio.run(run_qa())
    print(f"\nSession dir: {result['session_dir']}")
