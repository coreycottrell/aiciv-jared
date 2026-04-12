"""
pay-test-2 post-JSON-fix verification script
Date: 2026-02-27
Purpose: Verify brain video, chatbox, Begin Awakening button after JSON corruption fix
Page: https://purebrain.ai/pay-test-2/
Password: PureBrain.ai253443$
"""

import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/paytest2-json-fix-20260227")
PAGE_URL = "https://purebrain.ai/pay-test-2/"
PAGE_PASSWORD = "PureBrain.ai253443$"


async def run():
    results = {
        "url": PAGE_URL,
        "screenshots": [],
        "findings": {},
        "console_errors": [],
        "console_warnings": [],
        "waf_detected": False,
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900}
        )
        page = await context.new_page()

        # Capture console messages
        console_messages = []
        def handle_console(msg):
            entry = {"type": msg.type, "text": msg.text}
            console_messages.append(entry)
            if msg.type == "error":
                results["console_errors"].append(msg.text)
            elif msg.type == "warning":
                results["console_warnings"].append(msg.text)

        page.on("console", handle_console)

        # --- STEP 1: Navigate to page ---
        print(f"[1] Navigating to {PAGE_URL}")
        response = await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        print(f"    HTTP status: {response.status}")
        results["findings"]["http_status"] = response.status

        # Check for WAF / reCAPTCHA immediately
        page_text_early = await page.inner_text("body")
        if "verify you are human" in page_text_early.lower() or "recaptcha" in page_text_early.lower() or response.status == 429:
            print("[!] WAF CHALLENGE DETECTED - Cannot proceed")
            results["waf_detected"] = True
            shot = SCREENSHOT_DIR / "000-waf-challenge.png"
            await page.screenshot(path=str(shot), full_page=False)
            results["screenshots"].append({"file": str(shot), "label": "WAF challenge"})
            await browser.close()
            return results

        # --- STEP 2: Handle password ---
        print("[2] Checking for password field...")
        await asyncio.sleep(2)

        # Take screenshot before password entry
        shot1 = SCREENSHOT_DIR / "001-before-password.png"
        await page.screenshot(path=str(shot1), full_page=False)
        results["screenshots"].append({"file": str(shot1), "label": "Before password entry"})
        print(f"    Screenshot: {shot1}")

        password_field = await page.query_selector("input[id^='pwbox-']")
        if password_field:
            print("    Password field found - entering password...")
            await password_field.fill(PAGE_PASSWORD)
            await asyncio.sleep(0.5)
            # Submit password form
            submit_btn = await page.query_selector("input[type='submit']")
            if submit_btn:
                await submit_btn.click()
            else:
                await page.evaluate("document.querySelector('form.post-password-form').submit()")
            print("    Password submitted, waiting for page load...")
            await page.wait_for_load_state("networkidle", timeout=20000)
            await asyncio.sleep(15)  # Extra wait per Jared's instructions (15 seconds)
        else:
            print("    No password field found - page may already be unlocked or blank")
            await asyncio.sleep(15)

        # --- STEP 3: Screenshot at top of page ---
        print("[3] Taking top-of-page screenshot...")
        shot2 = SCREENSHOT_DIR / "002-page-top-after-load.png"
        await page.screenshot(path=str(shot2), full_page=False)
        results["screenshots"].append({"file": str(shot2), "label": "Page top after load (viewport)"})
        print(f"    Screenshot: {shot2}")

        # --- STEP 4: Inspect page content ---
        print("[4] Inspecting page content...")

        page_title = await page.title()
        results["findings"]["page_title"] = page_title
        print(f"    Page title: {page_title}")

        # Check if page is blank
        body_text = await page.inner_text("body")
        results["findings"]["body_text_length"] = len(body_text)
        results["findings"]["appears_blank"] = len(body_text.strip()) < 50
        print(f"    Body text length: {len(body_text)} chars")

        # Check for video element (brain/neural video)
        video_elements = await page.query_selector_all("video")
        results["findings"]["video_count"] = len(video_elements)
        print(f"    Video elements found: {len(video_elements)}")

        video_details = []
        for i, vid in enumerate(video_elements):
            src = await vid.get_attribute("src") or ""
            autoplay = await vid.get_attribute("autoplay")
            loop = await vid.get_attribute("loop")
            muted = await vid.get_attribute("muted")
            is_visible = await vid.is_visible()
            bbox = await vid.bounding_box()
            video_details.append({
                "index": i,
                "src": src[:100] if src else "(no src attr, likely uses <source>)",
                "autoplay": autoplay is not None,
                "loop": loop is not None,
                "muted": muted is not None,
                "is_visible": is_visible,
                "bounding_box": bbox
            })
            print(f"    Video[{i}]: visible={is_visible}, autoplay={autoplay is not None}, src={src[:80] if src else 'see <source>...'}")

        results["findings"]["video_details"] = video_details

        # Check for source elements inside video
        source_elements = await page.query_selector_all("video source")
        source_srcs = []
        for src_el in source_elements:
            src_val = await src_el.get_attribute("src") or ""
            source_srcs.append(src_val)
        results["findings"]["video_source_srcs"] = source_srcs
        if source_srcs:
            print(f"    Video <source> srcs: {source_srcs}")

        # Check for chatbox / Begin Your Awakening heading
        awakening_heading = await page.query_selector_all("h1, h2, h3, h4")
        heading_texts = []
        for h in awakening_heading:
            txt = await h.inner_text()
            heading_texts.append(txt.strip())
        results["findings"]["headings"] = heading_texts
        print(f"    Headings found: {heading_texts[:5]}")

        # Check for "Begin Your Awakening" specifically
        begin_awakening_heading = await page.query_selector("*:text('Begin Your Awakening')")
        results["findings"]["begin_awakening_heading_visible"] = begin_awakening_heading is not None
        print(f"    'Begin Your Awakening' heading: {'FOUND' if begin_awakening_heading else 'NOT FOUND'}")

        # Check for Begin Awakening button
        begin_btn = await page.query_selector(".chat-initial__btn")
        if not begin_btn:
            begin_btn = await page.query_selector("button:has-text('Begin Awakening')")
        if not begin_btn:
            begin_btn = await page.query_selector("*:text('Begin Awakening')")
        results["findings"]["begin_awakening_button_found"] = begin_btn is not None
        if begin_btn:
            btn_visible = await begin_btn.is_visible()
            btn_text = await begin_btn.inner_text()
            results["findings"]["begin_awakening_button_visible"] = btn_visible
            results["findings"]["begin_awakening_button_text"] = btn_text
            print(f"    Begin Awakening button: FOUND, visible={btn_visible}, text='{btn_text}'")
        else:
            print("    Begin Awakening button: NOT FOUND")

        # Check for chatbox container
        chatbox = await page.query_selector(".chat-initial, #chatMessages, .chat-container, [class*='chat']")
        results["findings"]["chatbox_found"] = chatbox is not None
        if chatbox:
            chatbox_visible = await chatbox.is_visible()
            chatbox_class = await chatbox.get_attribute("class") or ""
            results["findings"]["chatbox_visible"] = chatbox_visible
            results["findings"]["chatbox_class"] = chatbox_class
            print(f"    Chatbox: FOUND ({chatbox_class}), visible={chatbox_visible}")
        else:
            print("    Chatbox: NOT FOUND")

        # Check for Elementor data loading correctly
        elementor_active = await page.evaluate("""
            () => {
                return {
                    has_elementor: typeof window.elementorFrontend !== 'undefined',
                    elementor_initialized: typeof window.elementorFrontend !== 'undefined' && window.elementorFrontend.isEditMode !== undefined,
                }
            }
        """)
        results["findings"]["elementor"] = elementor_active
        print(f"    Elementor: {elementor_active}")

        # Check for video playing state via JS
        video_play_state = await page.evaluate("""
            () => {
                const videos = document.querySelectorAll('video');
                return Array.from(videos).map((v, i) => ({
                    index: i,
                    src: v.currentSrc || v.src || 'no-src',
                    paused: v.paused,
                    readyState: v.readyState,
                    networkState: v.networkState,
                    error: v.error ? v.error.code : null,
                    duration: v.duration,
                    width: v.videoWidth,
                    height: v.videoHeight,
                    display: window.getComputedStyle(v).display,
                    visibility: window.getComputedStyle(v).visibility,
                    opacity: window.getComputedStyle(v).opacity,
                    zIndex: window.getComputedStyle(v).zIndex,
                    position: window.getComputedStyle(v).position
                }));
            }
        """)
        results["findings"]["video_js_state"] = video_play_state
        for vs in video_play_state:
            print(f"    Video JS[{vs['index']}]: src={vs['src'][:80]}, paused={vs['paused']}, readyState={vs['readyState']}, error={vs['error']}, display={vs['display']}, zIndex={vs['zIndex']}")

        # --- STEP 5: Full page screenshot ---
        print("[5] Taking full page screenshot...")
        shot3 = SCREENSHOT_DIR / "003-full-page.png"
        await page.screenshot(path=str(shot3), full_page=True)
        results["screenshots"].append({"file": str(shot3), "label": "Full page scroll"})
        print(f"    Screenshot: {shot3}")

        # --- STEP 6: Scroll down to see chatbox area ---
        print("[6] Scrolling to chatbox area...")
        await page.evaluate("window.scrollTo(0, 400)")
        await asyncio.sleep(2)
        shot4 = SCREENSHOT_DIR / "004-scrolled-chatbox-area.png"
        await page.screenshot(path=str(shot4), full_page=False)
        results["screenshots"].append({"file": str(shot4), "label": "Scrolled to chatbox area"})
        print(f"    Screenshot: {shot4}")

        # --- STEP 7: Scroll further down ---
        print("[7] Scrolling further down...")
        await page.evaluate("window.scrollTo(0, 900)")
        await asyncio.sleep(2)
        shot5 = SCREENSHOT_DIR / "005-scrolled-lower.png"
        await page.screenshot(path=str(shot5), full_page=False)
        results["screenshots"].append({"file": str(shot5), "label": "Lower scroll position"})
        print(f"    Screenshot: {shot5}")

        # --- STEP 8: Console summary ---
        results["console_messages_total"] = len(console_messages)
        results["findings"]["all_console_errors"] = results["console_errors"]
        print(f"\n[8] Console: {len(results['console_errors'])} errors, {len(results['console_warnings'])} warnings, {len(console_messages)} total")
        for err in results["console_errors"]:
            print(f"    ERROR: {err[:200]}")

        await browser.close()

    # Save raw results
    results_file = SCREENSHOT_DIR / "raw_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[DONE] Results saved to {results_file}")

    return results


if __name__ == "__main__":
    results = asyncio.run(run())

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    if results.get("waf_detected"):
        print("STATUS: WAF CHALLENGE - Could not access page")
    else:
        f = results["findings"]
        print(f"HTTP Status: {f.get('http_status', '?')}")
        print(f"Page blank: {f.get('appears_blank', '?')}")
        print(f"Video elements: {f.get('video_count', 0)}")
        print(f"Brain video playing: {not f['video_js_state'][0]['paused'] if f.get('video_js_state') else 'N/A'}")
        print(f"'Begin Your Awakening' heading: {f.get('begin_awakening_heading_visible', False)}")
        print(f"Begin Awakening button: {f.get('begin_awakening_button_found', False)}")
        print(f"Chatbox found: {f.get('chatbox_found', False)}")
        print(f"Console errors: {len(results.get('console_errors', []))}")
        for err in results.get("console_errors", []):
            print(f"  - {err[:150]}")
