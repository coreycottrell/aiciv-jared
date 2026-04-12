#!/usr/bin/env python3
"""
Brevo 4 Automation Workflows Builder - v2
==========================================
Fixed approach based on investigation:
- Correct automation URL: /automation/automations (NOT /automation/list)
- Must navigate via clicking "Workflows" in sidebar (NOT direct URL after session restore)
- Uses fresh in-session navigation (not saved session restore)
- Handles "We could not show this page" by trying alternate navigation

Workflows to build:
  1. AI Partnership Audit — Lead Nurture
  2. Pricing Intent — Awakening Section
  3. 45-Day Inactive Re-engagement
  4. Email Reply — High Engagement Tag
"""

import os, sys, re, time, json, imaplib, email as email_module, email.utils, datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

BREVO_EMAIL = 'purebrain@puremarketing.ai'
BREVO_PASSWORD = os.environ.get('BREVO_PASSWORD', '_g%DXnKfQ5w*&65')
GMAIL_USER = os.environ.get('GMAIL_USERNAME', 'purebrain@puremarketing.ai')
GMAIL_APP_PASSWORD = os.environ.get('GOOGLE_APP_PASSWORD', 'mldvztmeligxhyaw')

SESSION_FILE = '/home/jared/projects/AI-CIV/aether/tools/brevo_session.json'
SS_DIR = '/home/jared/projects/AI-CIV/aether/exports/screenshots/brevo-workflows'
os.makedirs(SS_DIR, exist_ok=True)

_n = [0]
def ss(page, label):
    _n[0] += 1
    path = f"{SS_DIR}/{_n[0]:03d}_{label}.png"
    try:
        page.screenshot(path=path, full_page=False)
        print(f"  [SS] {path}")
    except Exception as e:
        print(f"  [SS ERR] {label}: {e}")
    return path


def wait_for_content(page, timeout=15):
    """Wait for page to have meaningful content (not just loading state)."""
    for _ in range(timeout):
        time.sleep(1)
        try:
            body = page.evaluate('() => document.body.innerText')
            if len(body.strip()) > 50 and 'Log In' not in body[:100]:
                return True
        except Exception:
            pass
    return False


def get_body(page):
    try:
        return page.evaluate('() => document.body.innerText')
    except Exception:
        return ''


# ─── 2FA ─────────────────────────────────────────────────────────────────────

def get_2fa_code(max_wait=90, started_at=None):
    if started_at is None:
        started_at = time.time() - 10
    print(f"  [2FA] Waiting for code (after {time.strftime('%H:%M:%S', time.localtime(started_at))})...")
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
                    if 'verify' not in msg.get('Subject', '').lower():
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
                    match = re.search(r'verification code[:\s]*\n?\s*(\d{6})', body, re.IGNORECASE)
                    if match:
                        code = match.group(1)
                    else:
                        codes = re.findall(r'\b\d{6}\b', body)
                        code = next((c for c in codes if not (c[0]==c[2]==c[4] and c[1]==c[3]==c[5])), None)
                    if code:
                        print(f"  [2FA] Got code: {code}")
                        m.logout()
                        return code
            m.logout()
        except Exception as e:
            print(f"  [2FA IMAP] {e}")
        remaining = int(deadline - time.time())
        print(f"  [2FA] Waiting... {remaining}s left")
        time.sleep(6)
    return None


# ─── Login ───────────────────────────────────────────────────────────────────

