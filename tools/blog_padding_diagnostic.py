#!/usr/bin/env python3
"""Diagnostic: check computed styles on blog post at desktop width"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

AETHER_ROOT = Path("/home/jared/projects/AI-CIV/aether")
load_dotenv(AETHER_ROOT / ".env")

URL = "https://purebrain.ai/the-difference-between-using-ai-and-having-an-ai-partner/?nocache=diagnostic"
SCREENSHOT_PATH = str(AETHER_ROOT / "exports/screenshots/blog_padding_diagnostic.png")
SCREENSHOT_MOBILE = str(AETHER_ROOT / "exports/screenshots/blog_padding_mobile.png")

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    # DESKTOP: 1440px wide
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    page.screenshot(path=SCREENSHOT_PATH, full_page=False)
    print(f"Desktop screenshot: {SCREENSHOT_PATH}")
    
    # Get computed styles
    computed = page.evaluate("""() => {
        const container = document.querySelector(".page-single-post .container");
        const postSingleImage = document.querySelector(".post-single-image");
        const img = document.querySelector(".post-single-image img");
        const row = document.querySelector(".page-single-post .row");
        const col = document.querySelector(".page-single-post .col-md-12");
        
        const getStyles = (el) => {
            if (!el) return "NOT FOUND";
            const s = window.getComputedStyle(el);
            return {
                width: el.offsetWidth,
                paddingLeft: s.paddingLeft,
                paddingRight: s.paddingRight,
                marginLeft: s.marginLeft,
                marginRight: s.marginRight,
                maxWidth: s.maxWidth,
                position: el.getBoundingClientRect().left + " from left",
            };
        };
        
        return {
            container: getStyles(container),
            postSingleImage: getStyles(postSingleImage),
            img: getStyles(img),
            row: getStyles(row),
            col: getStyles(col),
            viewportWidth: window.innerWidth,
        };
    }""")
    
    print("\n=== COMPUTED STYLES AT 1440px ===")
    import json
    print(json.dumps(computed, indent=2))
    
    # Also check if the plugin CSS is actually applied
    has_plugin_css = page.evaluate("""() => {
        const styles = document.getElementById("purebrain-blog-desktop-padding");
        return styles ? styles.textContent.substring(0, 200) : "NOT FOUND";
    }""")
    print("\n=== PLUGIN CSS TAG ===")
    print(has_plugin_css[:300] if has_plugin_css else "NOT FOUND")
    
    # Check specificity winner for .post-single-image max-width
    match_info = page.evaluate("""() => {
        const el = document.querySelector(".post-single-image");
        if (!el) return "element not found";
        
        // Get all CSS rules matching this element
        const sheets = document.styleSheets;
        const results = [];
        for (const sheet of sheets) {
            try {
                const rules = sheet.cssRules || sheet.rules;
                if (!rules) continue;
                for (const rule of rules) {
                    if (rule.selectorText && rule.style && rule.style.maxWidth) {
                        try {
                            if (el.matches(rule.selectorText)) {
                                results.push({
                                    selector: rule.selectorText,
                                    maxWidth: rule.style.maxWidth,
                                    href: sheet.href || "inline",
                                });
                            }
                        } catch(e) {}
                    }
                }
            } catch(e) {}
        }
        return results;
    }""")
    print("\n=== ALL max-width RULES MATCHING .post-single-image ===")
    print(json.dumps(match_info, indent=2))
    
    # MOBILE check
    page2 = browser.new_page(viewport={"width": 375, "height": 812})
    page2.goto(URL, wait_until="domcontentloaded")
    page2.wait_for_timeout(2000)
    page2.screenshot(path=SCREENSHOT_MOBILE, full_page=False)
    print(f"\nMobile screenshot: {SCREENSHOT_MOBILE}")
    
    browser.close()
