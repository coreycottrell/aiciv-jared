#!/usr/bin/env python3
"""
Brevo 4 Automation Workflows Builder
=====================================
Builds 4 automation workflows in Brevo via Playwright:
  1. AI Partnership Audit — Lead Nurture (trigger: Enterprise Leads list)
  2. Pricing Intent — Awakening Section (trigger: event awakening_section_viewed)
  3. 45-Day Inactive Re-engagement (trigger: inactivity 45 days, List 3)
  4. Email Reply — High Engagement Tag (trigger: event email_replied)

Strategy:
  - Try to use saved session first; if expired, do fresh login + 2FA
  - Use Brevo's "Create new automation" flow for each workflow
  - Take screenshots at every major step
  - Report results in a JSON summary

Based on prior work in brevo_complete_build.py + brevo_session_login.py
Critical learnings:
  - Brevo has NO REST API for automations - must use Playwright
  - Login button is type="button" with text "Log In"
  - 2FA code comes from account-alerts@t.brevo.com
  - Drag-and-drop is fragile; step-by-step mouse approach is more reliable
  - Sessions expire quickly
"""

import os
import re
import sys
import time
import json
import imaplib
import email as email_module
import email.utils
import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

BREVO_EMAIL = 'jared@puretechnology.nyc'  # Jared's primary email
BREVO_EMAIL_ALT = 'jared@puretechnology.nyc'
BREVO_PASSWORD = os.environ.get('BREVO_PASSWORD', '_g%DXnKfQ5w*&65')
GMAIL_USER = os.environ.get('GMAIL_USERNAME', 'purebrain@puremarketing.ai')
GMAIL_APP_PASSWORD = os.environ.get('GOOGLE_APP_PASSWORD', 'mldvztmeligxhyaw')

SESSION_FILE = '/home/jared/projects/AI-CIV/aether/tools/brevo_session.json'
SS_DIR = '/home/jared/projects/AI-CIV/aether/exports/screenshots/brevo-workflows'
os.makedirs(SS_DIR, exist_ok=True)

# Screenshot counter
_n = [0]
def ss(page, label):
    _n[0] += 1
    path = f"{SS_DIR}/{_n[0]:03d}_{label}.png"
    try:
        page.screenshot(path=path, full_page=False)
        print(f"  [SS] {_n[0]:03d}_{label}.png")
    except Exception as e:
        print(f"  [SS ERROR] {label}: {e}")
    return path


def wait_idle(page, timeout=10000):
    try:
        page.wait_for_load_state('networkidle', timeout=timeout)
    except PlaywrightTimeout:
        pass


def canvas_text(page):
    try:
        return page.evaluate('() => document.body.innerText')
    except Exception:
        return ''


# ─── 2FA Code Retrieval ────────────────────────────────────────────────────────

def extract_code_from_body(body):
    """Extract 6-digit code from email body."""
    match = re.search(r'verification code[:\s]*\n?\s*(\d{6})', body, re.IGNORECASE)
    if match:
        return match.group(1)
    for c in re.findall(r'\b\d{6}\b', body):
        d = list(c)
        if not (d[0] == d[2] == d[4] and d[1] == d[3] == d[5]):
            return c
    return None


def get_2fa_code(max_wait=120, started_at=None):
    """Wait for Brevo 2FA code from Gmail IMAP."""
    if started_at is None:
        started_at = time.time() - 10
    print(f"  [IMAP] Waiting for 2FA code (sent after {time.strftime('%H:%M:%S', time.localtime(started_at))})...")
    deadline = time.time() + max_wait

    while time.time() < deadline:
        try:
            m = imaplib.IMAP4_SSL('imap.gmail.com')
            m.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            m.select('INBOX')
            today = datetime.date.today().strftime('%d-%b-%Y')
            _, data = m.search(None, f'FROM account-alerts@t.brevo.com SINCE {today}')
            if data[0]:
                for mid in reversed(data[0].decode().split()):
                    _, mdata = m.fetch(mid, '(RFC822)')
                    msg = email_module.message_from_bytes(mdata[0][1])
                    subj = msg.get('Subject', '')
                    if 'verify' not in subj.lower():
                        continue
                    try:
                        msg_ts = email.utils.parsedate_to_datetime(msg.get('Date', '')).timestamp()
                        if msg_ts < started_at - 60:
                            continue
                    except Exception:
                        pass
                    body = ''
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() in ('text/plain', 'text/html'):
                                body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    else:
                        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    code = extract_code_from_body(body)
                    if code:
                        print(f"  [IMAP] Got code: {code}")
                        m.logout()
                        return code
            m.logout()
        except Exception as e:
            print(f"  [IMAP] Error: {e}")
        remaining = int(deadline - time.time())
        print(f"  [IMAP] Waiting... ({remaining}s left)")
        time.sleep(6)
    return None


# ─── Login ─────────────────────────────────────────────────────────────────────

