#!/usr/bin/env python3
"""Check theme stylesheet rules that could override link colors."""
import time
from playwright.sync_api import sync_playwright

JS_CODE = """() => {
    // Check the artistics theme stylesheet (sheet 11)
    let themeRules = [];
    let allImportantColorRulesInTheme = [];

    for (const sheet of document.styleSheets) {
        const href = sheet.href || '';
        if (!href.includes('artistics/style.css') && !href.includes('css-variable.css')) continue;

        try {
            for (let i = 0; i < sheet.cssRules.length; i++) {
                const rule = sheet.cssRules[i];
                if (!rule.selectorText || !rule.style) continue;

                // Any rule with color !important
                if (rule.style.color && rule.style.getPropertyPriority('color') === 'important') {
                    allImportantColorRulesInTheme.push({
                        ruleIdx: i,
                        selector: rule.selectorText.substring(0, 200),
                        color: rule.style.color,
                        sheet: href.split('/').pop()
                    });
                }

                // Rules that match generic 'a' or 'post-entry a'
                if (rule.selectorText.includes('post-entry') || rule.selectorText.includes('.post-content')) {
                    if (rule.style.color) {
                        themeRules.push({
                            ruleIdx: i,
                            selector: rule.selectorText.substring(0, 200),
                            color: rule.style.color,
                            priority: rule.style.getPropertyPriority('color'),
                            sheet: href.split('/').pop()
                        });
                    }
                }
            }
        } catch(e) {
            themeRules.push({error: e.message, sheet: href});
        }
    }

    // Also check for Elementor Kit inline styles
    let elementorRules = [];
    for (const sheet of document.styleSheets) {
        const ownerNode = sheet.ownerNode;
        if (!ownerNode) continue;
        const id = ownerNode.id || '';
        if (!id.includes('global-styles') && !id.includes('elementor')) continue;

        try {
            for (const rule of sheet.cssRules) {
                if (!rule.selectorText || !rule.style) continue;
                if (rule.style.color) {
                    // Check if it could affect links
                    if (rule.selectorText.includes('a') || rule.selectorText.includes('--')) {
                        elementorRules.push({
                            selector: rule.selectorText.substring(0, 150),
                            color: rule.style.color,
                            priority: rule.style.getPropertyPriority('color'),
                            sheetId: id
                        });
                    }
                }
                // Check for CSS variable definitions
                if (rule.style.cssText.includes('--e-global-color')) {
                    elementorRules.push({
                        selector: rule.selectorText.substring(0, 100),
                        cssText: rule.style.cssText.substring(0, 300),
                        sheetId: id
                    });
                }
            }
        } catch(e) {}
    }

    // Check the css-variable.css for link color vars
    let cssVarRules = [];
    for (const sheet of document.styleSheets) {
        const href = sheet.href || '';
        if (!href.includes('css-variable')) continue;
        try {
            for (const rule of sheet.cssRules) {
                if (!rule.selectorText || !rule.style) continue;
                if (rule.style.cssText.includes('--') || rule.style.color) {
                    cssVarRules.push({
                        selector: rule.selectorText.substring(0, 100),
                        cssText: rule.style.cssText.substring(0, 300)
                    });
                }
            }
        } catch(e) {}
    }

    // Check computed values for key CSS variables
    const root = document.documentElement;
    const rootStyle = getComputedStyle(root);
    const vars = {};
    for (const prop of ['--e-global-color-primary', '--e-global-color-secondary', '--e-global-color-accent',
                         '--e-global-color-text', '--e-global-color-black',
                         '--bs-link-color', '--bs-link-color-rgb']) {
        vars[prop] = rootStyle.getPropertyValue(prop).trim();
    }

    return {
        themeRules: themeRules.slice(0, 20),
        allImportantColorInTheme: allImportantColorRulesInTheme.slice(0, 10),
        elementorRules: elementorRules.slice(0, 20),
        cssVarRules: cssVarRules.slice(0, 10),
        cssVars: vars
    };
}"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    page.goto("https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/",
              wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)

    result = page.evaluate(JS_CODE)

    print(f"=== Theme Post-Entry Rules ===")
    for r in result.get('themeRules', []):
        if 'error' in r:
            print(f"  ERROR: {r}")
            continue
        print(f"  [{r['sheet']}] {r['selector']}")
        print(f"    color: {r['color']} {'!important' if r['priority'] == 'important' else ''}")

    print(f"\n=== Theme !important Color Rules ===")
    for r in result.get('allImportantColorInTheme', []):
        print(f"  [{r['sheet']}] Rule {r['ruleIdx']}: {r['selector']}")
        print(f"    color: {r['color']} !important")

    print(f"\n=== Elementor / Global Styles ===")
    for r in result.get('elementorRules', []):
        if 'cssText' in r:
            print(f"  [{r['sheetId']}] {r['selector']}")
            print(f"    {r['cssText'][:200]}")
        else:
            print(f"  [{r['sheetId']}] {r['selector']}")
            print(f"    color: {r['color']} {'!important' if r.get('priority') == 'important' else ''}")

    print(f"\n=== CSS Variable Rules ===")
    for r in result.get('cssVarRules', []):
        print(f"  {r['selector']}: {r['cssText'][:200]}")

    print(f"\n=== Resolved CSS Variables ===")
    for k, v in result.get('cssVars', {}).items():
        print(f"  {k}: '{v}'")

    browser.close()