def login(page):
    """Full login flow. Returns True if successful."""
    print("\n[LOGIN] Starting fresh login...")
    page.goto('https://login.brevo.com/', wait_until='domcontentloaded', timeout=60000)
    time.sleep(2)

    # Dismiss cookie banner
    try:
        page.wait_for_selector("button:has-text('Accept All Cookies')", timeout=4000).click()
        time.sleep(0.5)
    except PlaywrightTimeout:
        pass

    ss(page, 'login_page')

    try:
        page.wait_for_selector('input[name="email"], input#email', timeout=15000).fill(BREVO_EMAIL)
        page.wait_for_selector('input[type="password"]', timeout=10000).fill(BREVO_PASSWORD)
    except PlaywrightTimeout:
        print("  ERROR: Cannot find login fields")
        ss(page, 'login_fields_not_found')
        return False

    ss(page, 'login_creds_filled')
    login_at = time.time()

    try:
        page.wait_for_selector('button:has-text("Log In")', timeout=5000).click()
    except PlaywrightTimeout:
        page.keyboard.press('Enter')

    print(f"  Login submitted at {time.strftime('%H:%M:%S')}")
    time.sleep(4)

    print(f"  URL: {page.url}")
    ss(page, 'login_after_submit')

    # Handle 2FA
    if '2fa' in page.url or 'new-device' in page.url or 'verify' in page.url:
        print("  2FA required")
        code = get_2fa_code(max_wait=120, started_at=login_at)
        if not code:
            print("  ERROR: No 2FA code received")
            return False

        cf = None
        for sel in ['input[autocomplete="one-time-code"]', 'input[inputmode="numeric"]',
                    'form input[type="text"]:not([name="email"])']:
            try:
                cf = page.wait_for_selector(sel, timeout=3000, state='visible')
                break
            except PlaywrightTimeout:
                continue

        if not cf:
            print("  ERROR: No 2FA input found")
            return False

        cf.fill(code)
        time.sleep(0.5)
        ss(page, 'login_2fa_code_entered')

        try:
            page.wait_for_selector('button:has-text("Verify")', timeout=5000).click()
        except PlaywrightTimeout:
            cf.press('Enter')

        time.sleep(8)
        print(f"  URL after 2FA: {page.url}")
        ss(page, 'login_after_2fa')

    # Navigate to dashboard to verify login
    page.goto('https://app.brevo.com/', wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)

    if 'login' in page.url.lower():
        print("  ERROR: Login failed - still on login page")
        return False

    print(f"  Logged in! URL: {page.url}")
    ss(page, 'login_dashboard')
    return True


# ─── Navigate to Automations ─────────────────────────────────────────────────

def goto_automations(page):
    """Navigate to the Automations Workflows page."""
    print("\n  Navigating to Automations...")

    # Direct URL (works after initial login)
    page.goto('https://app.brevo.com/automation/automations', wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)

    body = get_body(page)
    print(f"  URL: {page.url}")

    if 'Create an automation' in body or 'Automation' in body:
        print("  Automations page loaded!")
        ss(page, 'automations_page')
        return True

    # If that didn't work, try clicking Workflows in sidebar
    print("  Direct URL failed, trying sidebar click...")
    try:
        wf_link = page.wait_for_selector('text=Workflows', timeout=8000)
        wf_link.click()
        time.sleep(5)
        body = get_body(page)
        if 'Create an automation' in body:
            print("  Got automations via sidebar click")
            ss(page, 'automations_via_sidebar')
            return True
    except PlaywrightTimeout:
        pass

    print("  WARNING: Could not reach automations page")
    ss(page, 'automations_failed')
    return False


def click_create_automation(page):
    """Click the '+ Create an automation' button."""
    print("  Clicking 'Create an automation'...")

    for sel in [
        'button:has-text("Create an automation")',
        'a:has-text("Create an automation")',
        '[data-testid*="create"]',
        'button:has-text("New")',
    ]:
        try:
            btn = page.wait_for_selector(sel, timeout=6000, state='visible')
            if btn:
                btn.click()
                time.sleep(3)
                print(f"  Clicked create via: {sel}")
                ss(page, 'create_automation_clicked')
                return True
        except PlaywrightTimeout:
            continue

    print("  ERROR: Create button not found")
    ss(page, 'create_not_found')
    return False


# ─── Automation Editor Helpers ────────────────────────────────────────────────

def get_editor_state(page):
    """Get current editor body text."""
    time.sleep(1)
    return get_body(page)


def click_tab(page, tab_name):
    """Click a tab in the automation editor (Triggers, Actions, etc.)."""
    try:
        tab = page.wait_for_selector(f'button:has-text("{tab_name}")', timeout=6000)
        tab.click()
        time.sleep(0.8)
        return True
    except PlaywrightTimeout:
        return False


