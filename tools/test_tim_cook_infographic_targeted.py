"""
Tim Cook page - Targeted Apple Infographic QA
Uses aig- class prefix found in initial discovery
Steve Jobs stat at y~2962, Tim Cook stat at y~3597
"""

import asyncio
import os
from playwright.async_api import async_playwright

OUTPUT_DIR = "/home/jared/projects/AI-CIV/aether/exports/qa-infographic"
URL = "https://purebrain.ai/your-ai-tim-cook/"

FORCE_VISIBLE_JS = """() => {
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
    `;
    document.head.appendChild(style);
}"""


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output: {OUTPUT_DIR}")
    print(f"URL: {URL}")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            device_scale_factor=1
        )
        page = await context.new_page()

        console_msgs = []
        page.on("console", lambda m: console_msgs.append({"type": m.type, "text": m.text}))

        print("\n[1] Loading page...")
        resp = await page.goto(URL, wait_until="networkidle", timeout=30000)
        print(f"  HTTP {resp.status}")
        await page.wait_for_timeout(2000)

        print("\n[2] Scrolling to trigger lazy loads...")
        total_h = await page.evaluate("document.body.scrollHeight")
        print(f"  Page height: {total_h}px")
        for y in range(0, total_h, 300):
            await page.evaluate(f"window.scrollTo(0, {y})")
            await page.wait_for_timeout(40)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)

        print("\n[3] Injecting force-visible CSS...")
        await page.evaluate(FORCE_VISIBLE_JS)
        await page.wait_for_timeout(300)

        print("\n[4] Discovering aig- elements (Apple Infographic Grid)...")
        aig_info = await page.evaluate("""() => {
            const results = [];
            const allEls = document.querySelectorAll('[class]');
            const seen = new Set();

            for (const el of allEls) {
                const classes = el.className.split ? el.className.split(' ') : [];
                for (const cls of classes) {
                    if (cls.startsWith('aig-') && !seen.has(cls)) {
                        seen.add(cls);
                        const rect = el.getBoundingClientRect();
                        const scrollY = window.scrollY || window.pageYOffset;
                        results.push({
                            class: cls,
                            tag: el.tagName,
                            top: Math.round(rect.top + scrollY),
                            height: Math.round(rect.height),
                            width: Math.round(rect.width),
                            text: (el.innerText || '').substring(0, 80).trim()
                        });
                    }
                }
            }

            // Sort by top position
            results.sort((a, b) => a.top - b.top);
            return results;
        }""")

        print(f"  Found {len(aig_info)} aig- elements:")
        for item in aig_info:
            print(f"    .{item['class']}: y={item['top']}, h={item['height']}, w={item['width']} | {item['text'][:60]}")

        # Find the main infographic wrapper (should contain both Steve Jobs and Tim Cook)
        main_wrapper = await page.evaluate("""() => {
            const allEls = document.querySelectorAll('*');
            for (const el of allEls) {
                const text = el.innerText || '';
                const cls = el.className || '';
                if ((cls.includes('aig-') || cls.includes('tc-')) &&
                    text.includes('Steve Jobs') && text.includes('Tim Cook') &&
                    text.includes('+$344')) {
                    const rect = el.getBoundingClientRect();
                    const scrollY = window.scrollY || window.pageYOffset;
                    return {
                        found: true,
                        className: el.className.substring(0, 120),
                        tag: el.tagName,
                        top: Math.round(rect.top + scrollY),
                        height: Math.round(rect.height),
                        width: Math.round(rect.width)
                    };
                }
            }
            return { found: false };
        }""")
        print(f"\n  Main infographic wrapper: {main_wrapper}")

        # Find individual panels
        panels_info = await page.evaluate("""() => {
            const results = {};

            // Jobs panel
            const jobsPanels = document.querySelectorAll('.aig-panel-jobs, [class*="jobs"]');
            if (jobsPanels.length > 0) {
                const rect = jobsPanels[0].getBoundingClientRect();
                results.jobs_panel = {
                    class: jobsPanels[0].className.substring(0, 80),
                    top: Math.round(rect.top + window.scrollY),
                    height: Math.round(rect.height)
                };
            }

            // Cook panel
            const cookPanels = document.querySelectorAll('.aig-panel-cook, [class*="cook"]');
            if (cookPanels.length > 0) {
                const rect = cookPanels[0].getBoundingClientRect();
                results.cook_panel = {
                    class: cookPanels[0].className.substring(0, 80),
                    top: Math.round(rect.top + window.scrollY),
                    height: Math.round(rect.height)
                };
            }

            // Insight box
            const insightEls = document.querySelectorAll('.aig-insight, [class*="insight"]');
            if (insightEls.length > 0) {
                const rect = insightEls[0].getBoundingClientRect();
                results.insight = {
                    class: insightEls[0].className.substring(0, 80),
                    top: Math.round(rect.top + window.scrollY),
                    height: Math.round(rect.height),
                    text: (insightEls[0].innerText || '').substring(0, 100)
                };
            }

            // Stat elements
            const statEls = document.querySelectorAll('.aig-stat-primary');
            results.stats = [];
            for (const el of statEls) {
                const rect = el.getBoundingClientRect();
                results.stats.push({
                    class: el.className,
                    text: (el.innerText || '').trim(),
                    top: Math.round(rect.top + window.scrollY)
                });
            }

            // Avatar circles
            const avatarEls = document.querySelectorAll('.aig-avatar, [class*="avatar"]');
            results.avatars = [];
            for (const el of avatarEls) {
                const rect = el.getBoundingClientRect();
                results.avatars.push({
                    class: el.className.substring(0, 60),
                    text: (el.innerText || '').trim(),
                    top: Math.round(rect.top + window.scrollY)
                });
            }

            // Product chips
            const chipEls = document.querySelectorAll('.aig-chip, [class*="chip"]');
            results.chips = [];
            for (const el of chipEls) {
                const rect = el.getBoundingClientRect();
                results.chips.push({
                    class: el.className.substring(0, 60),
                    text: (el.innerText || '').trim().substring(0, 30),
                    top: Math.round(rect.top + window.scrollY)
                });
            }

            // macOS window dots
            const dotEls = document.querySelectorAll('.aig-dot, [class*="dot"], .aig-title-bar, [class*="title-bar"]');
            results.mac_dots = dotEls.length;

            return results;
        }""")

        print(f"\n  Panel details:")
        print(f"    Jobs panel: {panels_info.get('jobs_panel', 'NOT FOUND')}")
        print(f"    Cook panel: {panels_info.get('cook_panel', 'NOT FOUND')}")
        print(f"    Insight box: {panels_info.get('insight', 'NOT FOUND')}")
        print(f"    Stats: {panels_info.get('stats', [])}")
        print(f"    Avatars: {panels_info.get('avatars', [])}")
        print(f"    Chips: {panels_info.get('chips', [])}")
        print(f"    Mac dots count: {panels_info.get('mac_dots', 0)}")

        # Determine the infographic Y range
        # From initial scan: aig-stat-jobs at y~2958, aig-stat-cook at y~3593
        # The infographic section likely starts ~300px above stats and ends ~300px below insight

        # Use aig_info to find the bounding box
        if aig_info:
            aig_tops = [item['top'] for item in aig_info if item['top'] > 0]
            if aig_tops:
                infographic_start = min(aig_tops) - 200
                infographic_end = max([item['top'] + item['height'] for item in aig_info]) + 200
                infographic_start = max(0, infographic_start)
                print(f"\n  Infographic Y range: {infographic_start} - {infographic_end}px")
            else:
                # Fallback based on known stat positions
                infographic_start = 2700
                infographic_end = 4400
        else:
            infographic_start = 2700
            infographic_end = 4400

        infographic_center = (infographic_start + infographic_end) // 2
        infographic_height = infographic_end - infographic_start

        print(f"  Center: {infographic_center}px, Height: {infographic_height}px")

        # ===== TAKE ALL REQUIRED SCREENSHOTS =====

        # Screenshot A: Full page top (hero) - verify nothing broken
        print("\n[5] Screenshot A: Full page top viewport (hero)...")
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(400)
        path = os.path.join(OUTPUT_DIR, "A-full-page-top-hero.png")
        await page.screenshot(path=path, full_page=False)
        print(f"  Saved: A-full-page-top-hero.png")

        # Screenshot B: Infographic section overview (showing it between S2 and S3)
        print("\n[6] Screenshot B: Infographic section - overview showing position in page...")
        # Scroll to show start of infographic section
        await page.evaluate(f"window.scrollTo(0, {max(0, infographic_start - 100)})")
        await page.wait_for_timeout(400)
        path = os.path.join(OUTPUT_DIR, "B-infographic-section-overview.png")
        await page.screenshot(path=path, full_page=False)
        print(f"  Saved: B-infographic-section-overview.png (at scroll y={max(0, infographic_start-100)})")

        # Screenshot C: Steve Jobs panel specifically
        print("\n[7] Screenshot C: Steve Jobs panel (blue bars + +$344.5B stat + SJ avatar)...")
        # aig-stat-jobs is at y~2958, so scroll to ~2750
        jobs_scroll = max(0, 2750)
        await page.evaluate(f"window.scrollTo(0, {jobs_scroll})")
        await page.wait_for_timeout(400)
        path = os.path.join(OUTPUT_DIR, "C-steve-jobs-panel.png")
        await page.screenshot(path=path, full_page=False)
        print(f"  Saved: C-steve-jobs-panel.png (at scroll y={jobs_scroll})")

        # Screenshot D: Tim Cook panel specifically
        print("\n[8] Screenshot D: Tim Cook panel (green bars + +$3,353B stat + TC avatar)...")
        # aig-stat-cook is at y~3593, so scroll to ~3400
        cook_scroll = max(0, 3350)
        await page.evaluate(f"window.scrollTo(0, {cook_scroll})")
        await page.wait_for_timeout(400)
        path = os.path.join(OUTPUT_DIR, "D-tim-cook-panel.png")
        await page.screenshot(path=path, full_page=False)
        print(f"  Saved: D-tim-cook-panel.png (at scroll y={cook_scroll})")

        # Screenshot E: Insight callout box
        print("\n[9] Screenshot E: Insight callout box below panels...")
        # After Tim Cook panel + chips, insight should be around y=4100-4500
        insight_scroll = 4100
        if panels_info.get('insight') and panels_info['insight'].get('top', 0) > 0:
            insight_scroll = max(0, panels_info['insight']['top'] - 100)
        await page.evaluate(f"window.scrollTo(0, {insight_scroll})")
        await page.wait_for_timeout(400)
        path = os.path.join(OUTPUT_DIR, "E-insight-callout.png")
        await page.screenshot(path=path, full_page=False)
        print(f"  Saved: E-insight-callout.png (at scroll y={insight_scroll})")

        # Screenshot F: Both panels together (wider view)
        print("\n[10] Screenshot F: Both panels together wide view...")
        # Scroll to show Steve Jobs panel and start of Tim Cook panel
        await page.evaluate(f"window.scrollTo(0, 2600)")
        await page.wait_for_timeout(400)
        path = os.path.join(OUTPUT_DIR, "F-both-panels-wide.png")
        await page.screenshot(path=path, full_page=False)
        print(f"  Saved: F-both-panels-wide.png")

        # Screenshot G: amplify-founder image (existing image - should still be there)
        print("\n[11] Screenshot G: amplify-founder image (existing image check)...")
        amp_top = 935  # from previous discovery
        await page.evaluate(f"window.scrollTo(0, {max(0, amp_top - 80)})")
        await page.wait_for_timeout(400)
        path = os.path.join(OUTPUT_DIR, "G-amplify-founder-image.png")
        await page.screenshot(path=path, full_page=False)
        print(f"  Saved: G-amplify-founder-image.png (amplify-founder at y={amp_top})")

        # Screenshot H: vc-fomo image (existing image - should still be there)
        print("\n[12] Screenshot H: vc-fomo image (existing image check)...")
        fomo_top = 8597  # from previous discovery
        await page.evaluate(f"window.scrollTo(0, {max(0, fomo_top - 80)})")
        await page.wait_for_timeout(400)
        path = os.path.join(OUTPUT_DIR, "H-vc-fomo-image.png")
        await page.screenshot(path=path, full_page=False)
        print(f"  Saved: H-vc-fomo-image.png (vc-fomo at y={fomo_top})")

        # Screenshot I: Section 3 transition (Soul vs Skeleton Framework - should be below infographic)
        print("\n[13] Screenshot I: Section 3 - Soul vs Skeleton Framework (below infographic)...")
        # This should be after the insight callout, around y=4500-5500
        s3_scroll = infographic_end + 100
        await page.evaluate(f"window.scrollTo(0, {s3_scroll})")
        await page.wait_for_timeout(400)
        path = os.path.join(OUTPUT_DIR, "I-section3-below-infographic.png")
        await page.screenshot(path=path, full_page=False)
        print(f"  Saved: I-section3-below-infographic.png (at scroll y={s3_scroll})")

        # ===== DOM VERIFICATION CHECKS =====
        print("\n[14] Running DOM verification checks...")

        checks = await page.evaluate("""() => {
            const results = {};

            // Check 1: macOS dots (red/yellow/green) in panels
            const allEls = document.querySelectorAll('*');
            let macDotsFound = 0;
            let dotColors = [];

            for (const el of allEls) {
                const cls = el.className || '';
                if (typeof cls === 'string' && (cls.includes('aig-dot') || cls.includes('mac-dot') || cls.includes('window-dot'))) {
                    macDotsFound++;
                    const computed = window.getComputedStyle(el);
                    dotColors.push({
                        class: cls.substring(0, 50),
                        bgColor: computed.backgroundColor,
                        width: computed.width,
                        height: computed.height
                    });
                }
            }
            results.macDots = { count: macDotsFound, colors: dotColors.slice(0, 6) };

            // Check 2: Steve Jobs stat text
            const jobsStat = document.querySelector('.aig-stat-jobs, .aig-stat-primary.aig-stat-jobs');
            results.jobsStat = jobsStat ? {
                found: true,
                text: (jobsStat.innerText || '').trim(),
                color: window.getComputedStyle(jobsStat).color
            } : { found: false };

            // Check 3: Tim Cook stat text
            const cookStat = document.querySelector('.aig-stat-cook, .aig-stat-primary.aig-stat-cook');
            results.cookStat = cookStat ? {
                found: true,
                text: (cookStat.innerText || '').trim(),
                color: window.getComputedStyle(cookStat).color
            } : { found: false };

            // Check 4: Avatar circles (SJ and TC)
            const avatars = document.querySelectorAll('[class*="avatar"]');
            results.avatars = [];
            for (const av of avatars) {
                const computed = window.getComputedStyle(av);
                results.avatars.push({
                    class: av.className.substring(0, 60),
                    text: (av.innerText || '').trim().substring(0, 10),
                    borderRadius: computed.borderRadius,
                    width: computed.width,
                    bgColor: computed.backgroundColor
                });
            }

            // Check 5: Product chips
            const chips = document.querySelectorAll('[class*="chip"]');
            results.chipTexts = [];
            for (const chip of chips) {
                results.chipTexts.push((chip.innerText || '').trim().substring(0, 20));
            }

            // Check 6: Bar charts
            const bars = document.querySelectorAll('[class*="bar"], [class*="chart"]');
            results.chartBars = [];
            for (const bar of Array.from(bars).slice(0, 10)) {
                const computed = window.getComputedStyle(bar);
                results.chartBars.push({
                    class: bar.className.substring(0, 60),
                    bgColor: computed.backgroundColor,
                    height: computed.height
                });
            }

            // Check 7: Insight callout
            const insight = document.querySelector('[class*="insight"]');
            results.insightBox = insight ? {
                found: true,
                text: (insight.innerText || '').substring(0, 200).trim(),
                class: insight.className.substring(0, 80)
            } : { found: false };

            // Check 8: Section title text check (Soul vs Skeleton)
            let soulSkelFound = false;
            for (const el of allEls) {
                const text = el.innerText || '';
                if (text.includes('Soul') && text.includes('Skeleton') && el.children.length < 5) {
                    soulSkelFound = true;
                    break;
                }
            }
            results.soulVsSkeleton = soulSkelFound;

            // Check 9: Background color
            results.bgColor = window.getComputedStyle(document.body).backgroundColor;

            // Check 10: Title bar (macOS window chrome)
            const titleBars = document.querySelectorAll('[class*="title-bar"], [class*="titlebar"]');
            results.titleBars = titleBars.length;

            // Check 11: "Hero's Delusion" text (Section 2 content)
            let heroDelusionFound = false;
            for (const el of allEls) {
                const text = el.innerText || '';
                if (text.includes("Hero's Delusion") || text.includes('Heros Delusion') || text.includes("hero's delusion")) {
                    heroDelusionFound = true;
                    break;
                }
            }
            results.heroDelusionFound = heroDelusionFound;

            return results;
        }""")

        print(f"\n  macOS dots: {checks['macDots']}")
        print(f"  Steve Jobs stat: {checks['jobsStat']}")
        print(f"  Tim Cook stat: {checks['cookStat']}")
        print(f"  Avatars: {checks['avatars']}")
        print(f"  Chip texts: {checks['chipTexts']}")
        print(f"  Bar charts (first 5): {checks['chartBars'][:5]}")
        print(f"  Insight box: {checks['insightBox']}")
        print(f"  Soul vs Skeleton found: {checks['soulVsSkeleton']}")
        print(f"  Background: {checks['bgColor']}")
        print(f"  Title bars: {checks['titleBars']}")
        print(f"  Hero's Delusion found: {checks['heroDelusionFound']}")

        # Console summary
        errors = [m for m in console_msgs if m['type'] == 'error']
        warnings = [m for m in console_msgs if m['type'] == 'warning']
        print(f"\n  Console: {len(errors)} errors, {len(warnings)} warnings")
        for e in errors[:5]:
            print(f"    ERROR: {e['text'][:100]}")

        await browser.close()

        print("\n" + "=" * 60)
        print("SCREENSHOTS SAVED:")
        for f in sorted(os.listdir(OUTPUT_DIR)):
            fpath = os.path.join(OUTPUT_DIR, f)
            size = os.path.getsize(fpath)
            print(f"  {f} ({size:,} bytes)")

        return {
            'aig_elements': aig_info,
            'panels': panels_info,
            'checks': checks,
            'errors': errors,
            'main_wrapper': main_wrapper
        }


if __name__ == "__main__":
    asyncio.run(main())
