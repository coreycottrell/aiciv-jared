#!/usr/bin/env python3
"""
Witness Birth Pipeline - Chatflow Visual Audit
Tests both sandbox-2 and pay-test-2 pages
Captures key UX moments for Witness integration analysis

Goal: Document where Witness birth pipeline would slot into the UX
"""

import sys
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/witness-audit-20260224")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

PASSWORD = "PureBrain.ai253443$$$"
SANDBOX_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PAYTEST_URL = "https://purebrain.ai/pay-test-2/"

# Witness/AiCIV keyword scan
WITNESS_KEYWORDS = [
    "aiciv", "ai-civ", "witness", "portal access", "oauth",
    "launching your ai", "launch your ai", "your ai is ready",
    "birth", "activate your ai", "your agent", "your instance"
]

findings = {
    "sandbox_2": {},
    "pay_test_2": {},
    "witness_keywords_found": [],
    "screenshots": []
}


def ss(page, name, desc=""):
    """Take screenshot and record it."""
    path = SCREENSHOT_DIR / f"{name}.png"
    try:
        page.screenshot(path=str(path), full_page=False)
        findings["screenshots"].append({"file": name, "desc": desc})
        print(f"  [screenshot] {name}.png - {desc}")
    except Exception as e:
        print(f"  [screenshot FAILED] {name}.png - {e}")
    return path


def unlock_page(page, url, label):
    """Navigate and unlock WP password-protected page."""
    print(f"\n[{label}] Loading {url}")
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print(f"  Timeout/error on goto (expected for heavy pages): {e}")
    time.sleep(5)

    # Check if password form present
    pw_input = page.locator("input[id^='pwbox-']")
    if pw_input.count() > 0:
        print(f"  Password gate found, entering...")
        pw_input.first.fill(PASSWORD)
        page.locator("input[type='submit']").first.click()
        time.sleep(10)
        print(f"  Unlocked!")
    else:
        print(f"  No password gate (may be cached or already unlocked)")

    ss(page, f"{label}_01_unlocked", "Page unlocked - initial state")
    return True


def scan_page_text_for_witness(page, label):
    """Scan all visible text for Witness/AiCIV keywords."""
    found = []
    try:
        page_text = page.evaluate("() => document.body.innerText").lower()
        script_text = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('script')).map(s => s.textContent).join(' ');
        }""").lower()

        for kw in WITNESS_KEYWORDS:
            if kw in page_text:
                found.append({"keyword": kw, "location": "visible_text"})
            if kw in script_text:
                found.append({"keyword": kw, "location": "script_content"})
    except Exception as e:
        print(f"  Scan error: {e}")

    if found:
        print(f"  WITNESS KEYWORDS FOUND: {found}")
        findings["witness_keywords_found"].extend(found)
    else:
        print(f"  No witness/AiCIV keywords in page")
    return found


def get_ai_messages(page):
    """Get all AI messages from post-payment chat."""
    try:
        return page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai'))
                .map(m => m.innerText.trim())
                .filter(t => t.length > 0);
        }""")
    except:
        return []


def get_visible_buttons(page):
    """Get all visible buttons."""
    try:
        return page.evaluate("""() => {
            return Array.from(document.querySelectorAll('button, .ptc-btn, .chat-btn'))
                .filter(b => b.offsetWidth > 0 || b.offsetHeight > 0)
                .map(b => ({text: b.innerText.trim(), id: b.id, classes: b.className.substring(0,80)}))
                .filter(b => b.text.length > 0)
                .slice(0, 15);
        }""")
    except:
        return []


def send_message(page, text, wait=10):
    """Send a message in the post-payment chat."""
    textarea = page.locator("textarea[placeholder*='Message'], textarea[placeholder*='message'], textarea[placeholder*='Your']")
    if textarea.count() > 0:
        textarea.first.fill(text)
        send_btn = page.locator("button.ptc-send-btn, button[class*='send']")
        if send_btn.count() > 0:
            send_btn.first.click()
        else:
            page.keyboard.press("Enter")
        time.sleep(wait)
        return True
    return False


