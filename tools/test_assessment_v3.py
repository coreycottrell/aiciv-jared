#!/usr/bin/env python3
"""
Assessment Results Screenshot Tool v3
Key insight: All questions are in DOM but hidden. Find VISIBLE options only.
Uses JavaScript to find only currently-visible options.
"""

import time
import sys
from playwright.sync_api import sync_playwright

ASSESSMENT_URL = "https://purebrain.ai/ai-partnership-assessment/"
SCREENSHOT_RESULTS = "/home/jared/projects/AI-CIV/aether/exports/screenshots/assessment_competitive_results.png"
SCREENSHOT_SHARE = "/home/jared/projects/AI-CIV/aether/exports/screenshots/assessment_competitive_share.png"
VIEWPORT = {"width": 1440, "height": 900}
SHOTS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots"


def log(msg):
    print(f"[assessment-v3] {msg}", flush=True)


def click_option_d_visible(page, question_num):
    """Click the 4th (D) visible option for the current question using JS."""
    result = page.evaluate("""
        () => {
            // Find all .option elements that are actually visible
            const allOptions = document.querySelectorAll('.option');
            const visibleOptions = Array.from(allOptions).filter(el => {
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                return rect.width > 0 && rect.height > 0 &&
                       style.display !== 'none' &&
                       style.visibility !== 'hidden' &&
                       style.opacity !== '0' &&
                       rect.top >= 0 && rect.top < window.innerHeight * 2;
            });

            console.log('Visible options count:', visibleOptions.length);

            if (visibleOptions.length === 0) return 'no-visible-options';

            // Pick D (index 3) or C (index 2) or last
            let targetIdx;
            if (visibleOptions.length >= 4) targetIdx = 3;
            else if (visibleOptions.length >= 3) targetIdx = 2;
            else targetIdx = visibleOptions.length - 1;

            const target = visibleOptions[targetIdx];
            target.click();

            // Return option text for verification
            return 'clicked:' + (target.innerText || '').substring(0, 50);
        }
    """)
    log(f"  Q{question_num}: JS click result: {result}")
    return result and 'clicked' in str(result)


def click_continue_button(page):
    """Click the visible Continue/Get My Results button."""
    result = page.evaluate("""
        () => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const visibleButtons = buttons.filter(btn => {
                const rect = btn.getBoundingClientRect();
                return rect.width > 0 && rect.height > 0;
            });

            // Look for Continue or Get My Results
            for (const btn of visibleButtons) {
                const text = btn.innerText.toLowerCase();
                if (text.includes('continue') || text.includes('get my results') ||
                    text.includes('next') || text.includes('results')) {
                    btn.click();
                    return 'clicked:' + btn.innerText.substring(0, 30);
                }
            }
            // Fallback: click first visible button that isn't Back
            for (const btn of visibleButtons) {
                const text = btn.innerText.toLowerCase();
                if (!text.includes('back')) {
                    btn.click();
                    return 'fallback:' + btn.innerText.substring(0, 30);
                }
            }
            return 'no-button-found';
        }
    """)
    log(f"  Button click result: {result}")
    return result


