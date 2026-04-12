#!/usr/bin/env python3
"""
pay-test-2 visibility audit v5
Password: PureBrain.ai253443$$$ (three dollar signs — confirmed working)
Fixes: screenshot timeout, full JS diagnostics
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/paytest2-visibility-audit")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

URL = "https://purebrain.ai/pay-test-2/"
PASSWORD = "PureBrain.ai253443$$$"

async def safe_screenshot(page, path, full_page=False, timeout=60000):
    """Screenshot with extended timeout"""
    try:
        await page.screenshot(path=str(path), full_page=full_page, timeout=timeout)
        print(f"  Screenshot: {path.name}")
    except Exception as e:
        print(f"  Screenshot FAILED: {path.name} — {str(e)[:100]}")
        # Try viewport-only as fallback
        try:
            await page.screenshot(path=str(path), full_page=False, timeout=15000)
            print(f"  Screenshot (viewport only): {path.name}")
        except Exception as e2:
            print(f"  Screenshot FAILED (fallback too): {str(e2)[:80]}")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-web-security",
                  "--font-render-hinting=none"]
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # === Navigate + Password ===
        print(f"[1] Navigating to {URL}")
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        pwd_input = page.locator('input[name="post_password"]')
        if await pwd_input.count() > 0:
            await pwd_input.first.click()
            await page.keyboard.type(PASSWORD)
            await page.wait_for_timeout(300)
            await page.locator('input[type="submit"]').first.click()
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
            await page.wait_for_timeout(3000)

        scroll_h = await page.evaluate("document.body.scrollHeight")
        sections_n = await page.evaluate("document.querySelectorAll('section').length")
        print(f"[2] ScrollH={scroll_h}, Sections={sections_n}")

        if scroll_h < 5000:
            print("[!] Page not loaded — exiting")
            await browser.close()
            return

        # === Screenshot 1: Top of page (viewport) ===
        ss1 = SCREENSHOT_DIR / "V5-01-top-viewport.png"
        await safe_screenshot(page, ss1, full_page=False)

        # === Scroll to What Happens Next section ===
        whn_info = await page.evaluate("""
(function() {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node;
    while (node = walker.nextNode()) {
        const txt = node.textContent || '';
        if (txt.toUpperCase().includes('WHAT HAPPENS NEXT')) {
            const el = node.parentElement;
            el.scrollIntoView({behavior: 'instant', block: 'start'});
            const rect = el.getBoundingClientRect();
            return {
                found: true,
                tag: el.tagName,
                class: el.className.substring(0, 80),
                scrollY: window.scrollY,
                rectTop: rect.top,
                text: txt.substring(0, 50)
            };
        }
    }
    return {found: false};
})()
""")
        print(f"[3] What Happens Next: {whn_info}")
        await page.wait_for_timeout(800)

        ss2 = SCREENSHOT_DIR / "V5-02-what-happens-next.png"
        await safe_screenshot(page, ss2)

        # Scroll 600px below WHN
        await page.evaluate("window.scrollBy(0, 600)")
        await page.wait_for_timeout(500)
        ss3 = SCREENSHOT_DIR / "V5-03-below-whn-600px.png"
        await safe_screenshot(page, ss3)

        # Another 700px below
        await page.evaluate("window.scrollBy(0, 700)")
        await page.wait_for_timeout(500)
        ss4 = SCREENSHOT_DIR / "V5-04-below-whn-1300px.png"
        await safe_screenshot(page, ss4)

        # === DOM Visibility: ALL sections ===
        sections_result = await page.evaluate("""
(function() {
    const allSections = document.querySelectorAll('section');
    const results = [];
    allSections.forEach((s, i) => {
        const rect = s.getBoundingClientRect();
        const styles = window.getComputedStyle(s);
        results.push({
            index: i,
            class: s.className.substring(0, 80),
            id: s.id,
            display: styles.display,
            visibility: styles.visibility,
            opacity: styles.opacity,
            height: rect.height,
            top: Math.round(rect.top + window.scrollY),
            overflow: styles.overflow,
            maxHeight: styles.maxHeight,
            position: styles.position
        });
    });
    return JSON.stringify(results, null, 2);
})()
""")
        sections_data = json.loads(sections_result)

        # === overflow:hidden clips ===
        clips_result = await page.evaluate("""