def do_login(page, email_addr, password):
    """Login to Brevo. Returns True if successful."""
    print(f"\n[LOGIN] Attempting login with {email_addr}...")
    page.goto('https://login.brevo.com/', wait_until='domcontentloaded', timeout=60000)
    time.sleep(2)

    # Dismiss cookies
    try:
        page.wait_for_selector("button:has-text('Accept All Cookies')", timeout=4000).click()
        time.sleep(0.5)
    except PlaywrightTimeout:
        pass

    ss(page, 'login_page')

    # Fill email
    try:
        ef = page.wait_for_selector('input[name="email"], input#email, input[type="email"]', timeout=15000)
        ef.fill(email_addr)
        time.sleep(0.3)
    except PlaywrightTimeout:
        print("  ERROR: Cannot find email field")
        ss(page, 'login_no_email_field')
        return False

    # Fill password
    try:
        pf = page.wait_for_selector('input[type="password"]', timeout=10000)
        pf.fill(password)
        time.sleep(0.3)
    except PlaywrightTimeout:
        print("  ERROR: Cannot find password field")
        return False

    ss(page, 'login_creds_filled')
    login_triggered_at = time.time()

    # Click login
    try:
        page.wait_for_selector(
            'button:has-text("Log In"), button[data-testid="submit-button"]',
            timeout=5000
        ).click()
    except PlaywrightTimeout:
        pf.press('Enter')

    print(f"  Submitted login at {time.strftime('%H:%M:%S')}")
    time.sleep(4)
    wait_idle(page, 20000)
    print(f"  URL after submit: {page.url}")
    ss(page, 'login_after_submit')

    # Handle CAPTCHA check
    body = canvas_text(page)
    if 'captcha' in body.lower() or 'robot' in body.lower():
        print("  CAPTCHA detected!")
        ss(page, 'login_CAPTCHA')
        return 'captcha'

    # Handle 2FA
    if '2fa' in page.url or 'new-device' in page.url or 'verify' in page.url:
        print("  [2FA] Device verification required")
        ss(page, 'login_2fa_page')
        code = get_2fa_code(max_wait=120, started_at=login_triggered_at)
        if not code:
            print("  ERROR: Could not retrieve 2FA code")
            return False

        # Find code input
        cf = None
        for sel in [
            'input[autocomplete="one-time-code"]',
            'input[inputmode="numeric"]',
            'input[type="number"]',
            'input[placeholder*="code" i]',
            'form input[type="text"]:not([name="email"])',
        ]:
            try:
                cf = page.wait_for_selector(sel, timeout=3000, state='visible')
                print(f"  Found code input via: {sel}")
                break
            except PlaywrightTimeout:
                continue

        if not cf:
            print("  ERROR: Cannot find 2FA input")
            ss(page, 'login_2fa_no_input')
            return False

        cf.fill(code)
        time.sleep(0.5)
        ss(page, 'login_2fa_code_entered')

        try:
            page.wait_for_selector(
                'button:has-text("Verify"), button[data-testid="submit-button"]',
                timeout=8000
            ).click()
        except PlaywrightTimeout:
            cf.press('Enter')

        # Wait for redirect
        for _ in range(20):
            time.sleep(1)
            if 'login' not in page.url.lower() and '2fa' not in page.url and 'new-device' not in page.url:
                break
            print(f"  Still on 2FA/login page... ({page.url[:60]})")

        print(f"  URL after 2FA: {page.url}")
        ss(page, 'login_after_2fa')

        if '2fa' in page.url or 'new-device' in page.url:
            print("  ERROR: Still on 2FA page - code failed")
            return False

    if 'login' in page.url.lower():
        print("  ERROR: Still on login page")
        ss(page, 'login_failed')
        return False

    print(f"  Login successful! URL: {page.url}")
    return True


def load_session(ctx):
    """Load saved session. Returns True if file exists."""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE) as f:
                state = json.load(f)
            print(f"  Session file found: {len(state.get('cookies', []))} cookies")
            # Note: can't inject into existing context - must create new context with storage_state
            return state
        except Exception as e:
            print(f"  Session load error: {e}")
    return None


def save_session(ctx):
    """Save current session to disk."""
    try:
        state = ctx.storage_state()
        with open(SESSION_FILE, 'w') as f:
            json.dump(state, f)
        print(f"  Session saved: {len(state.get('cookies', []))} cookies")
    except Exception as e:
        print(f"  Session save error: {e}")


def is_logged_in(page):
    """Check if we're logged into Brevo."""
    try:
        page.goto('https://app.brevo.com/', wait_until='domcontentloaded', timeout=30000)
        time.sleep(2)
        return 'login' not in page.url.lower()
    except Exception:
        return False


# ─── Automation UI Helpers ─────────────────────────────────────────────────────

def goto_automations(page):
    """Navigate to the Automations list page."""
    print("\n  Navigating to Automations...")
    page.goto('https://app.brevo.com/automation/list', wait_until='domcontentloaded', timeout=30000)
    time.sleep(3)
    wait_idle(page)
    ss(page, 'automations_list')
    print(f"  URL: {page.url}")


def click_create_automation(page):
    """Click 'Create new automation' or 'New automation' button."""
    print("  Looking for 'Create new automation' button...")
    for sel in [
        'button:has-text("Create a new automation")',
        'button:has-text("New automation")',
        'a:has-text("New automation")',
        'a:has-text("Create")',
        'button:has-text("Create")',
        '[data-testid="create-automation"]',
    ]:
        try:
            btn = page.wait_for_selector(sel, timeout=5000, state='visible')
            if btn:
                btn.click()
                time.sleep(2)
                wait_idle(page)
                print(f"  Clicked create via: {sel}")
                ss(page, 'create_clicked')
                return True
        except PlaywrightTimeout:
            continue

    # Try clicking any link/button visible with "create" or "new"
    body = canvas_text(page)
    print(f"  Page text snippet: {body[:500]}")
    ss(page, 'create_not_found')
    return False


