#!/usr/bin/env python3
"""
Witness Birth Pipeline - Chatflow Visual Audit v2
Correct flow: DISCOVER button first, THEN pricing appears, THEN sandbox bypass

Key fix: Must click #seeWhatBtn (DISCOVER WHAT KEEN CAN DO) before #proCta becomes visible
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
    path = SCREENSHOT_DIR / f"{name}.png"
    try:
        page.screenshot(path=str(path), full_page=False)
        findings["screenshots"].append({"file": name, "desc": desc})
        print(f"  [SS] {name}.png - {desc}")
    except Exception as e:
        print(f"  [SS FAIL] {name}: {e}")
    return path


def js_click(page, selector, desc=""):
    """Click element via JS regardless of visibility."""
    try:
        result = page.evaluate(f"""() => {{
            const el = document.querySelector('{selector}');
            if (el) {{ el.click(); return true; }}
            return false;
        }}""")
        print(f"  JS click '{selector}': {result} - {desc}")
        return result
    except Exception as e:
        print(f"  JS click error '{selector}': {e}")
        return False


def get_ai_messages(page):
    try:
        return page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-msg.ptc-msg--ai'))
                .map(m => m.innerText.trim())
                .filter(t => t.length > 0);
        }""")
    except:
        return []


def get_visible_ptc_buttons(page):
    try:
        return page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.ptc-btn'))
                .map(b => ({text: b.innerText.trim(), id: b.id, classes: b.className}))
                .filter(b => b.text.length > 0);
        }""")
    except:
        return []


def scan_for_witness(page, label):
    found = []
    try:
        body_text = page.evaluate("() => document.body.innerText").lower()
        script_text = page.evaluate("""() => Array.from(document.querySelectorAll('script')).map(s => s.textContent).join(' ')""").lower()
        for kw in WITNESS_KEYWORDS:
            if kw in body_text:
                found.append({"kw": kw, "loc": "body"})
            if kw in script_text:
                found.append({"kw": kw, "loc": "script"})
        findings["witness_keywords_found"].extend(found)
        if found:
            print(f"  [WITNESS] Keywords at {label}: {found}")
        else:
            print(f"  [WITNESS] No keywords at {label}")
    except Exception as e:
        print(f"  [WITNESS scan error] {e}")
    return found


def send_chat_message(page, text, wait=10):
    """Send message in post-payment chatbox."""
    textarea = page.locator("textarea")
    if textarea.count() > 0:
        textarea.first.fill(text)
        send_btn = page.locator("button.ptc-send-btn")
        if send_btn.count() > 0:
            send_btn.first.click()
        else:
            page.keyboard.press("Enter")
        time.sleep(wait)
        return True
    return False


def main():
    print("=" * 60)
    print("WITNESS CHATFLOW AUDIT v2 - Correct Click Sequence")
    print("Date: 2026-02-24")
    print("=" * 60)

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

        # ============================================================
        # SANDBOX-2 FLOW
        # ============================================================
        print("\n" + "="*60)
        print("PHASE 1: pay-test-sandbox-2")
        print("="*60)

        # Load page
        print("\n[1] Loading sandbox-2...")
        try:
            page.goto(SANDBOX_URL, wait_until="domcontentloaded", timeout=60000)
        except:
            pass
        time.sleep(5)

        # Unlock
        pw_box = page.locator("input[id^='pwbox-']")
        if pw_box.count() > 0:
            pw_box.first.fill(PASSWORD)
            page.locator("input[type='submit']").first.click()
            time.sleep(10)
            print("  Unlocked")
        ss(page, "s2_01_landing", "Sandbox-2 landing page - initial view")
        scan_for_witness(page, "sandbox2_initial")

        # ---- INITIAL PRE-CHAT STATE ----
        # Check for sandbox banner
        sandbox_banner = page.evaluate("""() => {
            const banner = document.querySelector('.sandbox-banner, [class*="sandbox"]');
            return banner ? banner.innerText.trim() : document.body.innerText.includes('SANDBOX') ? 'SANDBOX text found in body' : 'none';
        }""")
        print(f"\n[SANDBOX BANNER]: {sandbox_banner}")
        findings["sandbox_2"]["sandbox_banner"] = sandbox_banner

        # [2] Click Begin Awakening
        print("\n[2] Clicking Begin Awakening...")
        begin_btn = page.locator(".chat-initial__btn")
        if begin_btn.count() > 0:
            begin_btn.first.click()
        else:
            js_click(page, ".chat-initial__btn", "begin awakening fallback")
        time.sleep(4)
        ss(page, "s2_02_chat_opened", "Chat interface opened - typing area visible")

        # [3] Enter bypass code
        print("\n[3] Entering bypass code...")
        user_input = page.locator("#userInput")
        if user_input.count() > 0:
            user_input.first.fill("pb-full-bypass")
            page.keyboard.press("Enter")
        else:
            print("  #userInput not found!")
        print("  Waiting 20s for Keen response...")
        time.sleep(20)
        ss(page, "s2_03_bypass_response", "After bypass code - Keen appears with DISCOVER button")

        # Capture the chat text at this point
        chat_area_text = page.evaluate("""() => {
            const chat = document.querySelector('.chat-messages, #chatMessages, .chat-window');
            return chat ? chat.innerText.trim() : document.querySelector('.chat-body') ?
                   document.querySelector('.chat-body').innerText.trim() : 'chat area not found';
        }""")
        print(f"  Chat text: {chat_area_text[:300]}")
        findings["sandbox_2"]["chat_after_bypass"] = chat_area_text[:500]

        # [4] Click DISCOVER button
        print("\n[4] Clicking DISCOVER WHAT KEEN CAN DO...")
        discover_clicked = js_click(page, "#seeWhatBtn", "discover button")
        if not discover_clicked:
            js_click(page, ".chat-cta__btn", "discover fallback")
        print("  Waiting 20s for pricing section to load...")
        time.sleep(20)
        ss(page, "s2_04_after_discover", "After DISCOVER - pricing section should be visible")

        # Check pricing visibility
        pricing_visible = page.evaluate("""() => {
            const ps = document.querySelector('.pricing-section, [class*="pricing-section"]');
            if (!ps) return {exists: false};
            const style = window.getComputedStyle(ps);
            return {
                exists: true,
                display: style.display,
                visibility: style.visibility,
                text: ps.innerText.trim().substring(0, 200)
            };
        }""")
        print(f"  Pricing section: {json.dumps(pricing_visible, indent=2)}")
        findings["sandbox_2"]["pricing_after_discover"] = pricing_visible

        # Check if #proCta is now visible
        pro_cta_state = page.evaluate("""() => {
            const btn = document.querySelector('#proCta');
            if (!btn) return {exists: false};
            const style = window.getComputedStyle(btn);
            const parent_style = btn.parentElement ? window.getComputedStyle(btn.parentElement) : null;
            return {
                exists: true,
                display: style.display,
                visibility: style.visibility,
                text: btn.innerText.trim(),
                parent_display: parent_style ? parent_style.display : 'unknown'
            };
        }""")
        print(f"  #proCta state: {json.dumps(pro_cta_state, indent=2)}")
        findings["sandbox_2"]["pro_cta_after_discover"] = pro_cta_state

        # Scroll to see pricing
        page.evaluate("window.scrollBy(0, 500)")
        time.sleep(2)
        ss(page, "s2_05_pricing_visible", "Pricing section after scrolling post-DISCOVER")

        # [5] Click Activate Now via JS
        print("\n[5] Clicking Activate Now (proCta)...")
        activated = js_click(page, "#proCta", "activate now")
        if not activated:
            js_click(page, ".pricing-card__cta--primary", "primary pricing cta")
        time.sleep(5)
        ss(page, "s2_06_paypal_overlay", "PayPal overlay after clicking Activate Now")

        # Check PayPal modal state
        paypal_state = page.evaluate("""() => {
            const modal = document.querySelector('.paypal-modal, #paypalModal, [class*="paypal"]');
            const overlay = document.querySelector('.modal-overlay, [class*="modal"]');
            const sandbox_btn = document.querySelector('#pb-sandbox-bypass-btn');
            return {
                modal_exists: !!modal,
                overlay_exists: !!overlay,
                overlay_text: overlay ? overlay.innerText.trim().substring(0, 300) : null,
                sandbox_bypass_exists: !!sandbox_btn,
                sandbox_bypass_text: sandbox_btn ? sandbox_btn.innerText.trim() : null
            };
        }""")
        print(f"  PayPal overlay state: {json.dumps(paypal_state, indent=2)}")
        findings["sandbox_2"]["paypal_overlay"] = paypal_state

        # [6] Click sandbox bypass button
        print("\n[6] Clicking sandbox payment bypass...")
        bypass_result = js_click(page, "#pb-sandbox-bypass-btn", "sandbox payment bypass")
        if not bypass_result:
            print("  Sandbox bypass btn not found - checking if PayPal iframe opened...")
            # Try clicking by text
            page.evaluate("""() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const btn = btns.find(b => b.innerText.includes('Simulate') || b.innerText.includes('Test Only'));
                if (btn) btn.click();
            }""")

        print("  Waiting 15s for post-payment chat...")
        time.sleep(15)
        ss(page, "s2_07_post_payment", "POST-PAYMENT CHAT - main UX after payment")

        # Check post-payment container
        ptc_state = page.evaluate("""() => {
            const container = document.querySelector('#pay-test-post-payment');
            if (!container) return {exists: false};
            const style = window.getComputedStyle(container);
            const header = container.querySelector('h1, h2, h3, .ptc-header');
            const first_ai = container.querySelector('.ptc-msg--ai');
            return {
                exists: true,
                display: style.display,
                header: header ? header.innerText.trim() : null,
                first_ai_message: first_ai ? first_ai.innerText.trim() : null,
                has_textarea: !!container.querySelector('textarea'),
                has_send_btn: !!container.querySelector('button.ptc-send-btn')
            };
        }""")
        print(f"  Post-payment container: {json.dumps(ptc_state, indent=2)}")
        findings["sandbox_2"]["post_payment_container"] = ptc_state

        if ptc_state.get("exists"):
            print("\n  === QUESTIONNAIRE FLOW ===")

            ai_msgs = get_ai_messages(page)
            print(f"  Initial AI ({len(ai_msgs)}): {ai_msgs[-1][:150] if ai_msgs else 'none'}")
            findings["sandbox_2"]["q0_initial_ai"] = ai_msgs

            # Q1: Name
            print("\n  [Q1] Name...")
            send_chat_message(page, "Alex Johnson", wait=10)
            ai_msgs = get_ai_messages(page)
            findings["sandbox_2"]["q1_after_name"] = ai_msgs[-1] if ai_msgs else None
            print(f"  After name: {ai_msgs[-1][:150] if ai_msgs else 'none'}")
            ss(page, "s2_08_after_name", "Q1: Name answered - email question")

            # Q2: Email
            print("\n  [Q2] Email...")
            send_chat_message(page, "alex@company.com", wait=10)
            ai_msgs = get_ai_messages(page)
            findings["sandbox_2"]["q2_after_email"] = ai_msgs[-1] if ai_msgs else None
            print(f"  After email: {ai_msgs[-1][:150] if ai_msgs else 'none'}")
            ss(page, "s2_09_after_email", "Q2: Email answered - company question")

            # Q3: Company
            print("\n  [Q3] Company...")
            send_chat_message(page, "Acme Corp", wait=10)
            ai_msgs = get_ai_messages(page)
            findings["sandbox_2"]["q3_after_company"] = ai_msgs[-1] if ai_msgs else None
            print(f"  After company: {ai_msgs[-1][:200] if ai_msgs else 'none'}")
            ss(page, "s2_10_role_question", "Q3: ROLE QUESTION - key Witness slot")

            # Check for role buttons
            role_btns = get_visible_ptc_buttons(page)
            print(f"  Role buttons: {json.dumps(role_btns, indent=2)}")
            findings["sandbox_2"]["role_buttons"] = role_btns

            # Click first role button
            ptc_btns = page.locator(".ptc-btn")
            if ptc_btns.count() > 0:
                role_chosen = ptc_btns.first.inner_text()
                ptc_btns.first.click()
                print(f"  Clicked role: '{role_chosen}'")
                findings["sandbox_2"]["role_chosen"] = role_chosen
                time.sleep(12)

                ai_msgs = get_ai_messages(page)
                after_role = ai_msgs[-1] if ai_msgs else "none"
                findings["sandbox_2"]["q4_after_role"] = after_role
                print(f"  After role: {after_role[:300]}")
                ss(page, "s2_11_after_role", "After ROLE - Claude auth or next question")

                # Is this the Claude auth prompt?
                is_claude_auth = any(kw in after_role.lower() for kw in ["claude", "api key", "before we go deeper", "key"])
                findings["sandbox_2"]["claude_auth_after_role"] = is_claude_auth
                print(f"  Claude auth prompt: {is_claude_auth}")

                if is_claude_auth:
                    ss(page, "s2_12_claude_auth", "CLAUDE API AUTH - THIS IS WHERE WITNESS PIPELINE SLOTS IN")

                    # Click "I have my key"
                    have_key_btns = page.locator(".ptc-btn")
                    if have_key_btns.count() > 0:
                        key_btn_text = have_key_btns.first.inner_text()
                        have_key_btns.first.click()
                        print(f"  Clicked: '{key_btn_text}'")
                        time.sleep(5)
                        ss(page, "s2_13_api_key_input", "API key input state")

                        # Enter test API key
                        send_chat_message(page, "sk-ant-api03-test-key-audit", wait=12)
                        ai_msgs = get_ai_messages(page)
                        after_key = ai_msgs[-1] if ai_msgs else "none"
                        findings["sandbox_2"]["q5_after_api_key"] = after_key
                        print(f"  After API key: {after_key[:200]}")
                        ss(page, "s2_14_after_api_key", "After API key entry - primary goal question")

                        # Primary Goal buttons
                        goal_btns = get_visible_ptc_buttons(page)
                        print(f"  Goal buttons: {goal_btns}")
                        findings["sandbox_2"]["goal_buttons"] = goal_btns

                        goal_btn = page.locator(".ptc-btn")
                        if goal_btn.count() > 0:
                            goal_text = goal_btn.first.inner_text()
                            goal_btn.first.click()
                            print(f"  Goal chosen: '{goal_text}'")
                            findings["sandbox_2"]["goal_chosen"] = goal_text
                            time.sleep(10)
                            ss(page, "s2_15_behind_curtain_start", "BEHIND THE CURTAIN slides begin")

                            ai_msgs = get_ai_messages(page)
                            findings["sandbox_2"]["q6_after_goal"] = ai_msgs[-1] if ai_msgs else None
                            print(f"  Behind curtain msg: {ai_msgs[-1][:200] if ai_msgs else 'none'}")

                            # Navigate through slides
                            for i in range(1, 12):
                                # Check for slide indicator
                                slide_indicator = page.evaluate("""() => {
                                    const msgs = Array.from(document.querySelectorAll('.ptc-msg--ai'));
                                    const last = msgs[msgs.length - 1];
                                    return last ? last.innerText.substring(0, 100) : null;
                                }""")
                                print(f"  Slide {i}: {slide_indicator}")

                                # Check for "Show Me More" or "That's incredible"
                                show_more = page.locator("text=Show Me More")
                                incredible = page.locator("text=incredible")

                                if show_more.count() > 0:
                                    show_more.first.click()
                                    time.sleep(4)
                                    if i <= 3 or i >= 8:
                                        ss(page, f"s2_slide_{i:02d}", f"Behind the Curtain slide {i}")
                                elif incredible.count() > 0:
                                    ss(page, f"s2_slide_{i:02d}_last", f"Last slide - incredible button")
                                    incredible.first.click()
                                    time.sleep(8)
                                    ss(page, "s2_16_after_slides", "After all slides - Telegram question")
                                    break
                                else:
                                    # Check what's visible
                                    btns = get_visible_ptc_buttons(page)
                                    print(f"  Slide {i} - no more/incredible btns. Current buttons: {btns}")
                                    if btns:
                                        ptc_btn_next = page.locator(".ptc-btn")
                                        if ptc_btn_next.count() > 0:
                                            next_text = ptc_btn_next.first.inner_text()
                                            ptc_btn_next.first.click()
                                            time.sleep(5)
                                            ss(page, f"s2_slide_{i:02d}_btn", f"Slide {i} - clicked '{next_text}'")
                                    else:
                                        break

                            # After slides - Telegram section
                            ai_msgs = get_ai_messages(page)
                            after_slides = ai_msgs[-1] if ai_msgs else "none"
                            findings["sandbox_2"]["after_slides_msg"] = after_slides
                            print(f"\n  After slides: {after_slides[:300]}")

                            tg_btns = get_visible_ptc_buttons(page)
                            findings["sandbox_2"]["telegram_buttons"] = tg_btns
                            print(f"  Telegram buttons: {json.dumps(tg_btns, indent=2)}")
                            ss(page, "s2_17_telegram_question", "TELEGRAM - last step before Witness would go")

                            # Click Yes Telegram
                            tg_yes = page.locator("text=Yes, I have Telegram")
                            if tg_yes.count() > 0:
                                tg_yes.first.click()
                                time.sleep(8)
                                ss(page, "s2_18_telegram_setup", "Telegram setup instructions")
                                ai_msgs = get_ai_messages(page)
                                findings["sandbox_2"]["telegram_setup_msg"] = ai_msgs[-1] if ai_msgs else None
                                print(f"  Telegram setup: {ai_msgs[-1][:300] if ai_msgs else 'none'}")

            # Final state
            scan_for_witness(page, "sandbox2_post_payment")
            all_ai = get_ai_messages(page)
            findings["sandbox_2"]["complete_ai_history"] = all_ai
            print(f"\n  COMPLETE FLOW - {len(all_ai)} AI messages total")
            for i, m in enumerate(all_ai):
                print(f"    [{i+1}] {m[:120]}")

        ss(page, "s2_final", "Sandbox-2 final state")

        # ============================================================
        # PAY-TEST-2 FLOW (20s wait)
        # ============================================================
        print("\n\n" + "="*60)
        print("PAUSE: 20s before pay-test-2 (WAF protection)")
        print("="*60)
        time.sleep(20)

        print("\nPHASE 2: pay-test-2 (non-sandbox)")
        print("="*60)

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
        ss(page, "pt2_01_landing", "pay-test-2 landing - non-sandbox mode")
        scan_for_witness(page, "paytest2_initial")

        # Structural comparison
        pt2_structure = page.evaluate("""() => {
            return {
                title: document.title,
                url: window.location.href,
                has_sandbox_banner: document.body.innerText.includes('SANDBOX MODE'),
                has_sandbox_btn: !!document.querySelector('#pb-sandbox-bypass-btn'),
                has_proCta: !!document.querySelector('#proCta'),
                has_seeWhatBtn: !!document.querySelector('#seeWhatBtn'),
                has_post_payment: !!document.querySelector('#pay-test-post-payment'),
                paypal_plans: Array.from(document.querySelectorAll('[data-plan], [onclick*="PayPal"]'))
                    .map(b => ({id: b.id, text: b.innerText.trim().substring(0, 50), onclick: b.getAttribute('onclick') || ''}))
                    .slice(0, 10),
                sandbox_in_scripts: Array.from(document.querySelectorAll('script'))
                    .some(s => s.textContent.includes('pb-sandbox-bypass-btn'))
            };
        }""")
        print(f"\n  pay-test-2 structure: {json.dumps(pt2_structure, indent=2)}")
        findings["pay_test_2"]["structure"] = pt2_structure

        # Go through the same chat bypass flow
        begin_btn = page.locator(".chat-initial__btn")
        if begin_btn.count() > 0:
            begin_btn.first.click()
            time.sleep(3)
            ss(page, "pt2_02_chat_open", "pay-test-2 chat opened")

            user_input = page.locator("#userInput")
            if user_input.count() > 0:
                user_input.first.fill("pb-full-bypass")
                page.keyboard.press("Enter")
                time.sleep(20)
                ss(page, "pt2_03_after_bypass", "pay-test-2 after bypass")

            # Click discover
            js_click(page, "#seeWhatBtn", "discover on pay-test-2")
            time.sleep(20)
            ss(page, "pt2_04_after_discover", "pay-test-2 after DISCOVER - real PayPal CTAs")

            # Check PayPal button states on non-sandbox
            pt2_ctas = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('.pricing-card__cta, #proCta'))
                    .map(b => ({
                        id: b.id,
                        text: b.innerText.trim(),
                        onclick: b.getAttribute('onclick') || '',
                        visible: window.getComputedStyle(b.parentElement || b).display !== 'none'
                    }));
            }""")
            print(f"  pay-test-2 CTAs: {json.dumps(pt2_ctas, indent=2)}")
            findings["pay_test_2"]["cta_buttons"] = pt2_ctas

            # Check for sandbox bypass button (should NOT exist)
            has_sandbox_bypass = page.evaluate("() => !!document.querySelector('#pb-sandbox-bypass-btn')")
            print(f"  Has sandbox bypass btn: {has_sandbox_bypass} (expected: False)")
            findings["pay_test_2"]["has_sandbox_bypass"] = has_sandbox_bypass

            # Scroll to see pricing
            page.evaluate("window.scrollBy(0, 500)")
            time.sleep(2)
            ss(page, "pt2_05_pricing_real", "pay-test-2 real PayPal pricing - no sandbox bypass")

        # Script analysis for Witness keywords
        script_analysis = page.evaluate("""() => {
            const allScripts = Array.from(document.querySelectorAll('script')).map(s => s.textContent).join('\n');
            const lc = allScripts.toLowerCase();
            return {
                has_aiciv: lc.includes('aiciv'),
                has_witness: lc.includes('witness'),
                has_your_ai_ready: lc.includes('your ai is ready'),
                has_oauth: lc.includes('oauth'),
                has_portal_access: lc.includes('portal access'),
                aiciv_context: lc.includes('aiciv') ?
                    allScripts.substring(Math.max(0, allScripts.toLowerCase().indexOf('aiciv') - 100),
                                        allScripts.toLowerCase().indexOf('aiciv') + 200) : null,
                your_ai_context: lc.includes('your ai is ready') ?
                    allScripts.substring(Math.max(0, allScripts.toLowerCase().indexOf('your ai is ready') - 100),
                                        allScripts.toLowerCase().indexOf('your ai is ready') + 300) : null
            };
        }""")
        print(f"\n  Script Witness analysis: {json.dumps(script_analysis, indent=2)}")
        findings["pay_test_2"]["script_witness_analysis"] = script_analysis

        ss(page, "pt2_final", "pay-test-2 final state")

        browser.close()

    # Save
    report_path = Path("/home/jared/projects/AI-CIV/aether/exports/witness-chatflow-audit-20260224.json")
    with open(report_path, "w") as f:
        json.dump(findings, f, indent=2, default=str)

    print(f"\n[DONE] Report: {report_path}")
    print(f"Screenshots: {SCREENSHOT_DIR}")
    print(f"Total screenshots: {len(findings['screenshots'])}")
    print(f"Witness keywords: {len(findings['witness_keywords_found'])}")
    return findings


if __name__ == "__main__":
    result = main()

    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    print(f"Post-payment container exists: {result['sandbox_2'].get('post_payment_container', {}).get('exists')}")
    print(f"Role chosen: {result['sandbox_2'].get('role_chosen')}")
    print(f"Claude auth after role: {result['sandbox_2'].get('claude_auth_after_role')}")
    print(f"Witness keywords found: {result['witness_keywords_found']}")
    print(f"pay-test-2 has sandbox bypass: {result['pay_test_2'].get('has_sandbox_bypass')}")
    print(f"Script AiCIV in pay-test-2: {result['pay_test_2'].get('script_witness_analysis', {}).get('has_aiciv')}")
