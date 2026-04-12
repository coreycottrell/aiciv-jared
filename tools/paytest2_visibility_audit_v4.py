#!/usr/bin/env python3
"""
pay-test-2 visibility audit v4
Correct password: PureBrain.ai253443$$$  (THREE dollar signs)
Uses direct Playwright with correct password submission.
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/paytest2-visibility-audit")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

URL = "https://purebrain.ai/pay-test-2/"
PASSWORD = "PureBrain.ai253443$$$"

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

        # === Navigate ===
        print(f"[1] Navigating to {URL}")
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        # === Enter password using type character by character to avoid escaping issues ===
        pwd_input = page.locator('input[name="post_password"], input[id^="pwbox-"]')
        count = await pwd_input.count()
        print(f"[2] Password inputs: {count}")

        if count > 0:
            # Use type instead of fill to avoid any escaping issues
            await pwd_input.first.click()
            await page.keyboard.type(PASSWORD)
            await page.wait_for_timeout(500)

            # Verify what was typed
            typed_val = await pwd_input.first.input_value()
            print(f"[2] Typed value length: {len(typed_val)}, ends with: ...{typed_val[-5:]}")

            # Click submit
            submit = page.locator('input[type="submit"]')
            print(f"[2] Submit buttons: {await submit.count()}")
            await submit.first.click()

            # Wait for navigation
            await page.wait_for_load_state("domcontentloaded", timeout=15000)
            await page.wait_for_timeout(3000)

            # Check if password form is gone
            pwd_check = await page.locator('input[name="post_password"]').count()
            page_title = await page.title()
            scroll_h = await page.evaluate("document.body.scrollHeight")
            print(f"[2] After submit: pwd_form={pwd_check>0}, title={page_title}, scrollH={scroll_h}")

        # === Screenshot after password ===
        ss_after = SCREENSHOT_DIR / "V4-01-after-password.png"
        await page.screenshot(path=str(ss_after), full_page=False)
        print(f"[3] Screenshot: {ss_after}")

        # Check scrollHeight
        scroll_info = await page.evaluate("""
JSON.stringify({
    scrollHeight: document.body.scrollHeight,
    sectionCount: document.querySelectorAll('section').length,
    url: window.location.href,
    bodyPreview: document.body.innerHTML.substring(0, 200)
})
""")
        info = json.loads(scroll_info)
        print(f"[3] ScrollH: {info['scrollHeight']}, Sections: {info['sectionCount']}")
        print(f"[3] Body preview: {info['bodyPreview'][:150]}")

        if info['scrollHeight'] < 5000:
            print("[!] Page still showing password form or not loading. Trying networkidle wait...")
            await page.wait_for_load_state("networkidle", timeout=20000)
            await page.wait_for_timeout(2000)
            scroll_info2 = await page.evaluate("JSON.stringify({scrollHeight: document.body.scrollHeight, sectionCount: document.querySelectorAll('section').length})")
            print(f"[3b] After networkidle: {scroll_info2}")

        # === Full page screenshot ===
        await page.wait_for_timeout(2000)
        ss_full = SCREENSHOT_DIR / "V4-02-full-page.png"
        await page.screenshot(path=str(ss_full), full_page=True)
        print(f"[4] Full page screenshot: {ss_full}")

        final_scroll = await page.evaluate("document.body.scrollHeight")
        print(f"[4] Final scrollHeight: {final_scroll}")

        if final_scroll < 5000:
            print("[!] Page content still not loading. Checking HTML...")
            html_preview = await page.evaluate("document.body.innerHTML.substring(0, 1000)")
            print(f"HTML: {html_preview}")
            await browser.close()
            return

        # === Scroll to What Happens Next ===
        whn = await page.evaluate("""
(function() {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node;
    while (node = walker.nextNode()) {
        if (node.textContent && node.textContent.toUpperCase().includes('WHAT HAPPENS NEXT')) {
            const el = node.parentElement;
            el.scrollIntoView({behavior: 'instant', block: 'start'});
            return {
                found: true,
                tag: el.tagName,
                class: el.className.substring(0, 80),
                scrollY: window.scrollY
            };
        }
    }
    return {found: false};
})()
""")
        print(f"[5] What Happens Next element: {whn}")
        await page.wait_for_timeout(800)

        ss_whn = SCREENSHOT_DIR / "V4-03-what-happens-next.png"
        await page.screenshot(path=str(ss_whn))
        print(f"[5] WHN screenshot: {ss_whn}")

        # Scroll down 700px more to see what's below
        await page.evaluate("window.scrollBy(0, 700)")
        await page.wait_for_timeout(500)
        ss_below = SCREENSHOT_DIR / "V4-04-below-whn.png"
        await page.screenshot(path=str(ss_below))

        # More scrolling
        await page.evaluate("window.scrollBy(0, 700)")
        await page.wait_for_timeout(500)
        ss_below2 = SCREENSHOT_DIR / "V4-05-below-whn-2.png"
        await page.screenshot(path=str(ss_below2))

        # === ALL SECTIONS DOM ANALYSIS ===
        sections_js = """
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
JSON.stringify(results, null, 2);
"""
        sections_data = json.loads(await page.evaluate(sections_js))

        # === OVERFLOW:HIDDEN CLIPPING ===
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
        clips_data = json.loads(await page.evaluate(clips_js))

        # === TIMELINE-SECTION PARENT CHAIN ===
        timeline_js = """
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
    JSON.stringify(chain, null, 2);
} else {
    const similar = Array.from(document.querySelectorAll('[class*="timeline"],[class*="what-happens"],[class*="next-steps"]')).map(e => ({class: e.className.substring(0,80), tag: e.tagName, h: e.getBoundingClientRect().height}));
    JSON.stringify({error: 'timeline-section not found', similar: similar});
}
"""
        timeline_result = await page.evaluate(timeline_js)

        # === HIDDEN SECTIONS ===
        hidden_js = """
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
JSON.stringify(hidden, null, 2);
"""
        hidden_data = json.loads(await page.evaluate(hidden_js))

        # === PAGE BOTTOM ===
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)
        ss_bottom = SCREENSHOT_DIR / "V4-06-bottom.png"
        await page.screenshot(path=str(ss_bottom))

        final_info = await page.evaluate("""
JSON.stringify({
    scrollHeight: document.body.scrollHeight,
    clientHeight: document.documentElement.clientHeight,
    scrollY: window.scrollY,
    sectionCount: document.querySelectorAll('section').length
})
""")

        # === PRINT REPORT ===
        print(f"\n{'='*60}")
        print(f"SECTIONS ({len(sections_data)} total)")
        print('='*60)
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
            print(f"  [{s['index']}] top={s['top']:6d}px h={s['height']:7.1f}px | {status}")
            print(f"         cls={s['class'][:70]} id={s['id']}")

        print(f"\nOVERFLOW:HIDDEN CLIPS ({len(clips_data)})")
        print('='*60)
        for c in clips_data[:20]:
            print(f"  <{c['tag']}> cls={c['class'][:50]} client={c['clientHeight']} scroll={c['scrollHeight']}")

        print(f"\nTIMELINE SECTION CHAIN")
        print('='*60)
        print(timeline_result[:3000])

        print(f"\nHIDDEN SECTIONS/DIVS ({len(hidden_data)})")
        print('='*60)
        for h in hidden_data:
            print(f"  {h['tag']} cls={h['class'][:60]} display={h['display']} vis={h['visibility']} h={h['height']}")

        print(f"\nFINAL: {final_info}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
