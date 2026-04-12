#!/usr/bin/env python3
"""Test voice/HMI overlay by clicking mic-btn in chat input area"""

import asyncio
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

        console_errs = []
        page.on("console", lambda m: console_errs.append(f"{m.type}: {m.text}") if m.type == "error" else None)

        await page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)
        await page.evaluate(f"""
            localStorage.setItem('pb_token', '{TOKEN}');
            localStorage.setItem('portal_token', '{TOKEN}');
        """)
        await ctx.add_cookies([{"name":"pb_token","value":TOKEN,"domain":"app.purebrain.ai","path":"/"}])
        await page.reload(wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(5000)

        # Screenshot initial state
        await page.screenshot(path=f"{SS_DIR}/31-hmi-pre-click-full.png")

        # Check overlay before
        pre = await page.evaluate("""
            () => {
                const ov = document.querySelector('#hmiVoiceOverlay');
                const micBtn = document.querySelector('#mic-btn');
                const micBtnRect = micBtn ? micBtn.getBoundingClientRect() : null;
                return {
                    overlayDisplay: ov ? window.getComputedStyle(ov).display : 'not found',
                    micBtnRect: micBtnRect,
                    micBtnVisible: micBtn ? (micBtnRect.width > 0 && micBtnRect.height > 0) : false
                };
            }
        """)
        print(f"Pre-click: overlay={pre.get('overlayDisplay')}, micBtn rect={pre.get('micBtnRect')}, visible={pre.get('micBtnVisible')}")

        # Click the mic-btn
        await page.evaluate("document.querySelector('#mic-btn').click()")
        await page.wait_for_timeout(2000)

        await page.screenshot(path=f"{SS_DIR}/32-hmi-after-mic-click.png")
        print(f"Screenshot: {SS_DIR}/32-hmi-after-mic-click.png")

        # Check overlay after
        post = await page.evaluate("""
            () => {
                const ov = document.querySelector('#hmiVoiceOverlay');
                const ovStyle = ov ? window.getComputedStyle(ov) : null;
                const vortex = document.querySelector('#hmiCanvas');  // voice overlay uses #hmiCanvas too
                const hmiMicBtn = document.querySelector('#hmiMicBtn');
                const standbyBtn = Array.from(document.querySelectorAll('[class*="state-btn"]')).find(b => b.textContent.trim() === 'Standby');
                const statusVal = document.querySelector('#hmiStatusVal');

                // TWO-WAY check — look for it as a BUTTON (not in chat text)
                const twoWayBtn = Array.from(document.querySelectorAll('button, .btn, [role="button"]')).find(b =>
                    b.textContent.includes('Two-Way Communication') || b.textContent.includes('Click for Two-Way')
                );

                // Also check if the overlay has any button mentioning Two-Way
                const overlayHTML = ov ? ov.innerHTML : '';
                const twoWayInOverlay = overlayHTML.includes('Two-Way');

                return {
                    overlayDisplay: ovStyle ? ovStyle.display : 'not found',
                    overlayVisible: ov ? (ovStyle.display !== 'none' && ovStyle.visibility !== 'hidden') : false,
                    overlayRect: ov ? ov.getBoundingClientRect() : null,
                    hmiCanvas: vortex ? {id: vortex.id, w: vortex.width, h: vortex.height} : null,
                    hmiMicBtn: hmiMicBtn ? {id: hmiMicBtn.id, text: hmiMicBtn.textContent.trim()} : null,
                    standbyBtn: standbyBtn ? {text: standbyBtn.textContent.trim(), cls: standbyBtn.className} : null,
                    statusVal: statusVal ? statusVal.textContent.trim() : null,
                    twoWayBtn: twoWayBtn ? {tag: twoWayBtn.tagName, text: twoWayBtn.textContent.trim().substring(0,50)} : null,
                    twoWayInOverlay: twoWayInOverlay
                };
            }
        """)
        print(f"\nPost-click results:")
        for k, v in post.items():
            print(f"  {k}: {v}")

        await browser.close()
        return post

if __name__ == "__main__":
    asyncio.run(run())
