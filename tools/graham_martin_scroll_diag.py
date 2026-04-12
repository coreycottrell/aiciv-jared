#!/usr/bin/env python3
"""
Scroll Jank Diagnostic for purebrain.ai/purebrain-for-graham-martin/
Captures screenshots at multiple scroll positions and extracts CSS/JS causing jank.
"""
import os, time, json
from pathlib import Path
from playwright.sync_api import sync_playwright

TARGET_URL = 'https://purebrain.ai/purebrain-for-graham-martin/'
PASSWORD = 'skybet47'
SCREENSHOT_DIR = Path('/home/jared/projects/AI-CIV/aether/tools/screenshots/graham-scroll-diag')
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

def ss(page, name):
    p = str(SCREENSHOT_DIR / f'{name}.png')
    try:
        page.screenshot(path=p, full_page=False, timeout=15000)
        print(f'[SS] {p}')
    except Exception as e:
        print(f'[SS FAIL] {name}: {e}')
    return p

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            '--no-sandbox',
            '--disable-dev-shm-usage',
        ])
        context = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = context.new_page()

        # Collect console messages
        console_msgs = []
        page.on('console', lambda msg: console_msgs.append(f'[{msg.type}] {msg.text}'))

        print(f'\n=== NAVIGATING TO {TARGET_URL} ===')
        page.goto(TARGET_URL, wait_until='domcontentloaded', timeout=30000)
        time.sleep(2)

        # Handle password gate if present
        try:
            pwd_input = page.query_selector("input[type='password']")
            if pwd_input:
                print('[AUTH] Password gate detected, entering password...')
                pwd_input.fill(PASSWORD)
                page.click("input[type='submit']")
                page.wait_for_load_state('domcontentloaded', timeout=15000)
                time.sleep(3)
                print('[AUTH] Password submitted')
        except Exception as e:
            print(f'[AUTH] No password gate or error: {e}')

        ss(page, '01-initial-load')

        # =============================================
        # 1. EXTRACT PAGE SOURCE FOR CSS/JS ANALYSIS
        # =============================================
        print('\n=== EXTRACTING PAGE SOURCE ===')

        # Get full HTML
        html_content = page.content()

        # Save full HTML for inspection
        html_path = str(SCREENSHOT_DIR / 'page-source.html')
        with open(html_path, 'w') as f:
            f.write(html_content)
        print(f'[HTML] Saved to {html_path} ({len(html_content)} bytes)')

        # =============================================
        # 2. EXTRACT ALL INLINE STYLES AND SCRIPTS
        # =============================================
        print('\n=== EXTRACTING INLINE CSS/JS ===')

        # Get all style tags content
        style_data = page.evaluate('''
            () => {
                const styles = [];
                document.querySelectorAll('style').forEach((s, i) => {
                    styles.push({
                        index: i,
                        id: s.id || '',
                        content: s.textContent.substring(0, 3000)
                    });
                });
                return styles;
            }
        ''')
        print(f'[CSS] Found {len(style_data)} <style> blocks')
        for s in style_data:
            print(f'  Style #{s["index"]} id="{s["id"]}": {len(s["content"])} chars')

        # Get all external stylesheets
        stylesheets = page.evaluate('''
            () => {
                const sheets = [];
                document.querySelectorAll('link[rel="stylesheet"]').forEach(l => {
                    sheets.push(l.href);
                });
                return sheets;
            }
        ''')
        print(f'[CSS] External stylesheets: {len(stylesheets)}')
        for href in stylesheets[:10]:
            print(f'  {href[:100]}')

        # Get all script tags
        scripts = page.evaluate('''
            () => {
                const scripts = [];
                document.querySelectorAll('script').forEach((s, i) => {
                    scripts.push({
                        index: i,
                        src: s.src || '',
                        type: s.type || '',
                        content_preview: s.src ? '' : s.textContent.substring(0, 500)
                    });
                });
                return scripts;
            }
        ''')
        print(f'[JS] Found {len(scripts)} <script> tags')
        inline_scripts = [s for s in scripts if not s['src'] and s['content_preview']]
        external_scripts = [s for s in scripts if s['src']]
        print(f'  Inline: {len(inline_scripts)}, External: {len(external_scripts)}')

        # =============================================
        # 3. SCROLL-SPECIFIC CSS ANALYSIS
        # =============================================
        print('\n=== SCROLL BEHAVIOR ANALYSIS ===')

        scroll_analysis = page.evaluate('''
            () => {
                const results = {
                    scroll_behavior: [],
                    scroll_snap: [],
                    position_sticky: [],
                    position_fixed: [],
                    overflow_hidden: [],
                    overflow_scroll: [],
                    transforms: [],
                    will_change: [],
                    animations: [],
                    parallax_hints: []
                };

                // Check all elements for scroll-related CSS
                const allElements = document.querySelectorAll('*');
                let count = 0;
                allElements.forEach(el => {
                    if (count > 2000) return;  // limit
                    const cs = getComputedStyle(el);
                    const tag = el.tagName.toLowerCase();
                    const cls = el.className ? String(el.className).substring(0, 50) : '';
                    const id = el.id ? el.id.substring(0, 30) : '';
                    const label = `${tag}${id ? '#'+id : ''}${cls ? '.'+cls.replace(/\s+/g, '.') : ''}`.substring(0, 80);

                    if (cs.scrollBehavior && cs.scrollBehavior !== 'auto') {
                        results.scroll_behavior.push({el: label, value: cs.scrollBehavior});
                    }
                    if (cs.scrollSnapType && cs.scrollSnapType !== 'none') {
                        results.scroll_snap.push({el: label, value: cs.scrollSnapType});
                    }
                    if (cs.position === 'sticky') {
                        results.position_sticky.push({el: label, top: cs.top, bottom: cs.bottom});
                    }
                    if (cs.position === 'fixed') {
                        results.position_fixed.push({el: label, top: cs.top});
                    }
                    if ((cs.overflow === 'hidden' || cs.overflowY === 'hidden') && el !== document.documentElement) {
                        results.overflow_hidden.push({el: label, overflow: cs.overflow, overflowY: cs.overflowY});
                    }
                    if (cs.overflowY === 'scroll' || cs.overflowY === 'auto' || cs.overflow === 'auto' || cs.overflow === 'scroll') {
                        const rect = el.getBoundingClientRect();
                        if (rect.height > 50) {  // only meaningful containers
                            results.overflow_scroll.push({el: label, overflow: cs.overflow, overflowY: cs.overflowY, height: Math.round(rect.height)});
                        }
                    }
                    if (cs.transform && cs.transform !== 'none') {
                        results.transforms.push({el: label, transform: cs.transform.substring(0, 60)});
                    }
                    if (cs.willChange && cs.willChange !== 'auto') {
                        results.will_change.push({el: label, value: cs.willChange});
                    }
                    if (cs.animation && cs.animation !== 'none' && cs.animation !== '') {
                        results.animations.push({el: label, animation: cs.animation.substring(0, 80)});
                    }
                    // Check for data-parallax or similar attributes
                    if (el.hasAttribute('data-parallax') || el.hasAttribute('data-scroll') ||
                        el.hasAttribute('data-jarallax') || el.classList.contains('parallax')) {
                        results.parallax_hints.push({el: label, attrs: el.getAttributeNames().join(',')});
                    }
                    count++;
                });

                return results;
            }
        ''')

        print(f'[SCROLL] scroll-behavior (non-auto): {len(scroll_analysis["scroll_behavior"])}')
        for item in scroll_analysis['scroll_behavior']:
            print(f'  {item["el"]}: {item["value"]}')

        print(f'[SCROLL] scroll-snap: {len(scroll_analysis["scroll_snap"])}')
        for item in scroll_analysis['scroll_snap']:
            print(f'  {item["el"]}: {item["value"]}')

        print(f'[STICKY] position:sticky elements: {len(scroll_analysis["position_sticky"])}')
        for item in scroll_analysis['position_sticky']:
            print(f'  {item["el"]}: top={item["top"]}')

        print(f'[FIXED] position:fixed elements: {len(scroll_analysis["position_fixed"])}')
        for item in scroll_analysis['position_fixed'][:10]:
            print(f'  {item["el"]}: top={item["top"]}')

        print(f'[OVERFLOW] overflow:hidden elements: {len(scroll_analysis["overflow_hidden"])}')
        for item in scroll_analysis['overflow_hidden'][:15]:
            print(f'  {item["el"]}: {item["overflow"]} / y:{item["overflowY"]}')

        print(f'[OVERFLOW] scrollable containers: {len(scroll_analysis["overflow_scroll"])}')
        for item in scroll_analysis['overflow_scroll'][:10]:
            print(f'  {item["el"]}: h={item["height"]}px {item["overflow"]}')

        print(f'[TRANSFORM] transformed elements: {len(scroll_analysis["transforms"])}')
        for item in scroll_analysis['transforms'][:10]:
            print(f'  {item["el"]}: {item["transform"]}')

        print(f'[WILL-CHANGE] will-change elements: {len(scroll_analysis["will_change"])}')
        for item in scroll_analysis['will_change']:
            print(f'  {item["el"]}: {item["value"]}')

        print(f'[ANIMATION] animated elements: {len(scroll_analysis["animations"])}')
        for item in scroll_analysis['animations'][:10]:
            print(f'  {item["el"]}: {item["animation"]}')

        print(f'[PARALLAX] parallax elements: {len(scroll_analysis["parallax_hints"])}')
        for item in scroll_analysis['parallax_hints']:
            print(f'  {item["el"]}: {item["attrs"]}')

        # =============================================
        # 4. SEARCH INLINE STYLES FOR SCROLL KEYWORDS
        # =============================================
        print('\n=== INLINE STYLE KEYWORD SCAN ===')

        scroll_keywords = page.evaluate('''
            () => {
                const keywords = ['scroll', 'parallax', 'jarallax', 'smooth', 'snap', 'sticky',
                                  'overflow', 'transform', 'will-change', 'backface', 'perspective',
                                  'translateY', 'translateZ', 'fixed', 'lenis', 'locomotive', 'gsap',
                                  'ScrollTrigger', 'scrollmagic', 'skrollr'];
                const results = {};

                // Check all inline <style> blocks
                const allStyles = Array.from(document.querySelectorAll('style')).map(s => s.textContent).join('\\n');
                keywords.forEach(kw => {
                    const matches = (allStyles.match(new RegExp(kw, 'gi')) || []).length;
                    if (matches > 0) results[kw] = matches;
                });

                // Check inline style attributes on elements
                const inlineStyles = Array.from(document.querySelectorAll('[style]')).map(el => el.getAttribute('style')).join('\\n');
                const inlineResults = {};
                keywords.forEach(kw => {
                    const matches = (inlineStyles.match(new RegExp(kw, 'gi')) || []).length;
                    if (matches > 0) inlineResults[kw] = matches;
                });

                return {in_style_tags: results, in_inline_styles: inlineResults};
            }
        ''')
        print('[STYLE TAGS keywords found]:')
        if scroll_keywords['in_style_tags']:
            for kw, count in scroll_keywords['in_style_tags'].items():
                print(f'  "{kw}": {count} occurrences')
        else:
            print('  None')

        print('[INLINE STYLES keywords found]:')
        if scroll_keywords['in_inline_styles']:
            for kw, count in scroll_keywords['in_inline_styles'].items():
                print(f'  "{kw}": {count} occurrences')
        else:
            print('  None')

        # =============================================
        # 5. SEARCH INLINE SCRIPTS FOR SCROLL LISTENERS
        # =============================================
        print('\n=== SCROLL EVENT LISTENER SCAN ===')

        scroll_js = page.evaluate('''
            () => {
                const scrollKW = ['scroll', 'parallax', 'jarallax', 'locomotive', 'lenis', 'gsap',
                                   'ScrollTrigger', 'scrollmagic', 'skrollr', 'requestAnimationFrame',
                                   'addEventListener.*scroll', 'onscroll'];
                const allJS = Array.from(document.querySelectorAll('script:not([src])'))
                               .map(s => s.textContent).join('\\n');
                const results = {};
                scrollKW.forEach(kw => {
                    const matches = (allJS.match(new RegExp(kw, 'gi')) || []).length;
                    if (matches > 0) results[kw] = matches;
                });

                // Also extract snippets around scroll references
                const snippets = [];
                const lines = allJS.split('\\n');
                lines.forEach((line, i) => {
                    if (line.toLowerCase().includes('scroll') || line.toLowerCase().includes('parallax')) {
                        snippets.push({line: i, content: line.trim().substring(0, 150)});
                    }
                });

                return {keyword_counts: results, scroll_snippets: snippets.slice(0, 30)};
            }
        ''')

        print('[INLINE JS scroll keywords]:')
        if scroll_js['keyword_counts']:
            for kw, count in scroll_js['keyword_counts'].items():
                print(f'  "{kw}": {count}')
        else:
            print('  None')

        print(f'[INLINE JS scroll/parallax lines]: {len(scroll_js["scroll_snippets"])} found')
        for snippet in scroll_js['scroll_snippets'][:20]:
            print(f'  line {snippet["line"]}: {snippet["content"]}')

        # =============================================
        # 6. CHECK EXTERNAL SCRIPTS FOR SCROLL LIBS
        # =============================================
        print('\n=== EXTERNAL SCRIPT SOURCES FOR SCROLL LIBS ===')
        scroll_script_libs = ['jarallax', 'parallax', 'locomotive', 'lenis', 'gsap', 'scrollmagic',
                               'skrollr', 'smooth-scroll', 'fullpage', 'pagepiling', 'stellar']
        for script in external_scripts:
            src_lower = script['src'].lower()
            for lib in scroll_script_libs:
                if lib in src_lower:
                    print(f'  FOUND: {lib} in {script["src"][:100]}')

        # =============================================
        # 7. GET PAGE DIMENSIONS AND SCROLL METRICS
        # =============================================
        print('\n=== PAGE DIMENSIONS ===')
        dims = page.evaluate('''
            () => ({
                scrollHeight: document.documentElement.scrollHeight,
                clientHeight: document.documentElement.clientHeight,
                bodyScrollHeight: document.body.scrollHeight,
                bodyOverflow: getComputedStyle(document.body).overflow,
                bodyOverflowY: getComputedStyle(document.body).overflowY,
                htmlOverflow: getComputedStyle(document.documentElement).overflow,
                htmlOverflowY: getComputedStyle(document.documentElement).overflowY,
                bodyPosition: getComputedStyle(document.body).position,
                htmlScrollBehavior: getComputedStyle(document.documentElement).scrollBehavior,
                bodyScrollBehavior: getComputedStyle(document.body).scrollBehavior,
            })
        ''')
        for k, v in dims.items():
            print(f'  {k}: {v}')

        # =============================================
        # 8. SCROLL THROUGH PAGE WITH SCREENSHOTS
        # =============================================
        print('\n=== SCROLL SCREENSHOTS ===')

        scroll_height = dims['scrollHeight']
        viewport_height = 900
        num_stops = 6

        for i in range(num_stops + 1):
            scroll_pos = int((scroll_height - viewport_height) * i / num_stops)
            scroll_pos = max(0, min(scroll_pos, scroll_height - viewport_height))
            page.evaluate(f'window.scrollTo(0, {scroll_pos})')
            time.sleep(1.5)  # Wait for animations to settle
            ss(page, f'0{i+2}-scroll-y{scroll_pos}')
            print(f'[SCROLL] y={scroll_pos}px')

        # Back to top
        page.evaluate('window.scrollTo(0, 0)')
        time.sleep(1)

        # =============================================
        # 9. EXTRACT SPECIFIC CSS BLOCKS AROUND SCROLL
        # =============================================
        print('\n=== EXTRACTING SCROLL CSS BLOCKS FROM STYLE TAGS ===')
        style_content = page.evaluate('''
            () => {
                const allStyles = Array.from(document.querySelectorAll('style')).map(s => s.textContent).join('\\n---STYLE BREAK---\\n');
                // Find all CSS rules containing scroll-relevant properties
                const relevant = [];
                const rules = allStyles.split(/[{}]/);
                for (let i = 0; i < rules.length - 1; i += 2) {
                    const selector = rules[i].trim();
                    const props = rules[i+1] || '';
                    const relevantProps = ['scroll', 'overflow', 'transform', 'position:sticky',
                                          'position:fixed', 'will-change', 'animation', 'transition',
                                          'backface', 'perspective', 'translateY', 'parallax'];
                    if (relevantProps.some(kw => props.toLowerCase().includes(kw) || selector.toLowerCase().includes(kw))) {
                        if (selector.length < 200) {
                            relevant.push({selector: selector.substring(0,150), props: props.trim().substring(0,200)});
                        }
                    }
                }
                return relevant.slice(0, 60);
            }
        ''')
        print(f'[CSS RULES] Found {len(style_content)} scroll-relevant CSS rules')
        for rule in style_content[:40]:
            print(f'\n  SELECTOR: {rule["selector"]}')
            print(f'  PROPS: {rule["props"][:150]}')

        # =============================================
        # 10. LOOK FOR JARALLAX SPECIFICALLY (COMMON JANK SOURCE)
        # =============================================
        print('\n=== JARALLAX / PARALLAX ELEMENT CHECK ===')
        jarallax_check = page.evaluate('''
            () => {
                const results = {
                    jarallax_elements: [],
                    background_video_elements: [],
                    video_elements: [],
                    canvas_elements: [],
                    three_js_hints: []
                };

                // jarallax elements
                document.querySelectorAll('[data-jarallax], [class*="jarallax"], .jarallax').forEach(el => {
                    const rect = el.getBoundingClientRect();
                    results.jarallax_elements.push({
                        tag: el.tagName,
                        cls: String(el.className).substring(0,80),
                        attrs: el.getAttributeNames().join(','),
                        height: Math.round(rect.height)
                    });
                });

                // bg videos
                document.querySelectorAll('[class*="bg-video"], [class*="video-bg"], [class*="background-video"]').forEach(el => {
                    results.background_video_elements.push({tag: el.tagName, cls: String(el.className).substring(0,80)});
                });

                // video tags
                document.querySelectorAll('video').forEach(el => {
                    results.video_elements.push({
                        src: el.src || el.currentSrc || '',
                        autoplay: el.autoplay,
                        loop: el.loop,
                        width: el.videoWidth,
                        height: el.videoHeight
                    });
                });

                // canvas (Three.js)
                document.querySelectorAll('canvas').forEach(el => {
                    const rect = el.getBoundingClientRect();
                    results.canvas_elements.push({
                        width: el.width, height: el.height,
                        rect_w: Math.round(rect.width), rect_h: Math.round(rect.height)
                    });
                });

                // window globals hint at Three.js or GSAP
                const hints = [];
                if (typeof THREE !== 'undefined') hints.push('THREE.js loaded');
                if (typeof gsap !== 'undefined') hints.push('GSAP loaded');
                if (typeof ScrollTrigger !== 'undefined') hints.push('ScrollTrigger loaded');
                if (typeof LocomotiveScroll !== 'undefined') hints.push('LocomotiveScroll loaded');
                if (typeof Lenis !== 'undefined') hints.push('Lenis loaded');
                if (typeof jarallax !== 'undefined') hints.push('jarallax loaded');
                results.three_js_hints = hints;

                return results;
            }
        ''')

        print(f'[JARALLAX] Elements: {len(jarallax_check["jarallax_elements"])}')
        for el in jarallax_check['jarallax_elements']:
            print(f'  {el["tag"]}.{el["cls"]}: h={el["height"]}px attrs={el["attrs"]}')

        print(f'[VIDEO] Background video elements: {len(jarallax_check["background_video_elements"])}')
        for el in jarallax_check['background_video_elements']:
            print(f'  {el["tag"]}.{el["cls"]}')

        print(f'[VIDEO] <video> tags: {len(jarallax_check["video_elements"])}')
        for v in jarallax_check['video_elements']:
            print(f'  src={v["src"][:80]} autoplay={v["autoplay"]} loop={v["loop"]}')

        print(f'[CANVAS] <canvas> elements: {len(jarallax_check["canvas_elements"])}')
        for c in jarallax_check['canvas_elements']:
            print(f'  {c["width"]}x{c["height"]} (rendered: {c["rect_w"]}x{c["rect_h"]})')

        print(f'[GLOBAL LIBS]: {jarallax_check["three_js_hints"]}')

        # =============================================
        # 11. LOOK AT THE ACTUAL CSS/HTML CONTENT for scroll sections
        # =============================================
        print('\n=== SECTION STRUCTURE AUDIT ===')
        sections = page.evaluate('''
            () => {
                const sections = [];
                document.querySelectorAll('section, .elementor-section, [class*="section"]').forEach((el, i) => {
                    if (i > 20) return;
                    const cs = getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    sections.push({
                        tag: el.tagName,
                        cls: String(el.className).substring(0,80),
                        id: el.id || '',
                        height: Math.round(rect.height),
                        position: cs.position,
                        overflow: cs.overflow,
                        overflowY: cs.overflowY,
                        bgImage: cs.backgroundImage !== 'none' ? cs.backgroundImage.substring(0,60) : '',
                        bgAttachment: cs.backgroundAttachment,
                        transform: cs.transform !== 'none' ? cs.transform.substring(0,40) : '',
                        willChange: cs.willChange !== 'auto' ? cs.willChange : ''
                    });
                });
                return sections;
            }
        ''')
        print(f'[SECTIONS] Found {len(sections)} sections')
        for s in sections[:15]:
            flags = []
            if s['bgAttachment'] == 'fixed': flags.append('BG-FIXED!')
            if s['overflow'] == 'hidden': flags.append('overflow:hidden')
            if s['transform']: flags.append(f'transform:{s["transform"]}')
            if s['willChange']: flags.append(f'will-change:{s["willChange"]}')
            if s['bgImage']: flags.append(f'bg-img')
            if s['position'] in ['sticky', 'fixed']: flags.append(f'pos:{s["position"]}')
            flag_str = ' | '.join(flags) if flags else 'clean'
            print(f'  {s["tag"]}.{s["cls"][:50]}: h={s["height"]}px pos={s["position"]} [{flag_str}]')

        # =============================================
        # CONSOLE SUMMARY
        # =============================================
        print('\n=== CONSOLE MESSAGES ===')
        errors = [m for m in console_msgs if '[error]' in m.lower()]
        warnings = [m for m in console_msgs if '[warning]' in m.lower()]
        print(f'Errors: {len(errors)}, Warnings: {len(warnings)}, Total: {len(console_msgs)}')
        for msg in console_msgs[:20]:
            print(f'  {msg[:120]}')

        # Save analysis data
        analysis = {
            'scroll_analysis': scroll_analysis,
            'dims': dims,
            'scroll_keywords': scroll_keywords,
            'scroll_js': scroll_js['keyword_counts'],
            'jarallax_check': jarallax_check,
            'sections': sections,
            'console_errors': errors
        }
        with open(str(SCREENSHOT_DIR / 'analysis.json'), 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f'\n[DATA] Analysis saved to {SCREENSHOT_DIR}/analysis.json')
        print(f'[SCREENSHOTS] All screenshots in {SCREENSHOT_DIR}/')

        browser.close()
        print('\n=== DIAGNOSIS COMPLETE ===')

if __name__ == '__main__':
    run()
