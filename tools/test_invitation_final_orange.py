#!/usr/bin/env python3
"""
Final investigation: what EXACTLY sets body background to orange on invitation page.
Check all 22 inline stylesheets for any body background rule that resolves to orange.
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

        # Check sheet [22] - the last inline one (11 rules) - this loads after our !important rule
        sheet22 = await page.evaluate("""
        () => {
            const sheets = Array.from(document.styleSheets);
            // Get all inline sheets
            const results = [];
            let si = 0;
            for (const sheet of sheets) {
                if (!sheet.href) { // inline
                    try {
                        const rules = Array.from(sheet.cssRules || []);
                        const allRuleTexts = rules.map(r => r.cssText ? r.cssText.substring(0, 300) : '').filter(r => r.length > 0);
                        if (allRuleTexts.some(r => r.includes('body') || r.includes('background') || r.includes('f1420b') || r.includes('241, 66'))) {
                            results.push({
                                sheetIndex: si,
                                ruleCount: rules.length,
                                rules: allRuleTexts
                            });
                        }
                    } catch(e) {
                        results.push({ sheetIndex: si, error: e.message });
                    }
                }
                si++;
            }
            return results;
        }
        """)
        print("Inline stylesheets with body/background/orange rules:")
        print(json.dumps(sheet22, indent=2))

        # Get ALL rules from ALL inline stylesheets that affect body background
        all_inline_body = await page.evaluate("""
        () => {
            const results = [];
            let si = 0;
            for (const sheet of document.styleSheets) {
                if (!sheet.href) {
                    try {
                        let ri = 0;
                        for (const rule of sheet.cssRules) {
                            const text = rule.cssText || '';
                            if ((text.includes('body') || text.includes(':root')) &&
                                text.includes('background')) {
                                results.push({
                                    sheetIndex: si,
                                    ruleIndex: ri,
                                    cssText: text.substring(0, 400)
                                });
                            }
                            ri++;
                        }
                    } catch(e) {}
                }
                si++;
            }
            return results;
        }
        """)
        print("\nAll inline rules touching body+background:")
        for r in all_inline_body:
            print(f"\n  [sheet {r['sheetIndex']}, rule {r['ruleIndex']}]:")
            print(f"  {r['cssText']}")

        # Check if any JS is setting body.style.backgroundColor directly
        js_body_style = await page.evaluate("""
        () => {
            return {
                bodyStyleBackground: document.body.style.background,
                bodyStyleBackgroundColor: document.body.style.backgroundColor,
                bodyStyleCSSText: document.body.style.cssText
            };
        }
        """)
        print("\nBody inline style (set via JS):")
        print(json.dumps(js_body_style, indent=2))

        # Check if WooCommerce or another plugin adds inline styles
        # Get the FULL content of ALL inline style tags
        all_style_ids = await page.evaluate("""
        () => {
            const styles = document.querySelectorAll('style');
            return Array.from(styles).map(s => ({
                id: s.id || '(no id)',
                length: s.textContent.length,
                hasOrange: s.textContent.includes('241, 66, 11') || s.textContent.includes('f1420b'),
                preview: s.textContent.substring(0, 100)
            }));
        }
        """)
        print("\nAll style tags with orange indicator:")
        for s in all_style_ids:
            if s['hasOrange']:
                print(f"  id={s['id']} len={s['length']} ORANGE FOUND - preview: {s['preview'][:80]}")

        # Check if the WP kit (elementor-frontend-legacy-css or similar) has it
        # List all link[rel=stylesheet] hrefs to understand full load order
        all_links = await page.evaluate("""
        () => {
            return Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(l => l.href);
        }
        """)
        print("\nAll external stylesheets (link tags):")
        for l in all_links:
            print(f"  {l.split('/')[-2:]}")

        # Check if WooCommerce or another plugin adds body background via PHP inline style
        # Check for any <style> that contains body { and rgb(241
        final_check = await page.evaluate("""
        () => {
            // Direct check: what computed body background property wins?
            // Use getComputedStyle to get the actual resolved value
            const computed = window.getComputedStyle(document.body);
            return {
                backgroundColor: computed.backgroundColor,
                background: computed.background.substring(0, 200),
                backgroundImage: computed.backgroundImage,
                // Check if bootstrap --bs-body-bg resolves to orange
                bsBodyBg: document.documentElement.style.getPropertyValue('--bs-body-bg'),
                // Walk up from body to html to find where orange comes from
                htmlBg: window.getComputedStyle(document.documentElement).backgroundColor
            };
        }
        """)
        print("\nFinal computed values:")
        print(json.dumps(final_check, indent=2))

        # DEFINITIVE: Force body to dark and see if it works
        await page.evaluate("""
        () => {
            document.body.style.setProperty('background-color', '#0a0e1a', 'important');
            document.body.style.setProperty('background', '#0a0e1a', 'important');
        }
        """)
        await page.wait_for_timeout(1000)
        await page.screenshot(path="/home/jared/projects/AI-CIV/aether/exports/screenshots/invitation-audit-2026-02-27/fixed-body-bg-test.png")
        print("\nScreenshot taken with forced dark body background")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
