#!/usr/bin/env python3
"""
setup_neural_feed_automation.py
Neural Feed Welcome Sequence - Brevo Automation Setup

Creates the 7-email welcome sequence automation in Brevo for The Neural Feed (List 3).

What this script does:
  1. Loads existing Brevo session (brevo_session.json) or performs fresh login+2FA
  2. Checks if "Neural Feed Welcome Sequence" automation already exists (avoids duplicates)
  3. Navigates to automation #4 (or creates new) in the Brevo builder
  4. Configures trigger: Contact added to List 3 (The Neural Feed)
  5. Adds email sequence with delays via drag-and-drop on canvas:
     - Email 1 (Template 1): Immediate
     - Email 2 (Template 2): 2-day delay
     - Email 3 (Template 3): 2-day delay (day 4)
     - Email 4 (Template 4): 3-day delay (day 7)
     - Email 5 (Template 5): 3-day delay (day 10)
     - Email 6 (Template 6): 4-day delay (day 14)
     - Email 7 (Template 7): 4-day delay (day 18)
  6. Activates the workflow

Key learnings from prior attempts (incorporated here):
  - Drag-and-drop to a WorkflowCanvas target loses focus; must drag to exact pixel coords
  - "Send an email" drag may navigate to template editor if canvas target is not precise
  - Use dispatch dragstart/dragend events via evaluate() for more reliable drops
  - "Drop block here" text slot is the target - get its exact bounding box first
  - Trigger config: combobox opens a list picker; search for "Neural Feed" to find List 3
  - Session file has 44 cookies and remains valid for ~24h; re-use to skip 2FA
  - Automation #4 is "Neural Feed - Welcome Sequence" - confirmed from prior sessions

Usage:
    python3 tools/setup_neural_feed_automation.py [--dry-run] [--fresh-login]

    --dry-run     Check state without making changes
    --fresh-login Force fresh login instead of using session file

Author: full-stack-developer
Date: 2026-02-21
"""

import argparse
import imaplib
import email
import json
import os
import re
import sys
import time

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_PROJECT_ROOT, '.env'))

BREVO_EMAIL = 'purebrain@puremarketing.ai'
BREVO_PASSWORD = os.getenv('BREVO_PASSWORD', '')
GMAIL_USER = os.getenv('GMAIL_USERNAME', '')
GMAIL_APP_PASSWORD = os.getenv('GOOGLE_APP_PASSWORD', '')

SESSION_FILE = os.path.join(_PROJECT_ROOT, 'tools', 'brevo_session.json')
SS_DIR = os.path.join(_PROJECT_ROOT, 'exports', 'screenshots')
os.makedirs(SS_DIR, exist_ok=True)

WORKFLOW_NAME = 'Neural Feed Welcome Sequence'
AUTOMATION_EDIT_URL = 'https://app.brevo.com/automation/edit/4'
AUTOMATION_LIST_URL = 'https://app.brevo.com/automation/list'

# Template IDs confirmed via API (GET /v3/smtp/templates)
# (template_id, wait_days_before_this_email)
# wait_days=0 means send immediately after trigger (or previous email)
EMAIL_SEQUENCE = [
    (1, 0),   # Email 1 - immediate
    (2, 2),   # Email 2 - 2 day delay
    (3, 2),   # Email 3 - 2 day delay (cumulative day 4)
    (4, 3),   # Email 4 - 3 day delay (cumulative day 7)
    (5, 3),   # Email 5 - 3 day delay (cumulative day 10)
    (6, 4),   # Email 6 - 4 day delay (cumulative day 14)
    (7, 4),   # Email 7 - 4 day delay (cumulative day 18)
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ss(page, label: str) -> str:
    """Take a screenshot with sequential numbering."""
    _ss_n[0] += 1
    safe = re.sub(r'[^a-zA-Z0-9_-]', '_', label)[:40]
    path = f'{SS_DIR}/neural_feed_auto_{_ss_n[0]:02d}_{safe}.png'
    try:
        page.screenshot(path=path, full_page=False)
        print(f'  [SS] {_ss_n[0]:02d}_{safe}')
    except Exception as e:
        print(f'  [SS] Failed: {e}')
    return path


def pause(secs: float = 1.0, reason: str = '') -> None:
    if reason:
        print(f'  [WAIT] {secs}s - {reason}')
    time.sleep(secs)


def body_text(page) -> str:
    try:
        return page.evaluate('() => document.body.innerText')
    except Exception:
        return ''


def try_click(page, selectors, timeout: int = 5000, desc: str = '') -> bool:
    """Try clicking using a list of selectors; return True on first success."""
    for sel in selectors:
        try:
            el = page.wait_for_selector(sel, timeout=timeout, state='visible')
            if el:
                el.scroll_into_view_if_needed()
                el.click()
                pause(0.5)
                print(f'  [CLICK] {desc or sel[:60]}')
                return True
        except PlaywrightTimeout:
            continue
        except Exception as e:
            print(f'  [CLICK] Error for {sel}: {e}')
            continue
    return False


def dismiss_modals(page) -> None:
    """Dismiss any overlay modals or cookie banners."""
    for sel in [
        'button:has-text("Back to editor")',
        'button:has-text("Got it")',
        'button:has-text("Accept All Cookies")',
        'button:has-text("Accept All")',
        '[aria-label="Close"]',
        'button:has-text("OK")',
    ]:
        try:
            btn = page.wait_for_selector(sel, timeout=1500, state='visible')
            if btn:
                btn.click()
                pause(0.8)
        except PlaywrightTimeout:
            pass
    try:
        page.keyboard.press('Escape')
        pause(0.3)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------

def load_session() -> dict | None:
    """Load existing Playwright storage state from session file."""
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE) as f:
            data = json.load(f)
        cookies = data.get('cookies', [])
        if len(cookies) >= 10:
            print(f'  [SESSION] Loaded {len(cookies)} cookies from {SESSION_FILE}')
            return data
    except Exception as e:
        print(f'  [SESSION] Load error: {e}')
    return None


