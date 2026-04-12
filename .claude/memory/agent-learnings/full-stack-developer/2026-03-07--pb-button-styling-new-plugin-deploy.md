# 2026-03-07 — pb-button-styling New Plugin Deployment

**Type**: operational + teaching
**Topic**: Deploying a brand-new WordPress plugin that doesn't exist on the server yet

## Context
Deployed two plugins in one session:
1. Updated existing `purebrain-security` (removing button CSS that was extracted)
2. Created and activated NEW plugin `pb-button-styling` v1.0.0

## Key Learnings

### WP REST API POST /plugins does NOT support zip upload
- Sending multipart form data with a zip file returns `plugins_api_failed` (404)
- The REST endpoint only supports installing from WordPress.org plugin repo by slug
- DO NOT attempt REST API zip upload for new private plugins

### Correct approach: WP Admin Upload UI (plugin-install.php?tab=upload)
- Navigate to `wp-admin/plugin-install.php?tab=upload`
- Use `input[type="file"][name="pluginzip"]` with `set_input_files()`
- Click `#install-plugin-submit`
- After success: click "Activate Plugin" link that appears on result page
- This handles the full install + activate flow in one browser session

### Cookie HTTP login fails on GoDaddy-hosted WP
- Posting to `wp-login.php` with form data redirects back to login page
- Cookies do not get set properly via urllib HTTP
- Root cause: GoDaddy SSO intercepts the form POST
- FIX: Use Playwright browser automation, which properly handles SSO

### GoDaddy SSO toggle pattern (critical)
```python
sso_toggle = page.locator(".wpaas-sso-login-toggle")
if await sso_toggle.count() > 0 and await sso_toggle.is_visible():
    await sso_toggle.click()
    await page.wait_for_timeout(1500)
# Then fill #user_login, #user_pass normally
```

### Plugin editor still works via Playwright
- Navigate to `plugin-editor.php?file=...&plugin=...`
- Set CodeMirror: `page.evaluate("cm => { document.querySelector('.CodeMirror').CodeMirror.setValue(cm); cm.save(); }", content)`
- Also update textarea: `document.getElementById('newcontent').value = content`
- Submit `#submit`
- Look for "File edited successfully" in body text

### Zip creation for upload
```python
import zipfile
with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(str(php_path), f"{plugin_slug}/{php_filename}")
```
- Zip must contain directory: `pb-button-styling/pb-button-styling.php` (not just the PHP file at root)

## Files
- New plugin: `tools/security/pb-button-styling/pb-button-styling.php`
- Deploy script: `tools/security/deploy_playwright_both_plugins.py`
- Exported zip: `exports/pb-button-styling.zip`

## Verification Commands
```bash
# Check via REST API
python3 -c "
import base64, json, urllib.request, re
env = open('.env').read()
def e(k): m = re.search(rf\"^{k}='([^']+)'\", env, re.M); return m.group(1) if m else ''
tok = base64.b64encode(f'Aether:{e(\"PUREBRAIN_WP_APP_PASSWORD\")}'.encode()).decode()
req = urllib.request.Request('https://purebrain.ai/wp-json/wp/v2/plugins', headers={'Authorization': f'Basic {tok}'})
plugins = json.loads(urllib.request.urlopen(req).read())
for p in plugins:
    if 'pb-button' in p['plugin'] or 'purebrain-security' in p['plugin']:
        print(p['plugin'], p['status'])
"
```
