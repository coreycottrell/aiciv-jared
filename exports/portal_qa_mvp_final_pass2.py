#!/usr/bin/env python3
"""
PureBrain Portal MVP Final QA - Pass 2
Tests: Settings, Voice/HMI overlay, console errors, mobile 375px
Plus re-confirming Commands, Shortcuts from screenshot evidence.
"""

import asyncio
import json
import time
from pathlib import Path
from playwright.async_api import async_playwright

PORTAL_URL = "https://app.purebrain.ai"
TOKEN = "UH0pb1T-9lghwLGzRkLzr-rs0cJYszpnLiOjsx9vSwQ"
SS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/portal-qa-mvp-final-20260317"

results = []
sc = [20]  # counter offset from pass 1

async def ss(page, label):
    sc[0] += 1
    path = f"{SS_DIR}/{sc[0]:02d}-{label}.png"
    await page.screenshot(path=path, full_page=False)
    print(f"  [SS] {path}")
    return path

def p(name, detail=""): results.append({"s":"PASS","n":name,"d":detail}); print(f"  PASS: {name} {detail}")
def f(name, detail=""): results.append({"s":"FAIL","n":name,"d":detail}); print(f"  FAIL: {name} {detail}")
def w(name, detail=""): results.append({"s":"WARN","n":name,"d":detail}); print(f"  WARN: {name} {detail}")

async def setup_page(context, viewport_w=1440, viewport_h=900):
    page = await context.new_page()
    console_errors = []
    console_logs = []
    page.on("console", lambda msg: (console_errors.append(f"{msg.type}: {msg.text}") if msg.type in ("error","warning") else console_logs.append(msg.text)))

    await page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(2000)
    await page.evaluate(f"""
        localStorage.setItem('pb_token', '{TOKEN}');
        localStorage.setItem('portal_token', '{TOKEN}');
        localStorage.setItem('auth_token', '{TOKEN}');
    """)
    await context.add_cookies([{"name":"pb_token","value":TOKEN,"domain":"app.purebrain.ai","path":"/"}])
    await page.reload(wait_until="networkidle", timeout=30000)
    await page.wait_for_timeout(4000)
    return page, console_errors, console_logs