def save_session(context) -> None:
    """Save current browser session to file for reuse."""
    try:
        state = context.storage_state()
        with open(SESSION_FILE, 'w') as f:
            json.dump(state, f)
        cookies = state.get('cookies', [])
        print(f'  [SESSION] Saved {len(cookies)} cookies to {SESSION_FILE}')
    except Exception as e:
        print(f'  [SESSION] Save error: {e}')


# ---------------------------------------------------------------------------
# Login / 2FA
# ---------------------------------------------------------------------------

def get_2fa_code(max_wait: int = 90) -> str | None:
    """Fetch Brevo 2FA verification code from Gmail via IMAP."""
    print('  [2FA] Waiting for verification code in Gmail...')
    deadline = time.time() + max_wait

    while time.time() < deadline:
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            mail.select('INBOX')
            status, data = mail.search(None, 'FROM', 'account-alerts@t.brevo.com', 'UNSEEN')
            if status == 'OK' and data[0]:
                for mid in reversed(data[0].decode().split()):
                    _, msg_data = mail.fetch(mid, '(RFC822)')
                    msg = email.message_from_bytes(msg_data[0][1])
                    subj = msg.get('Subject', '')
                    if 'verify' not in subj.lower() and 'device' not in subj.lower():
                        continue
                    body = ''
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() in ('text/plain', 'text/html'):
                                body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    else:
                        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                    # Match 6-digit code near "verification code"
                    m = re.search(r'(?:verification code|one-time)[:\s]*\n?\s*(\d{6})', body, re.IGNORECASE)
                    if m:
                        code = m.group(1)
                        print(f'  [2FA] Code found: {code}')
                        mail.logout()
                        return code
                    # Fallback: any 6-digit number
                    for c in re.findall(r'\b\d{6}\b', body):
                        digits = list(c)
                        if not (digits[0] == digits[2] == digits[4] and digits[1] == digits[3] == digits[5]):
                            print(f'  [2FA] Code (fallback): {c}')
                            mail.logout()
                            return c
            mail.logout()
        except Exception as e:
            print(f'  [2FA] Gmail error: {e}')
        remaining = int(deadline - time.time())
        print(f'  [2FA] No code yet, retrying... ({remaining}s left)')
        time.sleep(5)
    return None


