#!/usr/bin/env python3
"""
pay-test-2 visibility audit v2
Handles WordPress password-protected page correctly via form submit button click.
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

        # Check page state
        title = await page.title()
        print(f"[1] Page title: {title}")

        # Screenshot of password form
        ss0 = SCREENSHOT_DIR / "00-password-form.png"
        await page.screenshot(path=str(ss0))
        print(f"[1] Password form screenshot: {ss0}")

        # === STEP 2: Find password input and submit button ===
        pwd_input = page.locator('input[name="post_password"], input[id^="pwbox-"], input[type="password"]')
        count = await pwd_input.count()
        print(f"[2] Password inputs found: {count}")

        if count > 0:
            print("[2] Filling password field")
            await pwd_input.first.fill(PASSWORD)
            await page.wait_for_timeout(500)

            # Click the submit button (WordPress uses input[type=submit])
            submit = page.locator('input[type="submit"], button[type="submit"], input.button, .post-password-form input[type="submit"]')
            submit_count = await submit.count()
            print(f"[2] Submit buttons found: {submit_count}")

            if submit_count > 0:
                print("[2] Clicking submit button")
                await submit.first.click()
            else:
                print("[2] No submit button — trying form submit via JS")
                await page.evaluate("document.querySelector('form.post-password-form, form[action*=\"wp-login\"]')?.submit()")

            # Wait for navigation after password submission
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=10000)
                await page.wait_for_timeout(3000)
            except Exception as e:
                print(f"[2] Wait after submit: {e}")

            title2 = await page.title()
            print(f"[2] Page title after submit: {title2}")

            # Check if password form is gone
            pwd_check = await page.locator('input[name="post_password"]').count()
            print(f"[2] Password form still present: {pwd_check > 0}")

        # === STEP 3: Screenshot after password ===
        ss1 = SCREENSHOT_DIR / "01-after-password.png"
        await page.screenshot(path=str(ss1))
        print(f"[3] After-password screenshot: {ss1}")

        # Check what's in the DOM
        body_html_preview = await page.evaluate("document.body.innerHTML.substring(0, 500)")
        print(f"[3] Body HTML preview: {body_html_preview[:300]}")

        # Check page dimensions
        page_info_basic = await page.evaluate("""
JSON.stringify({
    scrollHeight: document.body.scrollHeight,
    clientHeight: document.documentElement.clientHeight,
    innerHeight: window.innerHeight,
    title: document.title,
    url: window.location.href
})
""")
        print(f"[3] Page info: {page_info_basic}")

        # If page is still showing password form, try direct approach
        current_url = await page.evaluate("window.location.href")
        print(f"[3] Current URL: {current_url}")

        # === STEP 4: Full page screenshot ===
        print("[4] Taking full page screenshot (full_page=True)")
        ss_full = SCREENSHOT_DIR / "02-full-page.png"
        await page.screenshot(path=str(ss_full), full_page=True)
        print(f"[4] Full page screenshot: {ss_full}")

        # === STEP 5: Scroll to What Happens Next ===
        what_happens_scroll = await page.evaluate("""
(function() {
    const els = document.querySelectorAll('*');
    for (const el of els) {
        const text = el.textContent || '';
        if (text.toUpperCase().includes('WHAT HAPPENS NEXT') && el.children.length < 5) {
            el.scrollIntoView({behavior: 'instant', block: 'start'});
            return {found: true, tag: el.tagName, class: el.className, text: text.substring(0, 100)};
        }
    }
    return {found: false};
})()
""")
        print(f"[5] What Happens Next scroll: {what_happens_scroll}")
        await page.wait_for_timeout(1000)

        ss_whn = SCREENSHOT_DIR / "03-what-happens-next.png"
        await page.screenshot(path=str(ss_whn))
        print(f"[5] What Happens Next screenshot: {ss_whn}")

        # Scroll down 600px more to see what follows
        await page.evaluate("window.scrollBy(0, 700)")
        await page.wait_for_timeout(500)
        ss_below = SCREENSHOT_DIR / "04-below-whn.png"
        await page.screenshot(path=str(ss_below))
        print(f"[5b] Below Whn screenshot: {ss_below}")

        # === STEP 6: All section DOM analysis ===
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
        top: rect.top,
        overflow: styles.overflow,
        maxHeight: styles.maxHeight,
        position: styles.position
    });
});
JSON.stringify(results, null, 2);
"""
        sections_result = await page.evaluate(sections_js)
        sections_data = json.loads(sections_result)
        print(f"\n[6] Total sections in DOM: {len(sections_data)}")

        # === STEP 7: overflow:hidden clipping ===
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

        # === STEP 8: timeline-section parent chain ===
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
            visibility: s.visibility
        });
        el = el.parentElement;
    }
    JSON.stringify(chain, null, 2);
} else {
    JSON.stringify({error: 'timeline-section not found', allClasses: Array.from(document.querySelectorAll('[class*="timeline"]')).map(e => e.className.substring(0,80))});
}
"""
        timeline_result = await page.evaluate(timeline_js)

        # === STEP 9: hidden elements ===
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
        hidden_result = await page.evaluate(hidden_js)
        hidden_data = json.loads(hidden_result)

        # === STEP 10: Find ALL content sections by text ===
        content_map_js = """
