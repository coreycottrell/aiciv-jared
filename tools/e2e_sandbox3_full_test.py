"""
E2E Full Birth Pipeline Test: pay-test-sandbox-3
Date: 2026-03-04
Agent: browser-vision-tester

Tests the complete flow from landing page to portal button.
Uses sandbox bypass (not real PayPal) since PayPal creds have been unreliable.
Captures screenshots at every major step.
Sends Telegram progress updates throughout.
"""

import asyncio
import time
import os
import subprocess
import json
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

TARGET_URL = "https://purebrain.ai/pay-test-sandbox-3/"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-e2e-20260304"
REPORT_PATH = "/home/jared/projects/AI-CIV/aether/exports/sandbox3-e2e-report-20260304.md"
TG_SEND = "/home/jared/projects/AI-CIV/aether/tools/tg_send.sh"

# Test data
TEST_NAME = "Test User"
TEST_EMAIL = "testuser@purebrain-test.com"
TEST_COMPANY = "PureBrain Test Co"
TEST_AI_NAME = "Sage"
TEST_ROLE = "CEO"
TEST_GOAL = "Grow my business with AI"

# PAYPAL SANDBOX CREDS (may or may not work)
PAYPAL_EMAIL = "sb-c89tj49549583@personal.example.com"
PAYPAL_PASSWORD = "Z0+6<dS"

screenshot_count = 0
findings = []
step_log = []


def tg(msg):
    """Send message to Telegram."""
    try:
        subprocess.run([TG_SEND, msg], capture_output=True, timeout=10)
    except Exception as e:
        print(f"[TG FAIL] {e}")


def log_step(step_num, description, status="OK", detail=""):
    """Log a test step."""
    entry = {
        "step": step_num,
        "description": description,
        "status": status,
        "detail": detail,
        "time": datetime.now().strftime("%H:%M:%S")
    }
    step_log.append(entry)
    icon = "PASS" if status == "OK" else ("FAIL" if status == "FAIL" else "INFO")
    print(f"[{icon}] Step {step_num}: {description}")
    if detail:
        print(f"       Detail: {detail}")


async def screenshot(page, label):
    """Take a screenshot and return path."""
    global screenshot_count
    screenshot_count += 1
    filename = f"{screenshot_count:03d}-{label}.png"
    path = os.path.join(SCREENSHOT_DIR, filename)
    await page.screenshot(path=path, full_page=False)
    print(f"[SCREENSHOT] {filename}")
    return path


async def wait_for_element(page, selector, timeout=30, state="visible"):
    """Wait for element with timeout."""
    try:
        await page.wait_for_selector(selector, timeout=timeout * 1000, state=state)
        return True
    except PlaywrightTimeout:
        return False


