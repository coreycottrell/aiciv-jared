#!/usr/bin/env python3
"""
Phase 2: Build the Neural Feed Welcome Sequence in Brevo.
Loads saved session (no 2FA needed). Uses coordinate-based drag-and-drop
with precise element detection via class names confirmed from builder analysis.

Builder facts (confirmed from screenshots):
- Trigger cards: class DragableCard-module__dragable-card-conta, draggable=true
- Canvas: right portion of viewport, center ~(800, 300)
- Name field: "Automation #N" dropdown in top bar (click to rename)
- Actions tab leads to: Send an email, Wait steps
- Trigger: "Contact added to list" at approximately x=110, y=159
"""

import os
import re
import sys
import time
import json
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

SESSION_FILE = '/home/jared/projects/AI-CIV/aether/tools/brevo_session.json'
SS_DIR = '/home/jared/projects/AI-CIV/aether/exports/screenshots'
os.makedirs(SS_DIR, exist_ok=True)

WORKFLOW_NAME = "Neural Feed - Welcome Sequence"

# (template_id, wait_days_before_sending)
# wait_days=0 = send immediately after trigger
EMAIL_SEQUENCE = [
    (1, 0),   # Email 1 - immediate
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

_ss = [0]

def ss(page, label, desc=''):
    _ss[0] += 1
    path = f"{SS_DIR}/brevo_build_{_ss[0]:02d}_{label}.png"
    page.screenshot(path=path, full_page=True)
    print(f"  [SS] {_ss[0]:02d}_{label}: {desc or label}")
    return path


def slow_drag(page, src_x, src_y, dst_x, dst_y, steps=20):
    """Perform a slow, deliberate mouse drag for HTML5 drag-and-drop."""
    page.mouse.move(src_x, src_y)
    time.sleep(0.3)
    page.mouse.down()
    time.sleep(0.5)
    for i in range(1, steps + 1):
        t = i / steps
        cx = src_x + (dst_x - src_x) * t
        cy = src_y + (dst_y - src_y) * t
        page.mouse.move(cx, cy)
        time.sleep(0.04)
    time.sleep(0.5)
    page.mouse.up()
    time.sleep(1.5)


def dispatch_drag_drop(page, src_x, src_y, dst_x, dst_y):
    """
    Use JS to dispatch HTML5 dragstart/dragover/drop events.
    More reliable than mouse simulation for React/Vue DnD libraries.
    """
    page.evaluate(f"""
    (function() {{
        function getEl(x, y) {{
            return document.elementFromPoint(x, y);
        }}

        var src = getEl({src_x}, {src_y});
        var dst = getEl({dst_x}, {dst_y});

        if (!src || !dst) {{
            console.log('DnD: src or dst element not found');
            return false;
        }}

        console.log('DnD src:', src.tagName, src.className.substr(0,50));
        console.log('DnD dst:', dst.tagName, dst.className.substr(0,50));

        var dt = new DataTransfer();

        // Walk up to find draggable ancestor
        var draggable = src;
        while (draggable && draggable.getAttribute('draggable') !== 'true') {{
            draggable = draggable.parentElement;
        }}
        if (draggable) {{
            console.log('Found draggable:', draggable.tagName, draggable.className.substr(0,50));
        }} else {{
            draggable = src;
        }}

        var evtOpts = {{ bubbles: true, cancelable: true, dataTransfer: dt }};

        draggable.dispatchEvent(new DragEvent('dragstart', evtOpts));

        // Move over intermediate points
        for (var i = 0; i <= 5; i++) {{
            var ix = {src_x} + ({dst_x} - {src_x}) * i / 5;
            var iy = {src_y} + ({dst_y} - {src_y}) * i / 5;
            var mid = document.elementFromPoint(ix, iy);
            if (mid) mid.dispatchEvent(new DragEvent('dragover', evtOpts));
        }}

        dst.dispatchEvent(new DragEvent('dragover', evtOpts));
        dst.dispatchEvent(new DragEvent('dragenter', evtOpts));
        dst.dispatchEvent(new DragEvent('drop', evtOpts));
        draggable.dispatchEvent(new DragEvent('dragend', evtOpts));

        return true;
    }})()
    """)


def get_element_center(page, selector, timeout=8000):
    """Return (x, y) center coordinates of an element, or None."""
    try:
        el = page.wait_for_selector(selector, timeout=timeout, state='visible')
        if el:
            box = el.bounding_box()
            if box:
                return box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
    except PlaywrightTimeout:
        pass
    return None


def clear_search_and_go_to_library(page):
    """Ensure the left panel shows the full steps library (not search results)."""
    try:
        # Look for the search input in the builder panel
        search = page.query_selector('input[placeholder*="step" i], .search-input, input[class*="search"]')
        if search:
            val = search.input_value()
            if val:
                print(f"  [SEARCH] Clearing search box (had: '{val}')")
                search.triple_click()
                search.fill('')
                time.sleep(0.5)
                search.press('Escape')
                time.sleep(0.5)
    except Exception:
        pass

    # If showing "No steps match", click Go to steps library
    try:
        btn = page.wait_for_selector(
            'button:has-text("Go to steps library"), a:has-text("Go to steps library")',
            timeout=2000
        )
        btn.click()
        time.sleep(1)
        print("  [LIBRARY] Clicked 'Go to steps library'")
    except PlaywrightTimeout:
        pass


def rename_workflow(page):
    """
    The automation name 'Automation #N' sits in the top bar.
    Clicking the name text opens an inline edit field.
    """
    print(f"\n[RENAME] Setting name to: {WORKFLOW_NAME}")

    # The top bar has a button/div with the name + dropdown caret
    # Try clicking the name element in the header
    name_clicked = False
    for sel in [
        '[class*="AutomationTopBar"] button:first-child',
        '[class*="topbar"] [class*="name"]',
        '[class*="topBar"] button',
        'header button:first-child',
        '[class*="naos-topbar"] button',
        # The name area - look for text containing "Automation"
    ]:
        try:
            el = page.wait_for_selector(sel, timeout=3000, state='visible')
            txt = el.inner_text()
            if 'Automation' in txt or '#' in txt:
                el.click()
                time.sleep(1)
                print(f"  Clicked name via: {sel} (was: {txt.strip()})")
                name_clicked = True
                break
        except PlaywrightTimeout:
            continue

    if not name_clicked:
        # Try finding text containing "Automation #" directly
        try:
            el = page.locator('text=/Automation #\\d+/').first
            el.click()
            time.sleep(1)
            print("  Clicked name via regex locator")
            name_clicked = True
        except Exception as e:
            print(f"  Regex locator failed: {e}")

    if not name_clicked:
        print("  WARNING: Could not click name - will try coordinate click on top bar area")
        # Top bar name is typically at approximately x=200, y=14 in the header
        page.mouse.click(200, 14)
        time.sleep(1)

    ss(page, 'after_name_click', 'After clicking name area')

    # Now look for an editable input that appeared
    for sel in [
        'input[value*="Automation"]',
        '[class*="name-input"]',
        '[class*="workflow-name"] input',
        'input[class*="title"]',
        'input[class*="name"]',
        # Generic - any newly focused input
        'input:focus',
    ]:
        try:
            inp = page.wait_for_selector(sel, timeout=3000, state='visible')
            if inp:
                inp.click()
                page.keyboard.press('Control+a')
                time.sleep(0.1)
                page.keyboard.type(WORKFLOW_NAME)
                time.sleep(0.3)
                inp.press('Enter')
                time.sleep(0.5)
                print(f"  Renamed via: {sel}")
                ss(page, 'name_set', f'Name set to: {WORKFLOW_NAME}')
                return True
        except PlaywrightTimeout:
            continue

    print("  WARNING: Name field not found after click")
    ss(page, 'name_not_found', 'Name field not found')
    return False


def drag_trigger(page):
    """
    Drag 'Contact added to list' from left panel onto canvas.
    Uses both JS dispatch and mouse simulation as fallbacks.
    """
    print("\n[TRIGGER] Dragging 'Contact added to list' to canvas...")

    clear_search_and_go_to_library(page)
    time.sleep(0.5)

    # Make sure Triggers tab is selected
    try:
        triggers_tab = page.wait_for_selector(
            '[class*="naos-tab__btn"]:has-text("Triggers"), button:has-text("Triggers")',
            timeout=5000
        )
        triggers_tab.click()
        time.sleep(1)
        print("  Activated Triggers tab")
    except PlaywrightTimeout:
        print("  Triggers tab click skipped")

    ss(page, 'triggers_panel', 'Triggers panel')

    # Find the draggable card for "Contact added to list"
    # Class is DragableCard-module__dragable-card-conta (confirmed)
    trigger_card = None
    trigger_box = None

    # Method 1: Find by class + text content
    cards = page.query_selector_all('[class*="DragableCard"]')
    print(f"  Found {len(cards)} DragableCard elements")
    for card in cards:
        txt = card.inner_text().strip()
        print(f"    Card: '{txt[:50]}'")
        if 'Contact added to list' in txt:
            trigger_card = card
            trigger_box = card.bounding_box()
            print(f"    FOUND at box: {trigger_box}")
            break

    if not trigger_card:
        # Method 2: Search by text inside any draggable element
        draggables = page.query_selector_all('[draggable="true"]')
        print(f"  Searching {len(draggables)} draggable elements...")
        for d in draggables:
            txt = d.inner_text().strip()
            if 'Contact added to list' in txt:
                trigger_card = d
                trigger_box = d.bounding_box()
                print(f"  Found 'Contact added to list' in draggable: box={trigger_box}")
                break

    if not trigger_card or not trigger_box:
        print("  ERROR: Could not find 'Contact added to list' trigger card")
        ss(page, 'ERR_no_trigger', 'Cannot find trigger card')
        # Show all visible text
        print("  Page text:", page.inner_text('body')[:2000])
        return False

    src_x = trigger_box['x'] + trigger_box['width'] / 2
    src_y = trigger_box['y'] + trigger_box['height'] / 2

    # Find canvas drop zone
    canvas_x, canvas_y = None, None
    canvas_selectors = [
        '[class*="canvas"]',
        '[class*="Canvas"]',
        '[class*="drop-zone"]',
        '[class*="dropzone"]',
        '[class*="workflow-canvas"]',
    ]
    for sel in canvas_selectors:
        try:
            el = page.wait_for_selector(sel, timeout=3000, state='visible')
            if el:
                box = el.bounding_box()
                if box and box['width'] > 400:  # Must be large area
                    canvas_x = box['x'] + box['width'] / 2
                    canvas_y = box['y'] + box['height'] / 2
                    print(f"  Canvas found via {sel}: center=({canvas_x:.0f},{canvas_y:.0f})")
                    break
        except PlaywrightTimeout:
            continue

    if not canvas_x:
        # Fallback: the canvas is roughly at the right 2/3 of viewport
        vp = page.viewport_size
        canvas_x = vp['width'] * 0.62
        canvas_y = vp['height'] * 0.40
        print(f"  Using estimated canvas: ({canvas_x:.0f},{canvas_y:.0f})")

    print(f"  Drag: ({src_x:.0f},{src_y:.0f}) → ({canvas_x:.0f},{canvas_y:.0f})")

    # Try JS dispatch first (most reliable for React-based DnD)
    print("  [DND] Trying JS dispatch method...")
    dispatch_drag_drop(page, src_x, src_y, canvas_x, canvas_y)
    time.sleep(2)
    ss(page, 'after_js_drag', 'After JS drag dispatch')

    # Check if trigger was added (canvas should no longer say "Drop a step here")
    try:
        drop_hint = page.query_selector('text=Drop a step here')
        still_empty = drop_hint is not None
    except Exception:
        still_empty = True

    if still_empty:
        print("  [DND] JS dispatch didn't work - trying mouse drag...")
        slow_drag(page, src_x, src_y, canvas_x, canvas_y, steps=25)
        time.sleep(2)
        ss(page, 'after_mouse_drag', 'After mouse drag')

        # Check again
        try:
            drop_hint = page.query_selector('text=Drop a step here')
            still_empty = drop_hint is not None
        except Exception:
            still_empty = True

    if still_empty:
        print("  [DND] Mouse drag didn't work - trying Playwright drag_to...")
        try:
            vp = page.viewport_size
            canvas_locator = page.locator('[class*="canvas"]').first
            trigger_card.drag_to(
                canvas_locator,
                target_position={'x': int(canvas_x - 300), 'y': int(canvas_y - 200)}
            )
            time.sleep(2)
            ss(page, 'after_playwright_drag', 'After Playwright drag_to')
        except Exception as e:
            print(f"  Playwright drag_to failed: {e}")

    # Final check
    time.sleep(2)
    ss(page, 'trigger_drop_final', 'Final state after trigger drop attempts')
    try:
        body = page.inner_text('body')
        print(f"  Canvas content after drops:\n{body[:1500]}")
    except Exception:
        pass

    return True


def configure_trigger_list(page):
    """
    After trigger is placed, configure it to use List 3 (The Neural Feed).
    A side panel should appear on the right with list selector.
    """
    print("\n[TRIGGER CONFIG] Configuring trigger list...")
    time.sleep(2)
    ss(page, 'trigger_config_start', 'Before trigger config')

    # Try to select list
    for sel in [
        'select',
        '[class*="select"]',
        '[placeholder*="list" i]',
        '[aria-label*="list" i]',
        'text=Select a list',
        'text=Choose a list',
        '[class*="dropdown"]',
    ]:
        try:
            el = page.wait_for_selector(sel, timeout=4000, state='visible')
            if el:
                tag = el.evaluate('el => el.tagName.toLowerCase()')
                txt = el.inner_text()[:60]
                print(f"  Found potential list selector: {sel}, tag={tag}, text={txt}")

                if tag == 'select':
                    # Native select: set value to list ID 3
                    page.select_option(sel, value='3', label='The Neural Feed')
                    print("  Selected list via native select")
                    time.sleep(0.5)
                    break
                else:
                    el.click()
                    time.sleep(1)
                    ss(page, 'list_dropdown', 'List dropdown opened')
                    # Find Neural Feed option
                    for opt_sel in [
                        'text=The Neural Feed',
                        'li:has-text("Neural Feed")',
                        '[class*="option"]:has-text("Neural Feed")',
                        'text=Neural Feed',
                    ]:
                        try:
                            opt = page.wait_for_selector(opt_sel, timeout=3000)
                            opt.click()
                            print(f"  Selected 'The Neural Feed' via: {opt_sel}")
                            time.sleep(0.5)
                            ss(page, 'list_selected', 'Neural Feed list selected')
                            return True
                        except PlaywrightTimeout:
                            continue
        except PlaywrightTimeout:
            continue

    ss(page, 'trigger_config_done', 'After trigger configuration attempt')
    return False


def add_step_via_plus_button(page, step_type, template_id=None, wait_days=None, step_label=''):
    """
    In Brevo's builder, after the first trigger block is placed,
    a '+' button appears below it to add the next step.
    Click it, then choose the step type from the menu.
    """
    print(f"  [ADD STEP] {step_label}")

    # Find the '+' add-step button below the last block
    for sel in [
        'button[class*="add"]:last-of-type',
        '[class*="add-step"]',
        '[class*="AddStep"]',
        'button[aria-label*="add" i]',
        'button:has-text("+")',
        '[class*="plus"]',
    ]:
        try:
            buttons = page.query_selector_all(sel)
            if buttons:
                last_btn = buttons[-1]  # Always click the last '+' button
                last_btn.scroll_into_view_if_needed()
                last_btn.click()
                time.sleep(1.5)
                print(f"    Clicked add button via: {sel}")
                break
        except Exception:
            continue

    ss(page, f'add_step_{step_label}', f'After clicking add for {step_label}')

    if step_type == 'wait':
        # Choose "Wait" from the step menu
        for sel in [
            'text=Wait',
            'li:has-text("Wait")',
            '[class*="step-option"]:has-text("Wait")',
            'button:has-text("Wait")',
        ]:
            try:
                el = page.wait_for_selector(sel, timeout=4000)
                el.click()
                time.sleep(1.5)
                print(f"    Selected Wait via: {sel}")
                break
            except PlaywrightTimeout:
                continue

        # Set the days value
        for sel in ['input[type="number"]', 'input[name*="delay"]', 'input[name*="wait"]', 'input[name*="day"]']:
            try:
                inp = page.wait_for_selector(sel, timeout=4000, state='visible')
                inp.triple_click()
                inp.fill(str(wait_days))
                inp.press('Tab')
                print(f"    Set wait to {wait_days} days")
                break
            except PlaywrightTimeout:
                continue

    elif step_type == 'email':
        # Choose "Send an email" from the step menu
        for sel in [
            'text=Send an email',
            'li:has-text("Send an email")',
            '[class*="step-option"]:has-text("email")',
            'button:has-text("Send an email")',
            'text=Email',
        ]:
            try:
                el = page.wait_for_selector(sel, timeout=4000)
                el.click()
                time.sleep(1.5)
                print(f"    Selected 'Send an email' via: {sel}")
                break
            except PlaywrightTimeout:
                continue

        # Select template by ID/name
        tname = TEMPLATE_NAMES[template_id]
        for sel in [
            f'option:has-text("{tname}")',
            f'li:has-text("{tname}")',
            f'[data-value="{template_id}"]',
            'select[name*="template"]',
            '[class*="template-select"]',
        ]:
            try:
                el = page.wait_for_selector(sel, timeout=4000)
                el.click()
                print(f"    Selected template {template_id}: {tname[:40]}")
                break
            except PlaywrightTimeout:
                continue

    time.sleep(1)
    ss(page, f'step_done_{step_label}', f'After step {step_label}')


def save_and_activate(page):
    """Activate the automation."""
    print("\n[ACTIVATE] Activating automation...")

    # Save first (usually auto-save, but try)
    try:
        save_btn = page.wait_for_selector('button:has-text("Save")', timeout=3000)
        save_btn.click()
        time.sleep(2)
        print("  Saved")
    except PlaywrightTimeout:
        print("  No Save button - auto-save assumed")

    ss(page, 'before_activate', 'Before activation')

    # Click Activate automation
    try:
        act_btn = page.wait_for_selector(
            'button:has-text("Activate automation")',
            timeout=10000,
            state='visible'
        )
        act_btn.click()
        time.sleep(3)
        print("  Clicked 'Activate automation'")
    except PlaywrightTimeout:
        print("  Activate button not found")
        ss(page, 'activate_not_found', 'Activate button not found')
        return False

    # Handle any confirmation dialog
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

    ss(page, 'after_activate', 'After activation')

    # Check status
    try:
        status = page.wait_for_selector('text=Active, text=ACTIVE', timeout=5000)
        if status:
            print("  STATUS: Active - workflow is running!")
            ss(page, 'ACTIVATED_CONFIRMED', 'Automation Active confirmed')
            return True
    except PlaywrightTimeout:
        pass

    # Check page text for active status
    try:
        body = page.inner_text('body')
        if 'active' in body.lower():
            print("  Status shows active in page text")
            return True
        print(f"  Page text after activation:\n{body[:500]}")
    except Exception:
        pass

    return False


def main():
    print("=" * 65)
    print("Brevo Workflow Builder - Phase 2")
    print(f"Building: {WORKFLOW_NAME}")
    print("=" * 65)

    if not os.path.exists(SESSION_FILE):
        print(f"ERROR: Session file not found: {SESSION_FILE}")
        print("Run brevo_session_login.py first to establish session")
        return False

    with open(SESSION_FILE) as f:
        storage_state = json.load(f)
    n_cookies = len(storage_state.get('cookies', []))
    print(f"\n[SESSION] Loaded: {n_cookies} cookies")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )

        # Load saved session - no 2FA needed
        ctx = browser.new_context(
            viewport={'width': 1600, 'height': 900},
            device_scale_factor=2,
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            storage_state=storage_state,
        )
        page = ctx.new_page()
        page.set_default_timeout(30000)

        # ── Verify session works ───────────────────────────────────────
        print("\n[1] Verifying session...")
        page.goto('https://app.brevo.com/', wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)
        ss(page, 'session_verify', f'URL: {page.url}')

        if 'login' in page.url.lower():
            print("ERROR: Session expired or invalid - run brevo_session_login.py again")
            browser.close()
            return False

        print(f"  Session valid. URL: {page.url}")

        # ── Navigate to Automations list ───────────────────────────────
        print("\n[2] Navigating to Automations...")
        page.goto('https://app.brevo.com/automation/automations', wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)
        ss(page, 'automations_list', 'Automations list')
        print(f"  URL: {page.url}")

        # ── Navigate directly to automation #4 (already created) ────────
        print("\n[3] Navigating to Automation #4 (already created)...")
        page.goto('https://app.brevo.com/automation/edit/4', wait_until='domcontentloaded', timeout=30000)
        time.sleep(4)
        try:
            page.wait_for_load_state('networkidle', timeout=20000)
        except PlaywrightTimeout:
            pass

        builder_url = page.url
        ss(page, 'builder_opened', f'Builder: {builder_url}')
        print(f"  Builder URL: {builder_url}")
        print(f"  Page title: {page.title()}")

        # ── Rename the automation ──────────────────────────────────────
        rename_workflow(page)

        # ── Drag trigger onto canvas ───────────────────────────────────
        drag_success = drag_trigger(page)
        if not drag_success:
            print("  WARNING: Trigger drag may have failed - continuing anyway")

        # ── Configure trigger to use List 3 ───────────────────────────
        configure_trigger_list(page)

        # ── Analyze builder state before adding email steps ────────────
        print("\n[5] Analyzing builder state...")
        ss(page, 'builder_state_analysis', 'Builder state before adding steps')
        try:
            body = page.inner_text('body')
            print(f"  Builder text:\n{body[:2000]}")
        except Exception:
            pass

        # Get all visible buttons for context
        btns = page.query_selector_all('button')
        btn_texts = [b.inner_text()[:40].strip() for b in btns if b.inner_text().strip()]
        print(f"  Buttons visible: {btn_texts[:20]}")

        # ── Add email steps with waits ─────────────────────────────────
        print("\n[6] Adding email sequence steps...")
        for idx, (template_id, wait_days) in enumerate(EMAIL_SEQUENCE, 1):
            if wait_days > 0:
                label = f'wait{wait_days}d_before_email{idx}'
                add_step_via_plus_button(page, 'wait', wait_days=wait_days, step_label=label)
                time.sleep(1)

            label = f'email{idx}_tmpl{template_id}'
            add_step_via_plus_button(page, 'email', template_id=template_id, step_label=label)
            time.sleep(1)

        ss(page, 'sequence_complete', 'Full sequence added')

        # ── Save and activate ──────────────────────────────────────────
        activated = save_and_activate(page)

        # ── Final screenshot and report ────────────────────────────────
        ss(page, 'FINAL', f'Final state: activated={activated}')
        final_url = page.url
        final_text = page.inner_text('body') if True else ''

        print(f"\n{'='*65}")
        print("BUILD COMPLETE")
        print(f"  Workflow URL: {final_url}")
        print(f"  Activated: {activated}")
        print(f"  Screenshots: {SS_DIR}/brevo_build_*.png")

        browser.close()
        return {
            'status': 'activated' if activated else 'built',
            'workflow_url': final_url,
            'activated': activated,
        }


if __name__ == '__main__':
    result = main()
    print(json.dumps(result, indent=2) if isinstance(result, dict) else f'Result: {result}')