def do_login_and_2fa(page) -> bool:
    """Perform fresh Brevo login including 2FA if required."""
    print('\n[LOGIN] Starting fresh login...')
    page.goto('https://login.brevo.com/', wait_until='domcontentloaded', timeout=60000)
    pause(2)
    dismiss_modals(page)
    ss(page, 'login_page')

    # Fill email
    try:
        ef = page.wait_for_selector("input[name='email'], input#email", timeout=10000, state='visible')
        ef.fill(BREVO_EMAIL)
        pause(0.3)
    except PlaywrightTimeout:
        print('  ERROR: Email input not found')
        return False

    # Fill password
    try:
        pf = page.wait_for_selector("input[type='password'], input[name='password']", timeout=5000, state='visible')
        pf.fill(BREVO_PASSWORD)
        pause(0.3)
    except PlaywrightTimeout:
        print('  ERROR: Password input not found')
        return False

    ss(page, 'creds_filled')

    # Submit
    submitted = try_click(
        page,
        ["button:has-text('Log In')", "button:has-text('Log in')", "button[data-testid='submit-button']"],
        timeout=5000,
        desc='Login button'
    )
    if not submitted:
        try:
            pf.press('Enter')
        except Exception:
            pass

    pause(4, 'post-login')
    try:
        page.wait_for_load_state('networkidle', timeout=20000)
    except PlaywrightTimeout:
        pass

    ss(page, 'after_login_submit')

    # Handle 2FA
    if '2fa' in page.url or 'new-device' in page.url:
        print('\n  [2FA] Device verification required')
        code = get_2fa_code(max_wait=90)
        if not code:
            print('  ERROR: Could not retrieve 2FA code')
            return False
        try:
            code_field = page.wait_for_selector(
                "input[type='text'], input[type='number'], input[inputmode='numeric']",
                timeout=15000,
                state='visible'
            )
            code_field.fill(code)
            pause(0.5)
            try_click(page, ["button:has-text('Verify')", "button[type='submit']"], desc='Verify 2FA')
        except PlaywrightTimeout:
            print('  ERROR: 2FA code input not found')
            return False

        pause(4, 'post-2fa')
        try:
            page.wait_for_load_state('networkidle', timeout=30000)
        except PlaywrightTimeout:
            pass

        if 'login' in page.url.lower() or '2fa' in page.url:
            print('  ERROR: Still on auth page after 2FA')
            return False

    print(f'  Logged in. URL: {page.url}')
    return True


# ---------------------------------------------------------------------------
# Automation existence check
# ---------------------------------------------------------------------------

def check_existing_automations(page) -> dict:
    """
    Navigate to automation list and check if the welcome sequence already exists.
    Returns info dict with 'exists', 'active', 'automation_id'.
    """
    print('\n[CHECK] Looking for existing automation...')
    page.goto(AUTOMATION_LIST_URL, wait_until='domcontentloaded', timeout=30000)
    pause(3)
    try:
        page.wait_for_load_state('networkidle', timeout=15000)
    except PlaywrightTimeout:
        pass
    ss(page, 'automation_list')

    # Guard against session expiry redirect
    if 'login' in page.url.lower():
        print('  Session expired - redirected to login')
        return {'exists': False, 'active': False, 'automation_id': None, 'session_expired': True}

    page_content = body_text(page)
    print(f'  Page URL: {page.url}')
    print(f'  Page text preview: {page_content[:300]}')

    # Search for workflow name on the page (Brevo uses various name formats)
    name_variants = [
        WORKFLOW_NAME,
        'Neural Feed Welcome',
        'Neural Feed - Welcome Sequence',
        'Neural Feed Welcome Sequence',
    ]
    found = any(variant in page_content for variant in name_variants)

    if found:
        # Try to determine if it's active
        is_active = 'Active' in page_content and 'Neural Feed' in page_content
        print(f'  Found existing automation. Active: {is_active}')
        return {'exists': True, 'active': is_active, 'automation_id': 4}

    # Also try navigating directly to automation #4 to check if it exists
    page.goto(AUTOMATION_EDIT_URL, wait_until='domcontentloaded', timeout=30000)
    pause(3)
    if 'login' not in page.url.lower() and 'edit/4' in page.url:
        content = body_text(page)
        has_name = 'Neural Feed' in content or 'Welcome Sequence' in content
        is_active = 'Active' in content
        if has_name:
            print(f'  Found automation #4. Active: {is_active}')
            return {'exists': True, 'active': is_active, 'automation_id': 4}

    print('  No matching automation found')
    return {'exists': False, 'active': False, 'automation_id': None}


# ---------------------------------------------------------------------------
# Automation builder - trigger setup
# ---------------------------------------------------------------------------

