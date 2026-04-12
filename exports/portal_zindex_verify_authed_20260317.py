"""
Portal Z-Index Fix Verification — Authenticated
Injects bearer token directly via localStorage to bypass login screen
and capture the authenticated chat panel state.
"""

import asyncio
import json
import os
from playwright.async_api import async_playwright

PORTAL_URL = "https://app.purebrain.ai"
TOKEN = "UH0pb1T-9lghwLGzRkLzr-rs0cJYszpnLiOjsx9vSwQ"
SS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/portal-zindex-fix-verify"
os.makedirs(SS_DIR, exist_ok=True)

ss_count = [0]

def log(msg):
    print(msg, flush=True)

async def ss(page, label, clip=None):
    ss_count[0] += 1
    fname = f"{ss_count[0]:03d}-authed-{label}.png"
    path = os.path.join(SS_DIR, fname)
    if clip:
        await page.screenshot(path=path, clip=clip)
    else:
        await page.screenshot(path=path, full_page=False)
    log(f"    [Screenshot] {path}")
    return path

async def run():
    log("=" * 60)
    log("PORTAL Z-INDEX VERIFICATION — AUTHENTICATED SESSION")
    log("=" * 60)

    async with async_playwright() as p:

        # =====================================================
        # DESKTOP (1440x900) — AUTHENTICATED
        # =====================================================
        log("\n[DESKTOP] 1440x900 — with token injection")
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            extra_http_headers={"Authorization": f"Bearer {TOKEN}"}
        )
        page = await ctx.new_page()

        console_errs = []
        page.on("console", lambda m: console_errs.append(f"{m.type}: {m.text}"))

        # First load — inject token into storage
        await page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=20000)
        await page.evaluate(f"""
            () => {{
                // Try multiple storage keys that the portal may check
                localStorage.setItem('pb_bearer', '{TOKEN}');
                localStorage.setItem('bearer', '{TOKEN}');
                localStorage.setItem('auth_token', '{TOKEN}');
                localStorage.setItem('token', '{TOKEN}');
                sessionStorage.setItem('pb_bearer', '{TOKEN}');
                sessionStorage.setItem('bearer', '{TOKEN}');
                // Cookie approach
                document.cookie = 'pb_bearer={TOKEN}; path=/; SameSite=Lax';
                document.cookie = 'bearer={TOKEN}; path=/; SameSite=Lax';
            }}
        """)

        # Check what token key the app uses
        app_keys = await page.evaluate("""
            () => {
                const keys = Object.keys(localStorage);
                return keys.map(k => ({ key: k, value: localStorage.getItem(k)?.substring(0, 30) }));
            }
        """)
        log(f"  localStorage keys after injection: {json.dumps(app_keys, indent=2)}")

        # Check the page source for token key name
        page_source = await page.content()
        # Look for the token variable name
        import re
        token_keys = re.findall(r"localStorage\.(?:getItem|setItem)\(['\"]([^'\"]+)['\"]", page_source)
        log(f"  Token keys used in app source: {list(set(token_keys))[:10]}")

        # Reload to apply token
        await page.reload(wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(4000)

        # Take screenshot to see current state
        await ss(page, "desktop-after-token-1440")

        # Check page title / state
        title = await page.title()
        url = page.url
        log(f"  Page title: {title}")
        log(f"  Current URL: {url}")

        # Check if we're past the login screen
        login_form_visible = await page.evaluate("""
            () => {
                const input = document.querySelector('input[type="text"], input[placeholder*="Bearer"], input[placeholder*="Token"]');
                if (input) {
                    const cs = window.getComputedStyle(input);
                    return { visible: cs.display !== 'none' && cs.visibility !== 'hidden', display: cs.display };
                }
                return { visible: false };
            }
        """)
        log(f"  Login form visible: {login_form_visible}")

        if login_form_visible.get("visible"):
            log("  -> Still on login screen. Filling token and submitting...")
            # Try to fill the bearer token input and submit
            try:
                await page.fill('input[placeholder*="Bearer"], input[placeholder*="Token"], input[type="text"]', TOKEN)
                await page.wait_for_timeout(500)
                # Try clicking submit button
                await page.click('button[type="submit"], .submit-btn, button:has-text("ACCESS")', timeout=5000)
                await page.wait_for_timeout(4000)
                await ss(page, "desktop-after-submit-1440")
            except Exception as e:
                log(f"  Submit attempt failed: {e}")

        # Now inspect the chat header
        header_info = await page.evaluate("""
            () => {
                const header = document.querySelector('.chat-header');
                if (!header) return {exists: false};
                const cs = window.getComputedStyle(header);
                const rect = header.getBoundingClientRect();
                return {
                    exists: true,
                    zIndex: cs.zIndex,
                    position: cs.position,
                    backgroundColor: cs.backgroundColor,
                    opacity: cs.opacity,
                    display: cs.display,
                    top: rect.top,
                    left: rect.left,
                    width: rect.width,
                    height: rect.height
                };
            }
        """)
        log(f"\n  .chat-header: {json.dumps(header_info, indent=2)}")

        # Check all canvas elements
        canvases = await page.evaluate("""
            () => {
                const els = document.querySelectorAll('canvas');
                return Array.from(els).map(el => {
                    const cs = window.getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    return {
                        id: el.id,
                        className: el.className,
                        zIndex: cs.zIndex,
                        position: cs.position,
                        width: rect.width,
                        height: rect.height,
                        top: rect.top,
                        left: rect.left
                    };
                });
            }
        """)
        log(f"\n  Canvas elements: {json.dumps(canvases, indent=2)}")

        # Header crop if header is visible
        if header_info.get("exists") and header_info.get("width", 0) > 0:
            top = max(0, int(header_info.get("top", 0)) - 5)
            left = max(0, int(header_info.get("left", 0)) - 5)
            w = min(int(header_info.get("width", 1000)) + 10, 1440)
            h = int(header_info.get("height", 40)) + 80
            await ss(page, "desktop-header-crop-1440", clip={"x": left, "y": top, "width": w, "height": h})

        # Check for SESSION DIALOGUE title text
        session_text = await page.evaluate("""
            () => {
                // Search for SESSION DIALOGUE text in the DOM
                const allEls = document.querySelectorAll('.chat-header *');
                const texts = [];
                for (const el of allEls) {
                    const text = el.textContent.trim();
                    if (text.length > 0 && text.length < 100 && el.children.length === 0) {
                        const cs = window.getComputedStyle(el);
                        const rect = el.getBoundingClientRect();
                        texts.push({
                            text: text.substring(0, 50),
                            tag: el.tagName,
                            opacity: cs.opacity,
                            color: cs.color,
                            fontSize: cs.fontSize,
                            top: rect.top,
                            left: rect.left
                        });
                    }
                }
                return texts;
            }
        """)
        log(f"\n  Chat header text elements: {json.dumps(session_text, indent=2)}")

        # Check console for z-index related errors
        zindex_logs = [e for e in console_errs if "zIndex" in e.lower() or "z-index" in e.lower() or "canvas" in e.lower()]
        log(f"\n  Z-index/canvas console messages: {zindex_logs[:5]}")
        log(f"  Total console messages: {len(console_errs)}")

        # Crop top 100px across full width to show header bar
        await ss(page, "desktop-top-100px-1440", clip={"x": 0, "y": 0, "width": 1440, "height": 100})

        await browser.close()

        # =====================================================
        # MOBILE (375x667) — AUTHENTICATED
        # =====================================================
        log("\n[MOBILE] 375x667 — with token injection")
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={"width": 375, "height": 667},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            extra_http_headers={"Authorization": f"Bearer {TOKEN}"}
        )
        page_m = await ctx.new_page()
        await page_m.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=20000)
        await page_m.evaluate(f"""
            () => {{
                localStorage.setItem('pb_bearer', '{TOKEN}');
                localStorage.setItem('bearer', '{TOKEN}');
                localStorage.setItem('auth_token', '{TOKEN}');
                localStorage.setItem('token', '{TOKEN}');
                document.cookie = 'pb_bearer={TOKEN}; path=/; SameSite=Lax';
            }}
        """)
        await page_m.reload(wait_until="domcontentloaded", timeout=20000)
        await page_m.wait_for_timeout(3000)

        login_visible_m = await page_m.evaluate("""
            () => {
                const input = document.querySelector('input[placeholder*="Bearer"], input[placeholder*="Token"]');
                return input ? { visible: window.getComputedStyle(input).display !== 'none' } : { visible: false };
            }
        """)
        if login_visible_m.get("visible"):
            try:
                await page_m.fill('input[placeholder*="Bearer"], input[placeholder*="Token"]', TOKEN)
                await page_m.wait_for_timeout(300)
                await page_m.click('button:has-text("ACCESS")', timeout=5000)
                await page_m.wait_for_timeout(4000)
            except Exception as e:
                log(f"  Mobile submit: {e}")

        await ss(page_m, "mobile-full-375")
        await ss(page_m, "mobile-top-60px-375", clip={"x": 0, "y": 0, "width": 375, "height": 80})

        mobile_header = await page_m.evaluate("""
            () => {
                const h = document.querySelector('.chat-header');
                if (!h) return {exists: false};
                const cs = window.getComputedStyle(h);
                const rect = h.getBoundingClientRect();
                return {
                    exists: true,
                    zIndex: cs.zIndex,
                    position: cs.position,
                    backgroundColor: cs.backgroundColor,
                    opacity: cs.opacity,
                    top: rect.top,
                    height: rect.height,
                    width: rect.width
                };
            }
        """)
        log(f"\n  Mobile .chat-header: {json.dumps(mobile_header, indent=2)}")

        await browser.close()

    log("\n" + "=" * 60)
    log("AUTHED VERIFICATION COMPLETE")
    log(f"Screenshots: {SS_DIR}")
    log("=" * 60)

if __name__ == "__main__":
    asyncio.run(run())
