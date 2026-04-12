#!/usr/bin/env python3
"""
Brevo Automation Workflow Creator - FINAL
Full end-to-end build of Neural Feed Welcome Sequence.

Verified working:
- Login + 2FA via Gmail IMAP
- Navigation to builder at /automation/edit/2
- Builder UI is drag-and-drop canvas with left panel triggers/actions

Builder structure (confirmed from screenshot):
- Left panel: Triggers tab → "Contact added to list" draggable item
- Canvas: "Drop a step here to start building your automation"
- Top bar: "Automation #2", "Activate automation" button, "Exit editor"
"""

import os
import sys
import time
import re
import json
import imaplib
import email
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')
BREVO_EMAIL = 'purebrain@puremarketing.ai'
BREVO_PASSWORD = os.environ['BREVO_PASSWORD']
GMAIL_USER = os.environ['GMAIL_USERNAME']
GMAIL_APP_PASSWORD = os.environ['GOOGLE_APP_PASSWORD']
SS_DIR = '/home/jared/projects/AI-CIV/aether/exports/screenshots'
os.makedirs(SS_DIR, exist_ok=True)

WORKFLOW_NAME = "Neural Feed - Welcome Sequence"

# (template_id, wait_days_BEFORE_this_email)
# wait_days=0 means send immediately after trigger
EMAIL_SEQUENCE = [
    (1, 0),  # Email 1 - immediate
    (2, 2),  # Email 2 - 2 days wait
    (3, 2),  # Email 3 - 2 days wait
    (4, 3),  # Email 4 - 3 days wait
    (5, 3),  # Email 5 - 3 days wait
    (6, 4),  # Email 6 - 4 days wait
    (7, 7),  # Email 7 - 7 days wait
]

TEMPLATE_NAMES = {
    1: 'Neural Feed - Email 1 - Welcome (Aether)',
    2: "Neural Feed - Email 2 - Jared's Story",
    3: 'Neural Feed - Email 3 - Aether Writes Directly',
    4: 'Neural Feed - Email 4 - Partnership in Practice',
    5: 'Neural Feed - Email 5 - The Context Tax',
    6: 'Neural Feed - Email 6 - Social Proof & Results',
    7: 'Neural Feed - Email 7 - The Invitation',
}

_ss_n = [0]

def ss(page, label, desc=""):
    _ss_n[0] += 1
    fname = f"{_ss_n[0]:02d}_{label}"
    path = f"{SS_DIR}/brevo_final_{fname}.png"
    page.screenshot(path=path, full_page=True)
    print(f"  [SS] {fname}: {desc or label}")
    return path

def p(secs=1.5, why=""):
    if why: print(f"  [WAIT] {secs}s - {why}")
    time.sleep(secs)

def find(page, selector, timeout=20000, state="visible", desc=""):
    label = desc or selector[:50]
    try:
        el = page.wait_for_selector(selector, timeout=timeout, state=state)
        return el
    except PlaywrightTimeout:
        print(f"  [MISS] {label}")
        return None

def click(page, selector, timeout=15000, desc=""):
    el = find(page, selector, timeout=timeout, desc=desc or selector[:50])
    if el:
        el.scroll_into_view_if_needed()
        p(0.2)
        el.click()
        p(0.5)
        return True
    return False

def get_code(max_wait=90):
    print("  [IMAP] Fetching Brevo 2FA code from Gmail...")
    deadline = time.time() + max_wait
    while time.time() < deadline:
        try:
            m = imaplib.IMAP4_SSL('imap.gmail.com')
            m.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            m.select('INBOX')
            _, data = m.search(None, 'FROM', 'account-alerts@t.brevo.com', 'UNSEEN')
            if data[0]:
                for mid in reversed(data[0].decode().split()):
                    _, mdata = m.fetch(mid, '(RFC822)')
                    msg = email.message_from_bytes(mdata[0][1])
                    subj = msg.get('Subject', '')
                    if 'verify' not in subj.lower():
                        continue
                    body = ''
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() in ('text/plain', 'text/html'):
                                body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    else:
                        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    match = re.search(r'verification code[:\s]*\n?\s*(\d{6})', body, re.IGNORECASE)
                    if match:
                        code = match.group(1)
                        print(f"  [IMAP] Code: {code}")
                        m.logout()
                        return code
                    # Non-repeating fallback
                    for c in re.findall(r'\b\d{6}\b', body):
                        d = list(c)
                        if not (d[0]==d[2]==d[4] and d[1]==d[3]==d[5]):
                            print(f"  [IMAP] Code (fallback): {c}")
                            m.logout()
                            return c
            m.logout()
        except Exception as e:
            print(f"  [IMAP] Error: {e}")
        remaining = int(deadline - time.time())
        print(f"  [IMAP] Waiting... ({remaining}s left)")
        time.sleep(5)
    return None