def wait_for_question_change(page, current_q_num, timeout=10):
    """Wait until the question number changes to next."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            text = page.evaluate("() => document.body.innerText.substring(0, 200)")
            if f"Question {current_q_num + 1} of" in text or "Question 6 of" in text or "SHARE" in text or "Score" in text:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def run_assessment():
    with sync_playwright() as pw:
        log("Launching Chromium...")
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport=VIEWPORT,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        console_msgs = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))

        log(f"Navigating to {ASSESSMENT_URL}...")
        try:
            page.goto(ASSESSMENT_URL, wait_until="domcontentloaded", timeout=45000)
        except Exception as e:
            log(f"Nav warning: {e}")

        log("Waiting 5s for initial render...")
        time.sleep(5)

        page.screenshot(path=f"{SHOTS_DIR}/assessment_v3_01_initial.png")
        log("Initial screenshot saved.")

        # === ANSWER Q1-Q5 ===
        for q in range(1, 6):
            log(f"\n=== Question {q} ===")

            # Click option D (or C if only 3 options)
            success = click_option_d_visible(page, q)
            time.sleep(0.8)

            page.screenshot(path=f"{SHOTS_DIR}/assessment_v3_q{q}_answered.png")

            if not success:
                log(f"  WARNING: Option click may have failed for Q{q}")
                # Debug: show what's visible
                vis = page.evaluate("""
                    () => {
                        const opts = document.querySelectorAll('.option');
                        return Array.from(opts).map(el => {
                            const rect = el.getBoundingClientRect();
                            return {text: el.innerText.substring(0,30), h: rect.height, w: rect.width, top: Math.round(rect.top)};
                        }).slice(0, 8);
                    }
                """)
                log(f"  All .option elements: {vis}")

            # Click Continue
            result = click_continue_button(page)
            time.sleep(0.5)

            # Wait for next question
            if q < 5:
                changed = wait_for_question_change(page, q)
                if changed:
                    log(f"  Question {q+1} loaded successfully")
                else:
                    log(f"  WARNING: Q{q+1} may not have loaded")
                    # Take debug screenshot
                    page.screenshot(path=f"{SHOTS_DIR}/assessment_v3_q{q}_debug.png")
            else:
                # After Q5, wait for Q6 (contact form)
                time.sleep(2)

        log("\n=== Q1-Q5 done. Handling Q6 contact form ===")
        time.sleep(2)

        # Debug: show Q6 content
        q6_text = page.evaluate("() => document.body.innerText.substring(0, 400)")
        log(f"Q6 content:\n{q6_text}")

        q6_inputs = page.evaluate("""
            () => Array.from(document.querySelectorAll('input')).filter(el => {
                const rect = el.getBoundingClientRect();
                return rect.width > 0 && rect.height > 0;
            }).map(el => ({
                id: el.id, type: el.type, placeholder: el.placeholder, name: el.name
            }))
        """)
        log(f"Q6 inputs: {q6_inputs}")

        page.screenshot(path=f"{SHOTS_DIR}/assessment_v3_q6_start.png")

        # Fill using IDs from debug (expected: id=name, id=email, id=company)
        # Fill name
        page.evaluate("""
            () => {
                const nameInput = document.getElementById('name') ||
                    document.querySelector('input[placeholder*="John"], input[placeholder*="name" i]');
                if (nameInput) {
                    nameInput.value = 'Test User';
                    nameInput.dispatchEvent(new Event('input', {bubbles:true}));
                    nameInput.dispatchEvent(new Event('change', {bubbles:true}));
                    nameInput.dispatchEvent(new KeyboardEvent('keyup', {bubbles:true}));
                }
            }
        """)
        time.sleep(0.3)

        # Use Playwright fill for email (handles React state better)
        try:
            page.fill('#name', 'Test User')
            log("  Name filled via #name selector")
        except Exception:
            log("  Name filled via JS only")

        try:
            page.fill('#email', 'test@example.com')
            log("  Email filled via #email selector")
        except Exception:
            page.evaluate("""
                () => {
                    const el = document.getElementById('email') ||
                        document.querySelector('input[type="email"]');
                    if (el) {
                        el.value = 'test@example.com';
                        el.dispatchEvent(new Event('input', {bubbles:true}));
                        el.dispatchEvent(new Event('change', {bubbles:true}));
                    }
                }
            """)
            log("  Email filled via JS")

        try:
            page.fill('#company', 'Test Corp')
            log("  Company filled via #company selector")
        except Exception:
            page.evaluate("""
                () => {
                    const el = document.getElementById('company') ||
                        document.querySelector('input[placeholder*="Acme" i], input[placeholder*="company" i]');
                    if (el) {
                        el.value = 'Test Corp';
                        el.dispatchEvent(new Event('input', {bubbles:true}));
                        el.dispatchEvent(new Event('change', {bubbles:true}));
                    }
                }
            """)
            log("  Company filled via JS")

        time.sleep(1)
        page.screenshot(path=f"{SHOTS_DIR}/assessment_v3_q6_filled.png")
        log("Q6 filled screenshot saved.")

        # Click Get My Results
        log("Clicking 'Get My Results'...")
        result = click_continue_button(page)
        log(f"Submit result: {result}")

        log("Waiting 8 seconds for results...")
        time.sleep(8)

        # Get results state
        results_text = page.evaluate("() => document.body.innerText.substring(0, 800)")
        log(f"Results page:\n{results_text}")

        # Take screenshots
        page.screenshot(path=SCREENSHOT_RESULTS)
        log(f"Results screenshot: {SCREENSHOT_RESULTS}")

        page.screenshot(path=f"{SHOTS_DIR}/assessment_v3_results_full.png", full_page=True)

        # Scroll to share section
        page.evaluate("window.scrollBy(0, 700)")
        time.sleep(2)
        page.screenshot(path=SCREENSHOT_SHARE)
        log(f"Share screenshot: {SCREENSHOT_SHARE}")

        page.screenshot(path=f"{SHOTS_DIR}/assessment_v3_share_full.png", full_page=True)

        browser.close()
        log("\n=== COMPLETE ===")
        return True


if __name__ == "__main__":
    run_assessment()
