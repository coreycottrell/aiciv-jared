#!/usr/bin/env python3
"""
pay-test-2 visibility audit
Checks why content below "What Happens Next" is not visible.
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/paytest2-visibility-audit")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

URL = "https://purebrain.ai/pay-test-2/"
PASSWORD = "PureBrain.ai253443$$"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # === STEP 1: Navigate ===
        print(f"[1] Navigating to {URL}")
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        # === STEP 2: Password form ===
        pwd_input = page.locator('input[id^="pwbox-"]')
        if await pwd_input.count() > 0:
            print("[2] Password form detected — entering password")
            await pwd_input.fill(PASSWORD)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(3000)
            print("[2] Password submitted")
        else:
            print("[2] No password form — page may already be accessible")

        # === STEP 3: Full page screenshot ===
        print("[3] Taking full page screenshot")
        await page.wait_for_timeout(2000)
        ss1 = SCREENSHOT_DIR / "01-full-page.png"
        await page.screenshot(path=str(ss1), full_page=True)
        print(f"[3] Screenshot saved: {ss1}")

        # === STEP 4: Scroll to What Happens Next ===
        print("[4] Scrolling to 'What Happens Next' area")
        await page.evaluate("""
            const els = document.querySelectorAll('h1,h2,h3,h4,h5,h6,p,div');
            for (const el of els) {
                if (el.textContent && el.textContent.toUpperCase().includes('WHAT HAPPENS NEXT')) {
                    el.scrollIntoView({behavior: 'instant', block: 'start'});
                    break;
                }
            }
        """)
        await page.wait_for_timeout(1000)
        ss2 = SCREENSHOT_DIR / "02-what-happens-next.png"
        await page.screenshot(path=str(ss2))
        print(f"[4] Screenshot saved: {ss2}")

        # Scroll down more to see what follows
        await page.evaluate("window.scrollBy(0, 600)")
        await page.wait_for_timeout(500)
        ss3 = SCREENSHOT_DIR / "03-below-what-happens-next.png"
        await page.screenshot(path=str(ss3))
        print(f"[4b] Screenshot saved: {ss3}")

        # === STEP 5: DOM visibility of all sections ===
        print("[5] Running section visibility JS")
        sections_js = """
const allSections = document.querySelectorAll('section');
const results = [];
allSections.forEach((s, i) => {
    const rect = s.getBoundingClientRect();
    const styles = window.getComputedStyle(s);
    results.push({
        index: i,
        class: s.className.substring(0, 60),
        id: s.id,
        display: styles.display,
        visibility: styles.visibility,
        opacity: styles.opacity,
        height: rect.height,
        top: rect.top,
        overflow: styles.overflow,
        maxHeight: styles.maxHeight
    });
});
JSON.stringify(results, null, 2);
"""
        sections_result = await page.evaluate(sections_js)
        sections_data = json.loads(sections_result)
        print(f"[5] Found {len(sections_data)} sections")

        # === STEP 6: overflow:hidden elements clipping content ===
        print("[6] Checking overflow:hidden clipping elements")
        clips_js = """
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
JSON.stringify(clips, null, 2);
"""
        clips_result = await page.evaluate(clips_js)
        clips_data = json.loads(clips_result)
        print(f"[6] Found {len(clips_data)} overflow:hidden clipping elements")

        # === STEP 7: timeline-section parent chain ===
        print("[7] Checking .timeline-section parent chain")
        timeline_js = """
const timeline = document.querySelector('.timeline-section');
if (timeline) {
    let el = timeline;
    const chain = [];
    while (el && el !== document.body) {
        const s = window.getComputedStyle(el);
        chain.push({
            tag: el.tagName,
            class: el.className.substring(0, 60),
            display: s.display,
            overflow: s.overflow,
            height: el.getBoundingClientRect().height,
            maxHeight: s.maxHeight
        });
        el = el.parentElement;
    }
    JSON.stringify(chain, null, 2);
} else {
    '"timeline-section not found"';
}
"""
        timeline_result = await page.evaluate(timeline_js)
        print(f"[7] Timeline chain result: {timeline_result[:200]}...")

        # === STEP 8: Extra diagnostics — all hidden elements ===
        print("[8] Checking display:none / visibility:hidden elements")
        hidden_js = """
