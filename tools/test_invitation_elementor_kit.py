#!/usr/bin/env python3
"""
Find the Elementor kit stylesheet URL and what --e-global-color-black is set to.
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

        # Get --e-global-color-black from root
        kit_vars = await page.evaluate("""
        () => {
            const rootStyle = window.getComputedStyle(document.documentElement);
            const eBlack = rootStyle.getPropertyValue('--e-global-color-black');
            const eText = rootStyle.getPropertyValue('--e-global-color-text');
            const ePrimary = rootStyle.getPropertyValue('--e-global-color-primary');
            const eSecondary = rootStyle.getPropertyValue('--e-global-color-secondary');

            // Find where --e-global-color-black is defined
            const sources = [];
            for (const sheet of document.styleSheets) {
                try {
                    for (const rule of sheet.cssRules) {
                        if (rule.selectorText === ':root' && rule.style) {
                            const val = rule.style.getPropertyValue('--e-global-color-black');
                            if (val) {
                                sources.push({
                                    href: sheet.href ? sheet.href.split('/').slice(-3).join('/') : 'inline',
                                    value: val,
                                    ruleSnippet: rule.cssText.substring(0, 500)
                                });
                            }
                        }
                    }
                } catch(e) {}
            }

            return {
                eGlobalColorBlack: eBlack.trim(),
                eGlobalColorText: eText.trim(),
                eGlobalColorPrimary: ePrimary.trim(),
                eGlobalColorSecondary: eSecondary.trim(),
                sources
            };
        }
        """)
        print("Elementor kit CSS variables:")
        print(json.dumps(kit_vars, indent=2))

        # List all loaded stylesheets
        all_sheets = await page.evaluate("""
        () => {
            return Array.from(document.styleSheets).map((s, i) => ({
                index: i,
                href: s.href || 'inline',
                ruleCount: (() => { try { return (s.cssRules || s.rules).length; } catch(e) { return 'cors-blocked'; } })()
            }));
        }
        """)
        print("\nAll loaded stylesheets:")
        for s in all_sheets:
            print(f"  [{s['index']}] {s['href'].split('/')[-2:]} ({s['ruleCount']} rules)")

        # Find the artistics style.css body rule and check specificity chain
        # The theme sets body { background-color: var(--e-global-color-black); }
        # If kit-10 defines --e-global-color-black: #f1420b then body = orange
        elementor_kit_vars = await page.evaluate("""
        () => {
            // Find the elementor-kit CSS file
            const results = {};
            for (const sheet of document.styleSheets) {
                const href = sheet.href || '';
                if (href.includes('post-10') || href.includes('kit')) {
                    try {
                        const rules = sheet.cssRules || sheet.rules;
                        for (const rule of rules) {
                            if (rule.selectorText === ':root') {
                                results[href.split('/').slice(-2).join('/')] = rule.cssText.substring(0, 1000);
                            }
                        }
                    } catch(e) {
                        results[href] = 'cors-blocked: ' + e.message;
                    }
                }
            }
            return results;
        }
        """)
        print("\nElementor kit (post-10) :root rules:")
        print(json.dumps(elementor_kit_vars, indent=2))

        # Check all inline :root rules
        inline_roots = await page.evaluate("""
        () => {
            const results = [];
            const styles = document.querySelectorAll('style');
            for (const s of styles) {
                const content = s.textContent;
                if (content.includes('--e-global-color-black') || content.includes('e-global-color')) {
                    const match = content.match(/--e-global-color-black[^;]+;/);
                    results.push({
                        id: s.id,
                        match: match ? match[0] : null,
                        snippet: content.substring(0, 200)
                    });
                }
            }
            return results;
        }
        """)
        print("\nInline styles with --e-global-color-black:")
        print(json.dumps(inline_roots, indent=2))

        # What order are stylesheets loaded?  Check what comes AFTER the invitation page's inline style
        # The inline style has body { background: #0a0e1a !important } but body still shows orange
        # So something inline AFTER it must override with higher specificity or later order
        # Let's find all body rules across ALL stylesheets in cascade order
        all_body_bg_rules = await page.evaluate("""
        () => {
            const rules = [];
            let si = 0;
            for (const sheet of document.styleSheets) {
                let ri = 0;
                try {
                    for (const rule of sheet.cssRules) {
                        const sel = rule.selectorText || '';
                        if (rule.style && rule.style.backgroundColor &&
                            (sel === 'body' || sel.endsWith('body') || sel === ':root')) {
                            const bg = rule.style.backgroundColor;
                            if (bg && bg !== '') {
                                rules.push({
                                    sheetIndex: si,
                                    ruleIndex: ri,
                                    href: sheet.href ? sheet.href.split('/').slice(-2).join('/') : 'INLINE',
                                    selector: sel,
                                    backgroundColor: bg,
                                    hasImportant: rule.cssText.includes('!important')
                                });
                            }
                        }
                        ri++;
                    }
                } catch(e) {}
                si++;
            }
            return rules;
        }
        """)
        print("\nAll body background-color rules in cascade order:")
        for r in all_body_bg_rules:
            imp = "!important" if r['hasImportant'] else ""
            print(f"  [sheet {r['sheetIndex']}, rule {r['ruleIndex']}] {r['href']} | {r['selector']} {{ bg: {r['backgroundColor']} {imp} }}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