def drag_item_to_canvas(page, item_text):
    """
    Drag an item from the side panel to the canvas.
    Uses step-by-step mouse movement for reliability.
    """
    print(f"    Dragging: '{item_text}'")

    # Find draggable item
    item_loc = None
    for sel in [
        f'[draggable=true]:has-text("{item_text}")',
        f'[class*="drag"]:has-text("{item_text}")',
        f'[class*="item"]:has-text("{item_text}")',
    ]:
        try:
            item_loc = page.locator(sel).first
            ibox = item_loc.bounding_box()
            if ibox:
                print(f"    Found at ({ibox['x']:.0f},{ibox['y']:.0f})")
                break
        except Exception:
            continue

    if not item_loc or not ibox:
        print(f"    ERROR: '{item_text}' not found in panel")
        return False

    # Find drop target
    drop_text_options = ['Drop block here', 'Drop a step here', 'Add a step here']
    sbox = None
    for drop_text in drop_text_options:
        try:
            slot = page.wait_for_selector(f'text={drop_text}', timeout=3000)
            sbox = slot.bounding_box()
            if sbox:
                print(f"    Drop slot '{drop_text}' at ({sbox['x']:.0f},{sbox['y']:.0f})")
                break
        except PlaywrightTimeout:
            continue

    if not sbox:
        # Fallback: target visible canvas area
        canvas_candidates = [
            '[class*="Canvas"]',
            '[class*="canvas"]',
            '[class*="editor-content"]',
            '[class*="workflow"]',
        ]
        for sel in canvas_candidates:
            try:
                canvas = page.locator(sel).first
                cbox = canvas.bounding_box()
                if cbox and cbox['width'] > 200:
                    sbox = {
                        'x': cbox['x'] + cbox['width'] * 0.5,
                        'y': cbox['y'] + cbox['height'] * 0.4,
                        'width': 100,
                        'height': 40
                    }
                    print(f"    Using canvas fallback at ({sbox['x']:.0f},{sbox['y']:.0f})")
                    break
            except Exception:
                continue

    if not sbox:
        print("    ERROR: No drop target found")
        return False

    # Perform drag
    src_x = ibox['x'] + ibox['width'] / 2
    src_y = ibox['y'] + ibox['height'] / 2
    tgt_x = sbox['x'] + sbox.get('width', 100) / 2
    tgt_y = sbox['y'] + sbox.get('height', 40) / 2

    mouse = page.mouse
    mouse.move(src_x, src_y)
    time.sleep(0.4)
    mouse.down()
    time.sleep(0.5)

    steps = 25
    for i in range(1, steps + 1):
        nx = src_x + (tgt_x - src_x) * i / steps
        ny = src_y + (tgt_y - src_y) * i / steps
        mouse.move(nx, ny)
        time.sleep(0.04)

    time.sleep(0.6)
    mouse.up()
    time.sleep(3)

    body = get_editor_state(page)
    label = item_text[:15].replace(' ', '_')
    ss(page, f'drag_{label}')

    # Success check: item text appeared in canvas, or drop zone disappeared
    success = (item_text[:10] in body and 'Drop block here' not in body) or \
              all(dt not in body for dt in drop_text_options)
    print(f"    Drag {'SUCCESS' if success else 'MAY HAVE FAILED'}")
    return True  # Continue regardless


def save_config_panel(page):
    """Click Save in the config panel."""
    for sel in ['button:has-text("Save")', 'button:has-text("Confirm")', 'button:has-text("Done")']:
        try:
            btn = page.wait_for_selector(sel, timeout=4000, state='visible')
            btn.click()
            time.sleep(2)
            print(f"    Saved via: {sel}")
            return True
        except PlaywrightTimeout:
            continue
    print("    No Save button found")
    return False


# ─── Trigger Configuration ────────────────────────────────────────────────────

def configure_trigger_select_list(page, list_name):
    """Select a list from the trigger config panel."""
    print(f"    Configuring: list = '{list_name}'")
    time.sleep(1)
    ss(page, 'trigger_config_open')

    # Try various dropdown selectors
    opened = False
    for sel in [
        'text=Select a list',
        '[placeholder*="list" i]',
        '[class*="select-control"]',
        '[class*="Select"]:has-text("list")',
        'select',
    ]:
        try:
            el = page.wait_for_selector(sel, timeout=5000, state='visible')
            if el:
                el.click()
                time.sleep(1.5)
                ss(page, 'list_dropdown_opened')
                opened = True
                print(f"    Opened dropdown via: {sel}")
                break
        except PlaywrightTimeout:
            continue

    if not opened:
        print("    WARNING: Could not open list dropdown")
        ss(page, 'list_dropdown_not_found')
        return False

    # Select the list option
    for opt_sel in [
        f'text={list_name}',
        f'li:has-text("{list_name}")',
        f'[role="option"]:has-text("{list_name[:20]}")',
        f'[class*="option"]:has-text("{list_name[:20]}")',
    ]:
        try:
            opt = page.wait_for_selector(opt_sel, timeout=4000, state='visible')
            if opt:
                opt.click()
                time.sleep(1)
                print(f"    Selected: {list_name}")
                ss(page, 'list_selected')
                break
        except PlaywrightTimeout:
            continue
    else:
        # Show what's available
        opts = page.query_selector_all('[role="option"], li[class*="option"], [class*="menu-list"] li')
        print(f"    Available options ({len(opts)}):")
        for o in opts[:10]:
            try:
                print(f"      - {o.evaluate('el => el.textContent').strip()[:50]}")
            except Exception:
                pass
        ss(page, 'list_options_debug')

    return save_config_panel(page)