def set_automation_name(page, name):
    """Set the automation name in the editor."""
    print(f"  Setting name: {name}")
    for sel in [
        'input[placeholder*="Automation name" i]',
        'input[placeholder*="name" i]',
        '[data-testid="automation-name"]',
        'input[name*="name"]',
        'h1[contenteditable]',
        '.automation-name input',
    ]:
        try:
            inp = page.wait_for_selector(sel, timeout=5000, state='visible')
            if inp:
                inp.triple_click()
                time.sleep(0.3)
                inp.fill(name)
                time.sleep(0.5)
                print(f"  Name set via: {sel}")
                return True
        except PlaywrightTimeout:
            continue

    print("  WARNING: Could not find name input - checking page state")
    ss(page, 'name_field_not_found')
    return False


def click_triggers_tab(page):
    try:
        page.wait_for_selector('button:has-text("Triggers")', timeout=5000).click()
        time.sleep(0.8)
    except PlaywrightTimeout:
        pass


def click_actions_tab(page):
    try:
        page.wait_for_selector('button:has-text("Actions")', timeout=5000).click()
        time.sleep(0.8)
    except PlaywrightTimeout:
        pass


def drag_to_canvas(page, item_text, is_trigger=False):
    """
    Drag an item (trigger or action) from the side panel to the canvas drop slot.
    Returns True if drag appeared successful.
    """
    if is_trigger:
        click_triggers_tab(page)
    else:
        click_actions_tab(page)
    time.sleep(0.5)

    # Find the draggable item
    drag_sel = f'[draggable=true]:has-text("{item_text}")'
    try:
        item_loc = page.locator(drag_sel).first
        ibox = item_loc.bounding_box()
        if not ibox:
            print(f"  Draggable '{item_text}' not found")
            return False
    except Exception as e:
        print(f"  Error finding draggable: {e}")
        return False

    # Find drop target: "Drop block here" or "Drop a step here"
    drop_slot = None
    for drop_text in ['Drop block here', 'Drop a step here', 'Add a step']:
        try:
            drop_slot = page.wait_for_selector(f'text={drop_text}', timeout=4000)
            if drop_slot:
                print(f"  Found drop slot: '{drop_text}'")
                break
        except PlaywrightTimeout:
            continue

    if drop_slot:
        sbox = drop_slot.bounding_box()
    else:
        # Fall back to canvas center
        canvas_loc = page.locator('[class*="WorkflowCanvas"], [class*="canvas"], [class*="workflow-editor"]').first
        cbox = canvas_loc.bounding_box()
        if not cbox:
            print("  Cannot find canvas for drop target")
            return False
        sbox = {
            'x': cbox['x'] + cbox['width'] / 2 - 50,
            'y': cbox['y'] + cbox['height'] * 0.4,
            'width': 100,
            'height': 40
        }
        print(f"  Using canvas fallback drop target at {sbox}")

    # Perform step-by-step mouse drag (more reliable than drag_to)
    src_x = ibox['x'] + ibox['width'] / 2
    src_y = ibox['y'] + ibox['height'] / 2
    tgt_x = sbox['x'] + sbox['width'] / 2
    tgt_y = sbox['y'] + sbox['height'] / 2

    print(f"  Dragging from ({src_x:.0f},{src_y:.0f}) to ({tgt_x:.0f},{tgt_y:.0f})")

    mouse = page.mouse
    mouse.move(src_x, src_y)
    time.sleep(0.3)
    mouse.down()
    time.sleep(0.5)

    # Step-by-step movement
    steps = 20
    for i in range(1, steps + 1):
        nx = src_x + (tgt_x - src_x) * i / steps
        ny = src_y + (tgt_y - src_y) * i / steps
        mouse.move(nx, ny)
        time.sleep(0.03)

    time.sleep(0.5)
    mouse.up()
    time.sleep(2.5)
    wait_idle(page, 5000)
    label = item_text[:20].replace(' ', '_')
    ss(page, f'dragged_{label}')

    # Verify placement
    body = canvas_text(page)
    if item_text[:15] in body or 'Drop block here' not in body:
        print(f"  Drag appears successful")
        return True
    print(f"  WARNING: Drag may have failed (still see 'Drop block here')")
    return False


def configure_list_trigger(page, list_name):
    """Configure 'Contact added to a list' trigger - select the list."""
    print(f"  Configuring list trigger: '{list_name}'")
    time.sleep(1)
    ss(page, 'trigger_config_start')

    # Find the list selector
    for sel in [
        'text=Select a list',
        '[placeholder*="list" i]',
        '[class*="select-control"]',
        'select',
        '.sib-select, [class*="dropdown"]',
    ]:
        try:
            el = page.wait_for_selector(sel, timeout=6000, state='visible')
            if el:
                el.click()
                time.sleep(1.5)
                ss(page, 'list_dropdown_open')
                print(f"  Opened list dropdown via: {sel}")

                # Select the target list
                for opt_sel in [
                    f'text={list_name}',
                    f'li:has-text("{list_name}")',
                    f'[class*="option"]:has-text("{list_name[:30]}")',
                    f'[role="option"]:has-text("{list_name[:30]}")',
                ]:
                    try:
                        opt = page.wait_for_selector(opt_sel, timeout=4000, state='visible')
                        if opt:
                            opt.click()
                            time.sleep(1)
                            print(f"  Selected: {list_name}")
                            ss(page, 'list_selected')

                            # Save
                            try:
                                page.wait_for_selector('button:has-text("Save")', timeout=5000).click()
                                time.sleep(2)
                                ss(page, 'trigger_saved')
                                return True
                            except PlaywrightTimeout:
                                print("  No Save button after list select")
                                return True
                    except PlaywrightTimeout:
                        continue

                # Show available options for debugging
                opts = page.query_selector_all('[class*="option"], li[role="option"]')
                print(f"  Available options ({len(opts)}):")
                for o in opts[:15]:
                    try:
                        print(f"    - {o.evaluate('el => el.textContent').strip()[:60]}")
                    except Exception:
                        pass
                ss(page, 'list_options_visible')
                break
        except PlaywrightTimeout:
            continue

    ss(page, 'list_trigger_config_end')
    return False


