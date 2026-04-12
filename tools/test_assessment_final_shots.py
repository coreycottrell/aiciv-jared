#!/usr/bin/env python3
"""
Take better-framed screenshots of the assessment results.
Re-runs the assessment to get fresh results, then captures at optimal scroll positions.
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
    print(f"[final-shots] {msg}", flush=True)


def click_option_d_visible(page):
    return page.evaluate("""
        () => {
            const allOptions = document.querySelectorAll('.option');
            const visibleOptions = Array.from(allOptions).filter(el => {
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                return rect.width > 0 && rect.height > 0 &&
                       style.display !== 'none' &&
                       style.visibility !== 'hidden' &&
                       rect.top >= 0 && rect.top < window.innerHeight * 3;
            });
            if (!visibleOptions.length) return 'no-options';
            const idx = visibleOptions.length >= 4 ? 3 : visibleOptions.length - 1;
            visibleOptions[idx].click();
            return 'clicked:' + (visibleOptions[idx].innerText || '').substring(0, 40);
        }
    """)


def click_button_text(page, text):
    return page.evaluate(f"""
        () => {{
            const buttons = Array.from(document.querySelectorAll('button'));
            const btn = buttons.find(b => b.innerText.toLowerCase().includes('{text.lower()}'));
            if (btn) {{ btn.click(); return btn.innerText; }}
            return null;
        }}
    """)


def run():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport=VIEWPORT,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        log(f"Loading {ASSESSMENT_URL}...")
        try:
            page.goto(ASSESSMENT_URL, wait_until="domcontentloaded", timeout=45000)
        except Exception:
            pass
        time.sleep(5)

        # Answer Q1-Q5
        for q in range(1, 6):
            log(f"Q{q}: clicking option D...")
            result = click_option_d_visible(page)
            log(f"  -> {result}")
            time.sleep(0.8)

            if q < 5:
                click_button_text(page, "continue")
                time.sleep(2.5)
            else:
                click_button_text(page, "continue")
                time.sleep(2)

        log("Q6: filling contact form...")
        time.sleep(1)

        # Fill with Playwright native (handles React state better)
        try:
            page.fill('#name', '')
            page.fill('#name', 'Test User')
            log("  Name filled")
        except Exception as e:
            log(f"  Name fill error: {e}")

        try:
            page.fill('#email', '')
            page.fill('#email', 'test@example.com')
            log("  Email filled")
        except Exception as e:
            log(f"  Email fill error: {e}")

        try:
            page.fill('#company', '')
            page.fill('#company', 'Test Corp')
            log("  Company filled")
        except Exception as e:
            log(f"  Company fill error: {e}")

        time.sleep(0.5)
        page.screenshot(path=f"{SHOTS_DIR}/assessment_final_q6.png")

        log("Clicking Get My Results...")
        click_button_text(page, "get my results")
        log("Waiting 10 seconds for results...")
        time.sleep(10)

        # Check score
        body_text = page.evaluate("() => document.body.innerText.substring(0, 500)")
        log(f"Results:\n{body_text}")

        # === SCREENSHOT 1: Full results view from top ===
        # Scroll to top first
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)

        # The results section should be visible. Take the full results view.
        page.screenshot(path=SCREENSHOT_RESULTS)
        log(f"Results screenshot taken: {SCREENSHOT_RESULTS}")

        # === SCREENSHOT 2: Share section ===
        # Find the share section position and scroll to it
        share_y = page.evaluate("""
            () => {
                // Find share section
                const shareSection = document.querySelector('.share-section, [class*="share"], .score-card');
                if (shareSection) {
                    return shareSection.getBoundingClientRect().top + window.scrollY - 50;
                }
                // Fallback: scroll to button area
                const dlBtn = Array.from(document.querySelectorAll('button')).find(b =>
                    b.innerText.toLowerCase().includes('download') ||
                    b.innerText.toLowerCase().includes('score card')
                );
                if (dlBtn) {
                    return dlBtn.getBoundingClientRect().top + window.scrollY - 100;
                }
                return window.scrollY + 600;
            }
        """)
        log(f"Share section Y position: {share_y}")

        page.evaluate(f"window.scrollTo(0, {share_y})")
        time.sleep(2)

        page.screenshot(path=SCREENSHOT_SHARE)
        log(f"Share screenshot taken: {SCREENSHOT_SHARE}")

        # Also take a full page shot for reference
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.5)
        page.screenshot(path=f"{SHOTS_DIR}/assessment_final_fullpage.png", full_page=True)
        log("Full page screenshot taken.")

        # Get button info for verification
        buttons = page.evaluate("""
            () => Array.from(document.querySelectorAll('button')).map(b => ({
                text: b.innerText.substring(0, 50),
                visible: b.getBoundingClientRect().width > 0
            }))
        """)
        log(f"All buttons on results page: {buttons}")

        browser.close()
        log("Done!")


if __name__ == "__main__":
    run()