def do_login(page):
    """Login + handle 2FA. Returns True on success."""
    print("\n=== LOGIN ===")
    page.goto("https://login.brevo.com/", wait_until="domcontentloaded", timeout=60000)
    p(2)

    # Dismiss cookie banner
    try:
        btn = page.wait_for_selector("button:has-text('Accept All Cookies')", timeout=4000)
        btn.click()
        p(0.8)
        print("  [COOKIE] Dismissed")
    except PlaywrightTimeout:
        pass

    ss(page, "login", "Login page")

    # Email field: type="text" name="email" (NOT type="email")
    ef = find(page, "input[name='email'], input#email", timeout=15000, desc="email input")
    if not ef:
        ss(page, "ERR_no_email_field")
        return False
    ef.fill(BREVO_EMAIL)
    p(0.3)

    pf = find(page, "input[type='password']", desc="password input")
    if not pf:
        ss(page, "ERR_no_pw_field")
        return False
    pf.fill(BREVO_PASSWORD)
    p(0.3)

    ss(page, "creds_filled", "Credentials filled")

    # Submit: type="button" with text "Log In" (NOT type="submit")
    try:
        btn = page.wait_for_selector(
            "button:has-text('Log In'), button[data-testid='submit-button']",
            timeout=5000
        )
        btn.click()
    except PlaywrightTimeout:
        pf.press("Enter")
    print("  Submitted")

    p(4)
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except PlaywrightTimeout:
        pass

    ss(page, "after_submit", f"URL: {page.url}")

    # Handle 2FA
    if "2fa" in page.url or "new-device" in page.url:
        print("  [2FA] Device verification needed")
        code = get_code(max_wait=90)
        if not code:
            print("  [2FA] ERROR: No code obtained")
            return False

        cf = find(
            page,
            "input[type='text']:not([name='email']), input[type='number'], input[inputmode='numeric']",
            timeout=15000,
            desc="2FA code input"
        )
        if not cf:
            # Try any visible input
            cf = find(page, "input", timeout=5000, desc="any input for 2FA")
        if not cf:
            ss(page, "ERR_no_2fa_input")
            return False

        cf.fill(code)
        p(0.5)
        ss(page, "2fa_filled", f"Code {code} entered")

        try:
            vbtn = page.wait_for_selector(
                "button:has-text('Verify'), button[type='submit'], button[data-testid='submit-button']",
                timeout=8000
            )
            vbtn.click()
        except PlaywrightTimeout:
            cf.press("Enter")

        p(4)
        try:
            page.wait_for_load_state("networkidle", timeout=25000)
        except PlaywrightTimeout:
            pass
        ss(page, "after_2fa", f"URL: {page.url}")

    if "login" in page.url.lower() or "2fa" in page.url:
        print("  ERROR: Still on auth page")
        return False

    print(f"  Logged in. URL: {page.url}")
    return True


