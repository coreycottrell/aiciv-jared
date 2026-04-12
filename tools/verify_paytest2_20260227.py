#!/usr/bin/env python3
"""
Pay-Test-2 Visual Verification Script
Date: 2026-02-27
Purpose: Verify brain video + chatbox after JSON corruption fix
URL: https://purebrain.ai/pay-test-2/
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/paytest-verify-20260227")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

PAGE_URL = "https://purebrain.ai/pay-test-2/"
PAGE_PASSWORD = "PureBrain.ai253443$"
RESULTS = {}

async def take_screenshot(page, name, description):
    path = SCREENSHOTS_DIR / f"{name}.png"
    await page.screenshot(path=str(path), full_page=False)
    print(f"[SCREENSHOT] {name}: {description} -> {path}")
    return str(path)

async def main():
    print(f"\n{'='*60}")
    print("PAY-TEST-2 VERIFICATION - 2026-02-27")
    print(f"{'='*60}\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--autoplay-policy=no-user-gesture-required",
            ]
        )

        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            java_script_enabled=True,
        )

        # Collect console logs
        console_logs = []
        console_errors = []

        page = await context.new_page()

        page.on("console", lambda msg: (
            console_errors.append(f"[{msg.type.upper()}] {msg.text}") if msg.type in ["error", "warning"]
            else console_logs.append(f"[{msg.type.upper()}] {msg.text}")
        ))

        page.on("pageerror", lambda err: console_errors.append(f"[PAGE_ERROR] {err}"))

        # Step 1: Navigate to pay-test-2
        print("[1] Navigating to pay-test-2...")
        try:
            response = await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
            RESULTS["http_status"] = response.status
            print(f"    HTTP Status: {response.status}")
        except Exception as e:
            print(f"    ERROR navigating: {e}")
            RESULTS["navigation_error"] = str(e)
            await browser.close()
            return

        # Screenshot 1: Before password entry
        await asyncio.sleep(2)
        await take_screenshot(page, "01-before-password", "Page before password entry")

        # Check if password form is present
        pw_field = await page.query_selector("input[id^='pwbox-']")
        RESULTS["password_form_found"] = pw_field is not None
        print(f"[2] Password form found: {RESULTS['password_form_found']}")

        if pw_field:
            print("    Entering password...")
            await pw_field.click()
            await pw_field.fill(PAGE_PASSWORD)
            await asyncio.sleep(0.5)

            # Submit the password form
            submit_btn = await page.query_selector("input[type='submit'][name='Submit']")
            if submit_btn:
                await submit_btn.click()
            else:
                await page.keyboard.press("Enter")

            print("    Waiting for page to load after password...")
            await asyncio.sleep(15)  # Full 15 second wait as requested

        else:
            # No password form - page might already be unlocked
            print("    No password form - checking if page is already unlocked...")
            await asyncio.sleep(5)

        # Screenshot 2: After password, page loading
        await take_screenshot(page, "02-after-password-15s", "15 seconds after password entry")

        # Check for WAF/reCAPTCHA challenge
        page_content = await page.content()
        waf_detected = (
            "recaptcha" in page_content.lower() or
            "verify you are human" in page_content.lower() or
            "cloudflare" in page_content.lower() and "challenge" in page_content.lower() or
            "ddos" in page_content.lower()
        )
        RESULTS["waf_detected"] = waf_detected
        if waf_detected:
            print("[WAF] reCAPTCHA / WAF challenge DETECTED - cannot proceed")
            await take_screenshot(page, "03-waf-challenge", "WAF challenge page")
            RESULTS["waf_details"] = page_content[:500]
            await browser.close()
            return

        # Check page title
        title = await page.title()
        RESULTS["page_title"] = title
        print(f"[3] Page title: {title}")

        # ---- BRAIN VIDEO CHECK ----
        print("[4] Checking brain/neural video...")

        # Look for video elements
        video_elements = await page.query_selector_all("video")
        RESULTS["video_elements_count"] = len(video_elements)
        print(f"    Video elements found: {len(video_elements)}")

        video_details = []
        for i, vid in enumerate(video_elements):
            src = await vid.get_attribute("src") or ""
            autoplay = await vid.get_attribute("autoplay")
            loop = await vid.get_attribute("loop")
            muted = await vid.get_attribute("muted")
            classes = await vid.get_attribute("class") or ""
            display = await page.evaluate("el => window.getComputedStyle(el).display", vid)
            visibility = await page.evaluate("el => window.getComputedStyle(el).visibility", vid)
            opacity = await page.evaluate("el => window.getComputedStyle(el).opacity", vid)
            width = await page.evaluate("el => el.offsetWidth", vid)
            height = await page.evaluate("el => el.offsetHeight", vid)
            paused = await page.evaluate("el => el.paused", vid)
            ready_state = await page.evaluate("el => el.readyState", vid)

            # Check source elements inside video
            sources = await vid.query_selector_all("source")
            source_srcs = []
            for s in sources:
                s_src = await s.get_attribute("src") or ""
                source_srcs.append(s_src)

            vid_info = {
                "index": i,
                "src": src,
                "sources": source_srcs,
                "autoplay": autoplay is not None,
                "loop": loop is not None,
                "muted": muted is not None,
                "classes": classes,
                "display": display,
                "visibility": visibility,
                "opacity": opacity,
                "offsetWidth": width,
                "offsetHeight": height,
                "paused": paused,
                "readyState": ready_state,
            }
            video_details.append(vid_info)
            print(f"    Video[{i}]: display={display} visibility={visibility} opacity={opacity} paused={paused} readyState={ready_state}")
            print(f"             src='{src}' sources={source_srcs}")
            print(f"             size={width}x{height} classes='{classes}'")

        RESULTS["video_details"] = video_details

        # Check for background video via CSS background
        bg_video_check = await page.evaluate("""
            () => {
                // Check for video used as background
                const allVideos = document.querySelectorAll('video');
                const results = [];
                allVideos.forEach((v, i) => {
                    const style = window.getComputedStyle(v);
                    results.push({
                        index: i,
                        position: style.position,
                        zIndex: style.zIndex,
                        width: v.offsetWidth,
                        height: v.offsetHeight,
                        networkState: v.networkState,
                        error: v.error ? v.error.message : null,
                        currentSrc: v.currentSrc,
                    });
                });
                return results;
            }
        """)
        RESULTS["video_bg_check"] = bg_video_check
        for item in bg_video_check:
            print(f"    Video[{item['index']}] bg-check: position={item.get('position')} z-index={item.get('zIndex')} currentSrc={item.get('currentSrc')} networkState={item.get('networkState')} error={item.get('error')}")

        # ---- CHATBOX CHECK ----
        print("[5] Checking chatbox section...")

        # Check for "Begin Your Awakening" heading
        begin_awakening_heading = await page.query_selector("h1, h2, h3, h4")
        headings = await page.evaluate("""
            () => {
                const headings = document.querySelectorAll('h1, h2, h3, h4');
                return Array.from(headings).map(h => ({
                    tag: h.tagName,
                    text: h.innerText.trim(),
                    visible: h.offsetWidth > 0 && h.offsetHeight > 0
                })).filter(h => h.text.length > 0);
            }
        """)
        RESULTS["headings"] = headings
        print(f"    Headings found: {len(headings)}")
        for h in headings:
            print(f"      {h['tag']}: '{h['text']}' (visible: {h['visible']})")

        # Check for chatbox elements
        chat_initial = await page.query_selector(".chat-initial")
        chat_initial_visible = False
        if chat_initial:
            chat_initial_visible = await page.evaluate("el => el.offsetWidth > 0 && el.offsetHeight > 0", chat_initial)
        RESULTS["chat_initial_found"] = chat_initial is not None
        RESULTS["chat_initial_visible"] = chat_initial_visible
        print(f"    .chat-initial found: {chat_initial is not None}, visible: {chat_initial_visible}")

        # Check for "Begin Awakening" button
        begin_btn = await page.query_selector(".chat-initial__btn")
        begin_btn_visible = False
        begin_btn_text = ""
        if begin_btn:
            begin_btn_visible = await page.evaluate("el => el.offsetWidth > 0 && el.offsetHeight > 0", begin_btn)
            begin_btn_text = await begin_btn.inner_text()
        RESULTS["begin_btn_found"] = begin_btn is not None
        RESULTS["begin_btn_visible"] = begin_btn_visible
        RESULTS["begin_btn_text"] = begin_btn_text
        print(f"    .chat-initial__btn found: {begin_btn is not None}, visible: {begin_btn_visible}, text: '{begin_btn_text}'")

        # Broader button scan
        all_buttons = await page.evaluate("""
            () => {
                const btns = document.querySelectorAll('button, a.btn, input[type="button"], input[type="submit"]');
                return Array.from(btns).map(b => ({
                    tag: b.tagName,
                    text: b.innerText ? b.innerText.trim() : b.value || '',
                    visible: b.offsetWidth > 0 && b.offsetHeight > 0,
                    classes: b.className
                })).filter(b => b.text.length > 0).slice(0, 20);
            }
        """)
        RESULTS["all_buttons"] = all_buttons
        print(f"    All visible buttons ({len(all_buttons)}):")
        for b in all_buttons:
            if b["visible"]:
                print(f"      {b['tag']}: '{b['text']}' (classes: {b['classes'][:60]})")

        # ---- ELEMENTOR DATA CHECK ----
        print("[6] Checking Elementor data presence...")
        elementor_check = await page.evaluate("""
            () => {
                const scripts = document.querySelectorAll('script');
                let found = false;
                let elementorDataSize = 0;
                scripts.forEach(s => {
                    if (s.textContent.includes('_elementor') || s.src.includes('elementor')) {
                        found = true;
                    }
                });
                // Check if Elementor frontend is initialized
                const eFrontend = typeof window.elementorFrontend !== 'undefined';
                return { elementorScriptsFound: found, elementorFrontendInit: eFrontend };
            }
        """)
        RESULTS["elementor_check"] = elementor_check
        print(f"    Elementor scripts found: {elementor_check.get('elementorScriptsFound')}")
        print(f"    elementorFrontend init: {elementor_check.get('elementorFrontendInit')}")

        # ---- PAGE BLANK CHECK ----
        print("[7] Checking if page is blank...")
        is_blank = await page.evaluate("""
            () => {
                const body = document.body;
                if (!body) return true;
                const text = body.innerText.trim();
                const children = body.children.length;
                return text.length < 50 && children < 3;
            }
        """)
        RESULTS["page_is_blank"] = is_blank
        print(f"    Page is blank: {is_blank}")

        # Get visible text content summary
        visible_text = await page.evaluate("""
            () => {
                const body = document.body;
                return body ? body.innerText.trim().substring(0, 500) : '(no body)';
            }
        """)
        RESULTS["visible_text_preview"] = visible_text
        print(f"    Visible text preview: '{visible_text[:200]}'")

        # ---- SCREENSHOT MULTIPLE POSITIONS ----
        print("[8] Taking screenshots at multiple scroll positions...")

        await take_screenshot(page, "03-viewport-top", "Top of page viewport")

        # Scroll to middle
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        await asyncio.sleep(1)
        await take_screenshot(page, "04-viewport-middle", "Middle of page")

        # Scroll to bottom
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1)
        await take_screenshot(page, "05-viewport-bottom", "Bottom of page")

        # Scroll back to top for final check
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(1)

        # Full page screenshot
        full_path = SCREENSHOTS_DIR / "06-fullpage.png"
        await page.screenshot(path=str(full_path), full_page=True)
        print(f"[SCREENSHOT] 06-fullpage: Full page capture -> {full_path}")

        # ---- CONSOLE LOG SUMMARY ----
        print("[9] Console summary...")
        RESULTS["console_errors"] = console_errors
        RESULTS["console_logs_count"] = len(console_logs)
        print(f"    Errors/warnings: {len(console_errors)}")
        for err in console_errors[:10]:
            print(f"      {err}")

        await browser.close()

    # ---- SAVE RESULTS ----
    results_path = SCREENSHOTS_DIR / "results.json"
    with open(results_path, "w") as f:
        json.dump(RESULTS, f, indent=2, default=str)
    print(f"\n[SAVED] Results JSON: {results_path}")

    # ---- PRINT FINAL REPORT ----
    print(f"\n{'='*60}")
    print("VERIFICATION REPORT SUMMARY")
    print(f"{'='*60}")
    print(f"WAF detected: {RESULTS.get('waf_detected', 'N/A')}")
    print(f"HTTP status: {RESULTS.get('http_status', 'N/A')}")
    print(f"Page blank: {RESULTS.get('page_is_blank', 'N/A')}")
    print(f"Video elements: {RESULTS.get('video_elements_count', 0)}")
    print(f"Chat initial section: found={RESULTS.get('chat_initial_found')} visible={RESULTS.get('chat_initial_visible')}")
    print(f"Begin button: found={RESULTS.get('begin_btn_found')} visible={RESULTS.get('begin_btn_visible')} text='{RESULTS.get('begin_btn_text')}'")
    print(f"Console errors: {len(RESULTS.get('console_errors', []))}")
    print(f"\nScreenshots: {SCREENSHOTS_DIR}/")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(main())
