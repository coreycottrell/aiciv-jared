#!/usr/bin/env python3
"""
pay-test-2 visibility audit v3
Uses WP REST API to fetch page HTML, then serves locally and runs Playwright on it.
Bypasses the WordPress password protection entirely.
Strategy from memory: sandbox2_playwright_qa.py
"""

import asyncio
import json
import os
import http.server
import threading
import requests
import base64
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/paytest2-visibility-audit")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# WP credentials from .env
WP_BASE = "https://purebrain.ai"
WP_USER = "purebrain@puremarketing.ai"
WP_APP_PASS = "41w3 xWWZ 11em UXgj hjAF sx2T"
PAGE_ID = 689  # pay-test-2

def fetch_page_content():
    """Fetch page HTML via WP REST API with auth"""
    auth = base64.b64encode(f"{WP_USER}:{WP_APP_PASS}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # Try rendered content first
    url = f"{WP_BASE}/wp-json/wp/v2/pages/{PAGE_ID}?context=edit&_fields=id,slug,title,content,link"
    print(f"[API] Fetching: {url}")
    resp = requests.get(url, headers=headers, timeout=30)
    print(f"[API] Status: {resp.status_code}")

    if resp.status_code == 200:
        data = resp.json()
        print(f"[API] Title: {data.get('title', {}).get('rendered', 'N/A')}")
        raw_html = data.get("content", {}).get("raw", "")
        rendered_html = data.get("content", {}).get("rendered", "")
        print(f"[API] Raw HTML length: {len(raw_html)}")
        print(f"[API] Rendered HTML length: {len(rendered_html)}")
        return data
    else:
        print(f"[API] Error: {resp.text[:500]}")
        return None

def get_full_page_via_cookie():
    """Get the actual rendered page via WP login cookie"""
    # Try WP login to get auth cookie
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    # Get login page first
    login_url = f"{WP_BASE}/wp-login.php"
    resp = session.get(login_url, timeout=30)
    print(f"[LOGIN] Status: {resp.status_code}")

    # Login
    WP_PASS = "ij34utJdGCOst1*RcSvubXjb"
    login_data = {
        "log": WP_USER,
        "pwd": WP_PASS,
        "wp-submit": "Log In",
        "redirect_to": "/wp-admin/",
        "testcookie": "1"
    }
    resp2 = session.post(login_url, data=login_data, timeout=30, allow_redirects=True)
    print(f"[LOGIN] After login status: {resp2.status_code}, URL: {resp2.url}")

    # Now fetch the pay-test-2 page
    page_url = f"{WP_BASE}/pay-test-2/"
    resp3 = session.get(page_url, timeout=30)
    print(f"[PAGE] Status: {resp3.status_code}, Content length: {len(resp3.text)}")

    if resp3.status_code == 200 and len(resp3.text) > 5000:
        html_path = SCREENSHOT_DIR / "pay-test-2-full.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(resp3.text)
        print(f"[PAGE] Saved to: {html_path}")
        return str(html_path), resp3.text
    else:
        print(f"[PAGE] Failed or too short. Preview: {resp3.text[:300]}")
        return None, None


async def run_playwright_audit(html_path=None, live_url=None, cookies=None):
    """Run Playwright against the page"""
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

        if live_url:
            # Use live URL with injected cookies
            print(f"[PW] Navigating to live URL: {live_url}")
            if cookies:
                # Set cookies before navigation
                cookie_list = []
                for name, value in cookies.items():
                    cookie_list.append({
                        "name": name,
                        "value": value,
                        "domain": "purebrain.ai",
                        "path": "/"
                    })
                await context.add_cookies(cookie_list)

            await page.goto(live_url, wait_until="domcontentloaded", timeout=30000)
        else:
            # Serve local file
            print(f"[PW] Loading local file: {html_path}")
            await page.goto(f"file://{html_path}", wait_until="domcontentloaded", timeout=30000)

        await page.wait_for_timeout(3000)

        # Check if password form is showing
        pwd_form = await page.locator('input[name="post_password"]').count()
        print(f"[PW] Password form present: {pwd_form > 0}")

        page_info_basic = await page.evaluate("""
JSON.stringify({
    scrollHeight: document.body.scrollHeight,
    url: window.location.href,
    title: document.title
})
""")
        print(f"[PW] Basic info: {page_info_basic}")

        # === Full page screenshot ===
        ss_full = SCREENSHOT_DIR / "PW-01-full-page.png"
        await page.screenshot(path=str(ss_full), full_page=True)
        print(f"[PW] Full page: {ss_full}")

        # === Scroll to What Happens Next ===
        whn = await page.evaluate("""
(function() {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node;
    while (node = walker.nextNode()) {
        if (node.textContent.toUpperCase().includes('WHAT HAPPENS NEXT')) {
            const el = node.parentElement;
            el.scrollIntoView({behavior: 'instant', block: 'start'});
            return {found: true, tag: el.tagName, class: el.className, text: node.textContent.substring(0,100)};
        }
    }
    return {found: false};
})()
""")
        print(f"[PW] What Happens Next: {whn}")
        await page.wait_for_timeout(500)

        ss_whn = SCREENSHOT_DIR / "PW-02-what-happens-next.png"
        await page.screenshot(path=str(ss_whn))

        await page.evaluate("window.scrollBy(0, 700)")
        await page.wait_for_timeout(500)
        ss_below = SCREENSHOT_DIR / "PW-03-below-whn.png"
        await page.screenshot(path=str(ss_below))

        # === DOM analysis ===
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
    JSON.stringify({
        error: 'timeline-section not found',
        similarClasses: Array.from(document.querySelectorAll('[class*="timeline"],[class*="what-happens"],[class*="next-steps"]')).map(e => ({class: e.className.substring(0,80), tag: e.tagName}))
    });
}
"""
        timeline_result = await page.evaluate(timeline_js)

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

        # Final page info
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)
        ss_bottom = SCREENSHOT_DIR / "PW-04-bottom.png"
        await page.screenshot(path=str(ss_bottom))

        final_info = json.loads(await page.evaluate("""