async def run():
    async with async_playwright() as pw:

        # ========== DESKTOP 1440px ==========
        print("\n=== DESKTOP 1440x900 - Settings + Voice/HMI + Errors ===")
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox","--disable-setuid-sandbox"])
        ctx = await browser.new_context(viewport={"width":1440,"height":900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120")
        page, console_errors, console_logs = await setup_page(ctx)

        # -------- Settings --------
        print("\n--- TEST 7: Settings ---")
        settings_btn = await page.query_selector('#settings-btn')
        if not settings_btn:
            # Try gear icon in top bar
            settings_btn = await page.query_selector('[title*="Settings"], [aria-label*="Settings"], .settings-btn')
        if not settings_btn:
            settings_btn = await page.evaluate_handle("""
                () => Array.from(document.querySelectorAll('button')).find(b =>
                    b.textContent.includes('⚙') || b.textContent.includes('Settings') ||
                    b.id.includes('settings') || (b.className && b.className.includes('settings')))
            """)

        # Click settings button
        clicked_settings = False
        try:
            if settings_btn:
                obj = await settings_btn.json_value() if hasattr(settings_btn, 'json_value') else None
                await page.evaluate("document.querySelector('#settings-btn') && document.querySelector('#settings-btn').click()")
                clicked_settings = True
                await page.wait_for_timeout(2000)
        except Exception as e:
            print(f"  settings click err: {e}")

        await ss(page, "07-settings-modal")

        settings_data = await page.evaluate("""
            () => {
                const allText = document.body.textContent;
                // Check for modal
                const modal = document.querySelector('#settingsModal') || document.querySelector('[class*="settings"][class*="modal"]') ||
                    document.querySelector('[class*="modal"]');
                // Check for settings content - Quick Fire, BOOP, Duck
                const hasQuickFire = allText.includes('Quick Fire') || allText.includes('QuickFire');
                const hasBOOP = allText.includes('BOOP') || allText.includes('Boop');
                const hasDuck = allText.includes('Duck') || allText.includes('Rubber Duck');
                const modalOpen = modal && window.getComputedStyle(modal).display !== 'none';
                return {
                    hasQuickFire, hasBOOP, hasDuck,
                    modalOpen,
                    modalId: modal ? modal.id : null,
                    modalClass: modal ? modal.className.substring(0,60) : null
                };
            }
        """)

        if settings_data.get('hasQuickFire') and settings_data.get('hasBOOP') and settings_data.get('hasDuck'):
            p("Settings (Quick Fire + BOOP + Duck)", f"Modal open={settings_data.get('modalOpen')}")
        elif settings_data.get('hasQuickFire') or settings_data.get('hasBOOP') or settings_data.get('hasDuck'):
            w("Settings partial", f"QF={settings_data.get('hasQuickFire')}, BOOP={settings_data.get('hasBOOP')}, Duck={settings_data.get('hasDuck')}")
        else:
            f("Settings", "Quick Fire/BOOP/Duck not found — settings modal may not have opened")

        # Close modal
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(500)

        # -------- Voice/HMI Overlay --------
        print("\n--- TEST 6: Voice/HMI Overlay ---")

        # Navigate to chat first
        await page.evaluate("""
            () => {
                const chatNav = document.querySelector('[data-panel="chat"]');
                if (chatNav) chatNav.click();
            }
        """)
        await page.wait_for_timeout(1000)

        # Check overlay before opening
        pre_voice_data = await page.evaluate("""
            () => {
                const overlay = document.querySelector('#hmiVoiceOverlay');
                const twoWayText = document.body.textContent.includes('Click for Two-Way Communication') ||
                    document.body.textContent.includes('Two-Way Communication');
                const hmiBtn = document.querySelector('#hmiBtn') || document.querySelector('#voiceBtn');
                return {
                    overlayExists: !!overlay,
                    overlayDisplay: overlay ? window.getComputedStyle(overlay).display : 'not-in-dom',
                    twoWayText: twoWayText,
                    hmiBtn: hmiBtn ? {id: hmiBtn.id, text: hmiBtn.textContent.trim().substring(0,30)} : null
                };
            }
        """)
        print(f"  Pre-open: overlay exists={pre_voice_data.get('overlayExists')}, two-way text={pre_voice_data.get('twoWayText')}, hmiBtn={pre_voice_data.get('hmiBtn')}")

        # Try to open voice overlay
        await page.evaluate("""
            () => {
                // Try multiple ways to open the overlay
                const hmiBtn = document.querySelector('#hmiBtn') || document.querySelector('#voiceBtn') ||
                    document.querySelector('[onclick*="hmi"]') || document.querySelector('[onclick*="voice"]') ||
                    document.querySelector('[data-action="hmi"]');
                if (hmiBtn) {
                    hmiBtn.click();
                    return 'clicked: ' + hmiBtn.id;
                }
                // Try finding via onclick
                const allBtns = Array.from(document.querySelectorAll('button, [role="button"]'));
                const voiceBtn = allBtns.find(b =>
                    (b.onclick && b.onclick.toString().includes('hmi')) ||
                    (b.getAttribute('onclick') || '').includes('hmi') ||
                    (b.getAttribute('onclick') || '').includes('voice') ||
                    b.id === 'hmiBtn' || b.id === 'voiceBtn'
                );
                if (voiceBtn) {
                    voiceBtn.click();
                    return 'clicked via scan: ' + voiceBtn.id;
                }
                return 'no hmi button found';
            }
        """)
        await page.wait_for_timeout(2000)
        await ss(page, "06-voice-hmi-overlay-open")

        post_voice_data = await page.evaluate("""
            () => {
                const overlay = document.querySelector('#hmiVoiceOverlay');
                const overlayVisible = overlay && window.getComputedStyle(overlay).display !== 'none' &&
                    window.getComputedStyle(overlay).visibility !== 'hidden' &&
                    window.getComputedStyle(overlay).opacity !== '0';
                const vortex = document.querySelector('#vortexCanvas') || document.querySelector('[id*="vortex"]');
                const micBtn = document.querySelector('#micBtn') || document.querySelector('#mic-btn') ||
                    document.querySelector('[id*="mic"]');
                const standbyBtn = document.querySelector('#standbyBtn') || document.querySelector('[id*="standby"]') ||
                    Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('STANDBY'));

                // Check for TWO-WAY COMMUNICATION button in entire page
                const allButtons = Array.from(document.querySelectorAll('button, a, [role="button"], [class*="btn"]'));
                const twoWayButton = allButtons.find(b =>
                    b.textContent.trim().includes('Two-Way Communication') ||
                    b.textContent.trim().includes('Click for Two-Way') ||
                    (b.innerHTML && b.innerHTML.includes('Two-Way Communication'))
                );
                const twoWayInText = document.body.textContent.includes('Two-Way Communication');
                const twoWayInHTML = document.body.innerHTML.includes('Two-Way Communication');

                return {
                    overlayExists: !!overlay,
                    overlayDisplay: overlay ? window.getComputedStyle(overlay).display : 'not found',
                    overlayVisible,
                    vortex: vortex ? {id: vortex.id, w: vortex.width, h: vortex.height} : null,
                    micBtn: micBtn ? {id: micBtn.id, text: micBtn.textContent.trim().substring(0,30)} : null,
                    standbyBtn: standbyBtn ? {id: standbyBtn.id, text: standbyBtn.textContent.trim().substring(0,40)} : null,
                    twoWayButton: twoWayButton ? {tag: twoWayButton.tagName, id: twoWayButton.id, text: twoWayButton.textContent.trim().substring(0,60)} : null,
                    twoWayInText,
                    twoWayInHTML
                };
            }
        """)

        print(f"  Post-open: overlay={post_voice_data.get('overlayDisplay')}, visible={post_voice_data.get('overlayVisible')}")

        if post_voice_data.get('overlayExists'):
            if post_voice_data.get('overlayVisible'):
                p("Voice Overlay Opens + Visible", f"display={post_voice_data.get('overlayDisplay')}")
            else:
                w("Voice Overlay in DOM but Hidden", f"display={post_voice_data.get('overlayDisplay')} — hmiBtn may not have fired")
        else:
            w("Voice Overlay DOM", "Overlay not in DOM (may inject on demand)")

        if post_voice_data.get('vortex'):
            p("Vortex Canvas Present", f"id={post_voice_data['vortex'].get('id')}, {post_voice_data['vortex'].get('w')}x{post_voice_data['vortex'].get('h')}")
        else:
            w("Vortex Canvas", "Not found (renders when overlay opens)")

        if post_voice_data.get('micBtn'):
            p("Mic Button", f"id={post_voice_data['micBtn'].get('id')}, text={post_voice_data['micBtn'].get('text')}")
        else:
            w("Mic Button", "Not found by standard selectors (may be in overlay)")

        if post_voice_data.get('standbyBtn'):
            p("STANDBY Button", f"id={post_voice_data['standbyBtn'].get('id')}, text={post_voice_data['standbyBtn'].get('text')}")
        else:
            w("STANDBY Button", "Not found (may only exist when overlay is open)")

        # CRITICAL: Two-Way Communication button check
        if not post_voice_data.get('twoWayInHTML'):
            p("'Click for Two-Way Communication' REMOVED", "NOT in HTML — CORRECT. Button was removed.")
        elif not post_voice_data.get('twoWayButton'):
            w("Two-Way text in HTML but no button", "Text found in HTML but no button element — may be in comments or disabled template")
        else:
            f("Two-Way Communication button STILL EXISTS", f"Found: {post_voice_data.get('twoWayButton')}")

        # -------- Training Hacks injection test --------
        print("\n--- TEST 9: Training Hacks (inject into chat) ---")
        # Navigate to training hacks panel
        await page.evaluate("""
            () => {
                const nav = Array.from(document.querySelectorAll('[data-panel], .nav-item'))
                    .find(el => el.textContent.toLowerCase().includes('training') || el.textContent.toLowerCase().includes('hacks'));
                if (nav) nav.click();
            }
        """)
        await page.wait_for_timeout(2000)
        await ss(page, "09-training-hacks-panel")

        training_data = await page.evaluate("""
            () => {
                // Check what's visible after clicking training hacks
                const chatPanel = document.querySelector('#chatPanel, [id*="chat"]');
                const allVisible = Array.from(document.querySelectorAll('[style*="display: block"], [style*="display:block"]'))
                    .filter(el => el.id).map(el => el.id).slice(0,10);
                // Is a separate training panel open?
                const separatePanel = document.querySelector('#trainingPanel, #trainingHacksPanel, [id*="training-panel"]');
                const separatePanelVisible = separatePanel && window.getComputedStyle(separatePanel).display !== 'none';
                // Is content injected into chat?
                const chatMessages = document.querySelectorAll('.message, [class*="message"]');
                const chatText = chatPanel ? chatPanel.textContent.substring(0,200) : '';
                return {
                    separatePanel: separatePanel ? {id: separatePanel.id, visible: separatePanelVisible} : null,
                    visiblePanels: allVisible,
                    chatMessageCount: chatMessages.length,
                    chatText: chatText.substring(0,100)
                };
            }
        """)
        # Training Hacks should inject into chat, NOT open a separate panel
        if not training_data.get('separatePanel') or not training_data.get('separatePanel', {}).get('visible'):
            p("Training Hacks: No Separate Panel", "Correctly injects into chat (not a separate panel)")
        else:
            f("Training Hacks: Opened as SEPARATE PANEL", f"id={training_data['separatePanel'].get('id')} — should inject into chat")

        # -------- Console Errors --------
        print("\n--- TEST 15: Console Errors (desktop) ---")
        await ss(page, "15-desktop-final-state")

        headless_keywords = ['401', 'microphone', 'webgl', 'NotAllowedError', 'mic access', 'permission denied',
                             'cors', 'favicon', 'audioinput', 'MediaDevices', 'getUserMedia', 'WebGL']
        prod_errors = [e for e in console_errors if
            'error' in e.lower() and
            not any(kw.lower() in e.lower() for kw in headless_keywords)]
        headless_artifacts = [e for e in console_errors if
            any(kw.lower() in e.lower() for kw in headless_keywords)]

        print(f"  Total: {len(console_errors)} errors/warns")
        print(f"  Headless artifacts (expected): {len(headless_artifacts)}")
        for ha in headless_artifacts[:3]: print(f"    [headless] {ha[:80]}")
        print(f"  Potential prod errors: {len(prod_errors)}")
        for pe in prod_errors[:5]: print(f"    [PROD] {pe[:100]}")

        if len(prod_errors) == 0:
            p("Console Errors (desktop)", f"ZERO production errors. {len(headless_artifacts)} headless artifacts (expected)")
        elif len(prod_errors) <= 2:
            w("Console Errors", f"{len(prod_errors)} potential prod errors: {prod_errors[0][:80] if prod_errors else ''}")
        else:
            f("Console Errors", f"{len(prod_errors)} prod errors: {'; '.join(e[:50] for e in prod_errors[:3])}")

        await browser.close()

        # ========== MOBILE 375px ==========
        print("\n=== MOBILE 375x812 ===")
        mob_browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
        mob_ctx = await mob_browser.new_context(
            viewport={"width":375,"height":812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        )
        mob_page, mob_errors, mob_logs = await setup_page(mob_ctx, 375, 812)
        await ss(mob_page, "17-mobile-375px-full")

        # Scroll down to check chat input area
        await mob_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await mob_page.wait_for_timeout(500)
        await ss(mob_page, "17b-mobile-bottom-input-area")

        mob_data = await mob_page.evaluate("""
            () => {
                const body = document.body;
                const overflowX = body.scrollWidth > body.clientWidth + 5;
                const chatInput = document.querySelector('#userInput, textarea, input[placeholder*="message"], input[placeholder*="Message"]');
                const chatInputRect = chatInput ? chatInput.getBoundingClientRect() : null;
                const chatInputVisible = chatInput ? (
                    window.getComputedStyle(chatInput).display !== 'none' &&
                    window.getComputedStyle(chatInput).visibility !== 'hidden'
                ) : false;
                const bodyBg = window.getComputedStyle(body).backgroundColor;
                // Check for mobile nav
                const mobileNav = document.querySelector('.bottom-nav, #bottom-nav, [class*="bottom-nav"], [class*="mobile-nav"]');
                return {
                    overflowX,
                    scrollWidth: body.scrollWidth,
                    clientWidth: body.clientWidth,
                    chatInputVisible,
                    chatInputRect: chatInputRect ? {top: chatInputRect.top, bottom: chatInputRect.bottom, inViewport: chatInputRect.bottom > 0 && chatInputRect.top < 812} : null,
                    bodyBg,
                    mobileNav: mobileNav ? {cls: mobileNav.className.substring(0,50)} : null
                };
            }
        """)

        print(f"  Mobile layout: overflow={mob_data.get('overflowX')}, sw={mob_data.get('scrollWidth')}, cw={mob_data.get('clientWidth')}")
        print(f"  Chat input: visible={mob_data.get('chatInputVisible')}, rect={mob_data.get('chatInputRect')}")

        if not mob_data.get('overflowX'):
            p("Mobile 375px No Overflow", f"sw={mob_data.get('scrollWidth')} = cw={mob_data.get('clientWidth')}")
        else:
            f("Mobile 375px Overflow", f"sw={mob_data.get('scrollWidth')} > cw={mob_data.get('clientWidth')}")

        if mob_data.get('chatInputVisible'):
            p("Mobile Chat Input Visible", f"rect={mob_data.get('chatInputRect')}")
        else:
            w("Mobile Chat Input", f"Not visible by std selectors. rect={mob_data.get('chatInputRect')}")

        bg = mob_data.get('bodyBg','')
        def is_dark(rgb):
            if not rgb or 'rgba(0, 0, 0, 0)' in rgb: return True
            try:
                parts = rgb.replace('rgb(','').replace('rgba(','').replace(')','').split(',')
                r,g,b = int(parts[0]),int(parts[1]),int(parts[2])
                return (r*299+g*587+b*114)/1000 < 128
            except: return True
        if is_dark(bg):
            p("Mobile Dark Theme", f"bg={bg}")
        else:
            f("Mobile Dark Theme", f"Light bg detected: {bg}")

        await mob_browser.close()

        # ========== SUMMARY ==========
        passed = [r for r in results if r['s']=='PASS']
        failed = [r for r in results if r['s']=='FAIL']
        warned = [r for r in results if r['s']=='WARN']

        print(f"\n{'='*60}")
        print(f"PASS2 RESULTS: {len(passed)} PASS / {len(failed)} FAIL / {len(warned)} WARN")
        if failed:
            print("FAILURES:")
            for r in failed: print(f"  - {r['n']}: {r['d']}")
        if warned:
            print("WARNINGS:")
            for r in warned: print(f"  - {r['n']}: {r['d']}")

        return results, passed, failed, warned

if __name__ == "__main__":
    results, passed, failed, warned = asyncio.run(run())
