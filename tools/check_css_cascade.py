#!/usr/bin/env python3
"""Check CSS cascade order and which rules override the CTA button color."""
import time
from playwright.sync_api import sync_playwright

JS_CODE = """() => {
    // Find CTA link
    const links = document.querySelectorAll('a');
    let cta = null;
    for (const link of links) {
        if (link.textContent.includes('Start Your AI Partnership')) {
            cta = link;
            break;
        }
    }
    if (!cta) return {error: 'CTA not found'};

    // Get ALL matching CSS rules for the CTA element
    let allMatchingRules = [];
    let sheetOrder = [];
    let sheetIdx = 0;
    for (const sheet of document.styleSheets) {
        let sheetInfo = {
            index: sheetIdx,
            href: sheet.href ? sheet.href.substring(0, 100) : 'inline',
            ownerNode: sheet.ownerNode ? sheet.ownerNode.id || sheet.ownerNode.tagName : 'unknown'
        };
        sheetOrder.push(sheetInfo);

        try {
            for (const rule of sheet.cssRules) {
                if (!rule.selectorText || !rule.style || !rule.style.color) continue;
                try {
                    if (cta.matches(rule.selectorText)) {
                        allMatchingRules.push({
                            sheetIdx: sheetIdx,
                            selector: rule.selectorText.substring(0, 120),
                            color: rule.style.color,
                            important: rule.style.getPropertyPriority('color') === 'important',
                            sheetHref: sheet.href ? sheet.href.substring(sheet.href.lastIndexOf('/')) : 'inline:' + (sheet.ownerNode ? sheet.ownerNode.id : '?')
                        });
                    }
                } catch(matchErr) {}
            }
        } catch(e) { /* cross-origin */ }
        sheetIdx++;
    }

    // Also find rules matching the body (for inheritance)
    let bodyRules = [];
    for (const sheet of document.styleSheets) {
        try {
            for (const rule of sheet.cssRules) {
                if (!rule.selectorText || !rule.style || !rule.style.color) continue;
                try {
                    if (document.body.matches(rule.selectorText)) {
                        if (rule.style.getPropertyPriority('color') === 'important') {
                            bodyRules.push({
                                selector: rule.selectorText.substring(0, 120),
                                color: rule.style.color,
                                sheetHref: sheet.href ? sheet.href.substring(sheet.href.lastIndexOf('/')) : 'inline'
                            });
                        }
                    }
                } catch(matchErr) {}
            }
        } catch(e) {}
    }

    return {
        ctaComputedColor: getComputedStyle(cta).color,
        bodyComputedColor: getComputedStyle(document.body).color,
        matchingCTARules: allMatchingRules,
        bodyImportantRules: bodyRules,
        totalSheets: sheetOrder.length,
        sheetOrder: sheetOrder.slice(0, 15)
    };
}"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    page.goto("https://purebrain.ai/ceo-vs-employee-ai-transformation-gap/",
              wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)

    result = page.evaluate(JS_CODE)

    print(f"CTA computed color: {result['ctaComputedColor']}")
    print(f"Body computed color: {result['bodyComputedColor']}")
    print(f"Total stylesheets: {result['totalSheets']}")

    print(f"\n=== Stylesheet Order ===")
    for s in result['sheetOrder']:
        print(f"  [{s['index']}] {s['ownerNode']} -> {s['href']}")

    print(f"\n=== CSS Rules Matching CTA Element ({len(result['matchingCTARules'])}) ===")
    for r in result['matchingCTARules']:
        imp = " !important" if r['important'] else ""
        print(f"  Sheet[{r['sheetIdx']}] {r['sheetHref']}")
        print(f"    {r['selector']}")
        print(f"    color: {r['color']}{imp}")

    print(f"\n=== Body !important Color Rules ({len(result['bodyImportantRules'])}) ===")
    for r in result['bodyImportantRules']:
        print(f"  {r['sheetHref']}: {r['selector']}")
        print(f"    color: {r['color']} !important")

    browser.close()