(function() {
    const clips = [];
    document.querySelectorAll('*').forEach(el => {
        const s = window.getComputedStyle(el);
        if (s.overflow === 'hidden' && el.scrollHeight > el.clientHeight + 10) {
            clips.push({
                tag: el.tagName,
                class: el.className.substring(0, 60),
                id: el.id,
                clientHeight: el.clientHeight,
                scrollHeight: el.scrollHeight,
                overflow: s.overflow
            });
        }
    });
    return JSON.stringify(clips, null, 2);
})()
""")
        clips_data = json.loads(clips_result)

        # === timeline-section parent chain ===
        timeline_result = await page.evaluate("""
(function() {
    const timeline = document.querySelector('.timeline-section');
    if (timeline) {
        let el = timeline;
        const chain = [];
        while (el && el !== document.body) {
            const s = window.getComputedStyle(el);
            chain.push({
                tag: el.tagName,
                class: el.className.substring(0, 80),
                display: s.display,
                overflow: s.overflow,
                height: el.getBoundingClientRect().height,
                maxHeight: s.maxHeight,
                visibility: s.visibility,
                opacity: s.opacity
            });
            el = el.parentElement;
        }
        return JSON.stringify(chain, null, 2);
    } else {
        const similar = Array.from(document.querySelectorAll('[class*="timeline"],[class*="what-happens"],[class*="next-steps"]')).map(e => ({
            class: e.className.substring(0, 80),
            tag: e.tagName,
            h: Math.round(e.getBoundingClientRect().height),
            display: window.getComputedStyle(e).display,
            visibility: window.getComputedStyle(e).visibility
        }));
        return JSON.stringify({error: 'timeline-section not found', similar: similar});
    }
})()
""")

        # === hidden sections/divs ===
        hidden_result = await page.evaluate("""
(function() {
    const hidden = [];
    document.querySelectorAll('section, div[class*="section"], div[class*="timeline"], div[class*="what-happens"], div[class*="step"]').forEach(el => {
        const s = window.getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        if (s.display === 'none' || s.visibility === 'hidden' || parseFloat(s.opacity) < 0.1 || rect.height === 0) {
            hidden.push({
                tag: el.tagName,
                class: el.className.substring(0, 80),
                id: el.id,
                display: s.display,
                visibility: s.visibility,
                opacity: s.opacity,
                height: rect.height
            });
        }
    });
    return JSON.stringify(hidden, null, 2);
})()
""")
        hidden_data = json.loads(hidden_result)

        # === bottom of page ===
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)
        ss5 = SCREENSHOT_DIR / "V5-05-page-bottom.png"
        await safe_screenshot(page, ss5)

        final_info = json.loads(await page.evaluate("""
JSON.stringify({
    scrollHeight: document.body.scrollHeight,
    clientHeight: document.documentElement.clientHeight,
    scrollY: window.scrollY,
    sectionCount: document.querySelectorAll('section').length
})
"""))

        # === PRINT FULL REPORT ===
        print(f"\n{'='*65}")
        print(f"SECTION VISIBILITY ({len(sections_data)} sections)")
        print('='*65)
        for s in sections_data:
            flags = []
            if s["display"] == "none": flags.append("display:none")
            if s["visibility"] == "hidden": flags.append("vis:hidden")
            try:
                if float(s["opacity"]) < 0.1: flags.append(f"op:{s['opacity']}")
            except:
                pass
            if s["height"] == 0: flags.append("h:0")
            if s["maxHeight"] not in ["none", "", "0px"]: flags.append(f"maxH:{s['maxHeight']}")
            status = "HIDDEN: " + ", ".join(flags) if flags else "VISIBLE"
            print(f"  [{s['index']:2d}] top={s['top']:6d}px h={s['height']:7.1f}px | {status}")
            print(f"       cls='{s['class'][:70]}' id='{s['id']}'")

        print(f"\nOVERFLOW:HIDDEN CLIPS ({len(clips_data)} elements)")
        print('='*65)
        for c in clips_data[:25]:
            print(f"  <{c['tag']}> cls='{c['class'][:50]}' clientH={c['clientHeight']} scrollH={c['scrollHeight']}")

        print(f"\nTIMELINE-SECTION PARENT CHAIN")
        print('='*65)
        print(timeline_result[:3000])

        print(f"\nHIDDEN SECTIONS/DIVS ({len(hidden_data)})")
        print('='*65)
        for h in hidden_data:
            print(f"  {h['tag']} cls='{h['class'][:60]}' display={h['display']} vis={h['visibility']} h={h['height']}")

        print(f"\nFINAL PAGE INFO: {json.dumps(final_info)}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