(function() {
    const sections = [];
    // Look for major content blocks
    const candidates = document.querySelectorAll('section, [class*="section"], [class*="block"], [class*="container"]');
    candidates.forEach(el => {
        const rect = el.getBoundingClientRect();
        const s = window.getComputedStyle(el);
        const text = el.textContent.replace(/\\s+/g, ' ').trim().substring(0, 80);
        if (text.length > 10) {
            sections.push({
                tag: el.tagName,
                class: el.className.substring(0, 60),
                id: el.id,
                text: text,
                height: Math.round(rect.height),
                top: Math.round(rect.top + window.scrollY),
                display: s.display,
                visibility: s.visibility,
                opacity: s.opacity
            });
        }
    });
    return JSON.stringify(sections.slice(0, 50), null, 2);
})()
"""
        content_map_result = await page.evaluate(content_map_js)
        content_map_data = json.loads(content_map_result)

        # === STEP 11: Page total height and scroll to bottom ===
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1500)
        ss_bottom = SCREENSHOT_DIR / "05-page-bottom.png"
        await page.screenshot(path=str(ss_bottom))
        print(f"[11] Bottom screenshot: {ss_bottom}")

        final_page_info = await page.evaluate("""
JSON.stringify({
    scrollHeight: document.body.scrollHeight,
    clientHeight: document.documentElement.clientHeight,
    scrollY: window.scrollY,
    innerHeight: window.innerHeight,
    url: window.location.href
})
""")

        # === SAVE REPORT ===
        report = {
            "url": URL,
            "timestamp": datetime.now().isoformat(),
            "sections_raw": sections_data,
            "overflow_hidden_clips": clips_data,
            "timeline_parent_chain": json.loads(timeline_result) if timeline_result.startswith('[') or timeline_result.startswith('{') else timeline_result,
            "hidden_elements": hidden_data,
            "content_map": content_map_data,
            "page_info_final": json.loads(final_page_info),
            "screenshots": {
                "password_form": str(ss0),
                "after_password": str(ss1),
                "full_page": str(ss_full),
                "what_happens_next": str(ss_whn),
                "below_whn": str(ss_below),
                "bottom": str(ss_bottom)
            }
        }

        report_path = SCREENSHOT_DIR / "visibility-report-v2.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        # === PRINT FINDINGS ===
        print("\n" + "="*60)
        print("SECTION VISIBILITY SUMMARY")
        print("="*60)
        for s in sections_data:
            flags = []
            if s["display"] == "none": flags.append("display:none")
            if s["visibility"] == "hidden": flags.append("visibility:hidden")
            if float(s["opacity"]) < 0.1: flags.append(f"opacity:{s['opacity']}")
            if s["height"] == 0: flags.append("height:0")
            if s["maxHeight"] not in ["none", "", "0px"]: flags.append(f"max-height:{s['maxHeight']}")
            status = "HIDDEN: " + ", ".join(flags) if flags else "VISIBLE"
            print(f"  [{s['index']}] {status} | cls={s['class'][:50]} id={s['id']}")

        print(f"\nOVERFLOW:HIDDEN CLIPPING ({len(clips_data)} elements)")
        print("="*60)
        for c in clips_data[:15]:
            print(f"  <{c['tag']}> cls={c['class'][:50]} | client={c['clientHeight']} scroll={c['scrollHeight']}")

        print(f"\nTIMELINE PARENT CHAIN")
        print("="*60)
        print(json.dumps(json.loads(timeline_result) if timeline_result.startswith('[') or timeline_result.startswith('{') else timeline_result, indent=2)[:2000])

        print(f"\nHIDDEN SECTION/DIV ELEMENTS ({len(hidden_data)})")
        print("="*60)
        for h in hidden_data:
            print(f"  <{h['tag']}> cls={h['class'][:60]} | display={h['display']} vis={h['visibility']} op={h['opacity']} h={h['height']}")

        print(f"\nCONTENT MAP (first 30 blocks)")
        print("="*60)
        for c in content_map_data[:30]:
            print(f"  top={c['top']:6d}px h={c['height']:6d}px | {c['display'][:10]} | {c['class'][:40]} | {c['text'][:60]}")

        print(f"\nFINAL PAGE INFO: {final_page_info}")
        print(f"\nReport: {report_path}")

        await browser.close()
        return report

if __name__ == "__main__":
    asyncio.run(run())