def configure_event_trigger(page, event_name):
    """Configure 'Contact triggers an event' trigger."""
    print(f"  Configuring event trigger: '{event_name}'")
    time.sleep(1)
    ss(page, 'event_trigger_config_start')

    # Find event name input
    for sel in [
        'input[placeholder*="event" i]',
        'input[placeholder*="Event name" i]',
        'input[name*="event"]',
        '[class*="event"] input',
        'input[type="text"]',
    ]:
        try:
            inp = page.wait_for_selector(sel, timeout=6000, state='visible')
            if inp:
                inp.click()
                page.keyboard.press('Control+a')
                inp.fill(event_name)
                time.sleep(0.5)
                print(f"  Entered event name via: {sel}")
                ss(page, 'event_name_entered')

                # Save
                try:
                    page.wait_for_selector('button:has-text("Save")', timeout=5000).click()
                    time.sleep(2)
                    ss(page, 'event_trigger_saved')
                    return True
                except PlaywrightTimeout:
                    print("  No Save button - trying Enter")
                    inp.press('Enter')
                    time.sleep(1)
                    return True
        except PlaywrightTimeout:
            continue

    print("  WARNING: Could not find event name input")
    ss(page, 'event_trigger_failed')
    return False


def configure_inactivity_trigger(page, days, list_name):
    """Configure 'Inactivity on emails' trigger."""
    print(f"  Configuring inactivity trigger: {days} days, list: {list_name}")
    time.sleep(1)
    ss(page, 'inactivity_trigger_config_start')

    # Set the days
    for sel in ['input[type="number"]', 'input[placeholder*="day" i]', 'input[name*="days"]']:
        try:
            inp = page.wait_for_selector(sel, timeout=5000, state='visible')
            if inp:
                inp.triple_click()
                inp.fill(str(days))
                time.sleep(0.3)
                print(f"  Set {days} days via: {sel}")
                break
        except PlaywrightTimeout:
            continue

    # Select the list
    for sel in ['text=Select a list', '[placeholder*="list" i]', '[class*="select-control"]']:
        try:
            el = page.wait_for_selector(sel, timeout=4000, state='visible')
            if el:
                el.click()
                time.sleep(1)
                for opt_sel in [
                    f'text={list_name}',
                    f'li:has-text("{list_name}")',
                    f'[class*="option"]:has-text("{list_name[:30]}")',
                ]:
                    try:
                        opt = page.wait_for_selector(opt_sel, timeout=3000, state='visible')
                        if opt:
                            opt.click()
                            time.sleep(0.8)
                            print(f"  Selected list: {list_name}")
                            break
                    except PlaywrightTimeout:
                        continue
                break
        except PlaywrightTimeout:
            continue

    ss(page, 'inactivity_trigger_configured')

    # Save
    try:
        page.wait_for_selector('button:has-text("Save")', timeout=5000).click()
        time.sleep(2)
        ss(page, 'inactivity_trigger_saved')
        return True
    except PlaywrightTimeout:
        print("  No Save button for inactivity trigger")
        return False


