#!/usr/bin/env python3
"""Second pass - check GSAP usage, fade-in CSS, backdrop-filter elements."""
import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 900})
        page.goto('https://purebrain.ai/purebrain-for-graham-martin/', wait_until='domcontentloaded', timeout=30000)
        time.sleep(2)

        pwd = page.query_selector("input[type='password']")
        if pwd:
            pwd.fill('skybet47')
            page.click("input[type='submit']")
            page.wait_for_load_state('domcontentloaded', timeout=15000)
            time.sleep(3)

        # Get fade-in CSS
        fade_css = page.evaluate("""
            () => {
                const result = [];
                document.querySelectorAll('style').forEach((s, i) => {
                    const content = s.textContent;
                    if (content.includes('gm-fade-in')) {
                        const idx = content.indexOf('gm-fade-in');
                        result.push(content.substring(Math.max(0,idx-200), idx+800));
                    }
                });
                return result;
            }
        """)
        print("=== FADE-IN CSS ===")
        for block in fade_css:
            print(block)
            print('---')

        # Check GSAP usage
        gsap_check = page.evaluate("""
            () => {
                return {
                    gsap_defined: typeof gsap !== 'undefined',
                    ScrollTrigger_defined: typeof ScrollTrigger !== 'undefined',
                    ST_count: typeof ScrollTrigger !== 'undefined' ? ScrollTrigger.getAll().length : 0
                };
            }
        """)
        print("\n=== GSAP CHECK ===")
        print(gsap_check)

        # ScrollTrigger instances
        if gsap_check['ST_count'] > 0:
            st_data = page.evaluate("""
                () => {
                    const instances = ScrollTrigger.getAll();
                    return instances.map(st => {
                        return {
                            trigger_info: st.trigger ? (String(st.trigger.className).substring(0,60) + ' ' + st.trigger.tagName) : 'null',
                            start: st.start,
                            end: st.end
                        };
                    });
                }
            """)
            print("ScrollTrigger instances:", st_data)
        else:
            print("No ScrollTrigger instances active")

        # Smooth scroll state
        smooth = page.evaluate("""
            () => {
                const htmlCS = getComputedStyle(document.documentElement);
                const bodyCS = getComputedStyle(document.body);
                return {
                    html_scroll_behavior: htmlCS.scrollBehavior,
                    body_scroll_behavior: bodyCS.scrollBehavior,
                    html_overflowY: htmlCS.overflowY,
                    body_overflowY: bodyCS.overflowY,
                    body_padding_top: bodyCS.paddingTop
                };
            }
        """)
        print("\n=== SMOOTH SCROLL STATE ===")
        for k, v in smooth.items():
            print(f"  {k}: {v}")

        # Backdrop filter elements
        backdrop_els = page.evaluate("""
            () => {
                const els = [];
                document.querySelectorAll('*').forEach(el => {
                    const cs = getComputedStyle(el);
                    if (cs.backdropFilter && cs.backdropFilter !== 'none') {
                        const rect = el.getBoundingClientRect();
                        els.push({
                            tag: el.tagName,
                            id: el.id || '',
                            cls: String(el.className).substring(0,60),
                            bf: cs.backdropFilter,
                            pos: cs.position,
                            h: Math.round(rect.height)
                        });
                    }
                });
                return els;
            }
        """)
        print(f"\n=== BACKDROP-FILTER ELEMENTS (GPU intensive): {len(backdrop_els)} ===")
        for el in backdrop_els:
            print(f"  {el['tag']}#{el['id']}.{el['cls']}: {el['bf']} pos={el['pos']}")

        # Check artistics theme scroll JS
        artistics_js = page.evaluate("""
            () => {
                // Look for artistics theme scroll-related global vars or functions
                const keys = Object.keys(window).filter(k =>
                    k.toLowerCase().includes('scroll') ||
                    k.toLowerCase().includes('artistics') ||
                    k.toLowerCase().includes('smooth') ||
                    k.toLowerCase().includes('lenis') ||
                    k.toLowerCase().includes('locomotive')
                );
                return keys;
            }
        """)
        print("\n=== WINDOW GLOBALS (scroll-related) ===")
        print(artistics_js)

        # Check the artistics theme external script for scroll features
        # Fetch the artistics main JS to see what scroll it sets up
        artistics_scripts = page.evaluate("""
            () => {
                const scripts = [];
                document.querySelectorAll('script[src]').forEach(s => {
                    if (s.src.includes('artistics') || s.src.includes('theme')) {
                        scripts.push(s.src);
                    }
                });
                return scripts;
            }
        """)
        print("\n=== ARTISTICS THEME SCRIPTS ===")
        for s in artistics_scripts:
            print(f"  {s}")

        # Check for any elements with position:fixed that might compete
        fixed_els = page.evaluate("""
            () => {
                const els = [];
                document.querySelectorAll('*').forEach(el => {
                    const cs = getComputedStyle(el);
                    if (cs.position === 'fixed' || cs.position === 'sticky') {
                        const rect = el.getBoundingClientRect();
                        els.push({
                            tag: el.tagName,
                            id: el.id || '',
                            cls: String(el.className).substring(0,60),
                            pos: cs.position,
                            top: cs.top,
                            zIndex: cs.zIndex,
                            h: Math.round(rect.height),
                            w: Math.round(rect.width)
                        });
                    }
                });
                return els;
            }
        """)
        print(f"\n=== FIXED/STICKY ELEMENTS: {len(fixed_els)} ===")
        for el in fixed_els:
            print(f"  {el['tag']}#{el['id']}.{el['cls'][:40]}: {el['pos']} top={el['top']} z={el['zIndex']} {el['w']}x{el['h']}")

        # Check body padding computation (double nav)
        body_metrics = page.evaluate("""
            () => {
                const body = document.body;
                const bodyCS = getComputedStyle(body);
                return {
                    paddingTop: bodyCS.paddingTop,
                    marginTop: bodyCS.marginTop,
                    offsetTop: body.offsetTop,
                    // WP theme padding
                    wp_admin_bar_present: !!document.getElementById('wpadminbar'),
                };
            }
        """)
        print("\n=== BODY METRICS ===")
        for k, v in body_metrics.items():
            print(f"  {k}: {v}")

        browser.close()
        print("\n=== DONE ===")

if __name__ == '__main__':
    run()
