#!/usr/bin/env python3
"""
Brevo Definitive Build v2 - Neural Feed Welcome Sequence

Confirmed canvas state (from screenshots):
- Automation #4: "Neural Feed - Welcome Sequence" (name already set)
- Has 1 "Contact added to list" trigger (unconfigured)
- Has 1 "Send an email" step (unconfigured)
- Has "Exit" node
- A "needs valid trigger and action" modal may be open

Key findings:
- aria-label="action-list" = the ... menu button on each canvas node
- Drop slot "Drop block here" appears BELOW properly chained blocks
- Wait step text in Actions tab: "Wait"
- brevo_session.json has valid 44-cookie session

Strategy:
1. Close any open modals/panels
2. Delete the existing email step and trigger (start clean)
3. Drag trigger from sidebar → canvas
4. Configure trigger (Your First Folder -> Neural Feed list)
5. For each email in sequence:
   a. If wait > 0: drag Wait to drop slot, configure
   b. Drag Send an email to drop slot, configure template
6. Activate
"""

import os, time, json, sys
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

SESSION_FILE = '/home/jared/projects/AI-CIV/aether/tools/brevo_session.json'
SS_DIR = '/home/jared/projects/AI-CIV/aether/exports/screenshots'
os.makedirs(SS_DIR, exist_ok=True)

WORKFLOW_NAME = "Neural Feed - Welcome Sequence"