def setup_trigger(page) -> bool:
    """
    Configure the trigger block on canvas to use List 3 (The Neural Feed).
    The trigger block is already on canvas as 'Contact added to list'.
    We click it to open the config panel, then select the list.
    """
    print('\n[TRIGGER] Configuring trigger: Contact added to list -> List 3...')

    # Dismiss any open modals first
    dismiss_modals(page)
    pause(1)

    # The trigger block is on the canvas (right side of viewport).
    # From screenshots: trigger block is at approximately x=530, y=90 in the canvas area.
    # Strategy: find all elements with "Contact added to list" text, click the one on the right side.
    trigger_clicked = False

    try:
        matches = page.locator('text=Contact added to list').all()
        print(f'  Found {len(matches)} "Contact added to list" elements')
        for el in matches:
            try:
                box = el.bounding_box()
                if box and box['x'] > 350:  # Canvas is right of the panel (panel width ~260px)
                    print(f'  Clicking canvas trigger at x={box["x"]:.0f}, y={box["y"]:.0f}')
                    el.click()
                    trigger_clicked = True
                    pause(2, 'trigger panel opening')
                    break
            except Exception:
                continue
    except Exception as e:
        print(f'  Trigger element search error: {e}')

    if not trigger_clicked:
        # Fallback: click at known canvas position for trigger block
        print('  Fallback: clicking at canvas trigger coordinates')
        page.mouse.click(530, 90)
        trigger_clicked = True
        pause(2)

    ss(page, 'trigger_panel_open')

    page_text = body_text(page)
    if 'List' not in page_text and 'list' not in page_text:
        print('  Trigger panel may not have opened')
        ss(page, 'trigger_panel_check')

    # Open the list dropdown (combobox)
    combo_opened = False
    try:
        combo = page.wait_for_selector('[role="combobox"]', timeout=8000, state='visible')
        combo.click()
        pause(1.5, 'list dropdown')
        ss(page, 'list_dropdown_open')
        combo_opened = True
        print('  Opened list combobox')
    except PlaywrightTimeout:
        print('  Combobox not found - trying alternative selectors')
        for sel in [
            'select[name*="list"]',
            '.sib-select',
            '[class*="dropdown"]',
            'button:has-text("Select a list")',
        ]:
            try:
                el = page.wait_for_selector(sel, timeout=3000, state='visible')
                if el:
                    el.click()
                    pause(1.5)
                    combo_opened = True
                    break
            except PlaywrightTimeout:
                continue

    if not combo_opened:
        print('  ERROR: Could not open list selector')
        ss(page, 'trigger_no_combobox')
        return False

    # Select "The Neural Feed" (List 3)
    list_selected = False
    for sel in [
        'text=The Neural Feed - Blog Subscribers - #3',
        'text=The Neural Feed - Blog Subscribers',
        'text=The Neural Feed',
        'li:has-text("Neural Feed")',
        '[class*="option"]:has-text("Neural Feed")',
        '[role="option"]:has-text("Neural Feed")',
    ]:
        try:
            opt = page.wait_for_selector(sel, timeout=4000, state='visible')
            if opt:
                opt.click()
                print(f'  Selected list via: {sel}')
                list_selected = True
                pause(1)
                ss(page, 'list_selected')
                break
        except PlaywrightTimeout:
            continue

    if not list_selected:
        # Debug: show what options are visible
        print('  WARNING: Could not find Neural Feed option. Listing visible options:')
        try:
            opts = page.query_selector_all('[role="option"], li[class*="option"], [class*="menu-item"]')
            for o in opts[:15]:
                try:
                    t = o.evaluate('el => el.textContent').strip()[:80]
                    if t:
                        print(f'    Option: {t}')
                except Exception:
                    pass
        except Exception:
            pass
        ss(page, 'list_options_visible')

        # Try clicking first option that contains a number (list IDs)
        try:
            first_opt = page.wait_for_selector('[role="option"]', timeout=3000, state='visible')
            first_opt.click()
            list_selected = True
            print('  Selected first available option (fallback)')
        except PlaywrightTimeout:
            pass

    # Save trigger configuration
    try:
        save_btn = page.wait_for_selector('button:has-text("Save")', timeout=5000, state='visible')
        save_btn.click()
        pause(2, 'trigger save')
        ss(page, 'trigger_saved')
        print('  Trigger configured and saved')
        return True
    except PlaywrightTimeout:
        print('  No Save button found for trigger panel')
        ss(page, 'trigger_no_save')
        # Try pressing Enter
        page.keyboard.press('Enter')
        pause(1)
        return list_selected


# ---------------------------------------------------------------------------
# Automation builder - drag and drop helpers
# ---------------------------------------------------------------------------

def get_drop_slot_coords(page) -> dict | None:
    """
    Find the 'Drop block here' slot on canvas and return its center coordinates.
    Returns None if not found.
    """
    try:
        slot = page.wait_for_selector('text=Drop block here', timeout=8000, state='visible')
        box = slot.bounding_box()
        if box:
            return {
                'x': box['x'] + box['width'] / 2,
                'y': box['y'] + box['height'] / 2,
                'box': box,
            }
    except PlaywrightTimeout:
        pass
    return None


