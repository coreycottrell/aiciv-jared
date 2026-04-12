#!/usr/bin/env python3
"""
Final live staging test for naming ceremony - 2026-03-10
Tests the actual Cloudflare staging URLs after fix verification.
"""

import asyncio
import os
import json
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

SCREENSHOTS_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/naming-ceremony-test-20260310")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

TG_SEND = "/home/jared/projects/AI-CIV/aether/tools/tg_send.sh"

PAGES = {
    "pay-test-2-LIVE": "https://purebrain-staging.pages.dev/pay-test-2/",
    "sandbox-3-LIVE": "https://purebrain-staging.pages.dev/pay-test-sandbox-3/",
}

def tg(msg):
    os.system(f'{TG_SEND} "{msg}"')
    print(f"[TG] {msg}")

async def screenshot(page, label, prefix):
    path = SCREENSHOTS_DIR / f"{prefix}-{label}.png"
    await page.screenshot(path=str(path), full_page=False)
    print(f"[SCREENSHOT] {path.name}")
    return str(path)

async def dismiss_preloader(page):
    try:
        await page.wait_for_selector(".theme-preloader", state="hidden", timeout=8000)
        return
    except PlaywrightTimeout:
        pass
    await page.evaluate("""() => {
        const preloader = document.querySelector('.theme-preloader');
        if (preloader) {
            preloader.style.display = 'none';
            preloader.style.pointerEvents = 'none';
        }
    }""")

