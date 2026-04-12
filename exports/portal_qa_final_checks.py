"""
Final QA checks: Commands, Shortcuts, Agents, Settings, Voice
Using the correct click targets from diagnostic step 1
"""

import asyncio
from playwright.async_api import async_playwright

PORTAL_URL = "https://app.purebrain.ai"
TOKEN = "UH0pb1T-9lghwLGzRkLzr-rs0cJYszpnLiOjsx9vSwQ"
SS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/portal-qa-20260317"

async def click_panel(page, panel_id):
    """Click a nav panel - handles multiple matching elements by using JS click"""
    result = await page.evaluate(f"""
        (function() {{
            // Get all [data-panel="{panel_id}"] elements that are clickable
            var els = document.querySelectorAll('[data-panel="{panel_id}"]');
            for (var i = 0; i < els.length; i++) {{
                var el = els[i];
                var rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {{
                    el.click();
                    return 'clicked: ' + el.tagName + '.' + el.className.substring(0,30) + ' rect=' + JSON.stringify({{w: Math.round(rect.width), h: Math.round(rect.height)}});
                }}
            }}
            return 'no clickable element found';
        }})()
    """)
    return result

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        errors = []
        page.on("console", lambda msg: errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda err: errors.append(f"[pageerror] {err}"))

        # Login
        try:
            await page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=20000)
        except:
            pass
        await page.wait_for_timeout(1500)
        await page.evaluate(f"() => {{ localStorage.setItem('portal_token', '{TOKEN}'); }}")
        try:
            await page.reload(wait_until="domcontentloaded", timeout=20000)
        except:
            pass
        await page.wait_for_timeout(5000)

        # ── COMMANDS ──────────────────────────────────────────
        print("=== COMMANDS PANEL ===")
        click_result = await click_panel(page, "commands")
        print(f"  Click result: {click_result}")
        await page.wait_for_timeout(3000)

        cs = await page.evaluate("""
            (function() {
                var p = document.getElementById('panel-commands');
                if (!p) return {exists: false};
                var text = p.textContent.trim();
                return {
                    exists: true,
                    active: p.classList.contains('active'),
                    stuck: text.includes('Loading command reference'),
                    text_length: text.length,
                    has_server_info: text.includes('Server IP') || text.includes('SSH'),
                    preview: text.substring(0, 300)
                };
            })()
        """)
        print(f"  active={cs.get('active')}, stuck={cs.get('stuck')}, text_len={cs.get('text_length')}, has_server_info={cs.get('has_server_info')}")
        print(f"  preview: {cs.get('preview','')[:200]}")

        if cs.get('has_server_info') and not cs.get('stuck'):
            print("  >>> RESULT: PASS - Commands panel shows real data!")
        elif cs.get('stuck'):
            print("  >>> RESULT: FAIL - Commands panel stuck loading")
        else:
            print(f"  >>> RESULT: UNCLEAR - text_len={cs.get('text_length')}")

        await page.screenshot(path=f"{SS_DIR}/final-commands.png")

        # ── SHORTCUTS ─────────────────────────────────────────
        print("\n=== SHORTCUTS PANEL ===")
        click_result = await click_panel(page, "shortcuts")
        print(f"  Click result: {click_result}")
        await page.wait_for_timeout(4000)

        ss = await page.evaluate("""
            (function() {
                var p = document.getElementById('panel-shortcuts');
                if (!p) return {exists: false};
                var text = p.textContent.trim();
                return {
                    exists: true,
                    active: p.classList.contains('active'),
                    stuck: text.includes('Loading shortcuts'),
                    text_length: text.length,
                    preview: text.substring(0, 400)
                };
            })()
        """)
        print(f"  active={ss.get('active')}, stuck={ss.get('stuck')}, text_len={ss.get('text_length')}")
        print(f"  preview: {ss.get('preview','')[:250]}")

        if not ss.get('stuck') and ss.get('text_length', 0) > 300:
            print("  >>> RESULT: PASS - Shortcuts panel shows real data!")
        else:
            print("  >>> RESULT: FAIL - Shortcuts panel stuck loading")
            # Try calling loadShortcuts directly
            lr = await page.evaluate("""
                (function() {
                    if (typeof window.loadShortcuts === 'function') {
                        try { window.loadShortcuts(); return 'called loadShortcuts()'; }
                        catch(e) { return 'error: ' + e.toString(); }
                    }
                    return 'loadShortcuts not found';
                })()
            """)
            print(f"  Trying loadShortcuts() directly: {lr}")
            await page.wait_for_timeout(2500)

            ss2 = await page.evaluate("""
                (function() {
                    var p = document.getElementById('panel-shortcuts');
                    var text = p ? p.textContent.trim() : '';
                    return { stuck: text.includes('Loading shortcuts'), text_length: text.length, preview: text.substring(0, 300) };
                })()
            """)
            print(f"  After loadShortcuts(): stuck={ss2.get('stuck')}, text_len={ss2.get('text_length')}")
            print(f"  preview: {ss2.get('preview','')[:200]}")
            if not ss2.get('stuck') and ss2.get('text_length', 0) > 300:
                print("  >>> RESULT: FIXED by calling loadShortcuts() directly - click handler broken but function works")
            else:
                print(f"  >>> RESULT: STILL BROKEN even after loadShortcuts()")

        await page.screenshot(path=f"{SS_DIR}/final-shortcuts.png")

        # ── AGENTS ────────────────────────────────────────────
        print("\n=== AGENTS PANEL ===")
        click_result = await click_panel(page, "agents")
        print(f"  Click result: {click_result}")
        await page.wait_for_timeout(6000)

        ag = await page.evaluate("""
            (function() {
                var p = document.getElementById('panel-agents');
                if (!p) return {exists: false};
                var text = p.textContent.trim();
                // Look for actual agent names/data
                var rows = p.querySelectorAll('[class*="roster"], [class*="agent-row"], [class*="agent-card"], table tr');
                var loading_spinner = p.querySelector('[class*="loading-spinner"], [class*="spinner"], .loading');
                return {
                    exists: true,
                    active: p.classList.contains('active'),
                    text_length: text.length,
                    row_count: rows.length,
                    has_loading_spinner: !!loading_spinner,
                    loading_text: text.includes('Loading agents') || text.includes('Loading...'),
                    preview: text.substring(0, 500)
                };
            })()
        """)
        print(f"  active={ag.get('active')}, text_len={ag.get('text_length')}, rows={ag.get('row_count')}, spinner={ag.get('has_loading_spinner')}, loading_text={ag.get('loading_text')}")
        print(f"  preview: {ag.get('preview','')[:300]}")

        if ag.get('row_count', 0) > 5 and not ag.get('has_loading_spinner'):
            print("  >>> RESULT: PASS - Agents panel shows real data!")
        elif ag.get('text_length', 0) > 1000:
            print("  >>> RESULT: PASS (likely) - Long text content, appears loaded")
        else:
            print(f"  >>> RESULT: UNCLEAR/FAIL - rows={ag.get('row_count')}, text_len={ag.get('text_length')}")

        await page.screenshot(path=f"{SS_DIR}/final-agents.png")

        # ── SETTINGS ──────────────────────────────────────────
        print("\n=== SETTINGS (gear icon in top bar) ===")
        # The top bar has buttons - find the gear icon
        topbar_buttons = await page.evaluate("""
            (function() {
                // Look in the top bar area
                var candidates = document.querySelectorAll(
                    '[class*="top-bar"] *, header *, [class*="topbar"] *'
                );
                var results = [];
                candidates.forEach(function(el) {
                    if (el.tagName === 'BUTTON' || el.tagName === 'A' || el.getAttribute('onclick')) {
                        var rect = el.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0 && rect.top < 80) {
                            results.push({
                                tag: el.tagName,
                                id: el.id,
                                class: el.className.substring(0,50),
                                title: el.title || el.getAttribute('aria-label') || '',
                                text: el.textContent.trim().substring(0, 30),
                                rect: { top: Math.round(rect.top), left: Math.round(rect.left), w: Math.round(rect.width) }
                            });
                        }
                    }
                });
                return results;
            })()
        """)
        print(f"  Top bar clickable elements:")
        for b in topbar_buttons:
            print(f"    {b}")

        # Try clicking the gear icon by coordinates or by SVG/icon content
        settings_el = await page.evaluate("""
            (function() {
                // Try various ways to find the settings button
                var selectors = [
                    '#settings-btn',
                    '[id*="settings"]',
                    'button[onclick*="settings"]',
                    '[class*="settings-toggle"]',
                    '[class*="gear"]'
                ];
                for (var i = 0; i < selectors.length; i++) {
                    var el = document.querySelector(selectors[i]);
                    if (el) {
                        var rect = el.getBoundingClientRect();
                        return { found: true, selector: selectors[i], id: el.id, class: el.className.substring(0,50), rect: rect };
                    }
                }
                return { found: false };
            })()
        """)
        print(f"  Settings element search: {settings_el}")

        # Try clicking the gear icon at position from the desktop screenshot
        # In the screenshot, the gear icon appears at approximately x=1259, y=22 (top bar right side)
        try:
            await page.click('#settings-btn', timeout=2000)
            print("  Clicked #settings-btn")
        except:
            try:
                await page.click('[class*="settings-toggle"]', timeout=2000)
                print("  Clicked settings-toggle")
            except:
                print("  Could not click settings button via selector - trying coordinates")
                await page.mouse.click(1259, 22)

        await page.wait_for_timeout(2000)
        await page.screenshot(path=f"{SS_DIR}/final-settings.png")
        print(f"  Screenshot: final-settings.png")

        settings_state = await page.evaluate("""
            (function() {
                // Find any modal or panel that appeared
                var modals = document.querySelectorAll('[class*="modal"], [class*="settings"]');
                var visible = [];
                modals.forEach(function(m) {
                    var style = window.getComputedStyle(m);
                    if (style.display !== 'none' && style.visibility !== 'hidden' && m.offsetHeight > 0) {
                        visible.push({
                            id: m.id,
                            class: m.className.substring(0,60),
                            text: m.textContent.trim().substring(0, 100)
                        });
                    }
                });
                return visible;
            })()
        """)
        print(f"  Visible modals/settings after click: {settings_state}")

        # ── VOICE/HMI ─────────────────────────────────────────
        print("\n=== VOICE/HMI LOCATION ===")
        voice_elements = await page.evaluate("""
            (function() {
                var all = document.querySelectorAll('[class*="voice"], [id*="voice"], [class*="hmi"], [id*="hmi"]');
                var results = [];
                all.forEach(function(el) {
                    var rect = el.getBoundingClientRect();
                    var style = window.getComputedStyle(el);
                    results.push({
                        id: el.id,
                        class: el.className.substring(0, 60),
                        tag: el.tagName,
                        display: style.display,
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                        data_panel: el.getAttribute('data-panel')
                    });
                });
                return results;
            })()
        """)
        for v in voice_elements:
            print(f"  {v}")

        # ── TASKS COUNT ───────────────────────────────────────
        print("\n=== TASKS PANEL (badge count) ===")
        click_result = await click_panel(page, "tasks")
        await page.wait_for_timeout(2000)
        tasks_badge = await page.evaluate("""
            (function() {
                var badge = document.querySelector('[data-panel="tasks"] [class*="badge"], [data-panel="tasks"] [class*="count"]');
                var panel = document.getElementById('panel-tasks');
                return {
                    badge_text: badge ? badge.textContent.trim() : 'none',
                    panel_text_length: panel ? panel.textContent.trim().length : 0
                };
            })()
        """)
        print(f"  Tasks badge: {tasks_badge}")

        # ── TERMINAL ──────────────────────────────────────────
        print("\n=== TERMINAL PANEL ===")
        click_result = await click_panel(page, "terminal")
        await page.wait_for_timeout(2000)
        terminal_state = await page.evaluate("""
            (function() {
                var p = document.getElementById('panel-terminal');
                if (!p) return {exists: false};
                var text = p.textContent.trim();
                return {
                    exists: true,
                    active: p.classList.contains('active'),
                    text_length: text.length,
                    has_output: text.length > 100
                };
            })()
        """)
        print(f"  Terminal: active={terminal_state.get('active')}, text_len={terminal_state.get('text_length')}")
        await page.screenshot(path=f"{SS_DIR}/final-terminal.png")

        print("\n=== CONSOLE ERRORS TOTAL ===")
        print(f"  Total errors: {len(errors)}")
        for e in errors[:15]:
            print(f"  {e}")

        await browser.close()

asyncio.run(main())
