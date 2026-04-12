"""
Three.js Neural Network Brain Background Diagnosis
Target: https://purebrain.ai/invitation/
Purpose: Diagnose why the 3D WebGL brain animation is NOT rendering

Checks:
1. Screenshot of page as it loads
2. Browser console errors (module imports, Three.js errors)
3. Whether #pb-canvas-container has a <canvas> inside it
4. CSS overrides on #pb-canvas-container (position:fixed check)
5. Ancestor transform/filter CSS that breaks position:fixed
6. WebGL availability
"""

import asyncio
import os
import sys
from datetime import datetime
from playwright.async_api import async_playwright

SCREENSHOT_DIR = "/home/jared/projects/AI-CIV/aether/exports/screenshots/threejs-diagnosis"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

WP_PASSWORD = "purebrain25"
TARGET_URL = "https://purebrain.ai/invitation/"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

async def main():
    print("=" * 70)
    print("Three.js Neural Network Brain Background Diagnosis")
    print(f"Target: {TARGET_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--enable-webgl",
                "--use-gl=swiftshader",
                "--enable-accelerated-2d-canvas",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--ignore-gpu-blacklist",
            ]
        )

        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Collect console messages
        console_messages = []
        page = await context.new_page()
        page.on("console", lambda msg: console_messages.append({
            "type": msg.type,
            "text": msg.text,
            "location": f"{msg.location.get('url', '')}:{msg.location.get('lineNumber', '')}"
        }))

        # Collect page errors
        page_errors = []
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        # Collect failed requests
        failed_requests = []
        page.on("requestfailed", lambda req: failed_requests.append({
            "url": req.url,
            "failure": req.failure
        }))

        print("\n[Step 1] Navigating to page...")
        await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30000)

        # Check if WP password protection is active
        page_content = await page.content()
        if 'type="password"' in page_content and 'Protected' in page_content:
            print("  WP password protection detected — entering password...")
            await page.fill("input[type='password']", WP_PASSWORD)
            await page.click("input[type='submit']")
            await page.wait_for_load_state("domcontentloaded")
            print("  Password submitted")

        print("  Waiting 5s for scripts to load and execute...")
        await asyncio.sleep(5)

        # SCREENSHOT 1: Initial state
        shot1_path = f"{SCREENSHOT_DIR}/{timestamp}_01_initial_load.png"
        await page.screenshot(path=shot1_path, full_page=False)
        print(f"  Screenshot 1 saved: {shot1_path}")

        print("\n[Step 2] Checking console for JS errors...")
        errors = [m for m in console_messages if m["type"] == "error"]
        warnings = [m for m in console_messages if m["type"] == "warning"]

        print(f"  Total console messages: {len(console_messages)}")
        print(f"  Errors: {len(errors)}")
        print(f"  Warnings: {len(warnings)}")
        print(f"  Page errors: {len(page_errors)}")

        print("\n  -- ALL ERRORS --")
        for e in errors:
            print(f"    [ERROR] {e['text'][:200]}")
            if e['location']:
                print(f"           @ {e['location'][:100]}")

        print("\n  -- PAGE-LEVEL ERRORS (uncaught exceptions) --")
        for e in page_errors:
            print(f"    [PAGEERROR] {str(e)[:300]}")

        print("\n  -- ALL CONSOLE MESSAGES (chronological) --")
        for m in console_messages:
            print(f"    [{m['type'].upper()}] {m['text'][:200]}")

        print("\n[Step 3] Checking #pb-canvas-container for <canvas>...")
        canvas_check = await page.evaluate("""
        () => {
            const container = document.getElementById('pb-canvas-container');
            if (!container) return { error: 'NO #pb-canvas-container element found in DOM' };

            const canvases = container.querySelectorAll('canvas');
            const containerRect = container.getBoundingClientRect();
            const computedStyle = window.getComputedStyle(container);

            return {
                containerExists: true,
                containerHTML: container.outerHTML.substring(0, 500),
                containerChildCount: container.childElementCount,
                canvasCount: canvases.length,
                canvasDetails: Array.from(canvases).map(c => ({
                    width: c.width,
                    height: c.height,
                    clientWidth: c.clientWidth,
                    clientHeight: c.clientHeight,
                    style: c.getAttribute('style') || '',
                    visible: c.offsetParent !== null || window.getComputedStyle(c).position === 'fixed'
                })),
                containerRect: {
                    top: containerRect.top,
                    left: containerRect.left,
                    width: containerRect.width,
                    height: containerRect.height
                },
                containerStyles: {
                    position: computedStyle.position,
                    top: computedStyle.top,
                    left: computedStyle.left,
                    width: computedStyle.width,
                    height: computedStyle.height,
                    zIndex: computedStyle.zIndex,
                    display: computedStyle.display,
                    visibility: computedStyle.visibility,
                    opacity: computedStyle.opacity,
                    overflow: computedStyle.overflow,
                    pointerEvents: computedStyle.pointerEvents
                }
            };
        }
        """)

        print(f"  Container exists: {canvas_check.get('containerExists', False)}")
        if canvas_check.get('error'):
            print(f"  ERROR: {canvas_check['error']}")
        else:
            print(f"  Container HTML (first 500 chars): {canvas_check.get('containerHTML', 'N/A')}")
            print(f"  Canvas elements inside container: {canvas_check.get('canvasCount', 0)}")
            print(f"  Canvas details: {canvas_check.get('canvasDetails', [])}")
            print(f"  Container bounding rect: {canvas_check.get('containerRect', {})}")
            print(f"  Container computed styles:")
            for k, v in canvas_check.get('containerStyles', {}).items():
                print(f"    {k}: {v}")

        print("\n[Step 4] Checking CSS on #pb-canvas-container (position:fixed override?)...")
        css_check = await page.evaluate("""
        () => {
            const container = document.getElementById('pb-canvas-container');
            if (!container) return { error: 'container not found' };

            // Check all stylesheets for rules targeting this element
            const rules = [];
            try {
                for (const sheet of document.styleSheets) {
                    try {
                        for (const rule of sheet.cssRules || []) {
                            if (rule.selectorText && (
                                rule.selectorText.includes('pb-canvas') ||
                                rule.selectorText.includes('#pb-canvas')
                            )) {
                                rules.push({
                                    selector: rule.selectorText,
                                    cssText: rule.cssText.substring(0, 300),
                                    href: sheet.href
                                });
                            }
                        }
                    } catch(e) { /* cross-origin sheet, skip */ }
                }
            } catch(e) {}

            return {
                matchingCSSRules: rules,
                computedPosition: window.getComputedStyle(container).position,
                inlineStyle: container.getAttribute('style') || 'none'
            };
        }
        """)
        print(f"  Computed position: {css_check.get('computedPosition', 'unknown')}")
        print(f"  Inline style: {css_check.get('inlineStyle', 'none')}")
        print(f"  Matching CSS rules from stylesheets: {len(css_check.get('matchingCSSRules', []))}")
        for r in css_check.get('matchingCSSRules', []):
            print(f"    [{r.get('href', 'inline')[:60]}]")
            print(f"    Selector: {r.get('selector')}")
            print(f"    CSS: {r.get('cssText')}")

        print("\n[Step 5] Checking ancestors for transform/filter (breaks position:fixed)...")
        ancestor_check = await page.evaluate("""
        () => {
            const container = document.getElementById('pb-canvas-container');
            if (!container) return { error: 'container not found' };

            const ancestors = [];
            let el = container.parentElement;
            while (el && el !== document.body) {
                const cs = window.getComputedStyle(el);
                const transform = cs.transform;
                const filter = cs.filter;
                const willChange = cs.willChange;
                const perspective = cs.perspective;

                const hasProblem = (
                    (transform && transform !== 'none' && transform !== '') ||
                    (filter && filter !== 'none' && filter !== '') ||
                    (willChange && willChange !== 'auto' && willChange !== '') ||
                    (perspective && perspective !== 'none' && perspective !== '')
                );

                if (hasProblem || el.tagName === 'BODY' || ancestors.length < 5) {
                    ancestors.push({
                        tag: el.tagName,
                        id: el.id || null,
                        className: (typeof el.className === 'string' ? el.className : '').substring(0, 60),
                        transform: transform !== 'none' ? transform : null,
                        filter: filter !== 'none' ? filter : null,
                        willChange: willChange !== 'auto' ? willChange : null,
                        perspective: perspective !== 'none' ? perspective : null,
                        hasProblem: hasProblem
                    });
                }
                el = el.parentElement;
            }

            // Also check body
            const bodyCS = window.getComputedStyle(document.body);
            ancestors.push({
                tag: 'BODY',
                transform: bodyCS.transform !== 'none' ? bodyCS.transform : null,
                filter: bodyCS.filter !== 'none' ? bodyCS.filter : null,
                willChange: bodyCS.willChange !== 'auto' ? bodyCS.willChange : null,
                hasProblem: bodyCS.transform !== 'none' || bodyCS.filter !== 'none'
            });

            return { ancestors };
        }
        """)

        problem_ancestors = [a for a in ancestor_check.get('ancestors', []) if a.get('hasProblem')]
        print(f"  Ancestors with transform/filter/will-change: {len(problem_ancestors)}")
        for a in ancestor_check.get('ancestors', []):
            prefix = "  [PROBLEM!]" if a.get('hasProblem') else "  [OK]"
            print(f"{prefix} <{a.get('tag')}> id={a.get('id')} class={a.get('className', '')}")
            if a.get('transform'):
                print(f"           transform: {a.get('transform', '')[:100]}")
            if a.get('filter'):
                print(f"           filter: {a.get('filter', '')[:100]}")
            if a.get('willChange'):
                print(f"           will-change: {a.get('willChange', '')[:100]}")

        print("\n[Step 6] WebGL availability check...")
        webgl_check = await page.evaluate("""
        () => {
            try {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl2') || canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                if (!gl) return { available: false, reason: 'getContext returned null' };
                return {
                    available: true,
                    version: gl instanceof WebGL2RenderingContext ? 'WebGL2' : 'WebGL1',
                    renderer: gl.getParameter(gl.RENDERER),
                    vendor: gl.getParameter(gl.VENDOR),
                    maxTextureSize: gl.getParameter(gl.MAX_TEXTURE_SIZE)
                };
            } catch(e) {
                return { available: false, reason: e.message };
            }
        }
        """)
        print(f"  WebGL available: {webgl_check.get('available', False)}")
        print(f"  Version: {webgl_check.get('version', 'N/A')}")
        print(f"  Renderer: {webgl_check.get('renderer', 'N/A')}")
        print(f"  Vendor: {webgl_check.get('vendor', 'N/A')}")
        if not webgl_check.get('available'):
            print(f"  Reason for failure: {webgl_check.get('reason', 'unknown')}")

        print("\n[Step 6b] Checking if Three.js module loaded successfully...")
        threejs_check = await page.evaluate("""
        () => {
            // Look for evidence Three.js ran:
            // - Did the script's init function run?
            // - Is there any THREE global?
            // - Is the canvas-container populated?
            // - Check for any errors in DOM

            const container = document.getElementById('pb-canvas-container');
            const scripts = Array.from(document.querySelectorAll('script[type="module"]'));
            const allScripts = Array.from(document.querySelectorAll('script'));

            return {
                moduleScriptCount: scripts.length,
                moduleScriptSrcs: scripts.map(s => (s.src || 'inline:' + (s.textContent || '').substring(0, 100))),
                totalScriptCount: allScripts.length,
                containerInnerHTML: container ? container.innerHTML.substring(0, 300) : 'CONTAINER NOT FOUND',
                windowTHREE: typeof window.THREE !== 'undefined' ? 'THREE global exists' : 'No THREE global (expected for modules)',
                documentReadyState: document.readyState
            };
        }
        """)
        print(f"  Document ready state: {threejs_check.get('documentReadyState')}")
        print(f"  Module scripts found: {threejs_check.get('moduleScriptCount', 0)}")
        print(f"  Module script sources:")
        for src in threejs_check.get('moduleScriptSrcs', []):
            print(f"    {src[:150]}")
        print(f"  THREE global: {threejs_check.get('windowTHREE')}")
        print(f"  Container innerHTML: {threejs_check.get('containerInnerHTML', 'N/A')}")

        print("\n[Step 6c] Checking failed network requests (CDN imports)...")
        print(f"  Failed requests: {len(failed_requests)}")
        for req in failed_requests:
            print(f"    FAILED: {req['url'][:150]}")
            print(f"    Reason: {req['failure']}")

        # Check specifically if CDN URLs are reachable
        print("\n[Step 6d] Testing CDN URL accessibility directly...")
        cdn_check = await page.evaluate("""
        async () => {
            const urls = [
                'https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.module.js',
                'https://cdn.jsdelivr.net/npm/three@0.161.0/examples/jsm/postprocessing/EffectComposer.js'
            ];
            const results = [];
            for (const url of urls) {
                try {
                    const resp = await fetch(url, { method: 'HEAD', signal: AbortSignal.timeout(8000) });
                    results.push({ url, status: resp.status, ok: resp.ok });
                } catch(e) {
                    results.push({ url, error: e.message });
                }
            }
            return results;
        }
        """)
        for r in cdn_check:
            if r.get('ok'):
                print(f"    OK ({r.get('status')}): {r.get('url', '')[:80]}")
            else:
                print(f"    FAIL: {r.get('url', '')[:80]}")
                print(f"          Status: {r.get('status', 'N/A')} Error: {r.get('error', 'none')}")

        # Wait longer and check if canvas appears after more time
        print("\n[Step 7] Waiting 8 more seconds for async module loading...")
        await asyncio.sleep(8)

        canvas_after = await page.evaluate("""
        () => {
            const container = document.getElementById('pb-canvas-container');
            if (!container) return { error: 'no container' };
            return {
                canvasCount: container.querySelectorAll('canvas').length,
                innerHTML: container.innerHTML.substring(0, 200)
            };
        }
        """)
        print(f"  Canvas count after waiting: {canvas_after.get('canvasCount', 0)}")
        print(f"  Container innerHTML after waiting: {canvas_after.get('innerHTML', 'N/A')}")

        # Get any new console messages
        new_errors_after = [m for m in console_messages if m["type"] == "error"]
        print(f"  Total errors after full wait: {len(new_errors_after)}")

        # Final screenshot
        shot2_path = f"{SCREENSHOT_DIR}/{timestamp}_02_after_wait.png"
        await page.screenshot(path=shot2_path, full_page=False)
        print(f"  Screenshot 2 saved: {shot2_path}")

        # Also get the full page HTML around the canvas area for inspection
        print("\n[Step 8] Extracting canvas area HTML context...")
        html_context = await page.evaluate("""
        () => {
            const container = document.getElementById('pb-canvas-container');
            if (!container) {
                // Search for ANY canvas elements on page
                const allCanvases = document.querySelectorAll('canvas');
                return {
                    containerNotFound: true,
                    allCanvasCount: allCanvases.length,
                    allCanvasDetails: Array.from(allCanvases).map(c => ({
                        id: c.id,
                        className: c.className,
                        parentId: c.parentElement?.id,
                        parentClass: c.parentElement?.className?.substring?.(0, 60) || ''
                    }))
                };
            }
            return {
                containerNotFound: false,
                containerOuterHTML: container.outerHTML.substring(0, 1000),
                parentHTML: container.parentElement?.outerHTML?.substring?.(0, 500) || 'none'
            };
        }
        """)
        if html_context.get('containerNotFound'):
            print(f"  CONTAINER #pb-canvas-container NOT FOUND!")
            print(f"  All canvas elements on page: {html_context.get('allCanvasCount', 0)}")
            for c in html_context.get('allCanvasDetails', []):
                print(f"    canvas id={c.get('id')} class={c.get('className')} parent_id={c.get('parentId')} parent_class={c.get('parentClass')}")
        else:
            print(f"  Container outer HTML: {html_context.get('containerOuterHTML', 'N/A')}")

        await browser.close()

        print("\n" + "=" * 70)
        print("DIAGNOSIS COMPLETE")
        print(f"Screenshots in: {SCREENSHOT_DIR}")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