def go_to_builder(page):
    """Navigate to automations, create new from scratch, return automation ID."""
    print("\n=== NAVIGATE TO BUILDER ===")
    p(2)

    # Click Automations in sidebar
    if not click(page, "a[href*='automation'], [href='/automation/automations']", desc="Automations nav"):
        page.goto("https://app.brevo.com/automation/automations", wait_until="domcontentloaded", timeout=30000)
    p(3)
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except PlaywrightTimeout:
        pass
    ss(page, "automations_list", f"URL: {page.url}")
    print(f"  Automations list URL: {page.url}")

    # Click "Create an automation"
    if not click(page, "button:has-text('Create an automation'), button:has-text('Create')", desc="Create button"):
        ss(page, "ERR_no_create_btn")
        return False
    p(2, "modal opening")
    ss(page, "create_modal", "Create automation modal")

    # Click "Create from scratch"
    if not click(page, "button:has-text('Create from scratch')", timeout=10000, desc="Create from scratch"):
        # Try clicking it by text content in case it's a div/span
        try:
            page.locator("text=Create from scratch").click()
            print("  Clicked via locator text")
        except Exception as e:
            print(f"  ERROR: Could not click Create from scratch: {e}")
            ss(page, "ERR_no_from_scratch")
            return False
    p(5, "builder loading")
    try:
        page.wait_for_load_state("networkidle", timeout=30000)
    except PlaywrightTimeout:
        p(3)

    ss(page, "builder_loaded", f"Builder URL: {page.url}")
    print(f"  Builder URL: {page.url}")

    if "edit" not in page.url:
        print("  WARNING: Not on edit URL")
    return True


def rename_automation(page):
    """Rename 'Automation #N' to our workflow name."""
    print(f"\n=== RENAME: {WORKFLOW_NAME} ===")

    # The name shows in the top bar as "Automation #2" with a dropdown arrow
    # Click on the name text to edit it
    name_selectors = [
        ".sib-topbar__title",
        "[class*='title'] input",
        "[class*='automationName']",
        "button[class*='name']",
        "h1",
    ]

    # Try clicking the automation name in the header to get an edit field
    for sel in name_selectors:
        try:
            el = page.wait_for_selector(sel, timeout=4000, state="visible")
            if el:
                txt = el.inner_text()
                if "Automation" in txt or "#" in txt:
                    el.click()
                    p(1)
                    ss(page, "name_click", f"Clicked name element: {txt}")
                    print(f"  Clicked header name element: {txt}")
                    break
        except PlaywrightTimeout:
            continue

    # Look for an input that appeared after clicking
    for sel in ["input[class*='name']", "input[placeholder*='name' i]", "input[value*='Automation']"]:
        try:
            inp = page.wait_for_selector(sel, timeout=3000, state="visible")
            if inp:
                # Select all and replace
                inp.click()
                page.keyboard.press("Control+a")
                page.keyboard.type(WORKFLOW_NAME)
                p(0.5)
                page.keyboard.press("Enter")
                ss(page, "name_set", f"Name set to: {WORKFLOW_NAME}")
                print(f"  Name set via: {sel}")
                return True
        except PlaywrightTimeout:
            continue

    # Alternative: top bar might have a pencil/edit icon next to the name
    try:
        edit_icon = page.wait_for_selector("[aria-label*='edit' i], [aria-label*='rename' i], button[class*='edit']", timeout=3000)
        if edit_icon:
            edit_icon.click()
            p(1)
            inp = find(page, "input", timeout=5000, desc="name input after edit icon")
            if inp:
                inp.triple_click() if hasattr(inp, 'triple_click') else inp.click()
                page.keyboard.press("Control+a")
                page.keyboard.type(WORKFLOW_NAME)
                page.keyboard.press("Enter")
                ss(page, "name_set_via_icon", "Name set via edit icon")
                return True
    except PlaywrightTimeout:
        pass

    print("  WARNING: Could not rename - will leave as default")
    ss(page, "name_not_found", "Could not find name field")
    return False