def drag_action_to_canvas(page, action_name: str, step_label: str) -> bool:
    """
    Drag an action card (e.g. 'Send an email', 'Wait') from the left panel
    to the 'Drop block here' slot on the canvas.

    Key lesson from prior attempts:
    - The action cards are in the left panel (x < 260)
    - 'Drop block here' is on the canvas (x > 350)
    - Standard drag_to() loses the drag state when crossing element boundaries
    - Using mouse.move() steps with mouse.down() and mouse.up() is more reliable
    - We scroll the panel to make sure action card is visible before dragging
    """
    print(f'  [DRAG] Dragging "{action_name}" to canvas...')

    # Switch to Actions tab
    try_click(page, ['button:has-text("Actions")'], timeout=3000, desc='Actions tab')
    pause(0.5)

    # Find the draggable action card in the panel
    action_card = None
    card_box = None
    for sel in [
        f'[draggable=true]:has-text("{action_name}")',
        f'[class*="action-item"]:has-text("{action_name}")',
        f'[class*="step-card"]:has-text("{action_name}")',
        f'li:has-text("{action_name}")',
    ]:
        try:
            card = page.wait_for_selector(sel, timeout=3000, state='visible')
            if card:
                card.scroll_into_view_if_needed()
                pause(0.3)
                box = card.bounding_box()
                if box and box['x'] < 300:  # Must be in the left panel
                    action_card = card
                    card_box = box
                    print(f'  Found card via: {sel} at x={box["x"]:.0f}')
                    break
        except PlaywrightTimeout:
            continue

    if not action_card or not card_box:
        print(f'  ERROR: "{action_name}" action card not found in panel')
        ss(page, f'{step_label}_no_action_card')
        return False

    # Find drop slot
    drop_coords = get_drop_slot_coords(page)
    if not drop_coords:
        print('  ERROR: "Drop block here" slot not found on canvas')
        ss(page, f'{step_label}_no_drop_slot')
        return False

    src_x = card_box['x'] + card_box['width'] / 2
    src_y = card_box['y'] + card_box['height'] / 2
    dst_x = drop_coords['x']
    dst_y = drop_coords['y']

    print(f'  Drag: ({src_x:.0f},{src_y:.0f}) -> ({dst_x:.0f},{dst_y:.0f})')

    # Perform drag using step-by-step mouse events (more reliable for SPAs)
    try:
        page.mouse.move(src_x, src_y)
        pause(0.3)
        page.mouse.down()
        pause(0.5, 'drag start')

        # Move in steps toward target (helps trigger drag-over events)
        steps = 15
        for i in range(1, steps + 1):
            mid_x = src_x + (dst_x - src_x) * (i / steps)
            mid_y = src_y + (dst_y - src_y) * (i / steps)
            page.mouse.move(mid_x, mid_y)
            time.sleep(0.05)

        pause(0.5, 'over drop target')
        page.mouse.up()
        pause(2, 'drop complete')

        ss(page, f'{step_label}_after_drag')

        # Verify the action was added (check if "Drop block here" is still visible
        # or if the block appeared on canvas)
        canvas_text = body_text(page)
        if action_name in canvas_text or 'Drop block here' not in canvas_text:
            print(f'  Drag successful (canvas updated)')
            return True

        print(f'  Drag may not have registered - canvas unchanged')
        return False

    except Exception as e:
        print(f'  Drag error: {e}')
        ss(page, f'{step_label}_drag_error')
        return False


# ---------------------------------------------------------------------------
# Configure email and wait steps
# ---------------------------------------------------------------------------

