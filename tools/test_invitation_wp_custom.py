#!/usr/bin/env python3
"""
Check wp-custom-css (the plugin CSS) for body background rules that cause the orange.
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

        # Get the wp-custom-css body background rules
        wp_custom_body = await page.evaluate("""
        () => {
            const el = document.getElementById('wp-custom-css');
            if (!el) return { found: false };

            const content = el.textContent;

            // Find body-related rules
            // Parse crudely by splitting on closing braces
            const sections = content.split('}');
            const bodyBgSections = sections.filter(s =>
                s.includes('body') &&
                (s.includes('background') || s.includes('background-color')) &&
                !s.includes('body.single-post') &&
                !s.includes('body.blog') &&
                !s.includes('body.category') &&
                !s.includes('body.page-id-95') &&
                !s.includes('body .') &&
                !s.includes('body > ')
            );

            // Also find what's in wp-custom-css around line with "body {"
            const lines = content.split('\\n');
            const bodyLines = [];
            for (let i = 0; i < lines.length; i++) {
                if (lines[i].trim().startsWith('body {') || lines[i].trim() === 'body,') {
                    bodyLines.push({ lineNum: i, context: lines.slice(Math.max(0, i-2), i+10).join('\\n') });
                }
            }

            return {
                found: true,
                totalLength: content.length,
                bodyBgSections: bodyBgSections.slice(0, 10),
                bodyLineContexts: bodyLines
            };
        }
        """)
        print("wp-custom-css body background analysis:")
        print(json.dumps(wp_custom_body, indent=2))

        # Now let's find the exact loaded order of these stylesheet injections
        # The wp-custom-css comes from <style id="wp-custom-css"> and loads AFTER the page inline style
        # Check if the plugin CSS inside wp-custom-css sets body bg
        plugin_body_rule = await page.evaluate("""
        () => {
            // wp-custom-css is a <style> tag that loads last (it's WP Additional CSS)
            // It will override the page inline CSS unless the inline has higher specificity
            const el = document.getElementById('wp-custom-css');
            if (!el) return null;

            const content = el.textContent;

            // Find: body { ... background ... } without specific class qualifiers
            // Use regex to find bare body { background } rules
            const matches = content.match(/(?:^|\\n)\\s*body\\s*\\{[^}]+background[^}]+}/gm);
            return {
                matches: matches,
                // Also look for the starter-starter rule or bare body rule
                hasBodyDark: content.includes('#0a0e1a') || content.includes('10, 14, 26'),
                hasBodyOrange: content.includes('#f1420b') && content.includes('body {'),
                // Find the section of wp-custom-css that might set body background
                snippet_around_body: (() => {
                    const idx = content.indexOf('\\nbody {');
                    if (idx === -1) return null;
                    return content.substring(idx, idx + 500);
                })()
            };
        }
        """)
        print("\nPlugin body rule in wp-custom-css:")
        print(json.dumps(plugin_body_rule, indent=2))

        # Get the DOM ordering - which style tag comes LAST (lowest in the DOM = highest priority)
        dom_order = await page.evaluate("""
        () => {
            const styles = document.querySelectorAll('style');
            return Array.from(styles).map((s, i) => ({
                domIndex: i,
                id: s.id || '(no id)',
                length: s.textContent.length
            }));
        }
        """)
        print("\nAll style tags in DOM order (last wins):")
        for s in dom_order:
            print(f"  [{s['domIndex']}] id={s['id']} len={s['length']}")

        # Check which style element comes AFTER the page's inline CSS (no id, 27695 chars)
        # Find sheet index of wp-custom-css vs the page's inline style
        sheet_order = await page.evaluate("""
        () => {
            const sheets = Array.from(document.styleSheets);
            const results = [];
            sheets.forEach((sheet, i) => {
                if (!sheet.href) {
                    try {
                        const rules = sheet.cssRules;
                        if (rules.length > 100) { // Only non-trivial sheets
                            const firstRule = rules[0] ? rules[0].cssText.substring(0, 80) : '';
                            results.push({ sheetIndex: i, ruleCount: rules.length, firstRule });
                        }
                    } catch(e) {}
                }
            });
            return results;
        }
        """)
        print("\nNon-trivial inline sheets in cascade order:")
        for s in sheet_order:
            print(f"  [sheet {s['sheetIndex']}] {s['ruleCount']} rules - first: {s['firstRule'][:60]}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