def test_sandbox_2(page):
    """Full walk of sandbox-2 post-payment chatflow."""
    label = "sandbox2"
    print("\n" + "="*60)
    print("TESTING: pay-test-sandbox-2")
    print("="*60)

    unlock_page(page, SANDBOX_URL, label)
    scan_page_text_for_witness(page, label)

    # Click Begin Awakening
    print("  Clicking Begin Awakening...")
    begin_btn = page.locator(".chat-initial__btn")
    if begin_btn.count() > 0:
        begin_btn.first.scroll_into_view_if_needed()
        begin_btn.first.click()
        time.sleep(3)
        ss(page, f"{label}_02_chat_open", "Chat opened after Begin Awakening click")
    else:
        print("  WARNING: No .chat-initial__btn - looking for alternatives...")
        # Try scrolling down
        page.evaluate("window.scrollBy(0, 400)")
        time.sleep(2)
        begin_btn2 = page.locator("text=Begin Awakening")
        if begin_btn2.count() > 0:
            begin_btn2.first.click()
            time.sleep(3)
        ss(page, f"{label}_02_chat_open", "After Begin Awakening attempt")

    # Enter bypass code
    print("  Entering bypass code pb-full-bypass...")
    user_input = page.locator("#userInput")
    if user_input.count() > 0:
        user_input.first.fill("pb-full-bypass")
        page.keyboard.press("Enter")
        print("  Waiting 20s for Keen AI response...")
        time.sleep(20)
        ss(page, f"{label}_03_after_bypass", "After bypass - Keen response and pricing")
    else:
        print("  #userInput not found")
        ss(page, f"{label}_03_no_input", "userInput not found")

    # Check what's visible now
    buttons_now = get_visible_buttons(page)
    print(f"  Visible buttons after bypass: {json.dumps(buttons_now, indent=2)}")
    findings["sandbox_2"]["buttons_after_bypass"] = buttons_now

    # Scroll down to find pricing / CTA
    page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
    time.sleep(1)
    ss(page, f"{label}_04_scrolled_pricing", "Scrolled to see pricing section")

    # Click Activate Now / Pro CTA
    activate_btn = page.locator("#proCta")
    if activate_btn.count() > 0:
        print("  Clicking #proCta (Activate Now)...")
        activate_btn.first.click()
        time.sleep(5)
        ss(page, f"{label}_05_paypal_overlay", "PayPal overlay after clicking Activate Now")
    else:
        # Try pricing CTAs
        cta = page.locator(".pricing-card__cta")
        if cta.count() > 0:
            print(f"  Clicking pricing CTA ({cta.count()} found)...")
            cta.first.click()
            time.sleep(5)
            ss(page, f"{label}_05_paypal_overlay", "PayPal overlay after clicking pricing CTA")
        else:
            print("  No CTA found - clicking discover/discover type btn")
            page.evaluate("""() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const btn = btns.find(b => b.innerText.toLowerCase().includes('discover') ||
                                         b.innerText.toLowerCase().includes('activate'));
                if (btn) { btn.scrollIntoView(); btn.click(); }
            }""")
            time.sleep(5)
            ss(page, f"{label}_05_after_activate_attempt", "After activate attempt")

    # Look for sandbox bypass button
    print("  Looking for sandbox payment bypass button...")
    sandbox_btn = page.locator("#pb-sandbox-bypass-btn")
    if sandbox_btn.count() > 0:
        print("  FOUND #pb-sandbox-bypass-btn - clicking...")
        ss(page, f"{label}_06_pre_sandbox_bypass", "Before clicking sandbox payment bypass")
        sandbox_btn.first.click()
        print("  Waiting 15s for post-payment chat to load...")
        time.sleep(15)
        ss(page, f"{label}_07_post_payment_appeared", "POST-PAYMENT chat container appeared")
    else:
        print("  No sandbox bypass button visible yet - checking overlay...")
        # PayPal overlay might be in the way, look inside it
        overlay_buttons = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('button'))
                .map(b => ({text: b.innerText.trim(), id: b.id, visible: b.offsetParent !== null}))
                .filter(b => b.text.length > 0 && (b.visible || b.id));
        }""")
        print(f"  All buttons in DOM: {json.dumps(overlay_buttons[:20], indent=2)}")
        # Try direct JS click on sandbox bypass
        page.evaluate("""() => {
            const btn = document.querySelector('#pb-sandbox-bypass-btn');
            if (btn) { btn.scrollIntoView(); btn.click(); }
        }""")
        time.sleep(10)
        ss(page, f"{label}_07_after_js_click", "After JS click on sandbox bypass")

    # POST-PAYMENT QUESTIONNAIRE
    print("\n  === POST-PAYMENT QUESTIONNAIRE FLOW ===")

    post_pay = page.locator("#pay-test-post-payment")
    ptc_visible = post_pay.count() > 0
    findings["sandbox_2"]["post_payment_container_exists"] = ptc_visible

    if ptc_visible:
        print("  Post-payment container found in DOM!")

        ai_msgs = get_ai_messages(page)
        print(f"  Initial AI messages ({len(ai_msgs)}): {ai_msgs}")
        findings["sandbox_2"]["initial_ai_messages"] = ai_msgs
        ss(page, f"{label}_08_questionnaire_start", "Questionnaire start - initial AI message")

        # Check if there's a textarea for input
        has_textarea = page.locator("textarea").count() > 0
        print(f"  Has textarea: {has_textarea}")

        if has_textarea:
            # Q1: Name
            print("  Answering Name question...")
            sent = send_message(page, "Alex Johnson", wait=10)
            if sent:
                ai_msgs = get_ai_messages(page)
                findings["sandbox_2"]["after_name_ai"] = ai_msgs[-1] if ai_msgs else None
                print(f"  After name - last AI: {ai_msgs[-1][:100] if ai_msgs else 'none'}")
                ss(page, f"{label}_09_after_name", "After name - email question appears")

                # Q2: Email
                print("  Answering Email question...")
                send_message(page, "alex@company.com", wait=10)
                ai_msgs = get_ai_messages(page)
                findings["sandbox_2"]["after_email_ai"] = ai_msgs[-1] if ai_msgs else None
                print(f"  After email - last AI: {ai_msgs[-1][:100] if ai_msgs else 'none'}")
                ss(page, f"{label}_10_after_email", "After email - company question appears")

                # Q3: Company
                print("  Answering Company question...")
                send_message(page, "Acme Corp", wait=10)
                ai_msgs = get_ai_messages(page)
                findings["sandbox_2"]["after_company_ai"] = ai_msgs[-1] if ai_msgs else None
                print(f"  After company - last AI: {ai_msgs[-1][:150] if ai_msgs else 'none'}")
                ss(page, f"{label}_11_role_question", "ROLE QUESTION - key Witness insertion point")

                # Check for role buttons
                role_btns = get_visible_buttons(page)
                print(f"  Buttons at role question: {json.dumps(role_btns, indent=2)}")
                findings["sandbox_2"]["role_buttons"] = role_btns

                # Click first role button
                ptc_btn = page.locator(".ptc-btn, button.ptc-btn--primary")
                if ptc_btn.count() > 0:
                    role_text = ptc_btn.first.inner_text()
                    print(f"  Clicking role button: '{role_text}'")
                    ptc_btn.first.click()
                    time.sleep(12)

                    ai_msgs = get_ai_messages(page)
                    last_ai = ai_msgs[-1] if ai_msgs else "none"
                    findings["sandbox_2"]["after_role_ai"] = last_ai
                    findings["sandbox_2"]["role_chosen"] = role_text
                    print(f"  After role - last AI: {last_ai[:200]}")
                    ss(page, f"{label}_12_after_role", "AFTER ROLE - what appears next?")

                    # Check for Claude auth prompt
                    claude_auth = any(
                        kw in last_ai.lower()
                        for kw in ["claude", "api key", "api", "before we go deeper"]
                    )
                    findings["sandbox_2"]["claude_auth_appears_after_role"] = claude_auth
                    print(f"  Claude auth appears: {claude_auth}")

                    if claude_auth:
                        ss(page, f"{label}_13_claude_auth", "Claude API auth prompt - CRITICAL WITNESS OPPORTUNITY")

                        # Click "I have my key" if present
                        have_key = page.locator("text=I have my key")
                        if have_key.count() > 0:
                            have_key.first.click()
                            time.sleep(5)
                            ss(page, f"{label}_14_api_key_input", "API key input area")

                            # Enter test key
                            send_message(page, "sk-ant-api03-test-key-for-audit-only", wait=12)
                            ai_msgs = get_ai_messages(page)
                            findings["sandbox_2"]["after_api_key_ai"] = ai_msgs[-1] if ai_msgs else None
                            print(f"  After API key: {ai_msgs[-1][:200] if ai_msgs else 'none'}")
                            ss(page, f"{label}_15_after_api_key", "After API key - primary goal question")

                            # Q: Primary Goal
                            ptc_btn2 = page.locator(".ptc-btn, button.ptc-btn--primary")
                            if ptc_btn2.count() > 0:
                                goal_text = ptc_btn2.first.inner_text()
                                ptc_btn2.first.click()
                                time.sleep(10)
                                ai_msgs = get_ai_messages(page)
                                findings["sandbox_2"]["after_goal_ai"] = ai_msgs[-1] if ai_msgs else None
                                print(f"  After goal ({goal_text}): {ai_msgs[-1][:200] if ai_msgs else 'none'}")
                                ss(page, f"{label}_16_behind_curtain", "BEHIND THE CURTAIN slides begin")

                                # Navigate slides
                                for slide_num in range(1, 6):
                                    show_more = page.locator("text=Show Me More")
                                    if show_more.count() > 0:
                                        show_more.first.click()
                                        time.sleep(3)
                                        ss(page, f"{label}_slide_{slide_num:02d}", f"Behind the Curtain slide {slide_num}")
                                    else:
                                        # Try "That's incredible" button
                                        incredible = page.locator("text=incredible")
                                        if incredible.count() > 0:
                                            incredible.first.click()
                                            time.sleep(5)
                                        break

                                ss(page, f"{label}_17_after_slides", "After slides - Telegram question appears")
                                ai_msgs = get_ai_messages(page)
                                findings["sandbox_2"]["after_slides_ai"] = ai_msgs[-1] if ai_msgs else None
                                print(f"  After slides: {ai_msgs[-1][:200] if ai_msgs else 'none'}")

                                # Check for Telegram buttons
                                tg_btns = get_visible_buttons(page)
                                findings["sandbox_2"]["telegram_buttons"] = tg_btns
                                print(f"  Telegram buttons: {json.dumps(tg_btns, indent=2)}")
                                ss(page, f"{label}_18_telegram_question", "TELEGRAM SETUP - Witness pipeline would come AFTER this")

    scan_page_text_for_witness(page, f"{label}_final")

    # Capture all AI messages for full flow documentation
    all_ai = get_ai_messages(page)
    findings["sandbox_2"]["all_ai_messages_final"] = all_ai
    print(f"\n  COMPLETE AI MESSAGE HISTORY ({len(all_ai)} messages):")
    for i, msg in enumerate(all_ai):
        print(f"    [{i+1}] {msg[:150]}")

    ss(page, f"{label}_final_state", "Final state - sandbox-2 audit complete")
    print(f"\n[{label}] Audit complete")
    return findings["sandbox_2"]


def test_pay_test_2(page):
    """Audit pay-test-2 (non-sandbox) for structure differences."""
    label = "paytest2"
    print("\n" + "="*60)
    print("TESTING: pay-test-2 (non-sandbox)")
    print("="*60)

    print(f"  Loading {PAYTEST_URL}")
    try:
        page.goto(PAYTEST_URL, wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print(f"  Load timeout (expected): {e}")
    time.sleep(5)

    # Check password gate
    pw_input = page.locator("input[id^='pwbox-']")
    if pw_input.count() > 0:
        print("  Password gate - entering...")
        pw_input.first.fill(PASSWORD)
        page.locator("input[type='submit']").first.click()
        time.sleep(10)
    else:
        print("  No password gate (session cookie still valid)")

    ss(page, f"{label}_01_unlocked", "pay-test-2 unlocked")
    scan_page_text_for_witness(page, label)

    # Page structure check
    page_info = page.evaluate("""() => {
        return {
            title: document.title,
            url: window.location.href,
            has_sandbox_banner: !!(document.querySelector('.sandbox-banner') ||
                                   document.body.innerText.toLowerCase().includes('sandbox mode')),
            has_chat_initial: !!document.querySelector('.chat-initial__btn'),
            has_post_payment: !!document.querySelector('#pay-test-post-payment'),
            has_sandbox_bypass: !!document.querySelector('#pb-sandbox-bypass-btn'),
            has_witness: document.body.innerText.toLowerCase().includes('witness'),
            has_aiciv: document.body.innerText.toLowerCase().includes('aiciv'),
            has_portal: document.body.innerText.toLowerCase().includes('portal'),
            body_preview: document.body.innerText.substring(0, 300)
        };
    }""")
    print(f"  Page info: {json.dumps(page_info, indent=2)}")
    findings["pay_test_2"]["page_info"] = page_info

    # Click Begin Awakening
    begin_btn = page.locator(".chat-initial__btn")
    if begin_btn.count() > 0:
        begin_btn.first.click()
        time.sleep(3)
        ss(page, f"{label}_02_chat_open", "pay-test-2 chat opened")

        # Bypass code
        user_input = page.locator("#userInput")
        if user_input.count() > 0:
            user_input.first.fill("pb-full-bypass")
            page.keyboard.press("Enter")
            time.sleep(20)
            ss(page, f"{label}_03_after_bypass", "pay-test-2 after bypass - pricing visible")

        # Check sandbox bypass (should NOT be present)
        sb_btn = page.locator("#pb-sandbox-bypass-btn")
        has_sb = sb_btn.count() > 0
        print(f"  Has #pb-sandbox-bypass-btn: {has_sb} (EXPECTED: False for non-sandbox)")
        findings["pay_test_2"]["has_sandbox_bypass_btn"] = has_sb

        # CTA buttons
        cta_info = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.pricing-card__cta, #proCta, #bonded, #foundry'))
                .map(b => ({
                    id: b.id,
                    text: b.innerText.trim().substring(0, 50),
                    classes: b.className.substring(0, 80),
                    data_plan: b.getAttribute('data-plan') || b.getAttribute('data-subscription-id') || 'none'
                }));
        }""")
        print(f"  CTA buttons: {json.dumps(cta_info, indent=2)}")
        findings["pay_test_2"]["cta_buttons"] = cta_info
        ss(page, f"{label}_04_pricing_with_ctas", "pay-test-2 pricing section with real PayPal CTAs")

        # Scroll down to see full pricing
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        time.sleep(2)
        ss(page, f"{label}_05_pricing_scrolled", "pay-test-2 pricing scrolled")

        # Get all visible text on page for full comparison
        pricing_text = page.evaluate("""() => {
            const p = document.querySelector('.pricing-section');
            return p ? p.innerText : 'none';
        }""")
        print(f"  Pricing section: {pricing_text[:500] if pricing_text else 'none'}")
        findings["pay_test_2"]["pricing_section_text"] = pricing_text

    # Check for Witness/portal language in entire page
    scan_page_text_for_witness(page, f"{label}_final")

    # Check scripts for Witness references
    script_check = page.evaluate("""() => {
        const scripts = Array.from(document.querySelectorAll('script')).map(s => s.textContent);
        const allText = scripts.join(' ').toLowerCase();
        return {
            has_aiciv: allText.includes('aiciv'),
            has_witness: allText.includes('witness'),
            has_oauth: allText.includes('oauth'),
            has_portal: allText.includes('portal'),
            has_sandbox_logic: allText.includes('sandbox'),
            sandbox_line: scripts.find(s => s.includes('sandbox')) ?
                scripts.find(s => s.includes('sandbox')).substring(
                    scripts.find(s => s.includes('sandbox')).indexOf('sandbox') - 50,
                    scripts.find(s => s.includes('sandbox')).indexOf('sandbox') + 200
                ) : 'not found'
        };
    }""")
    print(f"  Script analysis: {json.dumps(script_check, indent=2)}")
    findings["pay_test_2"]["script_analysis"] = script_check

    ss(page, f"{label}_final_state", "Final state - pay-test-2 audit complete")
    print(f"\n[{label}] Audit complete")
    return findings["pay_test_2"]