def add_send_email_step(page, template_id, step_label):
    """Add a 'Send an email' step using template ID."""
    print(f"\n  [STEP] Send email: template {template_id}")

    # Try to select trigger type if on trigger selection screen
    # First check if we need to pick from a "what to do next" modal
    body = canvas_text(page)
    ss(page, f'before_email_step_{step_label}')

    if 'Choose a step' in body or 'What to do' in body:
        for sel in ['text=Send an email', '[data-testid*="email"]', '[class*="step"]:has-text("Send an email")']:
            try:
                page.wait_for_selector(sel, timeout=4000).click()
                time.sleep(1.5)
                print(f"  Picked 'Send an email' from modal")
                break
            except PlaywrightTimeout:
                continue

    # Drag "Send an email" to canvas
    dragged = drag_to_canvas(page, 'Send an email', is_trigger=False)

    if not dragged:
        # Try clicking "Add a step" button instead
        for sel in ['button:has-text("Add a step")', 'text=Add a step', '[data-testid*="add-step"]']:
            try:
                page.wait_for_selector(sel, timeout=4000).click()
                time.sleep(1.5)
                ss(page, f'add_step_clicked_{step_label}')
                # Now look for "Send an email" option
                for opt_sel in ['text=Send an email', '[data-testid*="email"]']:
                    try:
                        page.wait_for_selector(opt_sel, timeout=4000).click()
                        time.sleep(1.5)
                        break
                    except PlaywrightTimeout:
                        continue
                break
            except PlaywrightTimeout:
                continue

    time.sleep(1)
    ss(page, f'email_config_open_{step_label}')

    # Configure the template
    body = canvas_text(page)

    # Look for template selection UI
    configured = False

    # Method 1: "Add message" button -> template picker
    try:
        btn = page.wait_for_selector('button:has-text("Add message"), button:has-text("Choose a template"), button:has-text("Select a template")', timeout=5000)
        btn.click()
        time.sleep(2)
        ss(page, f'template_picker_open_{step_label}')

        # In the template picker modal, find the template by ID or name
        # Try searching by template ID
        try:
            search = page.wait_for_selector('input[placeholder*="search" i], input[placeholder*="Search" i]', timeout=4000)
            search.fill(str(template_id))
            time.sleep(1.5)
        except PlaywrightTimeout:
            pass

        # Click the template
        for tmpl_sel in [
            f'[data-template-id="{template_id}"]',
            f'[data-id="{template_id}"]',
            f'text=#{template_id}',
            f'[class*="template-card"]:nth-child({template_id})',
        ]:
            try:
                tmpl = page.wait_for_selector(tmpl_sel, timeout=3000)
                tmpl.click()
                time.sleep(1)
                print(f"  Selected template {template_id}")
                configured = True
                break
            except PlaywrightTimeout:
                continue

        if not configured:
            # Just click the first/nth template card based on ID position
            cards = page.query_selector_all('[class*="template"], [data-testid*="template"]')
            print(f"  Found {len(cards)} template cards")
            # Look for the one with template_id in its text
            for card in cards:
                try:
                    text = card.evaluate('el => el.textContent')
                    if str(template_id) in text:
                        card.click()
                        time.sleep(1)
                        print(f"  Clicked template card containing '{template_id}'")
                        configured = True
                        break
                except Exception:
                    continue

        # Click "Use this template" or "Select"
        for use_sel in ['button:has-text("Use")', 'button:has-text("Select")', 'button:has-text("Choose")']:
            try:
                page.wait_for_selector(use_sel, timeout=4000).click()
                time.sleep(1.5)
                break
            except PlaywrightTimeout:
                continue

    except PlaywrightTimeout:
        print("  No 'Add message' button found")
        ss(page, f'no_add_message_{step_label}')

    # Method 2: Direct template input/select
    if not configured:
        for sel in [
            'select[name*="template"]',
            'input[placeholder*="template" i]',
            '[class*="select"]:has-text("template")',
        ]:
            try:
                el = page.wait_for_selector(sel, timeout=4000, state='visible')
                if el:
                    tag = el.evaluate('el => el.tagName').lower()
                    if tag == 'select':
                        el.select_option(value=str(template_id))
                    else:
                        el.click()
                        time.sleep(1)
                        el.fill(str(template_id))
                    time.sleep(1)
                    configured = True
                    print(f"  Set template {template_id} via: {sel}")
                    break
            except PlaywrightTimeout:
                continue

    # Save step
    try:
        page.wait_for_selector('button:has-text("Save")', timeout=5000).click()
        time.sleep(2)
        ss(page, f'email_step_saved_{step_label}')
        print(f"  Email step saved")
        return True
    except PlaywrightTimeout:
        print("  No Save button for email step")
        ss(page, f'email_step_nosave_{step_label}')
        return configured


def add_wait_step(page, days, step_label):
    """Add a Wait step for N days."""
    print(f"\n  [STEP] Wait: {days} days")

    dragged = drag_to_canvas(page, 'Wait', is_trigger=False)
    if not dragged:
        # Try "Add a step" -> "Wait"
        for sel in ['button:has-text("Add a step")', 'text=Add a step']:
            try:
                page.wait_for_selector(sel, timeout=4000).click()
                time.sleep(1.5)
                for opt in ['text=Wait', 'text=Delay', '[data-testid*="wait"]']:
                    try:
                        page.wait_for_selector(opt, timeout=3000).click()
                        time.sleep(1)
                        break
                    except PlaywrightTimeout:
                        continue
                break
            except PlaywrightTimeout:
                continue

    time.sleep(1)
    ss(page, f'wait_config_open_{step_label}')

    # Set days
    for sel in ['input[type="number"]', 'input[placeholder*="day" i]', 'input[name*="duration"]']:
        try:
            inp = page.wait_for_selector(sel, timeout=5000, state='visible')
            if inp:
                inp.triple_click()
                inp.fill(str(days))
                time.sleep(0.5)
                print(f"  Set {days} days")

                # Ensure unit is "Days" not hours/minutes
                for unit_sel in [
                    f'option[value="days"]',
                    f'text=Day',
                    f'li:has-text("Day")',
                    '[role="option"]:has-text("day")',
                ]:
                    try:
                        unit = page.wait_for_selector(unit_sel, timeout=2000, state='visible')
                        if unit:
                            unit.click()
                            print("  Selected 'Days' unit")
                            break
                    except PlaywrightTimeout:
                        continue
                break
        except PlaywrightTimeout:
            continue

    # Save
    try:
        page.wait_for_selector('button:has-text("Save")', timeout=5000).click()
        time.sleep(2)
        ss(page, f'wait_step_saved_{step_label}')
        print(f"  Wait step saved")
        return True
    except PlaywrightTimeout:
        print("  No Save button for wait step")
        return False


