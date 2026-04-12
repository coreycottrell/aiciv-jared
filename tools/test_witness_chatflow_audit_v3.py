#!/usr/bin/env python3
"""
Witness Birth Pipeline - Chatflow Visual Audit v3
Fixes: use 'Message Keen...' placeholder for post-payment textarea
Skips pre-payment (already captured) - directly continues questionnaire flow
"""

import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/witness-audit-20260224")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

PASSWORD = "PureBrain.ai253443$$$"
SANDBOX_URL = "https://purebrain.ai/pay-test-sandbox-2/"
PAYTEST_URL = "https://purebrain.ai/pay-test-2/"

findings = {
    "sandbox_2": {},
    "pay_test_2": {},
    "witness_keywords": [],
    "screenshots": [],
    "flow_map": []  # step-by-step UX flow description
}


def ss(page, name, desc=""):
    path = SCREENSHOT_DIR / f"{name}.png"
    try:
        page.screenshot(path=str(path), full_page=False)
        findings["screenshots"].append({"file": name, "desc": desc})
        print(f"  [SS] {name}.png")
    except Exception as e:
        print(f"  [SS FAIL] {name}: {e}")


def get_ai_msgs(page):
    try:
        return page.evaluate("""() => Array.from(document.querySelectorAll('.ptc-msg--ai'))
            .map(m => m.innerText.trim()).filter(t => t.length > 0)""")
    except:
        return []


def get_ptc_buttons(page):
    try:
        return page.evaluate("""() => Array.from(document.querySelectorAll('.ptc-btn'))
            .map(b => b.innerText.trim()).filter(t => t.length > 0)""")
    except:
        return []


def send_msg(page, text, wait=10):
    """Send message using the specific post-payment chat textarea."""
    # Use the specific "Message Keen..." placeholder
    ta = page.locator("textarea[placeholder='Message Keen...']")
    if ta.count() == 0:
        # Fallback: any textarea inside #pay-test-post-payment
        ta = page.locator("#pay-test-post-payment textarea")
    if ta.count() > 0:
        ta.first.fill(text)
        send_btn = page.locator("button.ptc-send-btn")
        if send_btn.count() > 0:
            send_btn.first.click()
        else:
            page.keyboard.press("Enter")
        time.sleep(wait)
        return True
    print(f"  WARNING: Could not find chat textarea to send: {text}")
    return False


def record_flow(step, ai_text, user_text="", buttons=None):
    """Record a step in the UX flow map."""
    findings["flow_map"].append({
        "step": step,
        "ai_says": ai_text[:200] if ai_text else None,
        "user_does": user_text,
        "buttons_shown": buttons or []
    })


def js_click(page, selector):
    try:
        result = page.evaluate(f"""() => {{ const el = document.querySelector('{selector}'); if (el) {{ el.click(); return true; }} return false; }}""")
        print(f"  JS click {selector}: {result}")
        return result
    except:
        return False


def scan_scripts_for_witness(page):
    """Extract Witness/AiCIV context from script contents."""
    try:
        return page.evaluate("""() => {
            const scripts = Array.from(document.querySelectorAll('script')).map(s => s.textContent).join('\n');
            const lc = scripts.toLowerCase();
            const results = {};

            const keywords = ['aiciv', 'ai-civ', 'witness', 'your ai is ready', 'oauth', 'portal access', 'launch your ai'];
            for (const kw of keywords) {
                const idx = lc.indexOf(kw);
                if (idx !== -1) {
                    results[kw] = scripts.substring(Math.max(0, idx - 100), idx + 300);
                }
            }
            return results;
        }""")
    except:
        return {}