def main():
    print("=" * 60)
    print("WITNESS BIRTH PIPELINE - CHATFLOW VISUAL AUDIT")
    print("Date: 2026-02-24")
    print("=" * 60)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
                  "--disable-setuid-sandbox", "--no-first-run", "--disable-extensions"]
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            ignore_https_errors=True
        )
        page = context.new_page()
        page.set_default_timeout(60000)

        # Suppress console noise
        page.on("console", lambda msg: None)
        page.on("pageerror", lambda err: None)

        try:
            test_sandbox_2(page)

            print("\n[PAUSE] 20s before testing pay-test-2...")
            time.sleep(20)

            test_pay_test_2(page)

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()
            try:
                ss(page, "error_state", f"Error: {str(e)[:100]}")
            except:
                pass
        finally:
            browser.close()

    # Save findings
    report_path = Path("/home/jared/projects/AI-CIV/aether/exports/witness-chatflow-audit-20260224.json")
    with open(report_path, "w") as f:
        json.dump(findings, f, indent=2, default=str)

    print(f"\n[DONE] Findings saved: {report_path}")
    print(f"Screenshots: {SCREENSHOT_DIR}")
    print(f"Total screenshots: {len(findings['screenshots'])}")
    print(f"Witness keywords found: {len(findings['witness_keywords_found'])}")

    return findings


if __name__ == "__main__":
    result = main()
    print("\n=== SUMMARY ===")
    print(f"Sandbox-2 post-payment visible: {result['sandbox_2'].get('post_payment_container_exists')}")
    print(f"Sandbox-2 Claude auth after role: {result['sandbox_2'].get('claude_auth_appears_after_role')}")
    print(f"Sandbox-2 role chosen: {result['sandbox_2'].get('role_chosen')}")
    print(f"Witness keywords found: {result['witness_keywords_found']}")
    print(f"pay-test-2 has sandbox bypass: {result['pay_test_2'].get('has_sandbox_bypass_btn')}")
