"""
PureBrain Portal - Fast QA Audit
Date: 2026-03-16
Uses domcontentloaded instead of networkidle for speed
"""

import asyncio
import json
import os
import sys

from playwright.async_api import async_playwright

PORTAL_URL = "https://app.purebrain.ai"
TOKEN = "UH0pb1T-9lghwLGzRkLzr-rs0cJYszpnLiOjsx9vSwQ"
SS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/portal-qa-20260316"

results = {}
console_errors = []

def log(msg):
    print(msg, flush=True)

def record(panel, status, notes=""):
    results[panel] = {"status": status, "notes": notes}
    icon = "OK" if status == "PASS" else "!!" if status == "FAIL" else "--"
    log(f"  [{icon}] {panel}: {status} - {notes}")


async def run():
    os.makedirs(SS_DIR, exist_ok=True)
    log(f"Starting QA audit of {PORTAL_URL}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        page.on("console", lambda msg: console_errors.append(f"[{msg.type.upper()}] {msg.text}"))
        page.on("pageerror", lambda err: console_errors.append(f"[PAGE ERROR] {err}"))

        # =============================================
        # LOGIN
        # =============================================
        log("\n=== LOGIN ===")
        try:
            await page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=20000)
        except:
            pass
        await page.wait_for_timeout(3000)

        await page.screenshot(path=f"{SS_DIR}/001-initial-load.png")
        log("Screenshot: 001-initial-load.png")

        body_text = await page.evaluate("() => document.body.innerText.substring(0, 300)")
        log(f"Initial page: {body_text[:150]}")

        # Dismiss cookie/consent dialogs (check for visible dismissible dialogs)
        for dismiss_sel in [
            "button:has-text('Got it')",
            "button:has-text('Accept all')",
            "button:has-text('I accept')",
        ]:
            try:
                el = page.locator(dismiss_sel).first
                if await el.count() > 0 and await el.is_visible():
                    await el.click()
                    await page.wait_for_timeout(800)
                    log(f"Dismissed: {dismiss_sel}")
            except:
                pass

        # Check if already logged in
        logged_in_check = await page.query_selector("#chat-messages, .portal-container, .pb-portal")
        if logged_in_check:
            log("Already logged in!")
            record("Login", "PASS", "Portal already accessible")
        else:
            # Find password input
            pwd = None
            for sel in ["input[type='password']", "input[placeholder*='Bearer']", "input[placeholder*='Token']"]:
                el = await page.query_selector(sel)
                if el:
                    try:
                        if await el.is_visible():
                            pwd = el
                            log(f"Found input: {sel}")
                            break
                    except:
                        pass

            if not pwd:
                # Get all inputs
                inputs = await page.query_selector_all("input")
                for inp in inputs:
                    try:
                        if await inp.is_visible():
                            pwd = inp
                            ph = await inp.get_attribute("placeholder") or ""
                            log(f"Using first visible input, placeholder: {ph}")
                            break
                    except:
                        pass

            if pwd:
                await pwd.fill(TOKEN)
                await page.wait_for_timeout(300)
                log("Token entered")

            # Click login button (careful to avoid hidden/consent buttons)
            all_btns = await page.query_selector_all("button")
            for btn in all_btns:
                try:
                    if await btn.is_visible() and await btn.is_enabled():
                        txt = (await btn.inner_text()).strip().lower()
                        log(f"Visible button: '{txt}'")
                        if any(w in txt for w in ['sign in', 'login', 'enter', 'access', 'continue', 'submit']):
                            await btn.click()
                            log(f"Clicked button: '{txt}'")
                            break
                except:
                    pass
            else:
                # Try Enter key
                if pwd:
                    await page.keyboard.press("Enter")
                    log("Pressed Enter to submit")

            log("Waiting 8s for portal to load...")
            await page.wait_for_timeout(8000)
            await page.screenshot(path=f"{SS_DIR}/002-post-login.png")
            log(f"Post-login URL: {page.url}")
            log("Screenshot: 002-post-login.png")

            portal = await page.query_selector("#chat-messages, .portal-container, .sidebar, .pb-portal, .chat-panel")
            if portal:
                record("Login", "PASS", "Portal accessible after login")
            else:
                body2 = await page.evaluate("() => document.body.innerText.substring(0, 200)")
                log(f"Post-login body: {body2[:150]}")
                record("Login", "WARN", f"Portal uncertain. Body: {body2[:80]}")

        # =============================================
        # INSPECT PORTAL STRUCTURE
        # =============================================
        log("\n=== PORTAL STRUCTURE ANALYSIS ===")
        await page.screenshot(path=f"{SS_DIR}/003-portal-full.png")

        structure = await page.evaluate("""
            () => {
                // Full DOM analysis
                const everything = {};

                // Find sidebar/nav
                const navEls = document.querySelectorAll('.sidebar, #sidebar, nav, [class*="sidebar"], [class*="nav-panel"]');
                everything.navCount = navEls.length;
                everything.navClasses = Array.from(navEls).map(e => e.className.substring(0,50)).slice(0,5);

                // Find all clickable nav items
                const items = [];
                document.querySelectorAll('a, button, li, [role="button"], [data-panel]').forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        const txt = (el.innerText || el.title || el.getAttribute('aria-label') || el.getAttribute('data-panel') || '').trim();
                        const cls = el.className.substring(0,50);
                        const id = el.id;
                        if (txt && txt.length < 40) {
                            items.push({text: txt.substring(0,25), class: cls, id: id,
                                       x: Math.round(rect.x), y: Math.round(rect.y)});
                        }
                    }
                });

                everything.clickableItems = items.slice(0, 40);

                // Check for loading states anywhere
                const loadingTexts = [];
                document.querySelectorAll('*').forEach(el => {
                    if (el.children.length === 0) {
                        const t = (el.innerText || '').trim();
                        if (t.startsWith('Loading') && t.length < 60) {
                            loadingTexts.push(t);
                        }
                    }
                });
                everything.loadingTexts = [...new Set(loadingTexts)];

                // Check for chat messages
                const chatMsgs = document.querySelectorAll('.msg, .message, [class*="chat-message"]');
                everything.chatMessageCount = chatMsgs.length;

                // Check for canvas (neural network)
                const canvases = document.querySelectorAll('canvas');
                everything.canvases = Array.from(canvases).map(c => {
                    const s = window.getComputedStyle(c);
                    const r = c.getBoundingClientRect();
                    return {id: c.id, class: c.className.substring(0,40), opacity: s.opacity,
                            w: Math.round(r.width), h: Math.round(r.height)};
                });

                return everything;
            }
        """)

        log(f"Nav count: {structure['navCount']}, Nav classes: {structure['navClasses']}")
        log(f"Chat messages: {structure['chatMessageCount']}")
        log(f"Canvases: {structure['canvases']}")
        log(f"Loading texts: {structure['loadingTexts']}")
        log(f"Clickable items ({len(structure['clickableItems'])}):")
        for item in structure['clickableItems']:
            log(f"  '{item['text']}' cls='{item['class'][:40]}' id='{item['id']}' at ({item['x']},{item['y']})")

        # =============================================
        # CHECK ALL PANELS BY CLICKING NAV ITEMS
        # =============================================
        log("\n=== PANEL NAVIGATION TESTS ===")

        # Build a map of what nav items are available
        nav_items = {item['text'].lower(): item for item in structure['clickableItems']}

        # Define panels to test and what to look for
        panels_config = {
            "Chat": {
                "search_texts": ["chat", "messages"],
                "success_indicator": "#chat-messages, .chat-messages, .msg",
                "fail_keywords": ["loading"],
                "known_fix": False,
            },
            "Terminal": {
                "search_texts": ["terminal"],
                "success_indicator": ".terminal, .xterm, #terminal",
                "fail_keywords": ["loading terminal", "connecting..."],
                "known_fix": False,
            },
            "Teams": {
                "search_texts": ["teams", "team"],
                "success_indicator": None,
                "fail_keywords": ["loading teams"],
                "known_fix": False,
            },
            "Status": {
                "search_texts": ["status"],
                "success_indicator": None,
                "fail_keywords": ["loading status"],
                "known_fix": False,
            },
            "Files": {
                "search_texts": ["files", "file"],
                "success_indicator": None,
                "fail_keywords": ["loading files"],
                "known_fix": False,
            },
            "Refer & Earn": {
                "search_texts": ["refer", "earn"],
                "success_indicator": None,
                "fail_keywords": ["loading"],
                "known_fix": False,
            },
            "Bookmarks": {
                "search_texts": ["bookmarks", "bookmark"],
                "success_indicator": None,
                "fail_keywords": ["loading bookmarks"],
                "known_fix": False,
            },
            "Tasks": {
                "search_texts": ["tasks", "task"],
                "success_indicator": None,
                "fail_keywords": ["loading tasks"],
                "known_fix": False,
            },
            "Agent Roster": {
                "search_texts": ["agent roster", "roster", "agents"],
                "success_indicator": None,
                "fail_keywords": ["loading agents"],
                "known_fix": False,
            },
            "Commands": {
                "search_texts": ["commands", "command"],
                "success_indicator": None,
                "fail_keywords": ["loading command reference"],
                "known_fix": True,  # This was the broken one
            },
            "Shortcuts": {
                "search_texts": ["shortcuts", "shortcut"],
                "success_indicator": None,
                "fail_keywords": ["loading shortcuts"],
                "known_fix": True,  # This was the broken one
            },
            "Brainiac Training": {
                "search_texts": ["brainiac", "training"],
                "success_indicator": None,
                "fail_keywords": ["loading training"],
                "known_fix": False,
            },
        }

        ss_num = 4
        for panel_name, config in panels_config.items():
            log(f"\n--- {panel_name} ---")
            clicked = False

            # Try to find and click
            for search_txt in config["search_texts"]:
                # Check our discovered nav items
                for item_text, item_data in nav_items.items():
                    if search_txt in item_text:
                        # Try to click at those coordinates
                        try:
                            await page.mouse.click(item_data['x'] + 5, item_data['y'] + 5)
                            await page.wait_for_timeout(2000)
                            clicked = True
                            log(f"  Clicked '{item_text}' at ({item_data['x']},{item_data['y']})")
                            break
                        except Exception as e:
                            log(f"  Click failed: {e}")

                if clicked:
                    break

                # Fallback: try Playwright selectors
                if not clicked:
                    for sel in [
                        f"text={panel_name}",
                        f"[title='{panel_name}']",
                        f"[title*='{search_txt}']",
                        f"[data-panel='{search_txt}']",
                        f".nav-{search_txt}",
                        f"#nav-{search_txt}",
                    ]:
                        try:
                            el = await page.query_selector(sel)
                            if el and await el.is_visible():
                                await el.click()
                                await page.wait_for_timeout(2000)
                                clicked = True
                                log(f"  Clicked via selector: {sel}")
                                break
                        except:
                            pass
                    if clicked:
                        break

            # Take screenshot
            ss_path = f"{SS_DIR}/{ss_num:03d}-{panel_name.lower().replace(' ', '-').replace('&', 'and')}.png"
            await page.screenshot(path=ss_path)
            log(f"  Screenshot: {os.path.basename(ss_path)}")
            ss_num += 1

            # Check result
            panel_state = await page.evaluate("""
                (config) => {
                    const failKws = config.fail_keywords || [];
                    const stuckLoading = [];
                    document.querySelectorAll('*').forEach(el => {
                        if (el.children.length === 0) {
                            const t = (el.innerText || '').trim().toLowerCase();
                            for (const kw of failKws) {
                                if (t.includes(kw.toLowerCase())) {
                                    stuckLoading.push(t.substring(0, 80));
                                }
                            }
                        }
                    });

                    // Get main visible content
                    const mainSelectors = ['.panel-content', '#panel-content', '.right-panel', '.main-panel',
                                          '.panel-body', '.content-area', '[class*="panel-view"]'];
                    let mainText = '';
                    for (const sel of mainSelectors) {
                        const el = document.querySelector(sel);
                        if (el && el.offsetParent !== null) {
                            mainText = el.innerText.substring(0, 300);
                            break;
                        }
                    }
                    if (!mainText) {
                        // Get approximate center of page content
                        const centerEl = document.elementFromPoint(900, 450);
                        if (centerEl) mainText = centerEl.innerText ? centerEl.innerText.substring(0, 200) : '';
                    }

                    return {stuckLoading: [...new Set(stuckLoading)], mainText: mainText.substring(0, 200)};
                }
            """, config)

            log(f"  Stuck loading: {panel_state['stuckLoading']}")
            log(f"  Main content: {panel_state['mainText'][:120]}")

            if panel_state['stuckLoading']:
                if config.get('known_fix'):
                    record(panel_name, "FAIL", f"KNOWN FIX NOT WORKING: Still stuck '{panel_state['stuckLoading'][0]}'")
                else:
                    record(panel_name, "FAIL", f"Stuck in loading state: {panel_state['stuckLoading'][0]}")
            elif not clicked:
                record(panel_name, "WARN", f"Nav item not found for '{panel_name}'")
            else:
                content_preview = panel_state['mainText'].strip()
                if content_preview:
                    record(panel_name, "PASS", f"Loaded content: {content_preview[:80]}")
                else:
                    record(panel_name, "PASS", f"Panel clicked and no stuck loading detected")

        # =============================================
        # AI TRAINING HACKS — verify injects to chat
        # =============================================
        log("\n--- AI Training Hacks ---")
        clicked_hacks = False
        for search_txt in ["training hacks", "hacks", "ai training"]:
            for item_text, item_data in nav_items.items():
                if search_txt in item_text:
                    try:
                        await page.mouse.click(item_data['x'] + 5, item_data['y'] + 5)
                        await page.wait_for_timeout(2000)
                        clicked_hacks = True
                        log(f"  Clicked '{item_text}'")
                        break
                    except:
                        pass
            if clicked_hacks:
                break

        if not clicked_hacks:
            for sel in ["text=AI Training Hacks", "text=Training Hacks", "text=Hacks", "[title*='Hacks']"]:
                try:
                    el = await page.query_selector(sel)
                    if el and await el.is_visible():
                        await el.click()
                        await page.wait_for_timeout(2000)
                        clicked_hacks = True
                        break
                except:
                    pass

        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-training-hacks.png")
        ss_num += 1

        if clicked_hacks:
            chat_still = await page.query_selector("#chat-messages, .chat-messages")
            record("AI Training Hacks", "PASS" if chat_still else "WARN",
                   "Training Hacks injects to chat (not separate panel)" if chat_still else "Chat not visible after click")
        else:
            record("AI Training Hacks", "WARN", "AI Training Hacks nav item not found")

        # =============================================
        # NEURAL NETWORK BACKGROUND
        # =============================================
        log("\n--- Neural Network Background ---")
        # Navigate back to chat
        for sel in ["text=Chat", "[title='Chat']", ".nav-chat"]:
            try:
                el = await page.query_selector(sel)
                if el and await el.is_visible():
                    await el.click()
                    await page.wait_for_timeout(1000)
                    break
            except:
                pass

        canvas_info = await page.evaluate("""
            () => {
                const canvases = document.querySelectorAll('canvas');
                return Array.from(canvases).map(c => {
                    const s = window.getComputedStyle(c);
                    const r = c.getBoundingClientRect();
                    // Also check parent opacity
                    let parent = c.parentElement;
                    let parentOpacity = 1;
                    while (parent && parent !== document.body) {
                        const ps = window.getComputedStyle(parent);
                        parentOpacity = Math.min(parentOpacity, parseFloat(ps.opacity));
                        parent = parent.parentElement;
                    }
                    return {
                        id: c.id || '(no id)',
                        class: c.className.substring(0,50),
                        opacity: parseFloat(s.opacity),
                        parentOpacity: parentOpacity,
                        effectiveOpacity: parseFloat(s.opacity) * parentOpacity,
                        display: s.display,
                        w: Math.round(r.width),
                        h: Math.round(r.height),
                        visible: r.width > 0 && r.height > 0 && s.display !== 'none'
                    };
                });
            }
        """)

        log(f"  Canvases: {json.dumps(canvas_info, indent=2)[:400]}")

        visible_canvas = [c for c in canvas_info if c.get('visible')]
        if visible_canvas:
            c = visible_canvas[0]
            eff_opacity = c.get('effectiveOpacity', c.get('opacity', 1))
            if eff_opacity < 0.3:
                record("Neural Network BG", "FAIL",
                       f"Canvas opacity={c['opacity']}, parentOpacity={c['parentOpacity']}, effective={eff_opacity:.2f} — DIMMED BUG")
            elif eff_opacity < 0.6:
                record("Neural Network BG", "WARN",
                       f"Canvas somewhat dim: effective opacity={eff_opacity:.2f}")
            else:
                record("Neural Network BG", "PASS",
                       f"Canvas id='{c['id']}' opacity={c['opacity']}, effective={eff_opacity:.2f}, size={c['w']}x{c['h']}")
        else:
            record("Neural Network BG", "WARN", "No visible canvas found (neural network may use different rendering)")

        # =============================================
        # QUICK FIRE BUTTONS
        # =============================================
        log("\n--- Quick Fire Buttons ---")
        all_visible_btns = await page.evaluate("""
            () => {
                const btns = [];
                document.querySelectorAll('button, [role="button"]').forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        const s = window.getComputedStyle(el);
                        if (s.display !== 'none' && s.visibility !== 'hidden') {
                            const txt = (el.innerText || el.title || el.getAttribute('aria-label') || '').trim();
                            btns.push({
                                text: txt.substring(0,25),
                                title: (el.title || '').substring(0,25),
                                class: el.className.substring(0,50),
                                x: Math.round(rect.x), y: Math.round(rect.y),
                                w: Math.round(rect.width), h: Math.round(rect.height)
                            });
                        }
                    }
                });
                return btns;
            }
        """)

        log(f"  All visible buttons ({len(all_visible_btns)}):")
        btn_texts = set()
        for b in all_visible_btns:
            combined = f"{b['text']} {b['title']}".upper()
            btn_texts.add(combined.strip())
            log(f"    '{b['text']}' title='{b['title']}' at ({b['x']},{b['y']}) {b['w']}x{b['h']}")

        for qb in ["BOOP", "Grounding", "Status", "Compact", "Intel", "Duck"]:
            found = any(qb.upper() in t for t in btn_texts)
            record(f"Quick Button: {qb}", "PASS" if found else "WARN",
                   "Found" if found else f"'{qb}' not in visible buttons")

        await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-quick-buttons-view.png")
        ss_num += 1

        # =============================================
        # TOP BAR
        # =============================================
        log("\n--- Top Bar Elements ---")
        topbar = await page.evaluate("""
            () => {
                const results = {};
                const allBtns = document.querySelectorAll('button, [role="button"], a');
                let resume = false, restart = false, logout = false, share = false, settings = false;
                for (const b of allBtns) {
                    const t = (b.innerText || b.title || b.getAttribute('aria-label') || '').toLowerCase();
                    const c = (b.className || '').toLowerCase();
                    if (b.getBoundingClientRect().width === 0) continue;
                    if (t.includes('resume') || c.includes('resume')) resume = true;
                    if (t.includes('restart') || c.includes('restart')) restart = true;
                    if (t.includes('logout') || t.includes('log out') || t.includes('sign out')) logout = true;
                    if (t.includes('share') || c.includes('share')) share = true;
                    if (t.includes('settings') || c.includes('settings') || t.includes('gear')) settings = true;
                }
                results.buttons = {resume, restart, logout, share, settings};

                // CTX meter
                const ctxEl = document.querySelector('[class*="ctx"], [id*="ctx"], .context-meter, .token-meter');
                results.ctxMeter = ctxEl ? {found: true, text: ctxEl.innerText.substring(0,50)} : {found: false};

                // Online indicator
                const onlineEl = document.querySelector('.online, .online-dot, [class*="online-indicator"], .status-online, .connected');
                results.onlineIndicator = !!onlineEl;

                return results;
            }
        """)
        log(f"  Top bar: {json.dumps(topbar, indent=2)}")

        btns = topbar.get('buttons', {})
        record("Top Bar: CTX Meter", "PASS" if topbar.get('ctxMeter', {}).get('found') else "WARN",
               f"CTX: {topbar.get('ctxMeter', {}).get('text', 'not found')}")
        record("Top Bar: Resume Button", "PASS" if btns.get('resume') else "WARN", "Found" if btns.get('resume') else "Not found")
        record("Top Bar: Restart Button", "PASS" if btns.get('restart') else "WARN", "Found" if btns.get('restart') else "Not found")
        record("Top Bar: Online Indicator", "PASS" if topbar.get('onlineIndicator') else "WARN", "Found" if topbar.get('onlineIndicator') else "Not found")
        record("Top Bar: Share Button", "PASS" if btns.get('share') else "WARN", "Found" if btns.get('share') else "Not found")
        record("Top Bar: Logout Button", "PASS" if btns.get('logout') else "WARN", "Found" if btns.get('logout') else "Not found")
        record("Top Bar: Settings Gear", "PASS" if btns.get('settings') else "WARN", "Found" if btns.get('settings') else "Not found")

        # Try to open settings
        if btns.get('settings'):
            try:
                settings_el = await page.query_selector('[title*="Settings"], [aria-label*="Settings"], .settings-btn, [class*="settings-trigger"], button[class*="gear"]')
                if not settings_el:
                    # Search through all buttons for settings
                    all_btns_el = await page.query_selector_all("button, [role='button']")
                    for btn in all_btns_el:
                        txt = (await btn.get_attribute("title") or await btn.get_attribute("aria-label") or "").lower()
                        if "settings" in txt or "gear" in txt:
                            settings_el = btn
                            break

                if settings_el and await settings_el.is_visible():
                    await settings_el.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-settings-open.png")
                    ss_num += 1

                    settings_content = await page.evaluate("""
                        () => {
                            const modal = document.querySelector('.modal, .settings-panel, .settings-modal, .dialog, [class*="settings"]');
                            return modal ? {found: true, text: modal.innerText.substring(0, 200)} : {found: false};
                        }
                    """)
                    if settings_content.get('found'):
                        record("Settings Panel Opens", "PASS", f"Content: {settings_content['text'][:100]}")
                    else:
                        record("Settings Panel Opens", "WARN", "Settings button clicked but no modal detected")

                    await page.keyboard.press("Escape")
                    await page.wait_for_timeout(500)
            except Exception as e:
                record("Settings Panel Opens", "WARN", f"Could not click settings: {str(e)[:80]}")

        # =============================================
        # VOICE OVERLAY
        # =============================================
        log("\n--- Voice Overlay ---")
        voice_btn = await page.evaluate("""
            () => {
                const btns = document.querySelectorAll('button, [role="button"]');
                for (const b of btns) {
                    const t = (b.innerText || b.title || b.getAttribute('aria-label') || '').toLowerCase();
                    const c = (b.className || '').toLowerCase();
                    if (t.includes('voice') || t.includes('mic') || c.includes('voice') || c.includes('mic')) {
                        const rect = b.getBoundingClientRect();
                        if (rect.width > 0) return {found: true, class: c.substring(0,50), x: Math.round(rect.x), y: Math.round(rect.y)};
                    }
                }
                return {found: false};
            }
        """)
        log(f"  Voice button: {voice_btn}")

        if voice_btn.get('found'):
            try:
                await page.mouse.click(voice_btn['x'] + 5, voice_btn['y'] + 5)
                await page.wait_for_timeout(2000)
                await page.screenshot(path=f"{SS_DIR}/{ss_num:03d}-voice-overlay.png")
                ss_num += 1

                voice_state = await page.evaluate("""
                    () => {
                        // Check for any overlay/modal that appeared
                        const overlays = document.querySelectorAll('[class*="voice"], [class*="overlay"], .modal');
                        const visible = [];
                        for (const el of overlays) {
                            const rect = el.getBoundingClientRect();
                            if (rect.width > 100 && rect.height > 100) {
                                visible.push({cls: el.className.substring(0,60), text: el.innerText.substring(0,100)});
                            }
                        }
                        const triggerField = document.querySelector('input[placeholder*="trigger"], input[name*="trigger"], [class*="trigger"]');
                        return {overlaysVisible: visible.length > 0, overlays: visible.slice(0,3), triggerField: !!triggerField};
                    }
                """)
                record("Voice Overlay Opens", "PASS" if voice_state['overlaysVisible'] else "WARN",
                       f"Overlay visible: {voice_state['overlays'][:1]}" if voice_state['overlaysVisible'] else "No overlay detected after mic click")
                record("Voice Overlay: Trigger Field", "PASS" if voice_state['triggerField'] else "WARN",
                       "Trigger word field found" if voice_state['triggerField'] else "Trigger field not found")
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(500)
            except Exception as e:
                record("Voice Overlay", "WARN", f"Error: {str(e)[:80]}")
        else:
            record("Voice Overlay", "WARN", "No voice/mic button found")

        # =============================================
        # FULL DOM LOADING STATE SCAN
        # =============================================
        log("\n--- Full DOM Loading State Scan ---")
        final_loading = await page.evaluate("""
            () => {
                const stuck = [];
                document.querySelectorAll('*').forEach(el => {
                    if (el.children.length === 0) {
                        const t = (el.innerText || '').trim();
                        if (t.startsWith('Loading') && t.length < 80) {
                            stuck.push(t);
                        }
                    }
                });
                return [...new Set(stuck)];
            }
        """)
        log(f"  Loading states found: {final_loading}")
        if final_loading:
            record("DOM: Final Loading Scan", "FAIL", f"Stuck states: {final_loading}")
        else:
            record("DOM: Final Loading Scan", "PASS", "No stuck loading states in full DOM")

        # =============================================
        # MOBILE — 375px
        # =============================================
        log("\n=== MOBILE 375px ===")
        mob_ctx = await browser.new_context(
            viewport={"width": 375, "height": 812},
            is_mobile=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        )
        mob = await mob_ctx.new_page()
        mob.on("console", lambda msg: None)  # Ignore mobile console for speed

        try:
            await mob.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=20000)
        except:
            pass
        await mob.wait_for_timeout(2000)

        # Dismiss consent
        for sel in ["button:has-text('Got it')", "button:has-text('Accept')"]:
            try:
                el = await mob.query_selector(sel)
                if el and await el.is_visible():
                    await el.click()
                    await mob.wait_for_timeout(500)
                    break
            except:
                pass

        # Login on mobile
        pwd_m = await mob.query_selector("input[type='password'], input[placeholder*='Bearer']")
        if pwd_m and await pwd_m.is_visible():
            await pwd_m.fill(TOKEN)
            await mob.keyboard.press("Enter")
        await mob.wait_for_timeout(6000)

        await mob.screenshot(path=f"{SS_DIR}/{ss_num:03d}-mobile-375.png")
        log(f"  Screenshot: {ss_num:03d}-mobile-375.png")
        ss_num += 1

        # Hamburger check
        hamb = await mob.evaluate("""
            () => {
                const candidates = document.querySelectorAll('button, [role="button"], [class*="hamburger"], [class*="burger"], [class*="menu-toggle"]');
                for (const el of candidates) {
                    const c = (el.className || '').toLowerCase();
                    const t = (el.title || el.getAttribute('aria-label') || el.innerText || '').toLowerCase();
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0 && (c.includes('hamburger') || c.includes('burger') || c.includes('menu') || t.includes('menu'))) {
                        return {found: true, class: c.substring(0,50), x: Math.round(rect.x), y: Math.round(rect.y)};
                    }
                }
                return {found: false};
            }
        """)
        log(f"  Hamburger: {hamb}")
        record("Mobile 375px: Hamburger", "PASS" if hamb['found'] else "WARN",
               f"Found at ({hamb.get('x')},{hamb.get('y')})" if hamb['found'] else "Not found")

        # Overflow check
        overflow = await mob.evaluate("""
            () => {
                const dw = document.documentElement.clientWidth;
                const issues = [];
                document.querySelectorAll('*').forEach(el => {
                    const r = el.getBoundingClientRect();
                    if (r.right > dw + 5 && r.width > 20) {
                        issues.push({tag: el.tagName, cls: (el.className||'').substring(0,40), over: Math.round(r.right-dw)});
                        if (issues.length >= 3) return;
                    }
                });
                return {docWidth: dw, issues};
            }
        """)
        record("Mobile 375px: No Overflow", "PASS" if not overflow['issues'] else "FAIL",
               f"Clean at {overflow['docWidth']}px" if not overflow['issues'] else f"Overflow: {overflow['issues'][:2]}")

        await mob_ctx.close()

        # =============================================
        # TABLET — 768px
        # =============================================
        log("\n=== TABLET 768px ===")
        tab_ctx = await browser.new_context(viewport={"width": 768, "height": 1024})
        tab = await tab_ctx.new_page()

        try:
            await tab.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=20000)
        except:
            pass
        await tab.wait_for_timeout(2000)

        for sel in ["button:has-text('Got it')", "button:has-text('Accept')"]:
            try:
                el = await tab.query_selector(sel)
                if el and await el.is_visible():
                    await el.click()
                    await tab.wait_for_timeout(500)
                    break
            except:
                pass

        pwd_t = await tab.query_selector("input[type='password'], input[placeholder*='Bearer']")
        if pwd_t and await pwd_t.is_visible():
            await pwd_t.fill(TOKEN)
            await tab.keyboard.press("Enter")
        await tab.wait_for_timeout(6000)

        await tab.screenshot(path=f"{SS_DIR}/{ss_num:03d}-tablet-768.png")
        log(f"  Screenshot: {ss_num:03d}-tablet-768.png")
        ss_num += 1

        tab_portal = await tab.query_selector("#chat-messages, .portal-container, .sidebar")
        record("Tablet 768px: Portal Renders", "PASS" if tab_portal else "WARN",
               "Portal accessible at 768px" if tab_portal else "Portal not found at 768px")

        tab_overflow = await tab.evaluate("""
            () => {
                const dw = document.documentElement.clientWidth;
                const issues = [];
                document.querySelectorAll('*').forEach(el => {
                    const r = el.getBoundingClientRect();
                    if (r.right > dw + 10 && r.width > 20) {
                        issues.push({tag: el.tagName, cls: (el.className||'').substring(0,40), over: Math.round(r.right-dw)});
                        if (issues.length >= 3) return;
                    }
                });
                return {docWidth: dw, issues};
            }
        """)
        record("Tablet 768px: No Overflow", "PASS" if not tab_overflow['issues'] else "FAIL",
               f"Clean at {tab_overflow['docWidth']}px" if not tab_overflow['issues'] else f"Overflow: {tab_overflow['issues']}")

        await tab_ctx.close()

        # =============================================
        # CONSOLE SUMMARY
        # =============================================
        log("\n=== CONSOLE ERROR SUMMARY ===")
        errors = [e for e in console_errors if "[ERROR]" in e or "[PAGE ERROR]" in e]
        warnings = [e for e in console_errors if "[WARNING]" in e or "[WARN]" in e]
        log(f"  Errors: {len(errors)}, Warnings: {len(warnings)}, Total: {len(console_errors)}")

        # Deduplicate errors
        seen_err = set()
        unique_errors = []
        for e in errors:
            key = e[:80]
            if key not in seen_err:
                seen_err.add(key)
                unique_errors.append(e)
                log(f"  ERROR: {e[:250]}")
                if len(unique_errors) >= 8:
                    break

        record("Console Errors", "PASS" if len(errors) == 0 else "WARN" if len(errors) < 5 else "FAIL",
               f"{len(errors)} errors, {len(warnings)} warnings")

        await context.close()
        await browser.close()

        # =============================================
        # FINAL SUMMARY
        # =============================================
        log("\n" + "="*60)
        log("FINAL QA RESULTS")
        log("="*60)

        passes = sum(1 for v in results.values() if v["status"] == "PASS")
        fails = sum(1 for v in results.values() if v["status"] == "FAIL")
        warns = sum(1 for v in results.values() if v["status"] == "WARN")
        total = len(results)

        log(f"\nTOTAL: {total} | PASS: {passes} | FAIL: {fails} | WARN: {warns}")
        if total > 0:
            log(f"PASS RATE: {passes/total*100:.0f}%")

        log("\nDETAILED RESULTS:")
        for name, data in results.items():
            icon = "PASS" if data["status"] == "PASS" else "FAIL" if data["status"] == "FAIL" else "WARN"
            log(f"  [{icon}] {name}: {data['notes']}")

        log(f"\nScreenshots saved to: {SS_DIR}")
        log(f"Total screenshots: {ss_num - 1}")

        # Save JSON
        with open(f"{SS_DIR}/qa-results.json", "w") as f:
            json.dump({"results": results, "errors": unique_errors[:15],
                      "warnings": [w[:200] for w in warnings[:10]]}, f, indent=2)
        log(f"Results JSON: {SS_DIR}/qa-results.json")

        return results


if __name__ == "__main__":
    r = asyncio.run(run())