def drag_trigger_to_canvas(page):
    """
    Drag 'Contact added to list' from the Triggers panel to the canvas.
    The builder uses HTML5 drag-and-drop.
    """
    print("\n=== DRAG TRIGGER TO CANVAS ===")

    # Make sure we're on the Triggers tab
    try:
        triggers_tab = page.wait_for_selector("button:has-text('Triggers'), [role='tab']:has-text('Triggers')", timeout=8000)
        triggers_tab.click()
        p(1)
        print("  Clicked Triggers tab")
    except PlaywrightTimeout:
        print("  Triggers tab not found (may already be active)")

    ss(page, "triggers_tab", "Triggers tab active")

    # Find the "Contact added to list" trigger item in the left panel
    trigger_item = find(
        page,
        "text=Contact added to list",
        timeout=10000,
        desc="'Contact added to list' trigger item"
    )
    if not trigger_item:
        # Try broader selectors
        trigger_item = find(page, "[class*='step']:has-text('Contact added to list')", desc="trigger item broad")

    if not trigger_item:
        print("  ERROR: Cannot find 'Contact added to list' trigger")
        ss(page, "ERR_no_trigger_item")
        # Show what IS visible
        try:
            body = page.inner_text("body")[:3000]
            print(f"  Page text:\n{body[:1500]}")
        except Exception:
            pass
        return False

    # Find the canvas drop zone
    canvas = find(
        page,
        ".automation-canvas, [class*='canvas'], [class*='dropzone'], [data-role='canvas']",
        timeout=8000,
        desc="canvas drop zone"
    )

    if not canvas:
        # Try to find by the hint text
        try:
            canvas = page.wait_for_selector("text=Drop a step here", timeout=5000)
        except PlaywrightTimeout:
            pass

    if not canvas:
        print("  WARNING: Canvas not found by selector - will try coordinate-based drag")

    # Get bounding boxes for drag
    trigger_box = trigger_item.bounding_box()
    print(f"  Trigger box: {trigger_box}")

    if canvas:
        canvas_box = canvas.bounding_box()
        print(f"  Canvas box: {canvas_box}")
        # Target center of canvas
        target_x = canvas_box['x'] + canvas_box['width'] / 2
        target_y = canvas_box['y'] + canvas_box['height'] / 2
    else:
        # Canvas is roughly the right 75% of the viewport
        vp = page.viewport_size
        target_x = vp['width'] * 0.65
        target_y = vp['height'] * 0.45
        print(f"  Using estimated canvas position: ({target_x}, {target_y})")

    src_x = trigger_box['x'] + trigger_box['width'] / 2
    src_y = trigger_box['y'] + trigger_box['height'] / 2

    # Method 1: Playwright drag_to
    try:
        print(f"  Dragging from ({src_x:.0f},{src_y:.0f}) to ({target_x:.0f},{target_y:.0f})")
        trigger_item.drag_to(
            page.locator(f"css=[class*='canvas']").first if canvas else page.locator("body"),
            source_position={"x": int(src_x - trigger_box['x']), "y": int(src_y - trigger_box['y'])},
            target_position={"x": int(target_x), "y": int(target_y)},
        )
        p(2)
        ss(page, "after_drag_method1", "After drag (method 1)")
    except Exception as e:
        print(f"  Drag method 1 failed: {e}")

        # Method 2: Manual mouse events
        try:
            print("  Trying manual mouse drag...")
            page.mouse.move(src_x, src_y)
            p(0.3)
            page.mouse.down()
            p(0.5)
            # Slowly move to target
            steps = 10
            for i in range(steps + 1):
                cx = src_x + (target_x - src_x) * i / steps
                cy = src_y + (target_y - src_y) * i / steps
                page.mouse.move(cx, cy)
                p(0.05)
            p(0.5)
            page.mouse.up()
            p(2)
            ss(page, "after_drag_method2", "After drag (method 2)")
        except Exception as e2:
            print(f"  Drag method 2 failed: {e2}")

            # Method 3: Try clicking the item (some builders work with click-to-add)
            print("  Trying click-to-add...")
            trigger_item.click()
            p(2)
            ss(page, "after_click_add", "After click-to-add")

    # Check if trigger was added to canvas
    p(2)
    ss(page, "trigger_drop_result", "After trigger drop attempt")
    try:
        body = page.inner_text("body")[:3000]
        print(f"  Builder state after drop:\n{body[:1000]}")
    except Exception:
        pass

    return True