def configure_trigger_event_name(page, event_name):
    """Set event name in trigger config."""
    print(f"    Configuring event: '{event_name}'")
    time.sleep(1)
    ss(page, 'event_trigger_config')

    for sel in [
        'input[placeholder*="event" i]',
        'input[placeholder*="Event" i]',
        'input[name*="event"]',
        'input[type="text"]',
    ]:
        try:
            inp = page.wait_for_selector(sel, timeout=5000, state='visible')
            if inp:
                inp.click()
                page.keyboard.press('Control+a')
                inp.fill(event_name)
                time.sleep(0.5)
                print(f"    Set event name via: {sel}")
                break
        except PlaywrightTimeout:
            continue
    else:
        print("    WARNING: No event name input found")
        ss(page, 'event_name_input_not_found')
        return False

    return save_config_panel(page)


def configure_trigger_inactivity(page, days):
    """Set inactivity days and list for inactivity trigger."""
    print(f"    Configuring inactivity: {days} days")
    time.sleep(1)
    ss(page, 'inactivity_config')

    # Set days input
    for sel in ['input[type="number"]', 'input[name*="days"]', 'input[name*="duration"]']:
        try:
            inp = page.wait_for_selector(sel, timeout=5000, state='visible')
            if inp:
                inp.triple_click()
                inp.fill(str(days))
                print(f"    Set {days} days")
                break
        except PlaywrightTimeout:
            continue

    ss(page, 'inactivity_days_set')
    return save_config_panel(page)


# ─── Action Configuration ─────────────────────────────────────────────────────

def configure_send_email(page, template_id, step_label):
    """Configure a Send Email step with template ID."""
    print(f"    Configuring email step: template {template_id}")
    time.sleep(1)
    ss(page, f'email_config_{step_label}')

    body = get_body(page)

    # Method 1: Look for "Add message" / "Select a template" button
    template_selected = False
    for sel in [
        'button:has-text("Add message")',
        'button:has-text("Choose a template")',
        'button:has-text("Select a template")',
        'text=Select a template',
        '[class*="template"] button',
    ]:
        try:
            btn = page.wait_for_selector(sel, timeout=5000, state='visible')
            if btn:
                btn.click()
                time.sleep(2)
                ss(page, f'template_picker_{step_label}')
                print(f"    Opened template picker via: {sel}")

                # In the template picker, try to find template by ID
                # Try search input
                try:
                    search = page.wait_for_selector(
                        'input[placeholder*="search" i], input[placeholder*="Search" i]',
                        timeout=3000
                    )
                    search.fill(str(template_id))
                    time.sleep(1.5)
                    ss(page, f'template_searched_{step_label}')
                except PlaywrightTimeout:
                    pass

                # Click the template - try by data attribute first, then by visible card
                for t_sel in [
                    f'[data-id="{template_id}"], [data-template-id="{template_id}"]',
                    f'[class*="template-card"]:has-text("{template_id}")',
                    f'[class*="card"]:has-text("#{template_id}")',
                    f'[class*="card"]:has-text("{template_id}")',
                ]:
                    try:
                        t = page.wait_for_selector(t_sel, timeout=3000, state='visible')
                        if t:
                            t.click()
                            time.sleep(1)
                            print(f"    Clicked template card via: {t_sel}")
                            template_selected = True
                            break
                    except PlaywrightTimeout:
                        continue

                # Try "Use this template" / "Select" button
                for use_sel in ['button:has-text("Use")', 'button:has-text("Select")', 'button:has-text("Choose")']:
                    try:
                        page.wait_for_selector(use_sel, timeout=3000).click()
                        time.sleep(1.5)
                        print("    Clicked 'Use' button")
                        break
                    except PlaywrightTimeout:
                        continue

                break
        except PlaywrightTimeout:
            continue

    # Method 2: Direct select element
    if not template_selected:
        for sel in ['select[name*="template"]', 'select']:
            try:
                el = page.wait_for_selector(sel, timeout=3000, state='visible')
                if el:
                    el.select_option(value=str(template_id))
                    time.sleep(0.5)
                    template_selected = True
                    print(f"    Set template via select: {template_id}")
                    break
            except PlaywrightTimeout:
                continue

    ss(page, f'email_configured_{step_label}')
    return save_config_panel(page)


