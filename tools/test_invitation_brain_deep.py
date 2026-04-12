#!/usr/bin/env python3
"""
Deep audit of the 3D brain animation specifically.
"""

import asyncio
import json
from playwright.async_api import async_playwright

URL = "https://purebrain.ai/invitation/"
PASSWORD = "purebrain25"
SCREENSHOTS_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/invitation-audit-2026-02-27"

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--enable-webgl", "--use-gl=swiftshader"]
        )
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        console_msgs = []
        page.on("console", lambda m: console_msgs.append({"t": m.type, "msg": m.text}))
        page.on("pageerror", lambda e: console_msgs.append({"t": "pageerror", "msg": str(e)}))

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

        # Wait longer for Three.js to initialize
        await page.wait_for_timeout(5000)

        # Check canvas count NOW (after waiting)
        canvas_check = await page.evaluate("""
        () => {
            const canvases = document.querySelectorAll('canvas');
            return {
                count: canvases.length,
                canvases: Array.from(canvases).map(c => ({
                    id: c.id,
                    className: c.className,
                    width: c.width,
                    height: c.height,
                    style: c.getAttribute('style'),
                    parentId: c.parentElement ? c.parentElement.id : '',
                    parentClass: c.parentElement ? (typeof c.parentElement.className === 'string' ? c.parentElement.className : '') : ''
                }))
            };
        }
        """)
        print("Canvas check after 10s wait:")
        print(json.dumps(canvas_check, indent=2))

        # Check THREE global
        three_check = await page.evaluate("""
        () => {
            return {
                THREE_exists: typeof THREE !== 'undefined',
                THREE_version: typeof THREE !== 'undefined' ? THREE.REVISION : null,
                WebGLRenderer_exists: typeof THREE !== 'undefined' && typeof THREE.WebGLRenderer !== 'undefined'
            };
        }
        """)
        print("\nThree.js global check:")
        print(json.dumps(three_check, indent=2))

        # Find the neural script content
        script_content = await page.evaluate("""
        () => {
            const scripts = Array.from(document.scripts);
            for (const s of scripts) {
                if (!s.src && s.textContent &&
                    (s.textContent.includes('NeuralBrain') ||
                     s.textContent.includes('WebGLRenderer') ||
                     s.textContent.includes('neural-bg') ||
                     s.textContent.includes('THREE'))) {
                    return {
                        found: true,
                        snippet: s.textContent.substring(0, 1000)
                    };
                }
            }
            // Check external scripts
            const extScripts = scripts.filter(s => s.src && s.src.includes('three'));
            return {
                found: false,
                externalThreeScripts: extScripts.map(s => s.src)
            };
        }
        """)
        print("\nNeural script content:")
        print(json.dumps(script_content, indent=2))

        # Check if there's a #neural-bg div that should hold the canvas
        container_check = await page.evaluate("""
        () => {
            // Wide search for any potential container
            const candidates = [
                '#neural-bg', '#neural-network-bg', '#brain-canvas',
                '.neural-bg', '.brain-bg', '[id*="neural"]', '[id*="brain"]',
                '[class*="neural"]', '[class*="brain"]'
            ];
            const results = {};
            for (const sel of candidates) {
                const els = document.querySelectorAll(sel);
                if (els.length > 0) {
                    results[sel] = Array.from(els).map(el => ({
                        tag: el.tagName,
                        id: el.id,
                        className: typeof el.className === 'string' ? el.className : '',
                        hasCanvas: el.querySelector('canvas') !== null,
                        innerHTML_preview: el.innerHTML.substring(0, 200),
                        computedDisplay: window.getComputedStyle(el).display,
                        computedVisibility: window.getComputedStyle(el).visibility,
                        offsetWidth: el.offsetWidth,
                        offsetHeight: el.offsetHeight
                    }));
                }
            }
            return results;
        }
        """)
        print("\nContainer element check:")
        print(json.dumps(container_check, indent=2))

        # Check if hero section has a background canvas or CSS background
        hero_check = await page.evaluate("""
        () => {
            const hero = document.querySelector('.pb-hero, [class*="pb-hero"]');
            if (!hero) return { found: false };
            const computed = window.getComputedStyle(hero);
            return {
                found: true,
                className: typeof hero.className === 'string' ? hero.className : '',
                backgroundImage: computed.backgroundImage.substring(0, 200),
                backgroundAttachment: computed.backgroundAttachment,
                position: computed.position,
                hasCanvas: hero.querySelector('canvas') !== null,
                innerHTML_first500: hero.innerHTML.substring(0, 500)
            };
        }
        """)
        print("\nHero section check:")
        print(json.dumps(hero_check, indent=2))

        # Check all external scripts that loaded
        scripts_loaded = await page.evaluate("""
        () => {
            return Array.from(document.scripts)
                .filter(s => s.src)
                .map(s => s.src)
                .filter(s => s.includes('three') || s.includes('neural') || s.includes('brain') || s.includes('webgl') || s.includes('purebrain'));
        }
        """)
        print("\nRelevant external scripts loaded:")
        print(json.dumps(scripts_loaded, indent=2))

        # WAIT MORE and check again - maybe Three.js initializes slowly
        print("\nWaiting 5 more seconds for Three.js to potentially initialize...")
        await page.wait_for_timeout(5000)

        canvas_after_wait = await page.evaluate("() => document.querySelectorAll('canvas').length")
        print(f"Canvas count after total 20s wait: {canvas_after_wait}")

        # Check if there's a DOMContentLoaded race condition by manually triggering init
        manual_trigger = await page.evaluate("""
        () => {
            // Try to find and call any NeuralBrain init function
            if (typeof NeuralBrain !== 'undefined') {
                return { NeuralBrainExists: true };
            }
            if (typeof initNeuralBrain !== 'undefined') {
                return { initNeuralBrainExists: true };
            }
            // Check window properties
            const neuralKeys = Object.keys(window).filter(k =>
                k.toLowerCase().includes('neural') ||
                k.toLowerCase().includes('brain') ||
                k.toLowerCase().includes('three')
            );
            return { NeuralBrainExists: false, windowNeuralKeys: neuralKeys };
        }
        """)
        print("\nManual trigger check:")
        print(json.dumps(manual_trigger, indent=2))

        # Screenshot after full wait
        await page.screenshot(path=f"{SCREENSHOTS_DIR}/brain-deep-check.png")
        print(f"\nScreenshot saved: {SCREENSHOTS_DIR}/brain-deep-check.png")

        # Console messages
        errors = [m for m in console_msgs if m['t'] in ('error', 'pageerror')]
        warnings = [m for m in console_msgs if m['t'] == 'warning']
        print(f"\nConsole: {len(errors)} errors, {len(warnings)} warnings")
        for e in errors[:15]:
            print(f"  ERROR: {e['msg'][:200]}")
        for w in warnings[:5]:
            print(f"  WARN: {w['msg'][:150]}")

        # Also check all console for THREE-related
        three_console = [m for m in console_msgs if 'THREE' in m['msg'] or 'three' in m['msg'].lower() or 'webgl' in m['msg'].lower()]
        print(f"\nThree.js related console messages: {len(three_console)}")
        for m in three_console:
            print(f"  {m['t']}: {m['msg'][:200]}")

        await browser.close()
        return console_msgs

if __name__ == "__main__":
    asyncio.run(run())