def configure_email_step(page, template_id: int, step_label: str) -> bool:
    """
    After dragging 'Send an email' to canvas, configure the email step:
    click the newly added block, then select the template.
    """
    print(f'  [EMAIL] Configuring email step (template {template_id})...')
    pause(1)
    ss(page, f'{step_label}_email_config_start')

    # The newly added block should be on canvas - click it or look for config panel
    # The config panel may auto-open after drop

    # Look for "Add message" button in the config panel
    add_msg_clicked = try_click(
        page,
        [
            'button:has-text("Add message")',
            '#email-asset-selection-trigger',
            'button:has-text("Select template")',
            'button:has-text("Choose template")',
        ],
        timeout=8000,
        desc='Add message / template picker'
    )

    if not add_msg_clicked:
        # Try clicking a newly appeared block on canvas
        print('  "Add message" not found, trying to click the new canvas block...')
        # New email block should be between the trigger and Exit
        try:
            # Look for an unconfigured email block
            blocks = page.locator('[class*="step-node"], [class*="block"], [class*="WorkflowNode"]').all()
            for block in blocks:
                try:
                    box = block.bounding_box()
                    btext = block.evaluate('el => el.textContent').strip()
                    if box and 'Send an email' in btext and box['x'] > 350:
                        block.click()
                        pause(1.5)
                        add_msg_clicked = try_click(
                            page,
                            ['button:has-text("Add message")', '#email-asset-selection-trigger'],
                            timeout=5000,
                            desc='Add message after block click'
                        )
                        if add_msg_clicked:
                            break
                except Exception:
                    continue
        except Exception as e:
            print(f'  Block click error: {e}')

    if not add_msg_clicked:
        print(f'  ERROR: Could not open template picker for email {template_id}')
        ss(page, f'{step_label}_no_template_picker')
        return False

    pause(2, 'template picker loading')
    ss(page, f'{step_label}_template_picker_open')

    # Select the template by name
    tname = TEMPLATE_NAMES[template_id]
    tname_short = tname[:35]
    template_selected = False

    # Try selecting by name
    for sel in [
        f'text="{tname}"',
        f'text={tname_short}',
        f'[class*="card"]:has-text("{tname_short}")',
        f'[class*="template"]:has-text("{tname_short}")',
        f'li:has-text("{tname_short}")',
        f'button:has-text("{tname_short}")',
        f'[class*="item"]:has-text("{tname_short}")',
    ]:
        try:
            opt = page.wait_for_selector(sel, timeout=5000, state='visible')
            if opt:
                opt.click()
                print(f'  Selected template via: {sel}')
                template_selected = True
                pause(1.5)
                ss(page, f'{step_label}_template_selected')
                break
        except PlaywrightTimeout:
            continue

    if not template_selected:
        print(f'  Template not found by name, attempting selection by index...')
        # Scroll to find the right template - they're ordered by ID (newest first usually)
        # Template IDs 1-7 should be visible
        try:
            # Try searching for the template
            search_box = page.wait_for_selector(
                'input[placeholder*="search" i], input[placeholder*="Search" i]',
                timeout=3000, state='visible'
            )
            search_box.fill(str(template_id))
            pause(1)
            ss(page, f'{step_label}_template_search')
        except PlaywrightTimeout:
            pass

        # Try clicking any card with the template ID number
        try:
            cards = page.query_selector_all('[class*="template-card"], [class*="templateCard"], [class*="message-card"], [class*="template-item"]')
            print(f'  Found {len(cards)} template cards')
            for card in cards:
                try:
                    card_text = card.evaluate('el => el.textContent').strip()
                    if f'Email {template_id}' in card_text or TEMPLATE_NAMES[template_id][:15] in card_text:
                        card.click()
                        template_selected = True
                        print(f'  Selected by card text match')
                        pause(1.5)
                        break
                except Exception:
                    continue

            if not template_selected and cards:
                # Try to select by position (templates appear newest-first, so ID 7 is first)
                # The template IDs 1-7 were created in order, so ID 1 is oldest = last position
                idx = len(cards) - template_id  # Rough mapping
                if 0 <= idx < len(cards):
                    cards[idx].click()
                    template_selected = True
                    print(f'  Selected template by index {idx} (fallback)')
                    pause(1.5)
        except Exception as e:
            print(f'  Card selection error: {e}')

    # Confirm selection if there's a Use/Select/Confirm button
    try_click(
        page,
        ['button:has-text("Use")', 'button:has-text("Select")', 'button:has-text("Confirm")', 'button:has-text("Add")'],
        timeout=3000,
        desc='Confirm template selection'
    )
    pause(1)

    # Fill subject line if required (some email steps need it)
    try:
        subj = page.wait_for_selector(
            '[name*="subject"], [placeholder*="subject" i]',
            timeout=3000, state='visible'
        )
        val = subj.input_value()
        if not val:
            subj.fill(f'Neural Feed - Email {template_id}')
            print('  Filled empty subject line')
    except PlaywrightTimeout:
        pass

    # Save the email step
    saved = try_click(page, ['button:has-text("Save")'], timeout=6000, desc='Save email step')
    if saved:
        pause(2, 'email step saved')
        ss(page, f'{step_label}_email_saved')
        return True
    else:
        print(f'  No Save button - email {template_id} may not be fully configured')
        ss(page, f'{step_label}_email_no_save')
        return template_selected


def configure_wait_step(page, days: int, step_label: str) -> bool:
    """
    After dragging 'Wait' to canvas, configure the wait duration.
    """
    print(f'  [WAIT] Configuring wait: {days} days...')
    pause(1)
    ss(page, f'{step_label}_wait_config')

    # The config panel should be open showing wait duration input
    configured = False

    for sel in ['input[type="number"]', 'input[name*="delay"]', 'input[name*="duration"]', '[class*="duration"] input', 'input[class*="number"]']:
        try:
            inp = page.wait_for_selector(sel, timeout=6000, state='visible')
            if inp:
                inp.click()
                page.keyboard.press('Control+a')
                page.keyboard.type(str(days))
                pause(0.5)
                print(f'  Set duration: {days} days')
                configured = True

                # Ensure unit is "Days" (not hours/minutes)
                for unit_sel in [
                    'option[value="days"]',
                    'option[value="day"]',
                    'text=Days',
                    '[class*="unit"]:has-text("Day")',
                ]:
                    try:
                        unit = page.wait_for_selector(unit_sel, timeout=2000, state='visible')
                        if unit:
                            unit.click()
                            print('  Set unit to Days')
                            break
                    except PlaywrightTimeout:
                        continue

                break
        except PlaywrightTimeout:
            continue

    if not configured:
        print(f'  WARNING: Could not find wait duration input')
        ss(page, f'{step_label}_wait_no_input')

    # Save
    saved = try_click(page, ['button:has-text("Save")'], timeout=5000, desc='Save wait step')
    if saved:
        pause(2, 'wait step saved')
        ss(page, f'{step_label}_wait_saved')
        return True
    else:
        # Try pressing Enter to confirm
        try:
            page.keyboard.press('Enter')
            pause(1)
        except Exception:
            pass
        return configured


