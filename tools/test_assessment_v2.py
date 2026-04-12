#!/usr/bin/env python3
"""
Assessment Results Screenshot Tool v2
Properly handles the quiz step-by-step, waiting for DOM updates.
"""

import time
import sys
from playwright.sync_api import sync_playwright, expect

ASSESSMENT_URL = "https://purebrain.ai/ai-partnership-assessment/"
SCREENSHOT_RESULTS = "/home/jared/projects/AI-CIV/aether/exports/screenshots/assessment_competitive_results.png"
SCREENSHOT_SHARE = "/home/jared/projects/AI-CIV/aether/exports/screenshots/assessment_competitive_share.png"
VIEWPORT = {"width": 1440, "height": 900}
SHOTS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots"


def log(msg):
    print(f"[assessment-v2] {msg}", flush=True)


def wait_for_options(page, timeout=10000):
    """Wait for .option elements to be visible and return them."""
    try:
        page.wait_for_selector('.option', state='visible', timeout=timeout)
        options = page.locator('.option').all()
        return options
    except Exception:
        return []


def select_option_d_or_c(page, question_num):
    """Click option D (index 3) or C (index 2) for the current question."""
    options = wait_for_options(page)

    if not options:
        log(f"  Q{question_num}: No options found after waiting")
        # Debug: dump visible text
        try:
            text = page.evaluate("() => document.body.innerText.substring(0, 500)")
            log(f"  Page content: {text[:200]}")
        except Exception:
            pass
        return False

    log(f"  Q{question_num}: Found {len(options)} options")

    # Pick D (index 3) if exists, else C (index 2), else last option
    if len(options) >= 4:
        target = options[3]  # D
        log(f"  Q{question_num}: Clicking option D (index 3)")
    elif len(options) >= 3:
        target = options[2]  # C
        log(f"  Q{question_num}: Clicking option C (index 2)")
    else:
        target = options[-1]
        log(f"  Q{question_num}: Clicking last option (index {len(options)-1})")

    try:
        target.click()
        time.sleep(0.5)
        return True
    except Exception as e:
        log(f"  Q{question_num}: Click failed: {e}")
        # Try clicking via JavaScript
        try:
            page.evaluate("""
                () => {
                    const options = document.querySelectorAll('.option');
                    const idx = options.length >= 4 ? 3 : (options.length >= 3 ? 2 : options.length - 1);
                    if (options[idx]) options[idx].click();
                }
            """)
            log(f"  Q{question_num}: JS click fallback used")
            time.sleep(0.5)
            return True
        except Exception as e2:
            log(f"  Q{question_num}: JS click also failed: {e2}")
            return False


