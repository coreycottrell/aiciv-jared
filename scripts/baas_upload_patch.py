"""Patch BaaS server to add drag-and-drop (Method 4) and click-chooser (Method 5) to upload endpoint."""
import sys

BAAS_FILE = '/opt/baas/baas_server_simple.py'

with open(BAAS_FILE, 'r') as f:
    content = f.read()

# 1. Add drop_target_selector and click_selector to UploadFileReq model
old_model = "    mime_type: str = 'image/png'"
new_model = """    mime_type: str = 'image/png'
    drop_target_selector: Optional[str] = None  # CSS selector for drag-and-drop target area
    click_selector: Optional[str] = None  # CSS selector for button that opens file chooser dialog"""

if 'drop_target_selector' not in content:
    if old_model in content:
        content = content.replace(old_model, new_model, 1)
        print("Model patched: added drop_target_selector and click_selector")
    else:
        print("WARNING: Could not find model to patch, might already be modified")
else:
    print("Model already has drop_target_selector")

# 2. Add Method 4 and 5 before the final raise
# Find the exact block to replace
old_block = """        except Exception as e:
            errors.append(f'js_inject: {str(e)}')

        raise HTTPException(500, f'All upload methods failed: {"; ".join(errors)}')

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass"""

new_block = '''        except Exception as e:
            errors.append(f'js_inject: {str(e)}')

        # Method 4: Drag-and-drop simulation (for sites like LinkedIn that need native events)
        drop_sel = req.drop_target_selector or req.selector
        try:
            with open(actual_path, 'rb') as bf:
                b64_data_drop = base64.b64encode(bf.read()).decode()

            drop_js = f"""
            (function() {{
                var b64 = '{b64_data_drop}';
                var binary = atob(b64);
                var bytes = new Uint8Array(binary.length);
                for(var i=0; i<binary.length; i++) bytes[i] = binary.charCodeAt(i);
                var blob = new Blob([bytes], {{type: '{req.mime_type}'}});
                var file = new File([blob], '{req.filename}', {{type: '{req.mime_type}', lastModified: Date.now()}});
                var dt = new DataTransfer();
                dt.items.add(file);

                var target = document.querySelector('{drop_sel}');
                if (!target) return 'No drop target found for: {drop_sel}';

                target.dispatchEvent(new DragEvent('dragenter', {{bubbles: true, cancelable: true, dataTransfer: dt}}));
                target.dispatchEvent(new DragEvent('dragover', {{bubbles: true, cancelable: true, dataTransfer: dt}}));
                target.dispatchEvent(new DragEvent('drop', {{bubbles: true, cancelable: true, dataTransfer: dt}}));
                target.dispatchEvent(new DragEvent('dragleave', {{bubbles: true, cancelable: true, dataTransfer: dt}}));
                return 'Drop dispatched on ' + target.tagName + ', file size: ' + file.size;
            }})()
            """
            result = await page.evaluate(drop_js)
            if result and 'No drop target' not in str(result):
                _record_action(sid, 'upload-file-drop')
                return {
                    'success': True,
                    'method': 'drag_and_drop',
                    'selector': drop_sel,
                    'filename': req.filename,
                    'file_size': file_size,
                    'js_result': str(result)
                }
            else:
                errors.append(f'drag_drop: {str(result)}')
        except Exception as e:
            errors.append(f'drag_drop: {str(e)}')

        # Method 5: Click button to trigger native file chooser, then intercept with Playwright
        if req.click_selector:
            try:
                async with page.expect_file_chooser(timeout=10000) as fc_info:
                    await page.click(req.click_selector, timeout=5000)
                file_chooser = await fc_info.value
                await file_chooser.set_files(actual_path)
                _record_action(sid, 'upload-file-click-chooser')
                return {
                    'success': True,
                    'method': 'click_then_file_chooser',
                    'click_selector': req.click_selector,
                    'filename': req.filename,
                    'file_size': file_size
                }
            except Exception as e:
                errors.append(f'click_chooser: {str(e)}')

        raise HTTPException(500, f'All upload methods failed: {"; ".join(errors)}')

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass'''

if 'Method 4: Drag-and-drop' not in content:
    if old_block in content:
        content = content.replace(old_block, new_block, 1)
        print("Methods 4 and 5 added successfully")
    else:
        print("ERROR: Could not find the raise block to patch")
        print("Searching for alternative patterns...")
        # Try to find it with different whitespace
        if "raise HTTPException(500, f'All upload methods failed" in content:
            print("Found the raise but surrounding context differs")
        sys.exit(1)
else:
    print("Methods 4 and 5 already present")

with open(BAAS_FILE, 'w') as f:
    f.write(content)

print("")
print("PATCH COMPLETE - BaaS upload endpoint now has 5 methods:")
print("  1. Direct set_input_files on locator")
print("  2. File chooser event (click input + intercept)")
print("  3. JS DataTransfer injection (set files property)")
print("  4. Drag-and-drop simulation (NEW - for LinkedIn etc)")
print("  5. Click button + file chooser (NEW - for upload buttons)")
print("")
print("New request body fields:")
print("  drop_target_selector: CSS selector for the drop area (Method 4)")
print("  click_selector: CSS selector for button to click (Method 5)")
