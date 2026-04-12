#!/usr/bin/env python3
"""
pay-test-2 local audit
Loads the saved HTML file locally (no network), runs DOM analysis + screenshots.
Fast because no font/network timeouts.
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/paytest2-visibility-audit")
HTML_FILE = SCREENSHOT_DIR / "pay-test-2-unlocked.html"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
                  "--allow-file-access-from-files"]
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
        )
        page = await context.new_page()

        # Load local file
        local_url = f"file://{HTML_FILE}"
        print(f"Loading: {local_url}")
        await page.goto(local_url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(1000)

        scroll_h = await page.evaluate("document.body.scrollHeight")
        sections_n = await page.evaluate("document.querySelectorAll('section').length")
        print(f"scrollH={scroll_h}, sections={sections_n}")

        # Quick viewport screenshot at top
        ss1 = SCREENSHOT_DIR / "LOCAL-01-top.png"
        await page.screenshot(path=str(ss1), full_page=False, timeout=10000)
        print(f"SS1: {ss1.name}")

        # Scroll to WHN
        whn = await page.evaluate("""
(function() {
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var node;
    while (node = walker.nextNode()) {
        var txt = node.textContent || '';
        if (txt.toUpperCase().includes('WHAT HAPPENS NEXT')) {
            var el = node.parentElement;
            el.scrollIntoView({behavior: 'instant', block: 'start'});
            return {found: true, tag: el.tagName, cls: el.className.substring(0,80), scrollY: window.scrollY};
        }
    }
    return {found: false};
})()
""")
        print(f"WHN: {whn}")
        await page.wait_for_timeout(300)

        ss2 = SCREENSHOT_DIR / "LOCAL-02-whn.png"
        await page.screenshot(path=str(ss2), full_page=False, timeout=10000)
        print(f"SS2: {ss2.name}")

        await page.evaluate("window.scrollBy(0, 600)")
        await page.wait_for_timeout(300)
        ss3 = SCREENSHOT_DIR / "LOCAL-03-below-600.png"
        await page.screenshot(path=str(ss3), full_page=False, timeout=10000)
        print(f"SS3: {ss3.name}")

        await page.evaluate("window.scrollBy(0, 700)")
        await page.wait_for_timeout(300)
        ss4 = SCREENSHOT_DIR / "LOCAL-04-below-1300.png"
        await page.screenshot(path=str(ss4), full_page=False, timeout=10000)
        print(f"SS4: {ss4.name}")

        await page.evaluate("window.scrollBy(0, 700)")
        await page.wait_for_timeout(300)
        ss5 = SCREENSHOT_DIR / "LOCAL-05-below-2000.png"
        await page.screenshot(path=str(ss5), full_page=False, timeout=10000)
        print(f"SS5: {ss5.name}")

        # DOM QUERIES
        sections_data = json.loads(await page.evaluate("""
(function() {
    var allSections = document.querySelectorAll('section');
    var results = [];
    allSections.forEach(function(s, i) {
        var rect = s.getBoundingClientRect();
        var styles = window.getComputedStyle(s);
        results.push({
            index: i,
            class: s.className.substring(0, 80),
            id: s.id,
            display: styles.display,
            visibility: styles.visibility,
            opacity: styles.opacity,
            height: Math.round(rect.height),
            top: Math.round(rect.top + window.scrollY),
            overflow: styles.overflow,
            maxHeight: styles.maxHeight,
            position: styles.position
        });
    });
    return JSON.stringify(results);
})()
"""))

        clips_data = json.loads(await page.evaluate("""
(function() {
    var clips = [];
    document.querySelectorAll('*').forEach(function(el) {
        var s = window.getComputedStyle(el);
        if (s.overflow === 'hidden' && el.scrollHeight > el.clientHeight + 10) {
            clips.push({
                tag: el.tagName,
                class: el.className.substring(0, 60),
                id: el.id,
                clientHeight: el.clientHeight,
                scrollHeight: el.scrollHeight
            });
        }
    });
    return JSON.stringify(clips);
})()
"""))

        timeline_raw = await page.evaluate("""
(function() {
    var timeline = document.querySelector('.timeline-section');
    if (!timeline) {
        var similar = [];
        document.querySelectorAll('[class*="timeline"],[class*="what-happens"],[class*="next"]').forEach(function(e) {
            similar.push({cls: e.className.substring(0,80), tag: e.tagName, h: Math.round(e.getBoundingClientRect().height), display: window.getComputedStyle(e).display});
        });
        return JSON.stringify({error: 'not found', similar: similar.slice(0,15)});
    }
    var el = timeline;
    var chain = [];
    while (el && el !== document.body) {
        var s = window.getComputedStyle(el);
        chain.push({
            tag: el.tagName,
            class: el.className.substring(0, 80),
            display: s.display,
            overflow: s.overflow,
            height: Math.round(el.getBoundingClientRect().height),
            maxHeight: s.maxHeight,
            visibility: s.visibility,
            opacity: s.opacity
        });
        el = el.parentElement;
    }
    return JSON.stringify(chain);
})()
""")

        hidden_data = json.loads(await page.evaluate("""
