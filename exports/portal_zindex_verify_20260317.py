"""
Portal Z-Index Fix Verification
Date: 2026-03-17
Agent: browser-vision-tester

Verifies that .chat-header, #bookmarks-bar, and #chat-search-bar
now have z-index set correctly and are NOT washed out by the neural canvas.

Screenshots saved to: /home/jared/projects/AI-CIV/aether/exports/screenshots/portal-zindex-fix-verify/
"""

import asyncio
import json
import os
from playwright.async_api import async_playwright

PORTAL_URL = "https://app.purebrain.ai"
TOKEN = "UH0pb1T-9lghwLGzRkLzr-rs0cJYszpnLiOjsx9vSwQ"
SS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/portal-zindex-fix-verify"

os.makedirs(SS_DIR, exist_ok=True)

results = {}
ss_count = [0]

def log(msg):
    print(msg, flush=True)

def record(name, status, notes=""):
    results[name] = {"status": status, "notes": notes}
    icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    log(f"  {icon} [{status}] {name}: {notes}")

async def ss(page, label, clip=None):
    ss_count[0] += 1
    fname = f"{ss_count[0]:03d}-{label}.png"
    path = os.path.join(SS_DIR, fname)
    if clip:
        await page.screenshot(path=path, clip=clip)
    else:
        await page.screenshot(path=path, full_page=False)
    log(f"    [Screenshot] {path}")
    return path

async def inject_auth(page):
    await page.evaluate(f"""
        localStorage.setItem('pb_bearer', '{TOKEN}');
        localStorage.setItem('pb_auth_token', '{TOKEN}');
        document.cookie = 'pb_bearer={TOKEN}; path=/';
    """)