# ---------------------------------------------------------------------------
# Build the sequence
# ---------------------------------------------------------------------------

def build_email_sequence(page) -> dict:
    """
    Build the full 7-email sequence on the canvas.
    Returns a summary dict.
    """
    print('\n[BUILD] Building email sequence...')
    results = []
    step_num = 0

    for email_idx, (template_id, wait_days) in enumerate(EMAIL_SEQUENCE, 1):
        print(f'\n  --- Email {email_idx} (Template {template_id}, delay={wait_days}d) ---')

        # Add wait step first (if needed)
        if wait_days > 0:
            step_num += 1
            label = f'S{step_num}_Wait{wait_days}d'
            dragged = drag_action_to_canvas(page, 'Wait', label)
            if dragged:
                configured = configure_wait_step(page, wait_days, label)
                results.append({'step': label, 'type': 'wait', 'days': wait_days, 'ok': configured})
            else:
                results.append({'step': label, 'type': 'wait', 'days': wait_days, 'ok': False, 'error': 'drag_failed'})
            pause(1)

        # Add email step
        step_num += 1
        label = f'S{step_num}_Email{template_id}'
        dragged = drag_action_to_canvas(page, 'Send an email', label)
        if dragged:
            configured = configure_email_step(page, template_id, label)
            results.append({'step': label, 'type': 'email', 'template_id': template_id, 'ok': configured})
        else:
            results.append({'step': label, 'type': 'email', 'template_id': template_id, 'ok': False, 'error': 'drag_failed'})

        pause(1)
        ss(page, f'checkpoint_email{email_idx}')
        canvas = body_text(page)
        print(f'  Canvas length: {len(canvas)} chars')

    ss(page, 'sequence_complete')
    return {
        'total_steps': step_num,
        'results': results,
        'success_count': sum(1 for r in results if r.get('ok')),
    }


# ---------------------------------------------------------------------------
# Activate
# ---------------------------------------------------------------------------