def add_update_contact_step(page, attribute, value, step_label):
    """Add 'Update contact attribute' step."""
    print(f"\n  [STEP] Update contact: {attribute} = {value}")

    # Try drag
    dragged = drag_to_canvas(page, 'Update contact', is_trigger=False)
    if not dragged:
        drag_to_canvas(page, 'Update attribute', is_trigger=False)

    time.sleep(1)
    ss(page, f'update_contact_config_open_{step_label}')

    # Configure attribute name
    for sel in [
        'input[placeholder*="attribute" i]',
        'input[name*="attribute"]',
        'select[name*="attribute"]',
        '[class*="attribute"] input',
    ]:
        try:
            el = page.wait_for_selector(sel, timeout=5000, state='visible')
            if el:
                tag = el.evaluate('el => el.tagName').lower()
                if tag == 'select':
                    # Try selecting from dropdown
                    el.select_option(label=attribute)
                else:
                    el.click()
                    el.fill(attribute)
                time.sleep(0.5)
                print(f"  Set attribute name: {attribute}")
                break
        except PlaywrightTimeout:
            continue

    # Set attribute value
    for sel in [
        'input[placeholder*="value" i]',
        'input[name*="value"]',
        '[class*="value"] input',
        'input:last-of-type',
    ]:
        try:
            el = page.wait_for_selector(sel, timeout=4000, state='visible')
            if el:
                el.click()
                el.fill(value)
                time.sleep(0.5)
                print(f"  Set value: {value}")
                break
        except PlaywrightTimeout:
            continue

    ss(page, f'update_contact_configured_{step_label}')

    # Save
    try:
        page.wait_for_selector('button:has-text("Save")', timeout=5000).click()
        time.sleep(2)
        ss(page, f'update_contact_saved_{step_label}')
        return True
    except PlaywrightTimeout:
        print("  No Save button for update contact step")
        return False


def activate_automation(page):
    """Click 'Activate automation' button."""
    print("\n  Activating automation...")
    for sel in [
        'button:has-text("Activate automation")',
        'button:has-text("Activate")',
        '[data-testid*="activate"]',
    ]:
        try:
            btn = page.wait_for_selector(sel, timeout=10000, state='visible')
            btn.click()
            time.sleep(3)
            ss(page, 'after_activate_click')

            # Handle confirmation dialog
            for conf_sel in ['button:has-text("Activate")', 'button:has-text("Confirm")', 'button:has-text("OK")']:
                try:
                    page.wait_for_selector(conf_sel, timeout=5000).click()
                    time.sleep(3)
                    print("  Confirmed activation")
                    break
                except PlaywrightTimeout:
                    continue

            ss(page, 'after_activate_confirm')
            body = canvas_text(page)
            is_active = 'Active' in body and 'Inactive' not in body
            print(f"  Activation result: Active={is_active}")
            return is_active
        except PlaywrightTimeout:
            continue

    print("  Activate button not found")
    ss(page, 'activate_not_found')
    return False


def get_automation_url(page):
    """Return current page URL (automation edit URL)."""
    return page.url


# ─── 4 Workflow Builders ───────────────────────────────────────────────────────

def build_workflow_1(page):
    """AI Partnership Audit — Lead Nurture"""
    name = "AI Partnership Audit — Lead Nurture"
    print(f"\n{'='*60}")
    print(f"WORKFLOW 1: {name}")
    print(f"{'='*60}")
    result = {'name': name, 'status': 'failed', 'url': '', 'notes': []}

    goto_automations(page)
    time.sleep(1)

    if not click_create_automation(page):
        result['notes'].append("Could not click create button")
        ss(page, 'wf1_create_failed')
        return result

    ss(page, 'wf1_editor_loaded')
    time.sleep(2)

    # Set name
    set_automation_name(page, name)
    time.sleep(0.5)
    ss(page, 'wf1_name_set')

    # Trigger: Contact added to list (Enterprise Leads = List 4)
    print("\n  Setting trigger: Contact added to list...")
    click_triggers_tab(page)
    time.sleep(0.5)

    # Look for "Contact added to a list" trigger option
    triggered = False
    for sel in [
        'text=Contact added to a list',
        'li:has-text("Contact added to a list")',
        '[class*="trigger"]:has-text("Contact added")',
        'text=Added to a list',
    ]:
        try:
            t = page.wait_for_selector(sel, timeout=5000)
            if t:
                t.click()
                time.sleep(1.5)
                triggered = True
                print(f"  Clicked trigger via: {sel}")
                break
        except PlaywrightTimeout:
            continue

    if not triggered:
        drag_to_canvas(page, 'Contact added to a list', is_trigger=True)
        triggered = True

    ss(page, 'wf1_trigger_selected')

    # Configure trigger: select Enterprise Leads list
    configure_list_trigger(page, 'Enterprise Leads')
    time.sleep(1)
    ss(page, 'wf1_trigger_configured')

    # Steps: Email 13, Wait 2, Email 14, Wait 2, Email 15, Wait 3, Email 16
    steps = [
        ('email', 13, 'e13'),
        ('wait', 2, 'w2a'),
        ('email', 14, 'e14'),
        ('wait', 2, 'w2b'),
        ('email', 15, 'e15'),
        ('wait', 3, 'w3'),
        ('email', 16, 'e16'),
    ]

    for step_type, value, label in steps:
        if step_type == 'email':
            add_send_email_step(page, value, label)
        else:
            add_wait_step(page, value, label)
        time.sleep(1)

    ss(page, 'wf1_sequence_complete')

    # Activate
    activated = activate_automation(page)
    result['url'] = get_automation_url(page)
    result['status'] = 'activated' if activated else 'built'
    result['notes'].append(f"Activated: {activated}")
    ss(page, 'wf1_FINAL')

    print(f"\n  WF1 Result: {result['status']} | URL: {result['url']}")
    return result