(function() {
    var hidden = [];
    var sel = 'section, div[class*="section"], div[class*="timeline"], div[class*="what-happens"], div[class*="step"]';
    document.querySelectorAll(sel).forEach(function(el) {
        var s = window.getComputedStyle(el);
        var rect = el.getBoundingClientRect();
        if (s.display === 'none' || s.visibility === 'hidden' || parseFloat(s.opacity) < 0.1 || rect.height === 0) {
            hidden.push({
                tag: el.tagName,
                class: el.className.substring(0, 80),
                id: el.id,
                display: s.display,
                visibility: s.visibility,
                opacity: s.opacity,
                height: Math.round(rect.height)
            });
        }
    });
    return JSON.stringify(hidden);
})()
"""))

        # Scroll to page bottom screenshot
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(300)
        ss6 = SCREENSHOT_DIR / "LOCAL-06-bottom.png"
        await page.screenshot(path=str(ss6), full_page=False, timeout=10000)
        print(f"SS6: {ss6.name}")

        final_info = json.loads(await page.evaluate("""
JSON.stringify({scrollHeight: document.body.scrollHeight, sections: document.querySelectorAll('section').length, scrollY: window.scrollY})
"""))

        await browser.close()

        # === PRINT REPORT ===
        print(f"\n{'='*70}")
        print(f"SECTION VISIBILITY — {len(sections_data)} sections")
        print('='*70)
        for s in sections_data:
            flags = []
            if s["display"] == "none": flags.append("display:none")
            if s["visibility"] == "hidden": flags.append("vis:hidden")
            try:
                if float(s["opacity"]) < 0.1: flags.append(f"op:{s['opacity']}")
            except: pass
            if s["height"] == 0: flags.append("h:0")
            if s["maxHeight"] not in ["none", "", "0px"]: flags.append(f"maxH:{s['maxHeight']}")
            status = "*** HIDDEN: " + ", ".join(flags) + " ***" if flags else "VISIBLE"
            print(f"  [{s['index']:2d}] top={s['top']:6d}px h={s['height']:7d}px | {status}")
            print(f"       cls='{s['class'][:70]}' id='{s['id']}'")

        print(f"\n{'='*70}")
        print(f"OVERFLOW:HIDDEN CLIPS — {len(clips_data)}")
        print('='*70)
        for c in clips_data[:25]:
            print(f"  <{c['tag']}> cls='{c['class'][:50]}' clientH={c['clientHeight']} scrollH={c['scrollHeight']}")

        print(f"\n{'='*70}")
        print(f"TIMELINE-SECTION PARENT CHAIN")
        print('='*70)
        try:
            chain = json.loads(timeline_raw)
            if isinstance(chain, list):
                for i, item in enumerate(chain):
                    flags = []
                    if item["display"] == "none": flags.append("HIDDEN display:none")
                    if item["visibility"] == "hidden": flags.append("HIDDEN vis:hidden")
                    try:
                        if float(item["opacity"]) < 0.1: flags.append(f"HIDDEN op:{item['opacity']}")
                    except: pass
                    if item["height"] == 0: flags.append("HEIGHT:0")
                    if item["maxHeight"] not in ["none", "", "0px"]: flags.append(f"maxH:{item['maxHeight']}")
                    alert = " <-- PROBLEM!" if flags else ""
                    print(f"  [{i}] <{item['tag']}> h={item['height']}px ovf={item['overflow']} display={item['display']} vis={item['visibility']} maxH={item['maxHeight']}{alert}")
                    print(f"       cls='{item['class'][:70]}'")
            else:
                print(json.dumps(chain, indent=2))
        except Exception as e:
            print(f"Error: {e}")
            print(timeline_raw[:2000])

        print(f"\n{'='*70}")
        print(f"HIDDEN SECTIONS/DIVS — {len(hidden_data)}")
        print('='*70)
        for h in hidden_data:
            print(f"  {h['tag']} cls='{h['class'][:60]}' display={h['display']} vis={h['visibility']} h={h['height']}")

        print(f"\nFINAL: {final_info}")
        print(f"\nScreenshots: {SCREENSHOT_DIR}")

if __name__ == "__main__":
    asyncio.run(run())
