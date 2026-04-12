#!/usr/bin/env python3
"""
pay-test-2 visibility audit FINAL
Uses WP postpass cookie via requests, injects into Playwright context.
Full DOM analysis of sections below "What Happens Next".
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
    """Get the WP postpass cookie via HTTP POST"""
    session = requests.Session()
    session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

    # POST to WP password form endpoint
    resp = session.post(
        'https://purebrain.ai/wp-login.php?action=postpass',
        data={'post_password': PASSWORD},
        timeout=20,
        allow_redirects=True
    )
    print(f"[COOKIE] POST status: {resp.status_code}")
    print(f"[COOKIE] Cookies: {list(session.cookies.keys())}")

    # Convert requests cookies to Playwright format
    pw_cookies = []
    for cookie in session.cookies:
        pw_cookies.append({
            "name": cookie.name,
            "value": cookie.value,
            "domain": "purebrain.ai",
            "path": cookie.path or "/"
        })
    return pw_cookies

async def run():
    # Get cookies first
    cookies = get_wp_cookies()
    print(f"[COOKIE] Got {len(cookies)} cookies for Playwright injection")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--font-render-hinting=none"]
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )

        # Inject cookies BEFORE navigation
        await context.add_cookies(cookies)
        print(f"[PW] Cookies injected")

        page = await context.new_page()
        print(f"[PW] Navigating to {URL}")
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        # Verify page loaded correctly
        scroll_h = await page.evaluate("document.body.scrollHeight")
        sections_n = await page.evaluate("document.querySelectorAll('section').length")
        pwd_form = await page.locator('input[name="post_password"]').count()
        print(f"[PW] scrollH={scroll_h}, sections={sections_n}, pwd_form_present={pwd_form>0}")

        if scroll_h < 5000 or pwd_form > 0:
            print("[!] Page still locked or not loading properly")
            await page.screenshot(path=str(SCREENSHOT_DIR / "debug-locked.png"))
            await browser.close()
            return

        # === SCREENSHOT 1: Top of page ===
        ss1 = SCREENSHOT_DIR / "FINAL-01-top.png"
        try:
            await page.screenshot(path=str(ss1), full_page=False, timeout=15000)
            print(f"Screenshot 1: {ss1.name}")
        except Exception as e:
            print(f"SS1 failed: {e}")

        # === Scroll to "WHAT HAPPENS NEXT" ===
        whn_info = await page.evaluate("""
(function() {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node;
    while (node = walker.nextNode()) {
        const txt = node.textContent || '';
        if (txt.toUpperCase().includes('WHAT HAPPENS NEXT')) {
            const el = node.parentElement;
            el.scrollIntoView({behavior: 'instant', block: 'start'});
            return {
                found: true,
                tag: el.tagName,
                class: el.className.substring(0, 80),
                scrollY: window.scrollY,
                text: txt.trim().substring(0, 80)
            };
        }
    }
    return {found: false};
})()
""")
        print(f"[PW] WHN element: {whn_info}")
        await page.wait_for_timeout(800)

        ss2 = SCREENSHOT_DIR / "FINAL-02-what-happens-next.png"
        try:
            await page.screenshot(path=str(ss2), timeout=15000)
            print(f"Screenshot 2: {ss2.name}")
        except Exception as e:
            print(f"SS2 failed: {e}")

        # Scroll 600px further
        await page.evaluate("window.scrollBy(0, 600)")
        await page.wait_for_timeout(500)
        ss3 = SCREENSHOT_DIR / "FINAL-03-below-whn-600.png"
        try:
            await page.screenshot(path=str(ss3), timeout=15000)
            print(f"Screenshot 3: {ss3.name}")
        except Exception as e:
            print(f"SS3 failed: {e}")

        # Scroll 700px more
        await page.evaluate("window.scrollBy(0, 700)")
        await page.wait_for_timeout(500)
        ss4 = SCREENSHOT_DIR / "FINAL-04-below-whn-1300.png"
        try:
            await page.screenshot(path=str(ss4), timeout=15000)
            print(f"Screenshot 4: {ss4.name}")
        except Exception as e:
            print(f"SS4 failed: {e}")

        # === JS DIAGNOSTIC 1: All sections ===
        sections_data = json.loads(await page.evaluate("""
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
            height: Math.round(rect.height),
            top: Math.round(rect.top + window.scrollY),
            overflow: styles.overflow,
            maxHeight: styles.maxHeight,
            position: styles.position
        });
    });
    return JSON.stringify(results, null, 2);
})()
"""))

        # === JS DIAGNOSTIC 2: overflow:hidden clipping ===
        clips_data = json.loads(await page.evaluate("""
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
"""))

        # === JS DIAGNOSTIC 3: timeline-section parent chain ===
        timeline_raw = await page.evaluate("""
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
                height: Math.round(el.getBoundingClientRect().height),
                maxHeight: s.maxHeight,
                visibility: s.visibility,
                opacity: s.opacity
            });
            el = el.parentElement;
        }
        return JSON.stringify(chain, null, 2);
    }
    var similar = [];
    document.querySelectorAll('[class*="timeline"],[class*="what-happens"],[class*="next-steps"]').forEach(function(e) {
        similar.push({
            cls: e.className.substring(0,80),
            tag: e.tagName,
            h: Math.round(e.getBoundingClientRect().height),
            display: window.getComputedStyle(e).display,
            vis: window.getComputedStyle(e).visibility
        });
    });
    return JSON.stringify({error: 'timeline-section not found', similar: similar});
})()
""")

        # === JS DIAGNOSTIC 4: hidden sections ===
        hidden_data = json.loads(await page.evaluate("""