def build_workflow_2(page):
    """Pricing Intent — Awakening Section"""
    name = "Pricing Intent — Awakening Section"
    print(f"\n{'='*60}")
    print(f"WORKFLOW 2: {name}")
    print(f"{'='*60}")
    result = {'name': name, 'status': 'failed', 'url': '', 'notes': []}

    goto_automations(page)
    if not click_create_automation(page):
        result['notes'].append("Could not click create button")
        return result

    ss(page, 'wf2_editor_loaded')
    time.sleep(2)
    set_automation_name(page, name)
    ss(page, 'wf2_name_set')

    # Trigger: Contact triggers an event -> awakening_section_viewed
    print("\n  Setting trigger: Event...")
    click_triggers_tab(page)
    time.sleep(0.5)

    triggered = False
    for sel in [
        'text=A contact triggers an event',
        'text=Contact triggers an event',
        'text=Triggers an event',
        'li:has-text("triggers an event")',
        '[class*="trigger"]:has-text("event")',
    ]:
        try:
            t = page.wait_for_selector(sel, timeout=5000)
            if t:
                t.click()
                time.sleep(1.5)
                triggered = True
                print(f"  Clicked event trigger via: {sel}")
                break
        except PlaywrightTimeout:
            continue

    if not triggered:
        drag_to_canvas(page, 'triggers an event', is_trigger=True)

    ss(page, 'wf2_trigger_selected')
    configure_event_trigger(page, 'awakening_section_viewed')
    ss(page, 'wf2_trigger_configured')

    # Steps: Email 17, Wait 2, Email 18
    steps = [
        ('email', 17, 'e17'),
        ('wait', 2, 'w2'),
        ('email', 18, 'e18'),
    ]

    for step_type, value, label in steps:
        if step_type == 'email':
            add_send_email_step(page, value, label)
        else:
            add_wait_step(page, value, label)
        time.sleep(1)

    ss(page, 'wf2_sequence_complete')
    activated = activate_automation(page)
    result['url'] = get_automation_url(page)
    result['status'] = 'activated' if activated else 'built'
    result['notes'].append(f"Activated: {activated}")
    ss(page, 'wf2_FINAL')

    print(f"\n  WF2 Result: {result['status']} | URL: {result['url']}")
    return result


def build_workflow_3(page):
    """45-Day Inactive Re-engagement"""
    name = "45-Day Inactive Re-engagement"
    print(f"\n{'='*60}")
    print(f"WORKFLOW 3: {name}")
    print(f"{'='*60}")
    result = {'name': name, 'status': 'failed', 'url': '', 'notes': []}

    goto_automations(page)
    if not click_create_automation(page):
        result['notes'].append("Could not click create button")
        return result

    ss(page, 'wf3_editor_loaded')
    time.sleep(2)
    set_automation_name(page, name)
    ss(page, 'wf3_name_set')

    # Trigger: Inactivity on emails
    print("\n  Setting trigger: Inactivity...")
    click_triggers_tab(page)
    time.sleep(0.5)

    triggered = False
    for sel in [
        'text=Inactivity on emails',
        'text=Email inactivity',
        'text=No activity',
        'li:has-text("inactivity" )',
        'li:has-text("Inactivity")',
        '[class*="trigger"]:has-text("nactivity")',
    ]:
        try:
            t = page.wait_for_selector(sel, timeout=5000)
            if t:
                t.click()
                time.sleep(1.5)
                triggered = True
                print(f"  Clicked inactivity trigger via: {sel}")
                break
        except PlaywrightTimeout:
            continue

    if not triggered:
        drag_to_canvas(page, 'Inactivity', is_trigger=True)

    ss(page, 'wf3_trigger_selected')
    configure_inactivity_trigger(page, 45, 'The Neural Feed')
    ss(page, 'wf3_trigger_configured')

    # Steps: Email 19, Wait 7, Email 20, Wait 14, Email 21
    steps = [
        ('email', 19, 'e19'),
        ('wait', 7, 'w7'),
        ('email', 20, 'e20'),
        ('wait', 14, 'w14'),
        ('email', 21, 'e21'),
    ]

    for step_type, value, label in steps:
        if step_type == 'email':
            add_send_email_step(page, value, label)
        else:
            add_wait_step(page, value, label)
        time.sleep(1)

    ss(page, 'wf3_sequence_complete')
    activated = activate_automation(page)
    result['url'] = get_automation_url(page)
    result['status'] = 'activated' if activated else 'built'
    result['notes'].append(f"Activated: {activated}")
    ss(page, 'wf3_FINAL')

    print(f"\n  WF3 Result: {result['status']} | URL: {result['url']}")
    return result