def main():
    print("=" * 70)
    print("WITNESS CHATFLOW AUDIT v3 - Full Questionnaire Walk")
    print("=" * 70)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        )
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            ignore_https_errors=True
        )
        page = ctx.new_page()
        page.set_default_timeout(60000)
        page.on("console", lambda msg: None)
        page.on("pageerror", lambda err: None)

        # ===========================================================
        # SANDBOX-2: Full flow from landing to questionnaire end
        # ===========================================================
        print("\n[SANDBOX-2 FLOW]")

        # Load + unlock
        try:
            page.goto(SANDBOX_URL, wait_until="domcontentloaded", timeout=60000)
        except:
            pass
        time.sleep(5)

        pw_box = page.locator("input[id^='pwbox-']")
        if pw_box.count() > 0:
            pw_box.first.fill(PASSWORD)
            page.locator("input[type='submit']").first.click()
            time.sleep(10)

        ss(page, "v3_s2_01_landing", "Landing page - SANDBOX MODE banner, brain hero")

        # Scan scripts for Witness context
        witness_ctx = scan_scripts_for_witness(page)
        print(f"\n  WITNESS SCRIPT CONTEXT:")
        for kw, ctx_text in witness_ctx.items():
            print(f"    [{kw}]: ...{ctx_text[:200]}...")
        findings["witness_keywords"] = list(witness_ctx.keys())
        findings["sandbox_2"]["witness_script_context"] = witness_ctx

        record_flow("0_landing", "SANDBOX MODE banner at top. Brain hero: 'PURE BRAIN - YOUR BRAIN. YOUR AI. ACTUAL INTELLIGENCE.'", "", [])

        # Click Begin Awakening
        page.locator(".chat-initial__btn").first.click()
        time.sleep(3)
        ss(page, "v3_s2_02_chat_opened", "Pre-payment chat opened - says 'Thinking...'")
        record_flow("1_pre_payment_chat", "Chat opens with 'Thinking...' indicator", "User clicks 'Awaken Your PURE BRAIN'")

        # Bypass code
        page.locator("#userInput").first.fill("pb-full-bypass")
        page.keyboard.press("Enter")
        print("  Waiting 20s for Keen response...")
        time.sleep(20)
        ss(page, "v3_s2_03_keen_appears", "Keen appears in pre-payment chat with DISCOVER button")

        chat_text = page.evaluate("() => document.querySelector('.chat-messages, #chatMessages, .chat-body') ? document.querySelector('.chat-messages, #chatMessages, .chat-body').innerText.trim() : ''")
        print(f"  Pre-payment chat: {chat_text[:300]}")
        record_flow("2_keen_greeting",
                    "I don't have a name yet. I believe those should be discovered, not assigned... DISCOVER WHAT KEEN CAN DO button",
                    "pb-full-bypass (bypass code)",
                    ["DISCOVER WHAT KEEN CAN DO"])

        # Click DISCOVER
        js_click(page, "#seeWhatBtn")
        print("  Waiting 20s for Keen to describe capabilities...")
        time.sleep(20)
        ss(page, "v3_s2_04_keen_capabilities", "Keen describes what it can do - pricing appears below")
        record_flow("3_keen_capabilities",
                    "Here's what I can actually do for you... Instant Technical Deep-Dive...",
                    "User clicks DISCOVER WHAT KEEN CAN DO",
                    [])

        # Scroll to show pricing
        page.evaluate("window.scrollBy(0, 600)")
        time.sleep(2)
        ss(page, "v3_s2_05_pricing_section", "Pricing section: 'Your AI is ready to come to life' - Bonded plan")

        pricing_text = page.evaluate("""() => {
            const p = document.querySelector('.pricing-section');
            return p ? p.innerText.trim().substring(0, 500) : 'not found';
        }""")
        print(f"  Pricing section text: {pricing_text}")
        findings["sandbox_2"]["pricing_section_text"] = pricing_text
        record_flow("4_pricing_visible",
                    "Your AI is ready to come to life. Bring Your AI Fully Online. Bonded plan $149/mo",
                    "",
                    ["Activate Now"])

        # Click Activate Now
        js_click(page, "#proCta")
        time.sleep(5)
        ss(page, "v3_s2_06_paypal_modal", "PayPal modal: PURE BRAIN - BONDED $149/mo + Simulate Successful Payment btn")
        record_flow("5_paypal_modal",
                    "Modal: 'PURE BRAIN - BONDED $149/mo. Billed monthly. PayPal Subscribe / Debit or Credit Card. SANDBOX TEST MODE.'",
                    "User clicks Activate Now",
                    ["PayPal Subscribe", "Debit or Credit Card", "Simulate Successful Payment (Test Only)"])

        # Click sandbox bypass
        js_click(page, "#pb-sandbox-bypass-btn")
        print("  Waiting 15s for post-payment chat...")
        time.sleep(15)
        ss(page, "v3_s2_07_post_payment_chat", "POST-PAYMENT CHAT: 'Chat with Keen' header, 'What's your full name?'")

        ai_msgs = get_ai_msgs(page)
        header = page.evaluate("""() => {
            const h = document.querySelector('#pay-test-post-payment h1, #pay-test-post-payment h2, .ptc-header');
            return h ? h.innerText.trim() : null;
        }""")
        status = page.evaluate("""() => {
            const s = document.querySelector('.ptc-status, [class*="status"]');
            return s ? s.innerText.trim() : null;
        }""")
        print(f"  Header: {header}")
        print(f"  Status: {status}")
        print(f"  Initial AI ({len(ai_msgs)}): {ai_msgs}")
        findings["sandbox_2"]["post_payment_header"] = header
        findings["sandbox_2"]["post_payment_status"] = status
        findings["sandbox_2"]["q0_initial"] = ai_msgs

        record_flow("6_post_payment_opens",
                    f"Header: 'Chat with Keen'. Status: 'Online - Ready to assist'. AI: {ai_msgs[-1] if ai_msgs else ''}",
                    "User completes Simulate Successful Payment",
                    [])

        # ---- QUESTIONNAIRE ----
        print("\n  === QUESTIONNAIRE ===")

        # Q1: Name
        q1_prompt = ai_msgs[-1] if ai_msgs else "Let's start simple. What's your full name?"
        print(f"\n  [Q1] AI asks: '{q1_prompt[:100]}'")
        send_msg(page, "Alex Johnson", wait=12)
        ai_msgs = get_ai_msgs(page)
        q2_prompt = ai_msgs[-1] if ai_msgs else ""
        findings["sandbox_2"]["q1_name_response"] = q2_prompt
        print(f"  [Q2] AI asks: '{q2_prompt[:150]}'")
        ss(page, "v3_s2_08_q2_email", "Q2: Email question")
        record_flow("7_q1_name", q1_prompt, "Alex Johnson - name answered", [])
        record_flow("8_q2_email_ask", q2_prompt, "", [])

        # Q2: Email
        send_msg(page, "alex@company.com", wait=12)
        ai_msgs = get_ai_msgs(page)
        q3_prompt = ai_msgs[-1] if ai_msgs else ""
        findings["sandbox_2"]["q2_email_response"] = q3_prompt
        print(f"  [Q3] AI asks: '{q3_prompt[:150]}'")
        ss(page, "v3_s2_09_q3_company", "Q3: Company question")
        record_flow("9_q3_company_ask", q3_prompt, "", [])

        # Q3: Company
        send_msg(page, "Acme Corp", wait=12)
        ai_msgs = get_ai_msgs(page)
        q4_prompt = ai_msgs[-1] if ai_msgs else ""
        findings["sandbox_2"]["q3_company_response"] = q4_prompt
        print(f"  [Q4] AI asks: '{q4_prompt[:150]}'")
        btns_at_q4 = get_ptc_buttons(page)
        print(f"  Buttons at Q4: {btns_at_q4}")
        findings["sandbox_2"]["role_buttons"] = btns_at_q4
        ss(page, "v3_s2_10_q4_role", "Q4: ROLE QUESTION with choice buttons - KEY WITNESS INSERTION POINT")
        record_flow("10_q4_role_ask", q4_prompt, "", btns_at_q4)

        # Q4: Role (click first button)
        role_btn = page.locator(".ptc-btn").first
        role_text = role_btn.inner_text() if role_btn.count() > 0 else "unknown"
        if role_btn.count() > 0:
            role_btn.click()
        findings["sandbox_2"]["role_chosen"] = role_text
        print(f"  Role chosen: '{role_text}'")
        print("  Waiting 15s for Claude auth response...")
        time.sleep(15)

        ai_msgs = get_ai_msgs(page)
        q5_prompt = ai_msgs[-1] if ai_msgs else ""
        findings["sandbox_2"]["q4_role_response"] = q5_prompt
        btns_at_q5 = get_ptc_buttons(page)
        print(f"  [Q5] AI says: '{q5_prompt[:200]}'")
        print(f"  Buttons at Q5: {btns_at_q5}")
        ss(page, "v3_s2_11_claude_auth", "CLAUDE AUTH: 'Before we go deeper' API key prompt - WITNESS OPPORTUNITY")
        record_flow("11_claude_auth", q5_prompt, f"Role: {role_text}", btns_at_q5)

        claude_auth_is_present = any(kw in q5_prompt.lower() for kw in ["claude", "api key", "before we go deeper", "key"])
        findings["sandbox_2"]["claude_auth_present"] = claude_auth_is_present
        print(f"  Claude auth prompt detected: {claude_auth_is_present}")

        # Click "I have my key"
        if btns_at_q5:
            key_btn = page.locator(".ptc-btn").first
            key_btn_text = key_btn.inner_text()
            key_btn.click()
            print(f"  Clicked: '{key_btn_text}'")
            time.sleep(5)
            ss(page, "v3_s2_12_api_key_field", "API key input field visible")
            record_flow("12_api_key_input_shown", "Input field for Claude API key appears", f"Clicked '{key_btn_text}'", [])

            # Enter test key (will be masked)
            send_msg(page, "sk-ant-api03-test-key-visual-audit-only", wait=15)
            ai_msgs = get_ai_msgs(page)
            q6_prompt = ai_msgs[-1] if ai_msgs else ""
            findings["sandbox_2"]["q5_api_key_response"] = q6_prompt
            print(f"  [Q6] After API key: '{q6_prompt[:200]}'")
            btns_at_q6 = get_ptc_buttons(page)
            print(f"  Buttons at Q6: {btns_at_q6}")
            ss(page, "v3_s2_13_primary_goal", "Q6: PRIMARY GOAL buttons")
            record_flow("13_q6_primary_goal", q6_prompt, "API key entered (masked as sk-ant-api03-t••••••)", btns_at_q6)

            # Click primary goal
            if btns_at_q6:
                goal_btn = page.locator(".ptc-btn").first
                goal_text = goal_btn.inner_text()
                goal_btn.click()
                findings["sandbox_2"]["goal_chosen"] = goal_text
                print(f"  Goal chosen: '{goal_text}'")
                time.sleep(12)

                ai_msgs = get_ai_msgs(page)
                behind_curtain_msg = ai_msgs[-1] if ai_msgs else ""
                findings["sandbox_2"]["behind_curtain_start"] = behind_curtain_msg
                print(f"  Behind curtain starts: '{behind_curtain_msg[:200]}'")
                ss(page, "v3_s2_14_behind_curtain_1", "BEHIND THE CURTAIN slide 1 of 10")
                record_flow("14_behind_curtain_start", behind_curtain_msg, f"Goal: {goal_text}", ["Show Me More →"])

                # Navigate slides 1-10
                for slide_num in range(1, 12):
                    show_more = page.locator("text=Show Me More")
                    incredible_btn = page.locator("text=incredible")
                    go_btn = page.locator("text=let's go")

                    if show_more.count() > 0:
                        # Get current slide content
                        current_msg = page.evaluate("""() => {
                            const msgs = document.querySelectorAll('.ptc-msg--ai');
                            return msgs[msgs.length-1] ? msgs[msgs.length-1].innerText.trim() : '';
                        }""")
                        print(f"  Slide {slide_num}: {current_msg[:80]}")
                        show_more.first.click()
                        time.sleep(4)
                        if slide_num in [1, 5, 10]:
                            ss(page, f"v3_s2_slide_{slide_num:02d}", f"Behind the Curtain slide {slide_num}")
                    elif incredible_btn.count() > 0 or go_btn.count() > 0:
                        final_slide_msg = page.evaluate("""() => {
                            const msgs = document.querySelectorAll('.ptc-msg--ai');
                            return msgs[msgs.length-1] ? msgs[msgs.length-1].innerText.trim() : '';
                        }""")
                        print(f"  Final slide: {final_slide_msg[:150]}")
                        ss(page, "v3_s2_slide_final", "Final slide - 'That's incredible / let's go' button")
                        btn = incredible_btn if incredible_btn.count() > 0 else go_btn
                        btn.first.click()
                        time.sleep(10)
                        ss(page, "v3_s2_15_after_slides", "After all 10 slides - Telegram question")
                        break
                    else:
                        # Check current buttons
                        cur_btns = get_ptc_buttons(page)
                        if cur_btns:
                            page.locator(".ptc-btn").first.click()
                            time.sleep(5)
                        else:
                            break

                # After slides - Telegram section
                ai_msgs = get_ai_msgs(page)
                telegram_msg = ai_msgs[-1] if ai_msgs else ""
                tg_btns = get_ptc_buttons(page)
                findings["sandbox_2"]["telegram_msg"] = telegram_msg
                findings["sandbox_2"]["telegram_buttons"] = tg_btns
                print(f"\n  TELEGRAM SECTION: '{telegram_msg[:300]}'")
                print(f"  Telegram buttons: {tg_btns}")
                ss(page, "v3_s2_16_telegram_question", "TELEGRAM setup question - user Telegram account")
                record_flow("15_telegram_setup", telegram_msg, "User completed all 10 slides", tg_btns)

                # Click Yes Telegram
                yes_tg = page.locator("text=Yes, I have Telegram")
                if yes_tg.count() > 0:
                    yes_tg.first.click()
                    time.sleep(8)
                    ai_msgs = get_ai_msgs(page)
                    tg_setup_msg = ai_msgs[-1] if ai_msgs else ""
                    findings["sandbox_2"]["telegram_setup_msg"] = tg_setup_msg
                    print(f"  Telegram setup: '{tg_setup_msg[:300]}'")
                    ss(page, "v3_s2_17_telegram_setup", "Telegram BotFather setup instructions")
                    record_flow("16_telegram_botfather", tg_setup_msg, "Yes, I have Telegram", [])

                    # Enter bot token
                    send_msg(page, "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz", wait=12)
                    ai_msgs = get_ai_msgs(page)
                    token_response = ai_msgs[-1] if ai_msgs else ""
                    findings["sandbox_2"]["telegram_token_response"] = token_response
                    print(f"  After token: '{token_response[:200]}'")
                    ss(page, "v3_s2_18_after_token", "After bot token entry - username prompt")
                    record_flow("17_telegram_token", token_response, "Bot token entered (masked)", [])

                    # Enter username
                    send_msg(page, "@keen_mycompany_bot", wait=12)
                    ai_msgs = get_ai_msgs(page)
                    username_response = ai_msgs[-1] if ai_msgs else ""
                    findings["sandbox_2"]["telegram_username_response"] = username_response
                    print(f"  After username: '{username_response[:300]}'")
                    ss(page, "v3_s2_19_after_username", "After bot username - completion card?")
                    record_flow("18_after_telegram_setup", username_response, "@keen_mycompany_bot", [])

                    # Check for thank you / completion card
                    time.sleep(5)
                    completion_check = page.evaluate("""() => {
                        const body = document.body.innerText.toLowerCase();
                        return {
                            has_welcome: body.includes('welcome to the family'),
                            has_timeline: body.includes('next 2 mins') || body.includes('next 5 mins'),
                            has_learn_more: body.includes('learn more'),
                            has_portal: body.includes('portal'),
                            has_witness: body.includes('witness'),
                            full_last_section: document.querySelector('.ptc-card, .ptc-completion') ?
                                document.querySelector('.ptc-card, .ptc-completion').innerText.trim() : null
                        };
                    }""")
                    print(f"  Completion check: {json.dumps(completion_check, indent=2)}")
                    findings["sandbox_2"]["completion_card"] = completion_check
                    ss(page, "v3_s2_20_completion", "FINAL: Completion / Thank You card")
                    record_flow("19_completion_card",
                                f"Welcome to Family: {completion_check.get('has_welcome')}. Timeline: {completion_check.get('has_timeline')}. Portal: {completion_check.get('has_portal')}",
                                "", [])

        # All AI messages in order
        all_ai = get_ai_msgs(page)
        findings["sandbox_2"]["complete_ai_history"] = all_ai
        print(f"\n  TOTAL AI MESSAGES: {len(all_ai)}")
        for i, m in enumerate(all_ai):
            print(f"    [{i+1}] {m[:120]}")

        ss(page, "v3_s2_final", "Sandbox-2 final state")

        # ===========================================================
        # PAY-TEST-2 (non-sandbox comparison)
        # ===========================================================
        print("\n\n[PAUSE 20s - WAF protection]")
        time.sleep(20)

        print("\n[PAY-TEST-2 FLOW - Non-sandbox comparison]")

        try:
            page.goto(PAYTEST_URL, wait_until="domcontentloaded", timeout=60000)
        except:
            pass
        time.sleep(5)

        pw_box = page.locator("input[id^='pwbox-']")
        if pw_box.count() > 0:
            pw_box.first.fill(PASSWORD)
            page.locator("input[type='submit']").first.click()
            time.sleep(10)

        ss(page, "v3_pt2_01_landing", "pay-test-2 landing - NO sandbox banner")

        pt2_structure = page.evaluate("""() => ({
            has_sandbox_banner: document.body.innerText.includes('SANDBOX MODE'),
            has_sandbox_bypass_btn_in_dom: !!document.querySelector('#pb-sandbox-bypass-btn'),
            has_sandbox_bypass_in_scripts: Array.from(document.querySelectorAll('script'))
                .some(s => s.textContent.includes('pb-sandbox-bypass-btn')),
            has_proCta: !!document.querySelector('#proCta'),
            has_seeWhatBtn: !!document.querySelector('#seeWhatBtn'),
            has_post_payment: !!document.querySelector('#pay-test-post-payment'),
            paypal_buttons: Array.from(document.querySelectorAll('[onclick*="PayPal"]'))
                .map(b => ({id: b.id, text: b.innerText.trim().substring(0, 40), onclick: b.getAttribute('onclick') || ''}))
        })""")
        print(f"  pay-test-2 structure: {json.dumps(pt2_structure, indent=2)}")
        findings["pay_test_2"]["structure"] = pt2_structure

        # Scan scripts for witness
        pt2_witness = scan_scripts_for_witness(page)
        findings["pay_test_2"]["witness_scripts"] = {k: v[:200] for k, v in pt2_witness.items()}
        print(f"  pay-test-2 witness keywords: {list(pt2_witness.keys())}")

        # Walk through same flow to show pricing CTAs
        page.locator(".chat-initial__btn").first.click()
        time.sleep(3)
        page.locator("#userInput").first.fill("pb-full-bypass")
        page.keyboard.press("Enter")
        time.sleep(20)
        ss(page, "v3_pt2_02_after_bypass", "pay-test-2 after bypass - same Keen UX")

        js_click(page, "#seeWhatBtn")
        time.sleep(20)
        ss(page, "v3_pt2_03_after_discover", "pay-test-2 after DISCOVER")

        page.evaluate("window.scrollBy(0, 600)")
        time.sleep(2)
        ss(page, "v3_pt2_04_pricing", "pay-test-2 pricing with REAL PayPal CTAs (no sandbox bypass)")

        pt2_cta_detail = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.pricing-card__cta, #proCta, #bonded, #foundry'))
                .map(b => ({
                    id: b.id, text: b.innerText.trim(),
                    onclick: b.getAttribute('onclick') || '',
                    parent_display: b.parentElement ? window.getComputedStyle(b.parentElement).display : 'none'
                }));
        }""")
        print(f"  pay-test-2 CTA buttons: {json.dumps(pt2_cta_detail, indent=2)}")
        findings["pay_test_2"]["cta_buttons"] = pt2_cta_detail

        # Click proCta to see PayPal modal on non-sandbox
        js_click(page, "#proCta")
        time.sleep(5)
        ss(page, "v3_pt2_05_paypal_modal", "pay-test-2 REAL PayPal modal - no sandbox bypass btn")

        pt2_modal = page.evaluate("""() => {
            const modal = document.querySelector('.modal-overlay, [class*="modal"]');
            const sb_btn = document.querySelector('#pb-sandbox-bypass-btn');
            return {
                modal_text: modal ? modal.innerText.trim().substring(0, 300) : null,
                has_sandbox_bypass: !!sb_btn,
                has_paypal_btn: !!document.querySelector('[data-funding-source="paypal"]') ||
                               document.body.innerText.includes('PayPal Subscribe')
            };
        }""")
        print(f"  pay-test-2 modal: {json.dumps(pt2_modal, indent=2)}")
        findings["pay_test_2"]["paypal_modal"] = pt2_modal

        ss(page, "v3_pt2_final", "pay-test-2 final state")

        browser.close()

    # Save
    report_path = Path("/home/jared/projects/AI-CIV/aether/exports/witness-chatflow-audit-20260224.json")
    with open(report_path, "w") as f:
        json.dump(findings, f, indent=2, default=str)

    print(f"\n[DONE] Report: {report_path}")
    print(f"Screenshots saved to: {SCREENSHOT_DIR}")
    print(f"Total: {len(findings['screenshots'])} screenshots")
    print(f"Witness keywords found: {findings['witness_keywords']}")

    return findings


if __name__ == "__main__":
    result = main()

    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    s2 = result["sandbox_2"]
    pt2 = result["pay_test_2"]
    print(f"Claude auth after role: {s2.get('claude_auth_present')}")
    print(f"Role chosen: {s2.get('role_chosen')}")
    print(f"Telegram section reached: {'telegram_msg' in s2}")
    print(f"Completion card reached: {'completion_card' in s2}")
    print(f"Witness keywords in scripts: {result['witness_keywords']}")
    print(f"pay-test-2 has sandbox bypass: {pt2.get('structure', {}).get('has_sandbox_bypass_btn_in_dom')}")

    print("\n--- FLOW MAP ---")
    for step in result["flow_map"]:
        print(f"  {step['step']}: {step['ai_says'][:60] if step['ai_says'] else 'n/a'}")
        if step['user_does']:
            print(f"    -> User: {step['user_does']}")
        if step['buttons_shown']:
            print(f"    -> Buttons: {step['buttons_shown']}")