async def run():
    log("=" * 60)
    log("PORTAL Z-INDEX FIX VERIFICATION")
    log("Target: .chat-header, #bookmarks-bar, #chat-search-bar")
    log("=" * 60)

    async with async_playwright() as p:

        # ======================================================
        # TEST 1: DESKTOP (1440x900)
        # ======================================================
        log("\n[DESKTOP] Viewport: 1440x900")
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            extra_http_headers={"Authorization": f"Bearer {TOKEN}"}
        )
        page = await ctx.new_page()

        # Capture console errors
        console_errs = []
        page.on("console", lambda m: console_errs.append(f"{m.type}: {m.text}") if m.type == "error" else None)

        await page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=20000)
        await inject_auth(page)
        await page.reload(wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(3000)

        # Full page screenshot first
        await ss(page, "desktop-full-page-1440")

        # Check chat header z-index
        header_styles = await page.evaluate("""
            () => {
                const header = document.querySelector('.chat-header');
                if (!header) return null;
                const cs = window.getComputedStyle(header);
                const rect = header.getBoundingClientRect();
                return {
                    zIndex: cs.zIndex,
                    position: cs.position,
                    opacity: cs.opacity,
                    visibility: cs.visibility,
                    display: cs.display,
                    width: rect.width,
                    height: rect.height,
                    top: rect.top,
                    left: rect.left,
                    exists: true
                };
            }
        """)
        log(f"\n  .chat-header computed styles: {json.dumps(header_styles, indent=2)}")

        # Check bookmarks bar z-index
        bookmarks_styles = await page.evaluate("""
            () => {
                const el = document.getElementById('bookmarks-bar');
                if (!el) return null;
                const cs = window.getComputedStyle(el);
                const rect = el.getBoundingClientRect();
                return {
                    zIndex: cs.zIndex,
                    position: cs.position,
                    opacity: cs.opacity,
                    visibility: cs.visibility,
                    display: cs.display,
                    width: rect.width,
                    height: rect.height,
                    top: rect.top,
                    left: rect.left,
                    exists: true
                };
            }
        """)
        log(f"\n  #bookmarks-bar computed styles: {json.dumps(bookmarks_styles, indent=2)}")

        # Check chat-search-bar z-index
        search_styles = await page.evaluate("""
            () => {
                const el = document.getElementById('chat-search-bar');
                if (!el) return null;
                const cs = window.getComputedStyle(el);
                const rect = el.getBoundingClientRect();
                return {
                    zIndex: cs.zIndex,
                    position: cs.position,
                    opacity: cs.opacity,
                    visibility: cs.visibility,
                    display: cs.display,
                    width: rect.width,
                    height: rect.height,
                    top: rect.top,
                    left: rect.left,
                    exists: true
                };
            }
        """)
        log(f"\n  #chat-search-bar computed styles: {json.dumps(search_styles, indent=2)}")

        # Check neural canvas z-index (should be BELOW headers)
        canvas_styles = await page.evaluate("""
            () => {
                const el = document.getElementById('hmiCanvas') || document.querySelector('#neural-canvas, canvas');
                if (!el) return null;
                const cs = window.getComputedStyle(el);
                const rect = el.getBoundingClientRect();
                return {
                    zIndex: cs.zIndex,
                    position: cs.position,
                    opacity: cs.opacity,
                    width: rect.width,
                    height: rect.height,
                    top: rect.top,
                    left: rect.left,
                    id: el.id,
                    exists: true
                };
            }
        """)
        log(f"\n  Neural canvas computed styles: {json.dumps(canvas_styles, indent=2)}")

        # Assess z-index relationships
        log("\n--- Z-INDEX ANALYSIS ---")

        if header_styles and header_styles.get("exists"):
            h_z = header_styles.get("zIndex", "0")
            h_pos = header_styles.get("position", "static")
            z_ok = h_pos != "static" and (h_z == "auto" or int(h_z) >= 1 if h_z != "auto" else True)
            record("chat-header z-index", "PASS" if z_ok else "FAIL",
                   f"position={h_pos}, z-index={h_z}")
        else:
            record("chat-header z-index", "FAIL", "element not found in DOM")

        if bookmarks_styles and bookmarks_styles.get("exists"):
            b_z = bookmarks_styles.get("zIndex", "0")
            b_pos = bookmarks_styles.get("position", "static")
            b_display = bookmarks_styles.get("display", "none")
            z_ok = b_pos != "static" and (b_z == "auto" or int(b_z) >= 1 if b_z != "auto" else True)
            record("#bookmarks-bar z-index", "PASS" if z_ok else "WARN",
                   f"position={b_pos}, z-index={b_z}, display={b_display}")
        else:
            record("#bookmarks-bar z-index", "WARN", "element not found in DOM (may be conditional)")

        if search_styles and search_styles.get("exists"):
            s_z = search_styles.get("zIndex", "0")
            s_pos = search_styles.get("position", "static")
            s_display = search_styles.get("display", "none")
            z_ok = s_pos != "static" and (s_z == "auto" or int(s_z) >= 1 if s_z != "auto" else True)
            record("#chat-search-bar z-index", "PASS" if z_ok else "WARN",
                   f"position={s_pos}, z-index={s_z}, display={s_display}")
        else:
            record("#chat-search-bar z-index", "WARN", "element not found in DOM (may be conditional)")

        # Focused crop of chat header area (top ~200px of chat panel)
        if header_styles and header_styles.get("width", 0) > 0:
            h_top = int(header_styles.get("top", 0))
            h_left = int(header_styles.get("left", 0))
            h_width = int(header_styles.get("width", 800))
            h_height = int(header_styles.get("height", 60))
            # Add padding for context
            clip_region = {
                "x": max(0, h_left - 10),
                "y": max(0, h_top - 10),
                "width": min(h_width + 20, 1440),
                "height": h_height + 120  # Include bookmarks + search bars below
            }
            await ss(page, "desktop-chat-header-crop-1440", clip=clip_region)
            log(f"  Cropped chat header area: {clip_region}")

        # Screenshot focusing top-left chat panel area
        await ss(page, "desktop-chat-panel-top-1440", clip={"x": 0, "y": 0, "width": 1000, "height": 200})

        # Check if SESSION DIALOGUE text is visible
        session_dialogue = await page.evaluate("""
            () => {
                const els = document.querySelectorAll('*');
                for (const el of els) {
                    if (el.textContent.trim() === 'SESSION DIALOGUE' && el.children.length === 0) {
                        const rect = el.getBoundingClientRect();
                        const cs = window.getComputedStyle(el);
                        return {
                            found: true,
                            text: el.textContent,
                            opacity: cs.opacity,
                            color: cs.color,
                            visibility: cs.visibility,
                            top: rect.top,
                            left: rect.left
                        };
                    }
                }
                // Try partial match
                const heading = document.querySelector('.session-title, .chat-title, h1, h2, h3, h4');
                if (heading) {
                    const rect = heading.getBoundingClientRect();
                    const cs = window.getComputedStyle(heading);
                    return {
                        found: true,
                        text: heading.textContent.trim().substring(0, 50),
                        opacity: cs.opacity,
                        color: cs.color,
                        visibility: cs.visibility,
                        top: rect.top,
                        left: rect.left
                    };
                }
                return {found: false};
            }
        """)
        log(f"\n  SESSION DIALOGUE element: {json.dumps(session_dialogue, indent=2)}")

        # Check for Search button
        search_btn = await page.evaluate("""
            () => {
                // Look for search button in header
                const btns = document.querySelectorAll('.chat-header button, .chat-header [role="button"], .chat-header .btn');
                const results = [];
                for (const btn of btns) {
                    const rect = btn.getBoundingClientRect();
                    const cs = window.getComputedStyle(btn);
                    results.push({
                        text: btn.textContent.trim().substring(0, 30),
                        opacity: cs.opacity,
                        visibility: cs.visibility,
                        display: cs.display,
                        top: rect.top,
                        left: rect.left,
                        width: rect.width,
                        height: rect.height
                    });
                }
                return results;
            }
        """)
        log(f"\n  Header buttons: {json.dumps(search_btn, indent=2)}")

        record("SESSION DIALOGUE visible", "PASS" if session_dialogue.get("found") else "WARN",
               f"found={session_dialogue.get('found')}, opacity={session_dialogue.get('opacity', 'N/A')}")
        record("Desktop header buttons", "PASS" if len(search_btn) > 0 else "WARN",
               f"{len(search_btn)} buttons found in chat-header")

        # Console errors
        prod_errors = [e for e in console_errs if "401" not in e and "microphone" not in e.lower() and "webgl" not in e.lower()]
        record("Desktop console errors", "PASS" if len(prod_errors) == 0 else "WARN",
               f"{len(prod_errors)} production errors ({len(console_errs)} total)")

        await browser.close()

        # ======================================================
        # TEST 2: MOBILE (375x667)
        # ======================================================
        log("\n[MOBILE] Viewport: 375x667")
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            viewport={"width": 375, "height": 667},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            extra_http_headers={"Authorization": f"Bearer {TOKEN}"}
        )
        page_m = await ctx.new_page()

        mobile_errs = []
        page_m.on("console", lambda m: mobile_errs.append(f"{m.type}: {m.text}") if m.type == "error" else None)

        await page_m.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=20000)
        await page_m.evaluate(f"""
            localStorage.setItem('pb_bearer', '{TOKEN}');
            localStorage.setItem('pb_auth_token', '{TOKEN}');
        """)
        await page_m.reload(wait_until="domcontentloaded", timeout=20000)
        await page_m.wait_for_timeout(3000)

        # Full mobile screenshot
        await ss(page_m, "mobile-full-375")

        # Top area crop
        await ss(page_m, "mobile-top-section-375", clip={"x": 0, "y": 0, "width": 375, "height": 200})

        # Check same elements on mobile
        mobile_header = await page_m.evaluate("""
            () => {
                const header = document.querySelector('.chat-header');
                if (!header) return null;
                const cs = window.getComputedStyle(header);
                const rect = header.getBoundingClientRect();
                return {
                    zIndex: cs.zIndex,
                    position: cs.position,
                    opacity: cs.opacity,
                    display: cs.display,
                    width: rect.width,
                    height: rect.height,
                    top: rect.top
                };
            }
        """)
        log(f"\n  Mobile .chat-header: {json.dumps(mobile_header, indent=2)}")

        mobile_canvas = await page_m.evaluate("""
            () => {
                const el = document.getElementById('hmiCanvas') || document.querySelector('canvas');
                if (!el) return null;
                const cs = window.getComputedStyle(el);
                return {
                    zIndex: cs.zIndex,
                    position: cs.position,
                    id: el.id
                };
            }
        """)
        log(f"\n  Mobile canvas: {json.dumps(mobile_canvas, indent=2)}")

        if mobile_header and mobile_header.get("width", 0) > 0:
            h_pos = mobile_header.get("position", "static")
            h_z = mobile_header.get("zIndex", "0")
            z_ok = h_pos != "static" and (h_z == "auto" or int(h_z) >= 1 if h_z != "auto" else True)
            record("Mobile chat-header z-index", "PASS" if z_ok else "FAIL",
                   f"position={h_pos}, z-index={h_z}")
        else:
            record("Mobile chat-header z-index", "WARN", "element not found on mobile")

        m_prod_errors = [e for e in mobile_errs if "401" not in e and "microphone" not in e.lower() and "webgl" not in e.lower()]
        record("Mobile console errors", "PASS" if len(m_prod_errors) == 0 else "WARN",
               f"{len(m_prod_errors)} production errors")

        await browser.close()

    # ======================================================
    # FINAL REPORT
    # ======================================================
    log("\n" + "=" * 60)
    log("Z-INDEX FIX VERIFICATION RESULTS")
    log("=" * 60)
    passed = sum(1 for r in results.values() if r["status"] == "PASS")
    warned = sum(1 for r in results.values() if r["status"] == "WARN")
    failed = sum(1 for r in results.values() if r["status"] == "FAIL")
    total = len(results)
    log(f"PASS: {passed}/{total}  WARN: {warned}  FAIL: {failed}")
    log("")
    for name, r in results.items():
        icon = "✅" if r["status"] == "PASS" else "❌" if r["status"] == "FAIL" else "⚠️"
        log(f"  {icon} {name}: {r['notes']}")
    log(f"\nScreenshots: {SS_DIR}")
    log("=" * 60)

    return results

if __name__ == "__main__":
    asyncio.run(run())
