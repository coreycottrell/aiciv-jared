#!/usr/bin/env python3
"""Patch cookie_sync_page.py and baas_server_simple.py to support proxy login flow.

The core issue: sync_start launches browser with proxy=None, so cookies are born
on the server's IP instead of the proxy IP. This causes LinkedIn 429s when PureSurf
later uses those cookies from a different (proxy) IP.

Fix: Accept proxy_provider in /sync/start, resolve it to a proxy URL, and pass it
to _launch() so the browser session runs through the proxy from the start.
"""

import re
import sys
import os

SYNC_FILE = '/opt/baas/cookie_sync_page.py'
MAIN_FILE = '/opt/baas/baas_server_simple.py'

def patch_sync_file():
    with open(SYNC_FILE, 'r') as f:
        content = f.read()

    # ===== 1. Add proxy_provider to SyncStartReq =====
    old_model = '''class SyncStartReq(BaseModel):
    profile: str
    platform: str'''

    new_model = '''class SyncStartReq(BaseModel):
    profile: str
    platform: str
    proxy_provider: Optional[str] = 'residential'  # CRITICAL: cookies must be born on proxy IP'''

    if old_model not in content:
        print('WARNING: SyncStartReq already patched or not found')
    else:
        content = content.replace(old_model, new_model)
        print('PATCHED: SyncStartReq model - added proxy_provider field')

    # ===== 2. Update extend_sync_routes signature to accept resolve_proxy_fn =====
    old_sig = '''def extend_sync_routes(app: FastAPI, sessions: dict, auth_fn, launch_fn,
                       save_cookies_fn, cookies_path_fn, profile_cookies_path_fn,
                       encrypt_cookies_fn, decrypt_cookies_fn, profiles_dir: str):'''

    new_sig = '''def extend_sync_routes(app: FastAPI, sessions: dict, auth_fn, launch_fn,
                       save_cookies_fn, cookies_path_fn, profile_cookies_path_fn,
                       encrypt_cookies_fn, decrypt_cookies_fn, profiles_dir: str,
                       resolve_proxy_fn=None):'''

    if 'resolve_proxy_fn=None' in content:
        print('WARNING: extend_sync_routes already has resolve_proxy_fn')
    elif old_sig in content:
        content = content.replace(old_sig, new_sig)
        print('PATCHED: extend_sync_routes signature - added resolve_proxy_fn')
    else:
        print('ERROR: Could not find extend_sync_routes signature')
        return False

    # ===== 3. Update sync_start to use proxy =====
    # Replace the proxy=None launch call with proxy resolution
    old_launch = '''        try:
            ctx, page = await launch_fn(profile_name, proxy=None, device=None)
            sessions[profile_name] = {
                'ctx': ctx, 'page': page, 'user': u['user'],
                'created': time.time(), 'last_active': time.time(),
                'proxy': None, 'device': None,
                'profile_name': profile_name,
                '_sync_mode': True,
            }'''

    new_launch = '''        try:
            # Resolve proxy - CRITICAL: cookies must be born on the proxy IP
            proxy_url = None
            proxy_name = req.proxy_provider
            if proxy_name and resolve_proxy_fn:
                try:
                    proxy_url = resolve_proxy_fn(proxy_name)
                    log.info(f'Sync: Using proxy provider "{proxy_name}" for {profile_name}')
                except Exception as pe:
                    log.warning(f'Sync: Proxy "{proxy_name}" resolution failed: {pe}. Proceeding without proxy.')

            ctx, page = await launch_fn(profile_name, proxy=proxy_url, device=None)
            sessions[profile_name] = {
                'ctx': ctx, 'page': page, 'user': u['user'],
                'created': time.time(), 'last_active': time.time(),
                'proxy': proxy_url, 'device': None,
                'profile_name': profile_name,
                '_sync_mode': True,
            }'''

    if old_launch in content:
        content = content.replace(old_launch, new_launch)
        print('PATCHED: sync_start - now resolves and uses proxy')
    elif 'proxy_url = None' in content and 'resolve_proxy_fn' in content:
        print('WARNING: sync_start proxy logic already patched')
    else:
        print('ERROR: Could not find sync_start launch block')
        return False

    # ===== 4. Update the HTML JS to send proxy_provider =====
    old_js_start = '''body: JSON.stringify({profile: state.profile, platform: state.platform}),'''

    new_js_start = '''body: JSON.stringify({profile: state.profile, platform: state.platform, proxy_provider: state.proxyProvider || 'residential'}),'''

    if old_js_start in content:
        content = content.replace(old_js_start, new_js_start)
        print('PATCHED: JS startSync - now sends proxy_provider')
    else:
        print('WARNING: JS startSync body already patched or not found')

    # ===== 5. Add proxyProvider to state object =====
    old_state = '''let state = {
  apiKey: '',
  profile: '',
  platform: '',
  sessionId: '',
  screenshotInterval: null,
};'''

    new_state = '''let state = {
  apiKey: '',
  profile: '',
  platform: '',
  proxyProvider: 'residential',
  sessionId: '',
  screenshotInterval: null,
};'''

    if old_state in content:
        content = content.replace(old_state, new_state)
        print('PATCHED: JS state - added proxyProvider')
    else:
        print('WARNING: JS state already patched or not found')

    # ===== 6. Add proxy selector to HTML UI =====
    # Add proxy provider selector after the profile selector
    old_profile_card = '''    <div class="input-group">
      <label>Profile</label>
      <select id="profile-select" disabled>
        <option value="">Enter API key first</option>
      </select>
    </div>
  </div>

  <div class="card">
    <div class="card-title">2. Select Platform</div>'''

    new_profile_card = '''    <div class="input-group">
      <label>Profile</label>
      <select id="profile-select" disabled>
        <option value="">Enter API key first</option>
      </select>
    </div>
    <div class="input-group">
      <label>Proxy <span style="color:var(--success);font-size:11px">(cookies will use this IP)</span></label>
      <select id="proxy-select" onchange="state.proxyProvider=this.value;checkReady()">
        <option value="residential" selected>Residential (recommended)</option>
        <option value="residential-us">Residential US</option>
        <option value="us-ny">US New York</option>
        <option value="floppydata">FloppyData</option>
        <option value="">No Proxy (server IP)</option>
      </select>
    </div>
  </div>

  <div class="card">
    <div class="card-title">2. Select Platform</div>'''

    if old_profile_card in content:
        content = content.replace(old_profile_card, new_profile_card)
        print('PATCHED: HTML - added proxy selector')
    else:
        print('WARNING: HTML proxy selector block not found - may already be patched')

    # ===== 7. Add proxy info to the sync_start response =====
    old_response = '''            return {
                'session_id': profile_name,
                'status': 'login_page_loaded',
                'screenshot': b64,
                'platform': req.platform,
            }'''

    new_response = '''            return {
                'session_id': profile_name,
                'status': 'login_page_loaded',
                'screenshot': b64,
                'platform': req.platform,
                'proxy_provider': proxy_name or 'none',
                'using_proxy': bool(proxy_url),
            }'''

    if old_response in content:
        content = content.replace(old_response, new_response)
        print('PATCHED: sync_start response - added proxy info')
    else:
        print('WARNING: sync_start response already patched or not found')

    # ===== 8. Add proxy info to success metadata =====
    old_meta = '''        meta = {
            'last_sync': time.time(),
            'last_sync_count': cookie_count,
            'total_cookies': cookie_count,
            'domains': list(domains.keys()),
            'sync_source': 'mobile_sync_page',
            'platform': platform['name'],
            'key_cookies_found': key_found,
        }'''

    new_meta = '''        # Get proxy info from session
        session_proxy = sessions_dict.get(sid, {}).get('proxy')
        meta = {
            'last_sync': time.time(),
            'last_sync_count': cookie_count,
            'total_cookies': cookie_count,
            'domains': list(domains.keys()),
            'sync_source': 'mobile_sync_page',
            'platform': platform['name'],
            'key_cookies_found': key_found,
            'proxy_used': bool(session_proxy),
            'proxy_url': session_proxy[:30] + '...' if session_proxy else None,
        }'''

    if old_meta in content:
        content = content.replace(old_meta, new_meta)
        print('PATCHED: cookie metadata - added proxy info')
    else:
        print('WARNING: cookie metadata already patched or not found')

    with open(SYNC_FILE, 'w') as f:
        f.write(content)
    print(f'\nSaved {SYNC_FILE}')
    return True