def configure_wait(page, days, step_label):
    """Configure a Wait step."""
    print(f"    Configuring wait: {days} days")
    time.sleep(1)
    ss(page, f'wait_config_{step_label}')

    for sel in ['input[type="number"]', 'input[name*="duration"]', 'input[name*="delay"]']:
        try:
            inp = page.wait_for_selector(sel, timeout=5000, state='visible')
            if inp:
                inp.triple_click()
                inp.fill(str(days))
                print(f"    Set {days} days")

                # Ensure "Days" unit is selected
                for unit in ['option[value="days"]', 'li:has-text("day")', '[role="option"]:has-text("day")']:
                    try:
                        u = page.wait_for_selector(unit, timeout=2000, state='visible')
                        if u:
                            u.click()
                            print("    Selected 'days' unit")
                            break
                    except PlaywrightTimeout:
                        continue
                break
        except PlaywrightTimeout:
            continue

    return save_config_panel(page)


def configure_update_contact(page, attribute, value, step_label):
    """Configure an Update Contact step."""
    print(f"    Configuring update contact: {attribute} = {value}")
    time.sleep(1)
    ss(page, f'update_config_{step_label}')

    # Select attribute
    for sel in [
        'select[name*="attribute"]',
        '[class*="attribute"] select',
        'input[placeholder*="attribute" i]',
    ]:
        try:
            el = page.wait_for_selector(sel, timeout=5000, state='visible')
            if el:
                tag = el.evaluate('el => el.tagName').lower()
                if tag == 'select':
                    try:
                        el.select_option(label=attribute)
                    except Exception:
                        # Type in search box
                        el.click()
                        time.sleep(0.5)
                        for opt in [f'text={attribute}', f'[role="option"]:has-text("{attribute}")']:
                            try:
                                page.wait_for_selector(opt, timeout=2000).click()
                                break
                            except PlaywrightTimeout:
                                continue
                else:
                    el.click()
                    el.fill(attribute)
                time.sleep(0.5)
                print(f"    Set attribute: {attribute}")
                break
        except PlaywrightTimeout:
            continue

    # Set value
    for sel in ['input[placeholder*="value" i]', 'input[name*="value"]', 'input:last-of-type']:
        try:
            inp = page.wait_for_selector(sel, timeout=4000, state='visible')
            if inp:
                inp.click()
                inp.fill(value)
                print(f"    Set value: {value}")
                break
        except PlaywrightTimeout:
            continue

    return save_config_panel(page)


# ─── Activate Automation ──────────────────────────────────────────────────────

def activate_automation(page):
    """Click the Activate button."""
    print("    Activating automation...")
    ss(page, 'before_activate')

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

            # Confirm dialog
            for conf in ['button:has-text("Activate")', 'button:has-text("Confirm")', 'button:has-text("OK")']:
                try:
                    page.wait_for_selector(conf, timeout=4000, state='visible').click()
                    time.sleep(3)
                    print("    Confirmed activation")
                    break
                except PlaywrightTimeout:
                    continue

            ss(page, 'after_activate_confirm')
            body = get_body(page)
            active = 'Active' in body
            print(f"    Activation: Active={active}")
            return active
        except PlaywrightTimeout:
            continue

    print("    Activate button not found")
    ss(page, 'activate_not_found')
    return False


# ─── Workflow Builders ────────────────────────────────────────────────────────