async def wait_ptc_input_active(page, timeout=90):
    """Poll for PTC input row to become active (display != none)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            display = await page.evaluate("""(function(){
                var row = document.getElementById('ptc-input-row');
                if (!row) return 'not-found';
                return window.getComputedStyle(row).display;
            })()""")
            if display not in ("none", "not-found"):
                return True
        except Exception:
            pass
        await asyncio.sleep(1)
    return False


async def ptc_send(page, text, timeout=15):
    """Type and send message in PTC chatbox."""
    try:
        ta = await page.query_selector("#ptc-input")
        if not ta:
            ta = await page.query_selector("textarea.ptc-input")
        if not ta:
            return False, "textarea not found"

        await ta.click(timeout=timeout * 1000)
        await asyncio.sleep(0.3)
        await ta.fill("")
        await asyncio.sleep(0.2)
        await ta.type(text, delay=30)
        await asyncio.sleep(0.5)

        send_btn = await page.query_selector("#ptc-send-btn")
        if send_btn and await send_btn.is_visible():
            await send_btn.click()
        else:
            await ta.press("Enter")
        return True, "sent"
    except PlaywrightTimeout:
        return False, "click timeout (likely OAuth overlay appeared)"
    except Exception as e:
        return False, str(e)


async def get_ai_messages(page):
    """Get all AI message texts from PTC."""
    try:
        msgs = await page.query_selector_all(".ptc-msg--ai")
        texts = []
        for m in msgs:
            t = await m.text_content()
            if t:
                texts.append(t.strip())
        return texts
    except Exception:
        return []


async def check_page_errors(page):
    """Check for console errors."""
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    return errors


async def run_e2e_test():
    """Main E2E test flow."""
    console_errors = []
    console_logs = []
    network_calls = []
    birth_api_calls = []

    print(f"\n{'='*60}")
    print(f"SANDBOX-3 E2E TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    tg("E2E Test: Step 1 - Launching browser, navigating to sandbox-3")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )

        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )

        page = await context.new_page()

        # Collect console messages
        page.on("console", lambda msg: console_logs.append(f"[{msg.type.upper()}] {msg.text}"))
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        # Collect network calls
        async def on_request(req):
            url = req.url
            if any(x in url for x in ["purebrain.ai/api", "log-pay-test", "log-conversation",
                                        "verify-payment", "birth/start", "birth/status",
                                        "seed", "intake"]):
                network_calls.append({"url": url, "method": req.method, "time": time.time()})
                if "birth" in url.lower():
                    birth_api_calls.append({"url": url, "method": req.method, "time": time.time()})

        page.on("request", on_request)

        # ============================================================
        # STEP 1: Navigate to pay-test-sandbox-3
        # ============================================================
        log_step(1, "Navigate to pay-test-sandbox-3")
        await page.goto(TARGET_URL, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        title = await page.title()
        url_now = page.url
        log_step(1, f"Page loaded", "OK", f"Title: {title} | URL: {url_now}")

        ss1 = await screenshot(page, "01-landing-page")

        # ============================================================
        # STEP 2: Check page structure
        # ============================================================
        log_step(2, "Inspect page structure")

        page_state = await page.evaluate("""(function(){
            var result = {};
            // Check for password gate
            result.passwordGate = !!document.getElementById('pb-password-gate') ||
                                   !!document.querySelector('.pb-password-gate') ||
                                   !!document.querySelector('[class*="password-gate"]');
            // Check for hero section
            result.hasHero = !!document.querySelector('.hero-section, .pb-hero, #pb-hero');
            // Check for pricing
            result.hasPricing = !!document.querySelector('.pricing-section, #pricing, [class*="pricing"]');
            // Check for PayPal buttons
            result.hasPaypal = !!document.querySelector('.paypal-button, [data-funding-source], iframe[name*="paypal"]');
            // Check for PTC container
            result.ptcContainer = !!document.getElementById('pay-test-post-payment');
            // Check for chatbox visible
            result.ptcVisible = false;
            var ptc = document.getElementById('pay-test-post-payment');
            if (ptc) {
                result.ptcVisible = window.getComputedStyle(ptc).display !== 'none';
                result.ptcChildren = ptc.children.length;
            }
            // Check key buttons
            result.beginAwakeningBtn = !!document.querySelector('button[onclick*="beginAwakening"], .begin-awakening, #begin-awakening-btn');
            result.bypassBtn = !!document.querySelector('.pb-sandbox-bypass-btn, [onclick*="bypass"], #bypass-btn');
            // Check page title text
            result.h1Text = document.querySelector('h1') ? document.querySelector('h1').textContent.trim().substring(0,100) : 'none';
            // Check for errors in DOM
            result.errorElements = document.querySelectorAll('[class*="error"], [class*="Error"]').length;
            return result;
        })()""")

        log_step(2, "Page structure", "INFO", json.dumps(page_state, indent=2))

        # ============================================================
        # STEP 3: Handle password gate if present
        # ============================================================
        password_gate_present = page_state.get("passwordGate", False)

        if password_gate_present:
            log_step(3, "Password gate detected - entering bypass code")
            tg("E2E Test: Step 3 - Password gate found, entering bypass code")

            pw_input = await page.query_selector("input[type='password'], input[name='password'], #pb-password-input")
            if pw_input:
                await pw_input.fill("pb-full-bypass")
                await pw_input.press("Enter")
                await asyncio.sleep(2)
                ss3 = await screenshot(page, "03-after-password")
                log_step(3, "Bypass code entered", "OK", "pw-full-bypass submitted")
            else:
                log_step(3, "Password input not found despite gate detection", "FAIL")
        else:
            log_step(3, "No password gate detected - page is open access", "INFO")
            ss3 = await screenshot(page, "03-no-password-gate")

        # ============================================================
        # STEP 4: Look for Begin Awakening button or pricing section
        # ============================================================
        await asyncio.sleep(2)
        log_step(4, "Looking for Begin Awakening button / CTA")
        tg("E2E Test: Step 4 - Looking for CTA buttons")

        # Check all buttons on page
        buttons_info = await page.evaluate("""(function(){
            var btns = Array.from(document.querySelectorAll('button, a.btn, [role="button"]'));
            return btns.slice(0, 20).map(function(b) {
                return {
                    tag: b.tagName,
                    text: b.textContent.trim().substring(0,80),
                    id: b.id || '',
                    className: b.className ? b.className.toString().substring(0,60) : '',
                    onclick: b.getAttribute('onclick') ? b.getAttribute('onclick').substring(0,80) : '',
                    visible: b.offsetParent !== null
                };
            });
        })()""")

        log_step(4, f"Found {len(buttons_info)} buttons/CTAs", "INFO", str(buttons_info[:5]))

        ss4 = await screenshot(page, "04-page-with-buttons")

        # Try to click Begin Awakening
        begin_clicked = False
        for sel in [
            "#begin-awakening-btn",
            "button[onclick*='beginAwakening']",
            ".begin-awakening",
            "button.proCta",
            ".proCta",
        ]:
            elem = await page.query_selector(sel)
            if elem and await elem.is_visible():
                log_step(4, f"Clicking Begin Awakening: {sel}", "OK")
                await elem.click()
                begin_clicked = True
                await asyncio.sleep(2)
                break

        if not begin_clicked:
            # Try text-based matching
            for btn_text in ["Begin Awakening", "GET STARTED", "Awaken", "Choose Plan", "Select"]:
                try:
                    btn = page.get_by_text(btn_text, exact=False)
                    if await btn.count() > 0:
                        await btn.first.click()
                        begin_clicked = True
                        log_step(4, f"Clicked button by text: {btn_text}", "OK")
                        await asyncio.sleep(2)
                        break
                except Exception:
                    pass

        if not begin_clicked:
            log_step(4, "No Begin Awakening button found - checking for PayPal direct", "INFO")

        ss4b = await screenshot(page, "04b-after-cta-click")

        # ============================================================
        # STEP 5: Look for PayPal modal or direct PayPal buttons
        # ============================================================
        log_step(5, "Checking for PayPal modal or buttons")
        tg("E2E Test: Step 5 - Looking for PayPal payment UI")
        await asyncio.sleep(2)

        # Check for modal/PayPal
        modal_state = await page.evaluate("""(function(){
            var result = {};
            // Check for PayPal iframes
            var frames = document.querySelectorAll('iframe');
            result.iframeCount = frames.length;
            result.iframeNames = Array.from(frames).map(f => (f.name || f.src || '').substring(0,80));
            // Check for modal overlays
            result.hasModal = !!document.querySelector('.pb-modal, [class*="modal"], [id*="modal"]');
            // Check for bypass button
            result.hasBypass = !!document.querySelector('.pb-sandbox-bypass-btn, [class*="sandbox-bypass"]');
            // Check for PayPal button container
            result.hasPaypalContainer = !!document.querySelector('#paypal-button-container, .paypal-button-container');
            // Check for sandbox bypass button
            var bypassBtns = Array.from(document.querySelectorAll('button')).filter(b =>
                b.textContent.includes('bypass') || b.textContent.includes('Bypass') ||
                b.textContent.includes('Skip') || b.textContent.includes('sandbox'));
            result.bypassBtnTexts = bypassBtns.map(b => b.textContent.trim().substring(0,60));
            return result;
        })()""")

        log_step(5, "PayPal/Modal state", "INFO", json.dumps(modal_state, indent=2))
        ss5 = await screenshot(page, "05-paypal-modal-state")

        # ============================================================
        # STEP 6: Try sandbox bypass if available
        # ============================================================
        bypass_clicked = False
        log_step(6, "Attempting sandbox bypass click")
        tg("E2E Test: Step 6 - Attempting sandbox bypass")

        for sel in [
            ".pb-sandbox-bypass-btn",
            "button[class*='sandbox-bypass']",
            "button[onclick*='bypass']",
            "button[onclick*='simulatePayment']",
            "button[onclick*='onPaymentComplete']",
        ]:
            elem = await page.query_selector(sel)
            if elem:
                visible = await elem.is_visible()
                log_step(6, f"Found bypass button: {sel}, visible={visible}", "INFO")
                if visible:
                    await elem.click()
                    bypass_clicked = True
                    log_step(6, f"Sandbox bypass clicked: {sel}", "OK")
                    await asyncio.sleep(3)
                    break

        if not bypass_clicked:
            # Try text-based
            for bypass_text in ["sandbox", "bypass", "Bypass", "Skip Payment", "Test Payment"]:
                try:
                    btns = await page.query_selector_all("button")
                    for btn in btns:
                        txt = await btn.text_content()
                        if txt and bypass_text.lower() in txt.lower():
                            visible = await btn.is_visible()
                            if visible:
                                log_step(6, f"Bypass button found by text: '{txt.strip()}'", "OK")
                                await btn.click()
                                bypass_clicked = True
                                await asyncio.sleep(3)
                                break
                    if bypass_clicked:
                        break
                except Exception as e:
                    log_step(6, f"Bypass text search error: {e}", "INFO")

        if not bypass_clicked:
            # Try using PayPal sandbox login
            log_step(6, "No bypass found - trying PayPal sandbox login", "INFO")
            tg("E2E Test: Step 6 - No bypass button, attempting PayPal sandbox login")

            # Look for PayPal button frame
            frames = page.frames
            paypal_frame = None
            for frame in frames:
                frame_url = frame.url
                if "paypal.com" in frame_url and "button" in frame_url.lower():
                    paypal_frame = frame
                    break

            if paypal_frame:
                try:
                    pp_btn = await paypal_frame.query_selector(".paypal-button, [data-funding-source='paypal'] button")
                    if pp_btn:
                        await pp_btn.click()
                        log_step(6, "PayPal button clicked in iframe", "OK")
                        await asyncio.sleep(5)
                        bypass_clicked = True
                except Exception as e:
                    log_step(6, f"PayPal iframe click failed: {e}", "FAIL")

        ss6 = await screenshot(page, "06-after-bypass-attempt")

        # ============================================================
        # STEP 7: Check for PTC (Post-payment chatbox) appearance
        # ============================================================
        log_step(7, "Waiting for post-payment chatbox (PTC) to appear")
        tg("E2E Test: Step 7 - Waiting for post-payment chatbox")

        ptc_appeared = await wait_ptc_input_active(page, timeout=90)

        if ptc_appeared:
            log_step(7, "PTC chatbox appeared and is active", "OK")
        else:
            log_step(7, "PTC chatbox did NOT appear within 90 seconds", "FAIL")

        ss7 = await screenshot(page, "07-ptc-state")

        # Check PTC state in detail
        ptc_state = await page.evaluate("""(function(){
            var result = {};
            var container = document.getElementById('pay-test-post-payment');
            result.containerExists = !!container;
            if (container) {
                result.containerDisplay = window.getComputedStyle(container).display;
                result.containerChildren = container.children.length;
                result.containerHTML = container.innerHTML.substring(0, 500);
            }
            var inputRow = document.getElementById('ptc-input-row');
            result.inputRowExists = !!inputRow;
            if (inputRow) {
                result.inputRowDisplay = window.getComputedStyle(inputRow).display;
            }
            var textarea = document.getElementById('ptc-input');
            result.textareaExists = !!textarea;
            // Check for OAuth elements
            result.hasOAuthButton = !!document.querySelector('[class*="oauth"], [onclick*="oauth"], [href*="oauth"], [href*="claude.ai"]');
            // Check for "ENTER BRAIN STREAM" portal button
            result.hasPortalButton = !!document.querySelector('.ptc-portal-btn, [class*="portal-btn"], [class*="brain-stream"]');
            // Check for any visible error messages
            var errors = Array.from(document.querySelectorAll('.ptc-msg--ai, .ptc-message')).filter(el =>
                el.textContent.toLowerCase().includes('error'));
            result.errorMessages = errors.map(e => e.textContent.trim().substring(0,100));
            // Check what messages are visible in PTC
            var aiMsgs = document.querySelectorAll('.ptc-msg--ai');
            result.aiMessageCount = aiMsgs.length;
            result.firstAiMessage = aiMsgs.length > 0 ? aiMsgs[0].textContent.trim().substring(0,200) : '';
            return result;
        })()""")

        log_step(7, "PTC detailed state", "INFO", json.dumps(ptc_state, indent=2))

        # ============================================================
        # STEP 8: Document first chatbox question
        # ============================================================
        log_step(8, "Reading first chatbox question/message")

        if ptc_state.get("containerExists") and ptc_state.get("aiMessageCount", 0) > 0:
            first_msg = ptc_state.get("firstAiMessage", "")
            log_step(8, f"First AI message: '{first_msg}'", "OK")
        else:
            log_step(8, "No AI messages visible in PTC", "INFO" if not ptc_appeared else "FAIL")

        # ============================================================
        # STEP 9: Complete Q&A flow if PTC is active
        # ============================================================
        qa_results = {}

        if ptc_appeared:
            tg("E2E Test: Step 9 - PTC active! Completing Q&A flow")
            log_step(9, "Starting Q&A flow")

            # Wait for first AI message to settle
            await asyncio.sleep(3)

            ss9 = await screenshot(page, "09-ptc-first-question")

            # Get initial messages
            initial_msgs = await get_ai_messages(page)
            log_step(9, f"Initial AI messages: {initial_msgs}", "INFO")

            # Answer 1: Name (or AI name - depends on flow)
            log_step(9, "Sending test name/AI name")
            ok, detail = await ptc_send(page, TEST_AI_NAME)
            qa_results["q1_name"] = {"sent": TEST_AI_NAME, "ok": ok, "detail": detail}
            log_step(9, f"Name sent: {ok} - {detail}", "OK" if ok else "FAIL")
            await asyncio.sleep(3)
            ss9b = await screenshot(page, "09b-after-name")

            msgs_after_name = await get_ai_messages(page)
            log_step(9, f"Messages after name: {msgs_after_name}", "INFO")

            # Answer 2: Email
            log_step(9, "Sending test email")
            ok, detail = await ptc_send(page, TEST_EMAIL)
            qa_results["q2_email"] = {"sent": TEST_EMAIL, "ok": ok, "detail": detail}
            log_step(9, f"Email sent: {ok} - {detail}", "OK" if ok else "FAIL")
            await asyncio.sleep(3)
            ss9c = await screenshot(page, "09c-after-email")

            msgs_after_email = await get_ai_messages(page)
            log_step(9, f"Messages after email: {msgs_after_email}", "INFO")

            # Answer 3: Company
            log_step(9, "Sending test company")
            ok, detail = await ptc_send(page, TEST_COMPANY)
            qa_results["q3_company"] = {"sent": TEST_COMPANY, "ok": ok, "detail": detail}
            log_step(9, f"Company sent: {ok} - {detail}", "OK" if ok else "FAIL")
            await asyncio.sleep(3)
            ss9d = await screenshot(page, "09d-after-company")

            # Answer 4: Role (this triggers BIRTH on sandbox-2)
            log_step(9, "Sending role - this may trigger BIRTH API")
            ok, detail = await ptc_send(page, TEST_ROLE)
            qa_results["q4_role"] = {"sent": TEST_ROLE, "ok": ok, "detail": detail}
            log_step(9, f"Role sent: {ok} - {detail}", "OK" if ok else "FAIL")
            await asyncio.sleep(5)
            ss9e = await screenshot(page, "09e-after-role-birth-trigger")
            tg(f"E2E Test: Step 9 - Role sent. Birth API may have triggered. Checking state...")

            # Check if OAuth overlay appeared after role
            post_role_state = await page.evaluate("""(function(){
                var result = {};
                // Check for OAuth/authorization buttons
                result.oauthButtonText = '';
                var btns = Array.from(document.querySelectorAll('button, a'));
                var oauthBtn = btns.find(b =>
                    b.textContent.includes('Authorize') ||
                    b.textContent.includes('OAuth') ||
                    b.textContent.includes('I have my key') ||
                    b.textContent.includes('claude.ai'));
                if (oauthBtn) {
                    result.oauthButtonText = oauthBtn.textContent.trim();
                    result.oauthButtonHref = oauthBtn.href || oauthBtn.getAttribute('onclick') || '';
                }
                // Check all AI messages now
                var aiMsgs = document.querySelectorAll('.ptc-msg--ai');
                result.allAiMessages = Array.from(aiMsgs).map(m => m.textContent.trim().substring(0,200));
                // Check for portal button
                result.portalBtn = !!document.querySelector('.ptc-portal-btn, [class*="portal-btn"]');
                result.portalBtnHref = '';
                var pb = document.querySelector('.ptc-portal-btn, [class*="portal-btn"]');
                if (pb) {
                    result.portalBtnHref = pb.href || pb.getAttribute('onclick') || pb.getAttribute('data-href') || '';
                    result.portalBtnText = pb.textContent.trim();
                    result.portalBtnDisabled = pb.disabled || pb.classList.contains('disabled') || pb.style.opacity < 1;
                }
                // Check input row state
                var inputRow = document.getElementById('ptc-input-row');
                result.inputRowDisplay = inputRow ? window.getComputedStyle(inputRow).display : 'not found';
                return result;
            })()""")

            log_step(9, "Post-role state", "INFO", json.dumps(post_role_state, indent=2))

            # Answer 5: Goal (may fail if OAuth overlay appeared)
            log_step(9, "Sending goal (may fail if OAuth gate active)")
            ok, detail = await ptc_send(page, TEST_GOAL)
            qa_results["q5_goal"] = {"sent": TEST_GOAL, "ok": ok, "detail": detail}
            log_step(9, f"Goal sent: {ok} - {detail}", "OK" if ok else "INFO")
            await asyncio.sleep(5)
            ss9f = await screenshot(page, "09f-after-goal")

        else:
            log_step(9, "Skipping Q&A - PTC never became active", "FAIL")
            tg("E2E Test: FAIL - PTC did not appear. Cannot complete Q&A flow.")

        # ============================================================
        # STEP 10: Check for OAuth step in chatbox
        # ============================================================
        log_step(10, "Checking for OAuth step in chatbox flow")
        tg("E2E Test: Step 10 - Checking for OAuth elements")

        oauth_state = await page.evaluate("""(function(){
            var result = {};
            // All button texts
            var allBtns = Array.from(document.querySelectorAll('button, a[role="button"]'));
            result.allButtonTexts = allBtns.map(b => ({
                text: b.textContent.trim().substring(0,80),
                visible: b.offsetParent !== null,
                href: b.href || b.getAttribute('href') || ''
            })).filter(b => b.text.length > 0);

            // Check for OAuth URL displays
            var allText = document.body.innerText;
            result.hasClaudeAiUrl = allText.includes('claude.ai');
            result.hasOAuthUrl = allText.includes('oauth') || allText.includes('OAuth');
            result.hasAuthorize = allText.includes('Authorize');
            result.hasPortalUrl = allText.includes('purebrain.ai/portal') || allText.includes('/portal/');

            // Find OAuth URL if displayed
            var urlPattern = /https:\/\/claude\.ai[^\s"'<>]*/g;
            var matches = allText.match(urlPattern);
            result.claudeAiUrls = matches ? matches.slice(0,3) : [];

            // Check for "I have my key" button
            result.hasIHaveMyKey = !!document.querySelector('button, a').textContent;
            var iHaveKeyBtn = Array.from(document.querySelectorAll('button, a')).find(b =>
                b.textContent.includes('I have my key') || b.textContent.includes('have my key'));
            result.iHaveKeyBtn = iHaveKeyBtn ? iHaveKeyBtn.textContent.trim() : null;

            // Portal button state
            var ptcPortal = document.querySelector('.ptc-portal-btn');
            if (ptcPortal) {
                result.portalButton = {
                    exists: true,
                    text: ptcPortal.textContent.trim(),
                    href: ptcPortal.href || '',
                    disabled: ptcPortal.disabled,
                    opacity: window.getComputedStyle(ptcPortal).opacity,
                    display: window.getComputedStyle(ptcPortal).display,
                    classes: ptcPortal.className
                };
            } else {
                result.portalButton = { exists: false };
            }

            return result;
        })()""")

        log_step(10, "OAuth/portal state", "INFO", json.dumps(oauth_state, indent=2))
        ss10 = await screenshot(page, "10-oauth-portal-state")

        # ============================================================
        # STEP 11: Check birth polling / status
        # ============================================================
        log_step(11, "Checking birth polling behavior")
        tg("E2E Test: Step 11 - Checking birth polling and portal button state")

        # Wait a bit and see if status changes
        await asyncio.sleep(10)
        ss11 = await screenshot(page, "11-after-birth-polling-wait")

        birth_poll_state = await page.evaluate("""(function(){
            var result = {};
            // Check if birth polling JS is running
            result.birthPollFn = typeof window.checkBirthStatus;
            result.pollBirthFn = typeof window.pollBirthStatus;
            // Check birth-related window state
            result.birthOrderId = window.birthOrderId || window.currentBirthOrderId || null;
            result.birthStatus = window.birthStatus || window.currentBirthStatus || null;
            result.portalUrl = window.portalUrl || window.currentPortalUrl || null;
            // Check for any visible status messages
            var statusEls = document.querySelectorAll('[class*="status"], [class*="birth-status"], [id*="birth-status"]');
            result.statusElements = Array.from(statusEls).map(el => ({
                text: el.textContent.trim().substring(0,100),
                display: window.getComputedStyle(el).display
            }));
            // All AI messages at this point
            var aiMsgs = document.querySelectorAll('.ptc-msg--ai');
            result.totalAiMessages = aiMsgs.length;
            result.lastAiMessage = aiMsgs.length > 0 ? aiMsgs[aiMsgs.length-1].textContent.trim().substring(0,300) : '';
            // Portal button final state
            var pb = document.querySelector('.ptc-portal-btn');
            if (pb) {
                result.portalBtn = {
                    text: pb.textContent.trim(),
                    href: pb.href || '',
                    disabled: pb.disabled,
                    opacity: window.getComputedStyle(pb).opacity,
                    visible: pb.offsetParent !== null,
                    classes: pb.className
                };
            }
            return result;
        })()""")

        log_step(11, "Birth poll state", "INFO", json.dumps(birth_poll_state, indent=2))

        # ============================================================
        # STEP 12: Final state capture
        # ============================================================
        log_step(12, "Final state capture")
        tg("E2E Test: Step 12 - Capturing final state")

        await asyncio.sleep(5)
        ss12 = await screenshot(page, "12-final-state")

        final_state = await page.evaluate("""(function(){
            var result = {};
            // Full page button inventory
            var btns = Array.from(document.querySelectorAll('button, a[href], [role="button"]'));
            result.allButtons = btns.filter(b => b.offsetParent !== null).map(b => ({
                text: b.textContent.trim().substring(0,60),
                tag: b.tagName,
                href: b.href || '',
                disabled: b.disabled || false,
                classes: b.className ? b.className.toString().substring(0,60) : ''
            })).filter(b => b.text.length > 0).slice(0, 15);

            // Portal button specifics
            var pb = document.querySelector('.ptc-portal-btn, [class*="portal-btn"], [class*="brain-stream"]');
            result.portalBtn = pb ? {
                text: pb.textContent.trim(),
                href: pb.href || pb.dataset.href || '',
                onclick: pb.getAttribute('onclick') || '',
                disabled: pb.disabled,
                opacity: window.getComputedStyle(pb).opacity,
                classes: pb.className
            } : null;

            // All chat messages
            var aiMsgs = Array.from(document.querySelectorAll('.ptc-msg--ai'));
            result.allAiMessages = aiMsgs.map(m => m.textContent.trim().substring(0,200));
            result.userMessages = Array.from(document.querySelectorAll('.ptc-msg--user')).map(m => m.textContent.trim());

            return result;
        })()""")

        log_step(12, "Final complete state", "INFO", json.dumps(final_state, indent=2))

        # ============================================================
        # STEP 13: Compile console errors and network calls
        # ============================================================
        log_step(13, "Compiling console errors and network calls")

        log_step(13, f"Console errors ({len(console_errors)})", "INFO", str(console_errors[:10]))
        log_step(13, f"Network API calls ({len(network_calls)})", "INFO",
                 str([c["url"].split("?")[0].split("/")[-1] for c in network_calls]))
        log_step(13, f"Birth API calls ({len(birth_api_calls)})", "INFO",
                 str([c["url"] for c in birth_api_calls]))

        await browser.close()

    # ============================================================
    # Build Report
    # ============================================================
    return {
        "step_log": step_log,
        "qa_results": qa_results,
        "console_errors": console_errors,
        "console_logs": [l for l in console_logs if "ERROR" in l or "warn" in l.lower()][:30],
        "network_calls": network_calls,
        "birth_api_calls": birth_api_calls,
        "final_state": final_state,
        "birth_poll_state": birth_poll_state,
        "oauth_state": oauth_state,
        "ptc_state": ptc_state,
        "ptc_appeared": ptc_appeared,
        "bypass_clicked": bypass_clicked,
        "screenshot_count": screenshot_count,
    }


async def main():
    print("[START] E2E Sandbox-3 Full Test")

    try:
        results = await run_e2e_test()

        # Build markdown report
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ptc = results.get("ptc_appeared", False)
        bypass = results.get("bypass_clicked", False)
        errors = results.get("console_errors", [])
        birth_calls = results.get("birth_api_calls", [])
        final = results.get("final_state", {})
        oauth = results.get("oauth_state", {})

        portal_btn = final.get("portalBtn")
        ai_messages = final.get("allAiMessages", [])
        all_buttons = final.get("allButtons", [])

        # Determine key findings
        has_oauth = oauth.get("hasClaudeAiUrl") or oauth.get("hasAuthorize")
        portal_exists = portal_btn is not None
        portal_href = portal_btn.get("href", "") if portal_btn else ""
        portal_disabled = portal_btn.get("disabled") if portal_btn else None

        report = f"""# Sandbox-3 E2E Full Test Report

**Date**: {now}
**Agent**: browser-vision-tester
**Target**: https://purebrain.ai/pay-test-sandbox-3/
**Screenshots**: {results["screenshot_count"]} captured in `exports/screenshots/sandbox3-e2e-20260304/`

---

## Executive Summary

| Check | Result |
|-------|--------|
| Page loads | {"PASS" if True else "FAIL"} |
| Sandbox bypass available | {"PASS" if bypass else "FAIL - no bypass button found"} |
| PTC chatbox appeared | {"PASS" if ptc else "FAIL - chatbox did not appear"} |
| Console errors | {"FAIL - " + str(len(errors)) + " errors" if errors else "PASS - 0 errors"} |
| Birth API called | {"PASS - " + str(len(birth_calls)) + " calls" if birth_calls else "INFO - not triggered"} |
| OAuth step in chatbox | {"YES - found" if has_oauth else "NO - not found"} |
| Portal button present | {"YES" if portal_exists else "NO"} |

---

## Step-by-Step Flow

"""
        for step in results["step_log"]:
            icon = "[PASS]" if step["status"] == "OK" else ("[FAIL]" if step["status"] == "FAIL" else "[INFO]")
            report += f"**Step {step['step']}** ({step['time']}): {step['description']}\n"
            report += f"- Status: {icon} {step['status']}\n"
            if step.get("detail") and len(step["detail"]) < 300:
                report += f"- Detail: `{step['detail']}`\n"
            report += "\n"

        report += f"""---

## Key Findings

### 1. OAuth Step Analysis
- Claude.ai URL displayed: **{oauth.get("hasClaudeAiUrl", False)}**
- "Authorize" text visible: **{oauth.get("hasAuthorize", False)}**
- "I have my key" button: **{oauth.get("iHaveKeyBtn", "not found")}**
- Claude.ai URLs found: {oauth.get("claudeAiUrls", [])}

### 2. Portal Button State
"""
        if portal_btn:
            report += f"""- Exists: **YES**
- Text: `{portal_btn.get("text", "")}`
- href: `{portal_btn.get("href", "")}`
- onclick: `{portal_btn.get("onclick", "")}`
- Disabled: `{portal_btn.get("disabled")}`
- Opacity: `{portal_btn.get("opacity")}`
- Classes: `{portal_btn.get("classes", "")}`
"""
        else:
            report += "- Exists: **NO** - Portal button was not found in DOM at test completion\n"

        report += f"""
### 3. Chat Flow Q&A Results
"""
        for q, data in results.get("qa_results", {}).items():
            report += f"- **{q}**: Sent `{data.get('sent')}` -> {data.get('ok')} ({data.get('detail')})\n"

        report += f"""
### 4. All AI Messages in Chatbox
"""
        for i, msg in enumerate(ai_messages):
            report += f"{i+1}. \"{msg}\"\n"

        if not ai_messages:
            report += "- No AI messages captured\n"

        report += f"""
### 5. Birth API Calls
"""
        for call in birth_calls:
            report += f"- `{call['url']}` ({call['method']})\n"
        if not birth_calls:
            report += "- No birth API calls captured\n"

        report += f"""
### 6. Console Errors
"""
        for err in errors[:10]:
            report += f"- `{err}`\n"
        if not errors:
            report += "- No console errors\n"

        report += f"""
### 7. All Visible Buttons at Test End
"""
        for btn in all_buttons:
            report += f"- `{btn.get('tag')}` '{btn.get('text')}' href='{btn.get('href', '')}' disabled={btn.get('disabled')}\n"

        report += f"""
---

## Network API Calls
"""
        for call in results.get("network_calls", []):
            report += f"- `{call['method']} {call['url'].split('?')[0]}`\n"

        report += f"""
---

## Screenshots
All {results["screenshot_count"]} screenshots at:
`/home/jared/projects/AI-CIV/aether/exports/screenshots/sandbox3-e2e-20260304/`

Key screenshots:
- `001-landing-page.png` - Initial page load
- `05-paypal-modal-state.png` - PayPal/modal state
- `07-ptc-state.png` - PTC chatbox state
- `09e-after-role-birth-trigger.png` - After role (birth trigger point)
- `10-oauth-portal-state.png` - OAuth/portal button state
- `12-final-state.png` - Final page state

---

## What This Tells Witness

Based on this test:
1. **OAuth removal status**: {"OAuth elements STILL PRESENT in chatbox flow" if has_oauth else "OAuth elements NOT FOUND - appears removed"}
2. **Birth polling**: See birth_poll_state in JSON dump
3. **Portal button trigger**: {"Requires OAuth completion (Stage 3)" if not portal_exists else "Present - href: " + portal_href}
4. **Chatbox birth questions**: {len(ai_messages)} questions asked: {ai_messages[:3] if ai_messages else "none captured"}

---

*Generated by browser-vision-tester*
*Test run: {now}*
"""

        with open(REPORT_PATH, "w") as f:
            f.write(report)

        print(f"\n[REPORT] Written to: {REPORT_PATH}")
        print(f"[SCREENSHOTS] {results['screenshot_count']} files in: {SCREENSHOT_DIR}")

        # Send summary to Telegram
        summary = f"""E2E Test COMPLETE - Sandbox-3 Results:
- Bypass found: {bypass}
- PTC chatbox: {ptc}
- Console errors: {len(errors)}
- Birth API calls: {len(birth_calls)}
- OAuth in flow: {has_oauth}
- Portal button: {portal_exists} (href: {portal_href[:60] if portal_href else 'none'})
- AI messages: {len(ai_messages)}
- Screenshots: {results["screenshot_count"]}
Full report: exports/sandbox3-e2e-report-20260304.md"""

        tg(summary)

        return results, REPORT_PATH

    except Exception as e:
        error_msg = f"E2E Test CRASHED: {type(e).__name__}: {e}"
        print(f"[CRASH] {error_msg}")
        tg(f"E2E Test: CRASH - {error_msg}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    asyncio.run(main())
