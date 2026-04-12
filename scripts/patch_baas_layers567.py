#!/usr/bin/env python3
"""Patch baas_server_simple.py with Layer 5/6/7 integration."""

SERVER_FILE = '/opt/baas/baas_server_simple.py'

with open(SERVER_FILE, 'r') as f:
    content = f.read()

# 1. Add imports after the sheet_sync import
old_import = "from sheet_sync import extend_sheet_sync_router"
new_import = """from sheet_sync import extend_sheet_sync_router
from rate_intelligence import rate_limiter
from profile_manager import profile_manager
from warmup import warmup_protocol"""
assert old_import in content, "Could not find sheet_sync import"
content = content.replace(old_import, new_import, 1)

# 2. Patch _launch() to use ProfileManager for managed profiles
old_launch = """async def _launch(session_id: str, proxy: str = None, device: str = None):
    from camoufox.async_api import AsyncNewBrowser
    from browserforge.fingerprints import Screen
    pw = await get_pw()
    ud = _profile_dir(session_id)
    os.makedirs(ud, exist_ok=True)

    launch_kwargs = {
        'headless': 'virtual',
        'persistent_context': True,
        'user_data_dir': ud,
        'block_webrtc': True,
    }

    if device and device in DEVICE_PROFILES:
        dp = DEVICE_PROFILES[device]
        if dp.get('os'):
            launch_kwargs['os'] = dp['os']
        launch_kwargs['screen'] = Screen(
            min_width=dp.get('screen_min_width'),
            max_width=dp.get('screen_max_width'),
            min_height=dp.get('screen_min_height'),
            max_height=dp.get('screen_max_height'),
        )
        if dp.get('humanize'):
            launch_kwargs['humanize'] = True
        if dp.get('window'):
            launch_kwargs['window'] = tuple(dp['window'])

    if proxy:
        proxy_config = _parse_proxy(proxy)
        launch_kwargs['proxy'] = proxy_config
        # geoip disabled - download happens at runtime
        log.info(f'Session {session_id} using proxy: {proxy_config["server"]}')

    ctx = await AsyncNewBrowser(pw, **launch_kwargs)"""

new_launch = """async def _launch(session_id: str, proxy: str = None, device: str = None):
    from camoufox.async_api import AsyncNewBrowser
    from browserforge.fingerprints import Screen
    pw = await get_pw()
    ud = _profile_dir(session_id)
    os.makedirs(ud, exist_ok=True)

    launch_kwargs = {
        'headless': 'virtual',
        'persistent_context': True,
        'user_data_dir': ud,
        'block_webrtc': True,
    }

    # Layer 6: Check if this is a managed profile with isolation config
    if profile_manager.is_managed(session_id):
        pm_config = profile_manager.get_launch_config(session_id)
        log.info(f'Session {session_id} using MANAGED profile config: os={pm_config.get("os")}, proxy={bool(pm_config.get("proxy_url"))}')

        if pm_config.get('os'):
            launch_kwargs['os'] = pm_config['os']
        launch_kwargs['screen'] = Screen(
            min_width=pm_config.get('screen_min_width', 1920),
            max_width=pm_config.get('screen_max_width', 1920),
            min_height=pm_config.get('screen_min_height', 1080),
            max_height=pm_config.get('screen_max_height', 1080),
        )
        launch_kwargs['humanize'] = True

        # Use managed profile proxy if no explicit proxy was passed
        if not proxy and pm_config.get('proxy_url'):
            proxy = pm_config['proxy_url']
            log.info(f'Session {session_id} auto-resolved proxy from profile manager')

    elif device and device in DEVICE_PROFILES:
        dp = DEVICE_PROFILES[device]
        if dp.get('os'):
            launch_kwargs['os'] = dp['os']
        launch_kwargs['screen'] = Screen(
            min_width=dp.get('screen_min_width'),
            max_width=dp.get('screen_max_width'),
            min_height=dp.get('screen_min_height'),
            max_height=dp.get('screen_max_height'),
        )
        if dp.get('humanize'):
            launch_kwargs['humanize'] = True
        if dp.get('window'):
            launch_kwargs['window'] = tuple(dp['window'])

    if proxy:
        proxy_config = _parse_proxy(proxy)
        launch_kwargs['proxy'] = proxy_config
        # geoip disabled - download happens at runtime
        log.info(f'Session {session_id} using proxy: {proxy_config["server"]}')

    ctx = await AsyncNewBrowser(pw, **launch_kwargs)"""

assert old_launch in content, "Could not find _launch() function to patch"
content = content.replace(old_launch, new_launch, 1)

# 3. Add monitoring API endpoints before the uvicorn.run line
old_main = """if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8901)"""

new_main = """# ==================== LAYER 5/6/7 MONITORING ENDPOINTS ====================

@app.get('/api/v1/profiles/{profile_name}/rate-status')
async def get_rate_status(profile_name: str, x_api_key: str = Header(None)):
    auth(x_api_key)
    platform = 'linkedin'
    return rate_limiter.get_status(profile_name, platform)

@app.get('/api/v1/profiles/{profile_name}/warmup-status')
async def get_warmup_status(profile_name: str, x_api_key: str = Header(None)):
    auth(x_api_key)
    return warmup_protocol.get_warmup_status(profile_name)

@app.post('/api/v1/profiles/{profile_name}/warmup/start')
async def start_warmup(profile_name: str, x_api_key: str = Header(None)):
    auth(x_api_key)
    warmup_protocol.start_warmup(profile_name)
    return warmup_protocol.get_warmup_status(profile_name)

@app.post('/api/v1/profiles/{profile_name}/warmup/skip')
async def skip_warmup(profile_name: str, x_api_key: str = Header(None)):
    auth(x_api_key)
    warmup_protocol.override_to_full(profile_name)
    return warmup_protocol.get_warmup_status(profile_name)

@app.get('/api/v1/profiles/{profile_name}/managed-config')
async def get_managed_config(profile_name: str, x_api_key: str = Header(None)):
    auth(x_api_key)
    if not profile_manager.is_managed(profile_name):
        return {'managed': False, 'profile': profile_name}
    return {
        'managed': True,
        'profile': profile_name,
        'config': profile_manager.get_profile(profile_name),
        'can_run_now': profile_manager.can_run_now(profile_name),
        'fingerprint': profile_manager.get_fingerprint_config(profile_name),
    }

@app.get('/api/v1/managed-profiles')
async def list_managed_profiles(x_api_key: str = Header(None)):
    auth(x_api_key)
    return profile_manager.list_profiles()

@app.get('/api/v1/rate-status/all')
async def get_all_rate_status(x_api_key: str = Header(None)):
    auth(x_api_key)
    return rate_limiter.get_all_status()

@app.get('/api/v1/warmup-status/all')
async def get_all_warmup_status(x_api_key: str = Header(None)):
    auth(x_api_key)
    return warmup_protocol.list_all()


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8901)"""

assert old_main in content, "Could not find __main__ block"
content = content.replace(old_main, new_main, 1)

with open(SERVER_FILE, 'w') as f:
    f.write(content)

print('Patch applied successfully')
print(f'File size: {len(content)} bytes')
