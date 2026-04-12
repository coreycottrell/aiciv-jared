#!/usr/bin/env python3
"""Brute force: find EXACTLY what makes CTA orange."""
import time
from playwright.sync_api import sync_playwright

JS_CODE = """() => {
    const links = document.querySelectorAll('a');
    let cta = null;
    for (const link of links) {
        if (link.textContent.includes('Start Your AI Partnership')) {
            cta = link;
            break;
        }
    }
    if (!cta) return {error: 'CTA not found'};

    // Step 1: Disable ALL stylesheets and check color
    const sheets = Array.from(document.styleSheets);
    const results = {};

    // Current color
    results.before = getComputedStyle(cta).color;

    // Disable all sheets
    sheets.forEach(s => s.disabled = true);
    results.allDisabled = getComputedStyle(cta).color;

    // Re-enable all
    sheets.forEach(s => s.disabled = false);

    // Now disable one at a time and check
    results.perSheet = [];
    for (let i = 0; i < sheets.length; i++) {
        sheets[i].disabled = true;
        const color = getComputedStyle(cta).color;
        const changed = color !== results.before;
        if (changed) {
            results.perSheet.push({
                idx: i,
                href: sheets[i].href ? sheets[i].href.split('/').pop().substring(0, 60) : (sheets[i].ownerNode ? sheets[i].ownerNode.id : 'inline'),
                colorWhenDisabled: color,
                note: 'DISABLING THIS CHANGES THE COLOR'
            });
        }
        sheets[i].disabled = false;
    }

    // Step 2: Check if the custom CSS sheet is actually applying
    const customSheet = document.querySelector('style#wp-custom-css');
    if (customSheet && customSheet.sheet) {
        results.customSheetRulesCount = customSheet.sheet.cssRules.length;

        // Find the body.single-post a rule
        for (let i = 0; i < customSheet.sheet.cssRules.length; i++) {
            const rule = customSheet.sheet.cssRules[i];
            if (rule.selectorText && rule.selectorText === 'body.single-post a') {
                results.foundRule = {
                    idx: i,
                    selector: rule.selectorText,
                    color: rule.style.color,
                    priority: rule.style.getPropertyPriority('color'),
                    cssText: rule.cssText.substring(0, 200)
                };
                break;
            }
        }
    }

    // Step 3: Direct DOM manipulation test
    // Remove all style-related attributes from CTA
    const origStyle = cta.getAttribute('style');
    cta.removeAttribute('style');
    results.noInlineStyle = getComputedStyle(cta).color;
    cta.setAttribute('style', origStyle);

    // Step 4: Check if body has `color: ... !important` from some inline style
    results.bodyInlineStyle = document.body.getAttribute('style') || 'none';
    results.bodyComputedColor = getComputedStyle(document.body).color;

    return results;
}"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    page.goto("https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/",
              wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)

    result = page.evaluate(JS_CODE)

    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"CTA color before: {result['before']}")
        print(f"CTA color with ALL sheets disabled: {result['allDisabled']}")
        print(f"CTA color without inline style: {result['noInlineStyle']}")
        print(f"Body inline style: {result['bodyInlineStyle']}")
        print(f"Body computed color: {result['bodyComputedColor']}")

        print(f"\n=== Sheets that change CTA color when disabled ===")
        for s in result.get('perSheet', []):
            print(f"  Sheet[{s['idx']}] {s['href']}: disabling -> {s['colorWhenDisabled']}")

        print(f"\n=== Custom CSS Sheet ===")
        print(f"  Rules count: {result.get('customSheetRulesCount', 'N/A')}")
        if 'foundRule' in result:
            r = result['foundRule']
            print(f"  Found rule at index {r['idx']}: {r['selector']}")
            print(f"  color: {r['color']} priority: {r['priority']}")
            print(f"  cssText: {r['cssText']}")
        else:
            print(f"  body.single-post a rule NOT FOUND!")

    browser.close()