def patch_main_file():
    with open(MAIN_FILE, 'r') as f:
        content = f.read()

    # Add resolve_proxy_fn to the extend_sync_routes call
    old_call = '''extend_sync_routes(
    app=app,
    sessions=sessions,
    auth_fn=auth,
    launch_fn=_launch,
    save_cookies_fn=_save_cookies,'''

    # Check what the full call looks like
    if 'resolve_proxy_fn=_resolve_proxy_provider' in content:
        print('WARNING: main file already has resolve_proxy_fn')
        return True

    if old_call not in content:
        print('ERROR: Could not find extend_sync_routes call in main file')
        return False

    # Find the closing paren of the call to add the new parameter
    # The call ends with profiles_dir=PROFILES_DIR, followed by )
    old_end = '''    profiles_dir=PROFILES_DIR,
)'''

    new_end = '''    profiles_dir=PROFILES_DIR,
    resolve_proxy_fn=_resolve_proxy_provider,
)'''

    if old_end in content:
        content = content.replace(old_end, new_end)
        print('PATCHED: main file - passing _resolve_proxy_provider to extend_sync_routes')
    else:
        print('ERROR: Could not find end of extend_sync_routes call')
        return False

    with open(MAIN_FILE, 'w') as f:
        f.write(content)
    print(f'Saved {MAIN_FILE}')
    return True


if __name__ == '__main__':
    print('=' * 60)
    print('PureSurf Sync Proxy Login Patch')
    print('=' * 60)

    ok1 = patch_sync_file()
    print()
    ok2 = patch_main_file()

    if ok1 and ok2:
        print('\n[SUCCESS] All patches applied. Restart the server to activate.')
    else:
        print('\n[WARNING] Some patches may not have applied cleanly. Check output above.')