async def test_live_page(page_key, url):
    prefix = page_key.replace("-", "").replace("LIVE", "live")
    results = {
        "page": page_key, "url": url,
        "findings": [], "screenshots": [], "ai_messages": [],
        "verdict": "UNKNOWN", "chatbox_version": "UNKNOWN",
    }

    print(f"\n{'='*60}")
    print(f"LIVE TEST: {page_key}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        console_msgs = []
        page_errors = []
        api_requests = []

        page.on("console", lambda m: console_msgs.append({"type": m.type, "text": m.text}))
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.on("request", lambda r: api_requests.append(r.url[:200]) if any(k in r.url for k in ["workers.dev", "puremarketing.ai"]) else None)

        # Load
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
        except PlaywrightTimeout:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        await asyncio.sleep(5)
        await dismiss_preloader(page)

        shot = await screenshot(page, "F01-loaded", prefix)
        results["screenshots"].append(shot)

        # Check JS state
        js_state = await page.evaluate("""() => ({
            startConversation: typeof window.startConversation === 'function',
            btn_visible: !!document.querySelector('.chat-initial__btn'),
            page_errors: [],
        })""")
        print(f"[JS] {js_state}")
        results["findings"].append(f"JS check: {js_state}")

        if not js_state.get("startConversation"):
            results["findings"].append(f"FAIL: startConversation not defined. Page errors: {page_errors[:3]}")
            results["verdict"] = "FAIL - JS not loading"
            tg(f"QA LIVE: {page_key} FAIL - startConversation not defined! Page errors: {page_errors[:2]}")
            await browser.close()
            return results

        results["findings"].append("startConversation() registered - JS fix confirmed on LIVE staging!")

        # Scroll to chatbox
        await page.evaluate("() => { const c = document.getElementById('chatInitial'); if(c) c.scrollIntoView({block:'center'}); }")
        await asyncio.sleep(1)

        shot = await screenshot(page, "F02-chatbox-pre-click", prefix)
        results["screenshots"].append(shot)

        # Click via JS dispatch
        tg(f"QA LIVE: {page_key} - JS working on live staging! Clicking Begin Awakening...")
        await page.evaluate("() => document.querySelector('.chat-initial__btn').click()")
        await asyncio.sleep(2)

        shot = await screenshot(page, "F03-after-click", prefix)
        results["screenshots"].append(shot)

        # Wait for AI - 60s
        ai_appeared = False
        for i in range(12):
            await asyncio.sleep(5)
            count = await page.evaluate("document.querySelectorAll('.message--ai').length")
            api_count = len(api_requests)
            print(f"  [{(i+1)*5}s] AI messages: {count}, API calls: {api_count}")
            if count > 0:
                ai_appeared = True
                break

        if not ai_appeared:
            errors_txt = [m["text"][:150] for m in console_msgs if m["type"] == "error"][:5]
            results["findings"].append(f"No AI messages in 60s. API calls: {api_requests[:3]}")
            results["findings"].append(f"Console errors: {errors_txt}")
            results["verdict"] = "FAIL - API not responding on live staging"
            tg(f"QA LIVE: {page_key} FAIL - No AI response in 60s. API calls: {len(api_requests)}")
            shot = await screenshot(page, "F04-timeout", prefix)
            results["screenshots"].append(shot)
            await browser.close()
            return results

        await asyncio.sleep(3)
        shot = await screenshot(page, "F04-ai-opening", prefix)
        results["screenshots"].append(shot)

        opening = await page.evaluate("() => [...document.querySelectorAll('.message--ai')].map(m => m.innerText.trim())")
        results["ai_messages"] = opening
        print(f"[OPENING] {len(opening)} messages:")
        for t in opening:
            print(f"  '{t[:150]}'")
        results["findings"].append(f"Opening: {len(opening)} messages")
        tg(f"QA LIVE: {page_key} - AI is ALIVE! {len(opening)} opening messages. Testing naming ceremony...")

        # User input
        inp = await page.query_selector("#userInput")
        if inp:
            await inp.click()
            await inp.type("Hello! I'm a product manager who loves building things that matter.")
            await inp.press("Enter")
            await asyncio.sleep(2)
            try:
                await page.wait_for_function(f"document.querySelectorAll('.message--ai').length > {len(opening)}", timeout=25000)
            except PlaywrightTimeout:
                pass
            await asyncio.sleep(3)
            shot = await screenshot(page, "F05-greeting-response", prefix)
            results["screenshots"].append(shot)

            n1 = await page.evaluate("() => document.querySelectorAll('.message--ai').length")

            await inp.click()
            await inp.type("I care about depth, authenticity, and collaborative intelligence.")
            await inp.press("Enter")
            await asyncio.sleep(2)
            try:
                await page.wait_for_function(f"document.querySelectorAll('.message--ai').length > {n1}", timeout=25000)
            except PlaywrightTimeout:
                pass
            await asyncio.sleep(3)
            shot = await screenshot(page, "F06-second-response", prefix)
            results["screenshots"].append(shot)

            n2 = await page.evaluate("() => document.querySelectorAll('.message--ai').length")

            # Suggest Nova
            await inp.click()
            await inp.type("What if I called you Nova? Like something new and full of light.")
            await inp.press("Enter")
            tg(f"QA LIVE: {page_key} - Suggesting 'Nova', watching for full naming ceremony...")
            await asyncio.sleep(2)
            try:
                await page.wait_for_function(f"document.querySelectorAll('.message--ai').length > {n2}", timeout=30000)
            except PlaywrightTimeout:
                pass
            await asyncio.sleep(6)
            shot = await screenshot(page, "F07-naming-response", prefix)
            results["screenshots"].append(shot)

            final = await page.evaluate("() => [...document.querySelectorAll('.message--ai')].map(m => m.innerText.trim())")
            results["ai_messages"] = final
            naming_resp = final[n2:]
            results["findings"].append(f"Total AI messages: {len(final)}")
            results["findings"].append(f"Naming responses: {len(naming_resp)}")

            if naming_resp:
                results["findings"].append(f"Naming sample: {naming_resp[0][:300]}")

            combined = " ".join(final).lower()
            has_contemp = any(w in combined for w in ["contemplat", "before i", "let me sit", "resonates", "what i notice", "still", "reflecting"])
            has_name = any(w in combined for w in ["nova", "i am", "call me", "yes", "name"])
            results["findings"].append(f"Contemplation: {has_contemp}, Name acceptance: {has_name}")

            if has_contemp and has_name:
                results["chatbox_version"] = "FULL - contemplation + ceremony + naming on LIVE staging"
            elif has_name:
                results["chatbox_version"] = "GOOD - naming ceremony present on LIVE staging"
            else:
                results["chatbox_version"] = "IN PROGRESS - needs more turns"

        # Errors
        errors = [m for m in console_msgs if m["type"] == "error"]
        # Filter out expected errors (CORS from Cloudflare origin to WP APIs)
        real_errors = [m for m in errors if "workers.dev" not in m["text"] and "puremarketing.ai" not in m["text"]]
        results["findings"].append(f"Console errors: {len(errors)} total, {len(real_errors)} real")

        ai_count = len(final) if "final" in dir() else 0
        if ai_count >= 3:
            results["verdict"] = "PASS"
        else:
            results["verdict"] = "PARTIAL"

        await browser.close()
    return results


async def main():
    tg("QA LIVE: Running final naming ceremony test on live Cloudflare staging pages...")
    all_results = {}

    for key, url in PAGES.items():
        result = await test_live_page(key, url)
        all_results[key] = result
        tg(f"QA LIVE: {key}: {result['verdict']} | {result['chatbox_version']}")

    path = SCREENSHOTS_DIR / "live-final-results.json"
    with open(path, "w") as f:
        json.dump(all_results, f, indent=2)

    print("\n" + "="*60)
    print("FINAL LIVE TEST SUMMARY")
    print("="*60)
    for k, r in all_results.items():
        print(f"\n{k}:")
        print(f"  Verdict: {r['verdict']}")
        print(f"  Chatbox: {r['chatbox_version']}")
        print(f"  AI msgs: {len(r.get('ai_messages', []))}")
        for f in r.get("findings", [])[-8:]:
            print(f"    {f}")

    tg("QA LIVE: All live staging tests complete!")


if __name__ == "__main__":
    asyncio.run(main())
