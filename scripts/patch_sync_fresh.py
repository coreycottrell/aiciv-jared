#!/usr/bin/env python3
"""Add fresh profile cleanup to sync_start to fix stale cache + proxy conflicts."""

SYNC_FILE = '/opt/baas/cookie_sync_page.py'

with open(SYNC_FILE) as f:
    content = f.read()

changes = 0

# 1. Add fresh field to SyncStartReq
old = "    proxy_provider: Optional[str] = 'residential'  # CRITICAL: cookies must be born on proxy IP"
new = """    proxy_provider: Optional[str] = 'residential'  # CRITICAL: cookies must be born on proxy IP
    fresh: bool = False  # If True, clear profile browser data before starting"""

if 'fresh: bool' not in content:
    content = content.replace(old, new)
    changes += 1
    print('PATCHED: Added fresh field to SyncStartReq')

# 2. Add profile cleanup before launch
old_launch = "            # Resolve proxy - CRITICAL: cookies must be born on the proxy IP"
new_launch = """            # If fresh=True, clear stale browser data (prevents proxy redirect loops)
            if req.fresh:
                import shutil
                profile_dir = os.path.join(profiles_dir, f's_{profile_name}')
                if os.path.exists(profile_dir):
                    shutil.rmtree(profile_dir, ignore_errors=True)
                    os.makedirs(profile_dir, exist_ok=True)
                    log.info(f'Sync: Cleared stale profile data for {profile_name} (fresh=True)')

            # Resolve proxy - CRITICAL: cookies must be born on the proxy IP"""

if 'req.fresh' not in content:
    content = content.replace(old_launch, new_launch)
    changes += 1
    print('PATCHED: Added fresh profile cleanup logic')

# 3. Update JS to send fresh=true by default (sync always wants fresh cookies)
old_js = "body: JSON.stringify({profile: state.profile, platform: state.platform, proxy_provider: state.proxyProvider || 'residential'})"
new_js = "body: JSON.stringify({profile: state.profile, platform: state.platform, proxy_provider: state.proxyProvider || 'residential', fresh: true})"

if 'fresh: true' not in content:
    content = content.replace(old_js, new_js)
    changes += 1
    print('PATCHED: JS now sends fresh=true')

with open(SYNC_FILE, 'w') as f:
    f.write(content)

print(f'\nTotal changes: {changes}')
