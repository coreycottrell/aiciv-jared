#!/usr/bin/env python3
"""
Investigate: 404 errors, Two-Way button text, Voice overlay, Settings, mobile chat input
"""

import asyncio
import json
from playwright.async_api import async_playwright

PORTAL_URL = "https://app.purebrain.ai"
TOKEN = "UH0pb1T-9lghwLGzRkLzr-rs0cJYszpnLiOjsx9vSwQ"
SS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/portal-qa-mvp-final-20260317"

async def run():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = await browser.new_context(
            viewport={"width":1440,"height":900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120"
        )
        page = await ctx.new_page()

        # Track ALL network requests
        requests_404 = []
        all_requests = []
        page.on("response", lambda r: requests_404.append(f"{r.status} {r.url}") if r.status == 404 else None)
        page.on("response", lambda r: all_requests.append(f"{r.status} {r.url}"))

        console_errors = []
        page.on("console", lambda msg: console_errors.append(f"{msg.type}: {msg.text}") if msg.type in ("error","warning") else None)

        await page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)
        await page.evaluate(f"""
            localStorage.setItem('pb_token', '{TOKEN}');
            localStorage.setItem('portal_token', '{TOKEN}');
        """)
        await ctx.add_cookies([{"name":"pb_token","value":TOKEN,"domain":"app.purebrain.ai","path":"/"}])
        await page.reload(wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(5000)

        print("=== 404 REQUESTS ===")
        for r in requests_404:
            print(f"  404: {r}")

        print("\n=== ALL CONSOLE ERRORS ===")
        for e in console_errors:
            print(f"  {e[:150]}")

        # Investigate Two-Way Communication text
        print("\n=== TWO-WAY COMMUNICATION INVESTIGATION ===")
        twoway_data = await page.evaluate("""
            () => {
                // Find ALL elements containing "Two-Way"
                const treeWalker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );
                const textNodes = [];
                let node;
                while ((node = treeWalker.nextNode())) {
                    if (node.textContent.includes('Two-Way') || node.textContent.includes('two-way')) {
                        textNodes.push({
                            text: node.textContent.trim().substring(0,100),
                            parentTag: node.parentElement ? node.parentElement.tagName : 'unknown',
                            parentId: node.parentElement ? node.parentElement.id : '',
                            parentClass: node.parentElement ? node.parentElement.className.substring(0,50) : '',
                            parentDisplay: node.parentElement ? window.getComputedStyle(node.parentElement).display : 'unknown',
                            parentVisible: node.parentElement ? (window.getComputedStyle(node.parentElement).display !== 'none') : false
                        });
                    }
                }
                // Also check in HTML comments
                const html = document.body.innerHTML;
                const commentIdx = html.indexOf('Two-Way');
                const commentContext = commentIdx >= 0 ? html.substring(Math.max(0,commentIdx-50), commentIdx+100) : 'not found';

                return {textNodes, commentContext};
            }
        """)
        print(f"  Text nodes with Two-Way: {len(twoway_data.get('textNodes',[]))}")
        for tn in twoway_data.get('textNodes', []):
            print(f"    - tag={tn.get('parentTag')}, id={tn.get('parentId')}, class={tn.get('parentClass')[:30]}, display={tn.get('parentDisplay')}, visible={tn.get('parentVisible')}")
            print(f"      text: {tn.get('text')[:80]}")
        print(f"  Comment context: {twoway_data.get('commentContext','')[:150]}")

        # Investigate Settings
        print("\n=== SETTINGS INVESTIGATION ===")
        settings_data = await page.evaluate("""
            () => {
                // Find settings button
                const allBtns = Array.from(document.querySelectorAll('button, [role="button"]'));
                const settingsBtns = allBtns.filter(b =>
                    b.id.includes('settings') ||
                    (b.className && b.className.includes('settings')) ||
                    b.title?.includes('ettings') ||
                    b.getAttribute('aria-label')?.includes('ettings')
                );
                // Get settings modal
                const modal = document.querySelector('#settingsModal');
                return {
                    settingsBtns: settingsBtns.map(b => ({id: b.id, cls: b.className.substring(0,40), title: b.title, text: b.textContent.trim().substring(0,20)})),
                    modal: modal ? {id: modal.id, display: window.getComputedStyle(modal).display, cls: modal.className.substring(0,60)} : null
                };
            }
        """)
        print(f"  Settings buttons: {settings_data.get('settingsBtns')}")
        print(f"  Settings modal: {settings_data.get('modal')}")

        # Click settings
        if settings_data.get('settingsBtns'):
            btn_id = settings_data['settingsBtns'][0]['id']
            await page.evaluate(f"document.getElementById('{btn_id}').click()")
            await page.wait_for_timeout(2000)
            after_settings = await page.evaluate("""
                () => {
                    const modal = document.querySelector('#settingsModal');
                    const allText = document.body.textContent;
                    return {
                        modalDisplay: modal ? window.getComputedStyle(modal).display : 'not found',
                        hasQuickFire: allText.includes('Quick Fire'),
                        hasBOOP: allText.includes('BOOP'),
                        hasDuck: allText.includes('Duck')
                    };
                }
            """)
            print(f"  After click: {after_settings}")
            await page.screenshot(path=f"{SS_DIR}/28-settings-after-click.png")

        await page.keyboard.press("Escape")
        await page.wait_for_timeout(500)

        # Investigate Voice HMI Overlay
        print("\n=== VOICE/HMI OVERLAY INVESTIGATION ===")
        hmi_data = await page.evaluate("""
            () => {
                const overlay = document.querySelector('#hmiVoiceOverlay');
                const allBtns = Array.from(document.querySelectorAll('button, [role="button"], [id*="hmi"], [id*="voice"]'));
                const hmiBtns = allBtns.filter(b =>
                    b.id.includes('hmi') || b.id.includes('voice') || b.id.includes('mic') ||
                    (b.className && (b.className.includes('hmi') || b.className.includes('voice')))
                );
                // Look in the input area for HMI trigger
                const inputArea = document.querySelector('.chat-input-area, #chat-input-area, [class*="input-area"], [class*="input-row"]');
                const inputAreaBtns = inputArea ? Array.from(inputArea.querySelectorAll('button, [role="button"]')) : [];
                return {
                    overlayDisplay: overlay ? window.getComputedStyle(overlay).display : 'not found',
                    hmiBtns: hmiBtns.map(b => ({id: b.id, cls: b.className.substring(0,40), title: b.title, text: b.textContent.trim().substring(0,20)})),
                    inputAreaBtns: inputAreaBtns.map(b => ({id: b.id, cls: b.className.substring(0,40), text: b.textContent.trim().substring(0,20)})),
                    overlayContent: overlay ? overlay.innerHTML.substring(0,500) : 'not found'
                };
            }
        """)
        print(f"  Overlay display: {hmi_data.get('overlayDisplay')}")
        print(f"  HMI-related buttons: {hmi_data.get('hmiBtns')}")
        print(f"  Input area buttons: {hmi_data.get('inputAreaBtns')}")
        print(f"  Overlay HTML preview: {hmi_data.get('overlayContent','')[:300]}")

        # Try to open the overlay via correct button
        if hmi_data.get('hmiBtns'):
            for btn_info in hmi_data['hmiBtns']:
                if btn_info.get('id') and btn_info['id'] != 'mic-btn':
                    print(f"  Trying to click: {btn_info['id']}")
                    await page.evaluate(f"document.getElementById('{btn_info['id']}') && document.getElementById('{btn_info['id']}').click()")
                    await page.wait_for_timeout(2000)
                    break
        else:
            # Try clicking the mic button as it might toggle overlay
            await page.evaluate("document.querySelector('#mic-btn') && document.querySelector('#mic-btn').click()")
            await page.wait_for_timeout(2000)

        after_hmi = await page.evaluate("""
            () => {
                const overlay = document.querySelector('#hmiVoiceOverlay');
                const vortex = document.querySelector('#vortexCanvas') || document.querySelector('[id*="vortex"]');
                const standby = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('STANDBY'));
                return {
                    overlayDisplay: overlay ? window.getComputedStyle(overlay).display : 'not found',
                    overlayOpacity: overlay ? window.getComputedStyle(overlay).opacity : null,
                    vortex: vortex ? {id: vortex.id, w: vortex.width, h: vortex.height} : null,
                    standby: standby ? {text: standby.textContent.trim().substring(0,40), id: standby.id} : null
                };
            }
        """)
        print(f"  After HMI click: {after_hmi}")
        await page.screenshot(path=f"{SS_DIR}/29-hmi-overlay-after-click.png")

        # Mobile chat input investigation
        print("\n=== MOBILE CHAT INPUT INVESTIGATION ===")
        mob_browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
        mob_ctx = await mob_browser.new_context(viewport={"width":375,"height":812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)")
        mob_page = await mob_ctx.new_page()
        await mob_page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=30000)
        await mob_page.wait_for_timeout(2000)
        await mob_page.evaluate(f"localStorage.setItem('pb_token', '{TOKEN}')")
        await mob_ctx.add_cookies([{"name":"pb_token","value":TOKEN,"domain":"app.purebrain.ai","path":"/"}])
        await mob_page.reload(wait_until="networkidle", timeout=30000)
        await mob_page.wait_for_timeout(4000)

        mob_input_data = await mob_page.evaluate("""
            () => {
                const inputs = Array.from(document.querySelectorAll('input, textarea'));
                return inputs.map(el => ({
                    tag: el.tagName, id: el.id, cls: el.className.substring(0,40),
                    placeholder: el.placeholder ? el.placeholder.substring(0,30) : '',
                    display: window.getComputedStyle(el).display,
                    visibility: window.getComputedStyle(el).visibility,
                    rect: {top: el.getBoundingClientRect().top, bottom: el.getBoundingClientRect().bottom}
                }));
            }
        """)
        print("  Mobile inputs found:")
        for inp in mob_input_data:
            print(f"    {inp.get('tag')} id={inp.get('id')} display={inp.get('display')} placeholder={inp.get('placeholder')} rect={inp.get('rect')}")

        await mob_page.screenshot(path=f"{SS_DIR}/30-mobile-375px-chat-closeup.png")
        await mob_browser.close()

        await browser.close()

asyncio.run(run())
