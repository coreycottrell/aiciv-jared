#!/usr/bin/env python3
"""Find ALL CSS rules that set color on <a> elements with !important."""
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

    // Try ALL rules across ALL stylesheets
    let matchingRules = [];
    let sheetIdx = 0;
    for (const sheet of document.styleSheets) {
        try {
            for (let i = 0; i < sheet.cssRules.length; i++) {
                const rule = sheet.cssRules[i];
                if (!rule.selectorText) continue;

                // Check if rule has color property
                if (!rule.style || !rule.style.color) continue;

                // Check if it matches our CTA element
                try {
                    if (cta.matches(rule.selectorText)) {
                        matchingRules.push({
                            sheetIdx: sheetIdx,
                            ruleIdx: i,
                            selector: rule.selectorText.substring(0, 200),
                            color: rule.style.color,
                            priority: rule.style.getPropertyPriority('color'),
                            fullText: rule.cssText.substring(0, 300)
                        });
                    }
                } catch(e) {}
            }
        } catch(e) {
            matchingRules.push({sheetIdx: sheetIdx, error: 'cross-origin'});
        }
        sheetIdx++;
    }

    // Also check for @layer rules
    let layerInfo = [];
    for (const sheet of document.styleSheets) {
        try {
            for (const rule of sheet.cssRules) {
                if (rule.type === CSSRule.LAYER_BLOCK_RULE || rule.type === CSSRule.LAYER_STATEMENT_RULE) {
                    layerInfo.push({type: rule.type, name: rule.name || 'unnamed'});
                }
            }
        } catch(e) {}
    }

    // Check for !important on all color properties
    let importantColorRules = [];
    sheetIdx = 0;
    for (const sheet of document.styleSheets) {
        try {
            for (const rule of sheet.cssRules) {
                if (!rule.selectorText || !rule.style) continue;
                if (rule.style.getPropertyPriority('color') === 'important') {
                    try {
                        if (cta.matches(rule.selectorText)) {
                            importantColorRules.push({
                                sheetIdx: sheetIdx,
                                selector: rule.selectorText.substring(0, 200),
                                color: rule.style.color,
                                sheetHref: sheet.href ? sheet.href.split('/').pop() : (sheet.ownerNode ? sheet.ownerNode.id : 'inline')
                            });
                        }
                    } catch(e) {}
                }
            }
        } catch(e) {}
        sheetIdx++;
    }

    return {
        allMatchingRules: matchingRules,
        importantColorRules: importantColorRules,
        layerInfo: layerInfo,
        ctaClasses: cta.className,
        ctaTagName: cta.tagName,
        ctaParentClasses: cta.parentElement ? cta.parentElement.className : '',
        ctaGrandparentClasses: cta.parentElement && cta.parentElement.parentElement ?
            cta.parentElement.parentElement.className : ''
    };
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
        print(f"CTA tag: {result['ctaTagName']}")
        print(f"CTA classes: '{result['ctaClasses']}'")
        print(f"Parent classes: '{result['ctaParentClasses']}'")
        print(f"Grandparent classes: '{result['ctaGrandparentClasses']}'")

        print(f"\n=== ALL Matching Rules ({len(result['allMatchingRules'])}) ===")
        for r in result['allMatchingRules']:
            if 'error' in r:
                print(f"  Sheet[{r['sheetIdx']}]: {r['error']}")
                continue
            imp = " [IMPORTANT]" if r.get('priority') == 'important' else ""
            print(f"  Sheet[{r['sheetIdx']}] Rule[{r['ruleIdx']}]{imp}")
            print(f"    Selector: {r['selector']}")
            print(f"    Color: {r['color']}")

        print(f"\n=== Important Color Rules ({len(result['importantColorRules'])}) ===")
        for r in result['importantColorRules']:
            print(f"  Sheet[{r['sheetIdx']}] ({r['sheetHref']})")
            print(f"    {r['selector']}")
            print(f"    color: {r['color']} !important")

        print(f"\n=== Layer Info ===")
        print(f"  {result['layerInfo']}")

    browser.close()
