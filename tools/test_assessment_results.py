#!/usr/bin/env python3
"""
Assessment Results Screenshot Tool
Takes screenshots of the AI Partnership Assessment results page.
Completes the assessment with high-scoring answers (C/D options).
"""

import time
import sys
from playwright.sync_api import sync_playwright

ASSESSMENT_URL = "https://purebrain.ai/ai-partnership-assessment/"
SCREENSHOT_RESULTS = "/home/jared/projects/AI-CIV/aether/exports/screenshots/assessment_competitive_results.png"
SCREENSHOT_SHARE = "/home/jared/projects/AI-CIV/aether/exports/screenshots/assessment_competitive_share.png"
VIEWPORT = {"width": 1440, "height": 900}


def log(msg):
    print(f"[assessment-tester] {msg}", flush=True)


def click_option(page, question_num):
    """Try multiple strategies to click option C or D for a question."""
    answered = False

    # Strategy 1: Look for option text with letter prefix
    for option_letter in ["D", "C"]:
        for sel in [
            f'xpath=//label[contains(text(), "{option_letter}.")]',
            f'xpath=//div[contains(text(), "{option_letter}.")][contains(@class, "option")]',
            f'xpath=//*[@class and contains(@class, "option") and contains(., "{option_letter}.")]',
        ]:
            try:
                elems = page.locator(sel).all()
                for elem in elems:
                    if elem.is_visible(timeout=500):
                        elem.click()
                        log(f"  Q{question_num}: Clicked option {option_letter} via XPath")
                        return True
            except Exception:
                continue

    # Strategy 2: Radio buttons - pick 3rd or 4th (index 2 or 3)
    try:
        radios = page.locator('input[type="radio"]:visible').all()
        if radios:
            target_idx = min(3, len(radios) - 1)
            radios[target_idx].click(force=True)
            log(f"  Q{question_num}: Clicked radio option {target_idx}")
            return True
    except Exception:
        pass

    # Strategy 3: Any clickable option-like divs/buttons
    for sel in [
        '.answer-option', '.option', '.quiz-option', '.choice',
        '[class*="answer"]', '[class*="option"]', '[class*="choice"]'
    ]:
        try:
            elems = page.locator(sel).all()
            if len(elems) >= 4:
                elems[3].click()
                log(f"  Q{question_num}: Clicked 4th element matching {sel}")
                return True
            elif len(elems) >= 3:
                elems[2].click()
                log(f"  Q{question_num}: Clicked 3rd element matching {sel}")
                return True
        except Exception:
            continue

    # Strategy 4: JavaScript - find option C or D text and click parent
    try:
        result = page.evaluate("""
            () => {
                // Find all text nodes containing "C." or "D."
                const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                let node;
                while (node = walker.nextNode()) {
                    const text = node.textContent.trim();
                    if (text.startsWith('D.') || text.startsWith('C.')) {
                        const parent = node.parentElement;
                        if (parent) {
                            // Walk up to find clickable ancestor
                            let el = parent;
                            for (let i = 0; i < 5; i++) {
                                if (el.tagName === 'LABEL' || el.tagName === 'BUTTON' ||
                                    el.style.cursor === 'pointer' ||
                                    window.getComputedStyle(el).cursor === 'pointer') {
                                    el.click();
                                    return 'clicked:' + text.substring(0, 20);
                                }
                                el = el.parentElement;
                                if (!el) break;
                            }
                            parent.click();
                            return 'parent-clicked:' + text.substring(0, 20);
                        }
                    }
                }
                return 'not-found';
            }
        """)
        if result and 'clicked' in result:
            log(f"  Q{question_num}: JS found and clicked option: {result}")
            return True
    except Exception as e:
        log(f"  Q{question_num}: JS strategy failed: {e}")

    log(f"  Q{question_num}: WARNING - could not click option")
    return False