(function() {
    const hidden = [];
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
    return JSON.stringify(hidden, null, 2);
})()
"""))

        # === SCROLL TO BOTTOM ===
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)
        ss5 = SCREENSHOT_DIR / "FINAL-05-bottom.png"
        try:
            await page.screenshot(path=str(ss5), timeout=15000)
            print(f"Screenshot 5: {ss5.name}")
        except Exception as e:
            print(f"SS5 failed: {e}")

        final_info = json.loads(await page.evaluate("""
JSON.stringify({
    scrollHeight: document.body.scrollHeight,
    clientHeight: document.documentElement.clientHeight,
    scrollY: window.scrollY,
    sectionCount: document.querySelectorAll('section').length
})
"""))

        # === PRINT FULL REPORT ===
        print(f"\n{'='*70}")
        print(f"SECTION VISIBILITY REPORT — {len(sections_data)} sections total")
        print('='*70)
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
            status = "*** HIDDEN: " + ", ".join(flags) + " ***" if flags else "VISIBLE"
            print(f"  [{s['index']:2d}] top={s['top']:6d}px h={s['height']:7d}px | {status}")
            print(f"       cls='{s['class'][:70]}' id='{s['id']}'")

        print(f"\n{'='*70}")
        print(f"OVERFLOW:HIDDEN CLIPS — {len(clips_data)} elements clipping content")
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
                    except:
                        pass
                    if item["height"] == 0: flags.append("HEIGHT:0")
                    if item["maxHeight"] not in ["none", "", "0px"]: flags.append(f"maxH:{item['maxHeight']}")
                    alert = " <-- PROBLEM!" if flags else ""
                    print(f"  [{i}] <{item['tag']}> h={item['height']}px overflow={item['overflow']} display={item['display']} maxH={item['maxHeight']}")
                    print(f"       cls='{item['class'][:70]}'{alert}")
                    if flags:
                        print(f"       FLAGS: {', '.join(flags)}")
            else:
                print(json.dumps(chain, indent=2))
        except:
            print(timeline_raw[:2000])

        print(f"\n{'='*70}")
        print(f"HIDDEN SECTIONS/DIVS — {len(hidden_data)} hidden")
        print('='*70)
        for h in hidden_data:
            print(f"  {h['tag']} cls='{h['class'][:60]}' display={h['display']} vis={h['visibility']} h={h['height']}")

        print(f"\nFINAL PAGE INFO: {json.dumps(final_info)}")
        print(f"\nScreenshots saved in: {SCREENSHOT_DIR}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
