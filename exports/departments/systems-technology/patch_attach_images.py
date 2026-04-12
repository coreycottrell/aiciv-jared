#!/usr/bin/env python3
"""Replace _linkedin_attach_images in social_suite.py with improved version."""
import re
import os

SOURCE = '/opt/baas/social_suite.py'
with open(SOURCE, 'r') as f:
    code = f.read()

# Find the old function boundaries
start_marker = 'async def _linkedin_attach_images(page, media_urls: list):'
end_markers = ['\nasync def _linkedin_post(', '\nasync def _twitter_']

start_idx = code.find(start_marker)
if start_idx == -1:
    print('ERROR: Could not find _linkedin_attach_images')
    exit(1)

# Find the end - next function definition
end_idx = len(code)
for marker in end_markers:
    idx = code.find(marker, start_idx + 100)
    if idx != -1 and idx < end_idx:
        end_idx = idx

old_func = code[start_idx:end_idx]
print(f'Found old function: {len(old_func)} chars, lines {code[:start_idx].count(chr(10))+1}-{code[:end_idx].count(chr(10))+1}')

new_func = r'''async def _linkedin_attach_images(page, media_urls: list):
    """Attach images to LinkedIn post composer using Playwright file chooser.
    Must be called AFTER the compose modal is open.

    Uses 5 strategies in order of reliability:
    1. Click media button -> expect file_chooser event
    2. Direct set_input_files on visible input[type=file]
    3. Force-reveal hidden file inputs then set_input_files
    4. JS-based file injection via DataTransfer + dispatchEvent
    5. Deep scan shadow DOM for file inputs
    """
    file_paths = await _linkedin_resolve_media(media_urls)
    if not file_paths:
        log.warning('LinkedIn: no valid media files to attach')
        return

    log.info(f'LinkedIn: attaching {len(file_paths)} image(s): {file_paths}')

    # Extended selector list for LinkedIn compose modal toolbar (2024-2026 variants)
    media_btn_selectors = [
        # Current LinkedIn (2025-2026)
        'button[aria-label="Add media"]',
        'button[aria-label="Add a photo"]',
        'button[aria-label="Add a media"]',
        'button[aria-label="Media"]',
        # Partial match variants (case insensitive via CSS)
        'div[role="dialog"] button[aria-label*="media" i]',
        'div[role="dialog"] button[aria-label*="photo" i]',
        'div[role="dialog"] button[aria-label*="image" i]',
        # Class-based selectors (LinkedIn specific)
        'button[aria-label="Add media"][type="button"]',
        'button.share-creation-state__detour-btn[aria-label*="media"]',
        'button.share-creation-state__detour-btn[aria-label*="photo"]',
        'button[data-control-name="share.addMedia"]',
        '.share-creation-state__detour-btn',
        # Footer toolbar buttons (media icon is typically 1st or 2nd button)
        'div[role="dialog"] footer button:nth-child(1)',
        'div[role="dialog"] footer button:nth-child(2)',
    ]

    attached = False

    # ---- Strategy 1: Click media button -> file_chooser intercept ----
    for selector in media_btn_selectors:
        try:
            loc = page.locator(selector).first
            if await loc.count() == 0:
                continue

            # Check if button is visible
            is_visible = await loc.is_visible()
            if not is_visible:
                continue

            log.info(f'LinkedIn: trying file_chooser with selector "{selector}"')
            async with page.expect_file_chooser(timeout=8000) as fc_info:
                await loc.click(force=True, timeout=5000)

            file_chooser = await fc_info.value
            await file_chooser.set_files(file_paths)
            attached = True
            log.info(f'LinkedIn: SUCCESS - attached images via file_chooser after clicking "{selector}"')
            break

        except Exception as e:
            log.warning(f'LinkedIn: file_chooser with "{selector}" failed: {e}')
            continue

    # ---- Strategy 2: Directly set input[type="file"] ----
    if not attached:
        log.info('LinkedIn: trying Strategy 2 - direct input[type=file]')
        try:
            file_input_selectors = [
                'div[role="dialog"] input[type="file"][accept*="image"]',
                'div[role="dialog"] input[type="file"]',
                'input[type="file"][accept*="image"]',
                'input[type="file"]',
                '.share-creation-state input[type="file"]',
            ]
            for selector in file_input_selectors:
                loc = page.locator(selector).first
                if await loc.count() > 0:
                    await loc.set_input_files(file_paths)
                    attached = True
                    log.info(f'LinkedIn: SUCCESS - attached images via direct input[type="file"] "{selector}"')
                    break
        except Exception as e:
            log.warning(f'LinkedIn: direct input[type="file"] failed: {e}')

    # ---- Strategy 3: Force-reveal hidden file inputs via JS ----
    if not attached:
        log.info('LinkedIn: trying Strategy 3 - force-reveal hidden file inputs')
        try:
            has_file_input = await page.evaluate("""() => document.querySelectorAll('input[type="file"]').length""")
            log.info(f'LinkedIn: found {has_file_input} file input(s) on page')
            if has_file_input > 0:
                await page.evaluate("""() => {
                    document.querySelectorAll('input[type="file"]').forEach(el => {
                        el.style.display = 'block';
                        el.style.opacity = '1';
                        el.style.visibility = 'visible';
                        el.style.position = 'fixed';
                        el.style.top = '0';
                        el.style.left = '0';
                        el.style.width = '200px';
                        el.style.height = '200px';
                        el.style.zIndex = '99999';
                        el.removeAttribute('hidden');
                    });
                }""")
                await asyncio.sleep(0.5)
                loc = page.locator('input[type="file"]').first
                await loc.set_input_files(file_paths)
                attached = True
                log.info('LinkedIn: SUCCESS - attached images via forced-visible input[type="file"]')
        except Exception as e:
            log.warning(f'LinkedIn: forced file input failed: {e}')

    # ---- Strategy 4: JS DataTransfer drop simulation ----
    if not attached:
        log.info('LinkedIn: trying Strategy 4 - JS DataTransfer drop simulation')
        try:
            import base64 as _b64
            with open(file_paths[0], 'rb') as f:
                file_b64 = _b64.b64encode(f.read()).decode()

            fname = os.path.basename(file_paths[0])
            ext = fname.rsplit('.', 1)[-1].lower() if '.' in fname else 'jpg'
            mime_map = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'gif': 'image/gif', 'webp': 'image/webp'}
            mime = mime_map.get(ext, 'image/jpeg')

            js_code = """(args) => {
                return new Promise((resolve) => {
                    try {
                        const binary = atob(args.data);
                        const bytes = new Uint8Array(binary.length);
                        for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
                        const blob = new Blob([bytes], { type: args.mime });
                        const file = new File([blob], args.name, { type: args.mime });

                        const dropTarget = document.querySelector('[contenteditable="true"][role="textbox"]')
                            || document.querySelector('[role="dialog"]')
                            || document.querySelector('.ql-editor');

                        if (!dropTarget) {
                            resolve('no_drop_target');
                            return;
                        }

                        const dt = new DataTransfer();
                        dt.items.add(file);

                        ['dragenter', 'dragover', 'drop'].forEach(evtName => {
                            const evt = new DragEvent(evtName, {
                                bubbles: true, cancelable: true, dataTransfer: dt
                            });
                            dropTarget.dispatchEvent(evt);
                        });

                        // Also try setting it on any file input we find
                        const fileInput = document.querySelector('input[type="file"]');
                        if (fileInput) {
                            const dt2 = new DataTransfer();
                            dt2.items.add(file);
                            fileInput.files = dt2.files;
                            fileInput.dispatchEvent(new Event('change', { bubbles: true }));
                            fileInput.dispatchEvent(new Event('input', { bubbles: true }));
                        }

                        resolve('drop_dispatched');
                    } catch(e) {
                        resolve('error: ' + e.message);
                    }
                });
            }"""

            result = await page.evaluate(js_code, {'data': file_b64, 'name': fname, 'mime': mime})

            if result == 'drop_dispatched':
                await asyncio.sleep(3)
                has_img = await page.evaluate("""() => {
                    const dialog = document.querySelector('[role="dialog"]');
                    if (!dialog) return false;
                    const indicators = dialog.querySelectorAll('img[src*="blob:"], img[src*="data:"], .media-preview, [data-test-image-upload], .share-box-image-thumbnail');
                    return indicators.length > 0;
                }""")
                if has_img:
                    attached = True
                    log.info('LinkedIn: SUCCESS - attached images via DataTransfer drop')
                else:
                    log.warning('LinkedIn: DataTransfer drop dispatched but no image appeared in composer')
            else:
                log.warning(f'LinkedIn: DataTransfer drop result: {result}')
        except Exception as e:
            log.warning(f'LinkedIn: DataTransfer drop failed: {e}')

    # ---- Strategy 5: Deep scan for file inputs including shadow DOM ----
    if not attached:
        log.info('LinkedIn: trying Strategy 5 - deep scan for file inputs')
        try:
            result = await page.evaluate("""() => {
                function findFileInputs(root, depth) {
                    if (depth > 5) return [];
                    const inputs = [];
                    root.querySelectorAll('input[type="file"]').forEach(el => {
                        inputs.push({
                            accept: el.accept, id: el.id, name: el.name,
                            cls: el.className, display: getComputedStyle(el).display,
                            inDialog: !!el.closest('[role="dialog"]')
                        });
                    });
                    root.querySelectorAll('*').forEach(el => {
                        if (el.shadowRoot) {
                            findFileInputs(el.shadowRoot, depth + 1).forEach(i => inputs.push(i));
                        }
                    });
                    return inputs;
                }
                return JSON.stringify(findFileInputs(document, 0));
            }""")
            log.info(f'LinkedIn: deep scan file inputs: {result}')
        except Exception as e:
            log.warning(f'LinkedIn: deep scan failed: {e}')

    if attached:
        # Wait for LinkedIn to process the image upload
        await asyncio.sleep(4)
        log.info('LinkedIn: image attachment complete')
    else:
        # Take debug screenshot and dump DOM info
        debug_ss = await page.screenshot()
        ss_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screenshots', 'social')
        os.makedirs(ss_dir, exist_ok=True)
        debug_path = os.path.join(ss_dir, f'linkedin_media_debug_{int(time.time())}.png')
        with open(debug_path, 'wb') as f:
            f.write(debug_ss)

        try:
            dom_info = await page.evaluate("""() => {
                const dialog = document.querySelector('[role="dialog"]');
                if (!dialog) return 'NO_DIALOG_FOUND';
                const buttons = [];
                dialog.querySelectorAll('button').forEach(b => {
                    buttons.push({
                        aria: b.getAttribute('aria-label'),
                        text: (b.innerText||'').substring(0,40).trim(),
                        vis: b.offsetParent !== null
                    });
                });
                const inputs = [];
                document.querySelectorAll('input').forEach(i => {
                    inputs.push({
                        type: i.type, accept: i.accept,
                        name: i.name, display: getComputedStyle(i).display
                    });
                });
                return JSON.stringify({dialogButtons: buttons, allInputs: inputs});
            }""")
            log.error(f'LinkedIn: FAILED to attach images. Debug screenshot: {debug_path}. DOM info: {dom_info}')
        except Exception as ex:
            log.error(f'LinkedIn: FAILED to attach images. Debug screenshot: {debug_path}. DOM dump error: {ex}')


'''

# Do the replacement
code = code[:start_idx] + new_func + code[end_idx:]

with open(SOURCE, 'w') as f:
    f.write(code)

print(f'SUCCESS: Replaced _linkedin_attach_images ({len(old_func)} -> {len(new_func)} chars)')
print('Changes:')
print('  1. Extended media button selectors (14 variants including 2025-2026 LinkedIn)')
print('  2. All failure logs upgraded from debug to warning (visible in prod logs)')
print('  3. Added Strategy 4: JS DataTransfer drop simulation')
print('  4. Added Strategy 5: Shadow DOM deep scan')
print('  5. DOM info dump on failure for debugging')
print('  6. Visibility check before clicking buttons')
