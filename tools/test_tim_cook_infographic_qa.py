"""
Tim Cook page - Apple Leadership Infographic QA
Target: purebrain.ai/your-ai-tim-cook/
Focus: Newly added infographic between Section 2 and Section 3
Viewport: 1280x800
Output: exports/qa-infographic/
"""

import asyncio
import os
from playwright.async_api import async_playwright

OUTPUT_DIR = "/home/jared/projects/AI-CIV/aether/exports/qa-infographic"
URL = "https://purebrain.ai/your-ai-tim-cook/"

# CSS injection to force opacity:1 on all scroll-reveal elements
FORCE_VISIBLE_CSS = """
    * {
        opacity: 1 !important;
        transform: none !important;
        transition: none !important;
        animation-play-state: paused !important;
        visibility: visible !important;
    }
    .tc-reveal, .tc-reveal-delay-1, .tc-reveal-delay-2,
    .tc-reveal-delay-3, .tc-reveal-delay-4 {
        opacity: 1 !important;
        transform: none !important;
    }
"""


async def inject_force_visible(page):
    await page.evaluate("""() => {
        const style = document.createElement('style');
        style.id = 'qa-force-visible';
        style.textContent = `
            * {
                opacity: 1 !important;
                transform: none !important;
                transition: none !important;
                animation-play-state: paused !important;
                visibility: visible !important;
            }
            .tc-reveal, .tc-reveal-delay-1, .tc-reveal-delay-2,
            .tc-reveal-delay-3, .tc-reveal-delay-4 {
                opacity: 1 !important;
                transform: none !important;
            }
        `;
        document.head.appendChild(style);
    }""")


async def scroll_full_page(page):
    """Scroll through page to trigger lazy loads, then scroll back to top."""
    total_height = await page.evaluate("document.body.scrollHeight")
    print(f"  Page height: {total_height}px")
    for y in range(0, total_height, 200):
        await page.evaluate(f"window.scrollTo(0, {y})")
        await page.wait_for_timeout(40)
    await page.evaluate("window.scrollTo(0, 0)")
    await page.wait_for_timeout(500)


async def take_screenshot(page, filename, description=""):
    path = os.path.join(OUTPUT_DIR, filename)
    await page.screenshot(path=path, full_page=False)
    print(f"  Screenshot: {filename} ({description})")
    return path


async def take_full_page_screenshot(page, filename, description=""):
    path = os.path.join(OUTPUT_DIR, filename)
    await page.screenshot(path=path, full_page=True)
    print(f"  Full-page screenshot: {filename} ({description})")
    return path


async def scroll_to_and_screenshot(page, y_position, filename, description="", clip_height=600):
    """Scroll to a Y position and screenshot the viewport."""
    await page.evaluate(f"window.scrollTo(0, {y_position})")
    await page.wait_for_timeout(300)
    path = os.path.join(OUTPUT_DIR, filename)
    await page.screenshot(path=path, full_page=False)
    print(f"  Viewport screenshot at y={y_position}: {filename} ({description})")
    return path


async def find_infographic_position(page):
    """Find the infographic section position in the page."""
    result = await page.evaluate("""() => {
        // Search for infographic containers by class patterns
        const selectors = [
            '.tc-leadership-compare',
            '.tc-compare-grid',
            '[class*="compare"]',
            '[class*="infographic"]',
            '[class*="leadership"]',
            '[class*="apple"]',
            // Look for the macOS window pattern
            '[class*="panel"]',
            '[class*="window"]',
            // Look for Steve Jobs / Tim Cook text
        ];

        let found = {};

        // Try each selector
        for (const sel of selectors) {
            const els = document.querySelectorAll(sel);
            if (els.length > 0) {
                const rect = els[0].getBoundingClientRect();
                const scrollY = window.scrollY || window.pageYOffset;
                found[sel] = {
                    count: els.length,
                    top: rect.top + scrollY,
                    height: rect.height,
                    className: els[0].className.substring(0, 80)
                };
            }
        }

        // Also search by text content for Steve Jobs / Tim Cook
        const allElements = document.querySelectorAll('*');
        let steveJobsEl = null;
        let timCookEl = null;
        let insightEl = null;

        for (const el of allElements) {
            const text = el.innerText || '';
            if (!steveJobsEl && text.includes('Steve Jobs') && el.children.length < 5) {
                steveJobsEl = el;
            }
            if (!timCookEl && text.includes('Tim Cook') && text.includes('+') && el.children.length < 5) {
                timCookEl = el;
            }
        }

        // Search for the stat numbers like +344 or +3353
        const statEls = document.querySelectorAll('[class*="stat"], [class*="value"], [class*="number"]');
        let statInfo = [];
        for (const el of Array.from(statEls).slice(0, 20)) {
            const text = el.innerText || '';
            if (text.includes('+') || text.includes('$')) {
                const rect = el.getBoundingClientRect();
                const scrollY = window.scrollY || window.pageYOffset;
                statInfo.push({
                    text: text.substring(0, 50),
                    top: rect.top + scrollY,
                    className: el.className.substring(0, 60)
                });
            }
        }

        return {
            selectorResults: found,
            steveJobsFound: steveJobsEl ? {
                className: steveJobsEl.className.substring(0, 80),
                top: steveJobsEl.getBoundingClientRect().top + window.scrollY
            } : null,
            statElements: statInfo
        };
    }""")

    return result


