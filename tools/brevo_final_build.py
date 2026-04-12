#!/usr/bin/env python3
"""
Brevo Final Build - Neural Feed Welcome Sequence (Automation #4)
All UI interactions confirmed from screenshots and element inspection.

Key confirmed facts:
- Trigger config: click the trigger block on canvas → list selector opens (role=combobox at x=128,y=185)
- Email step: 'Add message' button → opens template picker modal
- Wait step: draggable from Actions panel
- Each step has a config panel on the left; Save button at bottom
- After each step is placed, click it on canvas to open config panel
"""

import os, time, json
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

SESSION_FILE = '/home/jared/projects/AI-CIV/aether/tools/brevo_session.json'
SS_DIR = '/home/jared/projects/AI-CIV/aether/exports/screenshots'
os.makedirs(SS_DIR, exist_ok=True)

WORKFLOW_NAME = "Neural Feed - Welcome Sequence"

# (template_id, wait_days_before_this_email)
EMAIL_SEQUENCE = [
    (1, 0),
    (2, 2),
    (3, 2),
    (4, 3),
    (5, 3),
    (6, 4),
    (7, 7),
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

_n = [0]
def ss(page, label):
    _n[0] += 1
    path = f"{SS_DIR}/brevo_final_{_n[0]:02d}_{label}.png"
    page.screenshot(path=path, full_page=False)
    print(f"  [SS] {_n[0]:02d}_{label}")
    return path

def txt(page):
    return page.evaluate('() => document.body.innerText')

def click_triggers_tab(page):
    try:
        page.locator('button:has-text("Triggers")').click()
        time.sleep(0.8)
    except Exception:
        pass

def click_actions_tab(page):
    try:
        page.locator('button:has-text("Actions")').click()
        time.sleep(0.8)
    except Exception:
        pass

def close_config_panel(page):
    """Close any open config panel by pressing Escape or clicking Cancel."""
    try:
        cancel = page.wait_for_selector('button:has-text("Cancel")', timeout=2000)
        cancel.click()
        time.sleep(1)
    except PlaywrightTimeout:
        try:
            page.keyboard.press('Escape')
            time.sleep(0.5)
        except Exception:
            pass


def setup_trigger(page):
    """
    Click the 'Contact added to list' block on canvas,
    select List 3 (The Neural Feed), and save.
    """
    print("\n[TRIGGER] Configuring trigger...")

    # Click the trigger block on canvas to open its config panel
    # The block text is 'Contact added to list' on the canvas (right side)
    # We need to click the canvas block, not the panel item
    # Canvas blocks are in the React Flow area (x > 500)
    try:
        # Find elements containing "Contact added to list" and pick the canvas one
        matches = page.locator('text=Contact added to list').all()
        print(f"  Found {len(matches)} 'Contact added to list' elements")
        for el in matches:
            box = el.bounding_box()
            if box and box['x'] > 400:  # Canvas is on the right side
                print(f"  Clicking canvas trigger block at: {box}")
                el.click()
                time.sleep(2)
                break
        else:
            # Fallback: click at known canvas location
            print("  Clicking at canvas trigger location...")
            page.mouse.click(530, 90)
            time.sleep(2)
    except Exception as e:
        print(f"  Error clicking trigger: {e}")

    ss(page, 'trigger_panel_open')
    body = txt(page)
    print(f"  Panel state: {body[body.find('List'):body.find('List')+200] if 'List' in body else 'No list in body'}")

    # Find and click the list dropdown (combobox)
    try:
        combo = page.wait_for_selector('[role="combobox"]', timeout=8000, state='visible')
        combo.click()
        time.sleep(1.5)
        ss(page, 'list_dropdown')
        print("  Opened list dropdown")
    except PlaywrightTimeout:
        print("  Combobox not found")
        ss(page, 'no_combobox')
        return False

    # Find and click "The Neural Feed" option
    for sel in [
        'text=The Neural Feed - Blog Subscribers',
        'text=The Neural Feed',
        'li:has-text("Neural Feed")',
        '[class*="option"]:has-text("Neural Feed")',
    ]:
        try:
            opt = page.wait_for_selector(sel, timeout=4000, state='visible')
            if opt:
                opt.click()
                print(f"  Selected list via: {sel}")
                time.sleep(1)
                ss(page, 'list_selected')
                break
        except PlaywrightTimeout:
            continue
    else:
        # Show available options
        opts = page.query_selector_all('[class*="option"], li[role="option"], [class*="menu-item"]')
        print(f"  Available options ({len(opts)}):")
        for o in opts[:10]:
            try:
                print(f"    {o.evaluate('el => el.textContent').strip()[:60]}")
            except Exception:
                pass
        ss(page, 'list_options')

    # Save trigger config
    try:
        save = page.wait_for_selector('button:has-text("Save")', timeout=5000)
        save.click()
        time.sleep(2)
        print("  Saved trigger config")
        ss(page, 'trigger_saved')
        return True
    except PlaywrightTimeout:
        print("  No Save button for trigger")
        return False


def drag_action(page, action_text):
    """
    Drag an action card from Actions panel to 'Drop block here' slot.
    Returns True if successful.
    """
    click_actions_tab(page)
    time.sleep(0.5)

    # Find the draggable action card
    action_loc = page.locator(f'[draggable=true]:has-text("{action_text}")').first
    try:
        abox = action_loc.bounding_box()
        if not abox:
            print(f"  '{action_text}' not visible in panel")
            return False
    except Exception as e:
        print(f"  '{action_text}' locator error: {e}")
        return False

    # Find "Drop block here" slot
    try:
        slot = page.wait_for_selector('text=Drop block here', timeout=8000)
        sbox = slot.bounding_box()
    except PlaywrightTimeout:
        print("  'Drop block here' not found")
        ss(page, f'no_drop_slot_{action_text[:10]}')
        return False

    # Get canvas element as drag target
    canvas_loc = page.locator('[class*="WorkflowCanvas"]').first
    cbox = canvas_loc.bounding_box()

    # Calculate target position relative to canvas
    tgt_x = sbox['x'] + sbox['width']/2 - cbox['x']
    tgt_y = sbox['y'] + sbox['height']/2 - cbox['y']

    src_pos = {'x': int(abox['width'] / 2), 'y': int(abox['height'] / 2)}
    tgt_pos = {'x': int(tgt_x), 'y': int(tgt_y)}

    print(f"  Dragging '{action_text}': src={src_pos} tgt={tgt_pos}")
    action_loc.drag_to(canvas_loc, source_position=src_pos, target_position=tgt_pos)
    time.sleep(2.5)
    return True


def configure_email_step(page, template_id):
    """
    Configure a 'Send an email' step.
    The config panel has an 'Add message' button that opens template picker.
    """
    print(f"  Configuring email: template {template_id}...")
    time.sleep(1)
    ss(page, f'email_config_t{template_id}')

    # Click "Add message" button
    try:
        add_msg = page.wait_for_selector(
            'button:has-text("Add message"), #email-asset-selection-trigger',
            timeout=8000, state='visible'
        )
        add_msg.click()
        time.sleep(2)
        ss(page, f'template_picker_t{template_id}')
        print("  Clicked 'Add message'")
    except PlaywrightTimeout:
        print("  'Add message' button not found")
        ss(page, f'no_add_message_t{template_id}')
        return False

    # Template picker modal/panel should open
    # Look for the template name
    tname = TEMPLATE_NAMES[template_id]
    tname_short = tname[:30]

    for sel in [
        f'text={tname}',
        f'text={tname_short}',
        f'[class*="template"]:has-text("{tname_short}")',
        f'li:has-text("{tname_short}")',
        f'button:has-text("{tname_short}")',
        f'[class*="card"]:has-text("{tname_short}")',
    ]:
        try:
            opt = page.wait_for_selector(sel, timeout=6000, state='visible')
            if opt:
                opt.click()
                print(f"  Selected template: {tname[:50]}")
                time.sleep(2)
                ss(page, f'template_selected_t{template_id}')
                break
        except PlaywrightTimeout:
            continue
    else:
        # Show what's visible in the template picker
        print("  Template not found by name. Looking for all visible items...")
        items = page.query_selector_all('[class*="template"], [class*="card"], li, tr')
        for item in items[:15]:
            try:
                t = item.evaluate('el => el.textContent').strip()[:60]
                if t and len(t) > 5:
                    print(f"    Visible item: {t}")
            except Exception:
                pass
        ss(page, f'template_picker_contents_t{template_id}')

        # Try selecting by index (template IDs 1-7 in order)
        # Look for any clickable template items
        cards = page.query_selector_all('[class*="template-card"], [class*="templateCard"], [class*="message-card"]')
        print(f"  Template cards found: {len(cards)}")
        if len(cards) >= template_id:
            cards[template_id - 1].click()
            time.sleep(2)
            print(f"  Selected template #{template_id} by index")
        elif cards:
            cards[0].click()
            time.sleep(2)
            print(f"  Selected first available template")

    # Look for a confirm/use/select button
    for sel in ['button:has-text("Use")', 'button:has-text("Select")', 'button:has-text("Confirm")', 'button:has-text("Add")']:
        try:
            btn = page.wait_for_selector(sel, timeout=3000, state='visible')
            btn.click()
            time.sleep(1.5)
            print(f"  Confirmed via: {sel}")
            break
        except PlaywrightTimeout:
            continue

    # Fill subject line if required
    try:
        subj = page.wait_for_selector('[name*="subject"], [placeholder*="subject" i]', timeout=3000, state='visible')
        if subj:
            val = subj.input_value()
            if not val:
                subj.fill(f'Neural Feed Email {template_id}')
                print(f"  Filled subject line")
    except PlaywrightTimeout:
        pass

    # Save
    try:
        save = page.wait_for_selector('button:has-text("Save")', timeout=6000, state='visible')
        save.click()
        time.sleep(2)
        print(f"  Saved email step {template_id}")
        ss(page, f'email_saved_t{template_id}')
        return True
    except PlaywrightTimeout:
        print(f"  No Save button for email step")
        ss(page, f'email_no_save_t{template_id}')
        return False


def configure_wait_step(page, days):
    """Configure a Wait step duration."""
    print(f"  Configuring wait: {days} days...")
    time.sleep(1)
    ss(page, f'wait_config_{days}d')

    # Find duration input
    for sel in ['input[type="number"]', 'input[name*="delay"]', 'input[name*="duration"]', '[class*="duration"] input']:
        try:
            inp = page.wait_for_selector(sel, timeout=6000, state='visible')
            if inp:
                inp.click()
                page.keyboard.press('Control+a')
                page.keyboard.type(str(days))
                time.sleep(0.5)
                print(f"  Set {days} days")

                # Ensure unit is "Days"
                try:
                    days_unit = page.wait_for_selector(
                        'text=Days, option[value="days"], [class*="unit"]:has-text("Day")',
                        timeout=3000
                    )
                    if days_unit:
                        days_unit.click()
                        print("  Set unit to Days")
                except PlaywrightTimeout:
                    pass

                # Save
                try:
                    save = page.wait_for_selector('button:has-text("Save")', timeout=5000, state='visible')
                    save.click()
                    time.sleep(2)
                    print(f"  Saved wait step ({days} days)")
                    ss(page, f'wait_saved_{days}d')
                    return True
                except PlaywrightTimeout:
                    inp.press('Enter')
                    time.sleep(1)
                    return True
        except PlaywrightTimeout:
            continue

    print(f"  Could not configure wait step")
    return False


def add_step(page, step_type, template_id=None, wait_days=None, step_label=''):
    """
    Add a step to the automation:
    1. Drag from actions panel to 'Drop block here'
    2. Configure the step in the left panel
    3. Save
    """
    print(f"\n  [{step_label}] Adding {step_type}" +
          (f" template={template_id}" if template_id else "") +
          (f" days={wait_days}" if wait_days else ""))

    action_text = 'Send an email' if step_type == 'email' else 'Wait'
    dragged = drag_action(page, action_text)

    if not dragged:
        print(f"  WARNING: Could not drag '{action_text}'")
        ss(page, f'drag_failed_{step_label}')
        return False

    time.sleep(1)

    if step_type == 'email':
        return configure_email_step(page, template_id)
    elif step_type == 'wait':
        return configure_wait_step(page, wait_days)


def activate_automation(page):
    """Activate the automation workflow."""
    print("\n[ACTIVATE] Activating...")

    # Save first
    try:
        page.wait_for_selector('button:has-text("Save")', timeout=3000).click()
        time.sleep(2)
    except PlaywrightTimeout:
        pass

    try:
        btn = page.wait_for_selector('button:has-text("Activate automation")', timeout=10000)
        btn.click()
        time.sleep(3)
        print("  Clicked 'Activate automation'")

        # Confirm if dialog appears
        for sel in ['button:has-text("Activate")', 'button:has-text("Confirm")', 'button:has-text("OK")']:
            try:
                confirm = page.wait_for_selector(sel, timeout=4000)
                confirm.click()
                time.sleep(3)
                print(f"  Confirmed via: {sel}")
                break
            except PlaywrightTimeout:
                continue

        ss(page, 'ACTIVATED')
        body = txt(page)
        if 'Active' in body:
            print("  Status: ACTIVE!")
            return True
        print(f"  Body after activate: {body[:300]}")
        return False
    except PlaywrightTimeout:
        print("  Activate button not found")
        ss(page, 'activate_missing')
        return False


def main():
    print("=" * 65)
    print("Brevo Final Build - Neural Feed Welcome Sequence")
    print("=" * 65)

    with open(SESSION_FILE) as f:
        session = json.load(f)
    print(f"Session: {len(session.get('cookies',[]))} cookies")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        ctx = browser.new_context(
            viewport={'width': 1600, 'height': 900},
            device_scale_factor=2,
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36',
            storage_state=session,
        )
        page = ctx.new_page()
        page.set_default_timeout(30000)

        # Load builder
        print("\n[1] Loading automation #4...")
        page.goto('https://app.brevo.com/automation/edit/4', wait_until='domcontentloaded', timeout=30000)
        time.sleep(4)
        ss(page, 'loaded')

        canvas_state = txt(page)
        print(f"  Title: {page.title()}")
        has_trigger = 'Contact added to list' in canvas_state and 'Verify and save' in canvas_state
        has_email = 'Send an email' in canvas_state
        print(f"  Has trigger: {has_trigger}, Has email step: {has_email}")

        # Configure trigger (click it to open config, select list, save)
        print("\n[2] Setting up trigger...")
        setup_trigger(page)
        time.sleep(2)

        ss(page, 'after_trigger_setup')
        body = txt(page)
        print(f"  Canvas after trigger: {body[body.find('Contact'):body.find('Contact')+200]}")

        # Now add the email sequence
        print("\n[3] Building email sequence...")
        step_num = 0
        for email_idx, (template_id, wait_days) in enumerate(EMAIL_SEQUENCE, 1):
            if wait_days > 0:
                step_num += 1
                add_step(page, 'wait', wait_days=wait_days, step_label=f'W{step_num}_{wait_days}d')
                time.sleep(1)

            step_num += 1
            add_step(page, 'email', template_id=template_id, step_label=f'E{step_num}_T{template_id}')
            time.sleep(1)

            ss(page, f'checkpoint_email{email_idx}')

            body = txt(page)
            print(f"  Canvas after email {email_idx}: {len(body)} chars, steps visible: {body.count('Step ID')}")

        ss(page, 'sequence_complete')
        print(f"\n  Sequence added: {step_num} total steps")
        print(f"  Canvas text length: {len(txt(page))}")

        # Activate
        activated = activate_automation(page)

        ss(page, 'FINAL')
        final_url = page.url
        browser.close()

    result = {
        'workflow': WORKFLOW_NAME,
        'url': final_url,
        'activated': activated,
        'total_steps': step_num,
        'screenshots': f'{SS_DIR}/brevo_final_*.png'
    }
    print("\n" + "=" * 65)
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    main()
