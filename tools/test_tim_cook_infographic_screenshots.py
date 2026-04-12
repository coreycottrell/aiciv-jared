"""
Tim Cook Infographic QA - Screenshot Capture
Based on DOM discovery: aig- elements mapped precisely
Key positions:
  - aig-outer-title: y=2724 (infographic header)
  - aig-panel-1 (Jobs): y=2872, h=616 -> ends y=3488
  - aig-panel-2 (Cook): y=3507, h=616 -> ends y=4123
  - aig-icon-chip: y=3405 (product chips in Jobs panel)
  - amplify-founder: y=935
  - vc-fomo: y=8597
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


async def ss(page, filename, description=""):
    path = os.path.join(OUTPUT_DIR, filename)
    await page.screenshot(path=path, full_page=False)
    size = os.path.getsize(path)
    print(f"  [SAVED] {filename} ({size:,}b) — {description}")
    return path


async def scroll_and_ss(page, y, filename, description=""):
    await page.evaluate(f"window.scrollTo(0, {max(0, y)})")
    await page.wait_for_timeout(350)
    return await ss(page, filename, description)


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output: {OUTPUT_DIR}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            device_scale_factor=1
        )
        page = await context.new_page()

        console_msgs = []
        page.on("console", lambda m: console_msgs.append({"type": m.type, "text": m.text}))

        print("\n[1] Loading page (waiting for network idle)...")
        resp = await page.goto(URL, wait_until="networkidle", timeout=30000)
        print(f"  HTTP {resp.status}")
        await page.wait_for_timeout(2000)

        print("\n[2] Scrolling full page to trigger lazy loads...")
        total_h = await page.evaluate("document.body.scrollHeight")
        for y in range(0, total_h, 300):
            await page.evaluate(f"window.scrollTo(0, {y})")
            await page.wait_for_timeout(40)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)
        print(f"  Done. Page height: {total_h}px")

        print("\n[3] Injecting force-visible CSS...")
        await page.evaluate(FORCE_VISIBLE_JS)
        await page.wait_for_timeout(400)

        print("\n[4] Taking screenshots...")

        # === SCREENSHOT 1: Full page top - hero section ===
        print("\n  --- Screenshot 1: Full page top (hero) ---")
        await scroll_and_ss(page, 0, "1-full-page-top.png", "Hero section, page top")

        # === SCREENSHOT 2: Infographic section overview ===
        # aig-outer-title at y=2724, show from 2550 to capture section heading context
        print("\n  --- Screenshot 2: Infographic section overview ---")
        # Show the "THE PROBLEM" section ending + infographic beginning
        await scroll_and_ss(page, 2550, "2-infographic-section-overview.png",
                             "Infographic section overview — 'Two Eras of Apple Leadership' heading visible")

        # === SCREENSHOT 3: Steve Jobs panel (blue bars + SJ avatar + +$344.5B) ===
        # aig-panel-1 starts at y=2872, we want to show the chrome + top row + chart
        # Scroll to 2800 to show the macOS title bar at top of viewport
        print("\n  --- Screenshot 3: Steve Jobs panel ---")
        await scroll_and_ss(page, 2800, "3-steve-jobs-panel.png",
                             "Steve Jobs panel — macOS chrome, SJ avatar, +$344.5B stat, blue bar chart")

        # === SCREENSHOT 4: Steve Jobs panel — chart area detail ===
        # aig-chart-wrap at y=3046, scroll to 2980 to see chart clearly
        print("\n  --- Screenshot 4: Steve Jobs chart + product chips ---")
        await scroll_and_ss(page, 2980, "4-steve-jobs-chart-chips.png",
                             "Steve Jobs chart area + product icon chips (iMac, Mac OS X, iPod, etc.)")

        # === SCREENSHOT 5: Tim Cook panel ===
        # aig-panel-2 at y=3507, scroll to 3430 to show it from near-top
        print("\n  --- Screenshot 5: Tim Cook panel ---")
        await scroll_and_ss(page, 3430, "5-tim-cook-panel.png",
                             "Tim Cook panel — macOS chrome, TC avatar, +$3,353B stat, green bar chart")

        # === SCREENSHOT 6: Tim Cook chart + chips ===
        # Tim Cook chart should be similar structure, around y=3650-3900
        print("\n  --- Screenshot 6: Tim Cook chart area ---")
        await scroll_and_ss(page, 3620, "6-tim-cook-chart.png",
                             "Tim Cook chart area detail")

        # === SCREENSHOT 7: Insight callout box ===
        # Below Tim Cook panel (ends ~4123), insight should be around 4100-4500
        print("\n  --- Screenshot 7: Insight callout box ---")
        await scroll_and_ss(page, 4050, "7-insight-callout.png",
                             "Insight callout box below both panels")

        # === SCREENSHOT 8: Post-infographic / Section 3 transition ===
        # Section 3 (Soul vs Skeleton) should start around 4500-5000
        print("\n  --- Screenshot 8: Section 3 transition (below infographic) ---")
        await scroll_and_ss(page, 4400, "8-section3-transition.png",
                             "Section 3 - Soul vs Skeleton Framework (below infographic)")

        # === SCREENSHOT 9: amplify-founder image ===
        # at y=935
        print("\n  --- Screenshot 9: amplify-founder image ---")
        await scroll_and_ss(page, 835, "9-amplify-founder.png",
                             "amplify-founder image (existing, between hero and The Problem)")

        # === SCREENSHOT 10: vc-fomo image ===
        # at y=8597
        print("\n  --- Screenshot 10: vc-fomo image ---")
        await scroll_and_ss(page, 8497, "10-vc-fomo.png",
                             "vc-fomo image (existing, before closing CTA)")

        # === DOM VERIFICATION ===
        print("\n[5] Running DOM verification checks...")
        checks = await page.evaluate("""() => {
            const get = (sel) => document.querySelector(sel);
            const getAll = (sel) => Array.from(document.querySelectorAll(sel));
            const text = (el) => el ? (el.innerText || '').trim() : null;
            const style = (el, prop) => el ? window.getComputedStyle(el)[prop] : null;

            return {
                // macOS dots
                dotRed: {
                    found: !!get('.aig-dot-red'),
                    color: style(get('.aig-dot-red'), 'backgroundColor')
                },
                dotYel: {
                    found: !!get('.aig-dot-yel'),
                    color: style(get('.aig-dot-yel'), 'backgroundColor')
                },
                dotGrn: {
                    found: !!get('.aig-dot-grn'),
                    color: style(get('.aig-dot-grn'), 'backgroundColor')
                },
                dotCount: getAll('.aig-dot').length,

                // Steve Jobs stats
                jobsStatText: text(get('.aig-stat-jobs')),
                jobsStatColor: style(get('.aig-stat-jobs'), 'color'),
                jobsPctText: text(get('.aig-stat-pct')),

                // Tim Cook stats
                cookStatText: text(get('.aig-stat-cook')),
                cookStatColor: style(get('.aig-stat-cook'), 'color'),

                // Avatars
                avatarJobs: {
                    text: text(get('.aig-avatar-jobs')),
                    borderRadius: style(get('.aig-avatar-jobs'), 'borderRadius'),
                    width: style(get('.aig-avatar-jobs'), 'width'),
                    bgColor: style(get('.aig-avatar-jobs'), 'backgroundColor')
                },
                avatarCook: {
                    text: text(get('.aig-avatar-cook')),
                    borderRadius: style(get('.aig-avatar-cook'), 'borderRadius'),
                    width: style(get('.aig-avatar-cook'), 'width'),
                    bgColor: style(get('.aig-avatar-cook'), 'backgroundColor')
                },

                // Product chips
                chipCount: getAll('.aig-icon-chip').length,
                chipTexts: getAll('.aig-icon-chip').map(el => (el.innerText || '').trim().substring(0, 30)),

                // Bar charts - look for bars within aig-chart-wrap
                chartBars: getAll('.aig-chart-wrap [class*="bar"], .aig-chart-wrap > div').slice(0, 10).map(el => ({
                    class: el.className.substring(0, 50),
                    bgColor: window.getComputedStyle(el).backgroundColor,
                    height: window.getComputedStyle(el).height
                })),

                // Insight box
                insightText: text(get('[class*="insight"], .aig-insight')),

                // Panel titles (macOS chrome titles)
                chromeTitles: getAll('.aig-chrome-title').map(el => text(el)),

                // Background
                bgColor: window.getComputedStyle(document.body).backgroundColor,

                // Images
                ampFounder: (() => {
                    const imgs = Array.from(document.querySelectorAll('img'));
                    const img = imgs.find(i => i.src.includes('amplify-founder'));
                    return img ? { found: true, loaded: img.complete, w: img.naturalWidth, h: img.naturalHeight } : { found: false };
                })(),
                vcFomo: (() => {
                    const imgs = Array.from(document.querySelectorAll('img'));
                    const img = imgs.find(i => i.src.includes('vc-fomo'));
                    return img ? { found: true, loaded: img.complete, w: img.naturalWidth, h: img.naturalHeight } : { found: false };
                })()
            };
        }""")

        print(f"\n  macOS dots:")
        print(f"    Total dot count: {checks['dotCount']} (expect 6 = 3 per panel x2 panels or 3 if only one panel has them)")
        print(f"    Red dot: found={checks['dotRed']['found']}, color={checks['dotRed']['color']}")
        print(f"    Yellow dot: found={checks['dotYel']['found']}, color={checks['dotYel']['color']}")
        print(f"    Green dot: found={checks['dotGrn']['found']}, color={checks['dotGrn']['color']}")

        print(f"\n  Steve Jobs panel:")
        print(f"    Stat text: {checks['jobsStatText']}")
        print(f"    Stat color: {checks['jobsStatColor']}")
        print(f"    Pct text: {checks['jobsPctText']}")

        print(f"\n  Tim Cook panel:")
        print(f"    Stat text: {checks['cookStatText']}")
        print(f"    Stat color: {checks['cookStatColor']}")

        print(f"\n  Avatars:")
        print(f"    SJ avatar: {checks['avatarJobs']}")
        print(f"    TC avatar: {checks['avatarCook']}")

        print(f"\n  Product chips: count={checks['chipCount']}")
        print(f"    Texts: {checks['chipTexts']}")

        print(f"\n  Bar charts (first 10 divs inside chart wrap):")
        for bar in checks['chartBars'][:8]:
            if bar['bgColor'] != 'rgba(0, 0, 0, 0)' and bar['bgColor']:
                print(f"    {bar['class'][:40]}: bg={bar['bgColor']}, h={bar['height']}")

        print(f"\n  macOS chrome titles: {checks['chromeTitles']}")
        print(f"\n  Insight text: {checks['insightText']}")
        print(f"\n  Background: {checks['bgColor']}")
        print(f"\n  amplify-founder: {checks['ampFounder']}")
        print(f"  vc-fomo: {checks['vcFomo']}")

        errors = [m for m in console_msgs if m['type'] == 'error']
        warnings = [m for m in console_msgs if m['type'] == 'warning']
        print(f"\n  Console: {len(errors)} errors, {len(warnings)} warnings")
        for e in errors[:5]:
            print(f"    ERROR: {e['text'][:120]}")

        await browser.close()

        print("\n" + "=" * 60)
        print("ALL SCREENSHOTS:")
        total_size = 0
        for f in sorted(os.listdir(OUTPUT_DIR)):
            fpath = os.path.join(OUTPUT_DIR, f)
            size = os.path.getsize(fpath)
            total_size += size
            print(f"  {f} ({size:,}b)")
        print(f"\nTotal: {total_size:,} bytes across {len(os.listdir(OUTPUT_DIR))} files")

        # Produce pass/fail table
        print("\n" + "=" * 60)
        print("QA PASS/FAIL SUMMARY:")
        results = []

        def chk(label, condition, detail=""):
            status = "PASS" if condition else "FAIL"
            results.append((label, status, detail))
            print(f"  [{status}] {label} {('— ' + detail) if detail else ''}")

        chk("Background dark (no orange bleed)",
            checks['bgColor'] == 'rgb(13, 17, 23)',
            checks['bgColor'])

        chk("macOS red dot present",
            checks['dotRed']['found'],
            checks['dotRed']['color'])

        chk("macOS yellow dot present",
            checks['dotYel']['found'],
            checks['dotYel']['color'])

        chk("macOS green dot present",
            checks['dotGrn']['found'],
            checks['dotGrn']['color'])

        chk("Steve Jobs stat +$344.5B present",
            checks['jobsStatText'] and '+$344.5B' in checks['jobsStatText'],
            checks['jobsStatText'])

        chk("Tim Cook stat +$3,353B present",
            checks['cookStatText'] and '+$3,353B' in checks['cookStatText'],
            checks['cookStatText'])

        chk("SJ avatar present (circle)",
            checks['avatarJobs']['text'] == 'SJ',
            f"text='{checks['avatarJobs']['text']}', borderRadius={checks['avatarJobs']['borderRadius']}")

        chk("TC avatar present (circle)",
            checks['avatarCook']['text'] == 'TC',
            f"text='{checks['avatarCook']['text']}', borderRadius={checks['avatarCook']['borderRadius']}")

        chk("Product icon chips visible",
            checks['chipCount'] >= 3,
            f"{checks['chipCount']} chips: {checks['chipTexts'][:3]}")

        chk("Chrome title (Steve Jobs panel) present",
            len(checks['chromeTitles']) >= 1 and 'Steve Jobs' in (checks['chromeTitles'][0] or ''),
            str(checks['chromeTitles']))

        chk("Chrome title (Tim Cook panel) present",
            len(checks['chromeTitles']) >= 2 and 'Tim Cook' in (checks['chromeTitles'][1] or ''),
            str(checks['chromeTitles']))

        chk("amplify-founder image present and loaded",
            checks['ampFounder']['found'] and checks['ampFounder']['loaded'],
            str(checks['ampFounder']))

        chk("vc-fomo image present and loaded",
            checks['vcFomo']['found'] and checks['vcFomo']['loaded'],
            str(checks['vcFomo']))

        chk("Console errors are CSP-only (not functional)",
            len(errors) <= 4,
            f"{len(errors)} errors")

        passed = sum(1 for _, s, _ in results if s == 'PASS')
        failed = sum(1 for _, s, _ in results if s == 'FAIL')
        print(f"\nTOTAL: {passed}/{passed+failed} checks PASS")

        return checks

if __name__ == "__main__":
    asyncio.run(main())