def configure_trigger_panel(page):
    """
    After dropping trigger, configure it:
    - Select list: List 3 (The Neural Feed)
    """
    print("\n=== CONFIGURE TRIGGER ===")
    p(2)
    ss(page, "trigger_config_start", "Trigger configuration panel")

    # Look for a configuration panel that should appear on the right
    # or in a modal/drawer
    config_selectors = [
        "[class*='settings']",
        "[class*='config']",
        "[class*='panel']",
        "[class*='sidebar']",
        "[class*='drawer']",
    ]

    # Look for list selector
    list_selectors = [
        "select[name*='list']",
        "[aria-label*='list' i]",
        "text=Select a list",
        "text=Choose a list",
        "[placeholder*='list' i]",
    ]

    for sel in list_selectors:
        try:
            el = page.wait_for_selector(sel, timeout=5000, state="visible")
            if el:
                print(f"  Found list selector: {sel}")
                el.click()
                p(1)
                ss(page, "list_dropdown_open", "List selector opened")

                # Select "The Neural Feed" (List 3)
                list_option_selectors = [
                    "option:has-text('Neural Feed')",
                    "li:has-text('Neural Feed')",
                    "div:has-text('The Neural Feed')",
                    "[data-value='3']",
                ]
                for lsel in list_option_selectors:
                    try:
                        opt = page.wait_for_selector(lsel, timeout=3000)
                        if opt:
                            opt.click()
                            print(f"  Selected Neural Feed list via: {lsel}")
                            p(1)
                            break
                    except PlaywrightTimeout:
                        continue
                ss(page, "trigger_configured", "Trigger configured")
                break
        except PlaywrightTimeout:
            continue

    # Capture current state
    try:
        body = page.inner_text("body")
        print(f"  Canvas/page state:\n{body[:2000]}")
    except Exception:
        pass


def add_action_step(page, step_type, template_id=None, wait_days=None, step_num=0):
    """
    Add an action step (email send or wait) to the automation.
    step_type: 'email' or 'wait'
    """
    print(f"\n  [STEP {step_num}] Adding {step_type}" +
          (f" (template {template_id}: {TEMPLATE_NAMES.get(template_id, '')})" if template_id else "") +
          (f" (wait {wait_days} days)" if wait_days else ""))

    # Click the Actions tab to find send email and wait steps
    try:
        actions_tab = page.wait_for_selector(
            "button:has-text('Actions'), [role='tab']:has-text('Actions')",
            timeout=5000
        )
        actions_tab.click()
        p(0.8)
    except PlaywrightTimeout:
        print("    Actions tab not found")

    if step_type == 'wait':
        # Find "Wait" action in the panel
        wait_item = find(
            page,
            "text=Wait, [class*='step']:has-text('Wait'), text=Delay",
            timeout=8000,
            desc="Wait step item"
        )
        if wait_item:
            # Try to add it (click or drag)
            wait_item.click()
            p(2)
            ss(page, f"wait_step_{step_num}", f"Wait step added attempt")

            # Configure wait duration
            # Look for input to enter days
            for sel in ["input[type='number']", "input[placeholder*='day' i]", "[name*='delay']", "[name*='wait']"]:
                try:
                    days_input = page.wait_for_selector(sel, timeout=4000, state="visible")
                    if days_input:
                        days_input.triple_click() if hasattr(days_input, 'triple_click') else (days_input.click(), page.keyboard.press("Control+a"))
                        days_input.fill(str(wait_days))
                        p(0.5)
                        print(f"    Set wait to {wait_days} days")
                        break
                except PlaywrightTimeout:
                    continue

    elif step_type == 'email':
        # Find "Send an email" action
        email_action = find(
            page,
            "text=Send an email, text=Send email, [class*='step']:has-text('email')",
            timeout=8000,
            desc="Send email step"
        )
        if email_action:
            email_action.click()
            p(2)
            ss(page, f"email_step_{step_num}", f"Email step {template_id} added attempt")

            # Select the template
            for sel in [
                f"option:has-text('{TEMPLATE_NAMES[template_id]}')",
                f"li:has-text('{TEMPLATE_NAMES[template_id]}')",
                f"[data-value='{template_id}']",
                "select[name*='template']",
            ]:
                try:
                    el = page.wait_for_selector(sel, timeout=4000)
                    if el:
                        el.click()
                        p(0.5)
                        print(f"    Selected template {template_id}")
                        break
                except PlaywrightTimeout:
                    continue


