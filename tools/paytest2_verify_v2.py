"""
pay-test-2 post-JSON-fix verification - v2
Date: 2026-02-27
Fixes: Use type() instead of fill() + click submit button by element, not form.submit()
Password has special chars: PureBrain.ai253443$
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/paytest2-json-fix-20260227")
PAGE_URL = "https://purebrain.ai/pay-test-2/"
PAGE_PASSWORD = "PureBrain.ai253443$"


async def run():
    results = {"screenshots": [], "findings": {}, "console_errors": [], "waf_detected": False}

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

        console_messages = []
        def handle_console(msg):
            console_messages.append({"type": msg.type, "text": msg.text})
            if msg.type == "error":
                results["console_errors"].append(msg.text)

        page.on("console", handle_console)

        # Navigate
        print(f"[1] Navigating to {PAGE_URL}")
        resp = await page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=30000)
        print(f"    HTTP: {resp.status}")
        results["findings"]["http_status"] = resp.status

        await asyncio.sleep(2)

        # Check for WAF
        body_html = await page.content()
        if "verify you are human" in body_html.lower() or resp.status == 429:
            print("[!] WAF DETECTED")
            results["waf_detected"] = True
            await page.screenshot(path=str(SCREENSHOT_DIR / "000-waf.png"))
            await browser.close()
            return results

        # --- PASSWORD ENTRY ---
        print("[2] Entering password...")
        pw_field = await page.query_selector("input[id^='pwbox-']")
        if pw_field:
            # Use click then type, not fill - handles special chars better
            await pw_field.click()
            await asyncio.sleep(0.3)
            await pw_field.type(PAGE_PASSWORD, delay=50)
            await asyncio.sleep(0.5)

            # Verify what was typed
            typed_val = await pw_field.input_value()
            print(f"    Typed value length: {len(typed_val)} (expected {len(PAGE_PASSWORD)})")

            # Click the submit button explicitly
            submit = await page.query_selector("input[type='submit']")
            if submit:
                print("    Clicking submit button...")
                await submit.click()
            else:
                print("    No submit button, pressing Enter...")
                await pw_field.press("Enter")

            print("    Waiting for page to load after password...")
            try:
                await page.wait_for_load_state("networkidle", timeout=25000)
            except Exception:
                print("    networkidle timeout, continuing...")
            await asyncio.sleep(5)
        else:
            print("    No password field - page may already be unlocked")

        # Screenshot right after unlock attempt
        shot_unlock = SCREENSHOT_DIR / "010-after-unlock.png"
        await page.screenshot(path=str(shot_unlock), full_page=False)
        results["screenshots"].append({"file": str(shot_unlock), "label": "After password unlock"})
        print(f"    Screenshot: {shot_unlock}")

        # Check if still on password page
        pw_check = await page.query_selector("input[id^='pwbox-']")
        invalid_msg = await page.query_selector(".post-password-form")
        if pw_check or invalid_msg:
            page_text = await page.inner_text("body")
            print(f"    STILL ON PASSWORD PAGE. Body: {page_text[:200]}")

            # Try alternate: use the WP password cookie approach
            print("    Trying cookie-based unlock...")
            # Get the post ID from the form action
            form_action = await page.evaluate("""
                () => {
                    const form = document.querySelector('form.post-password-form');
                    return form ? form.action : null;
                }
            """)
            print(f"    Form action: {form_action}")
            results["findings"]["password_rejected"] = True
            results["findings"]["form_action"] = form_action

            # Clear and retype
            if pw_check:
                await pw_check.triple_click()
                await pw_check.fill("")
                await asyncio.sleep(0.2)
                await pw_check.type(PAGE_PASSWORD, delay=30)
                typed_val2 = await pw_check.input_value()
                print(f"    Retry typed value length: {len(typed_val2)}")
                print(f"    Typed value: '{typed_val2}'")

                # Submit via Enter key
                await pw_check.press("Enter")
                try:
                    await page.wait_for_load_state("networkidle", timeout=20000)
                except Exception:
                    pass
                await asyncio.sleep(5)

                shot_retry = SCREENSHOT_DIR / "011-after-retry-unlock.png"
                await page.screenshot(path=str(shot_retry), full_page=False)
                results["screenshots"].append({"file": str(shot_retry), "label": "After retry unlock"})
                print(f"    Retry screenshot: {shot_retry}")

        else:
            print("    Password accepted - page unlocked!")
            results["findings"]["password_rejected"] = False

        # --- PAGE INSPECTION ---
        print("[3] Inspecting unlocked page...")
        await asyncio.sleep(10)  # Extra wait for JS to initialize

        shot_top = SCREENSHOT_DIR / "012-page-top.png"
        await page.screenshot(path=str(shot_top), full_page=False)
        results["screenshots"].append({"file": str(shot_top), "label": "Page top viewport"})
        print(f"    Screenshot: {shot_top}")

        body_text = await page.inner_text("body")
        results["findings"]["body_text_length"] = len(body_text)
        results["findings"]["body_text_preview"] = body_text[:500]
        print(f"    Body text ({len(body_text)} chars): {body_text[:300]}")

        # Video check
        videos = await page.query_selector_all("video")
        results["findings"]["video_count"] = len(videos)
        print(f"    Videos: {len(videos)}")

        video_states = await page.evaluate("""
            () => Array.from(document.querySelectorAll('video')).map((v, i) => ({
                index: i,
                src: v.currentSrc || v.src || '',
                paused: v.paused,
                readyState: v.readyState,
                error: v.error ? v.error.code : null,
                display: window.getComputedStyle(v).display,
                visibility: window.getComputedStyle(v).visibility,
                opacity: window.getComputedStyle(v).opacity,
                zIndex: window.getComputedStyle(v).zIndex,
                width: v.getBoundingClientRect().width,
                height: v.getBoundingClientRect().height,
            }))
        """)
        results["findings"]["video_states"] = video_states
        for vs in video_states:
            print(f"    Video[{vs['index']}]: src={vs['src'][:80]}, paused={vs['paused']}, err={vs['error']}, display={vs['display']}, z={vs['zIndex']}, size={vs['width']}x{vs['height']}")

        # Chatbox check
        chatbox_info = await page.evaluate("""
            () => {
                const selectors = [
                    '.chat-initial', '#chatMessages', '.chat-container',
                    '.chat-section', '[class*="chat"]', '#chat',
                    '.elementor-widget-html', '.elementor-section'
                ];
                const found = [];
                selectors.forEach(sel => {
                    const els = document.querySelectorAll(sel);
                    els.forEach(el => {
                        found.push({
                            selector: sel,
                            id: el.id,
                            className: el.className.substring(0, 60),
                            visible: el.offsetParent !== null,
                            display: window.getComputedStyle(el).display,
                            textContent: el.textContent.trim().substring(0, 100)
                        });
                    });
                });
                return found;
            }
        """)
        results["findings"]["chatbox_elements"] = chatbox_info
        for el in chatbox_info[:5]:
            print(f"    Element [{el['selector']}]: id={el['id']}, visible={el['visible']}, text={el['textContent'][:60]}")

        # Headings
        headings = await page.evaluate("""
            () => Array.from(document.querySelectorAll('h1,h2,h3,h4,h5')).map(h => ({
                tag: h.tagName,
                text: h.textContent.trim().substring(0, 80)
            }))
        """)
        results["findings"]["headings"] = headings
        print(f"    Headings: {[h['text'] for h in headings[:8]]}")

        # Elementor check
        elementor_check = await page.evaluate("""
            () => ({
                has_elementor: typeof window.elementorFrontend !== 'undefined',
                elementor_data_attr: document.body.getAttribute('data-elementor-device-mode'),
                elementor_sections: document.querySelectorAll('.elementor-section').length,
                elementor_widgets: document.querySelectorAll('.elementor-widget').length,
                all_classes_sample: Array.from(document.body.classList).join(' ')
            })
        """)
        results["findings"]["elementor"] = elementor_check
        print(f"    Elementor check: {elementor_check}")

        # Full page screenshot
        shot_full = SCREENSHOT_DIR / "013-full-page.png"
        await page.screenshot(path=str(shot_full), full_page=True)
        results["screenshots"].append({"file": str(shot_full), "label": "Full page"})
        print(f"    Full page screenshot: {shot_full}")

        # Console summary
        results["console_total"] = len(console_messages)
        print(f"\n[4] Console: {len(results['console_errors'])} errors, {len(console_messages)} total")
        for err in results["console_errors"]:
            print(f"    ERROR: {err[:180]}")

        await browser.close()

    # Save results
    results_file = SCREENSHOT_DIR / "raw_results_v2.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[DONE] Results: {results_file}")
    return results


if __name__ == "__main__":
    results = asyncio.run(run())
    print("\n=== FINAL SUMMARY ===")
    f = results["findings"]
    print(f"WAF: {results['waf_detected']}")
    print(f"Password rejected: {f.get('password_rejected', 'unknown')}")
    print(f"Body text length: {f.get('body_text_length', 0)}")
    print(f"Video count: {f.get('video_count', 0)}")
    print(f"Elementor sections: {f.get('elementor', {}).get('elementor_sections', 0)}")
    print(f"Console errors: {len(results.get('console_errors', []))}")
