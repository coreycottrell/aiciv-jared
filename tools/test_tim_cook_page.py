"""
QA test for purebrain.ai/your-ai-tim-cook/
Tests: dark theme, hero, sections, CTAs, wordmark, org chart, clock, animations, mobile
"""

import asyncio
import json
import os
from playwright.async_api import async_playwright

URL = "https://purebrain.ai/your-ai-tim-cook/"
SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/tim-cook-qa-2026-02-27"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

findings = []
screenshots = []

def log(msg):
    print(msg)
    findings.append(msg)

async def take_screenshot(page, name, label):
    path = f"{SCREENSHOT_DIR}/{name}.png"
    await page.screenshot(path=path, full_page=False)
    screenshots.append({"file": path, "label": label})
    print(f"  [SCREENSHOT] {name}.png - {label}")
    return path

async def run_qa():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # === DESKTOP TEST (1440x900) ===
        log("\n" + "="*60)
        log("DESKTOP TEST (1440x900)")
        log("="*60)

        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        # Capture console errors
        console_errors = []
        console_warnings = []
        page.on("console", lambda msg: (
            console_errors.append(msg.text) if msg.type == "error" else
            console_warnings.append(msg.text) if msg.type == "warning" else None
        ))

        # Navigate
        response = await page.goto(URL, wait_until="networkidle", timeout=30000)
        log(f"\n[1] PAGE LOAD")
        log(f"  Status: {response.status}")
        log(f"  URL: {response.url}")

        await page.wait_for_timeout(2000)
        await take_screenshot(page, "001-desktop-initial-load", "Desktop initial load 1440x900")

        # CHECK 1: Dark theme - body background
        body_bg = await page.evaluate("window.getComputedStyle(document.body).backgroundColor")
        body_bg_hex = await page.evaluate("""
            () => {
                const rgb = window.getComputedStyle(document.body).backgroundColor;
                const match = rgb.match(/\\d+/g);
                if (!match) return rgb;
                const [r, g, b] = match;
                return '#' + [r, g, b].map(x => parseInt(x).toString(16).padStart(2, '0')).join('');
            }
        """)
        log(f"\n[2] DARK THEME CHECK")
        log(f"  Body background computed: {body_bg}")
        log(f"  Body background hex: {body_bg_hex}")

        # Check if orange (#f1420b = rgb(241, 66, 11))
        is_orange_bg = "241, 66, 11" in body_bg or "f1420b" in body_bg_hex.lower()
        is_dark_bg = body_bg_hex.lower() in ["#0a0e1a", "#0d1117", "#111111", "#000000", "#0a0a0a"] or \
                     (body_bg_hex.startswith("#") and int(body_bg_hex[1:3], 16) < 30)

        if is_orange_bg:
            log(f"  STATUS: FAIL - Orange background bleed detected!")
        elif is_dark_bg:
            log(f"  STATUS: PASS - Dark theme confirmed")
        else:
            log(f"  STATUS: WARNING - Unexpected background color: {body_bg_hex}")

        # CHECK 2: Page template
        page_template = await page.evaluate("""
            () => {
                const body = document.body;
                return body.className;
            }
        """)
        log(f"\n[3] PAGE TEMPLATE")
        log(f"  Body classes: {page_template[:200]}")

        # Check if elementor_canvas
        has_elementor_canvas = "elementor-template-canvas" in page_template or "elementor_canvas" in page_template
        log(f"  Elementor Canvas: {has_elementor_canvas}")

        # CHECK 3: Hero section
        log(f"\n[4] HERO SECTION")
        hero = await page.query_selector(".tc-hero, .hero, [class*='hero'], h1")
        if hero:
            hero_text = await hero.inner_text()
            log(f"  Hero found: {hero_text[:100]}")
            hero_visible = await hero.is_visible()
            log(f"  Hero visible: {hero_visible}")
        else:
            log(f"  WARNING: No hero element found via common selectors")

        # Get H1
        h1 = await page.query_selector("h1")
        if h1:
            h1_text = await h1.inner_text()
            log(f"  H1 text: {h1_text[:150]}")

        # CHECK 4: Particle/animation canvas
        log(f"\n[5] PARTICLE ANIMATION")
        canvas_elements = await page.query_selector_all("canvas")
        log(f"  Canvas elements found: {len(canvas_elements)}")
        for i, canvas in enumerate(canvas_elements):
            canvas_id = await canvas.get_attribute("id")
            canvas_class = await canvas.get_attribute("class")
            log(f"    Canvas {i+1}: id={canvas_id}, class={canvas_class}")

        # CHECK 5: Section count
        log(f"\n[6] SECTIONS CHECK")
        sections = await page.query_selector_all("section, .tc-section, [class*='section']")
        log(f"  Total section-like elements: {len(sections)}")

        # Get all major headings to identify sections
        headings = await page.query_selector_all("h1, h2, h3")
        log(f"  Total headings (h1/h2/h3): {len(headings)}")
        for heading in headings[:15]:
            heading_text = await heading.inner_text()
            heading_tag = await heading.evaluate("el => el.tagName")
            log(f"    {heading_tag}: {heading_text[:80]}")

        # CHECK 6: CTA Buttons
        log(f"\n[7] CTA BUTTONS")
        buttons = await page.query_selector_all("a.tc-cta, button.tc-cta, .cta-button, [class*='cta'], a[href*='awakening'], a[href*='purebrain']")
        all_buttons = await page.query_selector_all("a[class*='btn'], a[class*='button'], button, .tc-btn")
        log(f"  CTA-style buttons: {len(buttons)}")
        log(f"  All clickable buttons: {len(all_buttons)}")

        # Check button colors
        button_color_check = await page.evaluate("""
            () => {
                const results = [];
                const btns = document.querySelectorAll('a, button');
                for (const btn of btns) {
                    const text = btn.innerText ? btn.innerText.trim() : '';
                    if (text.length > 2 && text.length < 60) {
                        const style = window.getComputedStyle(btn);
                        const bg = style.backgroundColor;
                        if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
                            results.push({text: text.substring(0, 40), bg});
                        }
                    }
                }
                return results.slice(0, 20);
            }
        """)
        for btn_info in button_color_check:
            log(f"    Button '{btn_info['text']}': bg={btn_info['bg']}")

        # CHECK 7: PUREBRAIN Wordmark
        log(f"\n[8] PUREBRAIN WORDMARK")
        wordmark_check = await page.evaluate("""
            () => {
                const spans = document.querySelectorAll('span');
                const results = [];
                for (const span of spans) {
                    const text = span.innerText ? span.innerText.trim() : '';
                    const color = window.getComputedStyle(span).color;
                    if ((text === 'PUREBR' || text === 'AI' || text === 'N' || text === 'PUREBRAIN') && color) {
                        results.push({text, color});
                    }
                }
                return results;
            }
        """)
        log(f"  Wordmark spans found: {len(wordmark_check)}")
        for w in wordmark_check:
            log(f"    '{w['text']}': color={w['color']}")

        # Also check for PUREBRAIN in any color-coded format
        purebrain_text = await page.evaluate("""
            () => {
                const allText = document.body.innerHTML;
                const matches = [];
                const spanPattern = /<span[^>]*class[^>]*blue[^>]*>([^<]+)<\/span>|<span[^>]*style[^>]*color[^>]*>([^<]+)<\/span>/g;
                let match;
                const found = allText.match(/PUREBR|PUREBRAIN/g);
                return found ? found.length : 0;
            }
        """)
        log(f"  'PUREBR/PUREBRAIN' occurrences in HTML: {purebrain_text}")

        # CHECK 8: Department org chart
        log(f"\n[9] DEPARTMENT ORG CHART")
        dept_grid = await page.query_selector(".dept-grid, .departments-grid, [class*='dept'], [class*='department'], .org-chart")
        dept_items = await page.query_selector_all(".dept-card, .department-card, [class*='dept-'], [class*='department-']")
        log(f"  Dept grid found: {dept_grid is not None}")
        log(f"  Dept card items: {len(dept_items)}")

        # Look for the 23 departments mentioned
        dept_count_check = await page.evaluate("""
            () => {
                // Look for elements that might be department cards
                const candidates = document.querySelectorAll('[class*="dept"], [class*="department"]');
                return candidates.length;
            }
        """)
        log(f"  Department-class elements: {dept_count_check}")

        # CHECK 9: Animated clock (24/7 section)
        log(f"\n[10] ANIMATED CLOCK (24/7 SECTION)")
        clock_check = await page.evaluate("""
            () => {
                // Look for clock elements
                const clockEls = document.querySelectorAll('.clock, .clock-face, .clock-hand, [class*="clock"], [class*="tick"]');
                const svgEls = document.querySelectorAll('svg');
                const animEls = document.querySelectorAll('[class*="anim"], [class*="rotate"]');
                return {
                    clockElements: clockEls.length,
                    svgElements: svgEls.length,
                    animElements: animEls.length,
                    // Check for 24/7 text
                    has247: document.body.innerHTML.includes('24/7') || document.body.innerHTML.includes('24\\/7')
                };
            }
        """)
        log(f"  Clock elements: {clock_check['clockElements']}")
        log(f"  SVG elements: {clock_check['svgElements']}")
        log(f"  Animation elements: {clock_check['animElements']}")
        log(f"  Has 24/7 text: {clock_check['has247']}")

        # CHECK 10: Scroll - check various scroll positions
        log(f"\n[11] SCROLL POSITION CHECKS")

        # Scroll to 25%
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.25)")
        await page.wait_for_timeout(1000)
        bg_at_25 = await page.evaluate("window.getComputedStyle(document.elementFromPoint(720, 400)).backgroundColor")
        await take_screenshot(page, "002-desktop-scroll-25pct", "Desktop scroll 25%")
        log(f"  Background at 25% scroll: {bg_at_25}")

        # Scroll to 50%
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.5)")
        await page.wait_for_timeout(1000)
        await take_screenshot(page, "003-desktop-scroll-50pct", "Desktop scroll 50%")
        bg_at_50 = await page.evaluate("window.getComputedStyle(document.elementFromPoint(720, 400)).backgroundColor")
        log(f"  Background at 50% scroll: {bg_at_50}")

        # Scroll to 75%
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.75)")
        await page.wait_for_timeout(1000)
        await take_screenshot(page, "004-desktop-scroll-75pct", "Desktop scroll 75%")

        # Scroll to bottom
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)
        await take_screenshot(page, "005-desktop-scroll-bottom", "Desktop scroll to bottom")

        # Back to top
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)

        # Full page screenshot
        full_page_path = f"{SCREENSHOT_DIR}/006-desktop-full-page.png"
        await page.screenshot(path=full_page_path, full_page=True)
        screenshots.append({"file": full_page_path, "label": "Full page desktop"})
        log(f"\n[12] Full page screenshot saved")

        # Get page dimensions and scroll height
        page_metrics = await page.evaluate("""
            () => ({
                scrollHeight: document.body.scrollHeight,
                clientHeight: document.documentElement.clientHeight,
                scrollWidth: document.body.scrollWidth,
                clientWidth: document.documentElement.clientWidth
            })
        """)
        log(f"\n[13] PAGE METRICS")
        log(f"  Page scroll height: {page_metrics['scrollHeight']}px")
        log(f"  Viewport height: {page_metrics['clientHeight']}px")
        log(f"  Scroll width: {page_metrics['scrollWidth']}px")

        # Console log report
        log(f"\n[14] CONSOLE ERRORS")
        log(f"  Total errors: {len(console_errors)}")
        for err in console_errors[:10]:
            log(f"    ERROR: {err[:120]}")
        log(f"  Total warnings: {len(console_warnings)}")
        for warn in console_warnings[:5]:
            log(f"    WARN: {warn[:100]}")

        await context.close()

        # === MOBILE TEST (375x667) ===
        log(f"\n" + "="*60)
        log("MOBILE TEST (375x667 - iPhone SE)")
        log("="*60)

        mobile_context = await browser.new_context(
            viewport={"width": 375, "height": 667},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15"
        )
        mobile_page = await mobile_context.new_page()

        mobile_errors = []
        mobile_page.on("console", lambda msg: mobile_errors.append(msg.text) if msg.type == "error" else None)

        await mobile_page.goto(URL, wait_until="networkidle", timeout=30000)
        await mobile_page.wait_for_timeout(2000)

        await take_screenshot(mobile_page, "007-mobile-375-initial", "Mobile 375x667 initial load")

        mobile_bg = await mobile_page.evaluate("""
            () => {
                const rgb = window.getComputedStyle(document.body).backgroundColor;
                const match = rgb.match(/\\d+/g);
                if (!match) return rgb;
                const [r, g, b] = match;
                return '#' + [r, g, b].map(x => parseInt(x).toString(16).padStart(2, '0')).join('');
            }
        """)
        log(f"  Mobile body background: {mobile_bg}")

        # Check for horizontal overflow (layout break indicator)
        mobile_overflow = await mobile_page.evaluate("""
            () => {
                const overflowing = [];
                document.querySelectorAll('*').forEach(el => {
                    if (el.scrollWidth > 375) {
                        overflowing.push({
                            tag: el.tagName,
                            class: el.className.toString().substring(0, 50),
                            width: el.scrollWidth
                        });
                    }
                });
                return overflowing.slice(0, 10);
            }
        """)
        log(f"\n  Mobile overflow elements: {len(mobile_overflow)}")
        for el in mobile_overflow[:5]:
            log(f"    {el['tag']} .{el['class']}: {el['width']}px wide")

        # Full mobile page
        mobile_full_path = f"{SCREENSHOT_DIR}/008-mobile-full-page.png"
        await mobile_page.screenshot(path=mobile_full_path, full_page=True)
        screenshots.append({"file": mobile_full_path, "label": "Full page mobile 375"})

        await mobile_context.close()

        # === TABLET TEST (768x1024) ===
        log(f"\n" + "="*60)
        log("TABLET TEST (768x1024)")
        log("="*60)

        tablet_context = await browser.new_context(
            viewport={"width": 768, "height": 1024},
        )
        tablet_page = await tablet_context.new_page()
        await tablet_page.goto(URL, wait_until="networkidle", timeout=30000)
        await tablet_page.wait_for_timeout(2000)
        await take_screenshot(tablet_page, "009-tablet-768-initial", "Tablet 768x1024 initial")

        tablet_path = f"{SCREENSHOT_DIR}/010-tablet-full-page.png"
        await tablet_page.screenshot(path=tablet_path, full_page=True)
        screenshots.append({"file": tablet_path, "label": "Full page tablet 768"})

        await tablet_context.close()

        # === SPECIFIC ELEMENT CHECKS ===
        log(f"\n" + "="*60)
        log("SPECIFIC ELEMENT DEEP CHECK")
        log("="*60)

        check_context = await browser.new_context(viewport={"width": 1440, "height": 900})
        check_page = await check_context.new_page()
        await check_page.goto(URL, wait_until="networkidle", timeout=30000)
        await check_page.wait_for_timeout(3000)

        # Deep HTML analysis
        deep_check = await check_page.evaluate("""
            () => {
                const body = document.body;
                const bodyBg = window.getComputedStyle(body).backgroundColor;

                // Find any orange backgrounds
                const allEls = document.querySelectorAll('*');
                const orangeEls = [];
                for (const el of allEls) {
                    const bg = window.getComputedStyle(el).backgroundColor;
                    if (bg.includes('241') && bg.includes('66') && bg.includes('11')) {
                        orangeEls.push({
                            tag: el.tagName,
                            id: el.id,
                            class: el.className ? el.className.toString().substring(0, 50) : '',
                            bg
                        });
                    }
                }

                // Find wordmark
                const wordmarkSpans = [];
                document.querySelectorAll('span, div').forEach(el => {
                    const text = el.innerText ? el.innerText.trim() : '';
                    if (text === 'PUREBR' || text === 'AI' || text === 'N' || text === 'PUREBRAIN') {
                        const color = window.getComputedStyle(el).color;
                        const bg = window.getComputedStyle(el).backgroundColor;
                        wordmarkSpans.push({text, color, bg, tag: el.tagName});
                    }
                });

                // Find CTA buttons with orange
                const ctaButtons = [];
                document.querySelectorAll('a, button').forEach(el => {
                    const bg = window.getComputedStyle(el).backgroundColor;
                    if (bg.includes('241') && bg.includes('66') && bg.includes('11')) {
                        ctaButtons.push({
                            text: el.innerText ? el.innerText.trim().substring(0, 50) : '',
                            href: el.href || '',
                            bg
                        });
                    }
                });

                // Find scroll reveal / animation elements
                const animElements = document.querySelectorAll('[class*="reveal"], [class*="fade"], [class*="slide"], [data-aos], [class*="animate"]');

                // Find clock
                const clockEls = document.querySelectorAll('.clock, [class*="clock"], .hand, [class*="hand"]');

                // Check for department grid
                const deptEls = document.querySelectorAll('[class*="dept-card"], [class*="department"], .tc-dept, .dept-item');

                return {
                    bodyBg,
                    orangeElements: orangeEls.slice(0, 10),
                    wordmarkSpans,
                    ctaButtons,
                    animElementCount: animElements.length,
                    clockElementCount: clockEls.length,
                    deptElementCount: deptEls.length,
                    totalBodyLength: body.innerHTML.length
                };
            }
        """)

        log(f"\n  Body background: {deep_check['bodyBg']}")
        log(f"\n  Orange elements found: {len(deep_check['orangeElements'])}")
        for el in deep_check['orangeElements'][:5]:
            log(f"    {el['tag']} #{el['id']} .{el['class']}: {el['bg']}")

        log(f"\n  Wordmark spans: {len(deep_check['wordmarkSpans'])}")
        for w in deep_check['wordmarkSpans']:
            log(f"    '{w['text']}' ({w['tag']}): color={w['color']}, bg={w['bg']}")

        log(f"\n  Orange CTA buttons: {len(deep_check['ctaButtons'])}")
        for btn in deep_check['ctaButtons']:
            log(f"    '{btn['text']}' -> {btn['href'][:60]}")

        log(f"\n  Animation elements: {deep_check['animElementCount']}")
        log(f"  Clock elements: {deep_check['clockElementCount']}")
        log(f"  Department elements: {deep_check['deptElementCount']}")
        log(f"  Total HTML body length: {deep_check['totalBodyLength']:,} bytes")

        await check_context.close()
        await browser.close()

    return findings, screenshots

# Run the test
findings, screenshots = asyncio.run(run_qa())

# Print summary
print("\n" + "="*60)
print("SCREENSHOTS CAPTURED:")
for s in screenshots:
    print(f"  {s['file']}")
    print(f"    -> {s['label']}")

print(f"\nTotal findings: {len(findings)} log lines")
print(f"Total screenshots: {len(screenshots)}")

# Save findings to JSON for report
output = {
    "findings": findings,
    "screenshots": screenshots
}
with open("/tmp/tim-cook-qa-raw.json", "w") as f:
    json.dump(output, f, indent=2)
print("\nRaw findings saved to /tmp/tim-cook-qa-raw.json")
