"""
Final diagnostic: Shortcuts panel loading issue + Settings/Voice discovery
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
        await page.wait_for_timeout(5000)  # Extra wait for full initialization

        print("=== TEST: Commands panel via direct click ===")
        # Use the actual clickable element
        await page.click('div.nav-item[data-panel="commands"]', timeout=5000)
        await page.wait_for_timeout(3000)

        commands_state = await page.evaluate("""
            (function() {
                var panel = document.getElementById('panel-commands');
                if (!panel) return { exists: false };
                var text = panel.textContent.trim();
                var stuck = text.includes('Loading command reference');
                return {
                    exists: true,
                    active: panel.classList.contains('active'),
                    stuck: stuck,
                    text_length: text.length,
                    preview: text.substring(0, 200)
                };
            })()
        """)
        print(f"  Commands: active={commands_state.get('active')}, stuck={commands_state.get('stuck')}, text_len={commands_state.get('text_length')}")
        if not commands_state.get('stuck') and commands_state.get('text_length', 0) > 500:
            print("  >>> COMMANDS PANEL: PASS - Real data loaded!")
        else:
            print(f"  >>> COMMANDS PANEL: FAIL - Preview: {commands_state.get('preview','')[:200]}")

        await page.screenshot(path=f"{SS_DIR}/final-01-commands.png")
        print(f"  Screenshot: final-01-commands.png")

        print("\n=== TEST: Shortcuts panel via direct click ===")
        await page.click('div.nav-item[data-panel="shortcuts"]', timeout=5000)
        await page.wait_for_timeout(4000)

        shortcuts_state = await page.evaluate("""
            (function() {
                var panel = document.getElementById('panel-shortcuts');
                if (!panel) return { exists: false };
                var text = panel.textContent.trim();
                var stuck = text.includes('Loading shortcuts');
                return {
                    exists: true,
                    active: panel.classList.contains('active'),
                    stuck: stuck,
                    text_length: text.length,
                    preview: text.substring(0, 500)
                };
            })()
        """)
        print(f"  Shortcuts: active={shortcuts_state.get('active')}, stuck={shortcuts_state.get('stuck')}, text_len={shortcuts_state.get('text_length')}")
        if not shortcuts_state.get('stuck') and shortcuts_state.get('text_length', 0) > 300:
            print("  >>> SHORTCUTS PANEL: PASS - Real data loaded!")
        else:
            print(f"  >>> SHORTCUTS PANEL: still stuck. Trying loadShortcuts()...")
            load_result = await page.evaluate("""
                (function() {
                    if (typeof window.loadShortcuts === 'function') {
                        try { window.loadShortcuts(); return 'called'; }
                        catch(e) { return 'error: ' + e.toString(); }
                    }
                    return 'not a function';
                })()
            """)
            print(f"  loadShortcuts() result: {load_result}")
            await page.wait_for_timeout(2000)

            shortcuts_state2 = await page.evaluate("""
                (function() {
                    var panel = document.getElementById('panel-shortcuts');
                    var text = panel ? panel.textContent.trim() : '';
                    return {
                        stuck: text.includes('Loading shortcuts'),
                        text_length: text.length,
                        preview: text.substring(0, 400)
                    };
                })()
            """)
            print(f"  After loadShortcuts(): stuck={shortcuts_state2.get('stuck')}, text_len={shortcuts_state2.get('text_length')}")
            print(f"  Preview: {shortcuts_state2.get('preview','')[:300]}")

        await page.screenshot(path=f"{SS_DIR}/final-02-shortcuts.png")
        print(f"  Screenshot: final-02-shortcuts.png")

        print("\n=== TEST: Agents panel with longer wait ===")
        await page.click('div.nav-item[data-panel="agents"]', timeout=5000)
        await page.wait_for_timeout(5000)

        agents_state = await page.evaluate("""
            (function() {
                var panel = document.getElementById('panel-agents');
                if (!panel) return { exists: false };
                var text = panel.textContent.trim();
                var loading = text.includes('Loading') && panel.querySelectorAll('[class*="loading"]').length > 0;
                var rows = panel.querySelectorAll('[class*="roster-row"], [class*="agent-row"], [data-agent]');
                var cards = panel.querySelectorAll('[class*="agent-card"]');
                return {
                    exists: true,
                    active: panel.classList.contains('active'),
                    loading_indicator: loading,
                    row_count: rows.length,
                    card_count: cards.length,
                    text_length: text.length,
                    preview: text.substring(0, 400)
                };
            })()
        """)
        print(f"  Agents: active={agents_state.get('active')}, loading={agents_state.get('loading_indicator')}, rows={agents_state.get('row_count')}, cards={agents_state.get('card_count')}, text_len={agents_state.get('text_length')}")
        print(f"  Preview: {agents_state.get('preview','')[:200]}")

        await page.screenshot(path=f"{SS_DIR}/final-03-agents.png")
        print(f"  Screenshot: final-03-agents.png")

        print("\n=== TEST: Settings button (top bar gear icon) ===")
        # Settings is often a gear icon in the top bar, not a sidebar nav item
        settings_clicked = False
        for sel in [
            'button[title*="Settings"]',
            '[class*="settings-btn"]',
            '.gear-icon',
            'button[aria-label*="settings"]',
            '.top-bar [class*="settings"]',
            'header button',
            '[title*="settings"]',
            # Try the gear icon by coordinates (it's in the top right area)
        ]:
            try:
                elements = await page.query_selector_all(sel)
                if elements:
                    await elements[0].click()
                    settings_clicked = True
                    print(f"  Clicked settings via: {sel}")
                    break
            except:
                pass

        if not settings_clicked:
            # Try clicking the gear icon in the top bar
            topbar_info = await page.evaluate("""
                (function() {
                    var buttons = document.querySelectorAll('header button, .top-bar button, [class*="topbar"] button, [class*="top-bar"] a');
                    var results = [];
                    buttons.forEach(function(btn) {
                        var rect = btn.getBoundingClientRect();
                        results.push({
                            tag: btn.tagName,
                            text: btn.textContent.trim().substring(0,30),
                            title: btn.getAttribute('title') || '',
                            class: btn.className.substring(0,50),
                            id: btn.id || '',
                            rect: { top: Math.round(rect.top), left: Math.round(rect.left), w: Math.round(rect.width) }
                        });
                    });
                    return results;
                })()
            """)
            print(f"  Top bar buttons: {topbar_info}")

        await page.wait_for_timeout(2000)
        await page.screenshot(path=f"{SS_DIR}/final-04-settings.png")
        print(f"  Screenshot: final-04-settings.png")

        settings_state = await page.evaluate("""
            (function() {
                var modal = document.querySelector('[class*="settings-modal"], [class*="settings-panel"], [id*="settings"]');
                return modal ? {
                    found: true,
                    visible: window.getComputedStyle(modal).display !== 'none',
                    class: modal.className.substring(0, 60),
                    text_length: modal.textContent.trim().length
                } : { found: false };
            })()
        """)
        print(f"  Settings state: {settings_state}")

        print("\n=== TEST: Voice nav location ===")
        voice_info = await page.evaluate("""
            (function() {
                // Look for voice-related elements anywhere on page
                var voiceEls = document.querySelectorAll('[class*="voice"], [id*="voice"], [data-panel*="voice"], [class*="hmi"], [id*="hmi"]');
                var results = [];
                voiceEls.forEach(function(el) {
                    var rect = el.getBoundingClientRect();
                    results.push({
                        id: el.id,
                        class: el.className.substring(0, 60),
                        panel: el.getAttribute('data-panel'),
                        tag: el.tagName,
                        rect: { top: Math.round(rect.top), left: Math.round(rect.left), w: Math.round(rect.width), h: Math.round(rect.height) }
                    });
                });
                return results;
            })()
        """)
        print(f"  Voice elements found: {len(voice_info)}")
        for v in voice_info[:10]:
            print(f"    id={v['id']}, class={v['class'][:50]}, panel={v['panel']}, rect={v['rect']}")

        print("\n=== TEST: Check Tasks panel (badge 3 visible) ===")
        await page.click('div.nav-item[data-panel="tasks"]' if await page.query_selector('div.nav-item[data-panel="tasks"]') else 'div[data-panel="tasks"]', timeout=3000)
        await page.wait_for_timeout(2000)
        tasks_state = await page.evaluate("""
            (function() {
                var panel = document.getElementById('panel-tasks');
                if (!panel) return { exists: false };
                var badge = document.querySelector('[data-panel="tasks"] .badge, [data-panel="tasks"] [class*="badge"], [data-panel="tasks"] [class*="count"]');
                return {
                    exists: true,
                    active: panel.classList.contains('active'),
                    has_badge: !!badge,
                    badge_text: badge ? badge.textContent.trim() : '',
                    text_length: panel.textContent.trim().length
                };
            })()
        """)
        print(f"  Tasks: active={tasks_state.get('active')}, badge={tasks_state.get('badge_text')}, text_len={tasks_state.get('text_length')}")
        await page.screenshot(path=f"{SS_DIR}/final-05-tasks.png")

        print("\n=== Console errors during this session ===")
        for e in errors[:20]:
            print(f"  {e}")

        await browser.close()

asyncio.run(main())