def build_workflow_4(page):
    """Email Reply — High Engagement Tag"""
    name = "Email Reply — High Engagement Tag"
    print(f"\n{'='*60}")
    print(f"WORKFLOW 4: {name}")
    print(f"{'='*60}")
    result = {'name': name, 'status': 'failed', 'url': '', 'notes': []}

    goto_automations(page)
    if not click_create_automation(page):
        result['notes'].append("Could not click create button")
        return result

    ss(page, 'wf4_editor_loaded')
    time.sleep(2)
    set_automation_name(page, name)
    ss(page, 'wf4_name_set')

    # Trigger: Contact triggers an event -> email_replied
    print("\n  Setting trigger: Event email_replied...")
    click_triggers_tab(page)
    time.sleep(0.5)

    triggered = False
    for sel in [
        'text=A contact triggers an event',
        'text=Contact triggers an event',
        'text=Triggers an event',
        'li:has-text("triggers an event")',
        '[class*="trigger"]:has-text("event")',
    ]:
        try:
            t = page.wait_for_selector(sel, timeout=5000)
            if t:
                t.click()
                time.sleep(1.5)
                triggered = True
                print(f"  Clicked event trigger via: {sel}")
                break
        except PlaywrightTimeout:
            continue

    if not triggered:
        drag_to_canvas(page, 'triggers an event', is_trigger=True)

    ss(page, 'wf4_trigger_selected')
    configure_event_trigger(page, 'email_replied')
    ss(page, 'wf4_trigger_configured')

    # Step: Update contact attribute ENGAGEMENT_LEVEL = "high"
    add_update_contact_step(page, 'ENGAGEMENT_LEVEL', 'high', 'engagement')
    time.sleep(1)

    ss(page, 'wf4_step_complete')
    activated = activate_automation(page)
    result['url'] = get_automation_url(page)
    result['status'] = 'activated' if activated else 'built'
    result['notes'].append(f"Activated: {activated}")
    ss(page, 'wf4_FINAL')

    print(f"\n  WF4 Result: {result['status']} | URL: {result['url']}")
    return result


# ─── Main Orchestrator ─────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("Brevo 4 Automation Workflows Builder")
    print("=" * 65)
    print(f"Screenshot dir: {SS_DIR}")
    print(f"Login email: {BREVO_EMAIL}")

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )

        # Try saved session first
        session_state = None
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE) as f:
                    session_state = json.load(f)
                print(f"Saved session found: {len(session_state.get('cookies', []))} cookies")
            except Exception as e:
                print(f"Session load error: {e}")

        if session_state:
            ctx = browser.new_context(
                viewport={'width': 1600, 'height': 900},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36',
                storage_state=session_state,
            )
            page = ctx.new_page()
            page.set_default_timeout(30000)

            if not is_logged_in(page):
                print("Saved session expired. Doing fresh login...")
                page.close()
                ctx.close()
                session_state = None

        if not session_state:
            ctx = browser.new_context(
                viewport={'width': 1600, 'height': 900},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
            )
            page = ctx.new_page()
            page.set_default_timeout(30000)

            # Try primary email first
            login_ok = do_login(page, BREVO_EMAIL, BREVO_PASSWORD)

            if login_ok == 'captcha':
                print("\nCAPTCHA detected - cannot proceed automatically")
                ss(page, 'CAPTCHA_BLOCKER')
                browser.close()
                return [{'name': 'ALL', 'status': 'blocked_by_captcha', 'url': '', 'notes': ['CAPTCHA on login page']}]

            if not login_ok:
                print(f"\nPrimary email failed. Trying alternate: {BREVO_EMAIL_ALT}")
                login_ok = do_login(page, BREVO_EMAIL_ALT, BREVO_PASSWORD)

            if not login_ok:
                print("\nERROR: Both login attempts failed")
                browser.close()
                return [{'name': 'ALL', 'status': 'login_failed', 'url': '', 'notes': ['Login failed with both emails']}]

            # Save new session
            save_session(ctx)
            print("New session saved")

        ss(page, 'logged_in_dashboard')
        print(f"\nLogged in! URL: {page.url}")

        # Build all 4 workflows
        try:
            r1 = build_workflow_1(page)
            results.append(r1)
        except Exception as e:
            print(f"WF1 ERROR: {e}")
            ss(page, 'wf1_exception')
            results.append({'name': 'AI Partnership Audit — Lead Nurture', 'status': 'exception', 'url': '', 'notes': [str(e)]})

        try:
            r2 = build_workflow_2(page)
            results.append(r2)
        except Exception as e:
            print(f"WF2 ERROR: {e}")
            ss(page, 'wf2_exception')
            results.append({'name': 'Pricing Intent — Awakening Section', 'status': 'exception', 'url': '', 'notes': [str(e)]})

        try:
            r3 = build_workflow_3(page)
            results.append(r3)
        except Exception as e:
            print(f"WF3 ERROR: {e}")
            ss(page, 'wf3_exception')
            results.append({'name': '45-Day Inactive Re-engagement', 'status': 'exception', 'url': '', 'notes': [str(e)]})

        try:
            r4 = build_workflow_4(page)
            results.append(r4)
        except Exception as e:
            print(f"WF4 ERROR: {e}")
            ss(page, 'wf4_exception')
            results.append({'name': 'Email Reply — High Engagement Tag', 'status': 'exception', 'url': '', 'notes': [str(e)]})

        browser.close()

    # Summary
    print("\n" + "=" * 65)
    print("FINAL RESULTS")
    print("=" * 65)
    for r in results:
        status_icon = "OK" if r['status'] in ('activated', 'built') else "FAIL"
        print(f"[{status_icon}] {r['name']}")
        print(f"     Status: {r['status']}")
        print(f"     URL: {r['url']}")
        print(f"     Notes: {r['notes']}")

    # Save results JSON
    results_path = f"{SS_DIR}/results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved: {results_path}")

    return results


if __name__ == '__main__':
    main()
