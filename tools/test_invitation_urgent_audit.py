#!/usr/bin/env python3
"""
Urgent audit of purebrain.ai/invitation/ - checking 3D brain, background, console errors.
"""
import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOT_DIR = Path("/home/jared/projects/AI-CIV/aether/exports/screenshots/invitation-audit-2026-02-27-v2")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

async def run_audit():
    results = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        # Collect ALL console messages and page errors
        console_logs = []
        page_errors = []

        page = await context.new_page()

        page.on("console", lambda msg: console_logs.append({
            "type": msg.type,
            "text": msg.text
        }))
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        print("Navigating to purebrain.ai/invitation/ ...")
        await page.goto("https://purebrain.ai/invitation/", wait_until="networkidle", timeout=30000)

        # Screenshot 1: Immediately after load
        path1 = str(SCREENSHOT_DIR / "001-immediate-load.png")
        await page.screenshot(path=path1, full_page=True)
        print(f"Screenshot 1 saved: {path1}")

        # Check 1: body background color
        bg_color = await page.evaluate("window.getComputedStyle(document.body).backgroundColor")
        results["body_bg_color"] = bg_color
        print(f"body backgroundColor: {bg_color}")

        # Check 2: page ID
        page_id = await page.evaluate("""
            () => {
                const classes = document.body.className;
                const match = classes.match(/page-id-(\\d+)/);
                return match ? match[1] : 'not found';
            }
        """)
        results["page_id"] = page_id
        print(f"Page ID: {page_id}")

        # Check 3: canvas inside #pb-canvas-container
        canvas_check = await page.evaluate("""
            () => {
                const container = document.querySelector('#pb-canvas-container');
                if (!container) return {container: false, canvas: false};
                const canvas = container.querySelector('canvas');
                return {
                    container: true,
                    containerStyle: container.style.cssText,
                    canvas: !!canvas,
                    canvasWidth: canvas ? canvas.width : 0,
                    canvasHeight: canvas ? canvas.height : 0
                };
            }
        """)
        results["canvas_check"] = canvas_check
        print(f"Canvas check: {json.dumps(canvas_check, indent=2)}")

        # Check 4: importmap present?
        importmap_check = await page.evaluate("""
            () => {
                const scripts = document.querySelectorAll('script[type="importmap"]');
                if (scripts.length === 0) return {present: false};
                return {present: true, count: scripts.length, content: scripts[0].textContent.substring(0, 200)};
            }
        """)
        results["importmap"] = importmap_check
        print(f"Importmap: {json.dumps(importmap_check, indent=2)}")

        # Check 5: && encoding check
        amp_check = await page.evaluate("""
            () => {
                const scripts = document.querySelectorAll('script:not([src]):not([type="importmap"])');
                let ampCount = 0;
                let scriptInfo = [];
                scripts.forEach((s, i) => {
                    const text = s.textContent || '';
                    const count = (text.match(/&#038;/g) || []).length;
                    if (count > 0) {
                        ampCount += count;
                        scriptInfo.push({index: i, ampCount: count, preview: text.substring(0, 100)});
                    }
                });
                return {totalAmpEntities: ampCount, affectedScripts: scriptInfo};
            }
        """)
        results["amp_encoding"] = amp_check
        print(f"&#038; entities in inline scripts: {amp_check['totalAmpEntities']}")

        # Check 6: pricing tiers
        pricing_check = await page.evaluate("""
            () => {
                const prices = [];
                document.querySelectorAll('.pb-price-amount, .price-amount, [class*="price"]').forEach(el => {
                    const text = el.textContent.trim();
                    if (text.includes('$')) prices.push(text);
                });
                // Also check for dollar amounts in the page
                const allText = document.body.innerText;
                const dollarAmounts = allText.match(/\\$\\d+/g) || [];
                return {priceElements: prices, dollarAmounts: [...new Set(dollarAmounts)]};
            }
        """)
        results["pricing"] = pricing_check
        print(f"Pricing: {json.dumps(pricing_check, indent=2)}")

        # Check 7: claimed spots count
        spots_check = await page.evaluate("""
            () => {
                const allText = document.body.innerText;
                const spotsMatch = allText.match(/(\\d+)\\s*(of\\s*\\d+\\s*)?spot/i);
                // Look for specific "2 claimed" or similar
                const claimed = allText.match(/(\\d+)\\s*claimed/i);
                // Look for countdown
                const countdown = document.querySelector('[class*="countdown"], [id*="countdown"], .pb-countdown');
                return {
                    spotsPattern: spotsMatch ? spotsMatch[0] : null,
                    claimedPattern: claimed ? claimed[0] : null,
                    countdownEl: countdown ? countdown.textContent.substring(0, 100) : null
                };
            }
        """)
        results["spots"] = spots_check
        print(f"Spots check: {json.dumps(spots_check, indent=2)}")

        # Wait 3 seconds for 3D to initialize
        print("Waiting 3 seconds for 3D initialization...")
        await asyncio.sleep(3)

        # Re-check canvas after wait
        canvas_after = await page.evaluate("""
            () => {
                const container = document.querySelector('#pb-canvas-container');
                if (!container) return {container: false, canvas: false};
                const canvas = container.querySelector('canvas');
                return {
                    container: true,
                    canvas: !!canvas,
                    canvasWidth: canvas ? canvas.width : 0,
                    canvasHeight: canvas ? canvas.height : 0
                };
            }
        """)
        results["canvas_after_3s"] = canvas_after
        print(f"Canvas after 3s: {json.dumps(canvas_after, indent=2)}")

        # Screenshot 2: After 3 second wait
        path2 = str(SCREENSHOT_DIR / "002-after-3s-wait.png")
        await page.screenshot(path=path2, full_page=True)
        print(f"Screenshot 2 saved: {path2}")

        # Screenshot 3: Hero section specifically
        path3 = str(SCREENSHOT_DIR / "003-hero-viewport.png")
        await page.screenshot(path=path3, full_page=False)  # viewport only
        print(f"Screenshot 3 (viewport/hero) saved: {path3}")

        # Check sections visible
        sections_check = await page.evaluate("""
            () => {
                const sections = {
                    hero: document.querySelector('.pb-hero, [class*="hero"], #hero'),
                    pricing: document.querySelector('.pb-pricing, [class*="pricing"], #pricing'),
                    process: document.querySelector('.pb-process, [class*="process"], #process'),
                    testimonial: document.querySelector('.pb-testimonial, [class*="testimonial"], [class*="review"]')
                };
                const result = {};
                for (const [name, el] of Object.entries(sections)) {
                    result[name] = el ? {found: true, text: el.textContent.substring(0, 80).trim()} : {found: false};
                }
                // Also check innerText for section keywords
                const allText = document.body.innerText.toLowerCase();
                result.hasHeroText = allText.includes('invitation') || allText.includes('exclusive');
                result.hasPricingText = allText.includes('awakened') || allText.includes('$79');
                result.hasProcessText = allText.includes('process') || allText.includes('step');
                result.hasTestimonialText = allText.includes('testimonial') || allText.includes('michael') || allText.includes('hancock');
                return result;
            }
        """)
        results["sections"] = sections_check
        print(f"Sections: {json.dumps(sections_check, indent=2)}")

        # Consolidate console logs
        errors = [l for l in console_logs if l["type"] == "error"]
        warnings = [l for l in console_logs if l["type"] == "warning"]
        info_logs = [l for l in console_logs if l["type"] in ("log", "info")]

        results["console"] = {
            "all_errors": errors[:20],
            "all_warnings": warnings[:10],
            "page_errors": page_errors[:10],
            "purebrain_logs": [l for l in info_logs if "purebrain" in l["text"].lower() or "3d" in l["text"].lower() or "neural" in l["text"].lower()],
            "total_errors": len(errors),
            "total_warnings": len(warnings),
            "total_page_errors": len(page_errors)
        }

        print(f"\n=== CONSOLE SUMMARY ===")
        print(f"Page errors: {len(page_errors)}")
        for err in page_errors:
            print(f"  PAGE ERROR: {err}")
        print(f"Console errors: {len(errors)}")
        for e in errors[:10]:
            print(f"  ERROR: {e['text']}")
        print(f"PureBrain logs: {results['console']['purebrain_logs']}")

        await browser.close()

    return results, path1, path2, path3

if __name__ == "__main__":
    results, path1, path2, path3 = asyncio.run(run_audit())

    # Save results
    out_path = "/home/jared/projects/AI-CIV/aether/exports/invitation-urgent-audit-2026-02-27.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n=== AUDIT COMPLETE ===")
    print(f"Results saved: {out_path}")
    print(f"Screenshots: {path1}, {path2}, {path3}")