async def find_section_boundaries(page):
    """Find key section positions to understand page layout."""
    result = await page.evaluate("""() => {
        const sections = {};

        // Find all major tc- sections
        const tcSections = document.querySelectorAll('[class*="tc-"]');
        const sectionMap = {};

        for (const el of tcSections) {
            const classes = el.className.split(' ');
            for (const cls of classes) {
                if (cls.startsWith('tc-') && !sectionMap[cls]) {
                    const rect = el.getBoundingClientRect();
                    const scrollY = window.scrollY || window.pageYOffset;
                    sectionMap[cls] = {
                        top: Math.round(rect.top + scrollY),
                        height: Math.round(rect.height),
                        tag: el.tagName
                    };
                }
            }
        }

        return sectionMap;
    }""")
    return result


async def get_page_structure(page):
    """Get a broad view of the page structure."""
    result = await page.evaluate("""() => {
        // Get page total height
        const totalHeight = document.body.scrollHeight;

        // Find any element containing Steve Jobs or Tim Cook text
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null
        );

        let node;
        let sjeNode = null;
        let tcNode = null;
        let insightNode = null;
        let sectionLabel = null;

        while ((node = walker.nextNode())) {
            const text = node.textContent.trim();
            if (!sjeNode && text.includes('Steve Jobs')) {
                sjeNode = node.parentElement;
            }
            if (!tcNode && (text.includes('Tim Cook') && text.length < 30)) {
                tcNode = node.parentElement;
            }
            if (!insightNode && text.includes('insight') || (text && text.toLowerCase().includes('the insight'))) {
                insightNode = node.parentElement;
            }
        }

        const getInfo = (el) => {
            if (!el) return null;
            let rect = el.getBoundingClientRect();
            // Walk up to find a substantial container
            let current = el;
            while (current && rect.height < 50) {
                current = current.parentElement;
                if (current) rect = current.getBoundingClientRect();
            }
            return {
                tag: current ? current.tagName : el.tagName,
                className: (current || el).className.substring(0, 100),
                top: Math.round(rect.top + window.scrollY),
                height: Math.round(rect.height)
            };
        };

        return {
            totalHeight,
            steveJobs: getInfo(sjeNode),
            timCookLabel: getInfo(tcNode),
            insight: getInfo(insightNode)
        };
    }""")
    return result


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Target URL: {URL}")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            device_scale_factor=1
        )
        page = await context.new_page()

        # Collect console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append({
            "type": msg.type,
            "text": msg.text
        }))

        print("\n[1] Loading page...")
        response = await page.goto(URL, wait_until="networkidle", timeout=30000)
        print(f"  Status: {response.status}")
        await page.wait_for_timeout(2000)

        print("\n[2] Scrolling full page to trigger lazy loads...")
        await scroll_full_page(page)

        print("\n[3] Discovering page structure...")
        structure = await get_page_structure(page)
        print(f"  Total page height: {structure['totalHeight']}px")
        print(f"  Steve Jobs element: {structure['steveJobs']}")
        print(f"  Tim Cook element: {structure['timCookLabel']}")
        print(f"  Insight element: {structure['insight']}")

        print("\n[4] Finding infographic position...")
        infographic_info = await find_infographic_position(page)
        print(f"  Selector results: {list(infographic_info['selectorResults'].keys())}")
        print(f"  Steve Jobs found: {infographic_info['steveJobsFound']}")
        print(f"  Stat elements: {infographic_info['statElements'][:5]}")

        print("\n[5] Getting full section map...")
        section_map = await find_section_boundaries(page)
        # Print all sections with their positions
        sorted_sections = sorted(section_map.items(), key=lambda x: x[1]['top'])
        for cls, info in sorted_sections[:30]:
            print(f"  {cls}: top={info['top']}px, height={info['height']}px")

        print("\n[6] Injecting force-visible CSS...")
        await inject_force_visible(page)
        await page.wait_for_timeout(500)

        # Screenshot 1: Full page view (viewport - top of page)
        print("\n[7] Taking Screenshot 1: Full page top viewport...")
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(300)
        await take_screenshot(page, "01-full-page-top.png", "Top of page, hero section")

        # Screenshot 2: Full-page screenshot (this will be long but confirms nothing broken)
        # We'll do a stitched composite instead - scroll to key positions
        total_height = structure['totalHeight']
        print(f"\n[8] Taking Screenshot 2: Full page scrolled view (height: {total_height}px)...")

        # We want a full-page screenshot but constrained for sanity
        await page.set_viewport_size({"width": 1280, "height": 800})

        # Full page screenshot
        full_page_path = os.path.join(OUTPUT_DIR, "02-full-page-complete.png")
        await page.screenshot(path=full_page_path, full_page=True)
        print(f"  Full-page screenshot saved: 02-full-page-complete.png")

        # Now find the infographic - use DOM info from structure analysis
        sje_info = structure['steveJobs']
        tc_info = structure['timCookLabel']

        # Determine infographic Y position
        infographic_top = None
        if sje_info:
            infographic_top = max(0, sje_info['top'] - 150)  # A bit above Steve Jobs section
        elif infographic_info['steveJobsFound']:
            infographic_top = max(0, infographic_info['steveJobsFound']['top'] - 150)
        elif infographic_info['statElements']:
            infographic_top = max(0, infographic_info['statElements'][0]['top'] - 200)

        if infographic_top is None:
            # Fallback: Try to find it by checking the compare/leadership section
            for cls, info in sorted_sections:
                if any(kw in cls for kw in ['compare', 'leadership', 'apple', 'panel', 'infographic']):
                    infographic_top = info['top']
                    print(f"  Fallback: found infographic via class '{cls}' at y={infographic_top}")
                    break

        if infographic_top is None:
            # Try to estimate based on page structure - infographic should be after hero/problem section
            # and before section 3. Page is typically ~8000-12000px long.
            # Section 2 (problem) is usually around 1500-3000px in
            # Let's probe the middle third of the page
            infographic_top = total_height // 4
            print(f"  Using estimated position: y={infographic_top}")

        print(f"\n[9] Infographic estimated at y={infographic_top}px")

        # Screenshot 3: Infographic section context view
        print("\n[10] Taking Screenshot 3: Infographic section overview...")
        await scroll_to_and_screenshot(
            page, max(0, infographic_top - 100),
            "03-infographic-section-overview.png",
            "Infographic section with surrounding context"
        )

        # Screenshot 4: Top of infographic (Steve Jobs panel area)
        print("\n[11] Taking Screenshot 4: Steve Jobs panel area...")
        await scroll_to_and_screenshot(
            page, infographic_top,
            "04-steve-jobs-panel.png",
            "Steve Jobs panel top area"
        )

        # Screenshot 5: Continue scrolling to Tim Cook panel
        await scroll_to_and_screenshot(
            page, infographic_top + 400,
            "05-tim-cook-panel.png",
            "Tim Cook panel area"
        )

        # Screenshot 6: Further down - bottom of infographic / insight callout
        await scroll_to_and_screenshot(
            page, infographic_top + 800,
            "06-insight-callout.png",
            "Insight callout box below panels"
        )

        # Screenshot 7: Extra down - insight callout may be further
        await scroll_to_and_screenshot(
            page, infographic_top + 1200,
            "07-post-infographic.png",
            "Area below insight callout - Section 3 transition"
        )

        # Now do more targeted screenshots using DOM data
        print("\n[12] Taking targeted DOM-based screenshots...")

        # Try to screenshot specific elements using clip
        clip_result = await page.evaluate("""() => {
            // Try to find the compare/infographic wrapper
            const searches = [
                '.tc-compare', '.tc-leadership', '.tc-apple',
                '[class*="compare-grid"]', '[class*="leadership-compare"]',
                '[class*="macos"]', '[class*="panel-wrap"]',
                '[class*="infographic"]',
                // Also search by content
            ];

            // Search all tc- elements for the one containing Steve Jobs text
            const allTcEls = document.querySelectorAll('[class^="tc-"], [class*=" tc-"]');
            for (const el of allTcEls) {
                const text = el.innerText || '';
                if (text.includes('Steve Jobs') && text.includes('Tim Cook')) {
                    const rect = el.getBoundingClientRect();
                    const scrollY = window.scrollY || window.pageYOffset;
                    return {
                        found: true,
                        method: 'text-search tc- element',
                        className: el.className.substring(0, 120),
                        top: Math.round(rect.top + scrollY),
                        height: Math.round(rect.height),
                        width: Math.round(rect.width)
                    };
                }
            }

            // Try general search
            const allEls = document.querySelectorAll('div, section, article');
            for (const el of allEls) {
                const text = el.innerText || '';
                if (text.includes('Steve Jobs') && text.includes('Tim Cook') &&
                    text.includes('+') && el.children.length > 1 && el.children.length < 20) {
                    const rect = el.getBoundingClientRect();
                    const scrollY = window.scrollY || window.pageYOffset;
                    return {
                        found: true,
                        method: 'general div/section text search',
                        className: el.className.substring(0, 120),
                        top: Math.round(rect.top + scrollY),
                        height: Math.round(rect.height),
                        width: Math.round(rect.width)
                    };
                }
            }

            return { found: false };
        }""")

        print(f"  DOM clip search result: {clip_result}")

        if clip_result.get('found'):
            infographic_actual_top = clip_result['top']
            infographic_height = clip_result['height']
            print(f"  Found infographic wrapper at y={infographic_actual_top}, height={infographic_height}px")

            # Scroll to top of infographic, screenshot
            await page.evaluate(f"window.scrollTo(0, {max(0, infographic_actual_top - 100)})")
            await page.wait_for_timeout(400)
            await take_screenshot(page, "08-infographic-top.png", f"Infographic at y={infographic_actual_top}")

            # Now take clipped screenshots of just the infographic
            # Scroll so the infographic starts near viewport top
            viewport_scroll = max(0, infographic_actual_top - 50)
            await page.evaluate(f"window.scrollTo(0, {viewport_scroll})")
            await page.wait_for_timeout(400)

            # Screenshot top of infographic (should show Steve Jobs panel)
            await take_screenshot(page, "09-infographic-viewport-top.png", "Infographic viewport - Steve Jobs panel area")

            # Scroll to middle of infographic
            mid_scroll = infographic_actual_top + (infographic_height // 2) - 400
            await page.evaluate(f"window.scrollTo(0, {max(0, mid_scroll)})")
            await page.wait_for_timeout(400)
            await take_screenshot(page, "10-infographic-viewport-mid.png", "Infographic viewport middle")

            # Scroll to bottom of infographic (Tim Cook panel + insight)
            bottom_scroll = infographic_actual_top + infographic_height - 800
            if bottom_scroll > viewport_scroll:
                await page.evaluate(f"window.scrollTo(0, {max(0, bottom_scroll)})")
                await page.wait_for_timeout(400)
                await take_screenshot(page, "11-infographic-viewport-bottom.png", "Infographic bottom - insight callout")

        # Screenshot of both existing images (amplify-founder and vc-fomo)
        print("\n[13] Checking for amplify-founder image...")
        amplify_result = await page.evaluate("""() => {
            const imgs = document.querySelectorAll('img');
            for (const img of imgs) {
                if (img.src && img.src.includes('amplify-founder')) {
                    const rect = img.getBoundingClientRect();
                    return {
                        found: true,
                        src: img.src,
                        top: Math.round(rect.top + window.scrollY),
                        naturalWidth: img.naturalWidth,
                        naturalHeight: img.naturalHeight
                    };
                }
            }
            return { found: false };
        }""")
        print(f"  amplify-founder: {amplify_result}")

        print("\n[14] Checking for vc-fomo image...")
        vcfomo_result = await page.evaluate("""() => {
            const imgs = document.querySelectorAll('img');
            for (const img of imgs) {
                if (img.src && img.src.includes('vc-fomo')) {
                    const rect = img.getBoundingClientRect();
                    return {
                        found: true,
                        src: img.src,
                        top: Math.round(rect.top + window.scrollY),
                        naturalWidth: img.naturalWidth,
                        naturalHeight: img.naturalHeight
                    };
                }
            }
            return { found: false };
        }""")
        print(f"  vc-fomo: {vcfomo_result}")

        # Screenshot amplify-founder in context
        if amplify_result.get('found'):
            amp_top = amplify_result['top']
            await page.evaluate(f"window.scrollTo(0, {max(0, amp_top - 100)})")
            await page.wait_for_timeout(400)
            await take_screenshot(page, "12-amplify-founder-context.png", f"amplify-founder image at y={amp_top}")

        # Screenshot vc-fomo in context
        if vcfomo_result.get('found'):
            fomo_top = vcfomo_result['top']
            await page.evaluate(f"window.scrollTo(0, {max(0, fomo_top - 100)})")
            await page.wait_for_timeout(400)
            await take_screenshot(page, "13-vc-fomo-context.png", f"vc-fomo image at y={fomo_top}")

        # Check background color
        print("\n[15] Checking background color...")
        bg_color = await page.evaluate("""() => {
            return window.getComputedStyle(document.body).backgroundColor;
        }""")
        print(f"  Body background: {bg_color}")

        # Check for orange bleed
        orange_check = await page.evaluate("""() => {
            const body = window.getComputedStyle(document.body);
            const bgColor = body.backgroundColor;
            // Check if it contains orange-ish values
            const match = bgColor.match(/rgb\\((\\d+),\\s*(\\d+),\\s*(\\d+)\\)/);
            if (match) {
                const r = parseInt(match[1]);
                const g = parseInt(match[2]);
                const b = parseInt(match[3]);
                // Orange would have high R, medium G, low B
                const isOrange = r > 200 && g > 50 && g < 150 && b < 50;
                return { bgColor, r, g, b, isOrange };
            }
            return { bgColor, isOrange: false };
        }""")
        print(f"  Orange bleed check: {orange_check}")

        # Collect console errors
        errors = [m for m in console_messages if m['type'] == 'error']
        warnings = [m for m in console_messages if m['type'] == 'warning']
        print(f"\n[16] Console: {len(errors)} errors, {len(warnings)} warnings")
        for err in errors[:5]:
            print(f"  ERROR: {err['text'][:100]}")

        # Final: Scroll back to top and take a clean "current state" screenshot
        print("\n[17] Final hero screenshot...")
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        await take_screenshot(page, "00-hero-final.png", "Hero section - final state")

        await browser.close()

        print("\n" + "=" * 60)
        print("SCREENSHOTS CAPTURED:")
        for f in sorted(os.listdir(OUTPUT_DIR)):
            fpath = os.path.join(OUTPUT_DIR, f)
            size = os.path.getsize(fpath)
            print(f"  {f} ({size:,} bytes)")

        print(f"\nResults summary:")
        print(f"  Background color: {bg_color}")
        print(f"  Orange bleed: {'YES - FAIL' if orange_check.get('isOrange') else 'NO - PASS'}")
        print(f"  amplify-founder: {'FOUND' if amplify_result.get('found') else 'NOT FOUND'}")
        print(f"  vc-fomo: {'FOUND' if vcfomo_result.get('found') else 'NOT FOUND'}")
        print(f"  Console errors: {len(errors)}")
        print(f"  Infographic found: {'YES' if clip_result.get('found') else 'NOT FOUND - check screenshots'}")
        if clip_result.get('found'):
            print(f"  Infographic position: y={clip_result['top']}px, height={clip_result['height']}px")

        return {
            'clip_result': clip_result,
            'bg_color': bg_color,
            'orange_check': orange_check,
            'amplify_result': amplify_result,
            'vcfomo_result': vcfomo_result,
            'errors': errors,
            'structure': structure,
            'section_map': sorted_sections
        }


if __name__ == "__main__":
    asyncio.run(main())