# (template_id, wait_days_before_this_email)
EMAIL_SEQUENCE = [
    (1, 0),   # Email 1: send immediately after trigger
    (2, 2),   # Email 2: wait 2 days, then send
    (3, 2),   # Email 3: wait 2 days
    (4, 3),   # Email 4: wait 3 days
    (5, 3),   # Email 5: wait 3 days
    (6, 4),   # Email 6: wait 4 days
    (7, 7),   # Email 7: wait 7 days
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
    path = f"{SS_DIR}/brevo_d2_{_n[0]:02d}_{label[:30]}.png"
    try:
        page.screenshot(path=path, full_page=False)
    except Exception:
        pass
    print(f"  [SS] {_n[0]:02d}_{label[:30]}")
    return path

def body(page):
    try:
        return page.evaluate('() => document.body.innerText')
    except Exception:
        return ''

def dismiss_modals(page):
    """Close any overlay modals or dialogs."""
    # Try 'Back to editor' button (from the "needs valid trigger" modal)
    for sel in [
        'button:has-text("Back to editor")',
        'button:has-text("Got it")',
        'button:has-text("Close")',
        '[aria-label="Close"]',
        'button:has-text("OK")',
        '[data-testid="modal-close"]',
    ]:
        try:
            btn = page.wait_for_selector(sel, timeout=1500, state='visible')
            if btn:
                btn.click()
                time.sleep(0.8)
                print(f"  Dismissed modal via: {sel}")
        except PlaywrightTimeout:
            continue
    # Press Escape to close any remaining overlays
    page.keyboard.press('Escape')
    time.sleep(0.5)

def close_panel(page):
    """Close left config panel via Cancel or Escape."""
    for sel in ['button:has-text("Cancel")', 'button:has-text("Discard")']:
        try:
            btn = page.wait_for_selector(sel, timeout=1500, state='visible')
            if btn:
                btn.click()
                time.sleep(0.8)
                return
        except PlaywrightTimeout:
            continue
    page.keyboard.press('Escape')
    time.sleep(0.5)

def click_triggers_tab(page):
    try:
        page.locator('button:has-text("Triggers")').first.click()
        time.sleep(0.8)
    except Exception:
        pass

def click_actions_tab(page):
    try:
        page.locator('button:has-text("Actions")').first.click()
        time.sleep(0.8)
    except Exception:
        pass

def count_canvas_steps(page):
    """Count how many step blocks are on the canvas."""
    b = body(page)
    return b.count('Step ID')

def get_canvas_box(page):
    """Get the bounding box of the workflow canvas."""
    for sel in ['[class*="WorkflowCanvas"]', '[class*="workflow-canvas"]',
                '[class*="react-flow__pane"]', '.react-flow__renderer']:
        try:
            loc = page.locator(sel).first
            box = loc.bounding_box()
            if box and box['width'] > 200:
                return box
        except Exception:
            continue
    return None

def delete_all_canvas_blocks(page):
    """
    Clear the canvas completely by deleting all blocks via their action-list menus.
    Start from the bottom (highest y) to avoid dependency issues.
    """
    print("\n[CLEAN] Clearing canvas...")
    dismiss_modals(page)
    time.sleep(1)

    max_attempts = 20
    for attempt in range(max_attempts):
        # Find all action-list buttons on canvas
        btns = []
        for btn in page.locator('[aria-label="action-list"]').all():
            try:
                bx = btn.bounding_box()
                if bx and bx['x'] > 300:
                    btns.append((btn, bx))
            except Exception:
                continue

        if not btns:
            print(f"  No more action-list buttons - canvas clear (attempt {attempt+1})")
            break

        # Delete the bottommost block first (reverse dependency order)
        btns.sort(key=lambda x: -x[1]['y'])
        btn, bx = btns[0]
        print(f"  Clicking ⋮ at ({bx['x']:.0f}, {bx['y']:.0f})...")
        try:
            btn.click()
            time.sleep(1)
            ss(page, f'del_menu_{attempt}')
        except Exception as e:
            print(f"  ⋮ click failed: {e}")
            break

        # Click Delete from the menu
        deleted = False
        for del_sel in [
            'button:has-text("Delete")',
            'li:has-text("Delete")',
            '[role="menuitem"]:has-text("Delete")',
            'a:has-text("Delete")',
            '[class*="menu"] :text("Delete")',
        ]:
            try:
                del_btn = page.wait_for_selector(del_sel, timeout=2000, state='visible')
                if del_btn:
                    del_btn.click()
                    time.sleep(1.5)
                    deleted = True
                    print(f"  Deleted via: {del_sel}")
                    break
            except PlaywrightTimeout:
                continue

        if not deleted:
            print(f"  Could not find Delete option in menu (attempt {attempt+1})")
            # Try pressing Escape and continue
            page.keyboard.press('Escape')
            time.sleep(0.5)
            # Try right-click approach as last resort
            page.mouse.click(bx['x'] - 50, bx['y'])
            time.sleep(0.5)
            page.keyboard.press('Delete')
            time.sleep(1)
            break

        time.sleep(0.5)

    ss(page, 'canvas_cleared')
    b = body(page)
    step_count = b.count('Step ID')
    print(f"  Canvas steps remaining: {step_count}")
    return step_count == 0


def drag_trigger_to_canvas(page):
    """
    Drag 'Contact added to list' from Triggers sidebar to canvas center.
    """
    print("\n[TRIGGER] Dragging trigger to canvas...")
    click_triggers_tab(page)
    time.sleep(1)

    # Find the drag handle for 'Contact added to list'
    # In Brevo sidebar, the ⠿ drag handle is class*="DragableCard" or draggable=true
    trigger_loc = None
    for sel in [
        '[draggable=true]:has-text("Contact added to list")',
        '[class*="DragableCard"]:has-text("Contact added to list")',
        '[class*="dragable"]:has-text("Contact added to list")',
    ]:
        try:
            locs = page.locator(sel).all()
            for loc in locs:
                bx = loc.bounding_box()
                if bx and bx['x'] < 300:  # Must be in sidebar (left side)
                    trigger_loc = loc
                    break
            if trigger_loc:
                break
        except Exception:
            continue

    if not trigger_loc:
        print("  Trigger drag card not found in sidebar")
        ss(page, 'trigger_not_in_sidebar')
        return False

    tbox = trigger_loc.bounding_box()
    print(f"  Trigger drag card at: ({tbox['x']:.0f}, {tbox['y']:.0f})")

    # Get canvas and drag to center-top area
    cbox = get_canvas_box(page)
    if not cbox:
        print("  Canvas not found")
        return False

    src = {'x': int(tbox['width'] / 2), 'y': int(tbox['height'] / 2)}
    # Target: center-ish, upper third of canvas
    tgt = {'x': int(cbox['width'] / 2), 'y': int(cbox['height'] * 0.25)}

    print(f"  Dragging: src={src} → canvas tgt={tgt}")
    canvas_loc = page.locator('[class*="WorkflowCanvas"]').first

    trigger_loc.drag_to(canvas_loc, source_position=src, target_position=tgt)
    time.sleep(3)

    ss(page, 'after_trigger_drag')
    b = body(page)
    on_canvas = 'Contact added to list' in b and ('Step ID' in b or 'Verify and save' in b or 'List *' in b)
    print(f"  Trigger on canvas: {on_canvas}")
    print(f"  Body snippet: {b[:300]}")
    return on_canvas


def configure_trigger(page):
    """
    Click canvas trigger → expand folder → select Neural Feed → Save.
    Assumes trigger config panel might already be open (it opens when trigger is dragged).
    """
    print("\n[TRIGGER] Configuring trigger...")

    # Config panel may already be open after drag
    b = body(page)
    panel_open = 'List *' in b or 'Select a list' in b or 'Contact added to list' in b and 'Cancel' in b

    if not panel_open:
        # Click on the canvas trigger block to open config
        for match in page.locator('text=Contact added to list').all():
            box = match.bounding_box()
            if box and box['x'] > 300:
                print(f"  Clicking trigger block at ({box['x']:.0f}, {box['y']:.0f})")
                match.click()
                time.sleep(2)
                break

    ss(page, 'trigger_panel')

    # Open the list combobox
    try:
        combo = page.wait_for_selector('[role="combobox"]', timeout=8000, state='visible')
        combo.click()
        time.sleep(1.5)
        ss(page, 'dropdown_open')
        print("  Dropdown opened")
    except PlaywrightTimeout:
        print("  No combobox found - checking body:")
        print(f"  {body(page)[:400]}")
        ss(page, 'no_combobox')
        return False

    # Expand "Your First Folder" to see lists
    try:
        folder = page.wait_for_selector('text=Your First Folder', timeout=4000, state='visible')
        folder.click()
        time.sleep(1.5)
        ss(page, 'folder_expanded')
        print("  Expanded 'Your First Folder'")
    except PlaywrightTimeout:
        print("  'Your First Folder' not found - checking available options...")
        opts = page.query_selector_all('[role="option"], [class*="option"], li[class]')
        for o in opts[:10]:
            try:
                print(f"    opt: {o.evaluate('el => el.textContent').strip()[:60]}")
            except Exception:
                pass

    # Select "The Neural Feed - Blog Subscribers"
    for sel in [
        'text=The Neural Feed - Blog Subscribers',
        'text=The Neural Feed',
        '[role="option"]:has-text("Neural Feed")',
        'li:has-text("Neural Feed")',
    ]:
        try:
            opt = page.wait_for_selector(sel, timeout=4000, state='visible')
            if opt:
                opt.click()
                print(f"  Selected Neural Feed via: {sel}")
                time.sleep(1)
                ss(page, 'list_selected')
                break
        except PlaywrightTimeout:
            continue
    else:
        print("  Could not find Neural Feed list in dropdown")
        ss(page, 'list_not_found')
        # Show what's available
        available = page.query_selector_all('[role="option"], li[class*="option"]')
        for a in available[:15]:
            try:
                print(f"    {a.evaluate('el => el.textContent').strip()[:60]}")
            except Exception:
                pass

    # Click Save - use locator to avoid stale element issues
    try:
        save_loc = page.locator('button:has-text("Save")').first
        save_loc.wait_for(state='visible', timeout=5000)
        save_loc.click()
        time.sleep(2)
        print("  Trigger saved")
        ss(page, 'trigger_saved')
        return True
    except Exception as e:
        print(f"  No Save button found: {e}")
        ss(page, 'trigger_no_save')
        return False


def find_drop_slot(page):
    """
    Find 'Drop block here' on canvas and return its center absolute coords.
    Returns (cx, cy) or (None, None).
    """
    # Ensure panel is closed so drop slot is visible
    # Don't aggressively close - just check
    try:
        slot = page.wait_for_selector('text=Drop block here', timeout=5000, state='visible')
        sbox = slot.bounding_box()
        if sbox:
            cx = sbox['x'] + sbox['width'] / 2
            cy = sbox['y'] + sbox['height'] / 2
            return cx, cy
    except PlaywrightTimeout:
        pass
    return None, None


def drag_action_to_drop_slot(page, action_text):
    """
    1. Close any open config panel (to reveal drop slot)
    2. Find 'Drop block here' slot on canvas
    3. Click Actions tab to find the draggable card
    4. Drag the card to the drop slot

    Returns True if successful.
    """
    # Step 1: Close panel
    close_panel(page)
    time.sleep(0.8)
    dismiss_modals(page)
    time.sleep(0.5)

    # Step 2: Find drop slot BEFORE opening Actions tab
    # (opening Actions tab might shift layout)
    cx, cy = find_drop_slot(page)
    if cx is None:
        # Try scrolling down on canvas to reveal drop slot
        cbox = get_canvas_box(page)
        if cbox:
            page.mouse.wheel(0, 200)
            time.sleep(0.5)
        cx, cy = find_drop_slot(page)

    if cx is None:
        print(f"  'Drop block here' not found for '{action_text}'")
        ss(page, f'no_drop_{action_text[:8]}')
        return False

    print(f"  Drop slot at absolute ({cx:.0f}, {cy:.0f})")

    # Step 3: Open Actions tab and find the action card
    click_actions_tab(page)
    time.sleep(0.8)

    action_loc = None
    for sel in [
        f'[draggable=true]:has-text("{action_text}")',
        f'[class*="DragableCard"]:has-text("{action_text}")',
        f'[class*="dragable"]:has-text("{action_text}")',
    ]:
        try:
            locs = page.locator(sel).all()
            for loc in locs:
                bx = loc.bounding_box()
                if bx and bx['x'] < 300:  # In sidebar
                    action_loc = loc
                    break
            if action_loc:
                break
        except Exception:
            continue

    if not action_loc:
        print(f"  '{action_text}' drag card not found in sidebar")
        ss(page, f'no_card_{action_text[:8]}')
        return False

    abox = action_loc.bounding_box()
    if not abox:
        print(f"  '{action_text}' bounding box is None")
        return False

    # Step 4: Drag to canvas at drop slot position
    cbox = get_canvas_box(page)
    if not cbox:
        print("  Canvas bounding box not found")
        return False

    # Convert absolute drop slot coords to canvas-relative
    tgt_x = cx - cbox['x']
    tgt_y = cy - cbox['y']

    src_pos = {'x': int(abox['width'] / 2), 'y': int(abox['height'] / 2)}
    tgt_pos = {'x': max(0, int(tgt_x)), 'y': max(0, int(tgt_y))}

    canvas_loc = page.locator('[class*="WorkflowCanvas"]').first

    print(f"  Dragging '{action_text}': src={src_pos} → tgt={tgt_pos}")
    action_loc.drag_to(canvas_loc, source_position=src_pos, target_position=tgt_pos)
    time.sleep(3)

    ss(page, f'after_drag_{action_text[:8]}')
    b = body(page)
    step_count = b.count('Step ID')
    drop_slots = b.count('Drop block here')
    print(f"  After drag - steps: {step_count}, drop slots: {drop_slots}")
    return True


def configure_email_step(page, template_id):
    """
    Configure a 'Send an email' step that's been dragged to canvas.
    Config panel should be open (it auto-opens after drag).
    If not open, click the email block to open it.
    """
    print(f"\n  [EMAIL] Configuring template {template_id}...")
    time.sleep(1)

    b = body(page)

    # Check if config panel is open
    if 'Send an email' not in b or 'Cancel' not in b:
        print("  Panel not open - clicking email block...")
        for match in page.locator('text=Send an email').all():
            box = match.bounding_box()
            if box and box['x'] > 300:
                match.click()
                time.sleep(2)
                break
        ss(page, f'email_panel_{template_id}')

    b = body(page)
    print(f"  Panel body snippet: {b[:200]}")

    # Try to find and click 'Add message' or equivalent
    template_opened = False
    for sel in [
        'button:has-text("Add message")',
        '#email-asset-selection-trigger',
        'button:has-text("Select a template")',
        'button:has-text("Choose a template")',
        '[class*="configure-message"]',
        '[class*="message-selector"]',
        'button:has-text("Select template")',
    ]:
        try:
            btn = page.wait_for_selector(sel, timeout=3000, state='visible')
            if btn:
                btn.click()
                time.sleep(2.5)
                ss(page, f'picker_open_{template_id}')
                print(f"  Template picker via: {sel}")
                template_opened = True
                break
        except PlaywrightTimeout:
            continue

    if not template_opened:
        print("  No 'Add message' button found - showing panel state:")
        ss(page, f'no_add_msg_{template_id}')
        b = body(page)
        print(f"  {b[:500]}")
        # Try to save as-is and move on
        try:
            save = page.wait_for_selector('button:has-text("Save")', timeout=3000)
            save.click()
            time.sleep(1.5)
        except PlaywrightTimeout:
            close_panel(page)
        return False

    # Template picker is open - look for our template
    # From screenshots: templates shown as cards with "Use template" buttons
    # Templates are listed in reverse order (#7 first, #1 last)
    tname = TEMPLATE_NAMES[template_id]
    ss(page, f'picker_{template_id}')

    # Scroll down in the picker if needed to find lower-numbered templates
    # Template cards have the template number as "#N" above the name
    selected = False

    # Strategy 1: Find the card with our template name, then click its "Use template" button
    # The card container has the name text AND a "Use template" button
    for name_sel in [
        f'text={tname}',
        f'text=Email {template_id} -',
        f':text("#{template_id}")',
        f'text=#{template_id}',
    ]:
        try:
            # Find the container that has this template's name
            card_loc = page.locator(f'[class*="card"]:has({name_sel}), '
                                    f'[class*="template"]:has({name_sel}), '
                                    f'div:has({name_sel}):has(button:has-text("Use template"))')
            # Wait a bit for cards to be visible
            time.sleep(0.5)

            # Try to find and click the "Use template" button within this card
            use_btn = card_loc.locator('button:has-text("Use template")').first
            if use_btn.is_visible():
                use_btn.click()
                print(f"  Clicked 'Use template' for '{tname[:40]}' (card match)")
                time.sleep(3)
                selected = True
                ss(page, f'tmpl_used_{template_id}')
                break
        except Exception as e:
            print(f"  Card approach failed ({name_sel}): {e}")
            continue

    if not selected:
        # Strategy 2: Find the template by scanning all "Use template" buttons
        # Since templates are in reverse order, template #N is at position (8-N)
        # i.e., template #1 is last, #7 is first
        print(f"  Strategy 2: Finding Use template button by position...")
        use_btns = page.locator('button:has-text("Use template")').all()
        print(f"  Found {len(use_btns)} 'Use template' buttons")

        if use_btns:
            # Try to find by adjacent text matching template number
            for i, ubtn in enumerate(use_btns):
                try:
                    # Get the parent card's text to find template number
                    card_text = ubtn.evaluate(
                        'el => el.closest("[class]")?.textContent || el.parentElement?.textContent || ""'
                    ).strip()
                    print(f"    Button {i}: {card_text[:80]}")
                    if f'#{template_id}' in card_text or tname[:20] in card_text:
                        ubtn.click()
                        print(f"  Selected via position {i} (matched '#{template_id}')")
                        time.sleep(3)
                        selected = True
                        ss(page, f'tmpl_used_{template_id}')
                        break
                except Exception as e:
                    print(f"    button {i} text error: {e}")
                    continue

        if not selected and use_btns:
            # Fallback: templates are in reverse order, #1 is last
            # If we have 7 buttons: index 0=#7, 1=#6, 2=#5, 3=#4, 4=#3, 5=#2, 6=#1
            reverse_idx = 7 - template_id  # 0-indexed from top
            idx = min(reverse_idx, len(use_btns) - 1)
            print(f"  Strategy 2 fallback: clicking button at reverse index {idx}")
            use_btns[idx].click()
            time.sleep(3)
            selected = True
            ss(page, f'tmpl_idx_{template_id}')

    if not selected:
        print(f"  WARNING: Could not select template {template_id}")
        ss(page, f'picker_failed_{template_id}')

    # Wait for picker to close and step config panel to be fully re-rendered
    time.sleep(2)
    ss(page, f'after_confirm_{template_id}')

    # Check if picker closed (back to step config)
    b = body(page)
    print(f"  After picker close - body snippet: {b[:200]}")

    # Try to save the email step using Locator (not ElementHandle) to avoid stale DOM
    try:
        # Use locator - it re-queries the DOM fresh each time
        save_loc = page.locator('button:has-text("Save")').first
        save_loc.wait_for(state='visible', timeout=8000)
        save_loc.click()
        time.sleep(2)
        ss(page, f'email_saved_{template_id}')
        print(f"  Email step {template_id} SAVED")
        return True
    except Exception as e:
        print(f"  No Save button for email {template_id}: {e}")
        ss(page, f'email_no_save_{template_id}')
        close_panel(page)
        return False


def configure_wait_step(page, days):
    """
    Configure a Wait step that was just dragged to canvas.
    Panel should auto-open after drag.
    """
    print(f"\n  [WAIT] Configuring {days} days wait...")
    time.sleep(1)

    b = body(page)
    if 'Wait' not in b or 'Cancel' not in b:
        # Click the wait block to open config
        for match in page.locator('text=Wait').all():
            box = match.bounding_box()
            if box and box['x'] > 300:
                match.click()
                time.sleep(2)
                break

    ss(page, f'wait_panel_{days}d')

    # Find the duration input
    for sel in [
        'input[type="number"]',
        'input[type="text"][inputmode="numeric"]',
        '[class*="duration"] input',
        'input[name*="delay"]',
        'input[name*="duration"]',
        'input[name*="wait"]',
    ]:
        try:
            inp = page.wait_for_selector(sel, timeout=5000, state='visible')
            if inp:
                inp.click()
                page.keyboard.press('Control+a')
                page.keyboard.type(str(days))
                time.sleep(0.5)
                print(f"  Set {days} days")

                # Ensure "Days" unit is selected (not hours/minutes)
                try:
                    unit_sel_btn = page.wait_for_selector(
                        'button:has-text("Days"), button:has-text("Hours"), button:has-text("Minutes"), '
                        '[class*="unit"] button, select[class*="unit"]',
                        timeout=2000
                    )
                    if unit_sel_btn:
                        unit_txt = unit_sel_btn.evaluate('el => el.textContent').strip().lower()
                        print(f"  Current unit: {unit_txt}")
                        if 'day' not in unit_txt:
                            unit_sel_btn.click()
                            time.sleep(0.5)
                            days_opt = page.wait_for_selector(
                                'button:has-text("Days"), li:has-text("Days"), option:has-text("Days")',
                                timeout=2000
                            )
                            days_opt.click()
                            time.sleep(0.5)
                            print("  Switched to Days")
                except PlaywrightTimeout:
                    pass

                # Save - use locator to avoid stale element issues
                try:
                    save_loc = page.locator('button:has-text("Save")').first
                    save_loc.wait_for(state='visible', timeout=5000)
                    save_loc.click()
                    time.sleep(2)
                    ss(page, f'wait_saved_{days}d')
                    print(f"  Wait step SAVED ({days} days)")
                    return True
                except Exception:
                    # Try pressing Enter as fallback
                    inp.press('Enter')
                    time.sleep(1.5)
                    ss(page, f'wait_enter_{days}d')
                    return True
        except PlaywrightTimeout:
            continue

    print("  Could not find duration input for wait step")
    ss(page, f'wait_no_input_{days}d')
    close_panel(page)
    return False


def activate_automation(page):
    """Click Activate and confirm."""
    print("\n[ACTIVATE] Activating automation...")
    close_panel(page)
    time.sleep(1)
    dismiss_modals(page)
    time.sleep(0.5)

    try:
        btn_loc = page.locator('button:has-text("Activate automation")').first
        btn_loc.wait_for(state='visible', timeout=10000)
        btn_loc.click()
        time.sleep(3)
        ss(page, 'activate_clicked')
        print("  Clicked Activate")
    except Exception as e:
        print(f"  Activate button not found: {e}")
        ss(page, 'no_activate')
        return False

    # Handle any confirmation dialog
    for sel in [
        'button:has-text("Activate")',
        'button:has-text("Confirm")',
        'button:has-text("OK")',
        'button:has-text("Yes")',
    ]:
        try:
            loc = page.locator(sel).first
            if loc.is_visible():
                loc.click()
                time.sleep(3)
                print(f"  Confirmed via: {sel}")
                break
        except Exception:
            continue

    ss(page, 'ACTIVATED')
    b = body(page)
    is_active = 'Active' in b and 'Inactive' not in b
    print(f"  Activation result body: {b[:300]}")
    return is_active


def get_current_canvas_state(page):
    """Inspect and report the current canvas state."""
    b = body(page)
    steps = b.count('Step ID')
    triggers = b.count('Contact added to list')
    emails = b.count('Send an email')
    waits = b.count('Wait')
    drops = b.count('Drop block here')
    print(f"  Canvas state: {steps} steps, {triggers} triggers, {emails} email steps, "
          f"{waits} waits, {drops} drop slots")
    return {
        'steps': steps, 'triggers': triggers, 'emails': emails,
        'waits': waits, 'drops': drops
    }


def main():
    print("=" * 65)
    print("Brevo Definitive Build v2")
    print(f"Workflow: {WORKFLOW_NAME}")
    print("=" * 65)

    with open(SESSION_FILE) as f:
        session = json.load(f)
    print(f"Session: {len(session.get('cookies', []))} cookies")

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

        # ─── STEP 1: Load the automation ───────────────────────────────
        print("\n[1] Loading automation #4...")
        page.goto('https://app.brevo.com/automation/edit/4',
                  wait_until='domcontentloaded', timeout=30000)
        time.sleep(5)
        ss(page, '01_loaded')
        print(f"  Title: {page.title()}")
        state = get_current_canvas_state(page)
        print(f"  Body snippet: {body(page)[:400]}")

        # ─── STEP 2: Dismiss any modal ──────────────────────────────────
        print("\n[2] Dismissing any modals...")
        dismiss_modals(page)
        time.sleep(1)
        ss(page, '02_after_modal_dismiss')

        # ─── STEP 3: Clear the canvas ───────────────────────────────────
        print("\n[3] Clearing canvas (deleting existing blocks)...")
        cleared = delete_all_canvas_blocks(page)
        time.sleep(1)
        ss(page, '03_cleared')
        get_current_canvas_state(page)

        # ─── STEP 4: Drag trigger to canvas ─────────────────────────────
        print("\n[4] Adding trigger...")
        dismiss_modals(page)
        close_panel(page)
        time.sleep(0.5)

        triggered = drag_trigger_to_canvas(page)
        time.sleep(2)
        ss(page, '04_trigger_on_canvas')
        get_current_canvas_state(page)

        if not triggered:
            print("  WARNING: Trigger drag may have failed - proceeding anyway")

        # ─── STEP 5: Configure trigger ──────────────────────────────────
        print("\n[5] Configuring trigger...")
        configure_trigger(page)
        time.sleep(2)
        ss(page, '05_trigger_configured')
        get_current_canvas_state(page)

        # ─── STEP 6: Build email sequence ───────────────────────────────
        print("\n[6] Building email sequence...")
        print(f"  Sequence: {len(EMAIL_SEQUENCE)} emails with waits")

        steps_added = 0
        for email_i, (template_id, wait_days) in enumerate(EMAIL_SEQUENCE, 1):
            print(f"\n  === Email {email_i}/{len(EMAIL_SEQUENCE)}: "
                  f"template={template_id}, wait_before={wait_days}d ===")

            # Add wait step if needed
            if wait_days > 0:
                print(f"  Adding Wait ({wait_days}d)...")
                dragged = drag_action_to_drop_slot(page, 'Wait')
                if dragged:
                    configure_wait_step(page, wait_days)
                    steps_added += 1
                else:
                    print(f"  WARNING: Wait drag failed for email {email_i}")
                time.sleep(1)

            # Add email step
            print(f"  Adding email (template {template_id})...")
            dragged = drag_action_to_drop_slot(page, 'Send an email')
            if dragged:
                configure_email_step(page, template_id)
                steps_added += 1
            else:
                print(f"  WARNING: Email drag failed for email {email_i}")
            time.sleep(1)

            ss(page, f'after_email_{email_i}')
            get_current_canvas_state(page)

        ss(page, 'sequence_complete')
        print(f"\n  Steps added: {steps_added}")
        print(f"  Final canvas:")
        get_current_canvas_state(page)
        b = body(page)
        print(f"  Body ({len(b)} chars):\n{b[:800]}")

        # ─── STEP 7: Activate ────────────────────────────────────────────
        activated = activate_automation(page)

        ss(page, 'FINAL')
        final_url = page.url
        browser.close()

    result = {
        'workflow': WORKFLOW_NAME,
        'url': final_url,
        'activated': activated,
        'steps_added': steps_added,
        'screenshots': f'{SS_DIR}/brevo_d2_*.png',
    }
    print("\n" + "=" * 65)
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    main()
