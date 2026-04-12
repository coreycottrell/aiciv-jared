#!/usr/bin/env python3
"""Check the LIVE wp-custom-css content on the blog post page."""
import time
from playwright.sync_api import sync_playwright

JS_CODE = """() => {
    const style = document.querySelector('style#wp-custom-css');
    if (!style) return {error: 'wp-custom-css not found'};

    const css = style.textContent;

    // Find ALL rules containing 'single-post a' (not :hover, just base)
    const lines = css.split('\\n');
    let singlePostALines = [];
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line.includes('body.single-post a') && !line.includes(':hover') && !line.includes('a[') && !line.includes('a.') && !line.includes('a i') && !line.includes('a svg')) {
            // Get context: this line + next 3 lines
            singlePostALines.push({
                lineNum: i,
                text: lines.slice(i, Math.min(i+4, lines.length)).join(' | ')
            });
        }
    }

    // Check var(--e-global-color-accent) value
    const accent = getComputedStyle(document.documentElement).getPropertyValue('--e-global-color-accent').trim();

    // Check if body.single-post class is present
    const bodyClasses = document.body.className;

    // Check the ACTUAL applied rule for body.single-post a
    // by testing a fresh a element
    const testA = document.createElement('a');
    testA.href = '#';
    testA.textContent = 'TEST';
    document.querySelector('.post-entry, .entry-content, article').appendChild(testA);
    const testColor = getComputedStyle(testA).color;
    testA.remove();

    return {
        cssLength: css.length,
        cssFirst200: css.substring(0, 200),
        singlePostALines: singlePostALines,
        accent: accent,
        bodyClasses: bodyClasses.substring(0, 120),
        testFreshLinkColor: testColor,
        totalLines: lines.length
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
        print(f"Custom CSS length: {result['cssLength']} chars ({result['totalLines']} lines)")
        print(f"First 200 chars: {result['cssFirst200']}")
        print(f"--e-global-color-accent: {result['accent']}")
        print(f"Body classes: {result['bodyClasses']}")
        print(f"Fresh link test color: {result['testFreshLinkColor']}")

        print(f"\n=== 'body.single-post a' rules ({len(result['singlePostALines'])}) ===")
        for line in result['singlePostALines']:
            print(f"  Line {line['lineNum']}: {line['text']}")

    browser.close()