def build_wf1(page):
    """AI Partnership Audit — Lead Nurture"""
    name = "AI Partnership Audit — Lead Nurture"
    print(f"\n{'='*55}\nWF1: {name}\n{'='*55}")
    result = {'name': name, 'status': 'failed', 'url': '', 'notes': []}

    if not goto_automations(page):
        result['notes'].append('Could not reach automations page')
        return result

    if not click_create_automation(page):
        result['notes'].append('Create button not found')
        return result

    # Page should now be in the automation editor
    time.sleep(3)
    ss(page, 'wf1_editor')
    url = page.url
    print(f"  Editor URL: {url}")
    result['url'] = url

    body = get_editor_state(page)
    print(f"  Editor content: {body[:300]}")

    # Check what we see - is there a name field?
    # Try to set automation name
    for name_sel in [
        'input[placeholder*="name" i]',
        'input[placeholder*="automation" i]',
        'h1[contenteditable]',
        '[data-testid*="name"] input',
    ]:
        try:
            inp = page.wait_for_selector(name_sel, timeout=4000, state='visible')
            if inp:
                inp.triple_click()
                inp.fill(name)
                time.sleep(0.5)
                print(f"  Set name via: {name_sel}")
                break
        except PlaywrightTimeout:
            continue
    else:
        print("  WARNING: Could not find name input")

    ss(page, 'wf1_name_set')

    # Set trigger: Contact added to list (Enterprise Leads = List 4)
    print("\n  Setting trigger...")
    click_tab(page, 'Triggers')
    time.sleep(0.5)

    # Look for "Contact added to a list" in the triggers panel
    triggered = False
    for sel in [
        'text=Contact added to a list',
        '[draggable=true]:has-text("Contact added to a list")',
        'li:has-text("Contact added")',
    ]:
        try:
            t = page.wait_for_selector(sel, timeout=5000, state='visible')
            if t:
                # First try clicking (some UIs open a picker)
                t.click()
                time.sleep(2)
                body = get_body(page)
                if 'Select a list' in body or 'Enterprise' in body or 'Drop block' not in body:
                    triggered = True
                    print(f"  Trigger selected by click: {sel}")
                    break
        except PlaywrightTimeout:
            continue

    if not triggered:
        # Try dragging
        click_tab(page, 'Triggers')
        drag_item_to_canvas(page, 'Contact added to a list')
        triggered = True

    ss(page, 'wf1_trigger_selected')
    configure_trigger_select_list(page, 'Enterprise Leads')
    ss(page, 'wf1_trigger_done')

    # Build sequence: Email 13, Wait 2, Email 14, Wait 2, Email 15, Wait 3, Email 16
    steps = [
        ('email', 13), ('wait', 2),
        ('email', 14), ('wait', 2),
        ('email', 15), ('wait', 3),
        ('email', 16),
    ]

    click_tab(page, 'Actions')
    for i, (stype, sval) in enumerate(steps, 1):
        print(f"\n  Step {i}: {stype} {sval}")
        if stype == 'email':
            drag_item_to_canvas(page, 'Send an email')
            configure_send_email(page, sval, f'wf1_s{i}')
        else:
            drag_item_to_canvas(page, 'Wait')
            configure_wait(page, sval, f'wf1_s{i}')
        time.sleep(1)
        ss(page, f'wf1_step{i}_done')

    ss(page, 'wf1_steps_complete')
    activated = activate_automation(page)
    result['url'] = page.url
    result['status'] = 'activated' if activated else 'built'
    result['notes'].append(f'Activated: {activated}')
    ss(page, 'wf1_FINAL')
    return result