const hidden = [];
document.querySelectorAll('section, div[class*="section"], div[class*="timeline"], div[class*="what-happens"]').forEach(el => {
    const s = window.getComputedStyle(el);
    if (s.display === 'none' || s.visibility === 'hidden' || s.opacity === '0') {
        hidden.push({
            tag: el.tagName,
            class: el.className.substring(0, 80),
            id: el.id,
            display: s.display,
            visibility: s.visibility,
            opacity: s.opacity
        });
    }
});
JSON.stringify(hidden, null, 2);
"""
        hidden_result = await page.evaluate(hidden_js)
        hidden_data = json.loads(hidden_result)
        print(f"[8] Found {len(hidden_data)} hidden section/div elements")

        # === STEP 9: page height and scroll position info ===
        page_info = await page.evaluate("""
JSON.stringify({
    scrollHeight: document.body.scrollHeight,
    clientHeight: document.documentElement.clientHeight,
    scrollY: window.scrollY,
    innerHeight: window.innerHeight
})
""")

        # === STEP 10: console logs ===
        console_msgs = []
        page.on("console", lambda msg: console_msgs.append({"type": msg.type, "text": msg.text}))

        # Scroll to very bottom to force reveal
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1500)
        ss4 = SCREENSHOT_DIR / "04-page-bottom.png"
        await page.screenshot(path=str(ss4))
        print(f"[9] Bottom screenshot saved: {ss4}")

        # === WRITE REPORT ===
        report = {
            "url": URL,
            "timestamp": datetime.now().isoformat(),
            "sections": sections_data,
            "overflow_hidden_clips": clips_data,
            "timeline_parent_chain": timeline_result,
            "hidden_elements": hidden_data,
            "page_info": json.loads(page_info),
            "screenshots": [
                str(ss1), str(ss2), str(ss3), str(ss4)
            ]
        }

        report_path = SCREENSHOT_DIR / "visibility-report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n[DONE] Report saved: {report_path}")

        # Print key findings to console
        print("\n=== SECTION VISIBILITY SUMMARY ===")
        for s in sections_data:
            status = "OK"
            flags = []
            if s["display"] == "none":
                flags.append("display:none")
            if s["visibility"] == "hidden":
                flags.append("visibility:hidden")
            if s["opacity"] == "0":
                flags.append("opacity:0")
            if s["height"] == 0:
                flags.append("height:0")
            if s["maxHeight"] not in ["none", ""]:
                flags.append(f"max-height:{s['maxHeight']}")
            if flags:
                status = "HIDDEN: " + ", ".join(flags)
            print(f"  [{s['index']}] cls={s['class'][:40]} id={s['id']} | {status}")

        print(f"\n=== OVERFLOW:HIDDEN CLIPPING ({len(clips_data)} elements) ===")
        for c in clips_data[:20]:
            print(f"  <{c['tag']}> cls={c['class'][:40]} | client={c['clientHeight']} scroll={c['scrollHeight']}")

        print(f"\n=== TIMELINE PARENT CHAIN ===")
        print(timeline_result[:2000])

        print(f"\n=== HIDDEN SECTION/DIV ELEMENTS ({len(hidden_data)}) ===")
        for h in hidden_data:
            print(f"  <{h['tag']}> cls={h['class'][:60]} | display={h['display']} vis={h['visibility']} op={h['opacity']}")

        print(f"\n=== PAGE INFO ===")
        print(page_info)

        await browser.close()
        return report

if __name__ == "__main__":
    asyncio.run(run())
