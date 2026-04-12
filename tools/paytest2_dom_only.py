#!/usr/bin/env python3
"""
pay-test-2 DOM-only audit (no full-page screenshots)
Gets all DOM data then takes quick viewport screenshots.
"""

import asyncio
import json
import requests
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/paytest2-visibility-audit")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

URL = "https://purebrain.ai/pay-test-2/"
PASSWORD = "PureBrain.ai253443$$$"

def get_wp_cookies():
    session = requests.Session()
    session.headers['User-Agent'] = 'Mozilla/5.0'
    session.post('https://purebrain.ai/wp-login.php?action=postpass',
                 data={'post_password': PASSWORD}, timeout=20, allow_redirects=True)
    return [{"name": c.name, "value": c.value, "domain": "purebrain.ai", "path": c.path or "/"} for c in session.cookies]

async def run():
    cookies = get_wp_cookies()
    print(f"Cookies: {[c['name'] for c in cookies]}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage",
                  "--disable-font-subpixel-positioning", "--font-render-hinting=none",
                  "--disable-gpu"]
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            # Disable CSS transitions/animations that might affect screenshots
        )
        await context.add_cookies(cookies)
        page = await context.new_page()

        # Block fonts to avoid screenshot timeout
        await page.route("**/*.woff*", lambda route: route.abort())
        await page.route("**/*.ttf", lambda route: route.abort())

        print(f"Navigating to {URL}")
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        scroll_h = await page.evaluate("document.body.scrollHeight")
        sections_n = await page.evaluate("document.querySelectorAll('section').length")
        print(f"scrollH={scroll_h}, sections={sections_n}")

        if scroll_h < 5000:
            print("LOCKED")
            await browser.close()
            return

        # === ALL DOM QUERIES FIRST ===

        # 1. All sections
        sections_data = json.loads(await page.evaluate("""
(function() {
    const allSections = document.querySelectorAll('section');
    const results = [];
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

        # 2. Overflow hidden clips
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

        # 3. Timeline section parent chain
        timeline_raw = await page.evaluate("""
(function() {
    var timeline = document.querySelector('.timeline-section');
    if (!timeline) {
        var similar = [];
        document.querySelectorAll('[class*="timeline"],[class*="what-happens"],[class*="next"]').forEach(function(e) {
            similar.push({cls: e.className.substring(0,80), tag: e.tagName, h: Math.round(e.getBoundingClientRect().height), display: window.getComputedStyle(e).display});
        });
        return JSON.stringify({error: 'not found', similar: similar.slice(0,10)});
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

        # 4. Hidden elements
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

        final_info = json.loads(await page.evaluate("""
JSON.stringify({scrollHeight: document.body.scrollHeight, sections: document.querySelectorAll('section').length})
"""))

        # === SCREENSHOTS (viewport only, no font waiting) ===
        positions = [
            ("01-top", 0),
            ("02-mid", 3000),
            ("03-whn-area", 5000),
            ("04-bottom", -1),
        ]

        for name, scroll_pos in positions:
            if scroll_pos == -1:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            else:
                await page.evaluate(f"window.scrollTo(0, {scroll_pos})")
            await page.wait_for_timeout(500)

            # Also find WHN for position 2
            if name == "02-mid":
                whn_scroll = await page.evaluate("""
(function() {
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var node;
    while (node = walker.nextNode()) {
        if (node.textContent && node.textContent.toUpperCase().includes('WHAT HAPPENS NEXT')) {
            node.parentElement.scrollIntoView({behavior: 'instant', block: 'start'});
            return window.scrollY;
        }
    }
    return -1;
})()
""")
                print(f"WHN scrollY: {whn_scroll}")
                await page.wait_for_timeout(300)

            path = SCREENSHOT_DIR / f"FINAL-{name}.png"
            try:
                await page.screenshot(path=str(path), full_page=False, timeout=8000)
                print(f"Screenshot: {path.name}")
            except Exception as e:
                print(f"Screenshot FAILED {name}: {str(e)[:80]}")

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
            print(f"Error parsing timeline: {e}")
            print(timeline_raw[:2000])

        print(f"\n{'='*70}")
        print(f"HIDDEN SECTIONS/DIVS — {len(hidden_data)}")
        print('='*70)
        for h in hidden_data:
            print(f"  {h['tag']} cls='{h['class'][:60]}' display={h['display']} vis={h['visibility']} h={h['height']}")

        print(f"\nFINAL: {final_info}")

if __name__ == "__main__":
    asyncio.run(run())