def click_continue(page):
    """Click the Continue button."""
    for sel in [
        'button:has-text("Continue")',
        'button:has-text("Get My Results")',
        'button:has-text("Next")',
        'button.btn-primary',
        '.btn.btn-primary',
    ]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=3000):
                btn.click()
                log(f"  Clicked button: {sel}")
                return True
        except Exception:
            continue

    # JS fallback
    try:
        result = page.evaluate("""
            () => {
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    const text = btn.innerText.toLowerCase();
                    if (text.includes('continue') || text.includes('next') || text.includes('result')) {
                        btn.click();
                        return btn.innerText;
                    }
                }
                return null;
            }
        """)
        if result:
            log(f"  JS clicked button: {result}")
            return True
    except Exception:
        pass

    log("  WARNING: No Continue/Next button found")
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

        console_errors = []
        page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)

        log(f"Navigating to {ASSESSMENT_URL}...")
        try:
            page.goto(ASSESSMENT_URL, wait_until="domcontentloaded", timeout=45000)
        except Exception as e:
            log(f"Navigation warning (continuing): {e}")

        log("Waiting 4s for initial render...")
        time.sleep(4)

        page.screenshot(path=f"{SHOTS_DIR}/assessment_01_initial.png")
        log("Initial screenshot saved.")

        # === ANSWER Q1-Q5 ===
        for q in range(1, 6):
            log(f"\n=== Question {q} ===")

            # Wait for options to appear
            select_option_d_or_c(page, q)
            time.sleep(0.5)

            page.screenshot(path=f"{SHOTS_DIR}/assessment_q{q}_selected.png")
            log(f"  Q{q} selected screenshot saved.")

            # Click Continue
            click_continue(page)

            # Wait for next question to load (options to change)
            time.sleep(2)

            # Verify question changed by checking question number in text
            try:
                text = page.evaluate("() => document.body.innerText.substring(0, 200)")
                log(f"  After Continue, page shows: {text[:150]}")
            except Exception:
                pass

        log("\n=== Q1-Q5 complete. Now handling Q6 contact form ===")
        time.sleep(2)
        page.screenshot(path=f"{SHOTS_DIR}/assessment_02_q6_start.png")

        # === Q6: Contact Form ===
        log("Looking for contact form fields...")

        # Check what's on the page now
        try:
            page_text = page.evaluate("() => document.body.innerText.substring(0, 500)")
            log(f"Q6 page content: {page_text[:300]}")
        except Exception:
            pass

        # Find all visible inputs
        try:
            inputs_info = page.evaluate("""
                () => {
                    const inputs = document.querySelectorAll('input:not([type="hidden"]), textarea');
                    return Array.from(inputs).filter(el => el.offsetParent !== null).map(el => ({
                        type: el.type,
                        name: el.name,
                        id: el.id,
                        placeholder: el.placeholder,
                        class: el.className.substring(0, 40)
                    }));
                }
            """)
            log(f"Visible inputs: {inputs_info}")
        except Exception as e:
            log(f"Input enumeration failed: {e}")

        # Fill name
        name_filled = False
        for sel in ['input[name="name"]', 'input[placeholder*="name" i]', 'input[placeholder*="Name"]',
                    'input[id*="name" i]', '.form-field input[type="text"]:first-of-type',
                    'input.name-field', '#user-name', '#userName']:
            try:
                elem = page.locator(sel).first
                if elem.is_visible(timeout=1500):
                    elem.clear()
                    elem.fill("Test User")
                    log(f"  Name filled via: {sel}")
                    name_filled = True
                    break
            except Exception:
                continue

        # Try JS fill if standard selectors failed
        if not name_filled:
            try:
                page.evaluate("""
                    () => {
                        const inputs = Array.from(document.querySelectorAll('input[type="text"], input:not([type])'));
                        const visible = inputs.filter(el => el.offsetParent !== null);
                        if (visible.length > 0) {
                            visible[0].value = 'Test User';
                            visible[0].dispatchEvent(new Event('input', {bubbles: true}));
                            visible[0].dispatchEvent(new Event('change', {bubbles: true}));
                        }
                    }
                """)
                log("  Name filled via JS on first visible text input")
                name_filled = True
            except Exception as e:
                log(f"  Name JS fill failed: {e}")

        # Fill email
        email_filled = False
        for sel in ['input[type="email"]', 'input[name="email"]', 'input[placeholder*="email" i]',
                    'input[id*="email" i]', '#user-email', '#userEmail']:
            try:
                elem = page.locator(sel).first
                if elem.is_visible(timeout=1500):
                    elem.clear()
                    elem.fill("test@example.com")
                    log(f"  Email filled via: {sel}")
                    email_filled = True
                    break
            except Exception:
                continue

        if not email_filled:
            try:
                page.evaluate("""
                    () => {
                        const inputs = Array.from(document.querySelectorAll('input'));
                        const emailInput = inputs.find(el =>
                            el.offsetParent !== null && (
                                el.type === 'email' ||
                                el.placeholder.toLowerCase().includes('email') ||
                                el.name.toLowerCase().includes('email')
                            )
                        );
                        if (emailInput) {
                            emailInput.value = 'test@example.com';
                            emailInput.dispatchEvent(new Event('input', {bubbles: true}));
                            emailInput.dispatchEvent(new Event('change', {bubbles: true}));
                        }
                    }
                """)
                log("  Email filled via JS")
                email_filled = True
            except Exception as e:
                log(f"  Email JS fill failed: {e}")

        # Fill company
        company_filled = False
        for sel in ['input[name="company"]', 'input[placeholder*="company" i]', 'input[id*="company" i]',
                    '#user-company', '#company', '.company-field input']:
            try:
                elem = page.locator(sel).first
                if elem.is_visible(timeout=1500):
                    elem.clear()
                    elem.fill("Test Corp")
                    log(f"  Company filled via: {sel}")
                    company_filled = True
                    break
            except Exception:
                continue

        if not company_filled:
            try:
                page.evaluate("""
                    () => {
                        const inputs = Array.from(document.querySelectorAll('input[type="text"], input:not([type])'));
                        const visible = inputs.filter(el => el.offsetParent !== null);
                        // Fill 3rd visible text input as company (after name and possibly others)
                        const idx = Math.min(2, visible.length - 1);
                        if (visible[idx]) {
                            visible[idx].value = 'Test Corp';
                            visible[idx].dispatchEvent(new Event('input', {bubbles: true}));
                            visible[idx].dispatchEvent(new Event('change', {bubbles: true}));
                        }
                    }
                """)
                log("  Company filled via JS on 3rd visible input")
                company_filled = True
            except Exception as e:
                log(f"  Company JS fill failed: {e}")

        log(f"Form fill status: name={name_filled}, email={email_filled}, company={company_filled}")
        time.sleep(1)
        page.screenshot(path=f"{SHOTS_DIR}/assessment_03_q6_filled.png")
        log("Q6 filled screenshot saved.")

        # Click Get My Results
        log("\nLooking for 'Get My Results' / submit button...")
        submitted = False
        for sel in [
            'button:has-text("Get My Results")',
            'button:has-text("Get Results")',
            'button:has-text("See My Results")',
            'button:has-text("Submit")',
            'button:has-text("Continue")',
            'input[type="submit"]',
            'button[type="submit"]',
            'button.btn-primary',
            '.submit-btn',
            '.btn-submit',
        ]:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    log(f"  Clicked: {sel}")
                    submitted = True
                    break
            except Exception:
                continue

        if not submitted:
            try:
                result = page.evaluate("""
                    () => {
                        const buttons = Array.from(document.querySelectorAll('button, input[type="submit"]'));
                        const btn = buttons.find(b => {
                            const text = (b.innerText || b.value || '').toLowerCase();
                            return text.includes('result') || text.includes('submit') ||
                                   text.includes('continue') || text.includes('get my');
                        });
                        if (btn) { btn.click(); return btn.innerText || btn.value; }
                        return null;
                    }
                """)
                if result:
                    log(f"  JS clicked: {result}")
                    submitted = True
                else:
                    log("  No submit button found via JS either")
            except Exception as e:
                log(f"  JS submit failed: {e}")

        log("Waiting 8 seconds for iframe submission and results display...")
        time.sleep(8)

        # === TAKE RESULTS SCREENSHOTS ===
        log("\nCapturing results...")

        # Get page state
        try:
            url = page.url
            title = page.title()
            page_text = page.evaluate("() => document.body.innerText.substring(0, 800)")
            log(f"URL: {url}")
            log(f"Title: {title}")
            log(f"Content preview:\n{page_text}")
        except Exception as e:
            log(f"Page state failed: {e}")

        # Viewport screenshot (primary results view)
        page.screenshot(path=SCREENSHOT_RESULTS)
        log(f"Results viewport screenshot: {SCREENSHOT_RESULTS}")

        # Full page screenshot
        page.screenshot(path=f"{SHOTS_DIR}/assessment_04_results_fullpage.png", full_page=True)
        log("Full page results screenshot saved.")

        # Scroll to share section
        log("Scrolling to find share/score card section...")
        page.evaluate("window.scrollBy(0, 600)")
        time.sleep(2)

        page.screenshot(path=SCREENSHOT_SHARE)
        log(f"Share section screenshot: {SCREENSHOT_SHARE}")

        # Scroll more to capture all
        page.evaluate("window.scrollBy(0, 400)")
        time.sleep(1)
        page.screenshot(path=f"{SHOTS_DIR}/assessment_05_lower_section.png")

        # Bottom of page
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        page.screenshot(path=f"{SHOTS_DIR}/assessment_06_bottom.png")

        # Log any console errors
        if console_errors:
            log("\nConsole errors:")
            for e in console_errors[-10:]:
                log(f"  {e}")

        browser.close()
        log("\n=== ALL DONE ===")
        log(f"Primary results: {SCREENSHOT_RESULTS}")
        log(f"Share section: {SCREENSHOT_SHARE}")
        return True


if __name__ == "__main__":
    success = run_assessment()
    sys.exit(0 if success else 1)