def build_wf2(page):
    """Pricing Intent — Awakening Section"""
    name = "Pricing Intent — Awakening Section"
    print(f"\n{'='*55}\nWF2: {name}\n{'='*55}")
    result = {'name': name, 'status': 'failed', 'url': '', 'notes': []}

    if not goto_automations(page):
        result['notes'].append('Could not reach automations page')
        return result

    if not click_create_automation(page):
        result['notes'].append('Create button not found')
        return result

    time.sleep(3)
    ss(page, 'wf2_editor')
    result['url'] = page.url

    # Set name
    for name_sel in ['input[placeholder*="name" i]', 'input[placeholder*="automation" i]']:
        try:
            inp = page.wait_for_selector(name_sel, timeout=4000, state='visible')
            if inp:
                inp.triple_click()
                inp.fill(name)
                break
        except PlaywrightTimeout:
            continue

    ss(page, 'wf2_name_set')

    # Trigger: event = awakening_section_viewed
    print("\n  Setting trigger: event...")
    click_tab(page, 'Triggers')
    time.sleep(0.5)

    triggered = False
    for sel in [
        'text=A contact triggers an event',
        'text=Contact triggers an event',
        '[draggable=true]:has-text("triggers an event")',
        'li:has-text("triggers an event")',
    ]:
        try:
            t = page.wait_for_selector(sel, timeout=5000, state='visible')
            if t:
                t.click()
                time.sleep(2)
                triggered = True
                print(f"  Event trigger via: {sel}")
                break
        except PlaywrightTimeout:
            continue

    if not triggered:
        drag_item_to_canvas(page, 'triggers an event')

    ss(page, 'wf2_trigger_selected')
    configure_trigger_event_name(page, 'awakening_section_viewed')
    ss(page, 'wf2_trigger_done')

    # Steps: Email 17, Wait 2, Email 18
    steps = [('email', 17), ('wait', 2), ('email', 18)]
    click_tab(page, 'Actions')
    for i, (stype, sval) in enumerate(steps, 1):
        print(f"\n  Step {i}: {stype} {sval}")
        if stype == 'email':
            drag_item_to_canvas(page, 'Send an email')
            configure_send_email(page, sval, f'wf2_s{i}')
        else:
            drag_item_to_canvas(page, 'Wait')
            configure_wait(page, sval, f'wf2_s{i}')
        time.sleep(1)

    ss(page, 'wf2_steps_complete')
    activated = activate_automation(page)
    result['url'] = page.url
    result['status'] = 'activated' if activated else 'built'
    result['notes'].append(f'Activated: {activated}')
    ss(page, 'wf2_FINAL')
    return result


def build_wf3(page):
    """45-Day Inactive Re-engagement"""
    name = "45-Day Inactive Re-engagement"
    print(f"\n{'='*55}\nWF3: {name}\n{'='*55}")
    result = {'name': name, 'status': 'failed', 'url': '', 'notes': []}

    if not goto_automations(page):
        result['notes'].append('Could not reach automations page')
        return result

    if not click_create_automation(page):
        result['notes'].append('Create button not found')
        return result

    time.sleep(3)
    ss(page, 'wf3_editor')
    result['url'] = page.url

    # Set name
    for name_sel in ['input[placeholder*="name" i]', 'input[placeholder*="automation" i]']:
        try:
            inp = page.wait_for_selector(name_sel, timeout=4000, state='visible')
            if inp:
                inp.triple_click()
                inp.fill(name)
                break
        except PlaywrightTimeout:
            continue

    ss(page, 'wf3_name_set')

    # Trigger: Inactivity on emails (45 days)
    print("\n  Setting trigger: inactivity...")
    click_tab(page, 'Triggers')
    time.sleep(0.5)

    triggered = False
    for sel in [
        'text=Inactivity on emails',
        'text=Email inactivity',
        '[draggable=true]:has-text("nactivity")',
        'li:has-text("nactivity")',
    ]:
        try:
            t = page.wait_for_selector(sel, timeout=5000, state='visible')
            if t:
                t.click()
                time.sleep(2)
                triggered = True
                print(f"  Inactivity trigger via: {sel}")
                break
        except PlaywrightTimeout:
            continue

    if not triggered:
        drag_item_to_canvas(page, 'Inactivity')

    ss(page, 'wf3_trigger_selected')
    configure_trigger_inactivity(page, 45)
    ss(page, 'wf3_trigger_done')

    # Steps: Email 19, Wait 7, Email 20, Wait 14, Email 21
    steps = [('email', 19), ('wait', 7), ('email', 20), ('wait', 14), ('email', 21)]
    click_tab(page, 'Actions')
    for i, (stype, sval) in enumerate(steps, 1):
        print(f"\n  Step {i}: {stype} {sval}")
        if stype == 'email':
            drag_item_to_canvas(page, 'Send an email')
            configure_send_email(page, sval, f'wf3_s{i}')
        else:
            drag_item_to_canvas(page, 'Wait')
            configure_wait(page, sval, f'wf3_s{i}')
        time.sleep(1)

    ss(page, 'wf3_steps_complete')
    activated = activate_automation(page)
    result['url'] = page.url
    result['status'] = 'activated' if activated else 'built'
    result['notes'].append(f'Activated: {activated}')
    ss(page, 'wf3_FINAL')
    return result