JSON.stringify({
    scrollHeight: document.body.scrollHeight,
    clientHeight: document.documentElement.clientHeight,
    scrollY: window.scrollY,
    sectionCount: document.querySelectorAll('section').length,
    allClassesWithSection: Array.from(new Set(Array.from(document.querySelectorAll('[class]')).map(e => e.className.split(' ')).flat().filter(c => c.includes('section') || c.includes('timeline') || c.includes('what-happen')))).join(', ')
})
"""))

        # Print summary
        print(f"\n{'='*60}")
        print(f"SECTIONS ({len(sections_data)} total)")
        print('='*60)
        for s in sections_data:
            flags = []
            if s["display"] == "none": flags.append("display:none")
            if s["visibility"] == "hidden": flags.append("vis:hidden")
            if float(s["opacity"]) < 0.1: flags.append(f"op:{s['opacity']}")
            if s["height"] == 0: flags.append("h:0")
            status = "HIDDEN: " + ", ".join(flags) if flags else "VISIBLE"
            print(f"  [{s['index']}] top={s['top']}px h={s['height']}px | {status} | {s['class'][:50]} | id={s['id']}")

        print(f"\nOVERFLOW:HIDDEN CLIPS ({len(clips_data)})")
        print('='*60)
        for c in clips_data[:15]:
            print(f"  <{c['tag']}> cls={c['class'][:50]} client={c['clientHeight']} scroll={c['scrollHeight']}")

        print(f"\nTIMELINE CHAIN")
        print('='*60)
        print(timeline_result[:2000])

        print(f"\nHIDDEN DIVS/SECTIONS ({len(hidden_data)})")
        print('='*60)
        for h in hidden_data:
            print(f"  {h['tag']} cls={h['class'][:60]} display={h['display']} vis={h['visibility']} h={h['height']}")

        print(f"\nFINAL PAGE INFO: {json.dumps(final_info, indent=2)}")
        print(f"\nScreenshots in: {SCREENSHOT_DIR}")

        await browser.close()
        return {
            "sections": sections_data,
            "clips": clips_data,
            "timeline": timeline_result,
            "hidden": hidden_data,
            "final_info": final_info
        }


async def main():
    # Step 1: Fetch via login
    print("=== STEP 1: Login and fetch page HTML ===")
    html_path, html_content = get_full_page_via_cookie()

    if html_path and html_content and len(html_content) > 10000:
        print(f"\n=== STEP 2: Run Playwright on live URL with cookies ===")
        # Parse cookies from requests session (can't easily pass them)
        # Instead use the saved HTML for DOM analysis
        await run_playwright_audit(html_path=html_path)
    else:
        print("\n[FALLBACK] Login failed or page too short. Checking API response...")
        data = fetch_page_content()
        if data:
            raw = data.get("content", {}).get("raw", "")
            print(f"\nRaw content preview (first 1000 chars):\n{raw[:1000]}")

if __name__ == "__main__":
    asyncio.run(main())