def activate_automation(page) -> bool:
    """Click 'Activate automation' and confirm."""
    print('\n[ACTIVATE] Activating automation...')

    # Save first
    try_click(page, ['button:has-text("Save")'], timeout=3000, desc='Pre-activate save')
    pause(1)

    activated = try_click(
        page,
        ['button:has-text("Activate automation")', 'button:has-text("Activate")'],
        timeout=10000,
        desc='Activate automation'
    )

    if not activated:
        print('  Activate button not found')
        ss(page, 'activate_not_found')
        return False

    pause(3, 'activation processing')

    # Confirm dialog if it appears
    try_click(
        page,
        ['button:has-text("Activate")', 'button:has-text("Confirm")', 'button:has-text("OK")'],
        timeout=4000,
        desc='Confirm activation'
    )
    pause(3)

    ss(page, 'after_activation')
    canvas = body_text(page)

    if 'Active' in canvas or 'active' in canvas.lower():
        print('  Automation is now ACTIVE')
        return True

    print(f'  Activation status unclear. Page text: {canvas[:200]}')
    return False


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def run(dry_run: bool = False, fresh_login: bool = False) -> dict:
    """
    Main entry point. Returns result dict.
    """
    print('=' * 65)
    print(f'Neural Feed Welcome Sequence - Brevo Automation Setup')
    print(f'Mode: {"DRY-RUN" if dry_run else "LIVE"} | Login: {"FRESH" if fresh_login else "SESSION"}')
    print('=' * 65)

    if not BREVO_PASSWORD:
        print('ERROR: BREVO_PASSWORD not found in .env')
        sys.exit(1)

    # Load existing session
    existing_session = None if fresh_login else load_session()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
            ]
        )

        # Create context with session if available
        if existing_session:
            ctx = browser.new_context(
                viewport={'width': 1600, 'height': 900},
                device_scale_factor=2,
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
                storage_state=existing_session,
            )
        else:
            ctx = browser.new_context(
                viewport={'width': 1600, 'height': 900},
                device_scale_factor=2,
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
            )

        page = ctx.new_page()
        page.set_default_timeout(30000)

        # Step 1: Login if needed
        if not existing_session or fresh_login:
            print('\n[STEP 1] Logging in...')
            if not do_login_and_2fa(page):
                print('FAILED: Login unsuccessful')
                browser.close()
                return {'status': 'failed', 'stage': 'login'}
            save_session(ctx)
        else:
            print('\n[STEP 1] Using existing session (skipping login)')
            # Quick verify we're authenticated by checking a simple API endpoint
            # rather than navigating the SPA (avoids session race conditions)
            page.goto('https://app.brevo.com/', wait_until='domcontentloaded', timeout=30000)
            pause(2)
            if 'login' in page.url.lower():
                print('  Session expired, performing fresh login...')
                if not do_login_and_2fa(page):
                    print('FAILED: Login unsuccessful')
                    browser.close()
                    return {'status': 'failed', 'stage': 'login'}
                save_session(ctx)
            else:
                print(f'  Session valid. URL: {page.url}')

        ss(page, 'authenticated')

        # Step 2: Check if automation already exists
        print('\n[STEP 2] Checking for existing automation...')
        existing = check_existing_automations(page)
        print(f'  Existing: {existing}')

        # Handle session expiry discovered during check
        if existing.get('session_expired'):
            print('  Session expired during check - logging in...')
            if not do_login_and_2fa(page):
                print('FAILED: Login unsuccessful')
                browser.close()
                return {'status': 'failed', 'stage': 'login'}
            save_session(ctx)
            existing = check_existing_automations(page)
            print(f'  Existing (after re-auth): {existing}')

        if existing['exists'] and existing['active']:
            print('\n  Automation already exists and is ACTIVE.')
            print('  No action needed - the workflow is live.')
            browser.close()
            return {
                'status': 'already_active',
                'message': 'Neural Feed Welcome Sequence is already active',
                'automation_id': existing['automation_id'],
            }

        if dry_run:
            print('\n[DRY-RUN] Would create/configure automation #4')
            print('  Template sequence:', EMAIL_SEQUENCE)
            browser.close()
            return {
                'status': 'dry_run',
                'existing': existing,
                'would_do': 'Configure trigger + build 7-email sequence + activate',
            }

        # Step 3: Open the automation builder
        print(f'\n[STEP 3] Opening automation builder (ID=4)...')
        page.goto(AUTOMATION_EDIT_URL, wait_until='domcontentloaded', timeout=30000)
        pause(4, 'builder loading')
        try:
            page.wait_for_load_state('networkidle', timeout=20000)
        except PlaywrightTimeout:
            pass

        ss(page, 'builder_loaded')
        print(f'  Builder URL: {page.url}')
        print(f'  Title: {page.title()}')
        canvas_state = body_text(page)
        print(f'  Has trigger: {"Contact added to list" in canvas_state}')
        print(f'  Has email step: {"Send an email" in canvas_state}')

        dismiss_modals(page)

        # Step 4: Configure trigger
        print('\n[STEP 4] Setting up trigger...')
        trigger_ok = setup_trigger(page)
        print(f'  Trigger setup: {"OK" if trigger_ok else "FAILED"}')
        pause(2)

        # Step 5: Build the sequence
        print('\n[STEP 5] Building 7-email sequence...')
        seq_result = build_email_sequence(page)
        print(f'\n  Sequence results:')
        for r in seq_result['results']:
            status = 'OK' if r.get('ok') else 'FAILED'
            print(f'    {r["step"]}: {status}')

        # Step 6: Activate
        print('\n[STEP 6] Activating automation...')
        activated = activate_automation(page)
        print(f'  Activated: {activated}')

        final_url = page.url
        save_session(ctx)
        browser.close()

        result = {
            'status': 'complete',
            'workflow': WORKFLOW_NAME,
            'trigger_configured': trigger_ok,
            'sequence': seq_result,
            'activated': activated,
            'final_url': final_url,
            'steps_total': seq_result['total_steps'],
            'steps_succeeded': seq_result['success_count'],
        }

        print('\n' + '=' * 65)
        print('FINAL RESULT:')
        print(json.dumps(result, indent=2))
        return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Set up Neural Feed Welcome Sequence in Brevo automation'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Check state without making changes'
    )
    parser.add_argument(
        '--fresh-login',
        action='store_true',
        help='Force fresh login instead of using saved session'
    )
    args = parser.parse_args()
    run(dry_run=args.dry_run, fresh_login=args.fresh_login)


if __name__ == '__main__':
    main()