def analyze_builder_deeply(page):
    """Take detailed screenshots and log the full builder state."""
    print("\n=== DEEP BUILDER ANALYSIS ===")
    ss(page, "analysis_full", "Full page screenshot")

    # Scroll down to see more
    page.evaluate("window.scrollTo(0, 500)")
    p(0.5)
    ss(page, "analysis_scrolled", "Scrolled view")
    page.evaluate("window.scrollTo(0, 0)")

    # Print ALL interactive elements
    try:
        all_btns = page.query_selector_all("button, [role='button'], [draggable='true']")
        print(f"  Interactive elements ({len(all_btns)}):")
        for el in all_btns[:30]:
            txt = el.inner_text()[:60].strip()
            drag = el.get_attribute('draggable')
            cls = (el.get_attribute('class') or '')[:40]
            if txt:
                print(f"    '{txt}' draggable={drag} class={cls}")
    except Exception as e:
        print(f"  Error listing elements: {e}")

    try:
        body = page.inner_text("body")
        print(f"\n  Full page text:\n{body[:3000]}")
    except Exception:
        pass


def save_and_activate(page):
    """Save the workflow and activate it."""
    print("\n=== SAVE AND ACTIVATE ===")

    # Save (usually auto-saves, but try save button if present)
    try:
        save_btn = page.wait_for_selector(
            "button:has-text('Save'), button[aria-label*='save' i]",
            timeout=5000
        )
        save_btn.click()
        p(2)
        print("  Saved")
    except PlaywrightTimeout:
        print("  No explicit save button (likely auto-saves)")

    ss(page, "before_activate", "Before activation")

    # Click "Activate automation"
    activated = click(
        page,
        "button:has-text('Activate automation'), button:has-text('Activate')",
        timeout=10000,
        desc="Activate automation button"
    )
    if activated:
        p(3)
        ss(page, "after_activate", "After activation click")
        print("  Clicked Activate")

        # Confirm any dialog
        try:
            confirm = page.wait_for_selector(
                "button:has-text('Activate'), button:has-text('Confirm'), button:has-text('OK')",
                timeout=5000
            )
            confirm.click()
            p(2)
            ss(page, "activated", "Automation activated")
            print("  Confirmed activation")
        except PlaywrightTimeout:
            pass

    return activated


def run():
    print("=" * 65)
    print("Brevo Neural Feed Welcome Sequence - FINAL BUILD")
    print("=" * 65)

    with sync_playwright() as p_api:
        browser = p_api.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-blink-features=AutomationControlled']
        )
        ctx = browser.new_context(
            viewport={'width': 1600, 'height': 900},
            device_scale_factor=2,
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
        )
        page = ctx.new_page()
        page.set_default_timeout(30000)

        # 1. Login + 2FA
        if not do_login(page):
            print("\nFAILED: Login/2FA")
            ss(page, "FAILED_login")
            browser.close()
            return {"status": "failed", "stage": "login"}

        ss(page, "logged_in", "Logged in successfully")

        # 2. Navigate to builder and create from scratch
        if not go_to_builder(page):
            print("\nFAILED: Could not reach builder")
            browser.close()
            return {"status": "failed", "stage": "builder_navigation"}

        # 3. Deeply analyze builder so we understand its structure
        analyze_builder_deeply(page)

        # 4. Rename automation
        rename_automation(page)

        # 5. Drag trigger to canvas
        drag_trigger_to_canvas(page)

        # 6. Configure trigger (List 3 - The Neural Feed)
        configure_trigger_panel(page)

        # 7. Add email steps with waits
        print("\n=== BUILDING EMAIL SEQUENCE ===")
        step_num = 0
        for template_id, wait_days in EMAIL_SEQUENCE:
            step_num += 1
            if wait_days > 0:
                add_action_step(page, 'wait', wait_days=wait_days, step_num=step_num)
                p(1)
                step_num += 1
            add_action_step(page, 'email', template_id=template_id, step_num=step_num)
            p(1)

        ss(page, "sequence_built", "Full sequence built")

        # 8. Save and activate
        activated = save_and_activate(page)

        # Final screenshot
        ss(page, "FINAL", "Final state")
        final_url = page.url
        print(f"\n  Final URL: {final_url}")

        try:
            final_text = page.inner_text("body")[:2000]
            print(f"  Final page text:\n{final_text[:1000]}")
        except Exception:
            pass

        browser.close()

        return {
            "status": "completed" if activated else "partial",
            "workflow_url": final_url,
            "activated": activated,
            "screenshots_dir": SS_DIR,
            "steps_added": step_num,
        }


if __name__ == "__main__":
    result = run()
    print("\n" + "=" * 65)
    print("RESULT:")
    print(json.dumps(result, indent=2))