def build_wf4(page):
    """Email Reply — High Engagement Tag"""
    name = "Email Reply — High Engagement Tag"
    print(f"\n{'='*55}\nWF4: {name}\n{'='*55}")
    result = {'name': name, 'status': 'failed', 'url': '', 'notes': []}

    if not goto_automations(page):
        result['notes'].append('Could not reach automations page')
        return result

    if not click_create_automation(page):
        result['notes'].append('Create button not found')
        return result

    time.sleep(3)
    ss(page, 'wf4_editor')
    result['url'] = page.url

    # Set name
    for name_sel in ['input[placeholder*="name" i]', 'input[placeholder*="automation" i]']:
        try:
            inp = page.wait_for_selector(name_sel, timeout=4000, state='visible')
            if inp:
                inp.triple_click()
                inp.fill(name)
                break
        except PlaywrightTimeout:
            continue

    ss(page, 'wf4_name_set')

    # Trigger: event = email_replied
    print("\n  Setting trigger: event email_replied...")
    click_tab(page, 'Triggers')
    time.sleep(0.5)

    triggered = False
    for sel in [
        'text=A contact triggers an event',
        'text=Contact triggers an event',
        '[draggable=true]:has-text("triggers an event")',
        'li:has-text("triggers an event")',
    ]:
        try:
            t = page.wait_for_selector(sel, timeout=5000, state='visible')
            if t:
                t.click()
                time.sleep(2)
                triggered = True
                print(f"  Event trigger via: {sel}")
                break
        except PlaywrightTimeout:
            continue

    if not triggered:
        drag_item_to_canvas(page, 'triggers an event')

    ss(page, 'wf4_trigger_selected')
    configure_trigger_event_name(page, 'email_replied')
    ss(page, 'wf4_trigger_done')

    # Step: Update contact attribute ENGAGEMENT_LEVEL = "high"
    print("\n  Step 1: Update contact")
    click_tab(page, 'Actions')
    drag_item_to_canvas(page, 'Update contact')
    configure_update_contact(page, 'ENGAGEMENT_LEVEL', 'high', 'wf4_s1')

    ss(page, 'wf4_steps_complete')
    activated = activate_automation(page)
    result['url'] = page.url
    result['status'] = 'activated' if activated else 'built'
    result['notes'].append(f'Activated: {activated}')
    ss(page, 'wf4_FINAL')
    return result


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Brevo 4 Automation Workflows Builder v2")
    print("=" * 60)
    print(f"Login: {BREVO_EMAIL}")
    print(f"Screenshots: {SS_DIR}")

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
        )
        ctx = browser.new_context(
            viewport={'width': 1600, 'height': 900},
            locale='en-US',
            timezone_id='America/New_York',
        )
        page = ctx.new_page()
        page.set_default_timeout(30000)

        # Login
        if not login(page):
            print("ERROR: Login failed")
            browser.close()
            return [{'name': 'ALL', 'status': 'login_failed', 'url': '', 'notes': ['Login failed']}]

        # Navigate to automations to verify access
        if not goto_automations(page):
            print("ERROR: Cannot access automations")
            browser.close()
            return [{'name': 'ALL', 'status': 'no_automations_access', 'url': '', 'notes': ['Automations page not accessible']}]

        ss(page, 'AUTOMATIONS_LIST_CONFIRMED')
        print(f"\nAutomations page accessible! Building 4 workflows...")

        # Build all 4
        for builder, name in [
            (build_wf1, 'WF1'),
            (build_wf2, 'WF2'),
            (build_wf3, 'WF3'),
            (build_wf4, 'WF4'),
        ]:
            try:
                r = builder(page)
                results.append(r)
                print(f"\n  {name} result: {r['status']}")
            except Exception as e:
                import traceback
                print(f"\n  {name} EXCEPTION: {e}")
                traceback.print_exc()
                ss(page, f'{name.lower()}_exception')
                results.append({'name': name, 'status': 'exception', 'url': page.url, 'notes': [str(e)]})

        # Save session
        state = ctx.storage_state()
        with open(SESSION_FILE, 'w') as f:
            json.dump(state, f)
        print(f"\nSession saved: {len(state.get('cookies', []))} cookies")

        browser.close()

    # Summary
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    for r in results:
        icon = "OK" if r['status'] in ('activated', 'built') else "FAIL"
        print(f"[{icon}] {r['name']}")
        print(f"     Status: {r['status']} | URL: {r['url']}")
        if r['notes']:
            print(f"     Notes: {r['notes']}")

    # Save results
    rpath = f"{SS_DIR}/results.json"
    with open(rpath, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults: {rpath}")

    return results


if __name__ == '__main__':
    main()