def run_assessment():
    with sync_playwright() as pw:
        log("Launching Chromium browser (headless)...")
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport=VIEWPORT,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # Capture console messages for debugging
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        log(f"Navigating to {ASSESSMENT_URL}...")
        try:
            page.goto(ASSESSMENT_URL, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            log(f"Page load warning (continuing): {e}")

        log("Waiting 5 seconds for page to fully render...")
        time.sleep(5)

        log("Taking initial screenshot...")
        page.screenshot(path="/home/jared/projects/AI-CIV/aether/exports/screenshots/assessment_01_initial.png")
        log("Initial screenshot saved.")

        # Get page HTML to understand structure
        log("Analyzing page structure...")
        try:
            page_info = page.evaluate("""
                () => {
                    const inputs = document.querySelectorAll('input, button, label, [class*="option"], [class*="answer"]');
                    const info = [];
                    inputs.forEach(el => {
                        if (el.offsetParent !== null) {  // only visible
                            info.push({
                                tag: el.tagName,
                                type: el.type || '',
                                class: el.className.substring(0, 50),
                                text: (el.innerText || el.value || '').substring(0, 50),
                                id: el.id.substring(0, 30)
                            });
                        }
                    });
                    return info.slice(0, 30);
                }
            """)
            log("Visible interactive elements found:")
            for el in page_info:
                log(f"  {el}")
        except Exception as e:
            log(f"Structure analysis failed: {e}")

        # Answer Q1-Q5
        for question_num in range(1, 6):
            log(f"\n--- Answering Q{question_num} ---")
            time.sleep(1)

            click_option(page, question_num)
            time.sleep(0.5)

            # Try to click Next/Continue
            next_clicked = False
            for next_sel in [
                'button:has-text("Next")',
                'button:has-text("Continue")',
                'button:has-text("Next Question")',
                '.next-btn',
                '.btn-next',
                '[class*="next"]:visible',
            ]:
                try:
                    btn = page.locator(next_sel).first
                    if btn.is_visible(timeout=1000):
                        btn.click()
                        log(f"  Clicked Next with {next_sel}")
                        next_clicked = True
                        time.sleep(1.5)
                        break
                except Exception:
                    continue

            if not next_clicked:
                log(f"  No Next button found - may auto-advance or already on next Q")
                time.sleep(1)

            # Take screenshot after each question
            page.screenshot(
                path=f"/home/jared/projects/AI-CIV/aether/exports/screenshots/assessment_q{question_num}_answered.png"
            )

        log("\n=== Completing Q5. Now handling Q6 contact form ===")
        time.sleep(2)
        page.screenshot(path="/home/jared/projects/AI-CIV/aether/exports/screenshots/assessment_02_before_q6.png")

        # Q6: Contact form
        log("Filling Q6 contact form...")

        # Name field
        name_filled = False
        for name_sel in [
            'input[name="name"]',
            'input[name="Name"]',
            'input[placeholder*="name" i]',
            'input[placeholder*="Name"]',
            'input[id*="name" i]',
            '#name',
            'input[type="text"]:first-of-type',
        ]:
            try:
                elem = page.locator(name_sel).first
                if elem.is_visible(timeout=2000):
                    elem.fill("Test User")
                    log(f"  Name filled with: {name_sel}")
                    name_filled = True
                    break
            except Exception:
                continue

        # Email field
        email_filled = False
        for email_sel in [
            'input[type="email"]',
            'input[name="email"]',
            'input[name="Email"]',
            'input[placeholder*="email" i]',
            'input[id*="email" i]',
            '#email',
        ]:
            try:
                elem = page.locator(email_sel).first
                if elem.is_visible(timeout=2000):
                    elem.fill("test@example.com")
                    log(f"  Email filled with: {email_sel}")
                    email_filled = True
                    break
            except Exception:
                continue

        # Company field
        company_filled = False
        for company_sel in [
            'input[name="company"]',
            'input[name="Company"]',
            'input[placeholder*="company" i]',
            'input[id*="company" i]',
            '#company',
        ]:
            try:
                elem = page.locator(company_sel).first
                if elem.is_visible(timeout=2000):
                    elem.fill("Test Corp")
                    log(f"  Company filled with: {company_sel}")
                    company_filled = True
                    break
            except Exception:
                continue

        log(f"  Form fill status: name={name_filled}, email={email_filled}, company={company_filled}")

        time.sleep(1)
        page.screenshot(path="/home/jared/projects/AI-CIV/aether/exports/screenshots/assessment_03_q6_filled.png")
        log("Q6 filled screenshot saved.")

        # Click Get My Results
        log("\nLooking for 'Get My Results' button...")
        results_clicked = False
        for submit_sel in [
            'button:has-text("Get My Results")',
            'button:has-text("Get Results")',
            'button:has-text("See My Results")',
            'button:has-text("View Results")',
            'button:has-text("Submit")',
            'input[type="submit"]',
            'button[type="submit"]',
            '.submit-btn',
            '.btn-submit',
            '[class*="submit"]',
            '[class*="result"] button',
        ]:
            try:
                btn = page.locator(submit_sel).first
                if btn.is_visible(timeout=1500):
                    btn.click()
                    log(f"  Clicked submit with: {submit_sel}")
                    results_clicked = True
                    break
            except Exception:
                continue

        if not results_clicked:
            log("  Trying JavaScript click on Get My Results button...")
            try:
                page.evaluate("""
                    () => {
                        const buttons = Array.from(document.querySelectorAll('button, input[type="submit"], [role="button"]'));
                        const btn = buttons.find(b => {
                            const text = (b.innerText || b.value || '').toLowerCase();
                            return text.includes('result') || text.includes('submit') || text.includes('see my');
                        });
                        if (btn) { btn.click(); return true; }
                        return false;
                    }
                """)
                log("  JS click attempted")
                results_clicked = True
            except Exception as e:
                log(f"  JS click failed: {e}")

        log("Waiting 8 seconds for Google Forms iframe submission and results to load...")
        time.sleep(8)

        # Take results screenshots
        log("Taking viewport screenshot of results...")
        page.screenshot(path=SCREENSHOT_RESULTS)
        log(f"Results screenshot: {SCREENSHOT_RESULTS}")

        log("Taking FULL page screenshot of results...")
        page.screenshot(
            path="/home/jared/projects/AI-CIV/aether/exports/screenshots/assessment_04_results_full.png",
            full_page=True
        )

        # Get current page state
        try:
            url = page.url
            title = page.title()
            log(f"Current URL: {url}")
            log(f"Page title: {title}")

            body_text = page.evaluate("() => document.body.innerText.substring(0, 1000)")
            log(f"Body text preview:\n{body_text}")
        except Exception as e:
            log(f"Page state check failed: {e}")

        # Scroll to find share section
        log("\nScrolling down to find share section...")
        page.evaluate("window.scrollBy(0, 700)")
        time.sleep(2)

        page.screenshot(path=SCREENSHOT_SHARE)
        log(f"Share screenshot: {SCREENSHOT_SHARE}")

        page.screenshot(
            path="/home/jared/projects/AI-CIV/aether/exports/screenshots/assessment_05_share_full.png",
            full_page=True
        )

        # Try scrolling more to get bottom of results
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        page.screenshot(
            path="/home/jared/projects/AI-CIV/aether/exports/screenshots/assessment_06_bottom.png"
        )

        log("\n=== Console Messages (last 30) ===")
        for msg in console_messages[-30:]:
            log(msg)

        browser.close()
        log("\n=== ALL SCREENSHOTS COMPLETE ===")
        return True


if __name__ == "__main__":
    success = run_assessment()
    sys.exit(0 if success else 1)
