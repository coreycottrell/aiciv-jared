"""
Deep diagnostic for Commands/Shortcuts/Agents panel failures
- Check actual DOM structure
- Check switchPanel function
- Check console errors at moment of click
- Check what selectors actually exist for nav items
"""

import asyncio
from playwright.async_api import async_playwright

PORTAL_URL = "https://app.purebrain.ai"
TOKEN = "UH0pb1T-9lghwLGzRkLzr-rs0cJYszpnLiOjsx9vSwQ"
SS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/portal-qa-20260317"

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
        await page.wait_for_timeout(4000)

        print("=== STEP 1: Find ALL nav items and their selectors ===")
        nav_info = await page.evaluate("""
            (function() {
                var allDataPanel = document.querySelectorAll('[data-panel]');
                var result = [];
                allDataPanel.forEach(function(el) {
                    var style = window.getComputedStyle(el);
                    var rect = el.getBoundingClientRect();
                    result.push({
                        panel: el.getAttribute('data-panel'),
                        tag: el.tagName,
                        id: el.id,
                        classes: el.className.substring(0, 60),
                        display: style.display,
                        visibility: style.visibility,
                        opacity: style.opacity,
                        rect: { top: Math.round(rect.top), left: Math.round(rect.left), width: Math.round(rect.width), height: Math.round(rect.height) },
                        clickable: rect.width > 0 && rect.height > 0 && style.display !== 'none'
                    });
                });
                return result;
            })()
        """)
        for item in nav_info:
            print(f"  panel={item['panel']}, clickable={item['clickable']}, rect={item['rect']}, display={item['display']}, classes={item['classes'][:50]}")

        print("\n=== STEP 2: Check switchPanel function exists ===")
        switch_info = await page.evaluate("""
            (function() {
                return {
                    switchPanel: typeof window.switchPanel,
                    loadCommands: typeof window.loadCommands,
                    loadShortcuts: typeof window.loadShortcuts,
                    agentsInterval: typeof window.agentsInterval
                };
            })()
        """)
        print(f"  window.switchPanel: {switch_info.get('switchPanel')}")
        print(f"  window.loadCommands: {switch_info.get('loadCommands')}")
        print(f"  window.loadShortcuts: {switch_info.get('loadShortcuts')}")
        print(f"  window.agentsInterval: {switch_info.get('agentsInterval')}")

        print("\n=== STEP 3: Find actual clickable Commands nav item ===")
        # Try different strategies
        commands_el_info = await page.evaluate("""
            (function() {
                // Try by data-panel
                var byDataPanel = document.querySelector('[data-panel="commands"]');
                // Try by text content
                var allEls = document.querySelectorAll('*');
                var byText = null;
                for (var i = 0; i < allEls.length; i++) {
                    var el = allEls[i];
                    if (el.textContent.trim() === 'Commands' && el.children.length <= 1) {
                        byText = el;
                        break;
                    }
                }
                // Try by sidebar nav class
                var sidebar = document.querySelector('.sidebar, [class*="sidebar"], nav');
                var navLinks = sidebar ? sidebar.querySelectorAll('[data-panel]') : [];

                return {
                    by_data_panel: byDataPanel ? {
                        tag: byDataPanel.tagName,
                        text: byDataPanel.textContent.trim().substring(0, 50),
                        rect: (function() { var r = byDataPanel.getBoundingClientRect(); return { top: Math.round(r.top), left: Math.round(r.left), w: Math.round(r.width), h: Math.round(r.height) }; })(),
                        display: window.getComputedStyle(byDataPanel).display
                    } : null,
                    by_text: byText ? byText.tagName + ': ' + byText.className.substring(0,40) : null,
                    nav_links_count: navLinks.length,
                    nav_panels: Array.from(navLinks).map(function(el) { return el.getAttribute('data-panel'); })
                };
            })()
        """)
        print(f"  by [data-panel='commands']: {commands_el_info.get('by_data_panel')}")
        print(f"  by text 'Commands': {commands_el_info.get('by_text')}")
        print(f"  sidebar nav panels: {commands_el_info.get('nav_panels')}")

        print("\n=== STEP 4: Try clicking commands via JS and check result ===")
        errors_before = len(errors)

        # Try clicking via JS
        click_result = await page.evaluate("""
            (function() {
                var el = document.querySelector('[data-panel="commands"]');
                if (!el) return 'no element found';
                // Check if there's an onclick
                var onclick = el.getAttribute('onclick');
                // Try to call switchPanel directly
                if (typeof window.switchPanel === 'function') {
                    try {
                        window.switchPanel('commands');
                        return 'called switchPanel("commands") directly';
                    } catch(e) {
                        return 'switchPanel error: ' + e.toString();
                    }
                }
                el.click();
                return 'clicked element';
            })()
        """)
        print(f"  Click result: {click_result}")
        await page.wait_for_timeout(2000)

        # Check for new errors
        new_errors = errors[errors_before:]
        print(f"  New errors after click: {new_errors}")

        # Check panel state
        panel_state = await page.evaluate("""
            (function() {
                var panel = document.getElementById('panel-commands');
                if (!panel) return { exists: false };
                var active = panel.classList.contains('active');
                var text = panel.textContent.trim();
                return {
                    exists: true,
                    active: active,
                    text_length: text.length,
                    preview: text.substring(0, 500)
                };
            })()
        """)
        print(f"  panel-commands after click: active={panel_state.get('active')}, text_length={panel_state.get('text_length')}")
        print(f"  preview: {panel_state.get('preview','')[:300]}")

        await page.screenshot(path=f"{SS_DIR}/diag-01-commands-after-js-click.png")
        print(f"  Screenshot saved: diag-01-commands-after-js-click.png")

        print("\n=== STEP 5: Try calling loadCommands() directly ===")
        errors_before2 = len(errors)
        load_result = await page.evaluate("""
            (function() {
                if (typeof window.loadCommands === 'function') {
                    try {
                        window.loadCommands();
                        return 'called loadCommands()';
                    } catch(e) {
                        return 'loadCommands error: ' + e.toString();
                    }
                }
                return 'loadCommands is not a function';
            })()
        """)
        print(f"  loadCommands result: {load_result}")
        await page.wait_for_timeout(2000)

        new_errors2 = errors[errors_before2:]
        print(f"  New errors: {new_errors2}")

        panel_state2 = await page.evaluate("""
            (function() {
                var panel = document.getElementById('panel-commands');
                if (!panel) return { exists: false };
                var text = panel.textContent.trim();
                var stuck = text.includes('Loading command reference');
                return {
                    exists: true,
                    stuck: stuck,
                    text_length: text.length,
                    preview: text.substring(0, 400)
                };
            })()
        """)
        print(f"  After loadCommands(): stuck={panel_state2.get('stuck')}, text_length={panel_state2.get('text_length')}")
        print(f"  preview: {panel_state2.get('preview','')[:300]}")

        await page.screenshot(path=f"{SS_DIR}/diag-02-commands-after-loadCommands.png")
        print(f"  Screenshot saved: diag-02-commands-after-loadCommands.png")

        print("\n=== STEP 6: Check agentsInterval in live code ===")
        agent_interval_check = await page.evaluate("""
            (function() {
                // Check if agentsInterval is accessible from window scope
                try {
                    return {
                        window_agentsInterval: typeof window.agentsInterval,
                        window_agentsInterval_value: window.agentsInterval,
                        schedInterval: typeof window.schedInterval,
                        teamsInterval: typeof window.teamsInterval
                    };
                } catch(e) {
                    return { error: e.toString() };
                }
            })()
        """)
        print(f"  agentsInterval check: {agent_interval_check}")

        print("\n=== STEP 7: Check Agents panel loading state ===")
        # Navigate to agents
        await page.evaluate("(function() { if (typeof window.switchPanel === 'function') window.switchPanel('agents'); })()")
        await page.wait_for_timeout(3000)

        agents_state = await page.evaluate("""
            (function() {
                var panel = document.getElementById('panel-agents');
                if (!panel) return { exists: false };
                var active = panel.classList.contains('active');
                var text = panel.textContent.trim();
                var loading = text.includes('Loading') || text.includes('loading');
                var items = panel.querySelectorAll('[class*="agent-row"], [class*="agent-card"], tr[data-agent], [class*="roster-row"]');
                return {
                    exists: true,
                    active: active,
                    loading: loading,
                    item_count: items.length,
                    text_length: text.length,
                    preview: text.substring(0, 300)
                };
            })()
        """)
        print(f"  Agents panel: active={agents_state.get('active')}, loading={agents_state.get('loading')}, items={agents_state.get('item_count')}, text_len={agents_state.get('text_length')}")
        print(f"  Preview: {agents_state.get('preview','')[:200]}")

        await page.screenshot(path=f"{SS_DIR}/diag-03-agents-panel-detail.png")
        print(f"  Screenshot saved: diag-03-agents-panel-detail.png")

        print("\n=== STEP 8: Check Shortcuts panel ===")
        await page.evaluate("(function() { if (typeof window.switchPanel === 'function') window.switchPanel('shortcuts'); })()")
        await page.wait_for_timeout(3000)

        shortcuts_state = await page.evaluate("""
            (function() {
                var panel = document.getElementById('panel-shortcuts');
                if (!panel) return { exists: false };
                var active = panel.classList.contains('active');
                var text = panel.textContent.trim();
                var stuck = text.includes('Loading shortcuts');
                return {
                    exists: true,
                    active: active,
                    stuck: stuck,
                    text_length: text.length,
                    preview: text.substring(0, 400)
                };
            })()
        """)
        print(f"  Shortcuts panel: active={shortcuts_state.get('active')}, stuck={shortcuts_state.get('stuck')}, text_len={shortcuts_state.get('text_length')}")
        print(f"  Preview: {shortcuts_state.get('preview','')[:200]}")

        await page.screenshot(path=f"{SS_DIR}/diag-04-shortcuts-detail.png")
        print(f"  Screenshot saved: diag-04-shortcuts-detail.png")

        print("\n=== ALL CONSOLE ERRORS DURING SESSION ===")
        for e in errors:
            print(f"  {e}")

        await browser.close()

asyncio.run(main())
