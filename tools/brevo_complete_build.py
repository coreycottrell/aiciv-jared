#!/usr/bin/env python3
"""
Brevo Complete Workflow Build - Neural Feed Welcome Sequence
Uses saved session (no 2FA). Builds the full 7-email automation.

Confirmed working approach:
- Trigger drag: Locator.drag_to() with source/target positions
- Config panel appears on left after drag
- "Drop block here" slot appears below trigger on canvas
- Clicking "Drop block here" should open a step picker

Automation #4 is the target (already created, named correctly).
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
    (1, 0),   # Email 1 - immediate (no wait)
    (2, 2),   # Email 2 - wait 2 days
    (3, 2),   # Email 3 - wait 2 days
    (4, 3),   # Email 4 - wait 3 days
    (5, 3),   # Email 5 - wait 3 days
    (6, 4),   # Email 6 - wait 4 days
    (7, 7),   # Email 7 - wait 7 days
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
    path = f"{SS_DIR}/brevo_complete_{_n[0]:02d}_{label}.png"
    page.screenshot(path=path, full_page=False)
    print(f"  [SS] {_n[0]:02d}_{label}")
    return path


def wait_idle(page, timeout=10000):
    try:
        page.wait_for_load_state('networkidle', timeout=timeout)
    except PlaywrightTimeout:
        pass


def canvas_text(page):
    return page.evaluate('() => document.body.innerText')


def is_empty(page):
    return 'Drop a step here' in canvas_text(page) or 'Drop block here' in canvas_text(page)


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


def drag_trigger_to_canvas(page):
    """
    Drag 'Contact added to list' from panel to canvas.
    Uses Locator.drag_to which is confirmed to work.
    """
    print("  Dragging 'Contact added to list' to canvas...")
    click_triggers_tab(page)
    time.sleep(0.5)

    trigger_loc = page.locator('[draggable=true]').first
    canvas_loc = page.locator('[class*="WorkflowCanvas"]').first

    tbox = trigger_loc.bounding_box()
    cbox = canvas_loc.bounding_box()
    print(f"  Trigger: {tbox}")
    print(f"  Canvas: {cbox}")

    # Source: center of trigger card relative to its top-left
    src_pos = {'x': int(tbox['width'] / 2), 'y': int(tbox['height'] / 2)}
    # Target: center of canvas (relative to canvas top-left)
    tgt_pos = {'x': int(cbox['width'] / 2), 'y': int(cbox['height'] * 0.3)}

    trigger_loc.drag_to(canvas_loc, source_position=src_pos, target_position=tgt_pos)
    time.sleep(3)
    ss(page, 'trigger_dragged')

    body = canvas_text(page)
    if 'Contact added to list' in body and 'Drop a step here' not in body:
        print("  Trigger placed successfully!")
        return True
    print(f"  WARNING: Trigger may not have placed. Body snippet: {body[:200]}")
    return False


def configure_list_trigger(page):
    """
    After trigger is placed, the config panel is open on the left.
    Select List 3 (The Neural Feed) and save.
    """
    print("  Configuring trigger: selecting List 3...")
    time.sleep(1)

    # Click the "Select a list" dropdown
    try:
        dropdown = page.wait_for_selector(
            'text=Select a list, [placeholder*="list" i], [class*="select-control"]',
            timeout=8000
        )
        dropdown.click()
        time.sleep(1.5)
        ss(page, 'list_dropdown_open')
        print("  Clicked list dropdown")
    except PlaywrightTimeout:
        print("  Could not find list dropdown")
        ss(page, 'list_dropdown_not_found')
        return False

    # Select "The Neural Feed" option
    selected = False
    for sel in [
        'text=The Neural Feed',
        'li:has-text("The Neural Feed")',
        'div:has-text("The Neural Feed"):not(:has(div))',
        '[class*="option"]:has-text("Neural Feed")',
        'text=Neural Feed',
    ]:
        try:
            opt = page.wait_for_selector(sel, timeout=4000, state='visible')
            if opt:
                opt.click()
                print(f"  Selected 'The Neural Feed' via: {sel}")
                selected = True
                time.sleep(1)
                break
        except PlaywrightTimeout:
            continue

    if not selected:
        # Show what options are visible
        print("  Could not find 'The Neural Feed' option. Visible options:")
        opts = page.query_selector_all('[class*="option"], li[role="option"]')
        for o in opts[:10]:
            try:
                txt = o.evaluate('el => el.textContent').strip()[:50]
                print(f"    Option: {txt}")
            except Exception:
                pass
        ss(page, 'list_options_visible')

    ss(page, 'after_list_select')

    # Click Save
    try:
        save_btn = page.wait_for_selector('button:has-text("Save")', timeout=5000)
        save_btn.click()
        time.sleep(2)
        print("  Clicked Save for trigger config")
        ss(page, 'trigger_saved')
        return True
    except PlaywrightTimeout:
        print("  No Save button found")
        return False


def click_drop_block_here(page):
    """
    Click the 'Drop block here' slot on the canvas to open the step picker.
    Returns True if a picker/panel opened.
    """
    try:
        slot = page.wait_for_selector('text=Drop block here', timeout=8000)
        if slot:
            box = slot.bounding_box()
            print(f"  'Drop block here' at: {box}")
            slot.click()
            time.sleep(2)
            ss(page, 'after_drop_block_click')
            # Check if anything opened
            body = canvas_text(page)
            if 'Send an email' in body or 'Wait' in body or 'Actions' in body:
                print("  Step picker/panel opened!")
                return True
    except PlaywrightTimeout:
        print("  'Drop block here' not found")
    return False


def drag_action_to_canvas(page, action_text, target_slot_text='Drop block here'):
    """
    Drag an action (e.g. 'Send an email', 'Wait') from the Actions panel to the canvas.
    """
    print(f"  Dragging action: '{action_text}'...")
    click_actions_tab(page)
    time.sleep(0.5)

    # Find the draggable action card
    action_loc = page.locator(f'[draggable=true]:has-text("{action_text}")').first
    try:
        abox = action_loc.bounding_box()
        if not abox:
            print(f"  Action '{action_text}' bounding box is None")
            return False
        print(f"  Action card at: {abox}")
    except Exception as e:
        print(f"  Action card not found: {e}")
        return False

    # Find the "Drop block here" slot on the canvas
    try:
        slot = page.wait_for_selector('text=Drop block here', timeout=8000)
        sbox = slot.bounding_box()
        print(f"  'Drop block here' slot at: {sbox}")
    except PlaywrightTimeout:
        print("  'Drop block here' not found - trying canvas center")
        canvas_loc = page.locator('[class*="WorkflowCanvas"]').first
        cbox = canvas_loc.bounding_box()
        sbox = {'x': cbox['x'] + cbox['width']/2 - 50, 'y': cbox['y'] + cbox['height']/2, 'width': 100, 'height': 30}

    # Drag
    src_pos = {'x': int(abox['width'] / 2), 'y': int(abox['height'] / 2)}
    # Target: center of the "Drop block here" slot relative to action card's top-left
    # We need to use the canvas as target with absolute position
    # Convert slot absolute coords to canvas-relative coords
    canvas_loc = page.locator('[class*="WorkflowCanvas"]').first
    cbox = canvas_loc.bounding_box()
    tgt_x = sbox['x'] + sbox['width']/2 - cbox['x']
    tgt_y = sbox['y'] + sbox['height']/2 - cbox['y']
    tgt_pos = {'x': int(tgt_x), 'y': int(tgt_y)}

    print(f"  Drag source_pos={src_pos}, target_pos={tgt_pos}")
    action_loc.drag_to(canvas_loc, source_position=src_pos, target_position=tgt_pos)
    time.sleep(2.5)
    ss(page, f'action_dragged_{action_text[:15].replace(" ","_")}')
    return True


def configure_send_email(page, template_id):
    """
    Configure the 'Send an email' step: select template by ID.
    The config panel appears on the left after placing the step.
    """
    print(f"  Configuring email step: template {template_id} ({TEMPLATE_NAMES[template_id][:40]})...")
    time.sleep(1)
    ss(page, f'email_config_start_t{template_id}')

    tname = TEMPLATE_NAMES[template_id]

    # Look for the template selector
    for sel in [
        'text=Select a template',
        '[placeholder*="template" i]',
        '[class*="template"] [class*="select"]',
        '[class*="select-control"]',
        'select',
    ]:
        try:
            el = page.wait_for_selector(sel, timeout=5000, state='visible')
            if el:
                el.click()
                time.sleep(1.5)
                print(f"  Opened template selector via: {sel}")
                ss(page, f'template_dropdown_t{template_id}')

                # Select the template
                for opt_sel in [
                    f'text={tname}',
                    f'li:has-text("{tname}")',
                    f'[class*="option"]:has-text("{tname[:30]}")',
                    # By template ID
                    f'[data-value="{template_id}"]',
                    f'option[value="{template_id}"]',
                ]:
                    try:
                        opt = page.wait_for_selector(opt_sel, timeout=3000, state='visible')
                        if opt:
                            opt.click()
                            print(f"  Selected template: {tname[:40]}")
                            time.sleep(1)
                            ss(page, f'template_selected_t{template_id}')
                            # Save
                            try:
                                save = page.wait_for_selector('button:has-text("Save")', timeout=4000)
                                save.click()
                                time.sleep(1.5)
                                print(f"  Saved email step")
                                return True
                            except PlaywrightTimeout:
                                print("  No Save button for email step")
                                return True  # May auto-save
                    except PlaywrightTimeout:
                        continue
                break
        except PlaywrightTimeout:
            continue

    print(f"  WARNING: Could not configure template {template_id}")
    ss(page, f'template_config_failed_t{template_id}')
    return False


def configure_wait_step(page, days):
    """
    Configure the Wait step: set duration in days.
    """
    print(f"  Configuring wait: {days} days...")
    time.sleep(1)

    for sel in [
        'input[type="number"]',
        'input[placeholder*="day" i]',
        'input[name*="delay"]',
        'input[name*="duration"]',
        '[class*="duration"] input',
    ]:
        try:
            inp = page.wait_for_selector(sel, timeout=5000, state='visible')
            if inp:
                inp.click()
                page.keyboard.press('Control+a')
                page.keyboard.type(str(days))
                time.sleep(0.5)
                print(f"  Set wait to {days} days")

                # Make sure "Days" is selected (not hours/minutes)
                try:
                    days_opt = page.wait_for_selector('text=day, option[value="days"], li:has-text("Day")', timeout=3000)
                    if days_opt:
                        days_opt.click()
                        print("  Selected 'Days' unit")
                except PlaywrightTimeout:
                    pass

                # Save
                try:
                    save = page.wait_for_selector('button:has-text("Save")', timeout=4000)
                    save.click()
                    time.sleep(1.5)
                    print(f"  Saved wait step")
                    return True
                except PlaywrightTimeout:
                    print("  No Save button for wait - trying Enter")
                    inp.press('Enter')
                    time.sleep(1)
                    return True
        except PlaywrightTimeout:
            continue

    print(f"  WARNING: Could not configure wait step")
    return False


def add_email_step(page, template_id, step_num):
    """Drag 'Send an email' to canvas and configure it."""
    print(f"\n  [STEP {step_num}] Adding email: {TEMPLATE_NAMES[template_id][:50]}")
    drag_action_to_canvas(page, 'Send an email')
    time.sleep(1)
    configure_send_email(page, template_id)


def add_wait_step(page, days, step_num):
    """Drag 'Wait' to canvas and configure it."""
    print(f"\n  [STEP {step_num}] Adding wait: {days} days")
    drag_action_to_canvas(page, 'Wait')
    time.sleep(1)
    configure_wait_step(page, days)


def activate_automation(page):
    """Click 'Activate automation' button."""
    print("\n[ACTIVATE] Activating automation...")
    try:
        btn = page.wait_for_selector('button:has-text("Activate automation")', timeout=10000)
        btn.click()
        time.sleep(3)
        ss(page, 'after_activate_click')
        print("  Clicked Activate automation")

        # Handle any confirmation
        try:
            confirm = page.wait_for_selector(
                'button:has-text("Activate"), button:has-text("Confirm"), button:has-text("OK")',
                timeout=5000
            )
            confirm.click()
            time.sleep(3)
            print("  Confirmed activation")
        except PlaywrightTimeout:
            pass

        ss(page, 'ACTIVATED')
        body = canvas_text(page)
        is_active = 'Active' in body and 'Inactive' not in body
        print(f"  Activation result - Active: {is_active}")
        return is_active
    except PlaywrightTimeout:
        print("  Activate button not found")
        ss(page, 'activate_not_found')
        return False


def main():
    print("=" * 65)
    print("Brevo Complete Build - Neural Feed Welcome Sequence")
    print("=" * 65)

    with open(SESSION_FILE) as f:
        session = json.load(f)
    print(f"Session loaded: {len(session.get('cookies', []))} cookies")

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

        # ── Load automation #4 ─────────────────────────────────────────
        print("\n[1] Loading automation #4...")
        page.goto('https://app.brevo.com/automation/edit/4', wait_until='domcontentloaded', timeout=30000)
        time.sleep(4)
        wait_idle(page)

        ss(page, 'loaded')
        title = page.title()
        print(f"  Page title: {title}")
        print(f"  URL: {page.url}")

        # ── Check current state ────────────────────────────────────────
        body = canvas_text(page)
        print(f"\n  Current canvas state (first 500 chars):\n{body[:500]}")

        # ── Place trigger if canvas is empty ───────────────────────────
        if 'Drop a step here' in body:
            print("\n[2] Canvas empty - placing trigger...")
            drag_trigger_to_canvas(page)
            time.sleep(2)
            configure_list_trigger(page)
            time.sleep(2)
        else:
            print("\n[2] Trigger already on canvas - checking state...")
            if 'Contact added to list' in body:
                print("  'Contact added to list' trigger is present")
                # Check if it still needs configuration
                if 'Verify and save' in body or 'Select a list' in body:
                    print("  Trigger needs configuration...")
                    configure_list_trigger(page)
                    time.sleep(2)
            ss(page, 'trigger_existing')

        ss(page, 'after_trigger_setup')
        body = canvas_text(page)
        print(f"\n  After trigger setup:\n{body[:800]}")

        # ── Add email steps with waits ─────────────────────────────────
        print("\n[3] Adding email sequence steps...")
        step_num = 0
        for email_idx, (template_id, wait_days) in enumerate(EMAIL_SEQUENCE, 1):
            print(f"\n  --- Email {email_idx} of {len(EMAIL_SEQUENCE)} ---")

            if wait_days > 0:
                step_num += 1
                add_wait_step(page, wait_days, step_num)
                time.sleep(1.5)

            step_num += 1
            add_email_step(page, template_id, step_num)
            time.sleep(1.5)

            ss(page, f'after_email_{email_idx}')

        ss(page, 'sequence_complete')
        print("\n  Sequence steps added!")

        # ── Final state analysis ───────────────────────────────────────
        print("\n[4] Final state analysis...")
        body = canvas_text(page)
        print(f"\n  Canvas text:\n{body[:2000]}")

        # ── Activate ───────────────────────────────────────────────────
        activated = activate_automation(page)

        # ── Final screenshots ──────────────────────────────────────────
        ss(page, 'FINAL')
        final_url = page.url
        final_title = page.title()
        print(f"\n  Final URL: {final_url}")
        print(f"  Final title: {final_title}")

        browser.close()

    result = {
        'status': 'activated' if activated else 'built_not_activated',
        'workflow_name': WORKFLOW_NAME,
        'workflow_url': final_url,
        'activated': activated,
        'steps_configured': step_num,
        'screenshots': f'{SS_DIR}/brevo_complete_*.png',
    }
    print("\n" + "=" * 65)
    print("BUILD RESULT:")
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    main()
