#!/usr/bin/env python3
"""Patch baas_server_simple.py to also save/load cookies from Firefox sqlite."""

SOURCE = '/opt/baas/baas_server_simple.py'
with open(SOURCE, 'r') as f:
    code = f.read()

# Find and enhance _save_cookies to also extract from Firefox sqlite
old_save = '''async def _save_cookies(session_id: str, page):
    try:
        cookies = await page.context.cookies()
        cp = _cookies_path(session_id)
        os.makedirs(os.path.dirname(cp), exist_ok=True)
        with open(cp, 'wb') as f:
            f.write(_encrypt_cookies(cookies))
        log.info(f'Saved {len(cookies)} cookies for session {session_id}')
        return len(cookies)
    except Exception as e:
        log.error(f'Failed to save cookies for {session_id}: {e}')
        return 0'''

new_save = '''async def _save_cookies(session_id: str, page):
    try:
        cookies = await page.context.cookies()

        # Also try to extract cookies from Firefox sqlite (Camoufox persistent context)
        # This catches httpOnly cookies like li_at that Playwright may not surface
        try:
            import sqlite3
            sqlite_path = os.path.join(_profile_dir(session_id), 'cookies.sqlite')
            if os.path.exists(sqlite_path):
                existing_names = {(c['name'], c.get('domain','')) for c in cookies}
                db = sqlite3.connect(sqlite_path)
                db.execute('PRAGMA journal_mode=WAL')
                cursor = db.execute(
                    'SELECT name, value, host, path, expiry, isSecure, isHttpOnly, sameSite '
                    'FROM moz_cookies'
                )
                added_from_sqlite = 0
                for row in cursor:
                    name, value, host, path, expiry, secure, httponly, samesite = row
                    if (name, host) not in existing_names and value:
                        cookie = {
                            'name': name,
                            'value': value,
                            'domain': host,
                            'path': path or '/',
                            'secure': bool(secure),
                            'httpOnly': bool(httponly),
                        }
                        if expiry and expiry > 0:
                            cookie['expires'] = expiry
                        if samesite == 1:
                            cookie['sameSite'] = 'Lax'
                        elif samesite == 2:
                            cookie['sameSite'] = 'Strict'
                        else:
                            cookie['sameSite'] = 'None'
                        cookies.append(cookie)
                        added_from_sqlite += 1
                db.close()
                if added_from_sqlite > 0:
                    log.info(f'Added {added_from_sqlite} cookies from Firefox sqlite for {session_id}')
        except Exception as sqlite_err:
            log.debug(f'Firefox sqlite cookie extraction failed for {session_id}: {sqlite_err}')

        cp = _cookies_path(session_id)
        os.makedirs(os.path.dirname(cp), exist_ok=True)
        with open(cp, 'wb') as f:
            f.write(_encrypt_cookies(cookies))
        log.info(f'Saved {len(cookies)} cookies for session {session_id}')
        return len(cookies)
    except Exception as e:
        log.error(f'Failed to save cookies for {session_id}: {e}')
        return 0'''

if old_save in code:
    code = code.replace(old_save, new_save)
    print('SUCCESS: Enhanced _save_cookies to also extract from Firefox sqlite')
else:
    print('WARNING: Could not find exact _save_cookies match, trying flexible match...')
    import re
    pattern = r'async def _save_cookies\(session_id: str, page\):.*?return 0\n'
    match = re.search(pattern, code, re.DOTALL)
    if match:
        # Just report what we found
        print(f'Found _save_cookies at position {match.start()}, length {len(match.group(0))}')
        print('Manual patch may be needed.')
    exit(1)

with open(SOURCE, 'w') as f:
    f.write(code)

print('Cookie persistence fix applied.')
print('This ensures li_at and other httpOnly cookies from Firefox sqlite are captured.')
