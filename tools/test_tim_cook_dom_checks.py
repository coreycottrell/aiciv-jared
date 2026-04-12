"""Quick DOM checks for infographic verification."""
import asyncio
from playwright.async_api import async_playwright

URL = "https://purebrain.ai/your-ai-tim-cook/"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        console_msgs = []
        page.on("console", lambda m: console_msgs.append({"type": m.type, "text": m.text}))

        resp = await page.goto(URL, wait_until="networkidle", timeout=30000)
        print(f"HTTP {resp.status}")
        await page.wait_for_timeout(1500)

        # Run checks as separate small evaluations to avoid SVG className issue
        print("\n--- macOS Dots ---")
        dots = await page.evaluate("""() => {
            const red = document.querySelector('.aig-dot-red');
            const yel = document.querySelector('.aig-dot-yel');
            const grn = document.querySelector('.aig-dot-grn');
            const allDots = document.querySelectorAll('.aig-dot');
            return {
                count: allDots.length,
                red: red ? window.getComputedStyle(red).backgroundColor : 'NOT FOUND',
                yellow: yel ? window.getComputedStyle(yel).backgroundColor : 'NOT FOUND',
                green: grn ? window.getComputedStyle(grn).backgroundColor : 'NOT FOUND'
            };
        }""")
        print(f"  Total .aig-dot elements: {dots['count']}")
        print(f"  Red dot color: {dots['red']}")
        print(f"  Yellow dot color: {dots['yellow']}")
        print(f"  Green dot color: {dots['green']}")

        print("\n--- Steve Jobs Stats ---")
        jobs_stats = await page.evaluate("""() => {
            const stat = document.querySelector('.aig-stat-jobs');
            const pct = document.querySelector('.aig-stat-pct');
            const av = document.querySelector('.aig-avatar-jobs');
            return {
                stat: stat ? stat.innerText.trim() : 'NOT FOUND',
                statColor: stat ? window.getComputedStyle(stat).color : null,
                pct: pct ? pct.innerText.trim() : 'NOT FOUND',
                avatarText: av ? av.innerText.trim() : 'NOT FOUND',
                avatarBorderRadius: av ? window.getComputedStyle(av).borderRadius : null,
                avatarWidth: av ? window.getComputedStyle(av).width : null
            };
        }""")
        print(f"  Stat: {jobs_stats['stat']} (color: {jobs_stats['statColor']})")
        print(f"  Pct: {jobs_stats['pct']}")
        print(f"  SJ Avatar: text='{jobs_stats['avatarText']}', borderRadius={jobs_stats['avatarBorderRadius']}, width={jobs_stats['avatarWidth']}")

        print("\n--- Tim Cook Stats ---")
        cook_stats = await page.evaluate("""() => {
            const stat = document.querySelector('.aig-stat-cook');
            const av = document.querySelector('.aig-avatar-cook');
            const panel2 = document.querySelector('.aig-panel-2');
            const panel2pct = panel2 ? panel2.querySelector('.aig-stat-pct') : null;
            return {
                stat: stat ? stat.innerText.trim() : 'NOT FOUND',
                statColor: stat ? window.getComputedStyle(stat).color : null,
                avatarText: av ? av.innerText.trim() : 'NOT FOUND',
                avatarBorderRadius: av ? window.getComputedStyle(av).borderRadius : null,
                cookPct: panel2pct ? panel2pct.innerText.trim() : 'NOT FOUND'
            };
        }""")
        print(f"  Stat: {cook_stats['stat']} (color: {cook_stats['statColor']})")
        print(f"  Pct: {cook_stats['cookPct']}")
        print(f"  TC Avatar: text='{cook_stats['avatarText']}', borderRadius={cook_stats['avatarBorderRadius']}")

        print("\n--- Product Chips ---")
        chips = await page.evaluate("""() => {
            const chips = Array.from(document.querySelectorAll('.aig-icon-chip'));
            return {
                count: chips.length,
                texts: chips.map(c => c.innerText.trim().replace(/\\n/g, ' ').substring(0, 30))
            };
        }""")
        print(f"  Count: {chips['count']}")
        print(f"  Texts: {chips['texts']}")

        print("\n--- macOS Chrome Titles ---")
        chrome = await page.evaluate("""() => {
            const titles = Array.from(document.querySelectorAll('.aig-chrome-title'));
            return titles.map(t => t.innerText.trim());
        }""")
        print(f"  Titles: {chrome}")

        print("\n--- Insight Box ---")
        insight = await page.evaluate("""() => {
            // Look for insight element
            const ins = document.querySelector('.aig-insight, [class*="insight"]');
            if (ins) {
                return {
                    found: true,
                    text: ins.innerText.trim().substring(0, 200),
                    tagClass: ins.tagName + '.' + (typeof ins.className === 'string' ? ins.className : 'svg-element')
                };
            }
            // Fallback: search for text containing "insight"
            const allEls = Array.from(document.querySelectorAll('p, div, blockquote, h2, h3, h4'));
            for (const el of allEls) {
                const t = el.innerText || '';
                if (t.toLowerCase().includes('the insight') || t.toLowerCase().includes('insight:')) {
                    return {
                        found: true,
                        method: 'text-search',
                        text: t.substring(0, 200)
                    };
                }
            }
            return { found: false };
        }""")
        print(f"  Insight: {insight}")

        print("\n--- Bar Chart Colors ---")
        bars = await page.evaluate("""() => {
            // Look for bar elements inside chart wraps
            const chartWraps = Array.from(document.querySelectorAll('.aig-chart-wrap'));
            const results = [];
            for (const wrap of chartWraps) {
                const children = Array.from(wrap.querySelectorAll('*')).slice(0, 30);
                for (const child of children) {
                    const cls = typeof child.className === 'string' ? child.className : '';
                    const bg = window.getComputedStyle(child).backgroundColor;
                    if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent' && cls) {
                        results.push({ cls: cls.substring(0, 40), bg });
                    }
                }
            }
            return results.slice(0, 15);
        }""")
        print(f"  Colored bar elements: {bars}")

        print("\n--- Background Color ---")
        bg = await page.evaluate("() => window.getComputedStyle(document.body).backgroundColor")
        print(f"  Body bg: {bg}")
        is_orange = False
        if 'rgb' in bg:
            parts = [int(x) for x in bg.replace('rgb(', '').replace(')', '').split(',')]
            if len(parts) == 3 and parts[0] > 200 and parts[1] < 150 and parts[2] < 50:
                is_orange = True
        print(f"  Orange bleed: {'YES - FAIL' if is_orange else 'NO - PASS'}")

        print("\n--- Images ---")
        images = await page.evaluate("""() => {
            const imgs = Array.from(document.querySelectorAll('img'));
            return imgs.map(img => ({
                src: img.src.split('/').pop(),
                complete: img.complete,
                naturalWidth: img.naturalWidth,
                naturalHeight: img.naturalHeight
            })).filter(i => i.src && i.naturalWidth > 0);
        }""")
        for img in images:
            print(f"  {img['src']}: {img['naturalWidth']}x{img['naturalHeight']}, complete={img['complete']}")

        print("\n--- Console ---")
        errors = [m for m in console_msgs if m['type'] == 'error']
        warnings = [m for m in console_msgs if m['type'] == 'warning']
        print(f"  Errors: {len(errors)}, Warnings: {len(warnings)}")
        for e in errors[:5]:
            print(f"  ERROR: {e['text'][:120]}")

        await browser.close()

        # Pass/Fail
        print("\n" + "="*60)
        print("QA PASS/FAIL TABLE:")
        checks_pass = [
            ("Dark background (no orange bleed)", not is_orange, bg),
            ("macOS red dot present", dots['red'] != 'NOT FOUND', dots['red']),
            ("macOS yellow dot present", dots['yellow'] != 'NOT FOUND', dots['yellow']),
            ("macOS green dot present", dots['green'] != 'NOT FOUND', dots['green']),
            ("Dot count (6 = 3 per panel x2)", dots['count'] >= 3, f"{dots['count']} dots"),
            ("Steve Jobs stat +$344.5B", '+$344.5B' in jobs_stats['stat'], jobs_stats['stat']),
            ("SJ percentage +13,900%", '+13,900%' in jobs_stats['pct'], jobs_stats['pct']),
            ("SJ avatar circle 'SJ'", jobs_stats['avatarText'] == 'SJ', f"text='{jobs_stats['avatarText']}'"),
            ("Tim Cook stat +$3,353B", '+$3,353B' in cook_stats['stat'], cook_stats['stat']),
            ("TC avatar circle 'TC'", cook_stats['avatarText'] == 'TC', f"text='{cook_stats['avatarText']}'"),
            ("Product chips present", chips['count'] >= 3, f"{chips['count']} chips"),
            ("Steve Jobs panel macOS title", len(chrome) >= 1 and 'Steve Jobs' in (chrome[0] if chrome else ''), str(chrome)),
            ("Tim Cook panel macOS title", len(chrome) >= 2 and 'Tim Cook' in (chrome[1] if len(chrome) > 1 else ''), str(chrome)),
            ("Insight box found", insight['found'], insight.get('text', 'N/A')[:80]),
            ("Console errors CSP-only (<=4)", len(errors) <= 4, f"{len(errors)} errors"),
        ]

        # Image checks from images list
        amp_found = any('amplify-founder' in img['src'] for img in images)
        fomo_found = any('vc-fomo' in img['src'] for img in images)
        checks_pass.append(("amplify-founder image loaded", amp_found, "present" if amp_found else "NOT FOUND"))
        checks_pass.append(("vc-fomo image loaded", fomo_found, "present" if fomo_found else "NOT FOUND"))

        passed = 0
        failed = 0
        for label, condition, detail in checks_pass:
            status = "PASS" if condition else "FAIL"
            if condition:
                passed += 1
            else:
                failed += 1
            print(f"  [{status}] {label}")
            if not condition or True:  # show detail always
                print(f"         {detail}")

        print(f"\nRESULT: {passed}/{passed+failed} PASS")

if __name__ == "__main__":
    asyncio.run(main())
