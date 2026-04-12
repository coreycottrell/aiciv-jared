#!/usr/bin/env python3
"""
Final check: Is --bg being overridden to orange by any stylesheet?
"""

import asyncio
import json
from playwright.async_api import async_playwright

URL = "https://purebrain.ai/invitation/"
PASSWORD = "purebrain25"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        try:
            await page.goto(URL, wait_until="networkidle", timeout=30000)
        except:
            pass
        await page.wait_for_timeout(2000)

        pw = await page.query_selector("input[type='password']")
        if pw:
            await pw.fill(PASSWORD)
            sub = await page.query_selector("input[type='submit']")
            if sub:
                await sub.click()
            await page.wait_for_timeout(10000)
        await page.wait_for_timeout(3000)

        # All rules that define --bg across all stylesheets
        bg_definitions = await page.evaluate("""
        () => {
            const results = [];
            let si = 0;
            for (const sheet of document.styleSheets) {
                let ri = 0;
                try {
                    for (const rule of sheet.cssRules) {
                        if (rule.style) {
                            const bg = rule.style.getPropertyValue('--bg');
                            if (bg && bg.trim()) {
                                results.push({
                                    sheetIndex: si,
                                    ruleIndex: ri,
                                    href: sheet.href ? sheet.href.split('/').slice(-2).join('/') : 'INLINE',
                                    selector: rule.selectorText || '@rule',
                                    value: bg.trim()
                                });
                            }
                        }
                        ri++;
                    }
                } catch(e) {}
                si++;
            }
            return results;
        }
        """)
        print("All --bg CSS variable definitions:")
        print(json.dumps(bg_definitions, indent=2))

        # Check all :root definitions across all sheets
        all_root_rules = await page.evaluate("""
        () => {
            const results = [];
            let si = 0;
            for (const sheet of document.styleSheets) {
                try {
                    for (const rule of sheet.cssRules) {
                        const sel = rule.selectorText;
                        if (sel === ':root' || sel === 'body') {
                            results.push({
                                sheetIndex: si,
                                href: sheet.href ? sheet.href.split('/').slice(-2).join('/') : 'INLINE',
                                selector: sel,
                                text: rule.cssText.substring(0, 300)
                            });
                        }
                    }
                } catch(e) {}
                si++;
            }
            return results;
        }
        """)
        print("\nAll :root and body rules:")
        for r in all_root_rules:
            print(f"\n  [sheet {r['sheetIndex']}] {r['href']} | {r['selector']}:")
            print(f"  {r['text'][:200]}")

        # Resolve --bg at the body level
        bg_resolved = await page.evaluate("""
        () => {
            const rootBg = window.getComputedStyle(document.documentElement).getPropertyValue('--bg').trim();
            const bodyBg = window.getComputedStyle(document.body).getPropertyValue('--bg').trim();
            // Use a temp element styled with --bg
            const temp = document.createElement('div');
            document.body.appendChild(temp);
            temp.style.background = 'var(--bg)';
            const computed = window.getComputedStyle(temp).backgroundColor;
            document.body.removeChild(temp);
            return {
                rootBg,
                bodyBg,
                resolvedColor: computed
            };
        }
        """)
        print("\n--bg resolution:")
        print(json.dumps(bg_resolved, indent=2))

        # Check if WooCommerce global styles inject something
        # Check the wp-custom-css for any "body.wp-" or "body.page" patterns that might match
        match_classes = await page.evaluate("""
        () => {
            const bodyClasses = document.body.className.split(' ');
            const el = document.getElementById('wp-custom-css');
            if (!el) return null;
            const content = el.textContent;

            // Find rules that match body's classes
            const matched = bodyClasses.filter(cls =>
                cls.length > 3 && content.includes('body.' + cls)
            );
            // Check if any of those matched rules have background
            const matchedRules = [];
            for (const cls of matched) {
                const pattern = 'body.' + cls;
                const idx = content.indexOf(pattern);
                if (idx > -1) {
                    const ctx = content.substring(idx, idx + 400);
                    if (ctx.includes('background')) {
                        matchedRules.push({ cls, context: ctx.substring(0, 300) });
                    }
                }
            }
            return { bodyClasses, matchedRules };
        }
        """)
        print("\nwp-custom-css rules matching body classes with background:")
        print(json.dumps(match_classes, indent=2))

        # FINAL: Check what happens with each body class individually for background
        page_specific = await page.evaluate("""
        () => {
            const el = document.getElementById('wp-custom-css');
            if (!el) return null;
            const content = el.textContent;

            // Look for page-id-987 specifically
            const idx = content.indexOf('page-id-987');
            if (idx > -1) {
                return {
                    found: true,
                    context: content.substring(Math.max(0, idx - 100), idx + 500)
                };
            }
            return { found: false };
        }
        """)
        print("\nwp-custom-css page-id-987 rule:")
        print(json.dumps(page_specific, indent=2))

        # Check global-styles-inline-css for body background
        global_styles_body = await page.evaluate("""
        () => {
            const el = document.getElementById('global-styles-inline-css');
            if (!el) return null;
            const content = el.textContent;
            const idx = content.indexOf('body {');
            if (idx === -1) return { found: false };
            return {
                found: true,
                context: content.substring(idx, idx + 300)
            };
        }
        """)
        print("\nglobal-styles-inline-css body rule:")
        print(json.dumps(global_styles_body, indent=2))

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
